"""
URL configuration for gamification app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserProfileViewSet, BadgeViewSet, UserBadgeViewSet,
    FantasyLeagueViewSet, FantasyTeamViewSet, PredictionViewSet,
    PredictionGameViewSet, ChallengeViewSet, UserChallengeViewSet,
    PointTransactionViewSet, LeaderboardViewSet, LeaderboardEntryViewSet,
    DashboardViewSet
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet, basename='userprofile')
router.register(r'badges', BadgeViewSet, basename='badge')
router.register(r'user-badges', UserBadgeViewSet, basename='userbadge')
router.register(r'prediction-games', PredictionGameViewSet, basename='predictiongame')
router.register(r'predictions', PredictionViewSet, basename='prediction')
router.register(r'fantasy-leagues', FantasyLeagueViewSet, basename='fantasyleague')
router.register(r'fantasy-teams', FantasyTeamViewSet, basename='fantasyteam')
router.register(r'challenges', ChallengeViewSet, basename='challenge')
router.register(r'user-challenges', UserChallengeViewSet, basename='userchallenge')
router.register(r'transactions', PointTransactionViewSet, basename='pointtransaction')
router.register(r'leaderboards', LeaderboardViewSet, basename='leaderboard')
router.register(r'leaderboard-entries', LeaderboardEntryViewSet, basename='leaderboardentry')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')

app_name = 'gamification'

urlpatterns = [
    path('', include(router.urls)),
]
