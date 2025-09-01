from celery import shared_task
import logging
from .services import MessageProcessor

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
