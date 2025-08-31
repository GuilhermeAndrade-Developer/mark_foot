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

    @action(detail=False, methods=['get'])
    def kpis(self, request):
        """Get key performance indicators for admin dashboard"""
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)
        last_month_start = (now - timedelta(days=60)).replace(day=1)
        last_month_end = thirty_days_ago.replace(day=1) - timedelta(days=1)
        
        # Current month metrics
        current_month_start = now.replace(day=1)
        
        # MRR Calculation
        active_subs = UserSubscription.objects.filter(status='active')
        current_mrr = sum([sub.plan.price_monthly for sub in active_subs])
        
        # Previous month MRR for growth calculation
        prev_month_subs = UserSubscription.objects.filter(
            status='active',
            started_at__lt=current_month_start
        ).exclude(
            cancelled_at__gte=current_month_start,
            cancelled_at__isnull=False
        )
        prev_mrr = sum([sub.plan.price_monthly for sub in prev_month_subs])
        mrr_growth = ((current_mrr - prev_mrr) / prev_mrr * 100) if prev_mrr > 0 else 0
        
        # Active subscribers
        active_subscribers = active_subs.count()
        prev_active_subscribers = prev_month_subs.count()
        subscriber_growth = ((active_subscribers - prev_active_subscribers) / prev_active_subscribers * 100) if prev_active_subscribers > 0 else 0
        
        # Churn rate
        cancelled_this_month = UserSubscription.objects.filter(
            cancelled_at__gte=current_month_start,
            cancelled_at__lt=now
        ).count()
        churn_rate = (cancelled_this_month / max(active_subscribers, 1)) * 100
        
        # Previous month churn for trend
        prev_month_cancelled = UserSubscription.objects.filter(
            cancelled_at__gte=last_month_start,
            cancelled_at__lt=last_month_end
        ).count()
        prev_churn_rate = (prev_month_cancelled / max(prev_active_subscribers, 1)) * 100
        churn_trend = churn_rate - prev_churn_rate
        
        # ARPU (Average Revenue Per User)
        arpu = current_mrr / max(active_subscribers, 1)
        prev_arpu = prev_mrr / max(prev_active_subscribers, 1)
        arpu_growth = ((arpu - prev_arpu) / prev_arpu * 100) if prev_arpu > 0 else 0
        
        return Response({
            'mrr': current_mrr,
            'mrr_growth': mrr_growth,
            'active_subscribers': active_subscribers,
            'subscriber_growth': subscriber_growth,
            'churn_rate': churn_rate,
            'churn_trend': churn_trend,
            'arpu': arpu,
            'arpu_growth': arpu_growth
        })

    @action(detail=False, methods=['get'])
    def revenue_chart(self, request):
        """Get revenue chart data"""
        timeframe = request.query_params.get('timeframe', '30d')
        
        # Parse timeframe
        if timeframe == '7d':
            days = 7
        elif timeframe == '30d':
            days = 30
        elif timeframe == '90d':
            days = 90
        elif timeframe == '1y':
            days = 365
        else:
            days = 30
            
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Generate daily revenue data
        labels = []
        revenue_data = []
        subscription_data = []
        
        for i in range(days + 1):
            date = start_date + timedelta(days=i)
            labels.append(date.strftime('%d/%m'))
            
            # Daily revenue from paid invoices
            daily_revenue = Invoice.objects.filter(
                paid_at__date=date,
                status='paid'
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            
            revenue_data.append(float(daily_revenue))
            
            # New subscriptions
            new_subs = UserSubscription.objects.filter(
                started_at__date=date
            ).count()
            subscription_data.append(new_subs)
        
        # Plans distribution
        plan_stats = []
        plan_distribution = UserSubscription.objects.filter(
            status='active'
        ).values('plan__name', 'plan__plan_type').annotate(count=Count('id'))
        
        total_subs = sum([item['count'] for item in plan_distribution])
        plan_colors = ['#1976D2', '#FFC107', '#4CAF50', '#FF5722']
        
        for i, item in enumerate(plan_distribution):
            percentage = (item['count'] / total_subs * 100) if total_subs > 0 else 0
            plan_stats.append({
                'name': item['plan__name'],
                'count': item['count'],
                'percentage': round(percentage, 1),
                'revenue': 0  # Calculate if needed
            })
        
        chart_data = {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Receita Diária',
                    'data': revenue_data,
                    'borderColor': '#1976D2',
                    'backgroundColor': 'rgba(25, 118, 210, 0.1)'
                },
                {
                    'label': 'Novas Assinaturas',
                    'data': subscription_data,
                    'borderColor': '#4CAF50',
                    'backgroundColor': 'rgba(76, 175, 80, 0.1)'
                }
            ]
        }
        
        plans_chart = {
            'labels': [item['name'] for item in plan_stats],
            'datasets': [{
                'data': [item['count'] for item in plan_stats],
                'backgroundColor': plan_colors[:len(plan_stats)]
            }]
        }
        
        return Response({
            'chart': chart_data,
            'plans_stats': plan_stats,
            'plans_chart': plans_chart
        })

    @action(detail=False, methods=['get'])
    def metrics(self, request):
        """Get conversion and API metrics"""
        
        # Conversion metrics (simplified for now)
        total_users = User.objects.count()
        paid_users = UserSubscription.objects.filter(
            status='active'
        ).exclude(plan__plan_type='free').count()
        
        conversion_metrics = {
            'lead_to_trial': 75.5,  # Placeholder - implement based on your tracking
            'trial_to_paid': (paid_users / max(total_users, 1)) * 100,
            'average_ltv': 450.0,  # Placeholder - calculate based on subscription data
            'customer_acquisition_cost': 85.0,  # Placeholder
            'payback_period': 2.5  # months
        }
        
        # API metrics
        today = timezone.now().date()
        month_start = timezone.now().replace(day=1).date()
        
        api_calls_today = ApiUsageLog.objects.filter(timestamp__date=today).count()
        api_calls_month = ApiUsageLog.objects.filter(timestamp__date__gte=month_start).count()
        
        # Top endpoint
        top_endpoint_data = ApiUsageLog.objects.filter(
            timestamp__date__gte=month_start
        ).values('endpoint').annotate(count=Count('id')).order_by('-count').first()
        
        top_endpoint = top_endpoint_data['endpoint'] if top_endpoint_data else 'N/A'
        
        api_metrics = {
            'calls_today': api_calls_today,
            'calls_month': api_calls_month,
            'calls_year': api_calls_month * 12,  # Estimate
            'daily_limit': 100000,  # Configure based on your infrastructure
            'monthly_limit': 3000000,
            'top_endpoint': top_endpoint,
            'endpoints_usage': [],  # Implement if needed
            'error_rate': 2.5,  # Placeholder
            'avg_response_time': 150  # ms
        }
        
        return Response({
            'conversion': conversion_metrics,
            'api': api_metrics
        })

    @action(detail=False, methods=['get'])
    def alerts(self, request):
        """Get system alerts"""
        alerts = []
        
        # Check for high churn rate
        current_month = timezone.now().replace(day=1)
        cancelled_this_month = UserSubscription.objects.filter(
            cancelled_at__gte=current_month
        ).count()
        
        active_subs = UserSubscription.objects.filter(status='active').count()
        churn_rate = (cancelled_this_month / max(active_subs, 1)) * 100
        
        if churn_rate > 10:
            alerts.append({
                'id': 'high_churn',
                'type': 'warning',
                'message': f'Taxa de churn alta este mês: {churn_rate:.1f}%',
                'created_at': timezone.now().isoformat()
            })
        
        # Check for API usage spikes
        today_calls = ApiUsageLog.objects.filter(
            timestamp__date=timezone.now().date()
        ).count()
        
        if today_calls > 50000:  # Threshold
            alerts.append({
                'id': 'high_api_usage',
                'type': 'info',
                'message': f'Alto uso da API hoje: {today_calls:,} calls',
                'created_at': timezone.now().isoformat()
            })
        
        # Check for payment failures
        failed_payments = Invoice.objects.filter(
            status='failed',
            created_at__date=timezone.now().date()
        ).count()
        
        if failed_payments > 0:
            alerts.append({
                'id': 'payment_failures',
                'type': 'error',
                'message': f'{failed_payments} falhas de pagamento hoje',
                'created_at': timezone.now().isoformat()
            })
        
        return Response({'alerts': alerts})
