#!/usr/bin/env python3
"""
Seeder for billing subscription plans.
"""

import os
import sys
import django

# Add the project root to Python path
sys.path.append('/app')

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mark_foot_backend.settings')
django.setup()

from django.db import transaction
from billing.models import SubscriptionPlan, UserSubscription, Invoice, PaymentMethod
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from decimal import Decimal
import random


def seed_sample_billing_data():
    """Create sample billing data for testing dashboard"""
    
    print("🚀 Creating sample billing data...")
    
    with transaction.atomic():
        # Get or create some test users
        users = []
        for i, (first_name, last_name, email) in enumerate([
            ('João', 'Silva', 'joao.silva@empresa.com'),
            ('Maria', 'Santos', 'maria.santos@startup.io'),
            ('Pedro', 'Costa', 'pedro.costa@tech.com'),
            ('Ana', 'Oliveira', 'ana.oliveira@digital.com'),
            ('Carlos', 'Ferreira', 'carlos.ferreira@corp.com')
        ]):
            user, created = User.objects.get_or_create(
                username=f'user_{i+1}',
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'is_active': True
                }
            )
            users.append(user)
            if created:
                print(f'✅ Created user: {user.username} ({first_name} {last_name})')
        
        # Get plans
        free_plan = SubscriptionPlan.objects.get(plan_type='free')
        premium_plan = SubscriptionPlan.objects.get(plan_type='premium')
        enterprise_plan = SubscriptionPlan.objects.get(plan_type='enterprise')
        
        # Create subscriptions for users
        subscriptions = []
        for i, user in enumerate(users):
            # Distribute users across plans
            if i == 0:
                plan = enterprise_plan
                billing_cycle = 'yearly'
            elif i <= 2:
                plan = premium_plan
                billing_cycle = 'monthly'
            else:
                plan = free_plan
                billing_cycle = 'monthly'
            
            # Update existing subscription or create new one
            subscription, created = UserSubscription.objects.update_or_create(
                user=user,
                defaults={
                    'plan': plan,
                    'status': random.choice(['active', 'active', 'active', 'pending']),
                    'billing_cycle': billing_cycle,
                    'started_at': datetime.now() - timedelta(days=random.randint(30, 365)),
                    'expires_at': datetime.now() + timedelta(days=random.randint(30, 365)),
                    'api_calls_used': random.randint(0, plan.api_calls_limit // 2),
                    'api_calls_reset_date': datetime.now() + timedelta(days=30),
                    'auto_renewal': True
                }
            )
            subscriptions.append(subscription)
            if created:
                print(f'✅ Created subscription: {user.username} -> {plan.name}')
            else:
                print(f'🔄 Updated subscription: {user.username} -> {plan.name}')
        
        # Create payment methods
        payment_methods = []
        for user in users[:3]:  # Only for paid plan users
            payment_method, created = PaymentMethod.objects.get_or_create(
                user=user,
                payment_type='credit_card',
                defaults={
                    'card_last_four': str(random.randint(1000, 9999)),
                    'card_brand': random.choice(['Visa', 'Mastercard', 'Elo']),
                    'card_exp_month': random.randint(1, 12),
                    'card_exp_year': random.randint(2025, 2030),
                    'is_default': True,
                    'is_active': True
                }
            )
            payment_methods.append(payment_method)
            if created:
                print(f'✅ Created payment method for: {user.username}')
        
        # Create sample invoices
        invoices_created = 0
        for subscription in subscriptions:
            if subscription.plan.plan_type == 'free':
                continue  # Free plans don't have invoices
            
            # Create 2-5 invoices per subscription
            num_invoices = random.randint(2, 5)
            for i in range(num_invoices):
                # Calculate invoice dates
                issue_date = datetime.now() - timedelta(days=random.randint(30, 180))
                due_date = issue_date + timedelta(days=30)
                
                # Calculate amounts
                base_amount = subscription.plan.price_monthly if subscription.billing_cycle == 'monthly' else subscription.plan.price_yearly
                tax_amount = base_amount * Decimal('0.1')  # 10% tax
                discount_amount = Decimal('0.00')
                if random.random() < 0.2:  # 20% chance of discount
                    discount_amount = base_amount * Decimal('0.1')  # 10% discount
                
                total_amount = base_amount + tax_amount - discount_amount
                
                # Determine status based on due date
                if due_date < datetime.now() - timedelta(days=30):
                    status = random.choice(['paid', 'paid', 'paid', 'refunded'])
                    paid_at = due_date + timedelta(days=random.randint(1, 5)) if status == 'paid' else None
                elif due_date < datetime.now():
                    status = random.choice(['paid', 'overdue'])
                    paid_at = due_date + timedelta(days=random.randint(1, 5)) if status == 'paid' else None
                else:
                    status = random.choice(['sent', 'paid'])
                    paid_at = datetime.now() - timedelta(days=random.randint(1, 10)) if status == 'paid' else None
                
                invoice = Invoice.objects.create(
                    user=subscription.user,
                    subscription=subscription,
                    subtotal=base_amount,
                    tax_amount=tax_amount,
                    discount_amount=discount_amount,
                    total_amount=total_amount,
                    status=status,
                    issue_date=issue_date,
                    due_date=due_date,
                    paid_at=paid_at,
                    billing_period_start=issue_date,
                    billing_period_end=due_date,
                )
                invoices_created += 1
        
        print(f'✅ Created {invoices_created} sample invoices')
        
        print('\n🎉 Sample billing data created successfully!')
        
        # Display summary
        print(f'\n📊 Billing Data Summary:')
        print(f'   Users: {User.objects.count()}')
        print(f'   Subscriptions: {UserSubscription.objects.count()}')
        print(f'   - Active: {UserSubscription.objects.filter(status="active").count()}')
        print(f'   - Free: {UserSubscription.objects.filter(plan__plan_type="free").count()}')
        print(f'   - Premium: {UserSubscription.objects.filter(plan__plan_type="premium").count()}')
        print(f'   - Enterprise: {UserSubscription.objects.filter(plan__plan_type="enterprise").count()}')
        print(f'   Payment Methods: {PaymentMethod.objects.count()}')
        print(f'   Invoices: {Invoice.objects.count()}')
        print(f'   - Paid: {Invoice.objects.filter(status="paid").count()}')
        print(f'   - Pending: {Invoice.objects.filter(status="sent").count()}')
        print(f'   - Overdue: {Invoice.objects.filter(status="overdue").count()}')


def seed_billing_plans():
    """Create initial subscription plans"""
    
    print("🚀 Starting billing plans seeder...")
    
    with transaction.atomic():
        # Free Plan
        free_plan, created = SubscriptionPlan.objects.get_or_create(
            plan_type='free',
            defaults={
                'name': 'Free',
                'description': 'Plano gratuito com funcionalidades básicas',
                'price_monthly': 0.00,
                'price_yearly': 0.00,
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
            print(f'✅ Created Free plan: {free_plan}')
        else:
            print(f'⚠️ Free plan already exists: {free_plan}')
        
        # Premium Plan
        premium_plan, created = SubscriptionPlan.objects.get_or_create(
            plan_type='premium',
            defaults={
                'name': 'Premium',
                'description': 'Plano premium com análises avançadas de IA e relatórios ilimitados',
                'price_monthly': 19.90,
                'price_yearly': 199.00,  # 2 months free
                'api_calls_limit': 10000,  # Much higher limit
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
            print(f'✅ Created Premium plan: {premium_plan}')
        else:
            print(f'⚠️ Premium plan already exists: {premium_plan}')
        
        # Enterprise Plan
        enterprise_plan, created = SubscriptionPlan.objects.get_or_create(
            plan_type='enterprise',
            defaults={
                'name': 'Enterprise',
                'description': 'Plano empresarial com multi-tenancy, suporte dedicado e white-label',
                'price_monthly': 499.00,
                'price_yearly': 4990.00,  # 2 months free
                'api_calls_limit': 100000,  # Very high limit
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
            print(f'✅ Created Enterprise plan: {enterprise_plan}')
        else:
            print(f'⚠️ Enterprise plan already exists: {enterprise_plan}')
        
        print('\n🎉 Billing plans seeder completed!')
        
        # Display summary
        total_plans = SubscriptionPlan.objects.count()
        active_plans = SubscriptionPlan.objects.filter(is_active=True).count()
        
        print(f'\n📊 Summary:')
        print(f'   Total plans: {total_plans}')
        print(f'   Active plans: {active_plans}')
        
        # Show plans
        print(f'\n📋 Available Plans:')
        for plan in SubscriptionPlan.objects.filter(is_active=True).order_by('sort_order'):
            print(f'   • {plan.name} - R$ {plan.price_monthly}/mês - {plan.api_calls_limit} API calls')


if __name__ == '__main__':
    seed_billing_plans()
    seed_sample_billing_data()
