"""
API Views for social features.
"""

from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Count, Q, F
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from .models import (
    UserFollow, Comment, CommentLike, UserActivity, 
    Notification, CommentReport
)
from .serializers import (
    UserFollowSerializer, CommentSerializer, CommentCreateSerializer,
    CommentLikeSerializer, UserActivitySerializer, NotificationSerializer,
    CommentReportSerializer, SocialStatsSerializer, UserSocialProfileSerializer
)


class UserFollowViewSet(viewsets.ModelViewSet):
    """ViewSet for user following system"""
    queryset = UserFollow.objects.all()
    serializer_class = UserFollowSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter based on query parameters"""
        queryset = super().get_queryset()
        user_id = self.request.query_params.get('user', None)
        if user_id:
            queryset = queryset.filter(Q(follower_id=user_id) | Q(followed_id=user_id))
        return queryset.select_related('follower', 'followed')
    
    def perform_create(self, serializer):
        """Set follower as current user"""
        serializer.save(follower=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_followers(self, request):
        """Get current user's followers"""
        followers = self.get_queryset().filter(followed=request.user)
        serializer = self.get_serializer(followers, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_following(self, request):
        """Get users current user follows"""
        following = self.get_queryset().filter(follower=request.user)
        serializer = self.get_serializer(following, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def follow_user(self, request):
        """Follow a user"""
        followed_id = request.data.get('user_id')
        if not followed_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            followed_user = User.objects.get(id=followed_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if followed_user == request.user:
            return Response({'error': 'Cannot follow yourself'}, status=status.HTTP_400_BAD_REQUEST)
        
        follow, created = UserFollow.objects.get_or_create(
            follower=request.user,
            followed=followed_user
        )
        
        if created:
            # Create notification
            Notification.objects.create(
                recipient=followed_user,
                sender=request.user,
                notification_type='new_follower',
                title='New Follower',
                message=f'{request.user.username} started following you',
                related_follow=follow
            )
            
            # Create activity
            UserActivity.objects.create(
                user=request.user,
                activity_type='follow',
                description=f'Started following {followed_user.username}',
                related_user=followed_user
            )
        
        serializer = self.get_serializer(follow)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def unfollow_user(self, request):
        """Unfollow a user"""
        followed_id = request.data.get('user_id')
        if not followed_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            follow = UserFollow.objects.get(
                follower=request.user,
                followed_id=followed_id
            )
            follow.delete()
            return Response({'message': 'Unfollowed successfully'}, status=status.HTTP_200_OK)
        except UserFollow.DoesNotExist:
            return Response({'error': 'Not following this user'}, status=status.HTTP_404_NOT_FOUND)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for comments"""
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        """Use different serializers for create/update vs read"""
        if self.action in ['create', 'update', 'partial_update']:
            return CommentCreateSerializer
        return CommentSerializer
    
    def get_queryset(self):
        """Filter comments based on query parameters"""
        queryset = Comment.objects.filter(status='active').select_related(
            'user', 'match', 'team', 'parent'
        ).prefetch_related('replies')
        
        # Filter by content type
        match_id = self.request.query_params.get('match', None)
        team_id = self.request.query_params.get('team', None)
        user_id = self.request.query_params.get('user', None)
        parent_id = self.request.query_params.get('parent', None)
        
        if match_id:
            queryset = queryset.filter(match_id=match_id)
        if team_id:
            queryset = queryset.filter(team_id=team_id)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set user as current user and create activity"""
        comment = serializer.save(user=self.request.user)
        
        # Create activity
        UserActivity.objects.create(
            user=self.request.user,
            activity_type='comment',
            description=f'Posted a comment',
            related_comment=comment,
            related_match=comment.match
        )
        
        # Create notification for parent comment author
        if comment.parent and comment.parent.user != self.request.user:
            Notification.objects.create(
                recipient=comment.parent.user,
                sender=self.request.user,
                notification_type='comment_reply',
                title='New Reply',
                message=f'{self.request.user.username} replied to your comment',
                related_comment=comment
            )
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Like a comment"""
        comment = self.get_object()
        
        # Toggle like
        like, created = CommentLike.objects.get_or_create(
            user=request.user,
            comment=comment,
            defaults={'reaction_type': 'like'}
        )
        
        if not created:
            if like.reaction_type == 'like':
                like.delete()
                # Update counter
                comment.likes_count = F('likes_count') - 1
                comment.save(update_fields=['likes_count'])
                return Response({'message': 'Like removed'})
            else:
                like.reaction_type = 'like'
                like.save()
                # Update counters
                comment.likes_count = F('likes_count') + 1
                comment.dislikes_count = F('dislikes_count') - 1
                comment.save(update_fields=['likes_count', 'dislikes_count'])
        else:
            # Update counter
            comment.likes_count = F('likes_count') + 1
            comment.save(update_fields=['likes_count'])
            
            # Create notification
            if comment.user != request.user:
                Notification.objects.create(
                    recipient=comment.user,
                    sender=request.user,
                    notification_type='comment_like',
                    title='Comment Liked',
                    message=f'{request.user.username} liked your comment',
                    related_comment=comment
                )
        
        return Response({'message': 'Comment liked'})
    
    @action(detail=True, methods=['post'])
    def dislike(self, request, pk=None):
        """Dislike a comment"""
        comment = self.get_object()
        
        # Toggle dislike
        like, created = CommentLike.objects.get_or_create(
            user=request.user,
            comment=comment,
            defaults={'reaction_type': 'dislike'}
        )
        
        if not created:
            if like.reaction_type == 'dislike':
                like.delete()
                # Update counter
                comment.dislikes_count = F('dislikes_count') - 1
                comment.save(update_fields=['dislikes_count'])
                return Response({'message': 'Dislike removed'})
            else:
                like.reaction_type = 'dislike'
                like.save()
                # Update counters
                comment.dislikes_count = F('dislikes_count') + 1
                comment.likes_count = F('likes_count') - 1
                comment.save(update_fields=['likes_count', 'dislikes_count'])
        else:
            # Update counter
            comment.dislikes_count = F('dislikes_count') + 1
            comment.save(update_fields=['dislikes_count'])
        
        return Response({'message': 'Comment disliked'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def report(self, request, pk=None):
        """Report a comment"""
        comment = self.get_object()
        reason = request.data.get('reason', 'other')
        description = request.data.get('description', '')
        
        report, created = CommentReport.objects.get_or_create(
            reporter=request.user,
            comment=comment,
            defaults={
                'reason': reason,
                'description': description
            }
        )
        
        if created:
            # Update comment flag count
            comment.flagged_count = F('flagged_count') + 1
            if comment.flagged_count >= 3:  # Auto-flag after 3 reports
                comment.is_flagged = True
            comment.save(update_fields=['flagged_count', 'is_flagged'])
        
        return Response({
            'message': 'Comment reported successfully' if created else 'Already reported'
        })


class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for user activities (read-only)"""
    queryset = UserActivity.objects.all()
    serializer_class = UserActivitySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter activities based on following"""
        queryset = super().get_queryset().select_related('user', 'related_user')
        
        # Get activities from followed users
        followed_users = UserFollow.objects.filter(
            follower=self.request.user
        ).values_list('followed', flat=True)
        
        return queryset.filter(
            Q(user=self.request.user) |  # Own activities
            Q(user__in=followed_users)   # Followed users' activities
        ).order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def feed(self, request):
        """Get social feed for current user"""
        activities = self.get_queryset()[:50]  # Limit to 50 recent activities
        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for notifications"""
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get notifications for current user"""
        return super().get_queryset().filter(
            recipient=self.request.user
        ).select_related('sender').order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        updated = self.get_queryset().filter(is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
        return Response({'message': f'{updated} notifications marked as read'})
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark single notification as read"""
        notification = self.get_object()
        notification.mark_as_read()
        return Response({'message': 'Notification marked as read'})


class SocialDashboardViewSet(viewsets.ViewSet):
    """ViewSet for social dashboard statistics"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get social dashboard statistics"""
        # Basic counts
        total_comments = Comment.objects.count()
        total_users = User.objects.count()
        total_follows = UserFollow.objects.count()
        
        # Today's activity
        today = timezone.now().date()
        active_comments_today = Comment.objects.filter(
            created_at__date=today,
            status='active'
        ).count()
        
        # Moderation stats
        pending_reports = CommentReport.objects.filter(status='pending').count()
        flagged_comments = Comment.objects.filter(is_flagged=True).count()
        
        # Top commenters
        top_commenters = User.objects.annotate(
            comment_count=Count('comment', filter=Q(comment__status='active'))
        ).filter(comment_count__gt=0).order_by('-comment_count')[:10]
        
        top_commenters_data = [
            {
                'id': user.id,
                'username': user.username,
                'comment_count': user.comment_count
            }
            for user in top_commenters
        ]
        
        # Recent activities
        recent_activities = UserActivity.objects.select_related('user').order_by('-created_at')[:10]
        recent_activities_data = UserActivitySerializer(recent_activities, many=True).data
        
        stats_data = {
            'total_comments': total_comments,
            'total_users': total_users,
            'total_follows': total_follows,
            'active_comments_today': active_comments_today,
            'pending_reports': pending_reports,
            'flagged_comments': flagged_comments,
            'top_commenters': top_commenters_data,
            'recent_activities': recent_activities_data
        }
        
        serializer = SocialStatsSerializer(stats_data)
        return Response(serializer.data)


class UserSocialProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for user social profiles"""
    queryset = User.objects.all()
    serializer_class = UserSocialProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Optimize queryset with prefetch"""
        return super().get_queryset().prefetch_related(
            'followers', 'following', 'comment_set'
        )
