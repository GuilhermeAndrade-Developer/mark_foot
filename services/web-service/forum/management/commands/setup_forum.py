from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.text import slugify
from forum.models import ForumCategory, ForumTopic, ForumPost, ForumUserProfile
from core.models import Team, Competition


class Command(BaseCommand):
    help = 'Popula dados iniciais do fórum com categorias baseadas em times e competições'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Remove todos os dados existentes antes de popular'
        )
        parser.add_argument(
            '--categories-only',
            action='store_true',
            help='Cria apenas categorias, sem tópicos de exemplo'
        )
        parser.add_argument(
            '--sample-data',
            action='store_true',
            help='Inclui dados de exemplo (tópicos e posts)'
        )
    
    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('🗑️  Removendo dados existentes do fórum...')
            self.reset_forum_data()
        
        self.stdout.write('🏗️  Criando categorias do fórum...')
        self.create_categories()
        
        if options['sample_data']:
            self.stdout.write('📝 Criando dados de exemplo...')
            self.create_sample_data()
        
        self.stdout.write(
            self.style.SUCCESS('✅ Setup do fórum concluído com sucesso!')
        )
    
    def reset_forum_data(self):
        """Remove todos os dados do fórum"""
        ForumPost.objects.all().delete()
        ForumTopic.objects.all().delete()
        ForumCategory.objects.all().delete()
        ForumUserProfile.objects.all().delete()
        self.stdout.write('   ✅ Dados removidos')
    
    def create_categories(self):
        """Cria categorias baseadas em times e competições"""
        categories_created = 0
        
        # 1. Categorias Gerais
        general_categories = [
            {
                'name': 'Discussões Gerais',
                'slug': 'discussoes-gerais',
                'description': 'Discussões gerais sobre futebol',
                'category_type': 'general'
            },
            {
                'name': 'Notícias',
                'slug': 'noticias',
                'description': 'Últimas notícias do mundo do futebol',
                'category_type': 'news'
            },
            {
                'name': 'Análises Táticas',
                'slug': 'analises-taticas',
                'description': 'Discussões sobre táticas e estratégias',
                'category_type': 'analysis'
            }
        ]
        
        for cat_data in general_categories:
            category, created = ForumCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            if created:
                categories_created += 1
                self.stdout.write(f'   ✅ Categoria criada: {category.name}')
        
        # 2. Categorias por Competição
        try:
            competitions = Competition.objects.all()[:10]  # Primeiras 10 competições
            for comp in competitions:
                cat_data = {
                    'name': f'{comp.name}',
                    'slug': slugify(f'{comp.name}'),
                    'description': f'Discussões sobre {comp.name}',
                    'category_type': 'competition',
                    'competition_id': comp.id
                }
                
                category, created = ForumCategory.objects.get_or_create(
                    slug=cat_data['slug'],
                    defaults=cat_data
                )
                if created:
                    categories_created += 1
                    self.stdout.write(f'   ✅ Categoria de competição: {category.name}')
        
        except Exception as e:
            self.stdout.write(f'   ⚠️ Erro ao criar categorias de competição: {e}')
        
        # 3. Categorias por Times Populares
        try:
            # Buscar times mais populares (exemplo: com mais partidas)
            popular_teams = Team.objects.all()[:15]  # Primeiros 15 times
            
            for team in popular_teams:
                cat_data = {
                    'name': f'{team.name}',
                    'slug': slugify(f'{team.name}'),
                    'description': f'Discussões sobre {team.name}',
                    'category_type': 'team',
                    'team_id': team.id
                }
                
                category, created = ForumCategory.objects.get_or_create(
                    slug=cat_data['slug'],
                    defaults=cat_data
                )
                if created:
                    categories_created += 1
                    self.stdout.write(f'   ✅ Categoria de time: {category.name}')
        
        except Exception as e:
            self.stdout.write(f'   ⚠️ Erro ao criar categorias de times: {e}')
        
        self.stdout.write(f'   📊 Total de categorias criadas: {categories_created}')
    
    def create_sample_data(self):
        """Cria dados de exemplo para demonstração"""
        # Buscar ou criar usuário admin
        admin_user, created = User.objects.get_or_create(
            username='forum_admin',
            defaults={
                'email': 'admin@markfoot.com',
                'first_name': 'Admin',
                'last_name': 'Forum',
                'is_staff': True
            }
        )
        
        # Criar perfil do usuário
        profile, created = ForumUserProfile.objects.get_or_create(
            user=admin_user,
            defaults={'signature': 'Administrador do Fórum Mark Foot'}
        )
        
        # Buscar categorias para criar tópicos
        categories = ForumCategory.objects.all()[:5]
        
        sample_topics = [
            {
                'title': 'Bem-vindos ao Fórum Mark Foot!',
                'content': '''Sejam bem-vindos ao novo sistema de fóruns do Mark Foot!
                
Aqui vocês podem:
• Discutir sobre seus times favoritos
• Analisar táticas e estratégias
• Compartilhar notícias
• Debater sobre competições

Esperamos que aproveitem este espaço para discussões construtivas sobre o mundo do futebol!''',
                'tags': 'bem-vindos, apresentação, regras'
            },
            {
                'title': 'Como usar o sistema de votação?',
                'content': '''O fórum possui um sistema de votação para posts:

👍 **Upvote**: Use quando concordar ou achar útil
👎 **Downvote**: Use apenas para conteúdo irrelevante (não para discordância)

A reputação é calculada baseada nos votos recebidos em seus posts.''',
                'tags': 'tutorial, votação, reputação'
            },
            {
                'title': 'Regras de Conduta do Fórum',
                'content': '''Para manter um ambiente saudável, seguiremos estas regras:

1. **Respeito**: Trate todos com cortesia
2. **Relevância**: Mantenha discussões relacionadas ao futebol
3. **Sem spam**: Evite posts repetitivos ou promocionais
4. **Fontes**: Cite fontes ao compartilhar notícias
5. **Linguagem**: Mantenha linguagem apropriada

Violações podem resultar em advertências ou banimento.''',
                'tags': 'regras, conduta, moderação'
            }
        ]
        
        topics_created = 0
        posts_created = 0
        
        for i, topic_data in enumerate(sample_topics):
            if i < len(categories):
                category = categories[i]
                
                topic = ForumTopic.objects.create(
                    category=category,
                    title=topic_data['title'],
                    slug=slugify(topic_data['title']),
                    content=topic_data['content'],
                    author=admin_user,
                    tags=topic_data['tags'],
                    status='pinned' if i == 0 else 'open'
                )
                topics_created += 1
                
                # Criar algumas respostas de exemplo
                sample_replies = [
                    f'Excelente iniciativa! Estou ansioso para participar das discussões sobre {category.name}.',
                    'Obrigado pelas informações. Já favoritei este tópico!',
                    'Ótimo trabalho na implementação do fórum. A interface está muito intuitiva.'
                ]
                
                for j, reply_content in enumerate(sample_replies[:2]):  # Máximo 2 replies por tópico
                    ForumPost.objects.create(
                        topic=topic,
                        content=reply_content,
                        author=admin_user
                    )
                    posts_created += 1
        
        self.stdout.write(f'   📊 Tópicos criados: {topics_created}')
        self.stdout.write(f'   📊 Posts criados: {posts_created}')
        
        # Atualizar contadores
        for category in categories:
            category.update_counters()
    
    def create_admin_user(self):
        """Cria usuário admin se não existir"""
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@markfoot.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write('   ✅ Usuário admin criado (senha: admin123)')
        
        return admin_user
