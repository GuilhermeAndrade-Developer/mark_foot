"""
API Views for gamification system.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.utils import timezone

from .models import (
    UserProfile, Badge, UserBadge, FantasyLeague, FantasyTeam,
    Prediction, PredictionGame, Challenge, UserChallenge,
    PointTransaction, Leaderboard, LeaderboardEntry
)
from .serializers import (
    UserProfileSerializer, BadgeSerializer, UserBadgeSerializer,
    FantasyLeagueSerializer, FantasyTeamSerializer, PredictionSerializer,
    PredictionGameSerializer, ChallengeSerializer, UserChallengeSerializer,
    PointTransactionSerializer, LeaderboardSerializer, LeaderboardEntrySerializer
)


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for user gamification profiles"""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile"""
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)


class BadgeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for badges (read-only)"""
    queryset = Badge.objects.filter(is_active=True)
    serializer_class = BadgeSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserBadgeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for user badges (read-only)"""
    queryset = UserBadge.objects.all()
    serializer_class = UserBadgeSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_badges(self, request):
        """Get current user's badges"""
        badges = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(badges, many=True)
        return Response(serializer.data)


class PredictionGameViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for prediction games"""
    queryset = PredictionGame.objects.filter(status='active')
    serializer_class = PredictionGameSerializer
    permission_classes = [permissions.IsAuthenticated]


class PredictionViewSet(viewsets.ModelViewSet):
    """ViewSet for predictions"""
    queryset = Prediction.objects.all()
    serializer_class = PredictionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_predictions(self, request):
        """Get current user's predictions"""
        predictions = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(predictions, many=True)
        return Response(serializer.data)


class FantasyLeagueViewSet(viewsets.ModelViewSet):
    """ViewSet for fantasy leagues"""
    queryset = FantasyLeague.objects.all()
    serializer_class = FantasyLeagueSerializer
    permission_classes = [permissions.IsAuthenticated]


class FantasyTeamViewSet(viewsets.ModelViewSet):
    """ViewSet for fantasy teams"""
    queryset = FantasyTeam.objects.all()
    serializer_class = FantasyTeamSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_teams(self, request):
        """Get current user's fantasy teams"""
        teams = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(teams, many=True)
        return Response(serializer.data)


class ChallengeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for challenges (read-only)"""
    queryset = Challenge.objects.filter(status='active')
    serializer_class = ChallengeSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join a challenge"""
        challenge = self.get_object()
        user = request.user
        
        # Check if already joined
        if UserChallenge.objects.filter(user=user, challenge=challenge).exists():
            return Response(
                {'error': 'Already joined this challenge'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create participation
        participation = UserChallenge.objects.create(
            user=user,
            challenge=challenge
        )
        
        serializer = UserChallengeSerializer(participation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserChallengeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for user challenge participation"""
    queryset = UserChallenge.objects.all()
    serializer_class = UserChallengeSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_challenges(self, request):
        """Get current user's challenge participation"""
        challenges = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(challenges, many=True)
        return Response(serializer.data)


class PointTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for point transactions (read-only)"""
    queryset = PointTransaction.objects.all()
    serializer_class = PointTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_transactions(self, request):
        """Get current user's transactions"""
        transactions = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)


class LeaderboardViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for leaderboards"""
    queryset = Leaderboard.objects.filter(is_active=True)
    serializer_class = LeaderboardSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def entries(self, request, pk=None):
        """Get leaderboard entries"""
        leaderboard = self.get_object()
        entries = LeaderboardEntry.objects.filter(
            leaderboard=leaderboard
        ).select_related('user').order_by('rank')
        
        serializer = LeaderboardEntrySerializer(entries, many=True)
        return Response(serializer.data)


class LeaderboardEntryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for leaderboard entries"""
    queryset = LeaderboardEntry.objects.all()
    serializer_class = LeaderboardEntrySerializer
    permission_classes = [permissions.IsAuthenticated]


class DashboardViewSet(viewsets.ViewSet):
    """ViewSet for dashboard data"""
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get user dashboard statistics"""
        user = request.user
        profile = user.user_profiles.first()
        
        if not profile:
            profile = UserProfile.objects.create(user=user)
        
        # Calculate stats
        badges_count = UserBadge.objects.filter(user=user).count()
        predictions_count = Prediction.objects.filter(user=user).count()
        challenges_completed = UserChallenge.objects.filter(
            user=user, is_completed=True
        ).count()
        fantasy_teams_count = FantasyTeam.objects.filter(user=user).count()
        
        # Simple rank calculation
        higher_points = UserProfile.objects.filter(
            total_points__gt=profile.total_points
        ).count()
        current_rank = higher_points + 1
        
        stats = {
            'total_points': profile.total_points,
            'level': profile.level,
            'badges_count': badges_count,
            'predictions_count': predictions_count,
            'challenges_completed': challenges_completed,
            'fantasy_teams_count': fantasy_teams_count,
            'current_rank': current_rank
        }
        
        return Response(stats)

    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """Get top users leaderboard"""
        top_users = UserProfile.objects.select_related('user').order_by(
            '-total_points'
        )[:10]
        
        leaderboard_data = []
        for idx, profile in enumerate(top_users, 1):
            leaderboard_data.append({
                'rank': idx,
                'username': profile.user.username,
                'total_points': profile.total_points,
                'level': profile.level
            })
        
        return Response(leaderboard_data)