from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ForumCategory, ForumTopic, ForumPost, ForumVote, ForumUserProfile


class UserSerializer(serializers.ModelSerializer):
    """Serializer para dados básicos do usuário"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'date_joined']


class ForumUserProfileSerializer(serializers.ModelSerializer):
    """Serializer para perfil do usuário no fórum"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ForumUserProfile
        fields = [
            'user', 'total_posts', 'total_topics', 'reputation_score',
            'signature', 'receive_notifications', 'joined_at', 'last_seen'
        ]


class ForumCategorySerializer(serializers.ModelSerializer):
    """Serializer para categorias do fórum"""
    
    class Meta:
        model = ForumCategory
        fields = [
            'id', 'name', 'description', 'slug', 'category_type',
            'team_id', 'competition_id', 'is_active', 'is_moderated',
            'created_at', 'updated_at', 'topic_count', 'post_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'topic_count', 'post_count']


class ForumCategoryDetailSerializer(ForumCategorySerializer):
    """Serializer detalhado para categorias com últimos tópicos"""
    recent_topics = serializers.SerializerMethodField()
    
    class Meta(ForumCategorySerializer.Meta):
        fields = ForumCategorySerializer.Meta.fields + ['recent_topics']
    
    def get_recent_topics(self, obj):
        """Retorna os 5 tópicos mais recentes da categoria"""
        recent = obj.topics.filter(status='open')[:5]
        return ForumTopicListSerializer(recent, many=True, context=self.context).data


class ForumTopicListSerializer(serializers.ModelSerializer):
    """Serializer para lista de tópicos"""
    author = UserSerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    last_post_author = serializers.SerializerMethodField()
    last_post_date = serializers.DateTimeField(source='last_activity', read_only=True)
    
    class Meta:
        model = ForumTopic
        fields = [
            'id', 'title', 'slug', 'author', 'category_name', 'status',
            'created_at', 'updated_at', 'last_activity', 'view_count',
            'post_count', 'tags', 'last_post_author', 'last_post_date'
        ]
        read_only_fields = [
            'id', 'author', 'created_at', 'updated_at', 'last_activity',
            'view_count', 'post_count'
        ]
    
    def get_last_post_author(self, obj):
        """Retorna o autor do último post"""
        last_post = obj.posts.order_by('-created_at').first()
        if last_post:
            return last_post.author.username
        return obj.author.username


class ForumTopicSerializer(serializers.ModelSerializer):
    """Serializer para criação/edição de tópicos"""
    author = UserSerializer(read_only=True)
    category = ForumCategorySerializer(read_only=True)
    category_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = ForumTopic
        fields = [
            'id', 'category', 'category_id', 'title', 'slug', 'content',
            'author', 'status', 'created_at', 'updated_at', 'last_activity',
            'view_count', 'post_count', 'tags'
        ]
        read_only_fields = [
            'id', 'author', 'created_at', 'updated_at', 'last_activity',
            'view_count', 'post_count'
        ]
    
    def create(self, validated_data):
        """Cria um novo tópico"""
        category_id = validated_data.pop('category_id')
        validated_data['category'] = ForumCategory.objects.get(id=category_id)
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class ForumPostSerializer(serializers.ModelSerializer):
    """Serializer para posts do fórum"""
    author = UserSerializer(read_only=True)
    topic_title = serializers.CharField(source='topic.title', read_only=True)
    vote_score = serializers.SerializerMethodField()
    user_vote = serializers.SerializerMethodField()
    replies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ForumPost
        fields = [
            'id', 'topic', 'content', 'author', 'topic_title', 'parent',
            'created_at', 'updated_at', 'is_edited', 'is_deleted',
            'is_reported', 'position', 'vote_score', 'user_vote', 'replies_count'
        ]
        read_only_fields = [
            'id', 'author', 'created_at', 'updated_at', 'is_edited',
            'position', 'vote_score', 'user_vote', 'replies_count'
        ]
    
    def get_vote_score(self, obj):
        """Calcula score de votos (upvotes - downvotes)"""
        upvotes = obj.votes.filter(vote_type='upvote').count()
        downvotes = obj.votes.filter(vote_type='downvote').count()
        return upvotes - downvotes
    
    def get_user_vote(self, obj):
        """Retorna o voto do usuário atual neste post"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            vote = obj.votes.filter(user=request.user).first()
            return vote.vote_type if vote else None
        return None
    
    def get_replies_count(self, obj):
        """Conta respostas diretas ao post"""
        return obj.replies.filter(is_deleted=False).count()


class ForumPostCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de posts"""
    
    class Meta:
        model = ForumPost
        fields = ['topic', 'content', 'parent']
    
    def create(self, validated_data):
        """Cria um novo post"""
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class ForumVoteSerializer(serializers.ModelSerializer):
    """Serializer para votação em posts"""
    
    class Meta:
        model = ForumVote
        fields = ['post', 'vote_type']
    
    def create(self, validated_data):
        """Cria ou atualiza um voto"""
        validated_data['user'] = self.context['request'].user
        
        # Verificar se já existe um voto deste usuário neste post
        existing_vote = ForumVote.objects.filter(
            post=validated_data['post'],
            user=validated_data['user']
        ).first()
        
        if existing_vote:
            # Se o voto é o mesmo, remove o voto
            if existing_vote.vote_type == validated_data['vote_type']:
                existing_vote.delete()
                return None
            else:
                # Se o voto é diferente, atualiza
                existing_vote.vote_type = validated_data['vote_type']
                existing_vote.save()
                return existing_vote
        else:
            # Cria novo voto
            return super().create(validated_data)


class ForumStatsSerializer(serializers.Serializer):
    """Serializer para estatísticas gerais do fórum"""
    total_categories = serializers.IntegerField()
    total_topics = serializers.IntegerField()
    total_posts = serializers.IntegerField()
    total_users = serializers.IntegerField()
    most_active_category = serializers.CharField()
    most_active_user = serializers.CharField()
    recent_activity = serializers.ListField()


class ForumSearchSerializer(serializers.Serializer):
    """Serializer para busca no fórum"""
    query = serializers.CharField(max_length=200)
    category = serializers.UUIDField(required=False)
    author = serializers.CharField(max_length=150, required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    sort_by = serializers.ChoiceField(
        choices=['relevance', 'date', 'votes'],
        default='relevance'
    )
