"""
Django management command for seeding billing data.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
from billing.models import SubscriptionPlan, UserSubscription, Invoice, PaymentMethod
from datetime import datetime, timedelta
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Seed billing subscription plans and sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset existing data before seeding',
        )
        parser.add_argument(
            '--with-user-data',
            action='store_true',
            help='Create sample user subscriptions and invoices',
        )

    def handle(self, *args, **options):
        self.stdout.write('🚀 Starting billing data seeder...')
        
        if options['reset']:
            UserSubscription.objects.all().delete()
            Invoice.objects.all().delete()
            PaymentMethod.objects.all().delete()
            SubscriptionPlan.objects.all().delete()
            self.stdout.write('🗑️  Existing billing data cleared')
        
        with transaction.atomic():
            # Create subscription plans
            self.create_subscription_plans()
            
            # Create sample user data if requested
            if options['with_user_data']:
                self.create_sample_user_data()
            
            self.display_summary()

        self.stdout.write(self.style.SUCCESS('\n🎉 Billing data seeder completed!'))

    def create_subscription_plans(self):
        """Create the three subscription plans"""
        # Free Plan
        free_plan, created = SubscriptionPlan.objects.get_or_create(
            plan_type='free',
            defaults={
                'name': 'Free',
                'description': 'Plano gratuito com funcionalidades básicas',
                'price_monthly': Decimal('0.00'),
                'price_yearly': Decimal('0.00'),
                'api_calls_limit': 100,
                'advanced_ai_analysis': False,
                'unlimited_reports': False,
                'white_label': False,
                'dedicated_support': False,
                'multi_tenancy': False,
                'features': {
                    'basic_stats': True,
                    'match_results': True,
                    'team_info': True,
                    'basic_predictions': True,
                    'community_access': True
                },
                'sort_order': 1,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✅ Created Free plan'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠️ Free plan already exists'))
        
        # Premium Plan
        premium_plan, created = SubscriptionPlan.objects.get_or_create(
            plan_type='premium',
            defaults={
                'name': 'Premium',
                'description': 'Plano premium com análises avançadas de IA e relatórios ilimitados',
                'price_monthly': Decimal('19.90'),
                'price_yearly': Decimal('199.00'),  # 2 months free
                'api_calls_limit': 10000,
                'advanced_ai_analysis': True,
                'unlimited_reports': True,
                'white_label': False,
                'dedicated_support': False,
                'multi_tenancy': False,
                'features': {
                    'basic_stats': True,
                    'match_results': True,
                    'team_info': True,
                    'basic_predictions': True,
                    'community_access': True,
                    'advanced_ai_predictions': True,
                    'player_analysis': True,
                    'market_insights': True,
                    'historical_data': True,
                    'export_reports': True,
                    'email_alerts': True,
                    'priority_support': True
                },
                'sort_order': 2,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✅ Created Premium plan'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠️ Premium plan already exists'))
        
        # Enterprise Plan
        enterprise_plan, created = SubscriptionPlan.objects.get_or_create(
            plan_type='enterprise',
            defaults={
                'name': 'Enterprise',
                'description': 'Plano empresarial com multi-tenancy, suporte dedicado e white-label',
                'price_monthly': Decimal('499.00'),
                'price_yearly': Decimal('4990.00'),  # 2 months free
                'api_calls_limit': 100000,
                'advanced_ai_analysis': True,
                'unlimited_reports': True,
                'white_label': True,
                'dedicated_support': True,
                'multi_tenancy': True,
                'features': {
                    'basic_stats': True,
                    'match_results': True,
                    'team_info': True,
                    'basic_predictions': True,
                    'community_access': True,
                    'advanced_ai_predictions': True,
                    'player_analysis': True,
                    'market_insights': True,
                    'historical_data': True,
                    'export_reports': True,
                    'email_alerts': True,
                    'priority_support': True,
                    'custom_branding': True,
                    'dedicated_account_manager': True,
                    'custom_integrations': True,
                    'sla_guarantee': True,
                    'advanced_analytics': True,
                    'bulk_data_export': True,
                    'webhook_notifications': True
                },
                'sort_order': 3,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✅ Created Enterprise plan'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠️ Enterprise plan already exists'))

    def create_sample_user_data(self):
        """Create sample user subscriptions, payment methods, and invoices"""
        self.stdout.write('👤 Creating sample user data...')
        
        # Get some users and plans
        users = User.objects.all()[:5]  # Get first 5 users
        plans = SubscriptionPlan.objects.all()
        
        if not users.exists():
            self.stdout.write(self.style.WARNING('⚠️ No users found for sample data'))
            return
            
        # Create user subscriptions
        for i, user in enumerate(users):
            # Skip if user already has subscription
            if UserSubscription.objects.filter(user=user).exists():
                continue
                
            # Assign different plans to different users
            if i == 0:
                plan = plans.get(plan_type='premium')
                billing_cycle = 'monthly'
            elif i == 1:
                plan = plans.get(plan_type='enterprise')
                billing_cycle = 'yearly'
            else:
                plan = plans.get(plan_type='free')
                billing_cycle = 'monthly'
            
            # Create subscription
            subscription = UserSubscription.objects.create(
                user=user,
                plan=plan,
                billing_cycle=billing_cycle,
                status='active',
                starts_at=datetime.now() - timedelta(days=30),
                expires_at=datetime.now() + timedelta(days=335 if billing_cycle == 'yearly' else 30),
                auto_renew=True,
                api_calls_used=random.randint(10, plan.api_calls_limit // 2)
            )
            
            # Create payment method for non-free users
            if plan.plan_type != 'free':
                PaymentMethod.objects.create(
                    user=user,
                    method_type='credit_card',
                    provider='stripe',
                    provider_payment_method_id=f'pm_test_{user.id}',
                    card_last_four='4242',
                    card_brand='visa',
                    card_exp_month=12,
                    card_exp_year=2026,
                    is_default=True
                )
                
                # Create some invoices
                self.create_invoices_for_subscription(subscription)
                
            self.stdout.write(f'   ✓ Created {plan.name} subscription for {user.username}')

    def create_invoices_for_subscription(self, subscription):
        """Create sample invoices for a subscription"""
        # Create a few historical invoices
        for i in range(3):
            invoice_date = datetime.now() - timedelta(days=30 * (i + 1))
            due_date = invoice_date + timedelta(days=7)
            
            # Most invoices are paid, some are pending
            status = 'paid' if i > 0 else random.choice(['paid', 'pending'])
            paid_at = invoice_date + timedelta(days=random.randint(1, 6)) if status == 'paid' else None
            
            amount = subscription.plan.price_monthly if subscription.billing_cycle == 'monthly' else subscription.plan.price_yearly
            
            Invoice.objects.create(
                subscription=subscription,
                invoice_number=f'INV-{subscription.id}-{i+1:03d}',
                amount=amount,
                status=status,
                due_date=due_date,
                paid_at=paid_at,
                payment_method='credit_card' if status == 'paid' else None,
                notes=f'Assinatura {subscription.plan.name} - {subscription.billing_cycle}'
            )

    def display_summary(self):
        """Display summary of created data"""
        total_plans = SubscriptionPlan.objects.count()
        active_plans = SubscriptionPlan.objects.filter(is_active=True).count()
        total_subscriptions = UserSubscription.objects.count()
        total_invoices = Invoice.objects.count()
        total_payment_methods = PaymentMethod.objects.count()
        
        self.stdout.write(self.style.SUCCESS(f'\n📊 Summary:'))
        self.stdout.write(f'   Subscription Plans: {total_plans} (active: {active_plans})')
        self.stdout.write(f'   User Subscriptions: {total_subscriptions}')
        self.stdout.write(f'   Payment Methods: {total_payment_methods}')
        self.stdout.write(f'   Invoices: {total_invoices}')
        
        # Show plans
        self.stdout.write(f'\n📋 Available Plans:')
        for plan in SubscriptionPlan.objects.filter(is_active=True).order_by('sort_order'):
            self.stdout.write(f'   • {plan.name} - R$ {plan.price_monthly}/mês - {plan.api_calls_limit} API calls')
            
        # Show sample subscriptions
        if total_subscriptions > 0:
            self.stdout.write(f'\n👥 Sample Subscriptions:')
            for sub in UserSubscription.objects.select_related('user', 'plan')[:5]:
                self.stdout.write(f'   • {sub.user.username} - {sub.plan.name} ({sub.status})')
