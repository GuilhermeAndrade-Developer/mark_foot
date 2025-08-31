"""
Models for social features - comments and user following system.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import Match, Team, Competition


class UserFollow(models.Model):
    """User following system"""
    follower = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='following',
        help_text="User who follows"
    )
    followed = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='followers',
        help_text="User being followed"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_follows'
        unique_together = ['follower', 'followed']
        indexes = [
            models.Index(fields=['follower']),
            models.Index(fields=['followed']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.follower.username} follows {self.followed.username}"


class Comment(models.Model):
    """Comments system for matches and general content"""
    
    COMMENT_TYPES = [
        ('match', 'Match Comment'),
        ('team', 'Team Comment'),
        ('general', 'General Comment'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('pending', 'Pending Moderation'),
        ('hidden', 'Hidden'),
        ('deleted', 'Deleted'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        help_text="User who made the comment"
    )
    content = models.TextField(
        max_length=1000,
        help_text="Comment content"
    )
    comment_type = models.CharField(
        max_length=20, 
        choices=COMMENT_TYPES,
        default='general'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    
    # Optional relationships to specific content
    match = models.ForeignKey(
        Match, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='comments',
        help_text="Related match"
    )
    team = models.ForeignKey(
        Team, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='comments',
        help_text="Related team"
    )
    
    # Comment threading (replies)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='replies',
        help_text="Parent comment for replies"
    )
    
    # Engagement metrics
    likes_count = models.PositiveIntegerField(default=0)
    dislikes_count = models.PositiveIntegerField(default=0)
    replies_count = models.PositiveIntegerField(default=0)
    
    # Moderation fields
    is_flagged = models.BooleanField(default=False)
    flagged_count = models.PositiveIntegerField(default=0)
    moderated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='moderated_comments'
    )
    moderated_at = models.DateTimeField(null=True, blank=True)
    moderation_reason = models.CharField(max_length=200, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'comments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['match']),
            models.Index(fields=['team']),
            models.Index(fields=['status']),
            models.Index(fields=['comment_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['parent']),
            models.Index(fields=['is_flagged']),
        ]
    
    def __str__(self):
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"{self.user.username}: {content_preview}"
    
    def get_content_object(self):
        """Get the main content object this comment is about"""
        if self.match:
            return self.match
        elif self.team:
            return self.team
        return None
    
    def get_content_type_display(self):
        """Get human readable content type"""
        if self.match:
            return f"Match: {self.match.home_team.name} vs {self.match.away_team.name}"
        elif self.team:
            return f"Team: {self.team.name}"
        return "General Comment"


class CommentLike(models.Model):
    """Like/Dislike system for comments"""
    
    REACTION_TYPES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='reactions')
    reaction_type = models.CharField(max_length=10, choices=REACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'comment_likes'
        unique_together = ['user', 'comment']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['comment']),
            models.Index(fields=['reaction_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} {self.reaction_type}s comment by {self.comment.user.username}"


class UserActivity(models.Model):
    """Track user activities for social feed"""
    
    ACTIVITY_TYPES = [
        ('comment', 'Posted a comment'),
        ('like', 'Liked a comment'),
        ('follow', 'Started following user'),
        ('join', 'Joined the platform'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.CharField(max_length=255)
    
    # Optional relationships to track what the activity was about
    related_comment = models.ForeignKey(
        Comment, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    related_user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='activities_about'
    )
    related_match = models.ForeignKey(
        Match, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_activities'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['activity_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}"


class Notification(models.Model):
    """Notification system for social interactions"""
    
    NOTIFICATION_TYPES = [
        ('new_follower', 'New Follower'),
        ('comment_reply', 'Comment Reply'),
        ('comment_like', 'Comment Liked'),
        ('mention', 'User Mention'),
    ]
    
    recipient = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_notifications'
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=100)
    message = models.CharField(max_length=255)
    
    # Optional relationships
    related_comment = models.ForeignKey(
        Comment, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    related_follow = models.ForeignKey(
        UserFollow, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    
    # Status
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['sender']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['is_read']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


class CommentReport(models.Model):
    """Report system for inappropriate comments"""
    
    REPORT_REASONS = [
        ('spam', 'Spam'),
        ('harassment', 'Harassment'),
        ('hate_speech', 'Hate Speech'),
        ('inappropriate', 'Inappropriate Content'),
        ('fake_news', 'Fake News'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    
    reporter = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='submitted_reports'
    )
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='reports')
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    description = models.TextField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Moderation
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reviewed_reports'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'comment_reports'
        unique_together = ['reporter', 'comment']
        indexes = [
            models.Index(fields=['comment']),
            models.Index(fields=['reporter']),
            models.Index(fields=['status']),
            models.Index(fields=['reason']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Report by {self.reporter.username} on comment {self.comment.id}"


class SocialPlatform(models.Model):
    """Configuration for social media platforms"""
    
    PLATFORM_CHOICES = [
        ('twitter', 'Twitter/X'),
        ('instagram', 'Instagram'),
        ('tiktok', 'TikTok'),
        ('facebook', 'Facebook'),
        ('youtube', 'YouTube'),
        ('linkedin', 'LinkedIn'),
    ]
    
    name = models.CharField(max_length=20, choices=PLATFORM_CHOICES, unique=True)
    display_name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    
    # API Configuration
    api_key = models.CharField(max_length=255, blank=True)
    api_secret = models.CharField(max_length=255, blank=True)
    access_token = models.TextField(blank=True)
    access_token_secret = models.CharField(max_length=255, blank=True)
    
    # Platform-specific settings
    base_url = models.URLField(blank=True)
    character_limit = models.PositiveIntegerField(default=280)
    supports_images = models.BooleanField(default=True)
    supports_videos = models.BooleanField(default=True)
    supports_hashtags = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'social_platforms'
        ordering = ['name']
    
    def __str__(self):
        return self.display_name


class ShareTemplate(models.Model):
    """Templates for social media posts"""
    
    TEMPLATE_TYPES = [
        ('match_result', 'Match Result'),
        ('player_stat', 'Player Statistics'),
        ('team_news', 'Team News'),
        ('prediction', 'Prediction'),
        ('achievement', 'User Achievement'),
        ('league_update', 'League Update'),
        ('custom', 'Custom'),
    ]
    
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    platform = models.ForeignKey(SocialPlatform, on_delete=models.CASCADE, related_name='templates')
    
    # Template content
    title_template = models.CharField(max_length=100, help_text="Template for title/headline")
    content_template = models.TextField(help_text="Template for main content with placeholders")
    hashtags = models.CharField(max_length=200, blank=True, help_text="Default hashtags")
    
    # Template variables available
    available_variables = models.JSONField(
        default=list,
        help_text="List of available variables for this template"
    )
    
    # Settings
    is_active = models.BooleanField(default=True)
    auto_share = models.BooleanField(default=False, help_text="Automatically share when conditions are met")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'share_templates'
        ordering = ['name']
        indexes = [
            models.Index(fields=['platform']),
            models.Index(fields=['template_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.platform.display_name}"


class SocialShare(models.Model):
    """Track social media shares"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('published', 'Published'),
        ('failed', 'Failed'),
        ('deleted', 'Deleted'),
    ]
    
    platform = models.ForeignKey(SocialPlatform, on_delete=models.CASCADE, related_name='shares')
    template = models.ForeignKey(ShareTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Content
    title = models.CharField(max_length=200)
    content = models.TextField()
    hashtags = models.CharField(max_length=200, blank=True)
    image_url = models.URLField(blank=True)
    video_url = models.URLField(blank=True)
    
    # Related content
    match = models.ForeignKey(Match, on_delete=models.CASCADE, null=True, blank=True, related_name='shares')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True, related_name='shares')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True, related_name='shares')
    
    # User who initiated the share
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_shares')
    
    # Scheduling
    scheduled_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Platform response
    platform_post_id = models.CharField(max_length=100, blank=True)
    platform_url = models.URLField(blank=True)
    platform_response = models.JSONField(default=dict, blank=True)
    
    # Metrics
    likes_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    views_count = models.PositiveIntegerField(default=0)
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'social_shares'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['platform']),
            models.Index(fields=['user']),
            models.Index(fields=['status']),
            models.Index(fields=['scheduled_at']),
            models.Index(fields=['published_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.platform.display_name} share: {self.title[:50]}..."


class PrivateGroup(models.Model):
    """Private groups for friends and families"""
    
    GROUP_TYPES = [
        ('family', 'Family'),
        ('friends', 'Friends'),
        ('team_fans', 'Team Fans'),
        ('competition', 'Competition Group'),
        ('custom', 'Custom'),
    ]
    
    PRIVACY_LEVELS = [
        ('private', 'Private - Invite Only'),
        ('restricted', 'Restricted - Request to Join'),
        ('public', 'Public - Anyone can Join'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True)
    group_type = models.CharField(max_length=20, choices=GROUP_TYPES, default='custom')
    privacy_level = models.CharField(max_length=20, choices=PRIVACY_LEVELS, default='private')
    
    # Group settings
    max_members = models.PositiveIntegerField(default=50)
    allow_member_invites = models.BooleanField(default=True)
    require_admin_approval = models.BooleanField(default=True)
    
    # Related content
    favorite_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    favorite_competition = models.ForeignKey(Competition, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Media
    cover_image = models.URLField(blank=True)
    avatar_image = models.URLField(blank=True)
    
    # Metadata
    member_count = models.PositiveIntegerField(default=0)
    post_count = models.PositiveIntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'private_groups'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['group_type']),
            models.Index(fields=['privacy_level']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.name


class GroupMembership(models.Model):
    """Group membership and roles"""
    
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Administrator'),
        ('moderator', 'Moderator'),
        ('member', 'Member'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('pending', 'Pending Approval'),
        ('banned', 'Banned'),
        ('left', 'Left Group'),
    ]
    
    group = models.ForeignKey(PrivateGroup, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Membership info
    invited_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='group_invitations_sent'
    )
    invitation_message = models.TextField(max_length=200, blank=True)
    
    # Activity tracking
    posts_count = models.PositiveIntegerField(default=0)
    last_activity = models.DateTimeField(null=True, blank=True)
    
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'group_memberships'
        unique_together = ['group', 'user']
        ordering = ['-joined_at']
        indexes = [
            models.Index(fields=['group']),
            models.Index(fields=['user']),
            models.Index(fields=['role']),
            models.Index(fields=['status']),
            models.Index(fields=['joined_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.group.name} ({self.role})"


class GroupPost(models.Model):
    """Posts within private groups"""
    
    POST_TYPES = [
        ('text', 'Text Post'),
        ('image', 'Image Post'),
        ('video', 'Video Post'),
        ('link', 'Link Share'),
        ('poll', 'Poll'),
        ('event', 'Event'),
    ]
    
    group = models.ForeignKey(PrivateGroup, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_posts')
    post_type = models.CharField(max_length=20, choices=POST_TYPES, default='text')
    
    # Content
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField(max_length=2000)
    
    # Media
    image_url = models.URLField(blank=True)
    video_url = models.URLField(blank=True)
    link_url = models.URLField(blank=True)
    link_title = models.CharField(max_length=200, blank=True)
    link_description = models.TextField(max_length=500, blank=True)
    
    # Related content
    related_match = models.ForeignKey(Match, on_delete=models.SET_NULL, null=True, blank=True)
    related_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Engagement
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)
    
    # Status
    is_pinned = models.BooleanField(default=False)
    is_announcement = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'group_posts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['group', '-created_at']),
            models.Index(fields=['author']),
            models.Index(fields=['post_type']),
            models.Index(fields=['is_pinned']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.group.name}: {self.title or self.content[:50]}..."


class GroupInvitation(models.Model):
    """Group invitations system"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    group = models.ForeignKey(PrivateGroup, on_delete=models.CASCADE, related_name='invitations')
    inviter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_group_invitations')
    invitee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_group_invitations')
    
    message = models.TextField(max_length=300, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Expiration
    expires_at = models.DateTimeField()
    
    # Response tracking
    responded_at = models.DateTimeField(null=True, blank=True)
    response_message = models.TextField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'group_invitations'
        unique_together = ['group', 'invitee']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['group']),
            models.Index(fields=['inviter']),
            models.Index(fields=['invitee']),
            models.Index(fields=['status']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.inviter.username} invited {self.invitee.username} to {self.group.name}"
    
    def is_expired(self):
        """Check if invitation is expired"""
        return timezone.now() > self.expires_at
    
    def can_respond(self):
        """Check if invitation can still be responded to"""
        return self.status == 'pending' and not self.is_expired()
