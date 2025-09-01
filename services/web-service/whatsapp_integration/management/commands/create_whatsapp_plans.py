from django.core.management.base import BaseCommand
from decimal import Decimal
from billing.models import SubscriptionPlan


class Command(BaseCommand):
    help = 'Create WhatsApp Premium subscription plans'

    def handle(self, *args, **options):
        """Create WhatsApp-specific subscription plans"""
        plans_data = [
            {
                'name': 'WhatsApp Premium',
                'plan_type': 'premium',
                'description': 'Plano Premium para WhatsApp - Consultas ilimitadas, análise de odds e previsões com IA',
                'price_monthly': Decimal('19.90'),
                'price_yearly': Decimal('199.00'),
                'api_calls_limit': 0,  # Unlimited
                'advanced_ai_analysis': True,
                'unlimited_reports': True,
                'white_label': False,
                'dedicated_support': False,
                'multi_tenancy': False,
                'features': {
                    'whatsapp_unlimited_queries': True,
                    'betting_odds_analysis': True,
                    'ai_predictions': True,
                    'match_alerts': True,
                    'basic_support': True
                },
                'is_active': True,
                'sort_order': 1
            },
            {
                'name': 'WhatsApp Pro',
                'plan_type': 'pro',
                'description': 'Plano Pro para WhatsApp - Tudo do Premium + Relatórios PDF, Suporte prioritário e Grupos VIP',
                'price_monthly': Decimal('49.90'),
                'price_yearly': Decimal('499.00'),
                'api_calls_limit': 0,  # Unlimited
                'advanced_ai_analysis': True,
                'unlimited_reports': True,
                'white_label': False,
                'dedicated_support': True,
                'multi_tenancy': False,
                'features': {
                    'whatsapp_unlimited_queries': True,
                    'betting_odds_analysis': True,
                    'ai_predictions': True,
                    'match_alerts': True,
                    'pdf_reports': True,
                    'priority_support': True,
                    'vip_groups': True,
                    'exclusive_insights': True,
                    'advanced_analytics': True
                },
                'is_active': True,
                'sort_order': 2
            }
        ]

        created_count = 0
        updated_count = 0

        for plan_data in plans_data:
            plan, created = SubscriptionPlan.objects.get_or_create(
                plan_type=plan_data['plan_type'],
                defaults=plan_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Created plan: {plan.name}")
                )
            else:
                # Update existing plan
                for key, value in plan_data.items():
                    setattr(plan, key, value)
                plan.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f"🔄 Updated plan: {plan.name}")
                )

        self.stdout.write(
            self.style.SUCCESS(f"\n📊 Summary:")
        )
        self.stdout.write(f"Created: {created_count} plans")
        self.stdout.write(f"Updated: {updated_count} plans")
        self.stdout.write(
            self.style.SUCCESS("✅ WhatsApp plans created successfully!")
        )
