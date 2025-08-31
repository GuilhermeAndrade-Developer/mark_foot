#!/usr/bin/env python
import os
import sys
import django

# Adicionar o caminho do projeto ao PYTHONPATH
sys.path.append('/app')

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mark_foot_backend.settings')
django.setup()

from django.contrib.auth.models import User
from billing.models import SubscriptionPlan, UserSubscription, PaymentMethod, Invoice
from decimal import Decimal
from datetime import datetime, timedelta
import pytz

def create_sample_data():
    # Criar um usuário de teste se não existir
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@markfoot.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        user.set_password('admin123')
        user.save()

    print(f'User created: {created}')

    # Buscar plano Premium
    premium_plan = SubscriptionPlan.objects.filter(plan_type='premium').first()
    if premium_plan:
        # Criar assinatura Premium para o usuário
        subscription, created = UserSubscription.objects.get_or_create(
            user=user,
            defaults={
                'plan': premium_plan,
                'status': 'active',
                'billing_cycle': 'monthly',
                'started_at': datetime.now(pytz.UTC),
                'expires_at': datetime.now(pytz.UTC) + timedelta(days=30),
                'api_calls_used': 2547,
                'api_calls_reset_date': datetime.now(pytz.UTC) + timedelta(days=15),
                'auto_renewal': True
            }
        )
        print(f'Subscription created: {created}')
        
        # Criar método de pagamento
        payment_method, created = PaymentMethod.objects.get_or_create(
            user=user,
            defaults={
                'payment_type': 'credit_card',
                'card_last_four': '4532',
                'card_brand': 'Visa',
                'card_exp_month': 12,
                'card_exp_year': 2025,
                'is_default': True,
                'is_active': True
            }
        )
        print(f'Payment method created: {created}')
        
        # Criar invoice
        invoice, created = Invoice.objects.get_or_create(
            user=user,
            subscription=subscription,
            defaults={
                'invoice_number': 'INV-2024-001',
                'subtotal': Decimal('19.90'),
                'tax_amount': Decimal('0.00'),
                'discount_amount': Decimal('0.00'),
                'total_amount': Decimal('19.90'),
                'currency': 'BRL',
                'status': 'paid',
                'issue_date': datetime.now(pytz.UTC),
                'due_date': datetime.now(pytz.UTC) + timedelta(days=7),
                'paid_at': datetime.now(pytz.UTC),
                'billing_period_start': datetime.now(pytz.UTC),
                'billing_period_end': datetime.now(pytz.UTC) + timedelta(days=30)
            }
        )
        print(f'Invoice created: {created}')

    print('Sample data created successfully!')

if __name__ == '__main__':
    create_sample_data()
