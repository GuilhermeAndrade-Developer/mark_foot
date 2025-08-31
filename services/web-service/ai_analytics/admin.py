from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
import json

from .models import (
    MatchPrediction, PlayerRecommendation, SentimentAnalysis,
    InjuryPrediction, MarketValuePrediction, PlayStyleCluster,
    AnomalyDetection, TransferSimulation
)


@admin.register(MatchPrediction)
class MatchPredictionAdmin(admin.ModelAdmin):
    list_display = [
        'match', 'prediction_type', 'predicted_value', 
        'confidence_score', 'prediction_accuracy', 'model_version', 'created_at'
    ]
    list_filter = [
        'prediction_type', 'model_version', 'created_at', 
        'match__competition', 'match__status'
    ]
    search_fields = [
        'match__home_team__name', 'match__away_team__name', 
        'predicted_value', 'actual_value'
    ]
    readonly_fields = ['created_at', 'updated_at', 'features_used_display']
    
    fieldsets = (
        ('Prediction Info', {
            'fields': ('match', 'prediction_type', 'predicted_value', 'confidence_score')
        }),
        ('Model Info', {
            'fields': ('model_version', 'features_used_display')
        }),
        ('Validation', {
            'fields': ('actual_value', 'prediction_accuracy')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def features_used_display(self, obj):
        if obj.features_used:
            formatted_json = json.dumps(obj.features_used, indent=2)
            return format_html('<pre>{}</pre>', formatted_json)
        return '-'
    features_used_display.short_description = 'Features Used'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('match__home_team', 'match__away_team')


@admin.register(PlayerRecommendation)
class PlayerRecommendationAdmin(admin.ModelAdmin):
    list_display = [
        'player', 'team', 'recommendation_type', 'score', 
        'model_version', 'season', 'created_at'
    ]
    list_filter = [
        'recommendation_type', 'model_version', 'season', 
        'created_at', 'team__name'
    ]
    search_fields = [
        'player__name', 'team__name', 'reasons'
    ]
    readonly_fields = ['created_at', 'updated_at', 'reasons_display', 'attributes_display']
    
    fieldsets = (
        ('Recommendation Info', {
            'fields': ('player', 'team', 'recommendation_type', 'score')
        }),
        ('Analysis', {
            'fields': ('reasons_display', 'attributes_display', 'comparison_players')
        }),
        ('Model Info', {
            'fields': ('model_version', 'season')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def reasons_display(self, obj):
        if obj.reasons:
            reasons_html = '<ul>'
            for reason in obj.reasons:
                reasons_html += f'<li>{reason}</li>'
            reasons_html += '</ul>'
            return format_html(reasons_html)
        return '-'
    reasons_display.short_description = 'Recommendation Reasons'
    
    def attributes_display(self, obj):
        if obj.attributes_analysis:
            formatted_json = json.dumps(obj.attributes_analysis, indent=2)
            return format_html('<pre>{}</pre>', formatted_json)
        return '-'
    attributes_display.short_description = 'Attributes Analysis'


@admin.register(SentimentAnalysis)
class SentimentAnalysisAdmin(admin.ModelAdmin):
    list_display = [
        'entity_display', 'sentiment', 'sentiment_score', 
        'confidence', 'source_platform', 'analysis_date'
    ]
    list_filter = [
        'entity_type', 'sentiment', 'source_platform', 
        'analysis_date', 'confidence'
    ]
    search_fields = [
        'source_text', 'keywords'
    ]
    readonly_fields = ['created_at', 'keywords_display', 'source_text_display']
    
    fieldsets = (
        ('Entity Info', {
            'fields': ('entity_type', 'entity_id')
        }),
        ('Sentiment Results', {
            'fields': ('sentiment', 'sentiment_score', 'confidence')
        }),
        ('Source Data', {
            'fields': ('source_text_display', 'source_platform', 'analysis_date')
        }),
        ('Keywords', {
            'fields': ('keywords_display',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def entity_display(self, obj):
        return f"{obj.entity_type} #{obj.entity_id}"
    entity_display.short_description = 'Entity'
    
    def keywords_display(self, obj):
        if obj.keywords:
            return ', '.join(obj.keywords)
        return '-'
    keywords_display.short_description = 'Keywords'
    
    def source_text_display(self, obj):
        if obj.source_text:
            # Truncate long text
            text = obj.source_text[:200] + '...' if len(obj.source_text) > 200 else obj.source_text
            return format_html('<div style="max-width: 400px; word-wrap: break-word;">{}</div>', text)
        return '-'
    source_text_display.short_description = 'Source Text'


@admin.register(InjuryPrediction)
class InjuryPredictionAdmin(admin.ModelAdmin):
    list_display = [
        'player', 'risk_level', 'injury_type', 'risk_score', 
        'prediction_period', 'actual_injury_occurred', 'prediction_date'
    ]
    list_filter = [
        'risk_level', 'injury_type', 'prediction_date', 
        'actual_injury_occurred', 'model_version'
    ]
    search_fields = ['player__name', 'risk_factors', 'recommended_actions']
    readonly_fields = ['created_at', 'updated_at', 'risk_factors_display', 'actions_display']
    
    fieldsets = (
        ('Player & Prediction', {
            'fields': ('player', 'risk_level', 'injury_type', 'risk_score', 'prediction_period')
        }),
        ('Analysis', {
            'fields': ('risk_factors_display', 'actions_display')
        }),
        ('Validation', {
            'fields': ('actual_injury_occurred', 'actual_injury_date', 'actual_injury_type')
        }),
        ('Model Info', {
            'fields': ('model_version', 'prediction_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def risk_factors_display(self, obj):
        if obj.risk_factors:
            formatted_json = json.dumps(obj.risk_factors, indent=2)
            return format_html('<pre>{}</pre>', formatted_json)
        return '-'
    risk_factors_display.short_description = 'Risk Factors'
    
    def actions_display(self, obj):
        if obj.recommended_actions:
            actions_html = '<ul>'
            for action in obj.recommended_actions:
                actions_html += f'<li>{action}</li>'
            actions_html += '</ul>'
            return format_html(actions_html)
        return '-'
    actions_display.short_description = 'Recommended Actions'


@admin.register(MarketValuePrediction)
class MarketValuePredictionAdmin(admin.ModelAdmin):
    list_display = [
        'player', 'predicted_value_display', 'currency', 
        'confidence_interval_display', 'season', 'prediction_date'
    ]
    list_filter = [
        'currency', 'season', 'prediction_date', 'model_version'
    ]
    search_fields = ['player__name', 'value_factors']
    readonly_fields = [
        'created_at', 'updated_at', 'value_factors_display', 
        'trend_display', 'comparable_display'
    ]
    
    def predicted_value_display(self, obj):
        return f"{obj.predicted_value:,.0f} {obj.currency}"
    predicted_value_display.short_description = 'Predicted Value'
    
    def confidence_interval_display(self, obj):
        return f"{obj.confidence_interval_low:,.0f} - {obj.confidence_interval_high:,.0f} {obj.currency}"
    confidence_interval_display.short_description = 'Confidence Interval'
    
    def value_factors_display(self, obj):
        if obj.value_factors:
            formatted_json = json.dumps(obj.value_factors, indent=2)
            return format_html('<pre>{}</pre>', formatted_json)
        return '-'
    value_factors_display.short_description = 'Value Factors'
    
    def trend_display(self, obj):
        if obj.trend_analysis:
            formatted_json = json.dumps(obj.trend_analysis, indent=2)
            return format_html('<pre>{}</pre>', formatted_json)
        return '-'
    trend_display.short_description = 'Trend Analysis'
    
    def comparable_display(self, obj):
        if obj.comparable_players:
            formatted_json = json.dumps(obj.comparable_players, indent=2)
            return format_html('<pre>{}</pre>', formatted_json)
        return '-'
    comparable_display.short_description = 'Comparable Players'


@admin.register(PlayStyleCluster)
class PlayStyleClusterAdmin(admin.ModelAdmin):
    list_display = [
        'entity_display', 'cluster_name', 'cluster_id', 
        'distance_to_centroid', 'season', 'analysis_date'
    ]
    list_filter = [
        'entity_type', 'cluster_id', 'season', 
        'analysis_date', 'model_version'
    ]
    search_fields = ['cluster_name', 'style_attributes']
    readonly_fields = [
        'created_at', 'updated_at', 'style_attributes_display',
        'centroid_display', 'similar_entities_display', 'characteristics_display'
    ]
    
    def entity_display(self, obj):
        return f"{obj.entity_type} #{obj.entity_id}"
    entity_display.short_description = 'Entity'
    
    def style_attributes_display(self, obj):
        if obj.style_attributes:
            formatted_json = json.dumps(obj.style_attributes, indent=2)
            return format_html('<pre>{}</pre>', formatted_json)
        return '-'
    style_attributes_display.short_description = 'Style Attributes'
    
    def centroid_display(self, obj):
        if obj.cluster_centroid:
            formatted_json = json.dumps(obj.cluster_centroid, indent=2)
            return format_html('<pre>{}</pre>', formatted_json)
        return '-'
    centroid_display.short_description = 'Cluster Centroid'
    
    def similar_entities_display(self, obj):
        if obj.similar_entities:
            entities_html = '<ul>'
            for entity in obj.similar_entities[:5]:  # Show first 5
                entities_html += f'<li>{entity}</li>'
            entities_html += '</ul>'
            return format_html(entities_html)
        return '-'
    similar_entities_display.short_description = 'Similar Entities'
    
    def characteristics_display(self, obj):
        if obj.characteristic_stats:
            formatted_json = json.dumps(obj.characteristic_stats, indent=2)
            return format_html('<pre>{}</pre>', formatted_json)
        return '-'
    characteristics_display.short_description = 'Characteristic Stats'


@admin.register(AnomalyDetection)
class AnomalyDetectionAdmin(admin.ModelAdmin):
    list_display = [
        'entity_display', 'anomaly_type', 'severity', 
        'anomaly_score', 'investigated', 'false_positive', 'detection_date'
    ]
    list_filter = [
        'entity_type', 'anomaly_type', 'severity', 
        'investigated', 'false_positive', 'detection_date'
    ]
    search_fields = ['description', 'investigation_notes']
    readonly_fields = [
        'created_at', 'updated_at', 'evidence_display',
        'normal_range_display', 'actual_values_display'
    ]
    
    actions = ['mark_as_investigated', 'mark_as_false_positive']
    
    def entity_display(self, obj):
        return f"{obj.entity_type} #{obj.entity_id}"
    entity_display.short_description = 'Entity'
    
    def evidence_display(self, obj):
        if obj.evidence:
            formatted_json = json.dumps(obj.evidence, indent=2)
            return format_html('<pre>{}</pre>', formatted_json)
        return '-'
    evidence_display.short_description = 'Evidence'
    
    def normal_range_display(self, obj):
        if obj.normal_range:
            formatted_json = json.dumps(obj.normal_range, indent=2)
            return format_html('<pre>{}</pre>', formatted_json)
        return '-'
    normal_range_display.short_description = 'Normal Range'
    
    def actual_values_display(self, obj):
        if obj.actual_values:
            formatted_json = json.dumps(obj.actual_values, indent=2)
            return format_html('<pre>{}</pre>', formatted_json)
        return '-'
    actual_values_display.short_description = 'Actual Values'
    
    def mark_as_investigated(self, request, queryset):
        queryset.update(investigated=True)
        self.message_user(request, f"Marked {queryset.count()} anomalies as investigated.")
    mark_as_investigated.short_description = "Mark selected anomalies as investigated"
    
    def mark_as_false_positive(self, request, queryset):
        queryset.update(false_positive=True, investigated=True)
        self.message_user(request, f"Marked {queryset.count()} anomalies as false positive.")
    mark_as_false_positive.short_description = "Mark selected anomalies as false positive"


@admin.register(TransferSimulation)
class TransferSimulationAdmin(admin.ModelAdmin):
    list_display = [
        'player', 'transfer_display', 'transfer_type', 
        'estimated_fee_display', 'success_probability', 'simulation_date'
    ]
    list_filter = [
        'transfer_type', 'simulation_date', 'season', 'model_version'
    ]
    search_fields = ['player__name', 'from_team__name', 'to_team__name']
    readonly_fields = [
        'created_at', 'updated_at', 'impact_analysis_display',
        'risk_assessment_display', 'performance_display'
    ]
    
    def transfer_display(self, obj):
        return f"{obj.from_team.name} → {obj.to_team.name}"
    transfer_display.short_description = 'Transfer'
    
    def estimated_fee_display(self, obj):
        if obj.estimated_fee:
            return f"€{obj.estimated_fee:,.0f}"
        return '-'
    estimated_fee_display.short_description = 'Estimated Fee'
    
    def impact_analysis_display(self, obj):
        if obj.impact_analysis:
            formatted_json = json.dumps(obj.impact_analysis, indent=2)
            return format_html('<pre>{}</pre>', formatted_json)
        return '-'
    impact_analysis_display.short_description = 'Impact Analysis'
    
    def risk_assessment_display(self, obj):
        if obj.risk_assessment:
            formatted_json = json.dumps(obj.risk_assessment, indent=2)
            return format_html('<pre>{}</pre>', formatted_json)
        return '-'
    risk_assessment_display.short_description = 'Risk Assessment'
    
    def performance_display(self, obj):
        if obj.predicted_performance:
            formatted_json = json.dumps(obj.predicted_performance, indent=2)
            return format_html('<pre>{}</pre>', formatted_json)
        return '-'
    performance_display.short_description = 'Predicted Performance'
