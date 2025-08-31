"""
API Views for billing and subscription management.
"""

from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta

from .models import (
    SubscriptionPlan, UserSubscription, PaymentMethod, 
    Invoice, ApiUsageLog, SubscriptionChange
)
from .serializers import (
    SubscriptionPlanSerializer, UserSubscriptionSerializer, PaymentMethodSerializer,
    InvoiceSerializer, ApiUsageLogSerializer, SubscriptionChangeSerializer,
    SubscriptionStatsSerializer, UserSubscriptionCreateSerializer
)


class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for subscription plans (read-only for users)"""
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]  # Public endpoint
    
    def get_queryset(self):
        """Filter plans based on user permissions"""
        queryset = super().get_queryset()
        return queryset.order_by('sort_order', 'price_monthly')


class UserSubscriptionViewSet(viewsets.ModelViewSet):
    """ViewSet for user subscriptions"""
    serializer_class = UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter subscriptions to current user only"""
        if self.request.user.is_staff:
            return UserSubscription.objects.all().select_related('plan', 'user')
        return UserSubscription.objects.filter(user=self.request.user).select_related('plan')
    
    def get_serializer_class(self):
        """Use different serializer for creation"""
        if self.action == 'create':
            return UserSubscriptionCreateSerializer
        return super().get_serializer_class()
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's subscription"""
        try:
            subscription = UserSubscription.objects.get(user=request.user)
            serializer = self.get_serializer(subscription)
            return Response(serializer.data)
        except UserSubscription.DoesNotExist:
            # Create default free subscription
            free_plan = SubscriptionPlan.objects.get(plan_type='free')
            subscription = UserSubscription.objects.create(
                user=request.user,
                plan=free_plan,
                expires_at=timezone.now() + timedelta(days=365 * 10),  # 10 years for free
                api_calls_reset_date=timezone.now() + timedelta(days=30)
            )
            serializer = self.get_serializer(subscription)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def change_plan(self, request, pk=None):
        """Change subscription plan"""
        subscription = self.get_object()
        new_plan_id = request.data.get('plan_id')
        
        if not new_plan_id:
            return Response(
                {'error': 'plan_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            new_plan = SubscriptionPlan.objects.get(id=new_plan_id, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            return Response(
                {'error': 'Invalid plan'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Determine change type
        old_price = subscription.plan.price_monthly
        new_price = new_plan.price_monthly
        
        if new_price > old_price:
            change_type = 'upgrade'
        elif new_price < old_price:
            change_type = 'downgrade'
        else:
            change_type = 'renewal'
        
        # Create subscription change record
        SubscriptionChange.objects.create(
            user=request.user,
            old_plan=subscription.plan,
            new_plan=new_plan,
            change_type=change_type,
            reason=request.data.get('reason', ''),
            effective_date=timezone.now()
        )
        
        # Update subscription
        subscription.plan = new_plan
        subscription.save()
        
        serializer = self.get_serializer(subscription)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel subscription"""
        subscription = self.get_object()
        
        if subscription.status == 'cancelled':
            return Response(
                {'error': 'Subscription is already cancelled'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        subscription.status = 'cancelled'
        subscription.cancelled_at = timezone.now()
        subscription.auto_renewal = False
        subscription.save()
        
        # Create change record
        SubscriptionChange.objects.create(
            user=request.user,
            old_plan=subscription.plan,
            new_plan=subscription.plan,  # Same plan, just cancelled
            change_type='cancellation',
            reason=request.data.get('reason', ''),
            effective_date=timezone.now()
        )
        
        serializer = self.get_serializer(subscription)
        return Response(serializer.data)


class PaymentMethodViewSet(viewsets.ModelViewSet):
    """ViewSet for payment methods"""
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter payment methods to current user only"""
        return PaymentMethod.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set user when creating payment method"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set payment method as default"""
        payment_method = self.get_object()
        
        # Remove default from other payment methods
        PaymentMethod.objects.filter(user=request.user).update(is_default=False)
        
        # Set this one as default
        payment_method.is_default = True
        payment_method.save()
        
        serializer = self.get_serializer(payment_method)
        return Response(serializer.data)


class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for invoices (read-only)"""
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter invoices to current user only"""
        if self.request.user.is_staff:
            return Invoice.objects.all().select_related('user', 'subscription__plan')
        return Invoice.objects.filter(user=self.request.user).select_related('subscription__plan')


class ApiUsageLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for API usage logs (read-only)"""
    serializer_class = ApiUsageLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter usage logs to current user only"""
        if self.request.user.is_staff:
            return ApiUsageLog.objects.all().select_related('user', 'subscription')
        return ApiUsageLog.objects.filter(user=self.request.user).select_related('subscription')
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get usage summary for current user"""
        user = request.user
        
        # Get current month usage
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        monthly_usage = ApiUsageLog.objects.filter(
            user=user,
            timestamp__gte=month_start
        ).count()
        
        # Get usage by endpoint
        usage_by_endpoint = ApiUsageLog.objects.filter(
            user=user,
            timestamp__gte=month_start
        ).values('endpoint').annotate(count=Count('id')).order_by('-count')[:10]
        
        # Get subscription info
        try:
            subscription = UserSubscription.objects.get(user=user)
            limit = subscription.plan.api_calls_limit
            remaining = subscription.api_calls_remaining
            percentage = subscription.api_usage_percentage
        except UserSubscription.DoesNotExist:
            limit = 100  # Default for free
            remaining = max(0, limit - monthly_usage)
            percentage = (monthly_usage / limit) * 100 if limit > 0 else 0
        
        return Response({
            'monthly_usage': monthly_usage,
            'limit': limit,
            'remaining': remaining,
            'percentage': round(percentage, 2),
            'usage_by_endpoint': list(usage_by_endpoint)
        })


class SubscriptionChangeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for subscription changes (read-only)"""
    serializer_class = SubscriptionChangeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter changes to current user only"""
        if self.request.user.is_staff:
            return SubscriptionChange.objects.all().select_related('user', 'old_plan', 'new_plan')
        return SubscriptionChange.objects.filter(user=self.request.user).select_related('old_plan', 'new_plan')


class BillingStatsViewSet(viewsets.ViewSet):
    """ViewSet for billing statistics (admin only)"""
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get billing dashboard statistics"""
        
        # Total users and subscriptions
        total_users = User.objects.count()
        active_subscriptions = UserSubscription.objects.filter(status='active').count()
        
        # Plan distribution
        plan_distribution = UserSubscription.objects.filter(
            status='active'
        ).values('plan__name').annotate(count=Count('id'))
        
        # Monthly revenue (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        monthly_revenue = Invoice.objects.filter(
            status='paid',
            paid_at__gte=thirty_days_ago
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # API usage stats
        api_usage_stats = {
            'total_calls_today': ApiUsageLog.objects.filter(
                timestamp__date=timezone.now().date()
            ).count(),
            'total_calls_month': ApiUsageLog.objects.filter(
                timestamp__gte=timezone.now().replace(day=1)
            ).count(),
            'top_endpoints': list(ApiUsageLog.objects.filter(
                timestamp__gte=thirty_days_ago
            ).values('endpoint').annotate(count=Count('id')).order_by('-count')[:5])
        }
        
        stats = {
            'total_users': total_users,
            'active_subscriptions': active_subscriptions,
            'plan_distribution': {item['plan__name']: item['count'] for item in plan_distribution},
            'monthly_revenue': monthly_revenue,
            'api_usage_stats': api_usage_stats
        }
        
        serializer = SubscriptionStatsSerializer(stats)
        return Response(serializer.data)
