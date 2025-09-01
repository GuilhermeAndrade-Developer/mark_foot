from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from billing.services.stripe_service import StripeService
from billing.services.pagseguro_service import PagSeguroService
from billing.models import SubscriptionPlan, UserSubscription
from ..models import WhatsAppUser, WhatsAppPaymentIntent, WhatsAppSubscriptionEvent
import uuid


class WhatsAppSubscriptionService:
    def __init__(self):
        self.stripe_service = StripeService()
        self.pagseguro_service = PagSeguroService()
        # MercadoPago service can be added later
        self.mercadopago_service = None
    
    def start_trial(self, whatsapp_user):
        """Start 7-day trial for WhatsApp user"""
        if whatsapp_user.subscription_status != 'free':
            return {'success': False, 'message': 'Trial already used or user has active subscription'}
        
        trial_end = timezone.now() + timedelta(days=7)
        
        whatsapp_user.subscription_status = 'trial'
        whatsapp_user.trial_started_at = timezone.now()
        whatsapp_user.trial_expires_at = trial_end
        whatsapp_user.save()
        
        # Create event
        WhatsAppSubscriptionEvent.objects.create(
            whatsapp_user=whatsapp_user,
            event_type='trial_started',
            data={'trial_end_date': trial_end.isoformat()}
        )
        
        return {
            'success': True,
            'trial_end_date': trial_end,
            'message': 'Trial started successfully'
        }
    
    def check_subscription_status(self, whatsapp_user):
        """Check and update subscription status"""
        now = timezone.now()
        
        # Check if trial expired
        if whatsapp_user.subscription_status == 'trial' and whatsapp_user.trial_expires_at:
            if now > whatsapp_user.trial_expires_at:
                whatsapp_user.subscription_status = 'trial_ended'
                whatsapp_user.save()
                
                WhatsAppSubscriptionEvent.objects.create(
                    whatsapp_user=whatsapp_user,
                    event_type='trial_ended'
                )
        
        # Check if subscription expired
        if whatsapp_user.user and hasattr(whatsapp_user.user, 'subscription'):
            subscription = whatsapp_user.user.subscription
            if subscription.is_expired and whatsapp_user.subscription_status in ['premium', 'pro']:
                whatsapp_user.subscription_status = 'expired'
                whatsapp_user.save()
                
                WhatsAppSubscriptionEvent.objects.create(
                    whatsapp_user=whatsapp_user,
                    event_type='subscription_expired'
                )
        
        return whatsapp_user.subscription_status
    
    def create_payment_intent(self, whatsapp_user, plan_type='premium', payment_provider='stripe'):
        """Create payment intent for subscription"""
        try:
            plan = SubscriptionPlan.objects.get(plan_type=plan_type)
        except SubscriptionPlan.DoesNotExist:
            return {'success': False, 'message': 'Plan not found'}
        
        # Create payment intent record
        payment_intent = WhatsAppPaymentIntent.objects.create(
            whatsapp_user=whatsapp_user,
            plan=plan,
            payment_provider=payment_provider,
            amount=plan.price_monthly,
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        # Create payment with selected provider
        if payment_provider == 'stripe':
            result = self._create_stripe_payment(payment_intent)
        elif payment_provider == 'pagseguro':
            result = self._create_pagseguro_payment(payment_intent)
        elif payment_provider == 'mercadopago':
            result = self._create_mercadopago_payment(payment_intent)
        else:
            return {'success': False, 'message': 'Invalid payment provider'}
        
        if result['success']:
            payment_intent.payment_url = result['payment_url']
            payment_intent.save()
        
        return result
    
    def _create_stripe_payment(self, payment_intent):
        """Create Stripe payment"""
        try:
            # Create or get user
            user = self._get_or_create_user(payment_intent.whatsapp_user)
            
            stripe_intent = self.stripe_service.create_payment_intent(
                amount=int(payment_intent.amount * 100),  # Convert to cents
                currency=payment_intent.currency.lower(),
                metadata={
                    'whatsapp_user_id': payment_intent.whatsapp_user.id,
                    'plan_id': payment_intent.plan.id,
                    'payment_intent_id': payment_intent.id
                }
            )
            
            payment_intent.stripe_payment_intent_id = stripe_intent['id']
            payment_intent.save()
            
            return {
                'success': True,
                'payment_url': f"https://checkout.stripe.com/pay/{stripe_intent['client_secret']}",
                'payment_intent_id': stripe_intent['id']
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def _create_pagseguro_payment(self, payment_intent):
        """Create PagSeguro payment"""
        try:
            user = self._get_or_create_user(payment_intent.whatsapp_user)
            
            payment_data = {
                'amount': float(payment_intent.amount),
                'description': f"Assinatura {payment_intent.plan.name}",
                'reference_id': str(payment_intent.id),
                'customer': {
                    'name': payment_intent.whatsapp_user.display_name or 'WhatsApp User',
                    'email': user.email or f"user_{payment_intent.whatsapp_user.id}@whatsapp.local",
                    'tax_id': '00000000000'  # CPF placeholder
                }
            }
            
            result = self.pagseguro_service.create_payment(payment_data)
            
            if result['success']:
                payment_intent.pagseguro_transaction_id = result['transaction_id']
                payment_intent.save()
                
                return {
                    'success': True,
                    'payment_url': result['payment_url'],
                    'transaction_id': result['transaction_id']
                }
            
            return result
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def _create_mercadopago_payment(self, payment_intent):
        """Create Mercado Pago payment"""
        # MercadoPago integration to be implemented
        return {'success': False, 'message': 'MercadoPago integration not implemented yet'}
    
    def _get_or_create_user(self, whatsapp_user):
        """Get or create Django user for WhatsApp user"""
        if whatsapp_user.user:
            return whatsapp_user.user
        
        # Create user
        username = f"whatsapp_{whatsapp_user.phone_number.replace('+', '')}"
        user = User.objects.create_user(
            username=username,
            email=f"{username}@whatsapp.local",
            first_name=whatsapp_user.display_name or 'WhatsApp User'
        )
        
        whatsapp_user.user = user
        whatsapp_user.save()
        
        return user
    
    def process_successful_payment(self, payment_intent_id, provider_transaction_id):
        """Process successful payment and activate subscription"""
        try:
            payment_intent = WhatsAppPaymentIntent.objects.get(id=payment_intent_id)
            payment_intent.status = 'completed'
            payment_intent.save()
            
            whatsapp_user = payment_intent.whatsapp_user
            user = self._get_or_create_user(whatsapp_user)
            
            # Create or update subscription
            subscription, created = UserSubscription.objects.get_or_create(
                user=user,
                defaults={
                    'plan': payment_intent.plan,
                    'expires_at': timezone.now() + timedelta(days=30),
                    'api_calls_reset_date': timezone.now() + timedelta(days=30)
                }
            )
            
            if not created:
                subscription.plan = payment_intent.plan
                subscription.status = 'active'
                subscription.expires_at = timezone.now() + timedelta(days=30)
                subscription.save()
            
            # Update WhatsApp user
            whatsapp_user.subscription_status = payment_intent.plan.plan_type
            whatsapp_user.current_plan = payment_intent.plan
            whatsapp_user.save()
            
            # Create event
            WhatsAppSubscriptionEvent.objects.create(
                whatsapp_user=whatsapp_user,
                event_type='subscription_created',
                data={
                    'plan': payment_intent.plan.name,
                    'amount': str(payment_intent.amount),
                    'provider_transaction_id': provider_transaction_id
                }
            )
            
            return {'success': True, 'message': 'Subscription activated'}
            
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def cancel_subscription(self, whatsapp_user):
        """Cancel user subscription"""
        if whatsapp_user.user and hasattr(whatsapp_user.user, 'subscription'):
            subscription = whatsapp_user.user.subscription
            subscription.status = 'cancelled'
            subscription.cancelled_at = timezone.now()
            subscription.save()
        
        whatsapp_user.subscription_status = 'cancelled'
        whatsapp_user.save()
        
        WhatsAppSubscriptionEvent.objects.create(
            whatsapp_user=whatsapp_user,
            event_type='subscription_cancelled'
        )
        
        return {'success': True, 'message': 'Subscription cancelled'}
    
    def get_subscription_info(self, whatsapp_user):
        """Get subscription information for user"""
        status = self.check_subscription_status(whatsapp_user)
        
        info = {
            'status': status,
            'plan': whatsapp_user.current_plan.name if whatsapp_user.current_plan else 'Free',
            'daily_limit': whatsapp_user.get_daily_limit(),
            'daily_used': whatsapp_user.daily_queries_count
        }
        
        if whatsapp_user.user and hasattr(whatsapp_user.user, 'subscription'):
            subscription = whatsapp_user.user.subscription
            if not subscription.is_expired:
                info['expires_at'] = subscription.expires_at
                info['days_remaining'] = subscription.days_remaining
        
        if whatsapp_user.is_trial_active:
            info['trial_end_date'] = whatsapp_user.trial_expires_at
            info['trial_days_remaining'] = whatsapp_user.trial_days_remaining
        
        return info
