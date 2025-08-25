"""
Serializers for the Mark Foot API
"""
from rest_framework import serializers
from core.models import (
    Area, Competition, Team, Season, Match, Standing, 
    ApiSyncLog, Player, PlayerStatistics, PlayerTransfer
)


class AreaSerializer(serializers.ModelSerializer):
    """Serializer for Area model"""
    
    class Meta:
        model = Area
        fields = [
            'id', 'name', 'code', 'flag_url', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CompetitionSerializer(serializers.ModelSerializer):
    """Serializer for Competition model"""
    area = AreaSerializer(read_only=True)
    area_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Competition
        fields = [
            'id', 'area', 'area_id', 'name', 'code', 'type', 
            'emblem_url', 'plan', 'current_season_id', 
            'number_of_available_seasons', 'last_updated',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class TeamSerializer(serializers.ModelSerializer):
    """Serializer for Team model"""
    area = AreaSerializer(read_only=True)
    area_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Team
        fields = [
            'id', 'area', 'area_id', 'name', 'short_name', 'tla',
            'crest_url', 'address', 'phone', 'website', 'email',
            'founded', 'club_colors', 'venue', 'last_updated',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class SeasonSerializer(serializers.ModelSerializer):
    """Serializer for Season model"""
    competition = CompetitionSerializer(read_only=True)
    competition_id = serializers.IntegerField(write_only=True)
    winner_team = TeamSerializer(read_only=True)
    winner_team_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Season
        fields = [
            'id', 'competition', 'competition_id', 'start_date', 
            'end_date', 'current_matchday', 'winner_team', 
            'winner_team_id', 'available', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class MatchSerializer(serializers.ModelSerializer):
    """Serializer for Match model"""
    competition = CompetitionSerializer(read_only=True)
    competition_id = serializers.IntegerField(write_only=True)
    season = SeasonSerializer(read_only=True)
    season_id = serializers.IntegerField(write_only=True)
    home_team = TeamSerializer(read_only=True)
    home_team_id = serializers.IntegerField(write_only=True)
    away_team = TeamSerializer(read_only=True)
    away_team_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Match
        fields = [
            'id', 'competition', 'competition_id', 'season', 'season_id',
            'home_team', 'home_team_id', 'away_team', 'away_team_id',
            'utc_date', 'status', 'stage', 'group_name', 'matchday',
            'last_updated', 'home_team_score', 'away_team_score',
            'winner', 'duration', 'attendance', 'referee_name',
            'venue', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class StandingSerializer(serializers.ModelSerializer):
    """Serializer for Standing model"""
    competition = CompetitionSerializer(read_only=True)
    competition_id = serializers.IntegerField(write_only=True)
    season = SeasonSerializer(read_only=True)
    season_id = serializers.IntegerField(write_only=True)
    team = TeamSerializer(read_only=True)
    team_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Standing
        fields = [
            'id', 'competition', 'competition_id', 'season', 'season_id',
            'team', 'team_id', 'stage', 'type', 'group_name',
            'position', 'played_games', 'form', 'won', 'draw', 'lost',
            'points', 'goals_for', 'goals_against', 'goal_difference',
            'snapshot_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class PlayerSerializer(serializers.ModelSerializer):
    """Serializer for Player model"""
    team = TeamSerializer(read_only=True)
    team_id = serializers.IntegerField(write_only=True, required=False)
    age_calculated = serializers.ReadOnlyField()
    
    class Meta:
        model = Player
        fields = [
            'id', 'external_id', 'name', 'short_name', 'team', 'team_id',
            'nationality', 'date_of_birth', 'age', 'age_calculated',
            'gender', 'position', 'position_category', 'status',
            'photo_url', 'cutout_url', 'description', 'height',
            'weight', 'wage', 'created_at', 'updated_at', 'last_sync'
        ]
        read_only_fields = ['created_at', 'updated_at', 'last_sync']


class PlayerStatisticsSerializer(serializers.ModelSerializer):
    """Serializer for PlayerStatistics model"""
    player = PlayerSerializer(read_only=True)
    player_id = serializers.IntegerField(write_only=True)
    season = SeasonSerializer(read_only=True)
    season_id = serializers.IntegerField(write_only=True)
    competition = CompetitionSerializer(read_only=True)
    competition_id = serializers.IntegerField(write_only=True, required=False)
    goals_per_game = serializers.ReadOnlyField()
    assists_per_game = serializers.ReadOnlyField()
    
    class Meta:
        model = PlayerStatistics
        fields = [
            'id', 'player', 'player_id', 'season', 'season_id',
            'competition', 'competition_id', 'appearances',
            'minutes_played', 'starts', 'substitutions_in',
            'substitutions_out', 'goals', 'assists', 'penalty_goals',
            'freekick_goals', 'yellow_cards', 'red_cards',
            'clean_sheets', 'saves', 'goals_conceded', 'rating',
            'goals_per_game', 'assists_per_game',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class PlayerTransferSerializer(serializers.ModelSerializer):
    """Serializer for PlayerTransfer model"""
    player = PlayerSerializer(read_only=True)
    player_id = serializers.IntegerField(write_only=True)
    from_team = TeamSerializer(read_only=True)
    from_team_id = serializers.IntegerField(write_only=True, required=False)
    to_team = TeamSerializer(read_only=True)
    to_team_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = PlayerTransfer
        fields = [
            'id', 'player', 'player_id', 'from_team', 'from_team_id',
            'to_team', 'to_team_id', 'transfer_date', 'transfer_type',
            'transfer_fee', 'currency', 'is_confirmed',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ApiSyncLogSerializer(serializers.ModelSerializer):
    """Serializer for ApiSyncLog model"""
    
    class Meta:
        model = ApiSyncLog
        fields = [
            'id', 'endpoint', 'http_status', 'records_processed',
            'records_inserted', 'records_updated', 'records_failed',
            'execution_time_ms', 'error_message', 'request_params',
            'response_data', 'sync_date', 'created_at'
        ]
        read_only_fields = ['created_at']


# Dashboard-specific serializers
class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    total_teams = serializers.IntegerField()
    total_players = serializers.IntegerField()
    total_competitions = serializers.IntegerField()
    total_matches = serializers.IntegerField()
    recent_matches_count = serializers.IntegerField()
    active_players_count = serializers.IntegerField()


class RecentMatchSerializer(serializers.ModelSerializer):
    """Simplified serializer for recent matches on dashboard"""
    home_team_name = serializers.CharField(source='home_team.name')
    away_team_name = serializers.CharField(source='away_team.name')
    home_team_crest = serializers.URLField(source='home_team.crest_url')
    away_team_crest = serializers.URLField(source='away_team.crest_url')
    competition_name = serializers.CharField(source='competition.name')
    
    class Meta:
        model = Match
        fields = [
            'id', 'home_team_name', 'away_team_name', 'home_team_crest',
            'away_team_crest', 'competition_name', 'utc_date', 'status',
            'home_team_score', 'away_team_score'
        ]


class TopPlayerSerializer(serializers.Serializer):
    """Serializer for top players statistics"""
    player_name = serializers.CharField()
    team_name = serializers.CharField()
    total_goals = serializers.IntegerField()
    total_assists = serializers.IntegerField()
    total_appearances = serializers.IntegerField()
