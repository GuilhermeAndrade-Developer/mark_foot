from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import ForumCategory, ForumTopic, ForumPost, ForumVote, ForumUserProfile


@admin.register(ForumCategory)
class ForumCategoryAdmin(admin.ModelAdmin):
    """Admin para categorias do fórum"""
    list_display = [
        'name', 'category_type', 'topic_count', 'post_count', 
        'is_active', 'is_moderated', 'created_at'
    ]
    list_filter = ['category_type', 'is_active', 'is_moderated', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['topic_count', 'post_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'slug', 'description', 'category_type')
        }),
        ('Configurações', {
            'fields': ('is_active', 'is_moderated')
        }),
        ('Referências', {
            'fields': ('team_id', 'competition_id'),
            'classes': ('collapse',)
        }),
        ('Estatísticas', {
            'fields': ('topic_count', 'post_count'),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(ForumTopic)
class ForumTopicAdmin(admin.ModelAdmin):
    """Admin para tópicos do fórum"""
    list_display = [
        'title', 'category_name', 'author_name', 'status', 
        'post_count', 'view_count', 'created_at'
    ]
    list_filter = ['status', 'category', 'created_at', 'last_activity']
    search_fields = ['title', 'content', 'author__username']
    readonly_fields = [
        'slug', 'post_count', 'view_count', 'last_activity', 
        'created_at', 'updated_at'
    ]
    raw_id_fields = ['author']
    
    fieldsets = (
        ('Conteúdo', {
            'fields': ('category', 'title', 'slug', 'content', 'tags')
        }),
        ('Autor e Status', {
            'fields': ('author', 'status')
        }),
        ('Estatísticas', {
            'fields': ('post_count', 'view_count', 'last_activity'),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def category_name(self, obj):
        return obj.category.name
    category_name.short_description = 'Categoria'
    
    def author_name(self, obj):
        return obj.author.username
    author_name.short_description = 'Autor'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'author')


@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    """Admin para posts do fórum"""
    list_display = [
        'post_preview', 'topic_title', 'author_name', 'position',
        'vote_score', 'is_edited', 'is_reported', 'created_at'
    ]
    list_filter = [
        'is_edited', 'is_deleted', 'is_reported', 
        'created_at', 'topic__category'
    ]
    search_fields = ['content', 'author__username', 'topic__title']
    readonly_fields = [
        'position', 'vote_score', 'created_at', 'updated_at'
    ]
    raw_id_fields = ['author', 'topic', 'parent']
    
    fieldsets = (
        ('Conteúdo', {
            'fields': ('topic', 'content', 'parent')
        }),
        ('Autor e Status', {
            'fields': ('author', 'is_edited', 'is_deleted', 'is_reported')
        }),
        ('Estatísticas', {
            'fields': ('position', 'vote_score'),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def post_preview(self, obj):
        """Mostra prévia do post"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    post_preview.short_description = 'Prévia do Post'
    
    def topic_title(self, obj):
        """Link para o tópico"""
        url = reverse('admin:forum_forumtopic_change', args=[obj.topic.pk])
        return format_html('<a href="{}">{}</a>', url, obj.topic.title)
    topic_title.short_description = 'Tópico'
    
    def author_name(self, obj):
        return obj.author.username
    author_name.short_description = 'Autor'
    
    def vote_score(self, obj):
        """Calcula e mostra score de votos"""
        upvotes = obj.votes.filter(vote_type='upvote').count()
        downvotes = obj.votes.filter(vote_type='downvote').count()
        score = upvotes - downvotes
        
        color = 'green' if score > 0 else 'red' if score < 0 else 'black'
        return format_html(
            '<span style="color: {};">{} (+{} / -{})</span>',
            color, score, upvotes, downvotes
        )
    vote_score.short_description = 'Score de Votos'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('topic', 'author')


@admin.register(ForumVote)
class ForumVoteAdmin(admin.ModelAdmin):
    """Admin para votos do fórum"""
    list_display = [
        'user_name', 'post_preview', 'vote_type', 'created_at'
    ]
    list_filter = ['vote_type', 'created_at']
    search_fields = ['user__username', 'post__content']
    readonly_fields = ['created_at']
    raw_id_fields = ['user', 'post']
    
    def user_name(self, obj):
        return obj.user.username
    user_name.short_description = 'Usuário'
    
    def post_preview(self, obj):
        """Mostra prévia do post votado"""
        content = obj.post.content[:30] + '...' if len(obj.post.content) > 30 else obj.post.content
        url = reverse('admin:forum_forumpost_change', args=[obj.post.pk])
        return format_html('<a href="{}">{}</a>', url, content)
    post_preview.short_description = 'Post'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'post')


@admin.register(ForumUserProfile)
class ForumUserProfileAdmin(admin.ModelAdmin):
    """Admin para perfis de usuário do fórum"""
    list_display = [
        'user_name', 'total_posts', 'total_topics', 
        'reputation_score', 'last_seen'
    ]
    list_filter = ['receive_notifications', 'joined_at', 'last_seen']
    search_fields = ['user__username', 'user__email']
    readonly_fields = [
        'total_posts', 'total_topics', 'reputation_score',
        'joined_at', 'last_seen'
    ]
    raw_id_fields = ['user']
    
    fieldsets = (
        ('Usuário', {
            'fields': ('user',)
        }),
        ('Estatísticas', {
            'fields': ('total_posts', 'total_topics', 'reputation_score')
        }),
        ('Configurações', {
            'fields': ('signature', 'receive_notifications')
        }),
        ('Metadados', {
            'fields': ('joined_at', 'last_seen'),
            'classes': ('collapse',)
        }),
    )
    
    def user_name(self, obj):
        return obj.user.username
    user_name.short_description = 'Usuário'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


# Customização do admin site
admin.site.site_header = "Mark Foot - Administração do Fórum"
admin.site.site_title = "Fórum Admin"
admin.site.index_title = "Administração do Sistema de Fóruns"
