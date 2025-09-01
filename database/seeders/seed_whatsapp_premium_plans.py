#!/usr/bin/env python3
"""
WhatsApp Premium Plans Seeder
Creates subscription plans specifically for WhatsApp integration
"""

import os
import sys
import django

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mark_foot_backend.settings')
django.setup()

from decimal import Decimal
from billing.models import SubscriptionPlan


def create_whatsapp_plans():
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
            print(f"✅ Created plan: {plan.name}")
        else:
            # Update existing plan
            for key, value in plan_data.items():
                setattr(plan, key, value)
            plan.save()
            updated_count += 1
            print(f"🔄 Updated plan: {plan.name}")

    print(f"\n📊 Summary:")
    print(f"Created: {created_count} plans")
    print(f"Updated: {updated_count} plans")


def main():
    """Main function"""
    print("🚀 Creating WhatsApp Premium Plans...")
    
    try:
        create_whatsapp_plans()
        print("\n✅ WhatsApp plans seeder completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error running seeder: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
