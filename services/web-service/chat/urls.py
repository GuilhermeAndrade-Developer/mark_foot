"""
URL configuration for chat app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'rooms', views.ChatRoomViewSet, basename='chatroom')
router.register(r'messages', views.ChatMessageViewSet, basename='chatmessage')
router.register(r'moderation', views.ChatModerationViewSet, basename='chatmoderation')
router.register(r'reports', views.ChatReportViewSet, basename='chatreport')
router.register(r'banned-users', views.ChatBannedUserViewSet, basename='chatbanneduser')
router.register(r'dashboard', views.ChatDashboardViewSet, basename='chatdashboard')

app_name = 'chat'

urlpatterns = [
    path('', include(router.urls)),
]
