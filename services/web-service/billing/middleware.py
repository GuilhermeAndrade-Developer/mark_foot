"""
Middleware for API usage tracking and rate limiting.
"""

from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from .models import UserSubscription, ApiUsageLog
import time


class ApiUsageMiddleware(MiddlewareMixin):
    """
    Middleware to track API usage and enforce rate limiting based on subscription plans.
    """
    
    def process_request(self, request):
        """Process request before view execution"""
        # Only track API endpoints
        if not request.path.startswith('/api/'):
            return None
        
        # Skip for non-authenticated users on certain endpoints
        if isinstance(request.user, AnonymousUser):
            # Allow access to public endpoints
            public_endpoints = [
                '/api/billing/api/plans/',
                '/api/schema/',
                '/api/docs/',
                '/api/redoc/',
            ]
            if any(request.path.startswith(endpoint) for endpoint in public_endpoints):
                return None
            return None  # Don't block anonymous users for now
        
        # Get user's subscription
        try:
            subscription = UserSubscription.objects.get(user=request.user)
        except UserSubscription.DoesNotExist:
            # Auto-create free subscription
            from .models import SubscriptionPlan
            try:
                free_plan = SubscriptionPlan.objects.get(plan_type='free')
                subscription = UserSubscription.objects.create(
                    user=request.user,
                    plan=free_plan,
                    expires_at=timezone.now() + timezone.timedelta(days=365 * 10),  # 10 years for free
                    api_calls_reset_date=timezone.now() + timezone.timedelta(days=30)
                )
            except SubscriptionPlan.DoesNotExist:
                # No plans available, allow access
                return None
        
        # Check if subscription is active
        if subscription.status != 'active' or subscription.is_expired:
            return JsonResponse({
                'error': 'Subscription expired or inactive',
                'code': 'SUBSCRIPTION_INACTIVE'
            }, status=402)  # Payment Required
        
        # Check API usage limits (only for non-unlimited plans)
        if subscription.plan.api_calls_limit > 0:
            # Reset usage if needed
            if timezone.now() >= subscription.api_calls_reset_date:
                subscription.reset_api_usage()
            
            # Check if limit is exceeded
            if subscription.api_calls_used >= subscription.plan.api_calls_limit:
                return JsonResponse({
                    'error': 'API rate limit exceeded',
                    'limit': subscription.plan.api_calls_limit,
                    'used': subscription.api_calls_used,
                    'reset_date': subscription.api_calls_reset_date.isoformat(),
                    'code': 'RATE_LIMIT_EXCEEDED'
                }, status=429)  # Too Many Requests
        
        # Store request start time for response time calculation
        request._api_start_time = time.time()
        request._user_subscription = subscription
        
        return None
    
    def process_response(self, request, response):
        """Process response after view execution"""
        # Only track API endpoints
        if not request.path.startswith('/api/'):
            return response
        
        # Skip if user is anonymous or no subscription
        if isinstance(request.user, AnonymousUser) or not hasattr(request, '_user_subscription'):
            return response
        
        subscription = request._user_subscription
        
        # Calculate response time
        response_time_ms = None
        if hasattr(request, '_api_start_time'):
            response_time_ms = int((time.time() - request._api_start_time) * 1000)
        
        # Log API usage (async would be better, but keep it simple for now)
        try:
            # Increment usage counter
            if subscription.plan.api_calls_limit > 0:  # Only count for limited plans
                subscription.api_calls_used += 1
                subscription.save(update_fields=['api_calls_used'])
            
            # Log the request
            ApiUsageLog.objects.create(
                user=request.user,
                subscription=subscription,
                endpoint=request.path,
                method=request.method,
                response_status=response.status_code,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                response_time_ms=response_time_ms
            )
        except Exception as e:
            # Don't break the response if logging fails
            print(f"API usage logging failed: {e}")
        
        # Add usage headers to response
        response['X-RateLimit-Limit'] = str(subscription.plan.api_calls_limit)
        response['X-RateLimit-Remaining'] = str(subscription.api_calls_remaining)
        response['X-RateLimit-Reset'] = subscription.api_calls_reset_date.isoformat()
        
        return response
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or '127.0.0.1'
