"""
URL configuration for social app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserFollowViewSet, CommentViewSet, UserActivityViewSet,
    NotificationViewSet, SocialDashboardViewSet, UserSocialProfileViewSet
)

# Create router for API endpoints
router = DefaultRouter()
router.register(r'follows', UserFollowViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'activities', UserActivityViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'dashboard', SocialDashboardViewSet, basename='social-dashboard')
router.register(r'profiles', UserSocialProfileViewSet, basename='social-profiles')

app_name = 'social'

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
]
