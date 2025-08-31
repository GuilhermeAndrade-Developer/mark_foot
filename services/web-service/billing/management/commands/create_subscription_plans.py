"""
Management command to create initial subscription plans.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from billing.models import SubscriptionPlan


class Command(BaseCommand):
    help = 'Create initial subscription plans (Free, Premium, Enterprise)'
    
    def handle(self, *args, **options):
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
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created Free plan: {free_plan}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Free plan already exists: {free_plan}')
                )
            
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
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created Premium plan: {premium_plan}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Premium plan already exists: {premium_plan}')
                )
            
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
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created Enterprise plan: {enterprise_plan}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Enterprise plan already exists: {enterprise_plan}')
                )
            
            self.stdout.write(
                self.style.SUCCESS('\n🎉 Subscription plans setup completed!')
            )
            
            # Display summary
            total_plans = SubscriptionPlan.objects.count()
            active_plans = SubscriptionPlan.objects.filter(is_active=True).count()
            
            self.stdout.write(
                self.style.SUCCESS(f'\n📊 Summary:')
            )
            self.stdout.write(f'   Total plans: {total_plans}')
            self.stdout.write(f'   Active plans: {active_plans}')
            
            # Show plans
            self.stdout.write(f'\n📋 Available Plans:')
            for plan in SubscriptionPlan.objects.filter(is_active=True).order_by('sort_order'):
                self.stdout.write(
                    f'   • {plan.name} - R$ {plan.price_monthly}/mês - {plan.api_calls_limit} API calls'
                )
