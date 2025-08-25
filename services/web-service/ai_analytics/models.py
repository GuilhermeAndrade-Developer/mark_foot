from django.db import models
from core.models import Player, Team, Match, Competition, Season


class MatchPrediction(models.Model):
    """Model to store match predictions from AI models"""
    
    PREDICTION_TYPES = [
        ('RESULT', 'Match Result'),
        ('SCORE', 'Exact Score'),
        ('GOALS', 'Total Goals'),
        ('BOTH_TEAMS_SCORE', 'Both Teams to Score'),
    ]
    
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='predictions')
    prediction_type = models.CharField(max_length=20, choices=PREDICTION_TYPES)
    predicted_value = models.CharField(max_length=50, help_text="Predicted outcome")
    confidence_score = models.FloatField(help_text="Confidence percentage (0-1)")
    model_version = models.CharField(max_length=50, help_text="AI model version used")
    features_used = models.JSONField(help_text="Features used for prediction")
    
    # Actual results for validation
    actual_value = models.CharField(max_length=50, null=True, blank=True)
    prediction_accuracy = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_match_predictions'
        unique_together = ['match', 'prediction_type', 'model_version']
        indexes = [
            models.Index(fields=['match', 'prediction_type']),
            models.Index(fields=['confidence_score']),
            models.Index(fields=['created_at']),
        ]
        
    def __str__(self):
        return f"{self.match} - {self.prediction_type}: {self.predicted_value}"


class PlayerRecommendation(models.Model):
    """Model to store player recommendations based on performance"""
    
    RECOMMENDATION_TYPES = [
        ('SIGNING', 'Transfer Signing'),
        ('LINEUP', 'Starting Lineup'),
        ('SUBSTITUTE', 'Substitution'),
        ('CAPTAIN', 'Team Captain'),
        ('FANTASY', 'Fantasy Pick'),
    ]
    
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='recommendations')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='player_recommendations')
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPES)
    score = models.FloatField(help_text="Recommendation score (0-100)")
    reasons = models.JSONField(help_text="List of reasons for recommendation")
    attributes_analysis = models.JSONField(help_text="Detailed attributes analysis")
    comparison_players = models.JSONField(null=True, blank=True, help_text="Similar players for comparison")
    
    model_version = models.CharField(max_length=50)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_player_recommendations'
        indexes = [
            models.Index(fields=['player', 'team']),
            models.Index(fields=['recommendation_type']),
            models.Index(fields=['score']),
            models.Index(fields=['season']),
        ]
        
    def __str__(self):
        return f"{self.player.name} -> {self.team.name} ({self.recommendation_type})"


class SentimentAnalysis(models.Model):
    """Model to store sentiment analysis results"""
    
    SENTIMENT_TYPES = [
        ('POSITIVE', 'Positive'),
        ('NEGATIVE', 'Negative'),
        ('NEUTRAL', 'Neutral'),
    ]
    
    ENTITY_TYPES = [
        ('PLAYER', 'Player'),
        ('TEAM', 'Team'),
        ('MATCH', 'Match'),
        ('COMPETITION', 'Competition'),
    ]
    
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPES)
    entity_id = models.BigIntegerField(help_text="ID of the entity (player, team, etc.)")
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_TYPES)
    sentiment_score = models.FloatField(help_text="Sentiment score (-1 to 1)")
    confidence = models.FloatField(help_text="Confidence in sentiment analysis")
    
    source_text = models.TextField(help_text="Original text analyzed")
    source_platform = models.CharField(max_length=50, help_text="Platform source (Twitter, Facebook, etc.)")
    keywords = models.JSONField(help_text="Key words/phrases extracted")
    
    analysis_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_sentiment_analysis'
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['sentiment']),
            models.Index(fields=['analysis_date']),
        ]
        
    def __str__(self):
        return f"{self.entity_type} {self.entity_id} - {self.sentiment}"


class InjuryPrediction(models.Model):
    """Model to store injury predictions for players"""
    
    RISK_LEVELS = [
        ('LOW', 'Low Risk'),
        ('MEDIUM', 'Medium Risk'),
        ('HIGH', 'High Risk'),
        ('CRITICAL', 'Critical Risk'),
    ]
    
    INJURY_TYPES = [
        ('MUSCLE', 'Muscle Injury'),
        ('LIGAMENT', 'Ligament Injury'),
        ('BONE', 'Bone Injury'),
        ('FATIGUE', 'Fatigue/Overuse'),
        ('GENERAL', 'General Injury'),
    ]
    
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='injury_predictions')
    risk_level = models.CharField(max_length=10, choices=RISK_LEVELS)
    injury_type = models.CharField(max_length=20, choices=INJURY_TYPES)
    risk_score = models.FloatField(help_text="Risk score (0-100)")
    prediction_period = models.IntegerField(help_text="Prediction period in days")
    
    risk_factors = models.JSONField(help_text="Factors contributing to injury risk")
    recommended_actions = models.JSONField(help_text="Recommended preventive actions")
    
    model_version = models.CharField(max_length=50)
    prediction_date = models.DateTimeField()
    
    # Validation fields
    actual_injury_occurred = models.BooleanField(null=True, blank=True)
    actual_injury_date = models.DateTimeField(null=True, blank=True)
    actual_injury_type = models.CharField(max_length=20, choices=INJURY_TYPES, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_injury_predictions'
        indexes = [
            models.Index(fields=['player', 'risk_level']),
            models.Index(fields=['prediction_date']),
            models.Index(fields=['risk_score']),
        ]
        
    def __str__(self):
        return f"{self.player.name} - {self.risk_level} ({self.injury_type})"


class MarketValuePrediction(models.Model):
    """Model to store market value predictions for players"""
    
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='market_predictions')
    predicted_value = models.DecimalField(max_digits=15, decimal_places=2, help_text="Predicted market value")
    currency = models.CharField(max_length=3, default='EUR')
    confidence_interval_low = models.DecimalField(max_digits=15, decimal_places=2)
    confidence_interval_high = models.DecimalField(max_digits=15, decimal_places=2)
    
    value_factors = models.JSONField(help_text="Factors affecting market value")
    trend_analysis = models.JSONField(help_text="Value trend over time")
    comparable_players = models.JSONField(help_text="Similar players for value comparison")
    
    model_version = models.CharField(max_length=50)
    prediction_date = models.DateTimeField()
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_market_value_predictions'
        indexes = [
            models.Index(fields=['player', 'prediction_date']),
            models.Index(fields=['predicted_value']),
            models.Index(fields=['season']),
        ]
        
    def __str__(self):
        return f"{self.player.name} - {self.predicted_value} {self.currency}"


class PlayStyleCluster(models.Model):
    """Model to store player/team play style clusters"""
    
    CLUSTER_TYPES = [
        ('PLAYER', 'Player Style'),
        ('TEAM', 'Team Style'),
    ]
    
    entity_type = models.CharField(max_length=10, choices=CLUSTER_TYPES)
    entity_id = models.BigIntegerField(help_text="ID of player or team")
    cluster_id = models.IntegerField(help_text="Cluster group ID")
    cluster_name = models.CharField(max_length=100, help_text="Descriptive cluster name")
    
    style_attributes = models.JSONField(help_text="Key style attributes")
    cluster_centroid = models.JSONField(help_text="Cluster center coordinates")
    distance_to_centroid = models.FloatField(help_text="Distance from cluster center")
    
    similar_entities = models.JSONField(help_text="Other entities in same cluster")
    characteristic_stats = models.JSONField(help_text="Stats that define this style")
    
    model_version = models.CharField(max_length=50)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    analysis_date = models.DateTimeField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_playstyle_clusters'
        unique_together = ['entity_type', 'entity_id', 'season', 'model_version']
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['cluster_id']),
            models.Index(fields=['season']),
        ]
        
    def __str__(self):
        return f"{self.entity_type} {self.entity_id} - {self.cluster_name}"


class AnomalyDetection(models.Model):
    """Model to store anomaly detection results"""
    
    ANOMALY_TYPES = [
        ('PERFORMANCE', 'Performance Anomaly'),
        ('BETTING', 'Betting Anomaly'),
        ('STATISTICAL', 'Statistical Anomaly'),
        ('BEHAVIORAL', 'Behavioral Anomaly'),
    ]
    
    SEVERITY_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    entity_type = models.CharField(max_length=20, help_text="Type of entity (player, team, match)")
    entity_id = models.BigIntegerField(help_text="ID of the entity")
    anomaly_type = models.CharField(max_length=20, choices=ANOMALY_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    
    anomaly_score = models.FloatField(help_text="Anomaly score (higher = more anomalous)")
    description = models.TextField(help_text="Description of the anomaly")
    evidence = models.JSONField(help_text="Evidence and data supporting anomaly")
    
    normal_range = models.JSONField(help_text="Expected normal range for comparison")
    actual_values = models.JSONField(help_text="Actual values that triggered anomaly")
    
    model_version = models.CharField(max_length=50)
    detection_date = models.DateTimeField()
    
    # Investigation fields
    investigated = models.BooleanField(default=False)
    investigation_notes = models.TextField(null=True, blank=True)
    false_positive = models.BooleanField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_anomaly_detection'
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['anomaly_type', 'severity']),
            models.Index(fields=['detection_date']),
            models.Index(fields=['investigated']),
        ]
        
    def __str__(self):
        return f"{self.entity_type} {self.entity_id} - {self.anomaly_type} ({self.severity})"


class TransferSimulation(models.Model):
    """Model to store transfer simulation results"""
    
    TRANSFER_TYPES = [
        ('IN', 'Transfer In'),
        ('OUT', 'Transfer Out'),
        ('LOAN_IN', 'Loan In'),
        ('LOAN_OUT', 'Loan Out'),
    ]
    
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='transfer_simulations')
    from_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='simulated_transfers_out')
    to_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='simulated_transfers_in')
    transfer_type = models.CharField(max_length=10, choices=TRANSFER_TYPES)
    
    # Financial impact
    estimated_fee = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    wage_impact = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    total_cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Performance impact
    team_strength_change = models.FloatField(help_text="Change in team strength (-100 to 100)")
    predicted_performance = models.JSONField(help_text="Predicted performance metrics")
    tactical_fit = models.FloatField(help_text="How well player fits team tactics (0-100)")
    
    # Analysis details
    impact_analysis = models.JSONField(help_text="Detailed impact analysis")
    risk_assessment = models.JSONField(help_text="Transfer risk assessment")
    success_probability = models.FloatField(help_text="Probability of successful transfer")
    
    model_version = models.CharField(max_length=50)
    simulation_date = models.DateTimeField()
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_transfer_simulations'
        indexes = [
            models.Index(fields=['player', 'from_team', 'to_team']),
            models.Index(fields=['transfer_type']),
            models.Index(fields=['simulation_date']),
            models.Index(fields=['success_probability']),
        ]
        
    def __str__(self):
        return f"{self.player.name}: {self.from_team.name} -> {self.to_team.name}"
