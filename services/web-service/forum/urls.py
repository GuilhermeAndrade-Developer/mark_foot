from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ForumCategoryViewSet,
    ForumTopicViewSet,
    ForumPostViewSet,
    ForumStatsViewSet,
    ForumSearchViewSet,
    ForumUserProfileViewSet
)

# Criar router para as ViewSets
router = DefaultRouter()
router.register(r'categories', ForumCategoryViewSet, basename='forum-category')
router.register(r'topics', ForumTopicViewSet, basename='forum-topic')
router.register(r'posts', ForumPostViewSet, basename='forum-post')
router.register(r'stats', ForumStatsViewSet, basename='forum-stats')
router.register(r'search', ForumSearchViewSet, basename='forum-search')
router.register(r'profiles', ForumUserProfileViewSet, basename='forum-profile')

app_name = 'forum'

urlpatterns = [
    path('', include(router.urls)),
]
