"""
URL configuration for billing app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SubscriptionPlanViewSet, UserSubscriptionViewSet, PaymentMethodViewSet,
    InvoiceViewSet, ApiUsageLogViewSet, SubscriptionChangeViewSet, BillingStatsViewSet
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'plans', SubscriptionPlanViewSet)
router.register(r'subscriptions', UserSubscriptionViewSet, basename='usersubscription')
router.register(r'payment-methods', PaymentMethodViewSet, basename='paymentmethod')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'usage-logs', ApiUsageLogViewSet, basename='apiusagelog')
router.register(r'subscription-changes', SubscriptionChangeViewSet, basename='subscriptionchange')
router.register(r'stats', BillingStatsViewSet, basename='billingstats')

# Admin router for administrative endpoints
admin_router = DefaultRouter()
admin_router.register(r'subscriptions', UserSubscriptionViewSet, basename='admin-usersubscription')
admin_router.register(r'stats', BillingStatsViewSet, basename='admin-billingstats')

app_name = 'billing'

urlpatterns = [
    # Public/User API endpoints
    path('api/', include(router.urls)),
    
    # Admin API endpoints  
    path('admin/', include(admin_router.urls)),
]
