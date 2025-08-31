"""
Serializers for chat API endpoints.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    ChatRoom, ChatMessage, ChatUserSession, ChatModeration,
    ChatReport, ChatBannedUser, ChatEmoji
)


class ChatRoomListSerializer(serializers.ModelSerializer):
    """Simplified serializer for chat room lists."""
    
    active_users_count = serializers.SerializerMethodField()
    match_info = serializers.SerializerMethodField()
    team_info = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = [
            'id', 'name', 'room_type', 'status', 'total_messages',
            'peak_concurrent_users', 'active_users_count', 'match_info',
            'team_info', 'created_at'
        ]
    
    def get_active_users_count(self, obj):
        return obj.get_active_users_count()
    
    def get_match_info(self, obj):
        if obj.match:
            return {
                'id': obj.match.id,
                'home_team': obj.match.home_team.name,
                'away_team': obj.match.away_team.name,
                'status': obj.match.status,
                'utc_date': obj.match.utc_date
            }
        return None
    
    def get_team_info(self, obj):
        if obj.team:
            return {
                'id': obj.team.id,
                'name': obj.team.name,
                'short_name': obj.team.short_name
            }
        return None


class ChatRoomDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for chat room details."""
    
    active_users_count = serializers.SerializerMethodField()
    recent_messages_count = serializers.SerializerMethodField()
    match_info = serializers.SerializerMethodField()
    team_info = serializers.SerializerMethodField()
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    moderation_stats = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = [
            'id', 'name', 'description', 'room_type', 'status',
            'max_users', 'rate_limit_messages', 'auto_moderation',
            'allow_guests', 'profanity_filter', 'spam_detection',
            'link_filter', 'emoji_only_mode', 'total_messages',
            'peak_concurrent_users', 'total_unique_users',
            'active_users_count', 'recent_messages_count',
            'match_info', 'team_info', 'created_by_username',
            'moderation_stats', 'created_at', 'updated_at'
        ]
    
    def get_active_users_count(self, obj):
        return obj.get_active_users_count()
    
    def get_recent_messages_count(self, obj):
        from django.utils import timezone
        from datetime import timedelta
        
        one_hour_ago = timezone.now() - timedelta(hours=1)
        return obj.messages.filter(
            created_at__gte=one_hour_ago,
            status='active'
        ).count()
    
    def get_match_info(self, obj):
        if obj.match:
            return {
                'id': obj.match.id,
                'home_team': obj.match.home_team.name,
                'away_team': obj.match.away_team.name,
                'status': obj.match.status,
                'utc_date': obj.match.utc_date,
                'home_score': obj.match.score_home,
                'away_score': obj.match.score_away
            }
        return None
    
    def get_team_info(self, obj):
        if obj.team:
            return {
                'id': obj.team.id,
                'name': obj.team.name,
                'short_name': obj.team.short_name,
                'crest': obj.team.crest
            }
        return None
    
    def get_moderation_stats(self, obj):
        from django.utils import timezone
        from datetime import timedelta
        
        last_24h = timezone.now() - timedelta(hours=24)
        return {
            'flagged_messages': obj.messages.filter(is_flagged=True).count(),
            'banned_users': obj.banned_users.filter(is_active=True).count(),
            'reports_last_24h': ChatReport.objects.filter(
                message__room=obj,
                created_at__gte=last_24h
            ).count(),
            'moderation_actions_last_24h': obj.moderation_actions.filter(
                created_at__gte=last_24h
            ).count()
        }


class ChatRoomCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating chat rooms."""
    
    class Meta:
        model = ChatRoom
        fields = [
            'name', 'description', 'room_type', 'match', 'team',
            'max_users', 'rate_limit_messages', 'auto_moderation',
            'allow_guests', 'profanity_filter', 'spam_detection',
            'link_filter', 'emoji_only_mode'
        ]
    
    def validate(self, data):
        """Custom validation for chat room creation."""
        room_type = data.get('room_type')
        match = data.get('match')
        team = data.get('team')
        
        if room_type == 'match' and not match:
            raise serializers.ValidationError("Match is required for match-type rooms")
        
        if room_type == 'team' and not team:
            raise serializers.ValidationError("Team is required for team-type rooms")
        
        if room_type == 'match' and match:
            # Check if match already has a chat room
            if ChatRoom.objects.filter(match=match).exists():
                raise serializers.ValidationError("This match already has a chat room")
        
        return data


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user info for chat contexts."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages."""
    
    user_info = UserBasicSerializer(source='user', read_only=True)
    username = serializers.SerializerMethodField()
    room_name = serializers.CharField(source='room.name', read_only=True)
    moderated_by_username = serializers.CharField(source='moderated_by.username', read_only=True)
    can_moderate = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'content', 'message_type', 'status', 'is_flagged',
            'flag_count', 'auto_flagged', 'likes_count', 'reports_count',
            'user_info', 'username', 'guest_name', 'room_name',
            'moderated_by_username', 'moderated_at', 'moderation_reason',
            'can_moderate', 'created_at', 'updated_at'
        ]
    
    def get_username(self, obj):
        return obj.get_username()
    
    def get_can_moderate(self, obj):
        """Check if current user can moderate this message."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        user = request.user
        return user.is_staff or user.is_superuser


class ChatUserSessionSerializer(serializers.ModelSerializer):
    """Serializer for chat user sessions."""
    
    username = serializers.SerializerMethodField()
    room_name = serializers.CharField(source='room.name', read_only=True)
    session_duration = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatUserSession
        fields = [
            'id', 'username', 'room_name', 'is_active',
            'messages_sent', 'last_activity', 'session_duration',
            'joined_at', 'left_at'
        ]
    
    def get_username(self, obj):
        if obj.user:
            return obj.user.username
        return f"Guest-{obj.guest_id}"
    
    def get_session_duration(self, obj):
        """Calculate session duration in minutes."""
        from django.utils import timezone
        
        end_time = obj.left_at or timezone.now()
        duration = end_time - obj.joined_at
        return int(duration.total_seconds() / 60)


class ChatModerationSerializer(serializers.ModelSerializer):
    """Serializer for moderation actions."""
    
    moderator_username = serializers.CharField(source='moderator.username', read_only=True)
    target_username = serializers.CharField(source='target_user.username', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatModeration
        fields = [
            'id', 'action_type', 'reason', 'duration_minutes',
            'moderator_username', 'target_username', 'room_name',
            'is_active', 'is_expired', 'created_at', 'expires_at'
        ]
    
    def get_is_expired(self, obj):
        """Check if moderation action has expired."""
        if not obj.expires_at:
            return False
        
        from django.utils import timezone
        return timezone.now() > obj.expires_at


class ChatReportSerializer(serializers.ModelSerializer):
    """Serializer for chat reports."""
    
    reporter_username = serializers.CharField(source='reporter.username', read_only=True)
    message_content = serializers.CharField(source='message.content', read_only=True)
    message_author = serializers.SerializerMethodField()
    room_name = serializers.CharField(source='message.room.name', read_only=True)
    reviewed_by_username = serializers.CharField(source='reviewed_by.username', read_only=True)
    
    class Meta:
        model = ChatReport
        fields = [
            'id', 'reason', 'description', 'status',
            'reporter_username', 'message_content', 'message_author',
            'room_name', 'reviewed_by_username', 'reviewed_at',
            'resolution_notes', 'created_at'
        ]
    
    def get_message_author(self, obj):
        return obj.message.get_username()


class ChatBannedUserSerializer(serializers.ModelSerializer):
    """Serializer for banned users."""
    
    username = serializers.CharField(source='user.username', read_only=True)
    banned_by_username = serializers.CharField(source='banned_by.username', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)
    is_expired = serializers.SerializerMethodField()
    time_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatBannedUser
        fields = [
            'id', 'username', 'room_name', 'ban_type', 'reason',
            'banned_by_username', 'is_active', 'is_expired',
            'time_remaining', 'created_at', 'expires_at'
        ]
    
    def get_is_expired(self, obj):
        return obj.is_expired()
    
    def get_time_remaining(self, obj):
        """Get time remaining for temporary bans."""
        if not obj.expires_at or obj.is_expired():
            return None
        
        from django.utils import timezone
        remaining = obj.expires_at - timezone.now()
        return int(remaining.total_seconds() / 60)  # minutes


class ChatEmojiSerializer(serializers.ModelSerializer):
    """Serializer for chat emojis."""
    
    class Meta:
        model = ChatEmoji
        fields = [
            'id', 'name', 'unicode_code', 'image_url',
            'is_active', 'usage_count', 'created_at'
        ]


class ChatStatsSerializer(serializers.Serializer):
    """Serializer for chat dashboard statistics."""
    
    total_rooms = serializers.IntegerField()
    active_rooms = serializers.IntegerField()
    total_messages_today = serializers.IntegerField()
    total_active_users = serializers.IntegerField()
    pending_reports = serializers.IntegerField()
    flagged_messages = serializers.IntegerField()
    banned_users = serializers.IntegerField()
    top_rooms = serializers.ListField()
    recent_activity = serializers.ListField()
    moderation_stats = serializers.DictField()
    hourly_activity = serializers.ListField()


class ChatRoomQuickStatsSerializer(serializers.Serializer):
    """Quick stats for a specific chat room."""
    
    room_id = serializers.UUIDField()
    room_name = serializers.CharField()
    active_users = serializers.IntegerField()
    messages_last_hour = serializers.IntegerField()
    messages_last_24h = serializers.IntegerField()
    flagged_messages = serializers.IntegerField()
    pending_reports = serializers.IntegerField()
    peak_users_today = serializers.IntegerField()
    avg_messages_per_user = serializers.FloatField()
