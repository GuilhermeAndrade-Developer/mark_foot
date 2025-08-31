"""
Django admin configuration for chat models.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import (
    ChatRoom, ChatMessage, ChatUserSession, ChatModeration,
    ChatReport, ChatBannedUser, ChatEmoji
)


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    """Admin interface for chat rooms."""
    
    list_display = [
        'name', 'room_type', 'status', 'total_messages',
        'get_active_users', 'match_info', 'created_at'
    ]
    list_filter = ['room_type', 'status', 'auto_moderation', 'allow_guests', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'total_messages', 'peak_concurrent_users', 'total_unique_users']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'description', 'room_type', 'status')
        }),
        ('Content Association', {
            'fields': ('match', 'team'),
            'classes': ('collapse',)
        }),
        ('Chat Settings', {
            'fields': (
                'max_users', 'rate_limit_messages', 'auto_moderation', 'allow_guests'
            )
        }),
        ('Moderation Settings', {
            'fields': (
                'profanity_filter', 'spam_detection', 'link_filter', 'emoji_only_mode'
            ),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('total_messages', 'peak_concurrent_users', 'total_unique_users'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_active_users(self, obj):
        count = obj.get_active_users_count()
        return format_html(
            '<span style="color: {};">{}</span>',
            'green' if count > 0 else 'gray',
            count
        )
    get_active_users.short_description = 'Active Users'
    
    def match_info(self, obj):
        if obj.match:
            return f"{obj.match.home_team.name} vs {obj.match.away_team.name}"
        elif obj.team:
            return f"Team: {obj.team.name}"
        return "-"
    match_info.short_description = 'Associated Content'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """Admin interface for chat messages."""
    
    list_display = [
        'get_username', 'room', 'content_preview', 'message_type',
        'status', 'is_flagged', 'likes_count', 'created_at'
    ]
    list_filter = [
        'message_type', 'status', 'is_flagged', 'auto_flagged', 'created_at'
    ]
    search_fields = ['content', 'user__username', 'guest_name']
    readonly_fields = [
        'id', 'likes_count', 'reports_count', 'flag_count',
        'user_ip', 'user_agent', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Message Information', {
            'fields': ('id', 'room', 'user', 'guest_name', 'content', 'message_type')
        }),
        ('Status & Moderation', {
            'fields': (
                'status', 'is_flagged', 'flag_count', 'auto_flagged',
                'moderated_by', 'moderated_at', 'moderation_reason'
            )
        }),
        ('Engagement', {
            'fields': ('likes_count', 'reports_count'),
            'classes': ('collapse',)
        }),
        ('Technical Info', {
            'fields': ('user_ip', 'user_agent', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
    
    def get_username(self, obj):
        return obj.get_username()
    get_username.short_description = 'User'


@admin.register(ChatUserSession)
class ChatUserSessionAdmin(admin.ModelAdmin):
    """Admin interface for user sessions."""
    
    list_display = [
        'get_username', 'room', 'is_active', 'messages_sent',
        'last_activity', 'session_duration'
    ]
    list_filter = ['is_active', 'joined_at', 'last_activity']
    search_fields = ['user__username', 'guest_id', 'room__name']
    readonly_fields = ['id', 'joined_at', 'session_duration']
    
    def get_username(self, obj):
        if obj.user:
            return obj.user.username
        return f"Guest-{obj.guest_id}"
    get_username.short_description = 'User'
    
    def session_duration(self, obj):
        end_time = obj.left_at or timezone.now()
        duration = end_time - obj.joined_at
        minutes = int(duration.total_seconds() / 60)
        return f"{minutes} minutes"
    session_duration.short_description = 'Duration'


@admin.register(ChatModeration)
class ChatModerationAdmin(admin.ModelAdmin):
    """Admin interface for moderation actions."""
    
    list_display = [
        'moderator', 'action_type', 'get_target', 'room',
        'reason', 'is_active', 'created_at'
    ]
    list_filter = ['action_type', 'is_active', 'created_at']
    search_fields = [
        'moderator__username', 'target_user__username', 
        'room__name', 'reason'
    ]
    readonly_fields = ['id', 'created_at']
    
    def get_target(self, obj):
        if obj.target_user:
            return obj.target_user.username
        elif obj.target_message:
            return f"Message by {obj.target_message.get_username()}"
        return "-"
    get_target.short_description = 'Target'


@admin.register(ChatReport)
class ChatReportAdmin(admin.ModelAdmin):
    """Admin interface for chat reports."""
    
    list_display = [
        'reporter', 'get_message_author', 'reason', 'status',
        'reviewed_by', 'created_at'
    ]
    list_filter = ['reason', 'status', 'created_at', 'reviewed_at']
    search_fields = [
        'reporter__username', 'message__user__username',
        'reason', 'description'
    ]
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Report Information', {
            'fields': ('id', 'reporter', 'message', 'reason', 'description')
        }),
        ('Status', {
            'fields': ('status', 'reviewed_by', 'reviewed_at', 'resolution_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def get_message_author(self, obj):
        return obj.message.get_username()
    get_message_author.short_description = 'Message Author'


@admin.register(ChatBannedUser)
class ChatBannedUserAdmin(admin.ModelAdmin):
    """Admin interface for banned users."""
    
    list_display = [
        'user', 'get_room_name', 'ban_type', 'reason',
        'banned_by', 'is_active', 'expires_at'
    ]
    list_filter = ['ban_type', 'is_active', 'created_at']
    search_fields = ['user__username', 'room__name', 'reason']
    readonly_fields = ['id', 'created_at']
    
    def get_room_name(self, obj):
        return obj.room.name if obj.room else "Global"
    get_room_name.short_description = 'Room'


@admin.register(ChatEmoji)
class ChatEmojiAdmin(admin.ModelAdmin):
    """Admin interface for chat emojis."""
    
    list_display = ['name', 'unicode_code', 'is_active', 'usage_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    readonly_fields = ['usage_count', 'created_at']
