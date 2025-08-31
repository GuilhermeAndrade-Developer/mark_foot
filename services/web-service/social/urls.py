"""
URL configuration for social app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserFollowViewSet, CommentViewSet, UserActivityViewSet,
    NotificationViewSet, SocialDashboardViewSet, UserSocialProfileViewSet,
    SocialPlatformViewSet, ShareTemplateViewSet, SocialShareViewSet,
    PrivateGroupViewSet, GroupMembershipViewSet, GroupPostViewSet, GroupInvitationViewSet
)

# Create router for API endpoints
router = DefaultRouter()
router.register(r'follows', UserFollowViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'activities', UserActivityViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'dashboard', SocialDashboardViewSet, basename='social-dashboard')
router.register(r'profiles', UserSocialProfileViewSet, basename='social-profiles')

# Social Sharing endpoints
router.register(r'platforms', SocialPlatformViewSet)
router.register(r'templates', ShareTemplateViewSet)
router.register(r'shares', SocialShareViewSet)

# Private Groups endpoints
router.register(r'groups', PrivateGroupViewSet)
router.register(r'memberships', GroupMembershipViewSet)
router.register(r'posts', GroupPostViewSet)
router.register(r'invitations', GroupInvitationViewSet)

app_name = 'social'

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
]
