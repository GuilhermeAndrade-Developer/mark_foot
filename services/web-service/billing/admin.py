"""
Django admin configuration for billing models.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    SubscriptionPlan, UserSubscription, PaymentMethod, 
    Invoice, ApiUsageLog, SubscriptionChange
)


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    """Admin for subscription plans"""
    list_display = ['name', 'plan_type', 'price_monthly', 'price_yearly', 'api_calls_limit', 'is_active']
    list_filter = ['plan_type', 'is_active', 'advanced_ai_analysis', 'unlimited_reports']
    search_fields = ['name', 'description']
    ordering = ['sort_order', 'price_monthly']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'plan_type', 'description', 'sort_order', 'is_active')
        }),
        ('Pricing', {
            'fields': ('price_monthly', 'price_yearly')
        }),
        ('Limits & Features', {
            'fields': (
                'api_calls_limit', 'advanced_ai_analysis', 'unlimited_reports',
                'white_label', 'dedicated_support', 'multi_tenancy'
            )
        }),
        ('Additional Features', {
            'fields': ('features',),
            'classes': ('collapse',)
        })
    )


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    """Admin for user subscriptions"""
    list_display = ['user', 'plan', 'status', 'billing_cycle', 'started_at', 'expires_at', 'api_usage_display']
    list_filter = ['status', 'billing_cycle', 'plan', 'auto_renewal']
    search_fields = ['user__username', 'user__email']
    date_hierarchy = 'started_at'
    ordering = ['-started_at']
    
    fieldsets = (
        ('Subscription Details', {
            'fields': ('user', 'plan', 'status', 'billing_cycle', 'auto_renewal')
        }),
        ('Dates', {
            'fields': ('started_at', 'expires_at', 'cancelled_at')
        }),
        ('API Usage', {
            'fields': ('api_calls_used', 'api_calls_reset_date')
        }),
        ('Payment Gateway IDs', {
            'fields': ('stripe_subscription_id', 'pagseguro_subscription_id'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def api_usage_display(self, obj):
        """Display API usage with progress bar"""
        percentage = obj.api_usage_percentage
        remaining = obj.api_calls_remaining
        
        if percentage < 50:
            color = 'green'
        elif percentage < 80:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<div style="width: 100px; background-color: #f0f0f0; border-radius: 3px;">'
            '<div style="width: {}%; background-color: {}; height: 20px; border-radius: 3px; text-align: center; color: white; font-size: 12px; line-height: 20px;">'
            '{:.1f}%'
            '</div></div>'
            '<small>{} remaining</small>',
            percentage, color, percentage, remaining
        )
    api_usage_display.short_description = 'API Usage'


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """Admin for payment methods"""
    list_display = ['user', 'payment_type', 'card_display', 'is_default', 'is_active', 'created_at']
    list_filter = ['payment_type', 'is_default', 'is_active', 'card_brand']
    search_fields = ['user__username', 'user__email', 'card_last_four']
    ordering = ['-created_at']
    
    def card_display(self, obj):
        """Display card info safely"""
        if obj.payment_type == 'credit_card':
            return f"{obj.card_brand} **** {obj.card_last_four}"
        return obj.get_payment_type_display()
    card_display.short_description = 'Card Info'


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Admin for invoices"""
    list_display = ['invoice_number', 'user', 'total_amount', 'currency', 'status', 'issue_date', 'due_date']
    list_filter = ['status', 'currency', 'issue_date']
    search_fields = ['invoice_number', 'user__username', 'user__email']
    date_hierarchy = 'issue_date'
    ordering = ['-issue_date']
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('invoice_number', 'user', 'subscription', 'status')
        }),
        ('Financial Details', {
            'fields': ('subtotal', 'tax_amount', 'discount_amount', 'total_amount', 'currency')
        }),
        ('Dates', {
            'fields': ('issue_date', 'due_date', 'paid_at')
        }),
        ('Billing Period', {
            'fields': ('billing_period_start', 'billing_period_end')
        }),
        ('Payment Gateway IDs', {
            'fields': ('stripe_invoice_id', 'pagseguro_invoice_id'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['invoice_number', 'created_at', 'updated_at']


@admin.register(ApiUsageLog)
class ApiUsageLogAdmin(admin.ModelAdmin):
    """Admin for API usage logs"""
    list_display = ['user', 'endpoint', 'method', 'response_status', 'response_time_ms', 'timestamp']
    list_filter = ['method', 'response_status', 'timestamp']
    search_fields = ['user__username', 'endpoint', 'ip_address']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    
    # Read-only since these are logs
    readonly_fields = ['user', 'subscription', 'endpoint', 'method', 'response_status', 
                      'ip_address', 'user_agent', 'response_time_ms', 'timestamp']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(SubscriptionChange)
class SubscriptionChangeAdmin(admin.ModelAdmin):
    """Admin for subscription changes"""
    list_display = ['user', 'change_type', 'old_plan', 'new_plan', 'prorated_amount', 'effective_date']
    list_filter = ['change_type', 'old_plan', 'new_plan', 'effective_date']
    search_fields = ['user__username', 'user__email', 'reason']
    date_hierarchy = 'effective_date'
    ordering = ['-effective_date']
    
    fieldsets = (
        ('Change Details', {
            'fields': ('user', 'change_type', 'old_plan', 'new_plan')
        }),
        ('Financial Impact', {
            'fields': ('prorated_amount', 'effective_date')
        }),
        ('Notes', {
            'fields': ('reason',)
        })
    )
    
    readonly_fields = ['created_at']
