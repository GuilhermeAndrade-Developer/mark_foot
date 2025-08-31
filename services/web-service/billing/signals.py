"""
Django signals for billing automation.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from .models import UserSubscription, SubscriptionPlan


@receiver(post_save, sender=User)
def create_free_subscription(sender, instance, created, **kwargs):
    """
    Automatically create a free subscription when a new user is created.
    """
    if created:
        try:
            # Check if user already has a subscription
            if hasattr(instance, 'subscription'):
                return
            
            # Get the free plan
            free_plan = SubscriptionPlan.objects.get(plan_type='free')
            
            # Create free subscription for new user
            UserSubscription.objects.create(
                user=instance,
                plan=free_plan,
                status='active',
                expires_at=timezone.now() + timezone.timedelta(days=365 * 10),  # 10 years for free
                api_calls_reset_date=timezone.now() + timezone.timedelta(days=30)
            )
            
            print(f"✅ Created free subscription for user: {instance.username}")
            
        except SubscriptionPlan.DoesNotExist:
            print(f"⚠️ Free plan not found. Cannot create subscription for user: {instance.username}")
        except Exception as e:
            print(f"❌ Error creating subscription for user {instance.username}: {e}")


@receiver(post_save, sender=UserSubscription)
def log_subscription_creation(sender, instance, created, **kwargs):
    """
    Log when a subscription is created or updated.
    """
    if created:
        print(f"🎉 New subscription created: {instance.user.username} -> {instance.plan.name}")
    else:
        print(f"📝 Subscription updated: {instance.user.username} -> {instance.plan.name} ({instance.status})")
