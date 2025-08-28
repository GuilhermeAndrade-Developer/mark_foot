from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count, F
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.shortcuts import get_object_or_404

from .models import ForumCategory, ForumTopic, ForumPost, ForumVote, ForumUserProfile
from .serializers import (
    ForumCategorySerializer, ForumCategoryDetailSerializer,
    ForumTopicListSerializer, ForumTopicSerializer,
    ForumPostSerializer, ForumPostCreateSerializer,
    ForumVoteSerializer, ForumUserProfileSerializer,
    ForumStatsSerializer, ForumSearchSerializer
)


class ForumCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet para categorias do fórum"""
    queryset = ForumCategory.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ForumCategoryDetailSerializer
        return ForumCategorySerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category_type = self.request.query_params.get('type')
        
        if category_type:
            queryset = queryset.filter(category_type=category_type)
        
        return queryset.order_by('name')
    
    @action(detail=True, methods=['get'])
    def topics(self, request, slug=None):
        """Lista tópicos de uma categoria específica"""
        category = self.get_object()
        topics = category.topics.filter(status='open')
        
        # Filtros
        search = request.query_params.get('search')
        if search:
            topics = topics.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(tags__icontains=search)
            )
        
        # Ordenação
        sort_by = request.query_params.get('sort', 'last_activity')
        if sort_by == 'latest':
            topics = topics.order_by('-created_at')
        elif sort_by == 'popular':
            topics = topics.order_by('-view_count')
        elif sort_by == 'posts':
            topics = topics.order_by('-post_count')
        else:
            topics = topics.order_by('-last_activity')
        
        page = self.paginate_queryset(topics)
        if page is not None:
            serializer = ForumTopicListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ForumTopicListSerializer(topics, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estatísticas das categorias"""
        categories = self.get_queryset().annotate(
            topic_count=Count('topics'),
            post_count=Count('topics__posts')
        )
        
        data = []
        for category in categories:
            data.append({
                'id': category.id,
                'name': category.name,
                'type': category.category_type,
                'topic_count': category.topic_count,
                'post_count': category.post_count
            })
        
        return Response(data)


class ForumTopicViewSet(viewsets.ModelViewSet):
    """ViewSet para tópicos do fórum"""
    queryset = ForumTopic.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ForumTopicSerializer
        return ForumTopicListSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author__username=author)
        
        status_filter = self.request.query_params.get('status', 'open')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-last_activity')
    
    def perform_create(self, serializer):
        """Cria tópico e gera slug automaticamente"""
        topic = serializer.save(author=self.request.user)
        if not topic.slug:
            topic.slug = slugify(topic.title)
            topic.save()
    
    def retrieve(self, request, *args, **kwargs):
        """Recupera tópico e incrementa contador de visualizações"""
        instance = self.get_object()
        instance.increment_view_count()
        
        serializer = ForumTopicSerializer(instance, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def posts(self, request, slug=None):
        """Lista posts de um tópico específico"""
        topic = self.get_object()
        posts = topic.posts.filter(is_deleted=False).select_related('author')
        
        # Filtros
        parent_only = request.query_params.get('parent_only', 'false').lower() == 'true'
        if parent_only:
            posts = posts.filter(parent__isnull=True)
        
        # Ordenação
        sort_by = request.query_params.get('sort', 'created_at')
        if sort_by == 'votes':
            posts = posts.annotate(
                vote_score=Count('votes', filter=Q(votes__vote_type='upvote')) -
                          Count('votes', filter=Q(votes__vote_type='downvote'))
            ).order_by('-vote_score')
        else:
            posts = posts.order_by('created_at')
        
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = ForumPostSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ForumPostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def close(self, request, slug=None):
        """Fecha um tópico"""
        topic = self.get_object()
        
        # Verificar permissões (autor ou admin)
        if topic.author != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Sem permissão para fechar este tópico'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        topic.status = 'closed'
        topic.save()
        
        return Response({'message': 'Tópico fechado com sucesso'})
    
    @action(detail=True, methods=['post'])
    def pin(self, request, slug=None):
        """Fixa um tópico (apenas staff)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Apenas moderadores podem fixar tópicos'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        topic = self.get_object()
        topic.status = 'pinned'
        topic.save()
        
        return Response({'message': 'Tópico fixado com sucesso'})


class ForumPostViewSet(viewsets.ModelViewSet):
    """ViewSet para posts do fórum"""
    queryset = ForumPost.objects.filter(is_deleted=False)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action in ['create']:
            return ForumPostCreateSerializer
        return ForumPostSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('author', 'topic')
        
        # Filtros
        topic_slug = self.request.query_params.get('topic')
        if topic_slug:
            queryset = queryset.filter(topic__slug=topic_slug)
        
        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author__username=author)
        
        return queryset.order_by('created_at')
    
    def perform_create(self, serializer):
        """Cria post e atualiza contadores"""
        post = serializer.save(author=self.request.user)
        
        # Atualizar contadores do tópico
        post.topic.update_post_count()
        post.topic.update_activity()
    
    def perform_update(self, serializer):
        """Atualiza post e marca como editado"""
        serializer.save(is_edited=True)
    
    @action(detail=True, methods=['post'])
    def vote(self, request, pk=None):
        """Sistema de votação para posts"""
        post = self.get_object()
        vote_type = request.data.get('vote_type')
        
        if vote_type not in ['upvote', 'downvote']:
            return Response(
                {'error': 'Tipo de voto inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Não permitir voto no próprio post
        if post.author == request.user:
            return Response(
                {'error': 'Não é possível votar no próprio post'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Criar ou atualizar voto
        vote_data = {'post': post.id, 'vote_type': vote_type}
        serializer = ForumVoteSerializer(data=vote_data, context={'request': request})
        
        if serializer.is_valid():
            vote = serializer.save()
            
            # Calcular novo score
            upvotes = post.votes.filter(vote_type='upvote').count()
            downvotes = post.votes.filter(vote_type='downvote').count()
            score = upvotes - downvotes
            
            return Response({
                'vote_type': vote.vote_type if vote else None,
                'score': score,
                'message': 'Voto registrado com sucesso'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def replies(self, request, pk=None):
        """Lista respostas de um post"""
        post = self.get_object()
        replies = post.replies.filter(is_deleted=False).order_by('created_at')
        
        serializer = ForumPostSerializer(replies, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def report(self, request, pk=None):
        """Reporta um post"""
        post = self.get_object()
        
        # Não permitir reportar próprio post
        if post.author == request.user:
            return Response(
                {'error': 'Não é possível reportar o próprio post'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        post.is_reported = True
        post.save()
        
        return Response({'message': 'Post reportado com sucesso'})


class ForumStatsViewSet(viewsets.ViewSet):
    """ViewSet para estatísticas do fórum"""
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        """Retorna estatísticas gerais do fórum"""
        stats = {
            'total_categories': ForumCategory.objects.filter(is_active=True).count(),
            'total_topics': ForumTopic.objects.count(),
            'total_posts': ForumPost.objects.filter(is_deleted=False).count(),
            'total_users': User.objects.filter(forum_posts__isnull=False).distinct().count(),
        }
        
        # Categoria mais ativa
        most_active_category = ForumCategory.objects.annotate(
            total_posts=Count('topics__posts')
        ).order_by('-total_posts').first()
        
        stats['most_active_category'] = most_active_category.name if most_active_category else None
        
        # Usuário mais ativo
        most_active_user = User.objects.annotate(
            total_posts=Count('forum_posts', filter=Q(forum_posts__is_deleted=False))
        ).order_by('-total_posts').first()
        
        stats['most_active_user'] = most_active_user.username if most_active_user else None
        
        # Atividade recente
        recent_posts = ForumPost.objects.filter(
            is_deleted=False
        ).select_related('author', 'topic').order_by('-created_at')[:10]
        
        stats['recent_activity'] = [
            {
                'id': post.id,
                'author': post.author.username,
                'topic_title': post.topic.title,
                'topic_slug': post.topic.slug,
                'created_at': post.created_at
            }
            for post in recent_posts
        ]
        
        serializer = ForumStatsSerializer(stats)
        return Response(serializer.data)


class ForumSearchViewSet(viewsets.ViewSet):
    """ViewSet para busca no fórum"""
    permission_classes = [permissions.AllowAny]
    
    def list(self, request):
        """Realiza busca no fórum"""
        serializer = ForumSearchSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        query = data['query']
        
        # Buscar em tópicos
        topics = ForumTopic.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(tags__icontains=query)
        )
        
        # Buscar em posts
        posts = ForumPost.objects.filter(
            Q(content__icontains=query),
            is_deleted=False
        )
        
        # Aplicar filtros adicionais
        if 'category' in data:
            topics = topics.filter(category_id=data['category'])
            posts = posts.filter(topic__category_id=data['category'])
        
        if 'author' in data:
            topics = topics.filter(author__username=data['author'])
            posts = posts.filter(author__username=data['author'])
        
        if 'date_from' in data:
            topics = topics.filter(created_at__gte=data['date_from'])
            posts = posts.filter(created_at__gte=data['date_from'])
        
        if 'date_to' in data:
            topics = topics.filter(created_at__lte=data['date_to'])
            posts = posts.filter(created_at__lte=data['date_to'])
        
        # Ordenação
        sort_by = data.get('sort_by', 'relevance')
        if sort_by == 'date':
            topics = topics.order_by('-created_at')
            posts = posts.order_by('-created_at')
        elif sort_by == 'votes':
            posts = posts.annotate(
                vote_score=Count('votes', filter=Q(votes__vote_type='upvote')) -
                          Count('votes', filter=Q(votes__vote_type='downvote'))
            ).order_by('-vote_score')
        
        # Serializar resultados
        topic_serializer = ForumTopicListSerializer(topics[:20], many=True, context={'request': request})
        post_serializer = ForumPostSerializer(posts[:20], many=True, context={'request': request})
        
        return Response({
            'topics': topic_serializer.data,
            'posts': post_serializer.data,
            'total_topics': topics.count(),
            'total_posts': posts.count()
        })


class ForumUserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para perfis de usuários do fórum"""
    queryset = ForumUserProfile.objects.all()
    serializer_class = ForumUserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'user__username'
    
    @action(detail=True, methods=['get'])
    def activity(self, request, user__username=None):
        """Retorna atividade recente do usuário"""
        profile = self.get_object()
        user = profile.user
        
        # Posts recentes
        recent_posts = user.forum_posts.filter(
            is_deleted=False
        ).select_related('topic').order_by('-created_at')[:10]
        
        # Tópicos recentes
        recent_topics = user.forum_topics.order_by('-created_at')[:10]
        
        return Response({
            'recent_posts': ForumPostSerializer(recent_posts, many=True, context={'request': request}).data,
            'recent_topics': ForumTopicListSerializer(recent_topics, many=True, context={'request': request}).data
        })
