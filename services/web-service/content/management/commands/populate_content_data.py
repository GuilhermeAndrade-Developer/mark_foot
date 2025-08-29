from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from content.models import ContentCategory, UserArticle
from polls.models import Poll, PollOption
import random


class Command(BaseCommand):
    help = 'Popula o banco de dados com dados de demonstração para Content e Polls'

    def handle(self, *args, **options):
        self.stdout.write('Populando dados de demonstração...')
        
        # Criar usuário de demonstração se não existir
        demo_user, created = User.objects.get_or_create(
            username='demo_user',
            defaults={
                'email': 'demo@markfoot.com',
                'first_name': 'Demo',
                'last_name': 'User',
                'is_staff': False,
                'is_active': True
            }
        )
        
        # Criar categorias de conteúdo
        categories_data = [
            {'name': 'Análises Táticas', 'icon': 'mdi-strategy', 'description': 'Análises detalhadas de jogos e formações'},
            {'name': 'Mercado da Bola', 'icon': 'mdi-cash-multiple', 'description': 'Transferências e mercado de jogadores'},
            {'name': 'História do Futebol', 'icon': 'mdi-book-open-variant', 'description': 'Fatos históricos e curiosidades'},
            {'name': 'Estatísticas', 'icon': 'mdi-chart-bar', 'description': 'Dados e números do futebol'},
            {'name': 'Opinião', 'icon': 'mdi-comment-text', 'description': 'Artigos de opinião e análises'},
            {'name': 'Entrevistas', 'icon': 'mdi-microphone', 'description': 'Entrevistas exclusivas'},
        ]
        
        for cat_data in categories_data:
            category, created = ContentCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'Categoria criada: {category.name}')
        
        # Criar artigos de demonstração
        articles_data = [
            {
                'title': 'Análise Tática: Como o Barcelona Dominou o El Clásico',
                'content': 'Uma análise detalhada da vitória do Barcelona no último El Clásico...',
                'excerpt': 'Análise completa da vitória histórica do Barcelona',
                'category': 'Análises Táticas',
                'tags': 'barcelona, real madrid, el clasico, tatica',
                'views': random.randint(5000, 15000),
                'likes': random.randint(100, 1000),
                'status': 'published'
            },
            {
                'title': 'Mercado da Bola: Os 10 Maiores Transfers do Verão',
                'content': 'Confira as principais transferências da janela de verão...',
                'excerpt': 'Lista completa das maiores contratações',
                'category': 'Mercado da Bola',
                'tags': 'transferencias, mercado, summer window',
                'views': random.randint(3000, 12000),
                'likes': random.randint(50, 800),
                'status': 'published'
            },
            {
                'title': 'A Evolução do Futebol Brasileiro nos Últimos 20 Anos',
                'content': 'Como o futebol brasileiro mudou nas últimas duas décadas...',
                'excerpt': 'Retrospectiva completa do futebol nacional',
                'category': 'História do Futebol',
                'tags': 'brasil, historia, evolucao, futebol brasileiro',
                'views': random.randint(2000, 8000),
                'likes': random.randint(200, 700),
                'status': 'published'
            },
            {
                'title': 'Estatísticas: Qual é o Melhor Atacante da Europa?',
                'content': 'Análise estatística dos principais atacantes europeus...',
                'excerpt': 'Números não mentem: a verdade sobre os atacantes',
                'category': 'Estatísticas',
                'tags': 'estatisticas, atacantes, europa, numeros',
                'views': random.randint(4000, 10000),
                'likes': random.randint(150, 600),
                'status': 'published'
            },
            {
                'title': 'Por que o VAR Ainda é Controverso?',
                'content': 'Uma opinião sobre os prós e contras do VAR no futebol moderno...',
                'excerpt': 'Reflexão sobre o impacto do VAR no futebol',
                'category': 'Opinião',
                'tags': 'var, arbitragem, controversia, opiniao',
                'views': random.randint(3000, 9000),
                'likes': random.randint(100, 400),
                'status': 'published'
            },
        ]
        
        for article_data in articles_data:
            try:
                category = ContentCategory.objects.get(name=article_data['category'])
                article, created = UserArticle.objects.get_or_create(
                    title=article_data['title'],
                    defaults={
                        **article_data,
                        'category': category,
                        'author': demo_user
                    }
                )
                if created:
                    self.stdout.write(f'Artigo criado: {article.title}')
            except ContentCategory.DoesNotExist:
                self.stdout.write(f'Categoria não encontrada: {article_data["category"]}')
        
        # Criar enquetes de demonstração
        polls_data = [
            {
                'title': 'Qual é o melhor jogador do mundo atual?',
                'question': 'Considerando performance, títulos e consistência, quem você considera o melhor jogador atualmente?',
                'description': 'Vote no que você considera o melhor jogador do mundo neste momento.',
                'status': 'active',
                'is_featured': True,
                'options': [
                    'Lionel Messi',
                    'Kylian Mbappé',
                    'Erling Haaland',
                    'Vinicius Jr.',
                    'Kevin De Bruyne'
                ]
            },
            {
                'title': 'Melhor formação tática para 2024?',
                'question': 'Qual formação tática você considera mais eficaz no futebol moderno?',
                'description': 'Analise as formações mais utilizadas pelos grandes clubes.',
                'status': 'active',
                'options': [
                    '4-3-3',
                    '4-2-3-1',
                    '3-5-2',
                    '4-4-2',
                    '3-4-3'
                ]
            },
            {
                'title': 'Time favorito para ganhar a Liga dos Campeões?',
                'question': 'Qual time tem mais chances de conquistar a Champions League esta temporada?',
                'description': 'Vote no seu favorito para levantar a taça da Champions.',
                'status': 'active',
                'options': [
                    'Manchester City',
                    'Real Madrid',
                    'Bayern München',
                    'Paris Saint-Germain',
                    'Barcelona'
                ]
            },
            {
                'title': 'Melhor técnico atualmente no futebol?',
                'question': 'Quem você considera o melhor treinador do futebol mundial?',
                'description': 'Vote no técnico que mais admira pelo trabalho atual.',
                'status': 'active',
                'options': [
                    'Pep Guardiola',
                    'Carlo Ancelotti',
                    'Jürgen Klopp',
                    'Xavi Hernández',
                    'Luis Enrique'
                ]
            },
            {
                'title': 'VAR: Ajuda ou atrapalha o futebol?',
                'question': 'Qual sua opinião sobre o uso do VAR no futebol?',
                'description': 'O VAR tem sido controverso. Dê sua opinião.',
                'status': 'closed',
                'options': [
                    'Ajuda muito, mais justiça',
                    'Ajuda, mas precisa melhorar',
                    'Neutro',
                    'Atrapalha, muito demorado',
                    'Atrapalha muito, deveria acabar'
                ]
            }
        ]
        
        for poll_data in polls_data:
            options = poll_data.pop('options')
            poll, created = Poll.objects.get_or_create(
                title=poll_data['title'],
                defaults={
                    **poll_data,
                    'author': demo_user,
                    'total_votes': random.randint(1000, 8000),
                    'views': random.randint(2000, 15000)
                }
            )
            
            if created:
                self.stdout.write(f'Enquete criada: {poll.title}')
                
                # Criar opções para a enquete
                for i, option_text in enumerate(options):
                    votes = random.randint(100, 2000)
                    option = PollOption.objects.create(
                        poll=poll,
                        text=option_text,
                        order=i,
                        votes=votes
                    )
                    # Atualizar porcentagem
                    if poll.total_votes > 0:
                        option.percentage = round((votes / poll.total_votes) * 100, 2)
                        option.save()
        
        self.stdout.write(
            self.style.SUCCESS('Dados de demonstração criados com sucesso!')
        )
