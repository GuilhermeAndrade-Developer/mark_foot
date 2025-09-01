from celery import shared_task
import logging
from django.utils import timezone
from datetime import timedelta
from .services import MessageProcessor, WhatsAppService
from .models import WhatsAppUser, WhatsAppSubscriptionEvent

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def process_whatsapp_message(self, webhook_data):
    """Process WhatsApp message asynchronously"""
    try:
        processor = MessageProcessor()
        processor.process_message(webhook_data)
        
        logger.info(f"Successfully processed WhatsApp message")
        
    except Exception as e:
        logger.error(f"Error processing WhatsApp message: {str(e)}")
        
        # Retry on failure
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying WhatsApp message processing. Attempt {self.request.retries + 1}")
            raise self.retry(countdown=60 * (self.request.retries + 1))
        else:
            logger.error(f"Max retries reached for WhatsApp message processing")
            raise

@shared_task
def send_premium_promotion_batch(phone_numbers):
    """Send premium promotion to multiple users"""
    from .services import WhatsAppService
    
    whatsapp_service = WhatsAppService()
    success_count = 0
    
    for phone_number in phone_numbers:
        try:
            whatsapp_service.send_premium_promotion(phone_number)
            success_count += 1
        except Exception as e:
            logger.error(f"Error sending promotion to {phone_number}: {str(e)}")
    
    logger.info(f"Sent premium promotion to {success_count}/{len(phone_numbers)} users")
    return success_count

@shared_task
def cleanup_old_messages():
    """Clean up old WhatsApp messages (older than 30 days)"""
    from django.utils import timezone
    from datetime import timedelta
    from .models import WhatsAppMessage
    
    cutoff_date = timezone.now() - timedelta(days=30)
    deleted_count, _ = WhatsAppMessage.objects.filter(
        timestamp__lt=cutoff_date
    ).delete()
    
    logger.info(f"Cleaned up {deleted_count} old WhatsApp messages")
    return deleted_count

@shared_task
def reset_daily_query_counts():
    """Reset daily query counts for all users (run daily at midnight)"""
    from .models import WhatsAppUser
    
    updated_count = WhatsAppUser.objects.all().update(daily_queries_count=0)
    logger.info(f"Reset daily query counts for {updated_count} users")
    return updated_count


@shared_task
def send_subscription_confirmation(whatsapp_user_id):
    """Send subscription confirmation message"""
    try:
        whatsapp_user = WhatsAppUser.objects.get(id=whatsapp_user_id)
        whatsapp_service = WhatsAppService()
        
        message = """🎉 Pagamento confirmado!

✅ Acesso premium liberado
🔓 Consultas ilimitadas
💎 Análise completa de odds
🤖 Previsões com IA

Experimente agora: Digite qualquer pergunta sobre futebol!

📞 Dúvidas? Responda esta mensagem."""
        
        whatsapp_service.send_text_message(whatsapp_user.phone_number, message)
        
        logger.info(f"Subscription confirmation sent to {whatsapp_user.phone_number}")
        return True
        
    except WhatsAppUser.DoesNotExist:
        logger.error(f"WhatsApp user not found: {whatsapp_user_id}")
        return False
    except Exception as e:
        logger.error(f"Error sending subscription confirmation: {str(e)}")
        return False


@shared_task
def check_expiring_subscriptions():
    """Check for subscriptions expiring in 3 days"""
    try:
        from billing.models import UserSubscription
        
        three_days_from_now = timezone.now() + timedelta(days=3)
        expiring_subscriptions = UserSubscription.objects.filter(
            expires_at__lte=three_days_from_now,
            expires_at__gt=timezone.now(),
            status='active'
        )
        
        whatsapp_service = WhatsAppService()
        count = 0
        
        for subscription in expiring_subscriptions:
            try:
                whatsapp_user = WhatsAppUser.objects.get(user=subscription.user)
                days_left = (subscription.expires_at - timezone.now()).days
                
                message = f"""⏰ Sua assinatura expira em {days_left} dias!

Renove agora e mantenha:
✅ Consultas ilimitadas
✅ Análise de odds
✅ Previsões IA

🔄 Renovar: /renovar
❓ Dúvidas: Responda esta mensagem"""
                
                whatsapp_service.send_text_message(whatsapp_user.phone_number, message)
                count += 1
                
            except WhatsAppUser.DoesNotExist:
                logger.warning(f"WhatsApp user not found for subscription user: {subscription.user.id}")
            except Exception as e:
                logger.error(f"Error sending expiring notification: {str(e)}")
        
        logger.info(f"Sent {count} expiring subscription notifications")
        return count
        
    except Exception as e:
        logger.error(f"Error checking expiring subscriptions: {str(e)}")
        return 0


@shared_task
def check_expired_subscriptions():
    """Check and notify expired subscriptions"""
    try:
        from billing.models import UserSubscription
        
        expired_subscriptions = UserSubscription.objects.filter(
            expires_at__lt=timezone.now(),
            status='active'
        )
        
        whatsapp_service = WhatsAppService()
        count = 0
        
        for subscription in expired_subscriptions:
            try:
                whatsapp_user = WhatsAppUser.objects.get(user=subscription.user)
                
                # Update subscription status
                subscription.status = 'expired'
                subscription.save()
                
                # Update WhatsApp user status
                whatsapp_user.subscription_status = 'expired'
                whatsapp_user.save()
                
                # Create event
                WhatsAppSubscriptionEvent.objects.create(
                    whatsapp_user=whatsapp_user,
                    event_type='subscription_expired'
                )
                
                message = """😞 Sua assinatura expirou

Você voltou ao plano gratuito:
📱 5 consultas por dia
❌ Sem análise de odds

🔄 Renovar agora: /renovar"""
                
                whatsapp_service.send_text_message(whatsapp_user.phone_number, message)
                count += 1
                
            except WhatsAppUser.DoesNotExist:
                logger.warning(f"WhatsApp user not found for expired subscription: {subscription.user.id}")
            except Exception as e:
                logger.error(f"Error processing expired subscription: {str(e)}")
        
        logger.info(f"Processed {count} expired subscriptions")
        return count
        
    except Exception as e:
        logger.error(f"Error checking expired subscriptions: {str(e)}")
        return 0


@shared_task
def check_trial_endings():
    """Check for trials ending today"""
    try:
        today = timezone.now().date()
        ending_trials = WhatsAppUser.objects.filter(
            subscription_status='trial',
            trial_expires_at__date=today
        )
        
        whatsapp_service = WhatsAppService()
        count = 0
        
        for whatsapp_user in ending_trials:
            try:
                # Update status
                whatsapp_user.subscription_status = 'trial_ended'
                whatsapp_user.save()
                
                # Create event
                WhatsAppSubscriptionEvent.objects.create(
                    whatsapp_user=whatsapp_user,
                    event_type='trial_ended'
                )
                
                message = """🏁 Seu trial de 7 dias terminou!

Gostou da experiência Premium?
💎 Continue com apenas R$ 19,90/mês

✅ Consultas ilimitadas
✅ Análise de odds
✅ Previsões IA

📝 Assinar: /premium"""
                
                whatsapp_service.send_text_message(whatsapp_user.phone_number, message)
                count += 1
                
            except Exception as e:
                logger.error(f"Error processing trial ending: {str(e)}")
        
        logger.info(f"Processed {count} trial endings")
        return count
        
    except Exception as e:
        logger.error(f"Error checking trial endings: {str(e)}")
        return 0


@shared_task
def cleanup_expired_payment_intents():
    """Clean up expired payment intents"""
    try:
        from .models import WhatsAppPaymentIntent
        
        expired_intents = WhatsAppPaymentIntent.objects.filter(
            status='pending',
            expires_at__lt=timezone.now()
        )
        
        count = expired_intents.count()
        expired_intents.update(status='expired')
        
        logger.info(f"Cleaned up {count} expired payment intents")
        return count
        
    except Exception as e:
        logger.error(f"Error cleaning up payment intents: {str(e)}")
        return 0
