import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.utils import timezone


class ForumCategory(models.Model):
    """Categorias dos fóruns (Times, Ligas, Discussões Gerais)"""
    
    CATEGORY_TYPES = [
        ('team', 'Time'),
        ('competition', 'Liga/Competição'),
        ('general', 'Discussão Geral'),
        ('news', 'Notícias'),
        ('analysis', 'Análises'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name='Nome')
    description = models.TextField(blank=True, verbose_name='Descrição')
    slug = models.SlugField(unique=True, max_length=100, verbose_name='Slug')
    category_type = models.CharField(
        max_length=20, 
        choices=CATEGORY_TYPES, 
        default='general',
        verbose_name='Tipo de Categoria'
    )
    
    # Referências opcionais para times e competições
    team_id = models.IntegerField(blank=True, null=True, verbose_name='ID do Time')
    competition_id = models.IntegerField(blank=True, null=True, verbose_name='ID da Competição')
    
    # Configurações da categoria
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    is_moderated = models.BooleanField(default=False, verbose_name='Moderado')
    
    # Metadados
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    # Contadores para performance
    topic_count = models.IntegerField(default=0, verbose_name='Total de Tópicos')
    post_count = models.IntegerField(default=0, verbose_name='Total de Posts')
    
    class Meta:
        verbose_name = 'Categoria do Fórum'
        verbose_name_plural = 'Categorias do Fórum'
        ordering = ['name']
        
    def __str__(self):
        return self.name
    
    def update_counters(self):
        """Atualiza contadores de tópicos e posts"""
        self.topic_count = self.topics.count()
        self.post_count = sum(topic.post_count for topic in self.topics.all())
        self.save(update_fields=['topic_count', 'post_count'])


class ForumTopic(models.Model):
    """Tópicos de discussão"""
    
    TOPIC_STATUS = [
        ('open', 'Aberto'),
        ('closed', 'Fechado'),
        ('pinned', 'Fixo'),
        ('locked', 'Bloqueado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        ForumCategory, 
        on_delete=models.CASCADE, 
        related_name='topics',
        verbose_name='Categoria'
    )
    
    # Conteúdo do tópico
    title = models.CharField(
        max_length=200, 
        validators=[MinLengthValidator(5)],
        verbose_name='Título'
    )
    slug = models.SlugField(max_length=200, verbose_name='Slug')
    content = models.TextField(verbose_name='Conteúdo')
    
    # Autor e moderação
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='forum_topics',
        verbose_name='Autor'
    )
    status = models.CharField(
        max_length=20, 
        choices=TOPIC_STATUS, 
        default='open',
        verbose_name='Status'
    )
    
    # Metadados
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    last_activity = models.DateTimeField(auto_now_add=True, verbose_name='Última Atividade')
    
    # Contadores
    view_count = models.IntegerField(default=0, verbose_name='Visualizações')
    post_count = models.IntegerField(default=0, verbose_name='Total de Posts')
    
    # Tags para busca
    tags = models.CharField(max_length=500, blank=True, verbose_name='Tags')
    
    class Meta:
        verbose_name = 'Tópico do Fórum'
        verbose_name_plural = 'Tópicos do Fórum'
        ordering = ['-last_activity']
        unique_together = [['category', 'slug']]
        
    def __str__(self):
        return self.title
    
    def increment_view_count(self):
        """Incrementa contador de visualizações"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def update_activity(self):
        """Atualiza timestamp da última atividade"""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])
    
    def update_post_count(self):
        """Atualiza contador de posts"""
        self.post_count = self.posts.count()
        self.save(update_fields=['post_count'])


class ForumPost(models.Model):
    """Posts/respostas nos tópicos"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    topic = models.ForeignKey(
        ForumTopic, 
        on_delete=models.CASCADE, 
        related_name='posts',
        verbose_name='Tópico'
    )
    
    # Conteúdo
    content = models.TextField(
        validators=[MinLengthValidator(10)],
        verbose_name='Conteúdo'
    )
    
    # Autor
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='forum_posts',
        verbose_name='Autor'
    )
    
    # Sistema de threading (respostas aninhadas)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True,
        related_name='replies',
        verbose_name='Post Pai'
    )
    
    # Metadados
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    is_edited = models.BooleanField(default=False, verbose_name='Editado')
    
    # Moderação
    is_deleted = models.BooleanField(default=False, verbose_name='Deletado')
    is_reported = models.BooleanField(default=False, verbose_name='Reportado')
    
    # Posição no tópico
    position = models.IntegerField(default=1, verbose_name='Posição')
    
    class Meta:
        verbose_name = 'Post do Fórum'
        verbose_name_plural = 'Posts do Fórum'
        ordering = ['created_at']
        
    def __str__(self):
        return f"Post de {self.author.username} em {self.topic.title}"
    
    def save(self, *args, **kwargs):
        # Definir posição se for um novo post
        if not self.pk:
            last_post = ForumPost.objects.filter(topic=self.topic).order_by('-position').first()
            self.position = (last_post.position + 1) if last_post else 1
        
        super().save(*args, **kwargs)
        
        # Atualizar contadores e atividade do tópico
        if not self.is_deleted:
            self.topic.update_post_count()
            self.topic.update_activity()
            self.topic.category.update_counters()


class ForumVote(models.Model):
    """Sistema de votação para posts"""
    
    VOTE_TYPES = [
        ('upvote', 'Positivo'),
        ('downvote', 'Negativo'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(
        ForumPost, 
        on_delete=models.CASCADE, 
        related_name='votes',
        verbose_name='Post'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='forum_votes',
        verbose_name='Usuário'
    )
    vote_type = models.CharField(
        max_length=10, 
        choices=VOTE_TYPES,
        verbose_name='Tipo de Voto'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    
    class Meta:
        verbose_name = 'Voto do Fórum'
        verbose_name_plural = 'Votos do Fórum'
        unique_together = [['post', 'user']]  # Um usuário só pode votar uma vez por post
        
    def __str__(self):
        return f"{self.user.username} - {self.vote_type} em post {self.post.id}"


class ForumUserProfile(models.Model):
    """Perfil estendido para usuários do fórum"""
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='forum_profile',
        verbose_name='Usuário'
    )
    
    # Estatísticas
    total_posts = models.IntegerField(default=0, verbose_name='Total de Posts')
    total_topics = models.IntegerField(default=0, verbose_name='Total de Tópicos')
    reputation_score = models.IntegerField(default=0, verbose_name='Pontuação de Reputação')
    
    # Configurações
    signature = models.TextField(
        max_length=500, 
        blank=True, 
        verbose_name='Assinatura'
    )
    receive_notifications = models.BooleanField(
        default=True, 
        verbose_name='Receber Notificações'
    )
    
    # Metadados
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name='Entrou em')
    last_seen = models.DateTimeField(auto_now=True, verbose_name='Visto por último')
    
    class Meta:
        verbose_name = 'Perfil do Usuário no Fórum'
        verbose_name_plural = 'Perfis dos Usuários no Fórum'
        
    def __str__(self):
        return f"Perfil de {self.user.username}"
    
    def update_stats(self):
        """Atualiza estatísticas do usuário"""
        self.total_posts = self.user.forum_posts.filter(is_deleted=False).count()
        self.total_topics = self.user.forum_topics.count()
        
        # Calcular reputação baseada em votos recebidos
        upvotes = ForumVote.objects.filter(
            post__author=self.user,
            vote_type='upvote'
        ).count()
        downvotes = ForumVote.objects.filter(
            post__author=self.user,
            vote_type='downvote'
        ).count()
        
        self.reputation_score = (upvotes * 2) - downvotes
        self.save(update_fields=['total_posts', 'total_topics', 'reputation_score'])
