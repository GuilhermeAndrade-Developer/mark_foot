"""
Serializers for billing and subscription management.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    SubscriptionPlan, UserSubscription, PaymentMethod, 
    Invoice, ApiUsageLog, SubscriptionChange
)


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Serializer for subscription plans"""
    
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'plan_type', 'description', 
            'price_monthly', 'price_yearly', 'api_calls_limit',
            'advanced_ai_analysis', 'unlimited_reports', 'white_label',
            'dedicated_support', 'multi_tenancy', 'features', 'is_active'
        ]
        read_only_fields = ['id']


class UserSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for user subscriptions"""
    plan = SubscriptionPlanSerializer(read_only=True)
    plan_id = serializers.IntegerField(write_only=True)
    days_remaining = serializers.ReadOnlyField()
    api_calls_remaining = serializers.ReadOnlyField()
    api_usage_percentage = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = UserSubscription
        fields = [
            'id', 'plan', 'plan_id', 'status', 'billing_cycle',
            'started_at', 'expires_at', 'cancelled_at',
            'api_calls_used', 'api_calls_reset_date',
            'auto_renewal', 'days_remaining', 'api_calls_remaining',
            'api_usage_percentage', 'is_expired'
        ]
        read_only_fields = [
            'id', 'started_at', 'api_calls_used', 'api_calls_reset_date',
            'stripe_subscription_id', 'pagseguro_subscription_id'
        ]


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer for payment methods"""
    
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'payment_type', 'card_last_four', 'card_brand',
            'card_exp_month', 'card_exp_year', 'is_default', 'is_active'
        ]
        read_only_fields = [
            'id', 'stripe_payment_method_id', 'pagseguro_payment_method_id'
        ]


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for invoices"""
    subscription_plan = serializers.CharField(source='subscription.plan.name', read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'subscription_plan', 'subtotal',
            'tax_amount', 'discount_amount', 'total_amount', 'currency',
            'status', 'issue_date', 'due_date', 'paid_at',
            'billing_period_start', 'billing_period_end'
        ]
        read_only_fields = [
            'id', 'invoice_number', 'stripe_invoice_id', 'pagseguro_invoice_id'
        ]


class ApiUsageLogSerializer(serializers.ModelSerializer):
    """Serializer for API usage logs"""
    
    class Meta:
        model = ApiUsageLog
        fields = [
            'id', 'endpoint', 'method', 'response_status',
            'response_time_ms', 'timestamp'
        ]
        read_only_fields = ['id', 'user', 'subscription', 'ip_address', 'user_agent']


class SubscriptionChangeSerializer(serializers.ModelSerializer):
    """Serializer for subscription changes"""
    old_plan_name = serializers.CharField(source='old_plan.name', read_only=True)
    new_plan_name = serializers.CharField(source='new_plan.name', read_only=True)
    
    class Meta:
        model = SubscriptionChange
        fields = [
            'id', 'change_type', 'old_plan_name', 'new_plan_name',
            'reason', 'prorated_amount', 'effective_date', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SubscriptionStatsSerializer(serializers.Serializer):
    """Serializer for subscription statistics"""
    total_users = serializers.IntegerField()
    active_subscriptions = serializers.IntegerField()
    plan_distribution = serializers.DictField()
    monthly_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    api_usage_stats = serializers.DictField()


class UserSubscriptionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating user subscriptions"""
    
    class Meta:
        model = UserSubscription
        fields = ['plan_id', 'billing_cycle']
    
    def create(self, validated_data):
        user = self.context['request'].user
        plan = SubscriptionPlan.objects.get(id=validated_data['plan_id'])
        
        # Calculate expiration date based on billing cycle
        from dateutil.relativedelta import relativedelta
        from django.utils import timezone
        
        now = timezone.now()
        if validated_data['billing_cycle'] == 'yearly':
            expires_at = now + relativedelta(years=1)
        else:
            expires_at = now + relativedelta(months=1)
        
        # Create subscription
        subscription = UserSubscription.objects.create(
            user=user,
            plan=plan,
            billing_cycle=validated_data['billing_cycle'],
            expires_at=expires_at,
            api_calls_reset_date=now + relativedelta(months=1)
        )
        
        return subscription
