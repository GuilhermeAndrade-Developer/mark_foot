#!/usr/bin/env python
import os
import sys
import django

# Adicionar o caminho do projeto ao PYTHONPATH
sys.path.append('/app')

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mark_foot_backend.settings')
django.setup()

from billing.models import SubscriptionPlan
from decimal import Decimal

def create_plans():
    # Free Plan
    free, created = SubscriptionPlan.objects.get_or_create(
        plan_type='free',
        defaults={
            'name': 'Free',
            'description': 'Plano gratuito',
            'price_monthly': Decimal('0.00'),
            'price_yearly': Decimal('0.00'),
            'api_calls_limit': 100,
            'is_active': True,
            'sort_order': 1
        }
    )
    print(f'Free plan created: {created}')

    # Premium Plan  
    premium, created = SubscriptionPlan.objects.get_or_create(
        plan_type='premium',
        defaults={
            'name': 'Premium',
            'description': 'Plano premium',
            'price_monthly': Decimal('19.90'),
            'price_yearly': Decimal('199.00'),
            'api_calls_limit': 10000,
            'is_active': True,
            'sort_order': 2
        }
    )
    print(f'Premium plan created: {created}')

    # Enterprise Plan
    enterprise, created = SubscriptionPlan.objects.get_or_create(
        plan_type='enterprise',
        defaults={
            'name': 'Enterprise',
            'description': 'Plano empresarial',
            'price_monthly': Decimal('499.00'),
            'price_yearly': Decimal('4990.00'),
            'api_calls_limit': 100000,
            'is_active': True,
            'sort_order': 3
        }
    )
    print(f'Enterprise plan created: {created}')

    print(f'Total plans: {SubscriptionPlan.objects.count()}')

if __name__ == '__main__':
    create_plans()
