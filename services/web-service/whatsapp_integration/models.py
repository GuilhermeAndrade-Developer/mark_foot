from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class WhatsAppUser(models.Model):
    phone_number = models.CharField(max_length=20, unique=True)
    display_name = models.CharField(max_length=100, blank=True)
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL)
    is_premium = models.BooleanField(default=False)
    subscription_plan = models.CharField(max_length=20, default='free')
    daily_queries_count = models.IntegerField(default=0)
    last_query_date = models.DateField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

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
        if self.is_premium:
            return True
        return self.daily_queries_count < 5  # Free users: 5 queries per day

    def increment_query_count(self):
        """Increment the daily query count"""
        self.reset_daily_queries_if_needed()
        self.daily_queries_count += 1
        self.save()

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
