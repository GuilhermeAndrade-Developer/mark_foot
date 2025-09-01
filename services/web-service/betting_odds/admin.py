from django.contrib import admin
from .models import BookmakerProvider, MatchOdds, OddsMovement, OddsAnalysis, MarketAlert

@admin.register(BookmakerProvider)
class BookmakerProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'reliability_score', 'rate_limit_per_minute', 'created_at']
    list_filter = ['is_active', 'api_key_required']
    search_fields = ['name']
    readonly_fields = ['created_at']

@admin.register(MatchOdds)
class MatchOddsAdmin(admin.ModelAdmin):
    list_display = ['match', 'bookmaker', 'home_win_odds', 'draw_odds', 'away_win_odds', 'last_updated']
    list_filter = ['bookmaker', 'timestamp']
    search_fields = ['match__home_team__name', 'match__away_team__name', 'bookmaker__name']
    readonly_fields = ['timestamp', 'last_updated', 'implied_probability_home', 'implied_probability_draw', 'implied_probability_away', 'bookmaker_margin']

@admin.register(OddsMovement)
class OddsMovementAdmin(admin.ModelAdmin):
    list_display = ['match_odds', 'market_type', 'old_odds', 'new_odds', 'movement_percentage', 'timestamp']
    list_filter = ['market_type', 'timestamp']
    search_fields = ['match_odds__match__home_team__name', 'match_odds__match__away_team__name']
    readonly_fields = ['movement_percentage', 'timestamp']

@admin.register(OddsAnalysis)
class OddsAnalysisAdmin(admin.ModelAdmin):
    list_display = ['match', 'value_bet_detected', 'value_bet_market', 'confidence_score', 'updated_at']
    list_filter = ['value_bet_detected', 'updated_at']
    search_fields = ['match__home_team__name', 'match__away_team__name']
    readonly_fields = ['updated_at']

@admin.register(MarketAlert)
class MarketAlertAdmin(admin.ModelAdmin):
    list_display = ['match', 'alert_type', 'market_type', 'is_active', 'created_at']
    list_filter = ['alert_type', 'market_type', 'is_active', 'created_at']
    search_fields = ['match__home_team__name', 'match__away_team__name']
    readonly_fields = ['created_at']
