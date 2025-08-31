"""
Seeder for forum module data.
Creates professional development data for forum discussions.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from forum.models import Category, Topic, Post as ForumPost
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Seed forum data for development'

    def handle(self, *args, **options):
        self.stdout.write('💬 Seeding forum data...')
        
        # Create categories
        categories_created = self.create_categories()
        
        # Create topics and posts
        topics_created = self.create_topics()

        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Forum data seeded:\n'
                f'   📂 Categories: {categories_created}\n'
                f'   💬 Topics: {topics_created}'
            )
        )

    def create_categories(self):
        """Create forum categories"""
        categories_data = [
            {
                'name': 'Discussão Geral',
                'description': 'Discussões gerais sobre futebol',
                'icon': 'mdi-forum',
                'color': '#2196F3',
                'is_active': True,
                'order': 1
            },
            {
                'name': 'Brasileirão',
                'description': 'Tudo sobre o Campeonato Brasileiro',
                'icon': 'mdi-flag',
                'color': '#4CAF50',
                'is_active': True,
                'order': 2
            },
            {
                'name': 'Futebol Internacional',
                'description': 'Discussões sobre futebol mundial',
                'icon': 'mdi-earth',
                'color': '#FF9800',
                'is_active': True,
                'order': 3
            },
            {
                'name': 'Análises Táticas',
                'description': 'Análises técnicas e táticas profundas',
                'icon': 'mdi-strategy',
                'color': '#9C27B0',
                'is_active': True,
                'order': 4
            },
            {
                'name': 'Fantasy Football',
                'description': 'Discussões sobre fantasy e cartola',
                'icon': 'mdi-trophy',
                'color': '#FFC107',
                'is_active': True,
                'order': 5
            }
        ]

        created_count = 0
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                created_count += 1

        return created_count

    def create_topics(self):
        """Create forum topics and posts"""
        users = list(User.objects.filter(is_active=True))
        categories = Category.objects.filter(is_active=True)
        
        if not users or not categories.exists():
            return 0

        topics_data = [
            {
                'title': 'Qual time vai ganhar o Brasileirão 2024?',
                'category': 'Brasileirão',
                'content': 'Estamos na metade do campeonato e ainda é difícil dizer quem vai levar o título. O que vocês acham?'
            },
            {
                'title': 'Análise: Por que o 4-3-3 está dominando?',
                'category': 'Análises Táticas',
                'content': 'Tenho notado que muitos times estão usando o 4-3-3. Vamos discutir as vantagens desta formação.'
            },
            {
                'title': 'Champions League: Brasileiros se destacando',
                'category': 'Futebol Internacional',
                'content': 'Varios brasileiros estão brilhando na Champions. Quais vocês acham que mais se destacam?'
            },
            {
                'title': 'Dicas para o Fantasy desta rodada',
                'category': 'Fantasy Football',
                'content': 'Quais jogadores vocês estão escalando para esta rodada? Vamos trocar dicas!'
            },
            {
                'title': 'VAR está funcionando no Brasil?',
                'category': 'Discussão Geral',
                'content': 'Muito se discute sobre o VAR. Na opinião de vocês, está ajudando ou atrapalhando?'
            },
            {
                'title': 'Melhor atacante do Brasileirão atualmente',
                'category': 'Brasileirão',
                'content': 'Considerando números e performance, quem vocês elegem como melhor atacante da temporada?'
            },
            {
                'title': 'Como melhorar a arbitragem brasileira?',
                'category': 'Discussão Geral',
                'content': 'Quais medidas vocês sugerem para melhorar a qualidade da arbitragem no Brasil?'
            },
            {
                'title': 'Análise: Pressão alta vs Posse de bola',
                'category': 'Análises Táticas',
                'content': 'Duas filosofias diferentes. Qual vocês acham mais efetiva no futebol atual?'
            }
        ]

        created_count = 0
        
        for topic_data in topics_data:
            try:
                category = categories.get(name=topic_data['category'])
                author = random.choice(users)
                
                # Create topic
                topic, created = Topic.objects.get_or_create(
                    title=topic_data['title'],
                    defaults={
                        'category': category,
                        'author': author,
                        'created_at': timezone.now() - timedelta(days=random.randint(1, 30)),
                        'is_pinned': random.choice([True, False]) if random.random() < 0.2 else False,
                        'is_locked': False,
                        'views': random.randint(50, 500)
                    }
                )
                
                if created:
                    created_count += 1
                    
                    # Create initial post
                    ForumPost.objects.create(
                        topic=topic,
                        author=author,
                        content=topic_data['content'],
                        created_at=topic.created_at,
                        is_first_post=True
                    )
                    
                    # Create replies
                    reply_count = random.randint(2, 8)
                    replies = [
                        "Concordo totalmente com sua análise!",
                        "Interessante ponto de vista, mas discordo em alguns pontos.",
                        "Excelente discussão! Vou acompanhar.",
                        "Ótima análise técnica!",
                        "Pensamento muito coerente!",
                        "Dados interessantes, obrigado por compartilhar!",
                        "Não havia pensado por esse ângulo!",
                        "Análise muito profunda, parabéns!"
                    ]
                    
                    for i in range(reply_count):
                        reply_author = random.choice(users)
                        reply_content = random.choice(replies)
                        
                        ForumPost.objects.create(
                            topic=topic,
                            author=reply_author,
                            content=reply_content,
                            created_at=topic.created_at + timedelta(hours=random.randint(1, 48)),
                            is_first_post=False
                        )
                    
                    # Update topic stats
                    topic.post_count = ForumPost.objects.filter(topic=topic).count()
                    topic.last_post_at = ForumPost.objects.filter(topic=topic).latest('created_at').created_at
                    topic.save()

            except Category.DoesNotExist:
                continue

        return created_count
