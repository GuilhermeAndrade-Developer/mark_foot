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
from billing.models import SubscriptionPlan


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
