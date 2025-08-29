from django.contrib import admin
from .models import ContentCategory, UserArticle, ArticleComment, ArticleVote


@admin.register(ContentCategory)
class ContentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserArticle)
class UserArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'views', 'likes', 'created_at']
    list_filter = ['status', 'category', 'is_featured', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views', 'likes', 'dislikes', 'created_at', 'updated_at']
    raw_id_fields = ['author']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('title', 'slug', 'author', 'category')
        }),
        ('Conteúdo', {
            'fields': ('content', 'excerpt', 'featured_image', 'tags')
        }),
        ('Configurações', {
            'fields': ('status', 'is_featured', 'read_time')
        }),
        ('Estatísticas', {
            'fields': ('views', 'likes', 'dislikes'),
            'classes': ('collapse',)
        }),
        ('Datas', {
            'fields': ('published_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ArticleComment)
class ArticleCommentAdmin(admin.ModelAdmin):
    list_display = ['article', 'author', 'is_approved', 'likes', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['content', 'author__username', 'article__title']
    raw_id_fields = ['author', 'article', 'parent']


@admin.register(ArticleVote)
class ArticleVoteAdmin(admin.ModelAdmin):
    list_display = ['article', 'user', 'vote_type', 'created_at']
    list_filter = ['vote_type', 'created_at']
    search_fields = ['user__username', 'article__title']
    raw_id_fields = ['user', 'article']
