from django.contrib import admin
from .models import WhatsAppUser, WhatsAppSession, WhatsAppMessage, WhatsAppPaymentIntent, WhatsAppSubscriptionEvent

@admin.register(WhatsAppUser)
class WhatsAppUserAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'display_name', 'subscription_status', 'current_plan', 
                   'daily_queries_count', 'last_query_date', 'created_at')
    list_filter = ('subscription_status', 'current_plan', 'created_at')
    search_fields = ('phone_number', 'display_name')
    readonly_fields = ('created_at', 'updated_at', 'last_query_date')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('phone_number', 'display_name', 'user')
        }),
        ('Assinatura', {
            'fields': ('subscription_status', 'current_plan', 'is_premium', 'subscription_plan')
        }),
        ('Trial', {
            'fields': ('trial_started_at', 'trial_expires_at')
        }),
        ('Uso', {
            'fields': ('daily_queries_count', 'last_query_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(WhatsAppPaymentIntent)
class WhatsAppPaymentIntentAdmin(admin.ModelAdmin):
    list_display = ('whatsapp_user', 'plan', 'payment_provider', 'amount', 'status', 'created_at')
    list_filter = ('payment_provider', 'status', 'plan', 'created_at')
    search_fields = ('whatsapp_user__phone_number', 'whatsapp_user__display_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informações do Pagamento', {
            'fields': ('whatsapp_user', 'plan', 'payment_provider', 'amount', 'currency')
        }),
        ('Status', {
            'fields': ('status', 'payment_url')
        }),
        ('IDs dos Provedores', {
            'fields': ('stripe_payment_intent_id', 'pagseguro_transaction_id', 'mercadopago_payment_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'expires_at')
        }),
    )

@admin.register(WhatsAppSubscriptionEvent)
class WhatsAppSubscriptionEventAdmin(admin.ModelAdmin):
    list_display = ('whatsapp_user', 'event_type', 'processed', 'created_at')
    list_filter = ('event_type', 'processed', 'created_at')
    search_fields = ('whatsapp_user__phone_number', 'whatsapp_user__display_name')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Evento', {
            'fields': ('whatsapp_user', 'event_type', 'processed')
        }),
        ('Dados', {
            'fields': ('data',)
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )

@admin.register(WhatsAppSession)
class WhatsAppSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'whatsapp_user', 'is_active', 'last_activity')
    list_filter = ('is_active', 'last_activity')
    search_fields = ('session_id', 'whatsapp_user__phone_number')
    readonly_fields = ('last_activity',)

@admin.register(WhatsAppMessage)
class WhatsAppMessageAdmin(admin.ModelAdmin):
    list_display = ('message_id', 'whatsapp_user', 'message_type', 'is_incoming', 
                   'processed', 'timestamp')
    list_filter = ('message_type', 'is_incoming', 'processed', 'timestamp')
    search_fields = ('message_id', 'whatsapp_user__phone_number', 'content')
    readonly_fields = ('timestamp',)
    
    fieldsets = (
        ('Informações da Mensagem', {
            'fields': ('message_id', 'whatsapp_user', 'message_type', 'is_incoming')
        }),
        ('Conteúdo', {
            'fields': ('content',)
        }),
        ('Status', {
            'fields': ('processed', 'error_message')
        }),
        ('Timestamps', {
            'fields': ('timestamp',)
        }),
    )
