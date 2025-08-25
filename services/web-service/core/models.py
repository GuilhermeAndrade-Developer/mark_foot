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


class Player(models.Model):
    """
    Model for Football Players from TheSportsDB API
    """
    # IDs and identification
    external_id = models.CharField(max_length=50, unique=True, help_text="TheSportsDB Player ID")
    name = models.CharField(max_length=200, help_text="Player full name")
    short_name = models.CharField(max_length=100, blank=True, help_text="Player short name")
    
    # Team relationship
    team = models.ForeignKey(
        Team, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='players',
        help_text="Current team"
    )
    
    # Personal information
    nationality = models.CharField(max_length=100, blank=True, help_text="Player nationality")
    date_of_birth = models.DateField(null=True, blank=True, help_text="Player birth date")
    age = models.PositiveIntegerField(null=True, blank=True, help_text="Player current age")
    gender = models.CharField(
        max_length=10, 
        choices=[('Male', 'Male'), ('Female', 'Female')], 
        default='Male'
    )
    
    # Position and role
    position = models.CharField(max_length=50, blank=True, help_text="Player position")
    position_category = models.CharField(
        max_length=20,
        choices=[
            ('GK', 'Goalkeeper'),
            ('DF', 'Defender'),
            ('MF', 'Midfielder'),
            ('FW', 'Forward'),
            ('SUB', 'Substitute'),
            ('COACH', 'Coach/Manager'),
        ],
        blank=True,
        help_text="Position category"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('Active', 'Active'),
            ('Retired', 'Retired'),
            ('Injured', 'Injured'),
            ('Loan', 'On Loan'),
            ('Unknown', 'Unknown'),
        ],
        default='Active'
    )
    
    # Media
    photo_url = models.URLField(blank=True, help_text="Player photo thumbnail")
    cutout_url = models.URLField(blank=True, help_text="Player cutout image")
    
    # Additional info
    description = models.TextField(blank=True, help_text="Player description/biography")
    height = models.CharField(max_length=20, blank=True, help_text="Player height")
    weight = models.CharField(max_length=20, blank=True, help_text="Player weight")
    wage = models.CharField(max_length=50, blank=True, help_text="Player wage/salary")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_sync = models.DateTimeField(null=True, blank=True, help_text="Last API sync timestamp")
    
    class Meta:
        db_table = 'players'
        ordering = ['name']
        indexes = [
            models.Index(fields=['external_id']),
            models.Index(fields=['team']),
            models.Index(fields=['nationality']),
            models.Index(fields=['position_category']),
            models.Index(fields=['status']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        team_name = self.team.name if self.team else "No Team"
        return f"{self.name} ({team_name})"
    
    @property
    def age_calculated(self):
        """Calculate age from date of birth"""
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    
    def update_age(self):
        """Update age field based on date of birth"""
        if self.date_of_birth:
            self.age = self.age_calculated
            self.save(update_fields=['age'])


class PlayerStatistics(models.Model):
    """
    Model for Player Statistics from various sources
    """
    player = models.ForeignKey(
        Player, 
        on_delete=models.CASCADE, 
        related_name='statistics'
    )
    season = models.ForeignKey(
        Season, 
        on_delete=models.CASCADE,
        help_text="Season for these statistics"
    )
    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Competition for these statistics"
    )
    
    # Basic statistics
    appearances = models.PositiveIntegerField(default=0, help_text="Total appearances")
    minutes_played = models.PositiveIntegerField(default=0, help_text="Total minutes played")
    starts = models.PositiveIntegerField(default=0, help_text="Games started")
    substitutions_in = models.PositiveIntegerField(default=0, help_text="Times substituted in")
    substitutions_out = models.PositiveIntegerField(default=0, help_text="Times substituted out")
    
    # Scoring statistics
    goals = models.PositiveIntegerField(default=0, help_text="Goals scored")
    assists = models.PositiveIntegerField(default=0, help_text="Assists made")
    penalty_goals = models.PositiveIntegerField(default=0, help_text="Penalty goals")
    freekick_goals = models.PositiveIntegerField(default=0, help_text="Free kick goals")
    
    # Disciplinary
    yellow_cards = models.PositiveIntegerField(default=0, help_text="Yellow cards received")
    red_cards = models.PositiveIntegerField(default=0, help_text="Red cards received")
    
    # Goalkeeper specific (if applicable)
    clean_sheets = models.PositiveIntegerField(default=0, help_text="Clean sheets (GK)")
    saves = models.PositiveIntegerField(default=0, help_text="Saves made (GK)")
    goals_conceded = models.PositiveIntegerField(default=0, help_text="Goals conceded (GK)")
    
    # Performance metrics
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        null=True, 
        blank=True,
        help_text="Average performance rating"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'player_statistics'
        unique_together = ['player', 'season', 'competition']
        ordering = ['-season', 'player']
        indexes = [
            models.Index(fields=['player', 'season']),
            models.Index(fields=['season', 'competition']),
            models.Index(fields=['goals']),
            models.Index(fields=['assists']),
            models.Index(fields=['appearances']),
        ]
    
    def __str__(self):
        comp_name = self.competition.name if self.competition else "All Competitions"
        return f"{self.player.name} - {self.season} ({comp_name})"
    
    @property
    def goals_per_game(self):
        """Calculate goals per game ratio"""
        if self.appearances > 0:
            return round(self.goals / self.appearances, 2)
        return 0
    
    @property
    def assists_per_game(self):
        """Calculate assists per game ratio"""
        if self.appearances > 0:
            return round(self.assists / self.appearances, 2)
        return 0


class PlayerTransfer(models.Model):
    """
    Model for Player Transfer History
    """
    player = models.ForeignKey(
        Player, 
        on_delete=models.CASCADE, 
        related_name='transfers'
    )
    
    # Transfer details
    from_team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transfers_out',
        help_text="Team player transferred from"
    )
    to_team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transfers_in',
        help_text="Team player transferred to"
    )
    
    # Transfer info
    transfer_date = models.DateField(help_text="Date of transfer")
    transfer_type = models.CharField(
        max_length=20,
        choices=[
            ('Permanent', 'Permanent Transfer'),
            ('Loan', 'Loan'),
            ('Free', 'Free Transfer'),
            ('Contract', 'Contract Renewal'),
            ('Release', 'Contract Release'),
        ],
        default='Permanent'
    )
    
    # Financial
    transfer_fee = models.CharField(max_length=50, blank=True, help_text="Transfer fee amount")
    currency = models.CharField(max_length=10, blank=True, help_text="Currency of transfer fee")
    
    # Status
    is_confirmed = models.BooleanField(default=False, help_text="Transfer confirmed")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'player_transfers'
        ordering = ['-transfer_date']
        indexes = [
            models.Index(fields=['player', 'transfer_date']),
            models.Index(fields=['from_team']),
            models.Index(fields=['to_team']),
            models.Index(fields=['transfer_type']),
        ]
    
    def __str__(self):
        from_name = self.from_team.name if self.from_team else "Unknown"
        to_name = self.to_team.name if self.to_team else "Unknown"
        return f"{self.player.name}: {from_name} → {to_name} ({self.transfer_date})"
