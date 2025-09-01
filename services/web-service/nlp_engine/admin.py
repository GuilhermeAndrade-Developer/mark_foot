from django.contrib import admin
from .models import Intent, EntityType, TrainingPhrase, EntityValue, UserQuery, IntentPattern, EntityRecognitionLog


@admin.register(Intent)
class IntentAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'confidence_threshold', 'is_active', 'created_at']
    list_filter = ['name', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(EntityType)
class EntityTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_active', 'created_at']
    list_filter = ['name', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(TrainingPhrase)
class TrainingPhraseAdmin(admin.ModelAdmin):
    list_display = ['intent', 'phrase_preview', 'language', 'confidence_score', 'is_active']
    list_filter = ['intent', 'language', 'is_active']
    search_fields = ['phrase', 'intent__name']
    ordering = ['intent', 'phrase']
    
    def phrase_preview(self, obj):
        return obj.phrase[:50] + "..." if len(obj.phrase) > 50 else obj.phrase
    phrase_preview.short_description = 'Phrase'


@admin.register(EntityValue)
class EntityValueAdmin(admin.ModelAdmin):
    list_display = ['entity_type', 'canonical_value', 'confidence_score', 'is_active']
    list_filter = ['entity_type', 'is_active']
    search_fields = ['value', 'canonical_value']
    ordering = ['entity_type', 'canonical_value']


@admin.register(UserQuery)
class UserQueryAdmin(admin.ModelAdmin):
    list_display = ['query_preview', 'detected_intent', 'intent_confidence', 'was_successful', 'timestamp']
    list_filter = ['detected_intent', 'was_successful', 'language', 'timestamp']
    search_fields = ['query_text', 'whatsapp_user_phone']
    ordering = ['-timestamp']
    readonly_fields = ['timestamp']
    
    def query_preview(self, obj):
        return obj.query_text[:50] + "..." if len(obj.query_text) > 50 else obj.query_text
    query_preview.short_description = 'Query'


@admin.register(IntentPattern)
class IntentPatternAdmin(admin.ModelAdmin):
    list_display = ['intent', 'pattern_preview', 'pattern_type', 'weight', 'is_active']
    list_filter = ['intent', 'pattern_type', 'is_active']
    search_fields = ['pattern']
    ordering = ['intent', 'weight']
    
    def pattern_preview(self, obj):
        return obj.pattern[:50] + "..." if len(obj.pattern) > 50 else obj.pattern
    pattern_preview.short_description = 'Pattern'


@admin.register(EntityRecognitionLog)
class EntityRecognitionLogAdmin(admin.ModelAdmin):
    list_display = ['entity_type', 'extracted_text', 'canonical_value', 'confidence_score', 'extraction_method', 'was_correct']
    list_filter = ['entity_type', 'extraction_method', 'was_correct']
    search_fields = ['extracted_text', 'canonical_value']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
