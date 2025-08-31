"""
API Views for billing and subscription management.
"""

import logging
from datetime import timedelta
from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Count, Sum, Q
from django.utils import timezone

from .models import (
    SubscriptionPlan, UserSubscription, PaymentMethod, 
    Invoice, ApiUsageLog, SubscriptionChange
)
from .serializers import (
    SubscriptionPlanSerializer, UserSubscriptionSerializer, PaymentMethodSerializer,
    InvoiceSerializer, ApiUsageLogSerializer, SubscriptionChangeSerializer,
    SubscriptionStatsSerializer, UserSubscriptionCreateSerializer
)

logger = logging.getLogger(__name__)


class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for subscription plans (read-only for users)"""
    queryset = SubscriptionPlan.objects.filter(is_active=True).order_by('sort_order')
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def features_comparison(self, request):
        """Get features comparison between all plans"""
        plans = self.get_queryset()
        comparison = []
        
        for plan in plans:
            comparison.append({
                'id': plan.id,
                'name': plan.name,
                'plan_type': plan.plan_type,
                'price_monthly': plan.price_monthly,
                'price_yearly': plan.price_yearly,
                'api_calls_limit': plan.api_calls_limit,
                'advanced_ai_analysis': plan.advanced_ai_analysis,
                'unlimited_reports': plan.unlimited_reports,
                'white_label': plan.white_label,
                'dedicated_support': plan.dedicated_support,
                'multi_tenancy': plan.multi_tenancy,
                'features': plan.features
            })
        
        return Response(comparison)


class UserSubscriptionViewSet(viewsets.ModelViewSet):
    """ViewSet for user subscriptions"""
    serializer_class = UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter subscriptions to current user only (or all for staff)"""
        if self.request.user.is_staff:
            return UserSubscription.objects.all().select_related('user', 'plan')
        return UserSubscription.objects.filter(user=self.request.user).select_related('plan')
    
    def get_serializer_class(self):
        """Use different serializer for creation"""
        if self.action == 'create':
            return UserSubscriptionCreateSerializer
        return UserSubscriptionSerializer
    
    def perform_create(self, serializer):
        """Set user when creating subscription"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current active subscription for user"""
        try:
            subscription = UserSubscription.objects.get(
                user=request.user, 
                status='active'
            )
            serializer = self.get_serializer(subscription)
            return Response(serializer.data)
        except UserSubscription.DoesNotExist:
            return Response(
                {'detail': 'No active subscription found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel subscription"""
        subscription = self.get_object()
        
        if subscription.user != request.user and not request.user.is_staff:
            return Response(
                {'detail': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        subscription.status = 'cancelled'
        subscription.cancelled_at = timezone.now()
        subscription.auto_renewal = False
        subscription.save()
        
        # Create subscription change record
        SubscriptionChange.objects.create(
            user=subscription.user,
            old_plan=subscription.plan,
            new_plan=subscription.plan,
            change_type='cancellation',
            reason='User requested cancellation'
        )
        
        serializer = self.get_serializer(subscription)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reactivate(self, request, pk=None):
        """Reactivate cancelled subscription"""
        subscription = self.get_object()
        
        if subscription.user != request.user and not request.user.is_staff:
            return Response(
                {'detail': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if subscription.status != 'cancelled':
            return Response(
                {'detail': 'Can only reactivate cancelled subscriptions'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        subscription.status = 'active'
        subscription.cancelled_at = None
        subscription.auto_renewal = True
        subscription.expires_at = timezone.now() + timedelta(days=30)
        subscription.save()
        
        # Create subscription change record
        SubscriptionChange.objects.create(
            user=subscription.user,
            old_plan=subscription.plan,
            new_plan=subscription.plan,
            change_type='reactivation',
            reason='User requested reactivation'
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
        ).values('endpoint').annotate(
            count=models.Count('id')
        ).order_by('-count')[:10]
        
        # Get user's current subscription
        subscription = None
        remaining_calls = 0
        try:
            subscription = UserSubscription.objects.get(user=user)
            remaining_calls = subscription.api_calls_remaining
        except UserSubscription.DoesNotExist:
            pass
        
        return Response({
            'monthly_usage': monthly_usage,
            'remaining_calls': remaining_calls,
            'usage_by_endpoint': list(usage_by_endpoint),
            'subscription': UserSubscriptionSerializer(subscription).data if subscription else None
        })


class SubscriptionChangeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for subscription changes (read-only)"""
    serializer_class = SubscriptionChangeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter subscription changes to current user only"""
        if self.request.user.is_staff:
            return SubscriptionChange.objects.all().select_related('user', 'old_plan', 'new_plan')
        return SubscriptionChange.objects.filter(user=self.request.user).select_related('old_plan', 'new_plan')


class BillingStatsViewSet(viewsets.ViewSet):
    """ViewSet for billing statistics (admin only)"""
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """Get billing overview statistics"""
        # Total revenue
        total_revenue = Invoice.objects.filter(
            status='paid'
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        # Monthly recurring revenue (current month)
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        monthly_revenue = Invoice.objects.filter(
            status='paid',
            paid_at__gte=month_start
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        # Active subscriptions
        active_subscriptions = UserSubscription.objects.filter(status='active').count()
        cancelled_subscriptions = UserSubscription.objects.filter(status='cancelled').count()
        
        # Total customers
        total_customers = UserSubscription.objects.values('user').distinct().count()
        
        # Revenue by plan
        revenue_by_plan = Invoice.objects.filter(
            status='paid'
        ).values(
            'subscription__plan__name'
        ).annotate(
            total_revenue=Sum('total_amount'),
            subscription_count=Count('subscription', distinct=True)
        ).order_by('-total_revenue')
        
        # Revenue trend (last 6 months)
        revenue_trend = []
        for i in range(6):
            month_date = now.replace(day=1) - timedelta(days=i*30)
            month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            next_month = (month_start + timedelta(days=32)).replace(day=1)
            
            month_revenue = Invoice.objects.filter(
                status='paid',
                paid_at__gte=month_start,
                paid_at__lt=next_month
            ).aggregate(
                total=Sum('total_amount')
            )['total'] or 0
            
            month_subscriptions = UserSubscription.objects.filter(
                started_at__gte=month_start,
                started_at__lt=next_month
            ).count()
            
            revenue_trend.append({
                'month': month_start.strftime('%Y-%m'),
                'revenue': float(month_revenue),
                'subscriptions': month_subscriptions
            })
        
        revenue_trend.reverse()
        
        # Calculate churn rate (simplified)
        total_ever_subscribed = UserSubscription.objects.count()
        churn_rate = (cancelled_subscriptions / total_ever_subscribed * 100) if total_ever_subscribed > 0 else 0
        
        # Average revenue per user
        arpu = (float(total_revenue) / total_customers) if total_customers > 0 else 0
        
        return Response({
            'total_revenue': float(total_revenue),
            'monthly_recurring_revenue': float(monthly_revenue),
            'annual_recurring_revenue': float(monthly_revenue * 12),
            'active_subscriptions': active_subscriptions,
            'cancelled_subscriptions': cancelled_subscriptions,
            'total_customers': total_customers,
            'revenue_by_plan': list(revenue_by_plan),
            'revenue_trend': revenue_trend,
            'churn_rate': round(churn_rate, 2),
            'average_revenue_per_user': round(arpu, 2)
        })


# ============================================================================
# PAYMENT PROCESSING VIEWS
# ============================================================================

class PaymentViewSet(viewsets.ViewSet):
    """ViewSet for payment processing"""
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def create_stripe_payment_intent(self, request):
        """Create Stripe payment intent for subscription"""
        from .services.stripe_service import StripeService
        
        try:
            plan_id = request.data.get('plan_id')
            payment_method_id = request.data.get('payment_method_id')
            
            if not plan_id:
                return Response(
                    {'error': 'Plan ID is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            plan = SubscriptionPlan.objects.get(id=plan_id)
            stripe_service = StripeService()
            
            # Create subscription
            result = stripe_service.create_subscription(
                user=request.user,
                plan=plan,
                payment_method_id=payment_method_id
            )
            
            if result['success']:
                # Update or create user subscription in our database
                subscription, created = UserSubscription.objects.get_or_create(
                    user=request.user,
                    defaults={
                        'plan': plan,
                        'status': 'pending',
                        'expires_at': timezone.now() + timedelta(days=30),
                        'api_calls_reset_date': timezone.now() + timedelta(days=30),
                        'stripe_subscription_id': result['subscription_id']
                    }
                )
                
                if not created:
                    subscription.plan = plan
                    subscription.stripe_subscription_id = result['subscription_id']
                    subscription.status = 'pending'
                    subscription.save()
                
                return Response({
                    'client_secret': result['client_secret'],
                    'subscription_id': result['subscription_id'],
                    'subscription': UserSubscriptionSerializer(subscription).data
                })
            else:
                return Response(
                    {'error': result['error']}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except SubscriptionPlan.DoesNotExist:
            return Response(
                {'error': 'Plan not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error creating Stripe payment intent: {e}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def create_pagseguro_payment(self, request):
        """Create PagSeguro payment for subscription"""
        from .services.pagseguro_service import PagSeguroService
        
        try:
            plan_id = request.data.get('plan_id')
            payment_method = request.data.get('payment_method', 'all')  # all, pix, boleto, credit_card
            
            if not plan_id:
                return Response(
                    {'error': 'Plan ID is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            plan = SubscriptionPlan.objects.get(id=plan_id)
            pagseguro_service = PagSeguroService()
            
            # Create payment request
            result = pagseguro_service.create_payment_request(
                user=request.user,
                plan=plan,
                payment_method=payment_method
            )
            
            if result['success']:
                return Response({
                    'payment_url': result['payment_url'],
                    'checkout_code': result['checkout_code']
                })
            else:
                return Response(
                    {'error': result['error']}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except SubscriptionPlan.DoesNotExist:
            return Response(
                {'error': 'Plan not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error creating PagSeguro payment: {e}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def attach_payment_method(self, request):
        """Attach Stripe payment method to user"""
        from .services.stripe_service import StripeService
        
        try:
            payment_method_id = request.data.get('payment_method_id')
            
            if not payment_method_id:
                return Response(
                    {'error': 'Payment method ID is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            stripe_service = StripeService()
            result = stripe_service.create_payment_method(
                user=request.user,
                payment_method_id=payment_method_id
            )
            
            if result['success']:
                return Response({
                    'message': 'Payment method attached successfully',
                    'payment_method': PaymentMethodSerializer(result['payment_method_obj']).data
                })
            else:
                return Response(
                    {'error': result['error']}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Error attaching payment method: {e}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def cancel_subscription(self, request):
        """Cancel user's subscription"""
        from .services.stripe_service import StripeService
        from .services.pagseguro_service import PagSeguroService
        
        try:
            subscription = UserSubscription.objects.get(user=request.user)
            
            # Cancel in payment gateway
            if subscription.stripe_subscription_id:
                stripe_service = StripeService()
                result = stripe_service.cancel_subscription(subscription.stripe_subscription_id)
                
                if not result['success']:
                    return Response(
                        {'error': f"Failed to cancel Stripe subscription: {result['error']}"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            elif subscription.pagseguro_subscription_id:
                pagseguro_service = PagSeguroService()
                result = pagseguro_service.cancel_subscription(subscription.pagseguro_subscription_id)
                
                if not result['success']:
                    return Response(
                        {'error': f"Failed to cancel PagSeguro subscription: {result['error']}"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Update subscription in our database
            subscription.status = 'cancelled'
            subscription.cancelled_at = timezone.now()
            subscription.auto_renewal = False
            subscription.save()
            
            return Response({
                'message': 'Subscription cancelled successfully',
                'subscription': UserSubscriptionSerializer(subscription).data
            })
            
        except UserSubscription.DoesNotExist:
            return Response(
                {'error': 'No active subscription found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error cancelling subscription: {e}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def test_payment_connection(self, request):
        """Test payment gateway connections"""
        from .services.stripe_service import StripeService
        from .services.pagseguro_service import PagSeguroService
        
        try:
            gateway = request.data.get('gateway', 'all') if hasattr(request, 'data') else request.POST.get('gateway', 'all')
            results = {}
            
            if gateway in ['stripe', 'all']:
                try:
                    stripe_service = StripeService()
                    # Simple API call to test connection
                    stripe_service.stripe.Account.retrieve()
                    results['stripe'] = {
                        'connected': True,
                        'message': 'Stripe connection successful'
                    }
                except Exception as e:
                    results['stripe'] = {
                        'connected': False,
                        'error': str(e)
                    }
            
            if gateway in ['pagseguro', 'all']:
                pagseguro_service = PagSeguroService()
                pagseguro_result = pagseguro_service.test_connection()
                results['pagseguro'] = {
                    'connected': pagseguro_result['success'],
                    'message': pagseguro_result.get('message'),
                    'error': pagseguro_result.get('error')
                }
            
            return Response(results)
            
        except Exception as e:
            logger.error(f"Error testing payment connections: {e}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============================================================================
# WEBHOOK HANDLERS
# ============================================================================

class WebhookViewSet(viewsets.ViewSet):
    """ViewSet for handling payment webhooks"""
    permission_classes = []  # Webhooks don't use authentication
    
    @action(detail=False, methods=['post'])
    def stripe(self, request):
        """Handle Stripe webhooks"""
        from .services.stripe_service import StripeService
        
        try:
            payload = request.body
            sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
            
            if not sig_header:
                return Response(
                    {'error': 'Missing signature header'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            stripe_service = StripeService()
            result = stripe_service.handle_webhook(payload.decode('utf-8'), sig_header)
            
            if result['success']:
                return Response({'message': result.get('message', 'Webhook processed')})
            else:
                return Response(
                    {'error': result['error']}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Error handling Stripe webhook: {e}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def pagseguro(self, request):
        """Handle PagSeguro webhooks"""
        from .services.pagseguro_service import PagSeguroService
        
        try:
            notification_code = request.data.get('notificationCode')
            notification_type = request.data.get('notificationType')
            
            if not notification_code or not notification_type:
                return Response(
                    {'error': 'Missing notification parameters'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            pagseguro_service = PagSeguroService()
            result = pagseguro_service.handle_webhook(notification_code, notification_type)
            
            if result['success']:
                return Response({'message': result.get('message', 'Webhook processed')})
            else:
                return Response(
                    {'error': result['error']}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Error handling PagSeguro webhook: {e}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
