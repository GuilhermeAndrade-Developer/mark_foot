from django.contrib import admin
from .models import Poll, PollOption, PollVote, PollComment


class PollOptionInline(admin.TabularInline):
    model = PollOption
    extra = 2
    fields = ['text', 'description', 'image', 'order', 'is_active']


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'total_votes', 'views', 'created_at']
    list_filter = ['status', 'is_multiple_choice', 'is_anonymous', 'is_featured', 'created_at']
    search_fields = ['title', 'description', 'question', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['total_votes', 'views', 'participation_rate', 'created_at', 'updated_at']
    raw_id_fields = ['author']
    inlines = [PollOptionInline]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('title', 'slug', 'author', 'question', 'description')
        }),
        ('Configurações', {
            'fields': ('status', 'is_multiple_choice', 'is_anonymous', 'is_featured', 'featured_image')
        }),
        ('Período', {
            'fields': ('start_date', 'end_date')
        }),
        ('Estatísticas', {
            'fields': ('total_votes', 'views', 'participation_rate'),
            'classes': ('collapse',)
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PollOption)
class PollOptionAdmin(admin.ModelAdmin):
    list_display = ['poll', 'text', 'votes', 'percentage', 'order', 'is_active']
    list_filter = ['is_active', 'poll__status']
    search_fields = ['text', 'description', 'poll__title']
    raw_id_fields = ['poll']


@admin.register(PollVote)
class PollVoteAdmin(admin.ModelAdmin):
    list_display = ['poll', 'option', 'user', 'ip_address', 'created_at']
    list_filter = ['created_at', 'poll__status']
    search_fields = ['user__username', 'poll__title', 'option__text']
    raw_id_fields = ['user', 'poll', 'option']


@admin.register(PollComment)
class PollCommentAdmin(admin.ModelAdmin):
    list_display = ['poll', 'author', 'is_approved', 'likes', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['content', 'author__username', 'poll__title']
    raw_id_fields = ['author', 'poll', 'parent']
