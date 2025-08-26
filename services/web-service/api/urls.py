"""
URL configuration for API app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    AreaViewSet, CompetitionViewSet, TeamViewSet, SeasonViewSet,
    MatchViewSet, StandingViewSet, PlayerViewSet, PlayerStatisticsViewSet,
    PlayerTransferViewSet, ApiSyncLogViewSet, DashboardViewSet
)
from .views_sync import (
    stats_summary, sync_competition, sync_players, api_status, sync_logs
)

# Create router for API endpoints
router = DefaultRouter()
router.register(r'areas', AreaViewSet)
router.register(r'competitions', CompetitionViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'seasons', SeasonViewSet)
router.register(r'matches', MatchViewSet)
router.register(r'standings', StandingViewSet)
router.register(r'players', PlayerViewSet)
router.register(r'player-statistics', PlayerStatisticsViewSet)
router.register(r'player-transfers', PlayerTransferViewSet)
router.register(r'api-sync-logs', ApiSyncLogViewSet)
router.register(r'dashboard', DashboardViewSet, basename='dashboard')

app_name = 'api'

urlpatterns = [
    # JWT Authentication endpoints
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Sync endpoints
    path('stats/summary/', stats_summary, name='stats_summary'),
    path('sync/competition/', sync_competition, name='sync_competition'),
    path('sync/players/', sync_players, name='sync_players'),
    path('sync/api-status/', api_status, name='api_status'),
    path('sync/logs/', sync_logs, name='sync_logs'),
    
    # API endpoints
    path('', include(router.urls)),
]
