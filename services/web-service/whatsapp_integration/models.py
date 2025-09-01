from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from billing.models import SubscriptionPlan, UserSubscription

class WhatsAppUser(models.Model):
    SUBSCRIPTION_STATUS = [
        ('free', 'Free'),
        ('trial', 'Trial'),
        ('premium', 'Premium'),
        ('pro', 'Pro'),
        ('expired', 'Expired'),
        ('trial_ended', 'Trial Ended'),
        ('cancelled', 'Cancelled'),
    ]
    
    phone_number = models.CharField(max_length=20, unique=True)
    display_name = models.CharField(max_length=100, blank=True)
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL)
    is_premium = models.BooleanField(default=False)
    subscription_plan = models.CharField(max_length=20, default='free')
    subscription_status = models.CharField(max_length=20, choices=SUBSCRIPTION_STATUS, default='free')
    current_plan = models.ForeignKey(SubscriptionPlan, null=True, blank=True, on_delete=models.SET_NULL)
    trial_started_at = models.DateTimeField(null=True, blank=True)
    trial_expires_at = models.DateTimeField(null=True, blank=True)
    daily_queries_count = models.IntegerField(default=0)
    last_query_date = models.DateField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.phone_number} - {self.display_name}"

    def reset_daily_queries_if_needed(self):
        """Reset daily queries count if it's a new day"""
        if self.last_query_date != timezone.now().date():
            self.daily_queries_count = 0
            self.last_query_date = timezone.now().date()
            self.save()

    def can_make_query(self):
        """Check if user can make another query"""
        self.reset_daily_queries_if_needed()
        
        # Premium users (including trial) have unlimited queries
        if self.subscription_status in ['premium', 'pro', 'trial']:
            return True
            
        # Free users: 5 queries per day
        return self.daily_queries_count < 5

    def increment_query_count(self):
        """Increment the daily query count"""
        self.reset_daily_queries_if_needed()
        self.daily_queries_count += 1
        self.save()
    
    def get_daily_limit(self):
        """Get daily query limit based on subscription"""
        if self.subscription_status in ['premium', 'pro', 'trial']:
            return None  # Unlimited
        return 5  # Free tier
    
    @property
    def is_trial_active(self):
        """Check if trial is still active"""
        if self.subscription_status != 'trial' or not self.trial_expires_at:
            return False
        return timezone.now() < self.trial_expires_at
    
    @property
    def trial_days_remaining(self):
        """Get remaining trial days"""
        if not self.is_trial_active:
            return 0
        return (self.trial_expires_at - timezone.now()).days


class WhatsAppPaymentIntent(models.Model):
    PAYMENT_PROVIDERS = [
        ('stripe', 'Stripe'),
        ('pagseguro', 'PagSeguro'),
        ('mercadopago', 'Mercado Pago'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    whatsapp_user = models.ForeignKey(WhatsAppUser, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    payment_provider = models.CharField(max_length=20, choices=PAYMENT_PROVIDERS)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='BRL')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Payment gateway IDs
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)
    pagseguro_transaction_id = models.CharField(max_length=255, blank=True)
    mercadopago_payment_id = models.CharField(max_length=255, blank=True)
    
    # Payment URL for user
    payment_url = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'whatsapp_payment_intents'
        
    def __str__(self):
        return f"{self.whatsapp_user.phone_number} - {self.plan.name} - {self.status}"


class WhatsAppSubscriptionEvent(models.Model):
    EVENT_TYPES = [
        ('subscription_created', 'Subscription Created'),
        ('subscription_renewed', 'Subscription Renewed'),
        ('subscription_cancelled', 'Subscription Cancelled'),
        ('subscription_expired', 'Subscription Expired'),
        ('trial_started', 'Trial Started'),
        ('trial_ended', 'Trial Ended'),
        ('payment_successful', 'Payment Successful'),
        ('payment_failed', 'Payment Failed'),
    ]
    
    whatsapp_user = models.ForeignKey(WhatsAppUser, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    data = models.JSONField(default=dict)
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'whatsapp_subscription_events'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.whatsapp_user.phone_number} - {self.get_event_type_display()}"

class WhatsAppSession(models.Model):
    whatsapp_user = models.ForeignKey(WhatsAppUser, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100, unique=True)
    context_data = models.JSONField(default=dict)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Session {self.session_id} - {self.whatsapp_user.phone_number}"

class WhatsAppMessage(models.Model):
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('interactive', 'Interactive'),
        ('image', 'Image'),
        ('document', 'Document'),
    ]
    
    whatsapp_user = models.ForeignKey(WhatsAppUser, on_delete=models.CASCADE)
    message_id = models.CharField(max_length=100, unique=True)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    content = models.TextField()
    is_incoming = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        direction = "IN" if self.is_incoming else "OUT"
        return f"{direction} - {self.whatsapp_user.phone_number} - {self.message_type}"
