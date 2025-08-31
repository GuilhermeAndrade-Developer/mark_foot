"""
Serializers for gamification API endpoints.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    UserProfile, Badge, UserBadge, FantasyLeague, FantasyTeam,
    Prediction, PredictionGame, Challenge, UserChallenge,
    PointTransaction, Leaderboard, LeaderboardEntry
)


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user gamification profile"""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'email', 'total_points', 'level', 'experience_points',
            'prediction_streak', 'login_streak', 'last_login_date', 'is_public_profile',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class BadgeSerializer(serializers.ModelSerializer):
    """Serializer for badges"""
    earned_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Badge
        fields = [
            'id', 'name', 'description', 'badge_type', 'rarity', 'icon_url',
            'points_reward', 'is_active', 'earned_count'
        ]
    
    def get_earned_count(self, obj):
        return obj.user_badges.count()


class UserBadgeSerializer(serializers.ModelSerializer):
    """Serializer for user badges"""
    badge_name = serializers.CharField(source='badge.name', read_only=True)
    badge_icon = serializers.CharField(source='badge.icon_url', read_only=True)
    badge_rarity = serializers.CharField(source='badge.rarity', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserBadge
        fields = [
            'id', 'user', 'username', 'badge', 'badge_name',
            'badge_icon', 'badge_rarity', 'earned_at', 'is_showcased'
        ]
        read_only_fields = ['earned_at']


class PredictionGameSerializer(serializers.ModelSerializer):
    """Serializer for prediction games"""
    active_predictions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PredictionGame
        fields = [
            'id', 'name', 'description', 'game_type', 'status', 'entry_fee_points',
            'reward_multiplier', 'created_at', 'active_predictions_count'
        ]
        read_only_fields = ['created_at']
    
    def get_active_predictions_count(self, obj):
        return obj.predictions.filter(status='pending').count()


class PredictionSerializer(serializers.ModelSerializer):
    """Serializer for predictions"""
    username = serializers.CharField(source='user.username', read_only=True)
    game_name = serializers.CharField(source='game.name', read_only=True)
    
    class Meta:
        model = Prediction
        fields = [
            'id', 'user', 'username', 'game', 'game_name', 'prediction_data',
            'points_earned', 'is_correct', 'created_at', 'resolved_at'
        ]
        read_only_fields = ['points_earned', 'is_correct', 'created_at', 'resolved_at']


class FantasyLeagueSerializer(serializers.ModelSerializer):
    """Serializer for fantasy leagues"""
    teams_count = serializers.SerializerMethodField()
    
    class Meta:
        model = FantasyLeague
        fields = [
            'id', 'name', 'description', 'league_type', 'max_participants',
            'entry_fee_points', 'prize_pool', 'is_active', 'join_code',
            'teams_count', 'created_at', 'starts_at', 'ends_at'
        ]
        read_only_fields = ['created_at']
    
    def get_teams_count(self, obj):
        return obj.fantasy_teams.count()


class FantasyTeamSerializer(serializers.ModelSerializer):
    """Serializer for fantasy teams"""
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    league_name = serializers.CharField(source='league.name', read_only=True)
    
    class Meta:
        model = FantasyTeam
        fields = [
            'id', 'name', 'formation', 'total_points', 'remaining_budget',
            'league', 'league_name', 'owner', 'owner_username',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['total_points', 'created_at', 'updated_at']


class ChallengeSerializer(serializers.ModelSerializer):
    """Serializer for challenges"""
    participants_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Challenge
        fields = [
            'id', 'title', 'description', 'challenge_type', 'status', 'requirements',
            'points_reward', 'start_date', 'end_date', 'max_participants',
            'current_participants', 'participants_count', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_participants_count(self, obj):
        return obj.user_challenges.count()


class UserChallengeSerializer(serializers.ModelSerializer):
    """Serializer for user challenge participation"""
    username = serializers.CharField(source='user.username', read_only=True)
    challenge_title = serializers.CharField(source='challenge.title', read_only=True)
    
    class Meta:
        model = UserChallenge
        fields = [
            'id', 'user', 'username', 'challenge', 'challenge_title',
            'status', 'completion_percentage', 'points_earned',
            'joined_at', 'completed_at'
        ]
        read_only_fields = ['points_earned', 'joined_at', 'completed_at']


class PointTransactionSerializer(serializers.ModelSerializer):
    """Serializer for point transactions"""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = PointTransaction
        fields = [
            'id', 'user', 'username', 'transaction_type', 'amount',
            'description', 'balance_after', 'created_at'
        ]
        read_only_fields = ['created_at']


class LeaderboardSerializer(serializers.ModelSerializer):
    """Serializer for leaderboards"""
    entries_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Leaderboard
        fields = [
            'id', 'name', 'leaderboard_type', 'description', 'is_active',
            'start_date', 'end_date', 'entries_count', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_entries_count(self, obj):
        return obj.entries.count()


class LeaderboardEntrySerializer(serializers.ModelSerializer):
    """Serializer for leaderboard entries"""
    username = serializers.CharField(source='user.username', read_only=True)
    leaderboard_name = serializers.CharField(source='leaderboard.name', read_only=True)
    
    class Meta:
        model = LeaderboardEntry
        fields = [
            'id', 'user', 'username', 'leaderboard', 'leaderboard_name',
            'rank', 'score', 'additional_data', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']