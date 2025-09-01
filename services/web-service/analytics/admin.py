from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Avg
import json

from .models import (
    UserAnalyticsPreference, AnalyticsReport, TeamAnalytics, 
    PlayerAnalytics, MatchAnalytics, AnalyticsDashboard
)


@admin.register(UserAnalyticsPreference)
class UserAnalyticsPreferenceAdmin(admin.ModelAdmin):
    """Admin interface for user analytics preferences"""
    list_display = [
        'user', 'report_frequency', 'auto_generate_reports', 
        'email_reports', 'whatsapp_reports', 'favorite_teams_count'
    ]
    list_filter = [
        'report_frequency', 'auto_generate_reports', 
        'email_reports', 'whatsapp_reports', 'created_at'
    ]
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'widgets_display']
    
    fieldsets = (
        ('User Info', {
            'fields': ('user',)
        }),
        ('Report Preferences', {
            'fields': ('report_frequency', 'auto_generate_reports', 'email_reports', 'whatsapp_reports')
        }),
        ('Favorites', {
            'fields': ('favorite_teams', 'favorite_players', 'favorite_competitions')
        }),
        ('Dashboard Configuration', {
            'fields': ('enabled_widgets', 'widgets_display', 'widget_layout'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    filter_horizontal = ['favorite_teams', 'favorite_players', 'favorite_competitions']
    
    def favorite_teams_count(self, obj):
        return obj.favorite_teams.count()
    favorite_teams_count.short_description = 'Favorite Teams'
    
    def widgets_display(self, obj):
        if obj.enabled_widgets:
            widgets_html = '<ul>'
            for widget in obj.enabled_widgets:
                widgets_html += f'<li>{widget}</li>'
            widgets_html += '</ul>'
            return format_html(widgets_html)
        return '-'
    widgets_display.short_description = 'Enabled Widgets'


@admin.register(AnalyticsReport)
class AnalyticsReportAdmin(admin.ModelAdmin):
    """Admin interface for analytics reports"""
    list_display = [
        'title', 'user', 'report_type', 'format', 'status', 
        'generation_time_display', 'download_count', 'created_at'
    ]
    list_filter = [
        'report_type', 'format', 'status', 'created_at', 
        'date_from', 'date_to'
    ]
    search_fields = ['title', 'user__username', 'user__email']
    readonly_fields = [
        'created_at', 'updated_at', 'generation_time', 
        'file_size', 'download_count', 'parameters_display', 'content_display'
    ]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Report Info', {
            'fields': ('user', 'title', 'report_type', 'format', 'status')
        }),
        ('Date Range', {
            'fields': ('date_from', 'date_to')
        }),
        ('Configuration', {
            'fields': ('parameters_display', 'file_path')
        }),
        ('Performance', {
            'fields': ('generation_time', 'file_size', 'download_count'),
            'classes': ('collapse',)
        }),
        ('Content Preview', {
            'fields': ('content_display',),
            'classes': ('collapse',)
        }),
        ('Error Info', {
            'fields': ('error_message',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['regenerate_reports', 'mark_as_failed']
    
    def generation_time_display(self, obj):
        if obj.generation_time:
            return f"{obj.generation_time:.2f}s"
        return '-'
    generation_time_display.short_description = 'Generation Time'
    
    def parameters_display(self, obj):
        if obj.parameters:
            formatted_json = json.dumps(obj.parameters, indent=2)
            return format_html('<pre>{}</pre>', formatted_json)
        return '-'
    parameters_display.short_description = 'Parameters'
    
    def content_display(self, obj):
        if obj.content_data:
            # Limit display to avoid huge content
            limited_content = str(obj.content_data)[:500]
            if len(str(obj.content_data)) > 500:
                limited_content += "... (truncated)"
            return format_html('<pre>{}</pre>', limited_content)
        return '-'
    content_display.short_description = 'Content Preview'
    
    def regenerate_reports(self, request, queryset):
        updated = queryset.update(status='pending')
        self.message_user(request, f'{updated} reports marked for regeneration.')
    regenerate_reports.short_description = "Mark selected reports for regeneration"
    
    def mark_as_failed(self, request, queryset):
        updated = queryset.update(status='failed')
        self.message_user(request, f'{updated} reports marked as failed.')
    mark_as_failed.short_description = "Mark selected reports as failed"


@admin.register(TeamAnalytics)
class TeamAnalyticsAdmin(admin.ModelAdmin):
    """Admin interface for team analytics"""
    list_display = [
        'team', 'date_range_display', 'matches_played', 'win_rate_display',
        'goal_difference', 'points_per_match_display', 'updated_at'
    ]
    list_filter = [
        'date_from', 'date_to', 'updated_at', 'team__name'
    ]
    search_fields = ['team__name']
    readonly_fields = [
        'created_at', 'updated_at', 'win_rate', 'goal_difference', 
        'form_display', 'performance_display'
    ]
    
    fieldsets = (
        ('Team & Period', {
            'fields': ('team', 'date_from', 'date_to')
        }),
        ('Match Results', {
            'fields': ('matches_played', 'wins', 'draws', 'losses', 'goals_for', 'goals_against')
        }),
        ('Calculated Metrics', {
            'fields': ('win_rate', 'goal_difference', 'points_per_match')
        }),
        ('Performance Data', {
            'fields': ('possession_avg', 'passing_accuracy', 'shots_per_match', 'shots_on_target_ratio')
        }),
        ('Form Analysis', {
            'fields': ('form_display', 'performance_display'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def date_range_display(self, obj):
        return f"{obj.date_from} to {obj.date_to}"
    date_range_display.short_description = 'Date Range'
    
    def win_rate_display(self, obj):
        if obj.win_rate:
            return f"{obj.win_rate:.1f}%"
        return '-'
    win_rate_display.short_description = 'Win Rate'
    
    def points_per_match_display(self, obj):
        if obj.points_per_match:
            return f"{obj.points_per_match:.2f}"
        return '-'
    points_per_match_display.short_description = 'PPM'
    
    def form_display(self, obj):
        if obj.recent_form:
            form_html = '<span style="font-family: monospace;">'
            for result in obj.recent_form:
                color = {'W': 'green', 'D': 'orange', 'L': 'red'}.get(result, 'black')
                form_html += f'<span style="color: {color}; font-weight: bold;">{result}</span> '
            form_html += '</span>'
            return format_html(form_html)
        return '-'
    form_display.short_description = 'Recent Form'
    
    def performance_display(self, obj):
        performance_data = []
        if obj.home_performance:
            performance_data.append(f"Home: {obj.home_performance}")
        if obj.away_performance:
            performance_data.append(f"Away: {obj.away_performance}")
        
        if performance_data:
            return format_html('<br>'.join(performance_data))
        return '-'
    performance_display.short_description = 'Home/Away Performance'


@admin.register(PlayerAnalytics)
class PlayerAnalyticsAdmin(admin.ModelAdmin):
    """Admin interface for player analytics"""
    list_display = [
        'player', 'date_range_display', 'appearances', 'goals_per_90_display',
        'assists_per_90_display', 'market_value_display', 'market_value_trend'
    ]
    list_filter = [
        'date_from', 'date_to', 'market_value_trend', 'updated_at'
    ]
    search_fields = ['player__name', 'player__team__name']
    readonly_fields = [
        'created_at', 'updated_at', 'goals_per_90', 'assists_per_90',
        'performances_display'
    ]
    
    fieldsets = (
        ('Player & Period', {
            'fields': ('player', 'date_from', 'date_to')
        }),
        ('Basic Statistics', {
            'fields': ('appearances', 'goals', 'assists', 'yellow_cards', 'red_cards', 'minutes_played')
        }),
        ('Performance Metrics', {
            'fields': ('goals_per_90', 'assists_per_90', 'pass_completion_rate')
        }),
        ('Advanced Metrics', {
            'fields': ('expected_goals', 'expected_assists', 'progressive_passes', 'key_passes')
        }),
        ('Market Analysis', {
            'fields': ('estimated_market_value', 'market_value_trend')
        }),
        ('Form Analysis', {
            'fields': ('performances_display', 'consistency_score'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def date_range_display(self, obj):
        return f"{obj.date_from} to {obj.date_to}"
    date_range_display.short_description = 'Date Range'
    
    def goals_per_90_display(self, obj):
        if obj.goals_per_90:
            return f"{obj.goals_per_90:.2f}"
        return '-'
    goals_per_90_display.short_description = 'Goals/90'
    
    def assists_per_90_display(self, obj):
        if obj.assists_per_90:
            return f"{obj.assists_per_90:.2f}"
        return '-'
    assists_per_90_display.short_description = 'Assists/90'
    
    def market_value_display(self, obj):
        if obj.estimated_market_value:
            return f"€{obj.estimated_market_value:,.0f}"
        return '-'
    market_value_display.short_description = 'Market Value'
    
    def performances_display(self, obj):
        if obj.recent_performances:
            limited_performances = obj.recent_performances[:5]  # Show last 5
            performances_html = '<ul>'
            for perf in limited_performances:
                performances_html += f'<li>{perf}</li>'
            performances_html += '</ul>'
            return format_html(performances_html)
        return '-'
    performances_display.short_description = 'Recent Performances'


@admin.register(MatchAnalytics)
class MatchAnalyticsAdmin(admin.ModelAdmin):
    """Admin interface for match analytics"""
    list_display = [
        'match', 'possession_comparison', 'shots_comparison', 
        'expected_goals_comparison', 'prediction_accuracy_display'
    ]
    list_filter = ['match__status', 'match__competition', 'updated_at']
    search_fields = ['match__home_team__name', 'match__away_team__name']
    readonly_fields = [
        'created_at', 'updated_at', 'stats_display', 
        'analysis_display', 'moments_display'
    ]
    
    fieldsets = (
        ('Match Info', {
            'fields': ('match',)
        }),
        ('Pre-match Analysis', {
            'fields': ('home_team_form_score', 'away_team_form_score', 'stats_display')
        }),
        ('Match Statistics', {
            'fields': (
                'possession_home', 'possession_away',
                'shots_home', 'shots_away',
                'shots_on_target_home', 'shots_on_target_away'
            )
        }),
        ('Advanced Metrics', {
            'fields': (
                'expected_goals_home', 'expected_goals_away',
                'passing_accuracy_home', 'passing_accuracy_away'
            )
        }),
        ('Post-match Analysis', {
            'fields': ('analysis_display', 'moments_display'),
            'classes': ('collapse',)
        }),
        ('Prediction Accuracy', {
            'fields': ('predicted_result', 'actual_result', 'prediction_accuracy')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def possession_comparison(self, obj):
        if obj.possession_home and obj.possession_away:
            return f"{obj.possession_home:.1f}% - {obj.possession_away:.1f}%"
        return '-'
    possession_comparison.short_description = 'Possession (H-A)'
    
    def shots_comparison(self, obj):
        if obj.shots_home and obj.shots_away:
            return f"{obj.shots_home} - {obj.shots_away}"
        return '-'
    shots_comparison.short_description = 'Shots (H-A)'
    
    def expected_goals_comparison(self, obj):
        if obj.expected_goals_home and obj.expected_goals_away:
            return f"{obj.expected_goals_home:.2f} - {obj.expected_goals_away:.2f}"
        return '-'
    expected_goals_comparison.short_description = 'xG (H-A)'
    
    def prediction_accuracy_display(self, obj):
        if obj.prediction_accuracy:
            return f"{obj.prediction_accuracy:.1f}%"
        return '-'
    prediction_accuracy_display.short_description = 'Prediction Accuracy'
    
    def stats_display(self, obj):
        if obj.head_to_head_stats:
            formatted_json = json.dumps(obj.head_to_head_stats, indent=2)
            return format_html('<pre>{}</pre>', formatted_json)
        return '-'
    stats_display.short_description = 'H2H Statistics'
    
    def analysis_display(self, obj):
        if obj.tactical_analysis:
            formatted_json = json.dumps(obj.tactical_analysis, indent=2)
            return format_html('<pre>{}</pre>', formatted_json)
        return '-'
    analysis_display.short_description = 'Tactical Analysis'
    
    def moments_display(self, obj):
        if obj.key_moments:
            moments_html = '<ul>'
            for moment in obj.key_moments:
                moments_html += f'<li>{moment}</li>'
            moments_html += '</ul>'
            return format_html(moments_html)
        return '-'
    moments_display.short_description = 'Key Moments'


@admin.register(AnalyticsDashboard)
class AnalyticsDashboardAdmin(admin.ModelAdmin):
    """Admin interface for analytics dashboards"""
    list_display = [
        'name', 'user', 'is_default', 'is_public', 
        'widgets_count', 'shared_count', 'updated_at'
    ]
    list_filter = ['is_default', 'is_public', 'created_at', 'updated_at']
    search_fields = ['name', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'layout_display', 'widgets_display']
    
    fieldsets = (
        ('Dashboard Info', {
            'fields': ('user', 'name', 'is_default', 'is_public')
        }),
        ('Configuration', {
            'fields': ('layout_display', 'widgets_display')
        }),
        ('Sharing', {
            'fields': ('shared_with_users',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    filter_horizontal = ['shared_with_users']
    
    def widgets_count(self, obj):
        if obj.widgets:
            return len(obj.widgets)
        return 0
    widgets_count.short_description = 'Widgets Count'
    
    def shared_count(self, obj):
        return obj.shared_with_users.count()
    shared_count.short_description = 'Shared With'
    
    def layout_display(self, obj):
        if obj.layout_config:
            formatted_json = json.dumps(obj.layout_config, indent=2)
            return format_html('<pre>{}</pre>', formatted_json)
        return '-'
    layout_display.short_description = 'Layout Configuration'
    
    def widgets_display(self, obj):
        if obj.widgets:
            widgets_html = '<ul>'
            for widget in obj.widgets:
                widgets_html += f'<li>{widget}</li>'
            widgets_html += '</ul>'
            return format_html(widgets_html)
        return '-'
    widgets_display.short_description = 'Dashboard Widgets'
