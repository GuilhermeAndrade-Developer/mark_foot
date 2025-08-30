"""
Seeder for content module (articles, categories).
Replaces hardcoded content data with professional seeds.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from content.models import ContentCategory, UserArticle
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Seed content data for development'

    def handle(self, *args, **options):
        self.stdout.write('📝 Seeding content data...')
        
        # Create categories
        categories_created = self.create_categories()
        
        # Create articles
        articles_created = self.create_articles()

        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Content data seeded:\n'
                f'   📂 Categories: {categories_created}\n'
                f'   📝 Articles: {articles_created}'
            )
        )

    def create_categories(self):
        """Create content categories"""
        categories_data = [
            {
                'name': 'Análises Táticas',
                'icon': 'mdi-strategy',
                'description': 'Análises detalhadas de jogos e formações táticas',
                'color': '#2196F3'
            },
            {
                'name': 'Mercado da Bola',
                'icon': 'mdi-cash-multiple',
                'description': 'Transferências, contratações e mercado de jogadores',
                'color': '#4CAF50'
            },
            {
                'name': 'História do Futebol',
                'icon': 'mdi-book-open-variant',
                'description': 'Fatos históricos, curiosidades e momentos marcantes',
                'color': '#FF9800'
            },
            {
                'name': 'Estatísticas',
                'icon': 'mdi-chart-bar',
                'description': 'Dados, números e análises estatísticas do futebol',
                'color': '#9C27B0'
            },
            {
                'name': 'Opinião',
                'icon': 'mdi-comment-text',
                'description': 'Artigos de opinião e análises críticas',
                'color': '#F44336'
            },
            {
                'name': 'Entrevistas',
                'icon': 'mdi-microphone',
                'description': 'Entrevistas exclusivas com jogadores e técnicos',
                'color': '#00BCD4'
            },
            {
                'name': 'Brasileirão',
                'icon': 'mdi-flag',
                'description': 'Cobertura completa do Campeonato Brasileiro',
                'color': '#FFEB3B'
            },
            {
                'name': 'Internacional',
                'icon': 'mdi-earth',
                'description': 'Futebol internacional e competições europeias',
                'color': '#607D8B'
            }
        ]

        created_count = 0
        for cat_data in categories_data:
            category, created = ContentCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                created_count += 1

        return created_count

    def create_articles(self):
        """Create sample articles"""
        # Get users for authors (prefer regular users, fallback to any user)
        authors = list(User.objects.filter(is_superuser=False, is_active=True))
        if not authors:
            authors = list(User.objects.filter(is_active=True))
        
        if not authors:
            self.stdout.write('⚠️  No users found for article authors')
            return 0

        categories = ContentCategory.objects.all()
        if not categories.exists():
            self.stdout.write('⚠️  No categories found')
            return 0

        articles_data = [
            {
                'title': 'Análise Tática: Como o Flamengo Dominou o Clássico',
                'content': self.get_sample_content('tatica'),
                'excerpt': 'Análise completa da vitória do Flamengo no último clássico carioca com detalhes táticos.',
                'category': 'Análises Táticas',
                'tags': 'flamengo, tatica, classico, analise',
                'status': 'published'
            },
            {
                'title': 'Mercado da Bola: As 10 Maiores Contratações do Brasileirão',
                'content': self.get_sample_content('mercado'),
                'excerpt': 'Lista completa das principais contratações que movimentaram o mercado nacional.',
                'category': 'Mercado da Bola',
                'tags': 'transferencias, brasileirao, contratacoes',
                'status': 'published'
            },
            {
                'title': 'A Evolução do Futebol Brasileiro nos Últimos 20 Anos',
                'content': self.get_sample_content('historia'),
                'excerpt': 'Retrospectiva completa das mudanças no futebol nacional nas últimas duas décadas.',
                'category': 'História do Futebol',
                'tags': 'brasil, historia, evolucao, retrospectiva',
                'status': 'published'
            },
            {
                'title': 'Estatísticas: Quem são os Artilheiros do Brasileirão 2024?',
                'content': self.get_sample_content('estatisticas'),
                'excerpt': 'Números completos dos principais goleadores do campeonato brasileiro.',
                'category': 'Estatísticas',
                'tags': 'estatisticas, artilheiros, brasileirao, gols',
                'status': 'published'
            },
            {
                'title': 'Por que o VAR Ainda Gera Polêmica no Futebol Brasileiro?',
                'content': self.get_sample_content('opiniao'),
                'excerpt': 'Reflexão sobre os desafios e controvérsias do VAR no futebol nacional.',
                'category': 'Opinião',
                'tags': 'var, arbitragem, polemica, opiniao',
                'status': 'published'
            },
            {
                'title': 'Entrevista Exclusiva: Técnico Revela Estratégias de Sucesso',
                'content': self.get_sample_content('entrevista'),
                'excerpt': 'Conversa exclusiva com técnico sobre metodologia e filosofia de trabalho.',
                'category': 'Entrevistas',
                'tags': 'entrevista, tecnico, estrategia, exclusiva',
                'status': 'published'
            },
            {
                'title': 'Brasileirão 2024: Análise da Primeira Metade da Temporada',
                'content': self.get_sample_content('brasileirao'),
                'excerpt': 'Balanço completo dos primeiros meses do Campeonato Brasileiro.',
                'category': 'Brasileirão',
                'tags': 'brasileirao, analise, temporada, campeonato',
                'status': 'published'
            },
            {
                'title': 'Champions League: Brasileiros se Destacam na Europa',
                'content': self.get_sample_content('internacional'),
                'excerpt': 'Como os jogadores brasileiros estão se saindo nas competições europeias.',
                'category': 'Internacional',
                'tags': 'champions, europa, brasileiros, internacional',
                'status': 'published'
            },
            # Draft articles
            {
                'title': 'Rascunho: Análise do Próximo Clássico',
                'content': 'Conteúdo em desenvolvimento...',
                'excerpt': 'Artigo em desenvolvimento sobre o próximo grande clássico.',
                'category': 'Análises Táticas',
                'tags': 'classico, preview, analise',
                'status': 'draft'
            },
            {
                'title': 'Rascunho: Novidades do Mercado Europeu',
                'content': 'Conteúdo em desenvolvimento...',
                'excerpt': 'Últimas movimentações no mercado de transferências europeu.',
                'category': 'Mercado da Bola',
                'tags': 'europa, transferencias, mercado',
                'status': 'draft'
            }
        ]

        created_count = 0
        for article_data in articles_data:
            try:
                category = categories.get(name=article_data['category'])
                author = random.choice(authors)
                
                # Set random publish date (last 30 days for published, last 7 for drafts)
                if article_data['status'] == 'published':
                    published_at = timezone.now() - timedelta(days=random.randint(1, 30))
                else:
                    published_at = None

                article, created = UserArticle.objects.get_or_create(
                    title=article_data['title'],
                    defaults={
                        'content': article_data['content'],
                        'excerpt': article_data['excerpt'],
                        'category': category,
                        'author': author,
                        'tags': article_data['tags'],
                        'status': article_data['status'],
                        'published_at': published_at,
                        'views': random.randint(100, 5000) if article_data['status'] == 'published' else 0,
                        'likes': random.randint(10, 500) if article_data['status'] == 'published' else 0,
                        'reading_time': random.randint(3, 15)
                    }
                )
                if created:
                    created_count += 1

            except ContentCategory.DoesNotExist:
                self.stdout.write(f'⚠️  Category not found: {article_data["category"]}')
                continue

        return created_count

    def get_sample_content(self, content_type):
        """Generate sample content based on type"""
        base_content = {
            'tatica': """
                ## Introdução

                O clássico de domingo mostrou uma diferença clara de organização tática entre as equipes. 
                Nesta análise, vamos detalhar as principais estratégias utilizadas e como elas definiram o resultado.

                ## Formação e Posicionamento

                A equipe visitante optou por uma formação 4-2-3-1 que se mostrou muito eficiente na marcação 
                e transições rápidas. Os volantes exerceram papel fundamental na recuperação da bola.

                ## Momentos Decisivos

                - **15 min**: Primeiro gol surgiu de uma jogada ensaiada
                - **32 min**: Mudança tática alterou o panorama do jogo  
                - **58 min**: Substituições foram cruciais para o resultado

                ## Conclusão

                A vitória foi resultado de uma preparação tática superior e execução quase perfeita do plano de jogo.
            """,
            'mercado': """
                ## Movimentações de Destaque

                O mercado da bola nacional teve grandes surpresas nesta janela de transferências. 
                Analisamos as principais contratações e seus impactos.

                ## Top 10 Contratações

                1. **Atacante X** - R$ 25 milhões
                2. **Meia Y** - R$ 18 milhões  
                3. **Zagueiro Z** - R$ 15 milhões

                ## Análise de Impacto

                Essas contratações devem elevar significativamente o nível técnico das equipes envolvidas.

                ## Tendências do Mercado

                - Valorização de jogadores jovens
                - Foco em atletas versáteis
                - Investimento em tecnologia de análise
            """,
            'historia': """
                ## Uma Jornada de Transformação

                O futebol brasileiro passou por mudanças profundas nos últimos 20 anos. 
                Desde aspectos técnicos até organizacionais, o esporte evoluiu significativamente.

                ## Principais Mudanças

                ### Aspecto Técnico
                - Evolução das formações táticas
                - Melhoria na preparação física
                - Uso de tecnologia no treinamento

                ### Aspecto Organizacional  
                - Profissionalização da gestão
                - Modernização dos estádios
                - Melhoria na transmissão

                ## Legado e Futuro

                As transformações criaram uma base sólida para o futuro do futebol nacional.
            """,
            'estatisticas': """
                ## Números que Impressionam

                Os dados do Brasileirão 2024 revelam tendências interessantes sobre o desempenho dos artilheiros.

                ## Ranking de Gols

                | Posição | Jogador | Time | Gols |
                |---------|---------|------|------|
                | 1º | Atacante A | Time X | 15 |
                | 2º | Atacante B | Time Y | 12 |
                | 3º | Atacante C | Time Z | 11 |

                ## Análise dos Dados

                A eficiência dos atacantes aumentou 23% comparado ao ano anterior, 
                reflexo da melhoria na criação de jogadas.

                ## Projeções

                Com base nos números atuais, a meta de 20 gols parece alcançável para o líder.
            """,
            'opiniao': """
                ## Um Debate Necessário

                O VAR trouxe mais justiça ao futebol, mas ainda gera discussões acaloradas. 
                É hora de uma reflexão madura sobre sua implementação.

                ## Pontos Positivos

                - Redução de erros crassos
                - Maior justiça nas decisões
                - Melhoria na qualidade da arbitragem

                ## Desafios Persistentes

                - Demora nas decisões
                - Interpretação subjetiva
                - Impacto no fluxo do jogo

                ## Minha Opinião

                O VAR é uma ferramenta importante, mas precisa de ajustes para maximizar seus benefícios 
                sem comprometer a fluidez do espetáculo.
            """,
            'entrevista': """
                ## Conversa Exclusiva

                Em entrevista exclusiva, o técnico compartilha sua filosofia de trabalho e 
                revela os segredos por trás do sucesso da equipe.

                **Repórter**: Como você define sua filosofia de jogo?

                **Técnico**: "Acredito no futebol ofensivo, mas sempre com organização defensiva. 
                O equilíbrio é fundamental."

                **Repórter**: Qual o diferencial da sua metodologia?

                **Técnico**: "Trabalho muito o aspecto mental dos jogadores. Futebol moderno 
                exige atletas preparados psicologicamente."

                ## Principais Revelações

                - Importância do trabalho mental
                - Foco na disciplina tática
                - Valorização do coletivo sobre individual
            """,
            'brasileirao': """
                ## Meio de Temporada

                O Brasileirão 2024 chegou à sua metade com grandes surpresas e confirmações. 
                Analisamos o que vimos até aqui.

                ## Destaques Positivos

                - Equilíbrio entre as equipes
                - Melhoria técnica geral
                - Revelação de novos talentos

                ## Surpresas da Temporada

                1. **Time X** na parte de cima da tabela
                2. **Time Y** lutando contra rebaixamento
                3. **Jogador Z** como artilheiro

                ## Projeções

                A segunda metade promete ser ainda mais emocionante, 
                com várias equipes brigando pelo título.
            """,
            'internacional': """
                ## Brasileiros na Europa

                A nova temporada europeia começou com brasileiros se destacando 
                em várias competições. Analisamos as principais performances.

                ## Destaques da Champions

                - **Jogador A**: 3 gols em 2 jogos
                - **Jogador B**: Melhor em campo na estreia
                - **Jogador C**: Liderando assistências

                ## Impacto na Seleção

                Essas performances elevam o nível da Seleção Brasileira 
                e aumentam as expectativas para as próximas convocações.

                ## Perspectivas

                Com tantos talentos em alta, o futuro do futebol brasileiro 
                na Europa nunca esteve tão promissor.
            """
        }

        return base_content.get(content_type, "Conteúdo de exemplo para artigo.")
