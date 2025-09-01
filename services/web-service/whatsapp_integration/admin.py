from django.contrib import admin
from .models import WhatsAppUser, WhatsAppSession, WhatsAppMessage

@admin.register(WhatsAppUser)
class WhatsAppUserAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'display_name', 'is_premium', 'subscription_plan', 
                   'daily_queries_count', 'last_query_date', 'created_at')
    list_filter = ('is_premium', 'subscription_plan', 'created_at')
    search_fields = ('phone_number', 'display_name')
    readonly_fields = ('created_at', 'last_query_date')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('phone_number', 'display_name', 'user')
        }),
        ('Assinatura', {
            'fields': ('is_premium', 'subscription_plan')
        }),
        ('Uso', {
            'fields': ('daily_queries_count', 'last_query_date')
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
