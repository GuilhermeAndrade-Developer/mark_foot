from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Poll(models.Model):
    """Enquetes/Polls"""
    POLL_STATUS = [
        ('draft', 'Rascunho'),
        ('active', 'Ativa'),
        ('closed', 'Fechada'),
        ('archived', 'Arquivada'),
    ]

    title = models.CharField(max_length=200, verbose_name="Título")
    slug = models.SlugField(unique=True, max_length=220, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Descrição")
    question = models.TextField(verbose_name="Pergunta")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Autor")
    status = models.CharField(max_length=20, choices=POLL_STATUS, default='draft', verbose_name="Status")
    featured_image = models.URLField(blank=True, verbose_name="Imagem Destacada")
    is_multiple_choice = models.BooleanField(default=False, verbose_name="Múltipla Escolha")
    is_anonymous = models.BooleanField(default=False, verbose_name="Votação Anônima")
    is_featured = models.BooleanField(default=False, verbose_name="Destacada")
    total_votes = models.PositiveIntegerField(default=0, verbose_name="Total de Votos")
    views = models.PositiveIntegerField(default=0, verbose_name="Visualizações")
    start_date = models.DateTimeField(null=True, blank=True, verbose_name="Data de Início")
    end_date = models.DateTimeField(null=True, blank=True, verbose_name="Data de Término")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Enquete"
        verbose_name_plural = "Enquetes"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        return self.status == 'active'

    @property
    def participation_rate(self):
        if self.views > 0:
            return round((self.total_votes / self.views) * 100, 2)
        return 0


class PollOption(models.Model):
    """Opções de uma enquete"""
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options', verbose_name="Enquete")
    text = models.CharField(max_length=200, verbose_name="Texto da Opção")
    description = models.TextField(blank=True, verbose_name="Descrição")
    image = models.URLField(blank=True, verbose_name="Imagem")
    votes = models.PositiveIntegerField(default=0, verbose_name="Votos")
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Porcentagem")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordem")
    is_active = models.BooleanField(default=True, verbose_name="Ativa")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        verbose_name = "Opção da Enquete"
        verbose_name_plural = "Opções das Enquetes"
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.poll.title} - {self.text}"

    def update_percentage(self):
        """Atualiza a porcentagem baseada no total de votos da enquete"""
        if self.poll.total_votes > 0:
            self.percentage = round((self.votes / self.poll.total_votes) * 100, 2)
        else:
            self.percentage = 0
        self.save(update_fields=['percentage'])


class PollVote(models.Model):
    """Votos em enquetes"""
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='poll_votes', verbose_name="Enquete")
    option = models.ForeignKey(PollOption, on_delete=models.CASCADE, related_name='option_votes', verbose_name="Opção")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Usuário")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Endereço IP")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        verbose_name = "Voto"
        verbose_name_plural = "Votos"
        ordering = ['-created_at']

    def __str__(self):
        if self.user:
            return f"{self.user.username} votou em {self.option.text}"
        return f"Voto anônimo em {self.option.text}"


class PollComment(models.Model):
    """Comentários em enquetes"""
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='comments', verbose_name="Enquete")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Autor")
    content = models.TextField(verbose_name="Conteúdo")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name="Comentário Pai")
    is_approved = models.BooleanField(default=True, verbose_name="Aprovado")
    likes = models.PositiveIntegerField(default=0, verbose_name="Curtidas")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Comentário da Enquete"
        verbose_name_plural = "Comentários das Enquetes"
        ordering = ['-created_at']

    def __str__(self):
        return f"Comentário de {self.author.username} em {self.poll.title}"
