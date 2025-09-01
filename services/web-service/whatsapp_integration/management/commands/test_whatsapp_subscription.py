from django.core.management.base import BaseCommand
from whatsapp_integration.models import WhatsAppUser
from whatsapp_integration.services.subscription_service import WhatsAppSubscriptionService
from billing.models import SubscriptionPlan


class Command(BaseCommand):
    help = 'Test WhatsApp subscription system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--phone',
            type=str,
            default='+5511999999999',
            help='Phone number to test (default: +5511999999999)'
        )
        parser.add_argument(
            '--action',
            type=str,
            choices=['trial', 'premium', 'pro', 'status', 'cancel'],
            default='status',
            help='Action to test'
        )

    def handle(self, *args, **options):
        phone_number = options['phone']
        action = options['action']
        
        # Get or create WhatsApp user
        whatsapp_user, created = WhatsAppUser.objects.get_or_create(
            phone_number=phone_number,
            defaults={
                'display_name': 'Test User'
            }
        )
        
        if created:
            self.stdout.write(f"Created test user: {phone_number}")
        else:
            self.stdout.write(f"Using existing user: {phone_number}")
        
        # Initialize subscription service
        subscription_service = WhatsAppSubscriptionService()
        
        # Execute action
        if action == 'trial':
            result = subscription_service.start_trial(whatsapp_user)
            self.stdout.write(f"Trial result: {result}")
            
        elif action == 'premium':
            try:
                plan = SubscriptionPlan.objects.get(plan_type='premium')
                result = subscription_service.create_payment_intent(
                    whatsapp_user, 
                    plan_type='premium', 
                    payment_provider='stripe'
                )
                self.stdout.write(f"Premium payment intent: {result}")
            except SubscriptionPlan.DoesNotExist:
                self.stdout.write(self.style.ERROR("Premium plan not found"))
                
        elif action == 'pro':
            try:
                plan = SubscriptionPlan.objects.get(plan_type='pro')
                result = subscription_service.create_payment_intent(
                    whatsapp_user, 
                    plan_type='pro', 
                    payment_provider='stripe'
                )
                self.stdout.write(f"Pro payment intent: {result}")
            except SubscriptionPlan.DoesNotExist:
                self.stdout.write(self.style.ERROR("Pro plan not found"))
                
        elif action == 'status':
            info = subscription_service.get_subscription_info(whatsapp_user)
            self.stdout.write(f"Subscription info: {info}")
            
        elif action == 'cancel':
            result = subscription_service.cancel_subscription(whatsapp_user)
            self.stdout.write(f"Cancel result: {result}")
        
        # Show current user status
        whatsapp_user.refresh_from_db()
        self.stdout.write("\n" + "="*50)
        self.stdout.write(f"User: {whatsapp_user.phone_number}")
        self.stdout.write(f"Display Name: {whatsapp_user.display_name}")
        self.stdout.write(f"Subscription Status: {whatsapp_user.subscription_status}")
        self.stdout.write(f"Current Plan: {whatsapp_user.current_plan}")
        self.stdout.write(f"Daily Queries: {whatsapp_user.daily_queries_count}")
        self.stdout.write(f"Can Make Query: {whatsapp_user.can_make_query()}")
        
        if whatsapp_user.is_trial_active:
            self.stdout.write(f"Trial Active: Yes")
            self.stdout.write(f"Trial Expires: {whatsapp_user.trial_expires_at}")
        else:
            self.stdout.write(f"Trial Active: No")
        
        self.stdout.write("="*50)
