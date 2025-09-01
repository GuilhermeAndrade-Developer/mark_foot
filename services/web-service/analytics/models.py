from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import Team, Player, Match, Competition
import uuid


class UserAnalyticsPreference(models.Model):
    """User preferences for analytics and reports"""
    REPORT_FREQUENCY = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'), 
        ('monthly', 'Monthly'),
        ('never', 'Never'),
    ]
    
    WIDGET_TYPES = [
        ('team_performance', 'Team Performance'),
        ('player_stats', 'Player Statistics'),
        ('match_predictions', 'Match Predictions'),
        ('betting_odds', 'Betting Odds'),
        ('market_value', 'Market Value'),
        ('injury_risk', 'Injury Risk'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='analytics_preferences')
    
    # Report preferences
    report_frequency = models.CharField(max_length=20, choices=REPORT_FREQUENCY, default='weekly')
    auto_generate_reports = models.BooleanField(default=True)
    email_reports = models.BooleanField(default=True)
    whatsapp_reports = models.BooleanField(default=False)
    
    # Dashboard preferences
    favorite_teams = models.ManyToManyField(Team, blank=True, related_name='favorited_by_users')
    favorite_players = models.ManyToManyField(Player, blank=True, related_name='favorited_by_users')
    favorite_competitions = models.ManyToManyField(Competition, blank=True, related_name='favorited_by_users')
    
    # Widget preferences
    enabled_widgets = models.JSONField(default=list, blank=True)
    widget_layout = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'analytics_user_preferences'
        verbose_name = 'User Analytics Preference'
        verbose_name_plural = 'User Analytics Preferences'
    
    def __str__(self):
        return f"Analytics preferences for {self.user.username}"


class AnalyticsReport(models.Model):
    """Generated analytics reports"""
    REPORT_TYPES = [
        ('team_analysis', 'Team Analysis'),
        ('player_analysis', 'Player Analysis'),
        ('match_prediction', 'Match Prediction'),
        ('market_analysis', 'Market Analysis'),
        ('performance_summary', 'Performance Summary'),
        ('betting_insights', 'Betting Insights'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('json', 'JSON'),
        ('html', 'HTML'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('generating', 'Generating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analytics_reports')
    
    # Report details
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='pdf')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Date range
    date_from = models.DateField()
    date_to = models.DateField()
    
    # Content
    parameters = models.JSONField(default=dict, blank=True)  # Filters and parameters used
    content_data = models.JSONField(default=dict, blank=True)  # Generated data
    file_path = models.CharField(max_length=500, blank=True)  # Path to generated file
    
    # Performance metrics
    generation_time = models.FloatField(null=True, blank=True)  # Time taken to generate in seconds
    file_size = models.IntegerField(null=True, blank=True)  # File size in bytes
    
    # Metadata
    error_message = models.TextField(blank=True)
    download_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'analytics_reports'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['report_type', 'status']),
            models.Index(fields=['date_from', 'date_to']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"


class TeamAnalytics(models.Model):
    """Analytics data for teams"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='analytics')
    
    # Time period
    date_from = models.DateField()
    date_to = models.DateField()
    
    # Performance metrics
    matches_played = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    goals_for = models.IntegerField(default=0)
    goals_against = models.IntegerField(default=0)
    
    # Advanced metrics
    possession_avg = models.FloatField(null=True, blank=True)
    passing_accuracy = models.FloatField(null=True, blank=True)
    shots_per_match = models.FloatField(null=True, blank=True)
    shots_on_target_ratio = models.FloatField(null=True, blank=True)
    
    # Form and trends
    recent_form = models.JSONField(default=list, blank=True)  # Last 5-10 matches
    home_performance = models.JSONField(default=dict, blank=True)
    away_performance = models.JSONField(default=dict, blank=True)
    
    # Calculated fields
    win_rate = models.FloatField(null=True, blank=True)
    goal_difference = models.IntegerField(default=0)
    points_per_match = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'analytics_team_analytics'
        unique_together = [['team', 'date_from', 'date_to']]
        indexes = [
            models.Index(fields=['team', '-date_from']),
            models.Index(fields=['win_rate']),
            models.Index(fields=['points_per_match']),
        ]
    
    def __str__(self):
        return f"{self.team.name} analytics ({self.date_from} to {self.date_to})"


class PlayerAnalytics(models.Model):
    """Analytics data for players"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='analytics')
    
    # Time period
    date_from = models.DateField()
    date_to = models.DateField()
    
    # Basic statistics
    appearances = models.IntegerField(default=0)
    goals = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    yellow_cards = models.IntegerField(default=0)
    red_cards = models.IntegerField(default=0)
    
    # Performance metrics
    minutes_played = models.IntegerField(default=0)
    goals_per_90 = models.FloatField(null=True, blank=True)
    assists_per_90 = models.FloatField(null=True, blank=True)
    pass_completion_rate = models.FloatField(null=True, blank=True)
    
    # Advanced metrics
    expected_goals = models.FloatField(null=True, blank=True)
    expected_assists = models.FloatField(null=True, blank=True)
    progressive_passes = models.IntegerField(null=True, blank=True)
    key_passes = models.IntegerField(null=True, blank=True)
    
    # Market value and trends
    estimated_market_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    market_value_trend = models.CharField(max_length=20, choices=[
        ('rising', 'Rising'),
        ('stable', 'Stable'),
        ('declining', 'Declining'),
    ], null=True, blank=True)
    
    # Form analysis
    recent_performances = models.JSONField(default=list, blank=True)
    consistency_score = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'analytics_player_analytics'
        unique_together = [['player', 'date_from', 'date_to']]
        indexes = [
            models.Index(fields=['player', '-date_from']),
            models.Index(fields=['goals_per_90']),
            models.Index(fields=['estimated_market_value']),
        ]
    
    def __str__(self):
        return f"{self.player.name} analytics ({self.date_from} to {self.date_to})"


class MatchAnalytics(models.Model):
    """Detailed analytics for individual matches"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    match = models.OneToOneField(Match, on_delete=models.CASCADE, related_name='analytics')
    
    # Pre-match analytics
    home_team_form_score = models.FloatField(null=True, blank=True)
    away_team_form_score = models.FloatField(null=True, blank=True)
    head_to_head_stats = models.JSONField(default=dict, blank=True)
    
    # Match analytics
    possession_home = models.FloatField(null=True, blank=True)
    possession_away = models.FloatField(null=True, blank=True)
    shots_home = models.IntegerField(null=True, blank=True)
    shots_away = models.IntegerField(null=True, blank=True)
    shots_on_target_home = models.IntegerField(null=True, blank=True)
    shots_on_target_away = models.IntegerField(null=True, blank=True)
    
    # Advanced metrics
    expected_goals_home = models.FloatField(null=True, blank=True)
    expected_goals_away = models.FloatField(null=True, blank=True)
    passing_accuracy_home = models.FloatField(null=True, blank=True)
    passing_accuracy_away = models.FloatField(null=True, blank=True)
    
    # Post-match analysis
    performance_ratings = models.JSONField(default=dict, blank=True)
    key_moments = models.JSONField(default=list, blank=True)
    tactical_analysis = models.JSONField(default=dict, blank=True)
    
    # Prediction accuracy
    predicted_result = models.CharField(max_length=50, blank=True)
    actual_result = models.CharField(max_length=50, blank=True)
    prediction_accuracy = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'analytics_match_analytics'
        indexes = [
            models.Index(fields=['match']),
            models.Index(fields=['prediction_accuracy']),
        ]
    
    def __str__(self):
        return f"Analytics for {self.match}"


class AnalyticsDashboard(models.Model):
    """Customizable dashboard for users"""
    WIDGET_TYPES = [
        ('team_form', 'Team Form Chart'),
        ('player_stats', 'Player Statistics Table'),
        ('match_predictions', 'Match Predictions'),
        ('betting_odds', 'Betting Odds Tracker'),
        ('market_value', 'Market Value Trends'),
        ('league_standings', 'League Standings'),
        ('injury_alerts', 'Injury Risk Alerts'),
        ('sentiment_analysis', 'Fan Sentiment'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dashboards')
    
    # Dashboard configuration
    name = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    
    # Layout and widgets
    layout_config = models.JSONField(default=dict, blank=True)
    widgets = models.JSONField(default=list, blank=True)
    
    # Permissions
    shared_with_users = models.ManyToManyField(User, blank=True, related_name='shared_dashboards')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'analytics_dashboards'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', 'is_default']),
            models.Index(fields=['is_public']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"
