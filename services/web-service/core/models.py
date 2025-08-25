from django.db import models
from django.utils import timezone


class Area(models.Model):
    """Model for countries/regions"""
    id = models.BigIntegerField(primary_key=True)  # ID from API
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, null=True, blank=True)
    flag_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'areas'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Competition(models.Model):
    """Model for football competitions"""
    
    COMPETITION_TYPES = [
        ('LEAGUE', 'League'),
        ('CUP', 'Cup'),
        ('TOURNAMENT', 'Tournament'),
    ]
    
    PLAN_TYPES = [
        ('TIER_ONE', 'Tier One'),
        ('TIER_TWO', 'Tier Two'),
        ('TIER_THREE', 'Tier Three'),
        ('TIER_FOUR', 'Tier Four'),
    ]
    
    id = models.BigIntegerField(primary_key=True)  # ID from API
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    type = models.CharField(max_length=20, choices=COMPETITION_TYPES)
    emblem_url = models.URLField(null=True, blank=True)
    plan = models.CharField(max_length=20, choices=PLAN_TYPES, null=True, blank=True)
    current_season_id = models.BigIntegerField(null=True, blank=True)
    number_of_available_seasons = models.IntegerField(default=0)
    last_updated = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'competitions'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['area']),
            models.Index(fields=['type']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Team(models.Model):
    """Model for football teams"""
    id = models.BigIntegerField(primary_key=True)  # ID from API
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=50, null=True, blank=True)
    tla = models.CharField(max_length=10, null=True, blank=True)  # Three Letter Abbreviation
    crest_url = models.URLField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    founded = models.IntegerField(null=True, blank=True)
    club_colors = models.CharField(max_length=100, null=True, blank=True)
    venue = models.CharField(max_length=100, null=True, blank=True)
    last_updated = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'teams'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['short_name']),
            models.Index(fields=['tla']),
            models.Index(fields=['area']),
        ]

    def __str__(self):
        return self.name


class Season(models.Model):
    """Model for competition seasons"""
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    current_matchday = models.IntegerField(default=1)
    winner_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'seasons'
        indexes = [
            models.Index(fields=['competition']),
            models.Index(fields=['start_date', 'end_date']),
        ]
        unique_together = ['competition', 'start_date']

    def __str__(self):
        return f"{self.competition.name} {self.start_date.year}/{self.end_date.year}"


class Match(models.Model):
    """Model for football matches"""
    
    MATCH_STATUS = [
        ('SCHEDULED', 'Scheduled'),
        ('LIVE', 'Live'),
        ('IN_PLAY', 'In Play'),
        ('PAUSED', 'Paused'),
        ('FINISHED', 'Finished'),
        ('POSTPONED', 'Postponed'),
        ('SUSPENDED', 'Suspended'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    WINNER_CHOICES = [
        ('HOME_TEAM', 'Home Team'),
        ('AWAY_TEAM', 'Away Team'),
        ('DRAW', 'Draw'),
    ]
    
    DURATION_CHOICES = [
        ('REGULAR', 'Regular'),
        ('EXTRA_TIME', 'Extra Time'),
        ('PENALTY_SHOOTOUT', 'Penalty Shootout'),
    ]
    
    id = models.BigIntegerField(primary_key=True)  # ID from API
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_matches')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_matches')
    utc_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=MATCH_STATUS)
    stage = models.CharField(max_length=50, null=True, blank=True)
    group_name = models.CharField(max_length=10, null=True, blank=True)
    matchday = models.IntegerField(null=True, blank=True)
    last_updated = models.DateTimeField(null=True, blank=True)
    
    # Result fields
    home_team_score = models.IntegerField(null=True, blank=True)
    away_team_score = models.IntegerField(null=True, blank=True)
    winner = models.CharField(max_length=20, choices=WINNER_CHOICES, null=True, blank=True)
    duration = models.CharField(max_length=20, choices=DURATION_CHOICES, default='REGULAR')
    
    # Additional fields for future use
    attendance = models.IntegerField(null=True, blank=True)
    referee_name = models.CharField(max_length=100, null=True, blank=True)
    venue = models.CharField(max_length=100, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'matches'
        indexes = [
            models.Index(fields=['competition', 'season']),
            models.Index(fields=['home_team', 'away_team']),
            models.Index(fields=['utc_date']),
            models.Index(fields=['status']),
            models.Index(fields=['matchday']),
        ]

    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name} - {self.utc_date.strftime('%Y-%m-%d')}"


class Standing(models.Model):
    """Model for league standings"""
    
    STANDING_TYPES = [
        ('TOTAL', 'Total'),
        ('HOME', 'Home'),
        ('AWAY', 'Away'),
    ]
    
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    stage = models.CharField(max_length=50, default='REGULAR_SEASON')
    type = models.CharField(max_length=10, choices=STANDING_TYPES, default='TOTAL')
    group_name = models.CharField(max_length=10, null=True, blank=True)
    
    # Statistics
    position = models.IntegerField()
    played_games = models.IntegerField(default=0)
    form = models.CharField(max_length=10, null=True, blank=True)  # Last 5 games: WWDLL
    won = models.IntegerField(default=0)
    draw = models.IntegerField(default=0)
    lost = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    goals_for = models.IntegerField(default=0)
    goals_against = models.IntegerField(default=0)
    goal_difference = models.IntegerField(default=0)
    
    snapshot_date = models.DateField()  # Date of this snapshot
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'standings'
        indexes = [
            models.Index(fields=['competition', 'season']),
            models.Index(fields=['position']),
            models.Index(fields=['-points']),  # Descending order
            models.Index(fields=['snapshot_date']),
        ]
        unique_together = ['competition', 'season', 'team', 'type', 'stage', 'snapshot_date']

    def __str__(self):
        return f"{self.team.name} - Position {self.position} ({self.competition.name})"


class ApiSyncLog(models.Model):
    """Model for API synchronization logs"""
    endpoint = models.CharField(max_length=255)
    http_status = models.IntegerField(null=True, blank=True)
    records_processed = models.IntegerField(default=0)
    records_inserted = models.IntegerField(default=0)
    records_updated = models.IntegerField(default=0)
    records_failed = models.IntegerField(default=0)
    execution_time_ms = models.IntegerField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    request_params = models.JSONField(null=True, blank=True)
    response_data = models.JSONField(null=True, blank=True)  # Sample of response
    sync_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_sync_logs'
        indexes = [
            models.Index(fields=['endpoint']),
            models.Index(fields=['sync_date']),
            models.Index(fields=['http_status']),
        ]

    def __str__(self):
        return f"{self.endpoint} - {self.sync_date.strftime('%Y-%m-%d %H:%M:%S')}"
