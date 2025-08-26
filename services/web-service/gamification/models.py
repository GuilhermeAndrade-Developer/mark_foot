"""
Models for the gamification system - adapted to existing database schema.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import Team, Match, Competition, Season


class UserProfile(models.Model):
    """Extended user profile matching existing schema"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_points = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    experience_points = models.PositiveIntegerField(default=0)
    prediction_streak = models.PositiveIntegerField(default=0)
    login_streak = models.PositiveIntegerField(default=0)
    last_login_date = models.DateField(null=True, blank=True)
    is_public_profile = models.BooleanField(default=True)
    allow_friend_requests = models.BooleanField(default=True)
    
    # Foreign keys
    favorite_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    favorite_competition = models.ForeignKey(Competition, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        indexes = [
            models.Index(fields=['total_points']),
            models.Index(fields=['level']),
            models.Index(fields=['prediction_streak']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - Level {self.level}"


class Badge(models.Model):
    """Achievement badges matching existing schema"""
    
    BADGE_TYPES = [
        ('prediction', 'Predição'),
        ('fantasy', 'Fantasy'),
        ('social', 'Social'),
        ('streak', 'Sequência'),
        ('special', 'Especial'),
    ]
    
    RARITY_CHOICES = [
        ('common', 'Comum'),
        ('uncommon', 'Incomum'),
        ('rare', 'Raro'),
        ('epic', 'Épico'),
        ('legendary', 'Lendário'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    badge_type = models.CharField(max_length=20, choices=BADGE_TYPES)
    rarity = models.CharField(max_length=20, choices=RARITY_CHOICES, default='common')
    icon_url = models.CharField(max_length=200)
    points_reward = models.PositiveIntegerField(default=0)
    
    # Requirements (nullable for flexibility)
    required_predictions = models.PositiveIntegerField(null=True, blank=True)
    required_streak = models.PositiveIntegerField(null=True, blank=True)
    required_fantasy_points = models.PositiveIntegerField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'badges'
    
    def __str__(self):
        return self.name


class UserBadge(models.Model):
    """User earned badges matching existing schema"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    is_showcased = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'user_badges'
        unique_together = ['user', 'badge']
    
    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"


class PredictionGame(models.Model):
    """Prediction games/rounds matching existing schema"""
    
    GAME_TYPES = [
        ('match_result', 'Resultado da Partida'),
        ('exact_score', 'Placar Exato'),
        ('weekly_round', 'Rodada Semanal'),
        ('tournament', 'Torneio'),
    ]
    
    STATUS_CHOICES = [
        ('upcoming', 'Próximo'),
        ('active', 'Ativo'),
        ('closed', 'Fechado'),
        ('resolved', 'Resolvido'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    game_type = models.CharField(max_length=20, choices=GAME_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    
    # Points and rewards
    entry_fee_points = models.PositiveIntegerField(default=0)
    reward_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=2.0)
    
    # Related objects
    match = models.ForeignKey(Match, on_delete=models.CASCADE, null=True, blank=True)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, null=True, blank=True)
    
    # Dates
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'prediction_games'
    
    def __str__(self):
        return self.name


class Prediction(models.Model):
    """User predictions matching existing schema"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(PredictionGame, on_delete=models.CASCADE)
    
    # Prediction data stored as JSON for flexibility
    prediction_data = models.JSONField()
    
    # Results
    points_earned = models.IntegerField(default=0)
    is_correct = models.BooleanField(null=True, blank=True)  # Null until resolved
    
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'predictions'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['game']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.game.name}"


class FantasyLeague(models.Model):
    """Fantasy leagues matching existing schema"""
    
    LEAGUE_TYPES = [
        ('public', 'Pública'),
        ('private', 'Privada'),
        ('premium', 'Premium'),
    ]
    
    # Using CharField for ID to match existing schema
    id = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    league_type = models.CharField(max_length=20, choices=LEAGUE_TYPES)
    
    max_participants = models.PositiveIntegerField(default=20)
    entry_fee_points = models.PositiveIntegerField(default=0)
    prize_pool = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    join_code = models.CharField(max_length=8, unique=True)
    
    # Foreign keys
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    
    class Meta:
        db_table = 'fantasy_leagues'
        indexes = [
            models.Index(fields=['league_type']),
            models.Index(fields=['competition']),
            models.Index(fields=['created_by']),
            models.Index(fields=['season']),
        ]
    
    def __str__(self):
        return self.name


class FantasyTeam(models.Model):
    """Fantasy teams matching existing schema"""
    
    FORMATION_CHOICES = [
        ('4-4-2', '4-4-2'),
        ('4-3-3', '4-3-3'),
        ('3-5-2', '3-5-2'),
        ('4-5-1', '4-5-1'),
        ('5-3-2', '5-3-2'),
    ]
    
    id = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=200)
    formation = models.CharField(max_length=10, choices=FORMATION_CHOICES, default='4-4-2')
    
    # Points and budget
    total_points = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    remaining_budget = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    
    # Foreign keys
    league = models.ForeignKey(FantasyLeague, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Player selections through M2M relationships
    goalkeepers = models.ManyToManyField('core.Player', related_name='fantasy_teams_gk', blank=True)
    defenders = models.ManyToManyField('core.Player', related_name='fantasy_teams_def', blank=True)
    midfielders = models.ManyToManyField('core.Player', related_name='fantasy_teams_mid', blank=True)
    forwards = models.ManyToManyField('core.Player', related_name='fantasy_teams_fwd', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fantasy_teams'
    
    def __str__(self):
        return f"{self.name} ({self.owner.username})"


class PointTransaction(models.Model):
    """Points transactions matching existing schema"""
    
    TRANSACTION_TYPES = [
        ('earned', 'Ganho'),
        ('spent', 'Gasto'),
        ('bonus', 'Bônus'),
        ('penalty', 'Penalidade'),
        ('refund', 'Reembolso'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.IntegerField()  # Can be negative
    description = models.CharField(max_length=255)
    
    # Optional reference to source object
    source_type = models.CharField(max_length=50, null=True, blank=True)
    source_id = models.PositiveIntegerField(null=True, blank=True)
    
    # Balance tracking
    balance_before = models.PositiveIntegerField()
    balance_after = models.PositiveIntegerField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'point_transactions'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['transaction_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username}: {self.amount} pts - {self.description}"


class Leaderboard(models.Model):
    """Leaderboards matching existing schema"""
    
    LEADERBOARD_TYPES = [
        ('overall_points', 'Pontuação Geral'),
        ('prediction_accuracy', 'Precisão de Predições'),
        ('fantasy_league', 'Liga Fantasy'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensal'),
    ]
    
    name = models.CharField(max_length=200)
    leaderboard_type = models.CharField(max_length=30, choices=LEADERBOARD_TYPES)
    description = models.TextField(blank=True)
    
    # Optional filters
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, null=True, blank=True)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, null=True, blank=True)
    
    # Period
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'leaderboards'
    
    def __str__(self):
        return self.name


class LeaderboardEntry(models.Model):
    """Leaderboard entries matching existing schema"""
    leaderboard = models.ForeignKey(Leaderboard, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    rank = models.PositiveIntegerField()
    score = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Additional data for specific leaderboard types
    additional_data = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'leaderboard_entries'
        unique_together = ['leaderboard', 'user']
        indexes = [
            models.Index(fields=['leaderboard', 'rank']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.leaderboard.name} - {self.user.username} (#{self.rank})"


class Challenge(models.Model):
    """Weekly/monthly challenges matching existing schema"""
    
    CHALLENGE_TYPES = [
        ('prediction', 'Predição'),
        ('fantasy', 'Fantasy'),
        ('streak', 'Sequência'),
        ('social', 'Social'),
    ]
    
    STATUS_CHOICES = [
        ('upcoming', 'Próximo'),
        ('active', 'Ativo'),
        ('completed', 'Concluído'),
        ('cancelled', 'Cancelado'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    challenge_type = models.CharField(max_length=20, choices=CHALLENGE_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    
    # Requirements and rewards
    requirements = models.JSONField(default=dict)
    points_reward = models.PositiveIntegerField(default=0)
    badge_reward = models.ForeignKey(Badge, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Participation limits
    max_participants = models.PositiveIntegerField(default=1000)
    current_participants = models.PositiveIntegerField(default=0)
    
    # Dates
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'challenges'
    
    def __str__(self):
        return self.title
    
    @property
    def is_active(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date and self.status == 'active'


class UserChallenge(models.Model):
    """User participation in challenges matching existing schema"""
    
    STATUS_CHOICES = [
        ('participating', 'Participando'),
        ('completed', 'Completo'),
        ('failed', 'Falhou'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='participating')
    
    # Progress tracking
    progress_data = models.JSONField(default=dict)
    completion_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Results
    points_earned = models.PositiveIntegerField(default=0)
    
    joined_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'user_challenges'
        unique_together = ['user', 'challenge']
    
    def __str__(self):
        return f"{self.user.username} - {self.challenge.title}"
