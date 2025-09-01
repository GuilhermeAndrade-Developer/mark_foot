from django.db import models
from core.models import Match, Team
from django.utils import timezone

class BookmakerProvider(models.Model):
    name = models.CharField(max_length=100, unique=True)
    api_endpoint = models.URLField()
    api_key_required = models.BooleanField(default=True)
    rate_limit_per_minute = models.IntegerField(default=60)
    is_active = models.BooleanField(default=True)
    reliability_score = models.FloatField(default=0.8)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({'Active' if self.is_active else 'Inactive'})"

    class Meta:
        verbose_name = "Bookmaker Provider"
        verbose_name_plural = "Bookmaker Providers"

class MatchOdds(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='odds')
    bookmaker = models.ForeignKey(BookmakerProvider, on_delete=models.CASCADE)
    home_win_odds = models.FloatField()
    draw_odds = models.FloatField()
    away_win_odds = models.FloatField()
    total_goals_over_2_5 = models.FloatField(null=True, blank=True)
    total_goals_under_2_5 = models.FloatField(null=True, blank=True)
    both_teams_score_yes = models.FloatField(null=True, blank=True)
    both_teams_score_no = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.match} - {self.bookmaker.name}"

    @property
    def implied_probability_home(self):
        return 1 / self.home_win_odds if self.home_win_odds > 0 else 0

    @property
    def implied_probability_draw(self):
        return 1 / self.draw_odds if self.draw_odds > 0 else 0

    @property
    def implied_probability_away(self):
        return 1 / self.away_win_odds if self.away_win_odds > 0 else 0

    @property
    def bookmaker_margin(self):
        total = self.implied_probability_home + self.implied_probability_draw + self.implied_probability_away
        return (total - 1) * 100 if total > 1 else 0

    class Meta:
        verbose_name = "Match Odds"
        verbose_name_plural = "Match Odds"
        unique_together = ['match', 'bookmaker']

class OddsMovement(models.Model):
    MARKET_TYPES = [
        ('home_win', 'Home Win'),
        ('draw', 'Draw'),
        ('away_win', 'Away Win'),
        ('over_2_5', 'Over 2.5 Goals'),
        ('under_2_5', 'Under 2.5 Goals'),
        ('btts_yes', 'Both Teams Score Yes'),
        ('btts_no', 'Both Teams Score No'),
    ]
    
    match_odds = models.ForeignKey(MatchOdds, on_delete=models.CASCADE, related_name='movements')
    market_type = models.CharField(max_length=50, choices=MARKET_TYPES)
    old_odds = models.FloatField()
    new_odds = models.FloatField()
    movement_percentage = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.match_odds.match} - {self.market_type}: {self.old_odds} → {self.new_odds}"

    def save(self, *args, **kwargs):
        if self.old_odds and self.new_odds:
            self.movement_percentage = ((self.new_odds - self.old_odds) / self.old_odds) * 100
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Odds Movement"
        verbose_name_plural = "Odds Movements"
        ordering = ['-timestamp']
    
class OddsAnalysis(models.Model):
    match = models.OneToOneField(Match, on_delete=models.CASCADE, related_name='odds_analysis')
    average_home_odds = models.FloatField()
    average_draw_odds = models.FloatField()
    average_away_odds = models.FloatField()
    best_home_odds = models.FloatField(null=True, blank=True)
    best_draw_odds = models.FloatField(null=True, blank=True)
    best_away_odds = models.FloatField(null=True, blank=True)
    value_bet_detected = models.BooleanField(default=False)
    value_bet_market = models.CharField(max_length=50, null=True, blank=True)
    confidence_score = models.FloatField(default=0.0)
    analysis_summary = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Analysis for {self.match}"

    class Meta:
        verbose_name = "Odds Analysis"
        verbose_name_plural = "Odds Analyses"

class MarketAlert(models.Model):
    ALERT_TYPES = [
        ('odds_drop', 'Significant Odds Drop'),
        ('odds_rise', 'Significant Odds Rise'),
        ('value_bet', 'Value Bet Detected'),
        ('arbitrage', 'Arbitrage Opportunity'),
        ('steam_move', 'Steam Movement'),
    ]
    
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='market_alerts')
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPES)
    market_type = models.CharField(max_length=50)
    description = models.TextField()
    old_odds = models.FloatField(null=True, blank=True)
    new_odds = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.match}"

    class Meta:
        verbose_name = "Market Alert"
        verbose_name_plural = "Market Alerts"
        ordering = ['-created_at']
