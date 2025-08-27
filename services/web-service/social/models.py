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
