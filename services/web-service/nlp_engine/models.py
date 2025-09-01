from django.db import models


class Intent(models.Model):
    """Represents different types of user intents in football queries"""
    
    INTENT_TYPES = [
        ('team_stats', 'Team Statistics'),
        ('player_stats', 'Player Statistics'),
        ('match_info', 'Match Information'),
        ('standings', 'League Standings'),
        ('subscription', 'Subscription Related'),
        ('help', 'Help/General'),
        ('betting_odds', 'Betting Odds'),
        ('predictions', 'Match Predictions'),
        ('news', 'Football News'),
        ('schedule', 'Match Schedule'),
    ]
    
    name = models.CharField(max_length=50, choices=INTENT_TYPES, unique=True)
    description = models.TextField()
    confidence_threshold = models.FloatField(default=0.7)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'nlp_intents'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.get_name_display()}"


class EntityType(models.Model):
    """Defines different types of entities that can be extracted from user queries"""
    
    ENTITY_TYPES = [
        ('team', 'Team'),
        ('player', 'Player'),
        ('competition', 'Competition'),
        ('date', 'Date'),
        ('number', 'Number'),
        ('location', 'Location'),
        ('season', 'Season'),
        ('match_status', 'Match Status'),
    ]
    
    name = models.CharField(max_length=50, choices=ENTITY_TYPES, unique=True)
    description = models.TextField()
    pattern_regex = models.TextField(blank=True, help_text="Optional regex pattern for entity recognition")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'nlp_entity_types'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.get_name_display()}"


class TrainingPhrase(models.Model):
    """Training phrases for intent recognition"""
    
    intent = models.ForeignKey(Intent, on_delete=models.CASCADE, related_name='training_phrases')
    phrase = models.TextField()
    language = models.CharField(max_length=5, default='pt')
    confidence_score = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'nlp_training_phrases'
        indexes = [
            models.Index(fields=['intent']),
            models.Index(fields=['language']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.intent.name}: {self.phrase[:50]}..."


class EntityValue(models.Model):
    """Predefined entity values and their synonyms"""
    
    entity_type = models.ForeignKey(EntityType, on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=200)
    canonical_value = models.CharField(max_length=200, help_text="Standardized form of the value")
    synonyms = models.JSONField(default=list, help_text="List of synonyms for this entity")
    confidence_score = models.FloatField(default=1.0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'nlp_entity_values'
        indexes = [
            models.Index(fields=['entity_type']),
            models.Index(fields=['canonical_value']),
            models.Index(fields=['is_active']),
        ]
        unique_together = ['entity_type', 'canonical_value']

    def __str__(self):
        return f"{self.entity_type.name}: {self.canonical_value}"


class UserQuery(models.Model):
    """Stores user queries and their processing results"""
    
    query_text = models.TextField()
    normalized_query = models.TextField(blank=True)
    detected_intent = models.CharField(max_length=50, blank=True)
    intent_confidence = models.FloatField(null=True, blank=True)
    detected_entities = models.JSONField(default=dict, help_text="Extracted entities with confidence scores")
    response_generated = models.TextField(blank=True)
    processing_time_ms = models.IntegerField(null=True, blank=True)
    was_successful = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    
    # User context
    whatsapp_user_phone = models.CharField(max_length=20, blank=True)
    user_id = models.IntegerField(null=True, blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    
    # Metadata
    timestamp = models.DateTimeField(auto_now_add=True)
    language = models.CharField(max_length=5, default='pt')
    
    class Meta:
        db_table = 'nlp_user_queries'
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['detected_intent']),
            models.Index(fields=['whatsapp_user_phone']),
            models.Index(fields=['was_successful']),
            models.Index(fields=['language']),
        ]

    def __str__(self):
        return f"Query: {self.query_text[:50]}... [{self.detected_intent}]"


class IntentPattern(models.Model):
    """Specific patterns for intent recognition"""
    
    intent = models.ForeignKey(Intent, on_delete=models.CASCADE, related_name='patterns')
    pattern = models.TextField(help_text="Pattern for matching user queries")
    pattern_type = models.CharField(
        max_length=20,
        choices=[
            ('regex', 'Regular Expression'),
            ('keyword', 'Keywords'),
            ('phrase', 'Exact Phrase'),
            ('semantic', 'Semantic Similarity'),
        ],
        default='keyword'
    )
    weight = models.FloatField(default=1.0, help_text="Pattern weight for scoring")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'nlp_intent_patterns'
        indexes = [
            models.Index(fields=['intent']),
            models.Index(fields=['pattern_type']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.intent.name}: {self.pattern[:50]}..."


class EntityRecognitionLog(models.Model):
    """Logs entity recognition results for analysis and improvement"""
    
    query = models.ForeignKey(UserQuery, on_delete=models.CASCADE, related_name='entity_logs')
    entity_type = models.CharField(max_length=50)
    extracted_text = models.CharField(max_length=200)
    canonical_value = models.CharField(max_length=200)
    confidence_score = models.FloatField()
    extraction_method = models.CharField(
        max_length=20,
        choices=[
            ('regex', 'Regular Expression'),
            ('database', 'Database Match'),
            ('nlp', 'NLP Model'),
            ('manual', 'Manual Rule'),
        ],
        default='nlp'
    )
    was_correct = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'nlp_entity_recognition_logs'
        indexes = [
            models.Index(fields=['query']),
            models.Index(fields=['entity_type']),
            models.Index(fields=['confidence_score']),
            models.Index(fields=['extraction_method']),
        ]

    def __str__(self):
        return f"{self.entity_type}: {self.extracted_text} -> {self.canonical_value}"
