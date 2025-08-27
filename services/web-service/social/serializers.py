"""
Serializers for social features API.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    UserFollow, Comment, CommentLike, UserActivity, 
    Notification, CommentReport
)


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user info for social features"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'date_joined']


class UserFollowSerializer(serializers.ModelSerializer):
    """Serializer for user following system"""
    follower = UserBasicSerializer(read_only=True)
    followed = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = UserFollow
        fields = ['id', 'follower', 'followed', 'created_at']
        read_only_fields = ['created_at']


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments"""
    user = UserBasicSerializer(read_only=True)
    content_type_display = serializers.CharField(source='get_content_type_display', read_only=True)
    replies = serializers.SerializerMethodField()
    can_moderate = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'user', 'content', 'comment_type', 'status',
            'match', 'team', 'parent', 'likes_count', 'dislikes_count',
            'replies_count', 'is_flagged', 'flagged_count',
            'content_type_display', 'replies', 'can_moderate',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'likes_count', 'dislikes_count', 'replies_count',
            'is_flagged', 'flagged_count', 'created_at', 'updated_at'
        ]
    
    def get_replies(self, obj):
        """Get comment replies (first level only)"""
        if obj.replies.exists():
            replies = obj.replies.filter(status='active')[:5]  # Limit to 5 recent replies
            return CommentSerializer(replies, many=True, context=self.context).data
        return []
    
    def get_can_moderate(self, obj):
        """Check if current user can moderate this comment"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.is_staff or request.user.is_superuser
        return False


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating comments"""
    class Meta:
        model = Comment
        fields = ['content', 'comment_type', 'match', 'team', 'parent']
    
    def validate_content(self, value):
        """Validate comment content"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Comment must be at least 3 characters long.")
        return value.strip()
    
    def validate(self, data):
        """Validate comment relationships"""
        comment_type = data.get('comment_type')
        match = data.get('match')
        team = data.get('team')
        parent = data.get('parent')
        
        # Validate comment type matches the relationship
        if comment_type == 'match' and not match:
            raise serializers.ValidationError("Match comment must specify a match.")
        if comment_type == 'team' and not team:
            raise serializers.ValidationError("Team comment must specify a team.")
        
        # Validate parent comment exists and is active
        if parent and parent.status != 'active':
            raise serializers.ValidationError("Cannot reply to inactive comment.")
        
        return data


class CommentLikeSerializer(serializers.ModelSerializer):
    """Serializer for comment reactions"""
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = CommentLike
        fields = ['id', 'user', 'comment', 'reaction_type', 'created_at']
        read_only_fields = ['created_at']


class UserActivitySerializer(serializers.ModelSerializer):
    """Serializer for user activities"""
    user = UserBasicSerializer(read_only=True)
    related_user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = UserActivity
        fields = [
            'id', 'user', 'activity_type', 'description',
            'related_comment', 'related_user', 'related_match',
            'metadata', 'created_at'
        ]
        read_only_fields = ['created_at']


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications"""
    sender = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'sender', 'notification_type', 'title', 'message',
            'related_comment', 'related_follow', 'is_read', 'is_sent',
            'created_at', 'read_at'
        ]
        read_only_fields = ['created_at', 'read_at']


class CommentReportSerializer(serializers.ModelSerializer):
    """Serializer for comment reports"""
    reporter = UserBasicSerializer(read_only=True)
    reviewed_by = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = CommentReport
        fields = [
            'id', 'reporter', 'comment', 'reason', 'description',
            'status', 'reviewed_by', 'reviewed_at', 'resolution_notes',
            'created_at'
        ]
        read_only_fields = ['reporter', 'reviewed_by', 'reviewed_at', 'created_at']


class SocialStatsSerializer(serializers.Serializer):
    """Serializer for social statistics"""
    total_comments = serializers.IntegerField()
    total_users = serializers.IntegerField()
    total_follows = serializers.IntegerField()
    active_comments_today = serializers.IntegerField()
    pending_reports = serializers.IntegerField()
    flagged_comments = serializers.IntegerField()
    top_commenters = serializers.ListField()
    recent_activities = serializers.ListField()


class UserSocialProfileSerializer(serializers.ModelSerializer):
    """Extended user profile with social stats"""
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    likes_received = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'date_joined',
            'followers_count', 'following_count', 'comments_count',
            'likes_received', 'is_following'
        ]
    
    def get_followers_count(self, obj):
        """Get count of users following this user"""
        return obj.followers.count()
    
    def get_following_count(self, obj):
        """Get count of users this user follows"""
        return obj.following.count()
    
    def get_comments_count(self, obj):
        """Get count of active comments by this user"""
        return obj.comment_set.filter(status='active').count()
    
    def get_likes_received(self, obj):
        """Get total likes received on user's comments"""
        return CommentLike.objects.filter(
            comment__user=obj,
            reaction_type='like'
        ).count()
    
    def get_is_following(self, obj):
        """Check if current user follows this user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user != obj:
            return UserFollow.objects.filter(
                follower=request.user,
                followed=obj
            ).exists()
        return False
