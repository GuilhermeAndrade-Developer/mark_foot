"""
Serializers for social features API.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    UserFollow, Comment, CommentLike, UserActivity, 
    Notification, CommentReport, SocialPlatform, ShareTemplate,
    SocialShare, PrivateGroup, GroupMembership, GroupPost, GroupInvitation
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


class SocialPlatformSerializer(serializers.ModelSerializer):
    """Serializer for social media platforms"""
    
    class Meta:
        model = SocialPlatform
        fields = [
            'id', 'name', 'display_name', 'is_active', 'character_limit',
            'supports_images', 'supports_videos', 'supports_hashtags',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class SocialPlatformAdminSerializer(serializers.ModelSerializer):
    """Admin serializer for social media platforms with sensitive data"""
    
    class Meta:
        model = SocialPlatform
        fields = [
            'id', 'name', 'display_name', 'is_active', 'api_key', 'api_secret',
            'access_token', 'access_token_secret', 'base_url', 'character_limit',
            'supports_images', 'supports_videos', 'supports_hashtags',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'api_key': {'write_only': True},
            'api_secret': {'write_only': True},
            'access_token': {'write_only': True},
            'access_token_secret': {'write_only': True},
        }


class ShareTemplateSerializer(serializers.ModelSerializer):
    """Serializer for share templates"""
    platform = SocialPlatformSerializer(read_only=True)
    platform_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ShareTemplate
        fields = [
            'id', 'name', 'template_type', 'platform', 'platform_id',
            'title_template', 'content_template', 'hashtags',
            'available_variables', 'is_active', 'auto_share',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class SocialShareSerializer(serializers.ModelSerializer):
    """Serializer for social shares"""
    platform = SocialPlatformSerializer(read_only=True)
    template = ShareTemplateSerializer(read_only=True)
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = SocialShare
        fields = [
            'id', 'platform', 'template', 'title', 'content', 'hashtags',
            'image_url', 'video_url', 'match', 'team', 'comment', 'user',
            'scheduled_at', 'published_at', 'platform_post_id', 'platform_url',
            'likes_count', 'shares_count', 'comments_count', 'views_count',
            'status', 'error_message', 'retry_count', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'platform_post_id', 'platform_url', 'likes_count', 'shares_count',
            'comments_count', 'views_count', 'error_message', 'retry_count',
            'created_at', 'updated_at'
        ]


class SocialShareCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating social shares"""
    
    class Meta:
        model = SocialShare
        fields = [
            'platform', 'template', 'title', 'content', 'hashtags',
            'image_url', 'video_url', 'match', 'team', 'comment', 'scheduled_at'
        ]
    
    def validate(self, data):
        """Validate share data"""
        platform = data.get('platform')
        content = data.get('content', '')
        
        # Check character limit
        if platform and len(content) > platform.character_limit:
            raise serializers.ValidationError(
                f"Content exceeds {platform.character_limit} character limit for {platform.display_name}"
            )
        
        return data


class PrivateGroupSerializer(serializers.ModelSerializer):
    """Serializer for private groups"""
    favorite_team = serializers.StringRelatedField(read_only=True)
    favorite_competition = serializers.StringRelatedField(read_only=True)
    user_membership = serializers.SerializerMethodField()
    can_join = serializers.SerializerMethodField()
    
    class Meta:
        model = PrivateGroup
        fields = [
            'id', 'name', 'description', 'group_type', 'privacy_level',
            'max_members', 'allow_member_invites', 'require_admin_approval',
            'favorite_team', 'favorite_competition', 'cover_image', 'avatar_image',
            'member_count', 'post_count', 'is_active', 'is_featured',
            'user_membership', 'can_join', 'created_at', 'updated_at'
        ]
        read_only_fields = ['member_count', 'post_count', 'created_at', 'updated_at']
    
    def get_user_membership(self, obj):
        """Get current user's membership status"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                membership = obj.memberships.get(user=request.user)
                return {
                    'status': membership.status,
                    'role': membership.role,
                    'joined_at': membership.joined_at
                }
            except GroupMembership.DoesNotExist:
                pass
        return None
    
    def get_can_join(self, obj):
        """Check if current user can join this group"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Check if user is already a member
            if obj.memberships.filter(user=request.user).exists():
                return False
            
            # Check privacy level
            if obj.privacy_level == 'public':
                return True
            elif obj.privacy_level == 'restricted':
                return True  # Can request to join
            else:  # private
                return False  # Invite only
        return False


class GroupMembershipSerializer(serializers.ModelSerializer):
    """Serializer for group memberships"""
    user = UserBasicSerializer(read_only=True)
    group = PrivateGroupSerializer(read_only=True)
    invited_by = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = GroupMembership
        fields = [
            'id', 'group', 'user', 'role', 'status', 'invited_by',
            'invitation_message', 'posts_count', 'last_activity',
            'joined_at', 'left_at'
        ]
        read_only_fields = ['posts_count', 'last_activity', 'joined_at', 'left_at']


class GroupPostSerializer(serializers.ModelSerializer):
    """Serializer for group posts"""
    author = UserBasicSerializer(read_only=True)
    group = PrivateGroupSerializer(read_only=True)
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    
    class Meta:
        model = GroupPost
        fields = [
            'id', 'group', 'author', 'post_type', 'title', 'content',
            'image_url', 'video_url', 'link_url', 'link_title', 'link_description',
            'related_match', 'related_team', 'likes_count', 'comments_count',
            'shares_count', 'is_pinned', 'is_announcement', 'is_approved',
            'can_edit', 'can_delete', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'likes_count', 'comments_count', 'shares_count',
            'created_at', 'updated_at'
        ]
    
    def get_can_edit(self, obj):
        """Check if current user can edit this post"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return (obj.author == request.user or 
                    request.user.is_staff or 
                    obj.group.memberships.filter(
                        user=request.user, 
                        role__in=['owner', 'admin', 'moderator']
                    ).exists())
        return False
    
    def get_can_delete(self, obj):
        """Check if current user can delete this post"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return (obj.author == request.user or 
                    request.user.is_staff or 
                    obj.group.memberships.filter(
                        user=request.user, 
                        role__in=['owner', 'admin']
                    ).exists())
        return False


class GroupInvitationSerializer(serializers.ModelSerializer):
    """Serializer for group invitations"""
    group = PrivateGroupSerializer(read_only=True)
    inviter = UserBasicSerializer(read_only=True)
    invitee = UserBasicSerializer(read_only=True)
    is_expired = serializers.SerializerMethodField()
    can_respond = serializers.SerializerMethodField()
    
    class Meta:
        model = GroupInvitation
        fields = [
            'id', 'group', 'inviter', 'invitee', 'message', 'status',
            'expires_at', 'responded_at', 'response_message',
            'is_expired', 'can_respond', 'created_at'
        ]
        read_only_fields = ['responded_at', 'created_at']
    
    def get_is_expired(self, obj):
        """Check if invitation is expired"""
        return obj.is_expired()
    
    def get_can_respond(self, obj):
        """Check if invitation can still be responded to"""
        return obj.can_respond()


class GroupInvitationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating group invitations"""
    invitee_username = serializers.CharField(write_only=True)
    
    class Meta:
        model = GroupInvitation
        fields = ['group', 'invitee_username', 'message', 'expires_at']
    
    def validate_invitee_username(self, value):
        """Validate invitee username exists"""
        try:
            user = User.objects.get(username=value)
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this username does not exist.")
    
    def validate(self, data):
        """Validate invitation data"""
        group = data.get('group')
        invitee = data.get('invitee_username')
        
        # Check if user is already a member
        if group.memberships.filter(user=invitee).exists():
            raise serializers.ValidationError("User is already a member of this group.")
        
        # Check if invitation already exists
        if group.invitations.filter(
            invitee=invitee, 
            status='pending'
        ).exists():
            raise serializers.ValidationError("Pending invitation already exists for this user.")
        
        return data
    
    def create(self, validated_data):
        """Create group invitation"""
        invitee_user = validated_data.pop('invitee_username')
        validated_data['invitee'] = invitee_user
        validated_data['inviter'] = self.context['request'].user
        return super().create(validated_data)


class SocialSharingStatsSerializer(serializers.Serializer):
    """Serializer for social sharing statistics"""
    total_shares = serializers.IntegerField()
    shares_by_platform = serializers.DictField()
    shares_today = serializers.IntegerField()
    shares_this_week = serializers.IntegerField()
    shares_this_month = serializers.IntegerField()
    top_shared_content = serializers.ListField()
    most_active_users = serializers.ListField()
    engagement_metrics = serializers.DictField()


class GroupStatsSerializer(serializers.Serializer):
    """Serializer for group statistics"""
    total_groups = serializers.IntegerField()
    total_members = serializers.IntegerField()
    total_posts = serializers.IntegerField()
    groups_by_type = serializers.DictField()
    groups_by_privacy = serializers.DictField()
    most_active_groups = serializers.ListField()
    recent_activity = serializers.ListField()
