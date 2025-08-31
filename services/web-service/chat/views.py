"""
API Views for chat management.
"""

from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Count, Q, F, Avg
from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from .models import (
    ChatRoom, ChatMessage, ChatUserSession, ChatModeration,
    ChatReport, ChatBannedUser, ChatEmoji
)
from .serializers import (
    ChatRoomListSerializer, ChatRoomDetailSerializer, ChatRoomCreateSerializer,
    ChatMessageSerializer, ChatUserSessionSerializer, ChatModerationSerializer,
    ChatReportSerializer, ChatBannedUserSerializer, ChatEmojiSerializer,
    ChatStatsSerializer, ChatRoomQuickStatsSerializer
)


class ChatRoomViewSet(viewsets.ModelViewSet):
    """ViewSet for chat room management."""
    
    queryset = ChatRoom.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Return different serializers for different actions."""
        if self.action == 'list':
            return ChatRoomListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ChatRoomCreateSerializer
        return ChatRoomDetailSerializer
    
    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = super().get_queryset().select_related(
            'match__home_team', 'match__away_team', 'team', 'created_by'
        ).prefetch_related('user_sessions', 'messages')
        
        # Filters
        room_type = self.request.query_params.get('room_type', None)
        status_filter = self.request.query_params.get('status', None)
        match_id = self.request.query_params.get('match', None)
        team_id = self.request.query_params.get('team', None)
        
        if room_type:
            queryset = queryset.filter(room_type=room_type)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if match_id:
            queryset = queryset.filter(match_id=match_id)
        if team_id:
            queryset = queryset.filter(team_id=team_id)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set created_by to current user."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a chat room."""
        room = self.get_object()
        room.status = 'active'
        room.save(update_fields=['status'])
        return Response({'message': 'Chat room activated'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a chat room."""
        room = self.get_object()
        room.status = 'inactive'
        room.save(update_fields=['status'])
        return Response({'message': 'Chat room deactivated'})
    
    @action(detail=True, methods=['get'])
    def quick_stats(self, request, pk=None):
        """Get quick statistics for a chat room."""
        room = self.get_object()
        now = timezone.now()
        one_hour_ago = now - timedelta(hours=1)
        one_day_ago = now - timedelta(hours=24)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate stats
        active_users = room.user_sessions.filter(is_active=True).count()
        messages_last_hour = room.messages.filter(
            created_at__gte=one_hour_ago,
            status='active'
        ).count()
        messages_last_24h = room.messages.filter(
            created_at__gte=one_day_ago,
            status='active'
        ).count()
        flagged_messages = room.messages.filter(is_flagged=True).count()
        pending_reports = ChatReport.objects.filter(
            message__room=room,
            status='pending'
        ).count()
        
        # Peak users today
        peak_users_today = room.user_sessions.filter(
            joined_at__gte=today_start
        ).count()
        
        # Average messages per user
        total_users = room.user_sessions.count()
        avg_messages_per_user = room.total_messages / total_users if total_users > 0 else 0
        
        stats_data = {
            'room_id': room.id,
            'room_name': room.name,
            'active_users': active_users,
            'messages_last_hour': messages_last_hour,
            'messages_last_24h': messages_last_24h,
            'flagged_messages': flagged_messages,
            'pending_reports': pending_reports,
            'peak_users_today': peak_users_today,
            'avg_messages_per_user': round(avg_messages_per_user, 2)
        }
        
        serializer = ChatRoomQuickStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def recent_messages(self, request, pk=None):
        """Get recent messages from the chat room."""
        room = self.get_object()
        limit = int(request.query_params.get('limit', 50))
        
        messages = room.messages.filter(
            status='active'
        ).select_related('user').order_by('-created_at')[:limit]
        
        serializer = ChatMessageSerializer(
            messages, 
            many=True, 
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def active_users(self, request, pk=None):
        """Get active users in the chat room."""
        room = self.get_object()
        
        sessions = room.user_sessions.filter(
            is_active=True
        ).select_related('user').order_by('-last_activity')
        
        serializer = ChatUserSessionSerializer(sessions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def create_match_room(self, request):
        """Create a chat room for a specific match."""
        match_id = request.data.get('match_id')
        if not match_id:
            return Response(
                {'error': 'match_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from core.models import Match
        try:
            match = Match.objects.get(id=match_id)
        except Match.DoesNotExist:
            return Response(
                {'error': 'Match not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if room already exists
        if ChatRoom.objects.filter(match=match).exists():
            return Response(
                {'error': 'Chat room already exists for this match'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create room
        room_name = f"{match.home_team.name} vs {match.away_team.name}"
        room = ChatRoom.objects.create(
            name=room_name,
            description=f"Live chat for {room_name} match",
            room_type='match',
            match=match,
            created_by=request.user
        )
        
        serializer = ChatRoomDetailSerializer(room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ChatMessageViewSet(viewsets.ModelViewSet):
    """ViewSet for chat message management."""
    
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter messages based on query parameters."""
        queryset = super().get_queryset().select_related(
            'user', 'room', 'moderated_by'
        )
        
        # Filters
        room_id = self.request.query_params.get('room', None)
        user_id = self.request.query_params.get('user', None)
        status_filter = self.request.query_params.get('status', None)
        flagged_only = self.request.query_params.get('flagged', None)
        
        if room_id:
            queryset = queryset.filter(room_id=room_id)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if flagged_only and flagged_only.lower() == 'true':
            queryset = queryset.filter(is_flagged=True)
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def flag_message(self, request, pk=None):
        """Flag a message for moderation."""
        message = self.get_object()
        reason = request.data.get('reason', 'Manual flag by admin')
        
        message.is_flagged = True
        message.flag_count = F('flag_count') + 1
        message.save(update_fields=['is_flagged', 'flag_count'])
        
        # Create moderation action
        ChatModeration.objects.create(
            room=message.room,
            moderator=request.user,
            target_message=message,
            action_type='message_delete',
            reason=reason
        )
        
        return Response({'message': 'Message flagged successfully'})
    
    @action(detail=True, methods=['post'])
    def unflag_message(self, request, pk=None):
        """Remove flag from a message."""
        message = self.get_object()
        
        message.is_flagged = False
        message.save(update_fields=['is_flagged'])
        
        return Response({'message': 'Message unflagged successfully'})
    
    @action(detail=True, methods=['post'])
    def hide_message(self, request, pk=None):
        """Hide a message."""
        message = self.get_object()
        reason = request.data.get('reason', 'Hidden by moderator')
        
        message.status = 'hidden'
        message.moderated_by = request.user
        message.moderated_at = timezone.now()
        message.moderation_reason = reason
        message.save(update_fields=[
            'status', 'moderated_by', 'moderated_at', 'moderation_reason'
        ])
        
        # Create moderation action
        ChatModeration.objects.create(
            room=message.room,
            moderator=request.user,
            target_user=message.user,
            target_message=message,
            action_type='message_delete',
            reason=reason
        )
        
        return Response({'message': 'Message hidden successfully'})
    
    @action(detail=True, methods=['post'])
    def delete_message(self, request, pk=None):
        """Delete a message."""
        message = self.get_object()
        reason = request.data.get('reason', 'Deleted by moderator')
        
        message.status = 'deleted'
        message.moderated_by = request.user
        message.moderated_at = timezone.now()
        message.moderation_reason = reason
        message.save(update_fields=[
            'status', 'moderated_by', 'moderated_at', 'moderation_reason'
        ])
        
        # Create moderation action
        ChatModeration.objects.create(
            room=message.room,
            moderator=request.user,
            target_user=message.user,
            target_message=message,
            action_type='message_delete',
            reason=reason
        )
        
        return Response({'message': 'Message deleted successfully'})


class ChatModerationViewSet(viewsets.ModelViewSet):
    """ViewSet for moderation actions."""
    
    queryset = ChatModeration.objects.all()
    serializer_class = ChatModerationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter moderation actions."""
        queryset = super().get_queryset().select_related(
            'moderator', 'target_user', 'room', 'target_message'
        )
        
        # Filters
        room_id = self.request.query_params.get('room', None)
        moderator_id = self.request.query_params.get('moderator', None)
        action_type = self.request.query_params.get('action_type', None)
        
        if room_id:
            queryset = queryset.filter(room_id=room_id)
        if moderator_id:
            queryset = queryset.filter(moderator_id=moderator_id)
        if action_type:
            queryset = queryset.filter(action_type=action_type)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set moderator to current user."""
        serializer.save(moderator=self.request.user)


class ChatReportViewSet(viewsets.ModelViewSet):
    """ViewSet for chat reports."""
    
    queryset = ChatReport.objects.all()
    serializer_class = ChatReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter reports."""
        queryset = super().get_queryset().select_related(
            'reporter', 'message__user', 'message__room', 'reviewed_by'
        )
        
        # Filters
        status_filter = self.request.query_params.get('status', None)
        room_id = self.request.query_params.get('room', None)
        reason = self.request.query_params.get('reason', None)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if room_id:
            queryset = queryset.filter(message__room_id=room_id)
        if reason:
            queryset = queryset.filter(reason=reason)
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def resolve_report(self, request, pk=None):
        """Resolve a report."""
        report = self.get_object()
        resolution_notes = request.data.get('resolution_notes', '')
        
        report.status = 'resolved'
        report.reviewed_by = request.user
        report.reviewed_at = timezone.now()
        report.resolution_notes = resolution_notes
        report.save(update_fields=[
            'status', 'reviewed_by', 'reviewed_at', 'resolution_notes'
        ])
        
        return Response({'message': 'Report resolved successfully'})
    
    @action(detail=True, methods=['post'])
    def dismiss_report(self, request, pk=None):
        """Dismiss a report."""
        report = self.get_object()
        resolution_notes = request.data.get('resolution_notes', '')
        
        report.status = 'dismissed'
        report.reviewed_by = request.user
        report.reviewed_at = timezone.now()
        report.resolution_notes = resolution_notes
        report.save(update_fields=[
            'status', 'reviewed_by', 'reviewed_at', 'resolution_notes'
        ])
        
        return Response({'message': 'Report dismissed successfully'})


class ChatBannedUserViewSet(viewsets.ModelViewSet):
    """ViewSet for banned users."""
    
    queryset = ChatBannedUser.objects.all()
    serializer_class = ChatBannedUserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter banned users."""
        queryset = super().get_queryset().select_related(
            'user', 'room', 'banned_by'
        )
        
        # Filters
        room_id = self.request.query_params.get('room', None)
        ban_type = self.request.query_params.get('ban_type', None)
        active_only = self.request.query_params.get('active_only', None)
        
        if room_id:
            queryset = queryset.filter(room_id=room_id)
        if ban_type:
            queryset = queryset.filter(ban_type=ban_type)
        if active_only and active_only.lower() == 'true':
            queryset = queryset.filter(is_active=True)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set banned_by to current user."""
        serializer.save(banned_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def unban_user(self, request, pk=None):
        """Unban a user."""
        ban = self.get_object()
        ban.is_active = False
        ban.save(update_fields=['is_active'])
        
        return Response({'message': 'User unbanned successfully'})


class ChatDashboardViewSet(viewsets.ViewSet):
    """ViewSet for chat dashboard statistics."""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get comprehensive chat statistics."""
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        one_day_ago = now - timedelta(hours=24)
        
        # Basic counts
        total_rooms = ChatRoom.objects.count()
        active_rooms = ChatRoom.objects.filter(status='active').count()
        total_messages_today = ChatMessage.objects.filter(
            created_at__gte=today_start,
            status='active'
        ).count()
        total_active_users = ChatUserSession.objects.filter(
            is_active=True
        ).count()
        
        # Moderation stats
        pending_reports = ChatReport.objects.filter(status='pending').count()
        flagged_messages = ChatMessage.objects.filter(is_flagged=True).count()
        banned_users = ChatBannedUser.objects.filter(is_active=True).count()
        
        # Top rooms by activity
        top_rooms = ChatRoom.objects.annotate(
            messages_today=Count(
                'messages',
                filter=Q(messages__created_at__gte=today_start, messages__status='active')
            )
        ).filter(messages_today__gt=0).order_by('-messages_today')[:10]
        
        top_rooms_data = [
            {
                'id': room.id,
                'name': room.name,
                'room_type': room.room_type,
                'messages_today': room.messages_today,
                'active_users': room.get_active_users_count()
            }
            for room in top_rooms
        ]
        
        # Recent activity (last 10 moderation actions)
        recent_activity = ChatModeration.objects.select_related(
            'moderator', 'target_user', 'room'
        ).order_by('-created_at')[:10]
        
        recent_activity_data = [
            {
                'id': action.id,
                'action_type': action.action_type,
                'moderator': action.moderator.username,
                'target_user': action.target_user.username if action.target_user else None,
                'room_name': action.room.name,
                'reason': action.reason,
                'created_at': action.created_at
            }
            for action in recent_activity
        ]
        
        # Moderation stats breakdown
        moderation_stats = {
            'actions_today': ChatModeration.objects.filter(
                created_at__gte=today_start
            ).count(),
            'warnings_today': ChatModeration.objects.filter(
                created_at__gte=today_start,
                action_type='warn'
            ).count(),
            'bans_today': ChatModeration.objects.filter(
                created_at__gte=today_start,
                action_type='ban'
            ).count(),
            'message_deletions_today': ChatModeration.objects.filter(
                created_at__gte=today_start,
                action_type='message_delete'
            ).count()
        }
        
        # Hourly activity for the last 24 hours
        hourly_activity = []
        for i in range(24):
            hour_start = (now - timedelta(hours=i)).replace(minute=0, second=0, microsecond=0)
            hour_end = hour_start + timedelta(hours=1)
            
            message_count = ChatMessage.objects.filter(
                created_at__gte=hour_start,
                created_at__lt=hour_end,
                status='active'
            ).count()
            
            hourly_activity.append({
                'hour': hour_start.strftime('%H:00'),
                'messages': message_count
            })
        
        hourly_activity.reverse()  # Show oldest first
        
        stats_data = {
            'total_rooms': total_rooms,
            'active_rooms': active_rooms,
            'total_messages_today': total_messages_today,
            'total_active_users': total_active_users,
            'pending_reports': pending_reports,
            'flagged_messages': flagged_messages,
            'banned_users': banned_users,
            'top_rooms': top_rooms_data,
            'recent_activity': recent_activity_data,
            'moderation_stats': moderation_stats,
            'hourly_activity': hourly_activity
        }
        
        serializer = ChatStatsSerializer(stats_data)
        return Response(serializer.data)
