from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class ContentCategory(models.Model):
    """Categorias para conteúdo gerado por usuário"""
    name = models.CharField(max_length=100, verbose_name="Nome")
    slug = models.SlugField(unique=True, max_length=120, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Descrição")
    icon = models.CharField(max_length=50, default="mdi-folder", verbose_name="Ícone")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Categoria de Conteúdo"
        verbose_name_plural = "Categorias de Conteúdo"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class UserArticle(models.Model):
    """Artigos criados por usuários"""
    ARTICLE_STATUS = [
        ('draft', 'Rascunho'),
        ('pending', 'Aguardando Moderação'),
        ('published', 'Publicado'),
        ('rejected', 'Rejeitado'),
        ('archived', 'Arquivado'),
    ]

    title = models.CharField(max_length=200, verbose_name="Título")
    slug = models.SlugField(unique=True, max_length=220, verbose_name="Slug")
    content = models.TextField(verbose_name="Conteúdo")
    excerpt = models.TextField(max_length=500, blank=True, verbose_name="Resumo")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Autor")
    category = models.ForeignKey(ContentCategory, on_delete=models.CASCADE, verbose_name="Categoria")
    status = models.CharField(max_length=20, choices=ARTICLE_STATUS, default='draft', verbose_name="Status")
    featured_image = models.URLField(blank=True, verbose_name="Imagem Destacada")
    tags = models.CharField(max_length=200, blank=True, verbose_name="Tags")
    read_time = models.PositiveIntegerField(default=5, verbose_name="Tempo de Leitura (min)")
    views = models.PositiveIntegerField(default=0, verbose_name="Visualizações")
    likes = models.PositiveIntegerField(default=0, verbose_name="Curtidas")
    dislikes = models.PositiveIntegerField(default=0, verbose_name="Descurtidas")
    is_featured = models.BooleanField(default=False, verbose_name="Destacado")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Publicado em")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Artigo"
        verbose_name_plural = "Artigos"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def vote_score(self):
        return self.likes - self.dislikes


class ArticleComment(models.Model):
    """Comentários em artigos"""
    article = models.ForeignKey(UserArticle, on_delete=models.CASCADE, related_name='comments', verbose_name="Artigo")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Autor")
    content = models.TextField(verbose_name="Conteúdo")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name="Comentário Pai")
    is_approved = models.BooleanField(default=True, verbose_name="Aprovado")
    likes = models.PositiveIntegerField(default=0, verbose_name="Curtidas")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Comentário"
        verbose_name_plural = "Comentários"
        ordering = ['-created_at']

    def __str__(self):
        return f"Comentário de {self.author.username} em {self.article.title}"


class ArticleVote(models.Model):
    """Votos em artigos (like/dislike)"""
    VOTE_TYPES = [
        ('like', 'Curtir'),
        ('dislike', 'Descurtir'),
    ]

    article = models.ForeignKey(UserArticle, on_delete=models.CASCADE, related_name='votes', verbose_name="Artigo")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    vote_type = models.CharField(max_length=10, choices=VOTE_TYPES, verbose_name="Tipo de Voto")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        verbose_name = "Voto do Artigo"
        verbose_name_plural = "Votos dos Artigos"
        unique_together = ['article', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.vote_type} - {self.article.title}"
