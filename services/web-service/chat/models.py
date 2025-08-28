"""
Models for live chat system.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinLengthValidator, MaxLengthValidator
from core.models import Match, Team
import uuid


class ChatRoom(models.Model):
    """Chat room model - typically associated with a match or team."""
    
    ROOM_TYPES = [
        ('match', 'Match Chat'),
        ('team', 'Team Chat'),
        ('general', 'General Chat'),
        ('admin', 'Admin Chat'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('archived', 'Archived'),
        ('maintenance', 'Maintenance'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='general')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Optional relationships
    match = models.OneToOneField(
        Match, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='chat_room',
        help_text="Related match for match-specific chats"
    )
    team = models.ForeignKey(
        Team, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='chat_rooms',
        help_text="Related team for team-specific chats"
    )
    
    # Chat settings
    max_users = models.PositiveIntegerField(default=1000, help_text="Maximum concurrent users")
    rate_limit_messages = models.PositiveIntegerField(default=5, help_text="Messages per minute per user")
    auto_moderation = models.BooleanField(default=True, help_text="Enable automatic moderation")
    allow_guests = models.BooleanField(default=False, help_text="Allow non-authenticated users")
    
    # Moderation settings
    profanity_filter = models.BooleanField(default=True)
    spam_detection = models.BooleanField(default=True)
    link_filter = models.BooleanField(default=True)
    emoji_only_mode = models.BooleanField(default=False)
    
    # Statistics
    total_messages = models.PositiveIntegerField(default=0)
    peak_concurrent_users = models.PositiveIntegerField(default=0)
    total_unique_users = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_chat_rooms'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_rooms'
        indexes = [
            models.Index(fields=['room_type', 'status']),
            models.Index(fields=['match']),
            models.Index(fields=['team']),
            models.Index(fields=['created_at']),
            models.Index(fields=['status']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_room_type_display()})"
    
    def get_active_users_count(self):
        """Get current active users count."""
        return self.user_sessions.filter(is_active=True).count()
    
    def can_user_join(self, user=None):
        """Check if user can join the room."""
        if self.status != 'active':
            return False
        
        if not self.allow_guests and not user:
            return False
            
        if self.get_active_users_count() >= self.max_users:
            return False
            
        return True


class ChatMessage(models.Model):
    """Individual chat message."""
    
    MESSAGE_TYPES = [
        ('text', 'Text Message'),
        ('emoji', 'Emoji Only'),
        ('system', 'System Message'),
        ('admin', 'Admin Message'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('hidden', 'Hidden'),
        ('deleted', 'Deleted'),
        ('flagged', 'Flagged'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='chat_messages'
    )
    guest_name = models.CharField(max_length=50, blank=True, help_text="Name for guest users")
    
    # Message content
    content = models.TextField(
        max_length=500,
        validators=[MinLengthValidator(1), MaxLengthValidator(500)]
    )
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Moderation
    is_flagged = models.BooleanField(default=False)
    flag_count = models.PositiveIntegerField(default=0)
    auto_flagged = models.BooleanField(default=False, help_text="Flagged by automatic moderation")
    moderated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='moderated_messages'
    )
    moderated_at = models.DateTimeField(null=True, blank=True)
    moderation_reason = models.CharField(max_length=200, blank=True)
    
    # Metadata
    user_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Engagement
    likes_count = models.PositiveIntegerField(default=0)
    reports_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'chat_messages'
        indexes = [
            models.Index(fields=['room', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['is_flagged']),
            models.Index(fields=['created_at']),
            models.Index(fields=['message_type']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        username = self.user.username if self.user else self.guest_name or 'Anonymous'
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"{username}: {content_preview}"
    
    def get_username(self):
        """Get the display name for the message author."""
        if self.user:
            return self.user.username
        return self.guest_name or 'Anonymous'


class ChatUserSession(models.Model):
    """Track user sessions in chat rooms."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='user_sessions')
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='chat_sessions'
    )
    guest_id = models.CharField(max_length=100, blank=True, help_text="Session ID for guest users")
    
    # Session info
    is_active = models.BooleanField(default=True)
    user_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    
    # Activity tracking
    messages_sent = models.PositiveIntegerField(default=0)
    last_activity = models.DateTimeField(auto_now=True)
    
    # Timestamps
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'chat_user_sessions'
        indexes = [
            models.Index(fields=['room', 'is_active']),
            models.Index(fields=['user', '-joined_at']),
            models.Index(fields=['last_activity']),
            models.Index(fields=['is_active']),
        ]
        unique_together = [['room', 'user'], ['room', 'guest_id']]
    
    def __str__(self):
        username = self.user.username if self.user else f"Guest-{self.guest_id}"
        return f"{username} in {self.room.name}"


class ChatModeration(models.Model):
    """Moderation actions and logs."""
    
    ACTION_TYPES = [
        ('warn', 'Warning'),
        ('timeout', 'Timeout'),
        ('kick', 'Kick'),
        ('ban', 'Ban'),
        ('message_delete', 'Delete Message'),
        ('message_edit', 'Edit Message'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='moderation_actions')
    moderator = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='moderation_actions'
    )
    target_user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='received_moderation_actions'
    )
    target_message = models.ForeignKey(
        ChatMessage, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='moderation_actions'
    )
    
    # Action details
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    reason = models.CharField(max_length=200)
    duration_minutes = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        help_text="Duration for timeouts/bans in minutes"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'chat_moderation'
        indexes = [
            models.Index(fields=['room', '-created_at']),
            models.Index(fields=['moderator', '-created_at']),
            models.Index(fields=['target_user', '-created_at']),
            models.Index(fields=['action_type']),
            models.Index(fields=['is_active', 'expires_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        target = self.target_user.username if self.target_user else "Message"
        return f"{self.moderator.username} {self.action_type} {target} in {self.room.name}"


class ChatReport(models.Model):
    """User reports for chat messages."""
    
    REPORT_REASONS = [
        ('spam', 'Spam'),
        ('harassment', 'Harassment'),
        ('hate_speech', 'Hate Speech'),
        ('inappropriate', 'Inappropriate Content'),
        ('off_topic', 'Off Topic'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_reports')
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='reports')
    
    # Report details
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    description = models.TextField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Resolution
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reviewed_chat_reports'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_reports'
        indexes = [
            models.Index(fields=['message', '-created_at']),
            models.Index(fields=['reporter', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['reason']),
        ]
        unique_together = [['reporter', 'message']]
    
    def __str__(self):
        return f"Report by {self.reporter.username} on message {self.message.id}"


class ChatBannedUser(models.Model):
    """Banned users from chat rooms."""
    
    BAN_TYPES = [
        ('room', 'Room Ban'),
        ('global', 'Global Ban'),
        ('temporary', 'Temporary Ban'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_bans')
    room = models.ForeignKey(
        ChatRoom, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='banned_users'
    )
    banned_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='issued_chat_bans'
    )
    
    # Ban details
    ban_type = models.CharField(max_length=20, choices=BAN_TYPES, default='room')
    reason = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    
    # Duration
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Leave blank for permanent ban")
    
    class Meta:
        db_table = 'chat_banned_users'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['room', 'is_active']),
            models.Index(fields=['ban_type']),
            models.Index(fields=['expires_at']),
        ]
        unique_together = [['user', 'room']]
    
    def __str__(self):
        room_name = self.room.name if self.room else "Global"
        return f"{self.user.username} banned from {room_name}"
    
    def is_expired(self):
        """Check if ban has expired."""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at


class ChatEmoji(models.Model):
    """Custom emojis for chat."""
    
    name = models.CharField(max_length=50, unique=True)
    unicode_code = models.CharField(max_length=20, blank=True)
    image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    usage_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_emojis'
        ordering = ['name']
    
    def __str__(self):
        return f":{self.name}:"
