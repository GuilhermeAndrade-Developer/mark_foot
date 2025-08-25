from django.contrib import admin
from .models import Area, Competition, Team, Season, Match, Standing, ApiSyncLog


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code', 'type', 'area', 'current_season_id']
    list_filter = ['type', 'plan', 'area', 'created_at']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at', 'updated_at', 'last_updated']
    raw_id_fields = ['area']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'short_name', 'tla', 'area', 'founded']
    list_filter = ['area', 'founded', 'created_at']
    search_fields = ['name', 'short_name', 'tla']
    readonly_fields = ['created_at', 'updated_at', 'last_updated']
    raw_id_fields = ['area']


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ['id', 'competition', 'start_date', 'end_date', 'current_matchday', 'available']
    list_filter = ['available', 'start_date', 'competition']
    search_fields = ['competition__name', 'competition__code']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['competition', 'winner_team']


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['id', 'home_team', 'away_team', 'utc_date', 'status', 'home_team_score', 'away_team_score', 'competition']
    list_filter = ['status', 'competition', 'utc_date', 'winner']
    search_fields = ['home_team__name', 'away_team__name', 'competition__name']
    readonly_fields = ['created_at', 'updated_at', 'last_updated']
    raw_id_fields = ['competition', 'season', 'home_team', 'away_team']
    date_hierarchy = 'utc_date'


@admin.register(Standing)
class StandingAdmin(admin.ModelAdmin):
    list_display = ['team', 'competition', 'position', 'points', 'played_games', 'won', 'draw', 'lost', 'snapshot_date']
    list_filter = ['competition', 'type', 'snapshot_date']
    search_fields = ['team__name', 'competition__name']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['competition', 'season', 'team']
    ordering = ['competition', 'position']


@admin.register(ApiSyncLog)
class ApiSyncLogAdmin(admin.ModelAdmin):
    list_display = ['endpoint', 'sync_date', 'http_status', 'records_processed', 'records_inserted', 'records_updated', 'records_failed']
    list_filter = ['http_status', 'sync_date', 'endpoint']
    search_fields = ['endpoint', 'error_message']
    readonly_fields = ['created_at']
    date_hierarchy = 'sync_date'
    
    def has_add_permission(self, request):
        return False  # Prevent manual creation
    
    def has_change_permission(self, request, obj=None):
        return False  # Prevent editing
