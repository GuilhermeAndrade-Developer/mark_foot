from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ContentCategory, UserArticle, ArticleComment, ArticleVote


class UserBasicSerializer(serializers.ModelSerializer):
    """Serializer básico para usuário"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']
        
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class ContentCategorySerializer(serializers.ModelSerializer):
    """Serializer para categorias de conteúdo"""
    articles_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ContentCategory
        fields = ['id', 'name', 'slug', 'description', 'icon', 'is_active', 
                 'articles_count', 'created_at', 'updated_at']
        
    def get_articles_count(self, obj):
        return obj.userarticle_set.filter(status='published').count()


class ArticleCommentSerializer(serializers.ModelSerializer):
    """Serializer para comentários de artigos"""
    author = UserBasicSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = ArticleComment
        fields = ['id', 'content', 'author', 'parent', 'is_approved', 
                 'likes', 'replies', 'created_at', 'updated_at']
        
    def get_replies(self, obj):
        if obj.replies.exists():
            return ArticleCommentSerializer(obj.replies.all(), many=True).data
        return []


class UserArticleListSerializer(serializers.ModelSerializer):
    """Serializer para listagem de artigos"""
    author = UserBasicSerializer(read_only=True)
    category = ContentCategorySerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()
    tags_list = serializers.SerializerMethodField()
    
    class Meta:
        model = UserArticle
        fields = ['id', 'title', 'slug', 'excerpt', 'author', 'category', 
                 'status', 'featured_image', 'tags', 'tags_list', 'read_time', 
                 'views', 'likes', 'dislikes', 'vote_score', 'is_featured', 
                 'comments_count', 'published_at', 'created_at', 'updated_at']
        
    def get_comments_count(self, obj):
        return obj.comments.filter(is_approved=True).count()
        
    def get_tags_list(self, obj):
        if obj.tags:
            return [tag.strip() for tag in obj.tags.split(',')]
        return []


class UserArticleDetailSerializer(UserArticleListSerializer):
    """Serializer detalhado para artigos"""
    comments = ArticleCommentSerializer(many=True, read_only=True)
    
    class Meta(UserArticleListSerializer.Meta):
        fields = UserArticleListSerializer.Meta.fields + ['content', 'comments']


class UserArticleCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação/edição de artigos"""
    
    class Meta:
        model = UserArticle
        fields = ['title', 'content', 'excerpt', 'category', 'status', 
                 'featured_image', 'tags', 'read_time', 'is_featured']
        
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class ArticleVoteSerializer(serializers.ModelSerializer):
    """Serializer para votos em artigos"""
    
    class Meta:
        model = ArticleVote
        fields = ['id', 'vote_type', 'created_at']
        read_only_fields = ['id', 'created_at']
