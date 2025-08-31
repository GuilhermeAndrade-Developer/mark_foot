"""
Models for billing and subscription management system.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import uuid


class SubscriptionPlan(models.Model):
    """
    Plans available for subscription (Free, Premium, Enterprise)
    """
    PLAN_TYPES = [
        ('free', 'Free'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES, unique=True)
    description = models.TextField()
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Limits and features
    api_calls_limit = models.IntegerField(default=100, help_text="API calls per month")
    advanced_ai_analysis = models.BooleanField(default=False)
    unlimited_reports = models.BooleanField(default=False)
    white_label = models.BooleanField(default=False)
    dedicated_support = models.BooleanField(default=False)
    multi_tenancy = models.BooleanField(default=False)
    
    # Additional features as JSON for flexibility
    features = models.JSONField(default=dict, blank=True)
    
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subscription_plans'
        ordering = ['sort_order', 'price_monthly']
        indexes = [
            models.Index(fields=['plan_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} - R$ {self.price_monthly}/mês"


class UserSubscription(models.Model):
    """
    User's current subscription
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('pending', 'Pending Payment'),
        ('suspended', 'Suspended'),
    ]
    
    BILLING_CYCLE_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLE_CHOICES, default='monthly')
    
    # Subscription period
    started_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    # API usage tracking
    api_calls_used = models.IntegerField(default=0)
    api_calls_reset_date = models.DateTimeField()
    
    # Payment info
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    pagseguro_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Auto-renewal
    auto_renewal = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_subscriptions'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['plan']),
            models.Index(fields=['status']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name} ({self.status})"
    
    @property
    def is_expired(self):
        """Check if subscription is expired"""
        return timezone.now() > self.expires_at
    
    @property
    def days_remaining(self):
        """Get days remaining in subscription"""
        if self.is_expired:
            return 0
        return (self.expires_at - timezone.now()).days
    
    @property
    def api_calls_remaining(self):
        """Get remaining API calls for current period"""
        return max(0, self.plan.api_calls_limit - self.api_calls_used)
    
    @property
    def api_usage_percentage(self):
        """Get API usage percentage"""
        if self.plan.api_calls_limit == 0:
            return 0
        return min(100, (self.api_calls_used / self.plan.api_calls_limit) * 100)
    
    def reset_api_usage(self):
        """Reset API usage counter (called monthly)"""
        self.api_calls_used = 0
        # Set next reset to next month
        from dateutil.relativedelta import relativedelta
        self.api_calls_reset_date = timezone.now() + relativedelta(months=1)
        self.save(update_fields=['api_calls_used', 'api_calls_reset_date'])


class PaymentMethod(models.Model):
    """
    User's payment methods (Credit Card, PIX, etc.)
    """
    PAYMENT_TYPES = [
        ('credit_card', 'Credit Card'),
        ('pix', 'PIX'),
        ('boleto', 'Boleto'),
        ('paypal', 'PayPal'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    
    # Card info (encrypted/tokenized)
    card_last_four = models.CharField(max_length=4, blank=True)
    card_brand = models.CharField(max_length=20, blank=True)
    card_exp_month = models.IntegerField(null=True, blank=True)
    card_exp_year = models.IntegerField(null=True, blank=True)
    
    # Payment gateway tokens
    stripe_payment_method_id = models.CharField(max_length=255, blank=True)
    pagseguro_payment_method_id = models.CharField(max_length=255, blank=True)
    
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_methods'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_default']),
        ]
    
    def __str__(self):
        if self.payment_type == 'credit_card':
            return f"{self.card_brand} **** {self.card_last_four}"
        return f"{self.get_payment_type_display()}"


class Invoice(models.Model):
    """
    Billing invoices for subscriptions
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    invoice_number = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, related_name='invoices')
    
    # Invoice details
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    currency = models.CharField(max_length=3, default='BRL')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Dates
    issue_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField()
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # Payment gateway references
    stripe_invoice_id = models.CharField(max_length=255, blank=True)
    pagseguro_invoice_id = models.CharField(max_length=255, blank=True)
    
    # Invoice metadata
    billing_period_start = models.DateTimeField()
    billing_period_end = models.DateTimeField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'invoices'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['subscription']),
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Generate invoice number: INV-YYYY-MM-XXXXXX
            from datetime import datetime
            now = datetime.now()
            last_invoice = Invoice.objects.filter(
                invoice_number__startswith=f"INV-{now.year:04d}-{now.month:02d}"
            ).order_by('-created_at').first()
            
            if last_invoice:
                last_number = int(last_invoice.invoice_number.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.invoice_number = f"INV-{now.year:04d}-{now.month:02d}-{new_number:06d}"
        
        super().save(*args, **kwargs)


class ApiUsageLog(models.Model):
    """
    Track API usage for billing purposes
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_usage_logs')
    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, related_name='usage_logs')
    
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    response_status = models.IntegerField()
    
    # Request metadata
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    # Performance metrics
    response_time_ms = models.IntegerField(null=True, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'api_usage_logs'
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['subscription']),
            models.Index(fields=['endpoint']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.endpoint} ({self.timestamp})"


class SubscriptionChange(models.Model):
    """
    Track subscription plan changes
    """
    CHANGE_TYPES = [
        ('upgrade', 'Upgrade'),
        ('downgrade', 'Downgrade'),
        ('renewal', 'Renewal'),
        ('cancellation', 'Cancellation'),
        ('reactivation', 'Reactivation'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscription_changes')
    old_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, related_name='old_subscriptions', null=True)
    new_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, related_name='new_subscriptions')
    
    change_type = models.CharField(max_length=20, choices=CHANGE_TYPES)
    reason = models.TextField(blank=True)
    
    # Financial impact
    prorated_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    effective_date = models.DateTimeField(default=timezone.now)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'subscription_changes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['change_type']),
            models.Index(fields=['effective_date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_change_type_display()}"
