from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Poll, PollOption, PollVote, PollComment


class UserBasicSerializer(serializers.ModelSerializer):
    """Serializer básico para usuário"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']
        
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class PollOptionSerializer(serializers.ModelSerializer):
    """Serializer para opções de enquete"""
    
    class Meta:
        model = PollOption
        fields = ['id', 'text', 'description', 'image', 'votes', 'percentage', 
                 'order', 'is_active', 'created_at']
        read_only_fields = ['votes', 'percentage']


class PollCommentSerializer(serializers.ModelSerializer):
    """Serializer para comentários de enquetes"""
    author = UserBasicSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = PollComment
        fields = ['id', 'content', 'author', 'parent', 'is_approved', 
                 'likes', 'replies', 'created_at', 'updated_at']
        
    def get_replies(self, obj):
        if obj.replies.exists():
            return PollCommentSerializer(obj.replies.all(), many=True).data
        return []


class PollListSerializer(serializers.ModelSerializer):
    """Serializer para listagem de enquetes"""
    author = UserBasicSerializer(read_only=True)
    options_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    time_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = Poll
        fields = ['id', 'title', 'slug', 'description', 'question', 'author', 
                 'status', 'featured_image', 'is_multiple_choice', 'is_anonymous', 
                 'is_featured', 'total_votes', 'views', 'participation_rate', 
                 'options_count', 'comments_count', 'time_remaining', 
                 'start_date', 'end_date', 'created_at', 'updated_at']
        
    def get_options_count(self, obj):
        return obj.options.filter(is_active=True).count()
        
    def get_comments_count(self, obj):
        return obj.comments.filter(is_approved=True).count()
        
    def get_time_remaining(self, obj):
        if obj.end_date:
            from django.utils import timezone
            if obj.end_date > timezone.now():
                delta = obj.end_date - timezone.now()
                return delta.total_seconds()
        return None


class PollDetailSerializer(PollListSerializer):
    """Serializer detalhado para enquetes"""
    options = PollOptionSerializer(many=True, read_only=True)
    comments = PollCommentSerializer(many=True, read_only=True)
    
    class Meta(PollListSerializer.Meta):
        fields = PollListSerializer.Meta.fields + ['options', 'comments']


class PollCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação/edição de enquetes"""
    options = PollOptionSerializer(many=True, write_only=True)
    
    class Meta:
        model = Poll
        fields = ['title', 'description', 'question', 'status', 'featured_image', 
                 'is_multiple_choice', 'is_anonymous', 'is_featured', 
                 'start_date', 'end_date', 'options']
        
    def create(self, validated_data):
        options_data = validated_data.pop('options')
        validated_data['author'] = self.context['request'].user
        poll = super().create(validated_data)
        
        for i, option_data in enumerate(options_data):
            option_data['order'] = i
            PollOption.objects.create(poll=poll, **option_data)
            
        return poll
        
    def update(self, instance, validated_data):
        options_data = validated_data.pop('options', None)
        poll = super().update(instance, validated_data)
        
        if options_data is not None:
            # Remove opções existentes
            poll.options.all().delete()
            # Cria novas opções
            for i, option_data in enumerate(options_data):
                option_data['order'] = i
                PollOption.objects.create(poll=poll, **option_data)
                
        return poll


class PollVoteSerializer(serializers.ModelSerializer):
    """Serializer para votos em enquetes"""
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = PollVote
        fields = ['id', 'option', 'user', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
