from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import ForumCategory, ForumTopic, ForumPost, ForumVote, ForumUserProfile


class ForumModelTests(TestCase):
    """Testes para os modelos do fórum"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        self.category = ForumCategory.objects.create(
            name='Discussão Geral',
            slug='discussao-geral',
            description='Categoria para discussões gerais',
            category_type='general'
        )
        
        self.topic = ForumTopic.objects.create(
            category=self.category,
            title='Tópico de Teste',
            slug='topico-de-teste',
            content='Conteúdo do tópico de teste',
            author=self.user1
        )
    
    def test_category_creation(self):
        """Testa criação de categoria"""
        self.assertEqual(self.category.name, 'Discussão Geral')
        self.assertEqual(self.category.slug, 'discussao-geral')
        self.assertEqual(str(self.category), 'Discussão Geral')
    
    def test_topic_creation(self):
        """Testa criação de tópico"""
        self.assertEqual(self.topic.title, 'Tópico de Teste')
        self.assertEqual(self.topic.author, self.user1)
        self.assertEqual(self.topic.category, self.category)
        self.assertEqual(str(self.topic), 'Tópico de Teste')
    
    def test_post_creation(self):
        """Testa criação de post"""
        post = ForumPost.objects.create(
            topic=self.topic,
            content='Conteúdo do post de teste',
            author=self.user2
        )
        
        self.assertEqual(post.topic, self.topic)
        self.assertEqual(post.author, self.user2)
        self.assertEqual(post.position, 1)
        
        # Verificar se contadores foram atualizados
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.post_count, 1)
    
    def test_vote_creation(self):
        """Testa sistema de votação"""
        post = ForumPost.objects.create(
            topic=self.topic,
            content='Post para testar votação',
            author=self.user1
        )
        
        vote = ForumVote.objects.create(
            post=post,
            user=self.user2,
            vote_type='upvote'
        )
        
        self.assertEqual(vote.post, post)
        self.assertEqual(vote.user, self.user2)
        self.assertEqual(vote.vote_type, 'upvote')
    
    def test_user_profile_creation(self):
        """Testa criação de perfil de usuário"""
        profile = ForumUserProfile.objects.create(user=self.user1)
        
        self.assertEqual(profile.user, self.user1)
        self.assertEqual(profile.total_posts, 0)
        self.assertEqual(profile.reputation_score, 0)
    
    def test_topic_increment_view_count(self):
        """Testa incremento de visualizações"""
        initial_count = self.topic.view_count
        self.topic.increment_view_count()
        
        self.assertEqual(self.topic.view_count, initial_count + 1)
    
    def test_category_update_counters(self):
        """Testa atualização de contadores da categoria"""
        # Criar alguns posts
        post1 = ForumPost.objects.create(
            topic=self.topic,
            content='Post 1',
            author=self.user1
        )
        post2 = ForumPost.objects.create(
            topic=self.topic,
            content='Post 2',
            author=self.user2
        )
        
        self.category.update_counters()
        self.assertEqual(self.category.topic_count, 1)
        self.assertEqual(self.category.post_count, 2)


class ForumAPITests(APITestCase):
    """Testes para a API do fórum"""
    
    def setUp(self):
        """Configuração inicial para os testes da API"""
        self.user = User.objects.create_user(
            username='apiuser',
            email='api@example.com',
            password='apipass123'
        )
        
        self.category = ForumCategory.objects.create(
            name='API Test Category',
            slug='api-test-category',
            category_type='general'
        )
        
        self.topic = ForumTopic.objects.create(
            category=self.category,
            title='API Test Topic',
            slug='api-test-topic',
            content='Conteúdo para teste da API',
            author=self.user
        )
    
    def test_category_list(self):
        """Testa listagem de categorias"""
        url = reverse('forum:forum-category-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'API Test Category')
    
    def test_topic_list(self):
        """Testa listagem de tópicos"""
        url = reverse('forum:forum-topic-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'API Test Topic')
    
    def test_create_topic_requires_authentication(self):
        """Testa que criação de tópico requer autenticação"""
        url = reverse('forum:forum-topic-list')
        data = {
            'category_id': str(self.category.id),
            'title': 'Novo Tópico',
            'content': 'Conteúdo do novo tópico'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_topic_authenticated(self):
        """Testa criação de tópico autenticado"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('forum:forum-topic-list')
        data = {
            'category_id': str(self.category.id),
            'title': 'Novo Tópico Autenticado',
            'content': 'Conteúdo do novo tópico',
            'slug': 'novo-topico-autenticado'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Novo Tópico Autenticado')
    
    def test_create_post(self):
        """Testa criação de post"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('forum:forum-post-list')
        data = {
            'topic': str(self.topic.id),
            'content': 'Conteúdo do novo post'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'Conteúdo do novo post')
    
    def test_vote_on_post(self):
        """Testa votação em post"""
        # Criar um post
        post = ForumPost.objects.create(
            topic=self.topic,
            content='Post para votar',
            author=self.user
        )
        
        # Criar outro usuário para votar
        voter = User.objects.create_user(
            username='voter',
            password='voterpass123'
        )
        self.client.force_authenticate(user=voter)
        
        url = reverse('forum:forum-post-vote', kwargs={'pk': post.id})
        data = {'vote_type': 'upvote'}
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['vote_type'], 'upvote')
        self.assertEqual(response.data['score'], 1)
    
    def test_cannot_vote_own_post(self):
        """Testa que não é possível votar no próprio post"""
        post = ForumPost.objects.create(
            topic=self.topic,
            content='Meu próprio post',
            author=self.user
        )
        
        self.client.force_authenticate(user=self.user)
        
        url = reverse('forum:forum-post-vote', kwargs={'pk': post.id})
        data = {'vote_type': 'upvote'}
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Não é possível votar no próprio post', response.data['error'])
    
    def test_forum_stats(self):
        """Testa endpoint de estatísticas"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('forum:forum-stats-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_categories', response.data)
        self.assertIn('total_topics', response.data)
        self.assertIn('total_posts', response.data)
    
    def test_forum_search(self):
        """Testa busca no fórum"""
        url = reverse('forum:forum-search-list')
        params = {'query': 'API Test'}
        
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('topics', response.data)
        self.assertIn('posts', response.data)
        self.assertEqual(len(response.data['topics']), 1)


class ForumIntegrationTests(TestCase):
    """Testes de integração do fórum"""
    
    def setUp(self):
        """Configuração para testes de integração"""
        self.user1 = User.objects.create_user(
            username='user1',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='pass123'
        )
        
        self.category = ForumCategory.objects.create(
            name='Integração',
            slug='integracao',
            category_type='general'
        )
    
    def test_full_forum_workflow(self):
        """Testa workflow completo do fórum"""
        # 1. Criar tópico
        topic = ForumTopic.objects.create(
            category=self.category,
            title='Workflow Test',
            slug='workflow-test',
            content='Tópico para teste de workflow',
            author=self.user1
        )
        
        # 2. Criar posts
        post1 = ForumPost.objects.create(
            topic=topic,
            content='Primeiro post',
            author=self.user2
        )
        
        post2 = ForumPost.objects.create(
            topic=topic,
            content='Segundo post',
            author=self.user1
        )
        
        # 3. Votar nos posts
        ForumVote.objects.create(
            post=post1,
            user=self.user1,
            vote_type='upvote'
        )
        
        ForumVote.objects.create(
            post=post2,
            user=self.user2,
            vote_type='downvote'
        )
        
        # 4. Verificar contadores
        topic.refresh_from_db()
        self.category.refresh_from_db()
        
        self.assertEqual(topic.post_count, 2)
        self.assertEqual(self.category.topic_count, 1)
        self.assertEqual(self.category.post_count, 2)
        
        # 5. Verificar scores de votos
        post1_score = (post1.votes.filter(vote_type='upvote').count() - 
                      post1.votes.filter(vote_type='downvote').count())
        post2_score = (post2.votes.filter(vote_type='upvote').count() - 
                      post2.votes.filter(vote_type='downvote').count())
        
        self.assertEqual(post1_score, 1)
        self.assertEqual(post2_score, -1)
