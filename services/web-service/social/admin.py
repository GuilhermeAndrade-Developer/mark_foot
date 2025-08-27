"""
Django Admin configuration for social features.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import (
    UserFollow, Comment, CommentLike, UserActivity, 
    Notification, CommentReport
)


@admin.register(UserFollow)
class UserFollowAdmin(admin.ModelAdmin):
    """Admin interface for user following system"""
    list_display = ['follower_username', 'followed_username', 'created_at']
    list_filter = ['created_at']
    search_fields = ['follower__username', 'followed__username', 'follower__email', 'followed__email']
    readonly_fields = ['created_at']
    raw_id_fields = ['follower', 'followed']
    
    def follower_username(self, obj):
        return obj.follower.username
    follower_username.short_description = 'Follower'
    follower_username.admin_order_field = 'follower__username'
    
    def followed_username(self, obj):
        return obj.followed.username
    followed_username.short_description = 'Followed'
    followed_username.admin_order_field = 'followed__username'
    
    def has_add_permission(self, request):
        return True
    
    def has_change_permission(self, request, obj=None):
        return True
    
    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin interface for comments"""
    list_display = [
        'id', 'user_link', 'content_preview', 'comment_type', 
        'status', 'engagement_stats', 'content_link', 'created_at'
    ]
    list_filter = [
        'status', 'comment_type', 'is_flagged', 'created_at', 
        'moderated_at'
    ]
    search_fields = [
        'user__username', 'content', 'user__email',
        'match__home_team__name', 'match__away_team__name',
        'team__name'
    ]
    readonly_fields = [
        'likes_count', 'dislikes_count', 'replies_count', 
        'created_at', 'updated_at', 'flagged_count'
    ]
    raw_id_fields = ['user', 'match', 'team', 'parent', 'moderated_by']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Comment Info', {
            'fields': ('user', 'content', 'comment_type', 'status')
        }),
        ('Content Relationship', {
            'fields': ('match', 'team', 'parent'),
            'classes': ('collapse',)
        }),
        ('Engagement', {
            'fields': ('likes_count', 'dislikes_count', 'replies_count'),
            'classes': ('collapse',)
        }),
        ('Moderation', {
            'fields': (
                'is_flagged', 'flagged_count', 'moderated_by', 
                'moderated_at', 'moderation_reason'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_comments', 'hide_comments', 'flag_comments', 'delete_selected']
    
    def content_preview(self, obj):
        preview = obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
        return preview
    content_preview.short_description = 'Content Preview'
    
    def user_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__username'
    
    def engagement_stats(self, obj):
        return format_html(
            '👍 {} | 👎 {} | 💬 {}',
            obj.likes_count,
            obj.dislikes_count,
            obj.replies_count
        )
    engagement_stats.short_description = 'Engagement'
    
    def content_link(self, obj):
        content_obj = obj.get_content_object()
        if content_obj:
            if obj.match:
                url = reverse('admin:core_match_change', args=[obj.match.id])
                return format_html('<a href="{}">Match #{}</a>', url, obj.match.id)
            elif obj.team:
                url = reverse('admin:core_team_change', args=[obj.team.id])
                return format_html('<a href="{}">{}</a>', url, obj.team.name)
        return "General"
    content_link.short_description = 'Related Content'
    
    def approve_comments(self, request, queryset):
        updated = queryset.update(
            status='active',
            moderated_by=request.user,
            moderated_at=timezone.now(),
            moderation_reason='Approved by admin'
        )
        self.message_user(request, f'{updated} comments approved.')
    approve_comments.short_description = "Approve selected comments"
    
    def hide_comments(self, request, queryset):
        updated = queryset.update(
            status='hidden',
            moderated_by=request.user,
            moderated_at=timezone.now(),
            moderation_reason='Hidden by admin'
        )
        self.message_user(request, f'{updated} comments hidden.')
    hide_comments.short_description = "Hide selected comments"
    
    def flag_comments(self, request, queryset):
        updated = queryset.update(
            is_flagged=True,
            moderated_by=request.user,
            moderated_at=timezone.now()
        )
        self.message_user(request, f'{updated} comments flagged for review.')
    flag_comments.short_description = "Flag selected comments"


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    """Admin interface for comment reactions"""
    list_display = ['user_link', 'comment_preview', 'reaction_type', 'created_at']
    list_filter = ['reaction_type', 'created_at']
    search_fields = ['user__username', 'comment__content', 'user__email']
    readonly_fields = ['created_at']
    raw_id_fields = ['user', 'comment']
    
    def user_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__username'
    
    def comment_preview(self, obj):
        preview = obj.comment.content[:50] + "..." if len(obj.comment.content) > 50 else obj.comment.content
        url = reverse('admin:social_comment_change', args=[obj.comment.id])
        return format_html('<a href="{}">{}</a>', url, preview)
    comment_preview.short_description = 'Comment'


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    """Admin interface for user activities"""
    list_display = ['user_link', 'activity_type', 'description', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['user__username', 'description', 'user__email']
    readonly_fields = ['created_at', 'metadata']
    raw_id_fields = ['user', 'related_comment', 'related_user', 'related_match']
    date_hierarchy = 'created_at'
    
    def user_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__username'
    
    def has_add_permission(self, request):
        return False  # Activities are created automatically
    
    def has_change_permission(self, request, obj=None):
        return False  # Activities shouldn't be edited


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for notifications"""
    list_display = [
        'recipient_link', 'sender_link', 'notification_type', 
        'title', 'is_read', 'is_sent', 'created_at'
    ]
    list_filter = ['notification_type', 'is_read', 'is_sent', 'created_at']
    search_fields = [
        'recipient__username', 'sender__username', 'title', 'message',
        'recipient__email', 'sender__email'
    ]
    readonly_fields = ['created_at', 'read_at']
    raw_id_fields = ['recipient', 'sender', 'related_comment', 'related_follow']
    date_hierarchy = 'created_at'
    
    actions = ['mark_as_read', 'mark_as_sent', 'mark_as_unread']
    
    def recipient_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.recipient.id])
        return format_html('<a href="{}">{}</a>', url, obj.recipient.username)
    recipient_link.short_description = 'Recipient'
    recipient_link.admin_order_field = 'recipient__username'
    
    def sender_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.sender.id])
        return format_html('<a href="{}">{}</a>', url, obj.sender.username)
    sender_link.short_description = 'Sender'
    sender_link.admin_order_field = 'sender__username'
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True, read_at=timezone.now())
        self.message_user(request, f'{updated} notifications marked as read.')
    mark_as_read.short_description = "Mark selected as read"
    
    def mark_as_sent(self, request, queryset):
        updated = queryset.update(is_sent=True)
        self.message_user(request, f'{updated} notifications marked as sent.')
    mark_as_sent.short_description = "Mark selected as sent"
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False, read_at=None)
        self.message_user(request, f'{updated} notifications marked as unread.')
    mark_as_unread.short_description = "Mark selected as unread"


@admin.register(CommentReport)
class CommentReportAdmin(admin.ModelAdmin):
    """Admin interface for comment reports"""
    list_display = [
        'id', 'reporter_link', 'comment_preview', 'reason', 
        'status', 'reviewed_by_link', 'created_at'
    ]
    list_filter = ['reason', 'status', 'created_at', 'reviewed_at']
    search_fields = [
        'reporter__username', 'comment__content', 'description',
        'reporter__email', 'reviewed_by__username'
    ]
    readonly_fields = ['created_at']
    raw_id_fields = ['reporter', 'comment', 'reviewed_by']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Report Info', {
            'fields': ('reporter', 'comment', 'reason', 'description', 'status')
        }),
        ('Review', {
            'fields': ('reviewed_by', 'reviewed_at', 'resolution_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_reviewed', 'mark_as_resolved', 'dismiss_reports']
    
    def reporter_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.reporter.id])
        return format_html('<a href="{}">{}</a>', url, obj.reporter.username)
    reporter_link.short_description = 'Reporter'
    reporter_link.admin_order_field = 'reporter__username'
    
    def comment_preview(self, obj):
        preview = obj.comment.content[:50] + "..." if len(obj.comment.content) > 50 else obj.comment.content
        url = reverse('admin:social_comment_change', args=[obj.comment.id])
        return format_html('<a href="{}">{}</a>', url, preview)
    comment_preview.short_description = 'Comment'
    
    def reviewed_by_link(self, obj):
        if obj.reviewed_by:
            url = reverse('admin:auth_user_change', args=[obj.reviewed_by.id])
            return format_html('<a href="{}">{}</a>', url, obj.reviewed_by.username)
        return "-"
    reviewed_by_link.short_description = 'Reviewed By'
    
    def mark_as_reviewed(self, request, queryset):
        updated = queryset.update(
            status='reviewed',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'{updated} reports marked as reviewed.')
    mark_as_reviewed.short_description = "Mark selected as reviewed"
    
    def mark_as_resolved(self, request, queryset):
        updated = queryset.update(
            status='resolved',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'{updated} reports marked as resolved.')
    mark_as_resolved.short_description = "Mark selected as resolved"
    
    def dismiss_reports(self, request, queryset):
        updated = queryset.update(
            status='dismissed',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'{updated} reports dismissed.')
    dismiss_reports.short_description = "Dismiss selected reports"
