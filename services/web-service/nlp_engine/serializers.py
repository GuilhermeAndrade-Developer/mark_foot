from rest_framework import serializers
from .models import Intent, EntityType, TrainingPhrase, UserQuery


class IntentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Intent
        fields = ['id', 'name', 'description', 'confidence_threshold', 'is_active', 'created_at']


class EntityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityType
        fields = ['id', 'name', 'description', 'pattern_regex', 'is_active', 'created_at']


class TrainingPhraseSerializer(serializers.ModelSerializer):
    intent_name = serializers.CharField(source='intent.name', read_only=True)
    
    class Meta:
        model = TrainingPhrase
        fields = ['id', 'intent', 'intent_name', 'phrase', 'language', 'confidence_score', 'is_active', 'created_at']


class UserQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserQuery
        fields = [
            'id', 'query_text', 'detected_intent', 'intent_confidence',
            'detected_entities', 'response_generated', 'processing_time_ms',
            'was_successful', 'timestamp', 'language'
        ]


class QueryRequestSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=1000)
    user_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    user_id = serializers.IntegerField(required=False, allow_null=True)
    language = serializers.CharField(max_length=5, default='pt')


class QueryResponseSerializer(serializers.Serializer):
    query = serializers.CharField()
    intent = serializers.CharField()
    intent_confidence = serializers.FloatField()
    entities = serializers.JSONField()
    response = serializers.CharField()
    processing_time_ms = serializers.IntegerField()
    success = serializers.BooleanField()
