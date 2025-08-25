from django.db import models
from django.utils import timezone


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
        'core.Team', 
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
        'core.Season', 
        on_delete=models.CASCADE,
        help_text="Season for these statistics"
    )
    competition = models.ForeignKey(
        'core.Competition',
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
        'core.Team',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transfers_out',
        help_text="Team player transferred from"
    )
    to_team = models.ForeignKey(
        'core.Team',
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
