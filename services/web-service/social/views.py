"""
API Views for social features.
"""

from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Count, Q, F
from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from .models import (
    UserFollow, Comment, CommentLike, UserActivity, 
    Notification, CommentReport, SocialPlatform, ShareTemplate,
    SocialShare, PrivateGroup, GroupMembership, GroupPost, GroupInvitation
)
from .serializers import (
    UserFollowSerializer, CommentSerializer, CommentCreateSerializer,
    CommentLikeSerializer, UserActivitySerializer, NotificationSerializer,
    CommentReportSerializer, SocialStatsSerializer, UserSocialProfileSerializer,
    SocialPlatformSerializer, SocialPlatformAdminSerializer, ShareTemplateSerializer,
    SocialShareSerializer, SocialShareCreateSerializer, PrivateGroupSerializer,
    GroupMembershipSerializer, GroupPostSerializer, GroupInvitationSerializer,
    GroupInvitationCreateSerializer, SocialSharingStatsSerializer, GroupStatsSerializer
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


class SocialPlatformViewSet(viewsets.ModelViewSet):
    """ViewSet for social media platforms"""
    queryset = SocialPlatform.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Use admin serializer for staff users"""
        if self.request.user.is_staff:
            return SocialPlatformAdminSerializer
        return SocialPlatformSerializer
    
    def get_queryset(self):
        """Filter active platforms for non-staff users"""
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        return queryset.order_by('name')


class ShareTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for share templates"""
    queryset = ShareTemplate.objects.all()
    serializer_class = ShareTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter by platform and type"""
        queryset = super().get_queryset().select_related('platform')
        
        platform = self.request.query_params.get('platform')
        template_type = self.request.query_params.get('type')
        
        if platform:
            queryset = queryset.filter(platform_id=platform)
        if template_type:
            queryset = queryset.filter(template_type=template_type)
        
        return queryset.filter(is_active=True).order_by('name')


class SocialShareViewSet(viewsets.ModelViewSet):
    """ViewSet for social shares"""
    queryset = SocialShare.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Use create serializer for create/update"""
        if self.action in ['create', 'update', 'partial_update']:
            return SocialShareCreateSerializer
        return SocialShareSerializer
    
    def get_queryset(self):
        """Filter shares by user and platform"""
        queryset = super().get_queryset().select_related(
            'platform', 'template', 'user', 'match', 'team'
        )
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        platform = self.request.query_params.get('platform')
        status_filter = self.request.query_params.get('status')
        
        if platform:
            queryset = queryset.filter(platform_id=platform)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set user as current user"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get social sharing statistics"""
        from django.db.models import Count
        from datetime import datetime, timedelta
        
        queryset = self.get_queryset()
        
        # Basic stats
        total_shares = queryset.count()
        shares_today = queryset.filter(created_at__date=timezone.now().date()).count()
        shares_this_week = queryset.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        shares_this_month = queryset.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        # Shares by platform
        shares_by_platform = dict(
            queryset.values('platform__name').annotate(
                count=Count('id')
            ).values_list('platform__name', 'count')
        )
        
        # Top shared content
        top_shared_content = []
        # This would need more complex logic based on engagement metrics
        
        # Most active users
        most_active_users = []
        if request.user.is_staff:
            most_active_users = list(
                queryset.values('user__username').annotate(
                    share_count=Count('id')
                ).order_by('-share_count')[:10]
            )
        
        # Engagement metrics
        engagement_metrics = {
            'total_likes': sum(queryset.values_list('likes_count', flat=True)),
            'total_shares': sum(queryset.values_list('shares_count', flat=True)),
            'total_comments': sum(queryset.values_list('comments_count', flat=True)),
            'total_views': sum(queryset.values_list('views_count', flat=True)),
        }
        
        stats_data = {
            'total_shares': total_shares,
            'shares_by_platform': shares_by_platform,
            'shares_today': shares_today,
            'shares_this_week': shares_this_week,
            'shares_this_month': shares_this_month,
            'top_shared_content': top_shared_content,
            'most_active_users': most_active_users,
            'engagement_metrics': engagement_metrics
        }
        
        serializer = SocialSharingStatsSerializer(stats_data)
        return Response(serializer.data)


class PrivateGroupViewSet(viewsets.ModelViewSet):
    """ViewSet for private groups"""
    queryset = PrivateGroup.objects.all()
    serializer_class = PrivateGroupSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter groups based on user access"""
        queryset = super().get_queryset().prefetch_related('memberships')
        
        # For non-staff users, only show groups they're members of or public groups
        if not self.request.user.is_staff:
            user_groups = GroupMembership.objects.filter(
                user=self.request.user,
                status='active'
            ).values_list('group_id', flat=True)
            
            queryset = queryset.filter(
                Q(id__in=user_groups) | Q(privacy_level='public')
            )
        
        # Filter by group type
        group_type = self.request.query_params.get('type')
        if group_type:
            queryset = queryset.filter(group_type=group_type)
        
        return queryset.filter(is_active=True).order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join a group"""
        group = self.get_object()
        
        # Check if user can join
        if group.memberships.filter(user=request.user).exists():
            return Response(
                {'error': 'Already a member of this group'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check privacy level
        if group.privacy_level == 'private':
            return Response(
                {'error': 'This is a private group. Invitation required.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create membership
        membership_status = 'active' if group.privacy_level == 'public' else 'pending'
        if group.require_admin_approval:
            membership_status = 'pending'
        
        membership = GroupMembership.objects.create(
            group=group,
            user=request.user,
            status=membership_status
        )
        
        # Update group member count if active
        if membership_status == 'active':
            group.member_count = F('member_count') + 1
            group.save(update_fields=['member_count'])
        
        serializer = GroupMembershipSerializer(membership)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave a group"""
        group = self.get_object()
        
        try:
            membership = group.memberships.get(user=request.user, status='active')
            membership.status = 'left'
            membership.left_at = timezone.now()
            membership.save()
            
            # Update group member count
            group.member_count = F('member_count') - 1
            group.save(update_fields=['member_count'])
            
            return Response({'message': 'Left group successfully'})
        except GroupMembership.DoesNotExist:
            return Response(
                {'error': 'Not a member of this group'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get group statistics"""
        queryset = PrivateGroup.objects.all()
        
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Basic stats
        total_groups = queryset.count()
        total_members = GroupMembership.objects.filter(status='active').count()
        total_posts = GroupPost.objects.count()
        
        # Groups by type
        groups_by_type = dict(
            queryset.values('group_type').annotate(
                count=Count('id')
            ).values_list('group_type', 'count')
        )
        
        # Groups by privacy
        groups_by_privacy = dict(
            queryset.values('privacy_level').annotate(
                count=Count('id')
            ).values_list('privacy_level', 'count')
        )
        
        # Most active groups
        most_active_groups = list(
            queryset.annotate(
                recent_posts=Count('posts', filter=Q(
                    posts__created_at__gte=timezone.now() - timedelta(days=7)
                ))
            ).order_by('-recent_posts')[:10].values(
                'name', 'recent_posts', 'member_count'
            )
        )
        
        # Recent activity (simplified)
        recent_activity = []
        
        stats_data = {
            'total_groups': total_groups,
            'total_members': total_members,
            'total_posts': total_posts,
            'groups_by_type': groups_by_type,
            'groups_by_privacy': groups_by_privacy,
            'most_active_groups': most_active_groups,
            'recent_activity': recent_activity
        }
        
        serializer = GroupStatsSerializer(stats_data)
        return Response(serializer.data)


class GroupMembershipViewSet(viewsets.ModelViewSet):
    """ViewSet for group memberships"""
    queryset = GroupMembership.objects.all()
    serializer_class = GroupMembershipSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter memberships based on group access"""
        queryset = super().get_queryset().select_related('user', 'group', 'invited_by')
        
        group_id = self.request.query_params.get('group')
        user_id = self.request.query_params.get('user')
        
        if group_id:
            queryset = queryset.filter(group_id=group_id)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # For non-staff users, only show memberships for groups they're admins of
        # or their own memberships
        if not self.request.user.is_staff:
            admin_groups = GroupMembership.objects.filter(
                user=self.request.user,
                role__in=['owner', 'admin'],
                status='active'
            ).values_list('group_id', flat=True)
            
            queryset = queryset.filter(
                Q(group_id__in=admin_groups) | Q(user=self.request.user)
            )
        
        return queryset.order_by('-joined_at')


class GroupPostViewSet(viewsets.ModelViewSet):
    """ViewSet for group posts"""
    queryset = GroupPost.objects.all()
    serializer_class = GroupPostSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter posts based on group membership"""
        queryset = super().get_queryset().select_related('author', 'group')
        
        group_id = self.request.query_params.get('group')
        if group_id:
            queryset = queryset.filter(group_id=group_id)
        
        # Check if user has access to the group
        if not self.request.user.is_staff:
            user_groups = GroupMembership.objects.filter(
                user=self.request.user,
                status='active'
            ).values_list('group_id', flat=True)
            
            queryset = queryset.filter(group_id__in=user_groups)
        
        return queryset.filter(is_approved=True).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set author as current user"""
        serializer.save(author=self.request.user)


class GroupInvitationViewSet(viewsets.ModelViewSet):
    """ViewSet for group invitations"""
    queryset = GroupInvitation.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Use create serializer for create action"""
        if self.action == 'create':
            return GroupInvitationCreateSerializer
        return GroupInvitationSerializer
    
    def get_queryset(self):
        """Filter invitations for current user"""
        queryset = super().get_queryset().select_related('group', 'inviter', 'invitee')
        
        # Show invitations sent by user or received by user
        return queryset.filter(
            Q(inviter=self.request.user) | Q(invitee=self.request.user)
        ).order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept a group invitation"""
        invitation = self.get_object()
        
        if invitation.invitee != request.user:
            return Response(
                {'error': 'Not authorized to accept this invitation'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not invitation.can_respond():
            return Response(
                {'error': 'Invitation cannot be accepted (expired or already responded)'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create membership
        membership = GroupMembership.objects.create(
            group=invitation.group,
            user=invitation.invitee,
            status='active',
            invited_by=invitation.inviter,
            invitation_message=invitation.message
        )
        
        # Update invitation
        invitation.status = 'accepted'
        invitation.responded_at = timezone.now()
        invitation.save()
        
        # Update group member count
        invitation.group.member_count = F('member_count') + 1
        invitation.group.save(update_fields=['member_count'])
        
        serializer = GroupMembershipSerializer(membership)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        """Decline a group invitation"""
        invitation = self.get_object()
        
        if invitation.invitee != request.user:
            return Response(
                {'error': 'Not authorized to decline this invitation'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not invitation.can_respond():
            return Response(
                {'error': 'Invitation cannot be declined (expired or already responded)'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update invitation
        invitation.status = 'declined'
        invitation.responded_at = timezone.now()
        invitation.response_message = request.data.get('message', '')
        invitation.save()
        
        return Response({'message': 'Invitation declined'})
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending invitations for current user"""
        invitations = self.get_queryset().filter(
            invitee=request.user,
            status='pending'
        )
        serializer = self.get_serializer(invitations, many=True)
        return Response(serializer.data)
