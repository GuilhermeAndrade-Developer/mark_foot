from django.core.management.base import BaseCommand
from nlp_engine.models import Intent, EntityType, TrainingPhrase, IntentPattern


class Command(BaseCommand):
    help = 'Load initial training data for NLP engine'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Loading NLP training data...'))
        
        # Create intents
        intents_data = [
            {
                'name': 'team_stats',
                'description': 'User wants information about team statistics and performance'
            },
            {
                'name': 'player_stats',
                'description': 'User wants information about player statistics and performance'
            },
            {
                'name': 'match_info',
                'description': 'User wants information about matches, schedules, or results'
            },
            {
                'name': 'standings',
                'description': 'User wants to see league standings or table positions'
            },
            {
                'name': 'betting_odds',
                'description': 'User wants betting odds and analysis (premium feature)'
            },
            {
                'name': 'subscription',
                'description': 'User wants information about premium subscription'
            },
            {
                'name': 'help',
                'description': 'User needs help or general information'
            },
            {
                'name': 'predictions',
                'description': 'User wants match predictions and analysis'
            },
            {
                'name': 'news',
                'description': 'User wants football news and updates'
            },
            {
                'name': 'schedule',
                'description': 'User wants match schedule information'
            }
        ]
        
        for intent_data in intents_data:
            intent, created = Intent.objects.get_or_create(
                name=intent_data['name'],
                defaults={'description': intent_data['description']}
            )
            if created:
                self.stdout.write(f'Created intent: {intent.name}')
        
        # Create entity types
        entity_types_data = [
            {
                'name': 'team',
                'description': 'Football team names and references'
            },
            {
                'name': 'player',
                'description': 'Football player names and references'
            },
            {
                'name': 'competition',
                'description': 'Football competition names (leagues, cups, etc.)'
            },
            {
                'name': 'date',
                'description': 'Date and time references'
            },
            {
                'name': 'number',
                'description': 'Numeric values (scores, statistics, etc.)'
            },
            {
                'name': 'location',
                'description': 'Geographic locations and venues'
            },
            {
                'name': 'season',
                'description': 'Season references (2023/24, current, etc.)'
            },
            {
                'name': 'match_status',
                'description': 'Match status (scheduled, live, finished, etc.)'
            }
        ]
        
        for entity_data in entity_types_data:
            entity_type, created = EntityType.objects.get_or_create(
                name=entity_data['name'],
                defaults={'description': entity_data['description']}
            )
            if created:
                self.stdout.write(f'Created entity type: {entity_type.name}')
        
        # Create training phrases for team_stats intent
        team_stats_intent = Intent.objects.get(name='team_stats')
        team_stats_phrases = [
            'Como está o Flamengo?',
            'Situação do Palmeiras',
            'Como está o time do Corinthians?',
            'Posição do Santos na tabela',
            'Como está jogando o São Paulo?',
            'Desempenho do Botafogo',
            'Classificação do Vasco',
            'Como está o Grêmio nesta temporada?',
            'Situação atual do Internacional',
            'Performance do Atlético Mineiro',
            'Como vai o Cruzeiro?',
            'Posição do Fluminense',
            'Como está o Athletico?',
            'Situação do Bahia no campeonato',
            'Desempenho do Fortaleza',
        ]
        
        for phrase in team_stats_phrases:
            TrainingPhrase.objects.get_or_create(
                intent=team_stats_intent,
                phrase=phrase,
                defaults={'language': 'pt'}
            )
        
        # Create training phrases for player_stats intent
        player_stats_intent = Intent.objects.get(name='player_stats')
        player_stats_phrases = [
            'Estatísticas do Gabigol',
            'Como está o Messi?',
            'Gols do Neymar',
            'Performance do Cristiano Ronaldo',
            'Estatísticas do Vini Jr',
            'Como está jogando o Mbappé?',
            'Números do Haaland',
            'Assistências do Kevin De Bruyne',
            'Cartões do Casemiro',
            'Gols do Lewandowski',
            'Performance do Pedri',
            'Estatísticas do Bruno Fernandes',
            'Como está o Alisson?',
            'Defesas do Ederson',
            'Números do Rodrygo',
        ]
        
        for phrase in player_stats_phrases:
            TrainingPhrase.objects.get_or_create(
                intent=player_stats_intent,
                phrase=phrase,
                defaults={'language': 'pt'}
            )
        
        # Create training phrases for standings intent
        standings_intent = Intent.objects.get(name='standings')
        standings_phrases = [
            'Tabela do Brasileirão',
            'Classificação da Premier League',
            'Posições da Champions League',
            'Tabela da La Liga',
            'Ranking da Serie A',
            'Classificação do Campeonato Carioca',
            'Tabela da Copa do Brasil',
            'Posições da Libertadores',
            'Classificação da Serie B',
            'Tabela da Bundesliga',
            'Ranking da Ligue 1',
            'Posições da Liga dos Campeões',
            'Tabela atual do campeonato',
            'Como está a classificação?',
            'Quem está em primeiro lugar?',
        ]
        
        for phrase in standings_phrases:
            TrainingPhrase.objects.get_or_create(
                intent=standings_intent,
                phrase=phrase,
                defaults={'language': 'pt'}
            )
        
        # Create training phrases for subscription intent
        subscription_intent = Intent.objects.get(name='subscription')
        subscription_phrases = [
            'Como assinar o premium?',
            'Quero ser premium',
            'Informações sobre assinatura',
            'Quanto custa o plano premium?',
            'Como cancelar minha assinatura?',
            'Quais os benefícios do premium?',
            'Quero fazer upgrade',
            'Como pagar o premium?',
            'Trial gratuito',
            'Período de teste',
            'Planos disponíveis',
            'Assinatura mensal',
            'Premium features',
            'Benefícios da assinatura',
            'Como funciona o premium?',
        ]
        
        for phrase in subscription_phrases:
            TrainingPhrase.objects.get_or_create(
                intent=subscription_intent,
                phrase=phrase,
                defaults={'language': 'pt'}
            )
        
        # Create training phrases for match_info intent
        match_info_intent = Intent.objects.get(name='match_info')
        match_info_phrases = [
            'Quando joga o Flamengo?',
            'Próximo jogo do Palmeiras',
            'Resultado do último jogo',
            'Jogos de hoje',
            'Partidas de amanhã',
            'Horário do jogo',
            'Resultado Flamengo x Palmeiras',
            'Quando é o clássico?',
            'Jogos da rodada',
            'Placar do jogo',
            'Que horas joga?',
            'Próxima partida',
            'Último resultado',
            'Jogos desta semana',
            'Agenda de jogos',
        ]
        
        for phrase in match_info_phrases:
            TrainingPhrase.objects.get_or_create(
                intent=match_info_intent,
                phrase=phrase,
                defaults={'language': 'pt'}
            )
        
        # Create training phrases for betting_odds intent
        betting_odds_intent = Intent.objects.get(name='betting_odds')
        betting_odds_phrases = [
            'Odds Flamengo x Palmeiras',
            'Cotações do jogo',
            'Análise de apostas',
            'Melhores odds',
            'Cotação para vitória',
            'Odds para gols',
            'Apostas recomendadas',
            'Value bets',
            'Análise de cotações',
            'Odds do campeonato',
            'Cotações atualizadas',
            'Dicas de apostas',
            'Probabilidades do jogo',
            'Odds favoritas',
            'Mercado de apostas',
        ]
        
        for phrase in betting_odds_phrases:
            TrainingPhrase.objects.get_or_create(
                intent=betting_odds_intent,
                phrase=phrase,
                defaults={'language': 'pt'}
            )
        
        # Create intent patterns
        patterns_data = [
            # Team stats patterns
            {
                'intent': 'team_stats',
                'pattern': 'como está situação posição performance desempenho classificação',
                'pattern_type': 'keyword',
                'weight': 1.0
            },
            {
                'intent': 'team_stats',
                'pattern': r'como (está|ta) (o |a )?(\w+)',
                'pattern_type': 'regex',
                'weight': 1.2
            },
            
            # Player stats patterns
            {
                'intent': 'player_stats',
                'pattern': 'estatísticas jogador gols assists cartões performance números',
                'pattern_type': 'keyword',
                'weight': 1.0
            },
            {
                'intent': 'player_stats',
                'pattern': r'(estatísticas|gols|assists) (do|da) (\w+)',
                'pattern_type': 'regex',
                'weight': 1.2
            },
            
            # Standings patterns
            {
                'intent': 'standings',
                'pattern': 'tabela classificação posições ranking standings',
                'pattern_type': 'keyword',
                'weight': 1.0
            },
            {
                'intent': 'standings',
                'pattern': r'tabela (do|da) (\w+)',
                'pattern_type': 'regex',
                'weight': 1.2
            },
            
            # Match info patterns
            {
                'intent': 'match_info',
                'pattern': 'quando joga próximo jogo resultado placar horário partida',
                'pattern_type': 'keyword',
                'weight': 1.0
            },
            {
                'intent': 'match_info',
                'pattern': r'quando joga (o |a )?(\w+)',
                'pattern_type': 'regex',
                'weight': 1.2
            },
            
            # Subscription patterns
            {
                'intent': 'subscription',
                'pattern': 'premium assinar assinatura plano cancelar upgrade trial',
                'pattern_type': 'keyword',
                'weight': 1.0
            },
            
            # Betting odds patterns
            {
                'intent': 'betting_odds',
                'pattern': 'odds cotações apostas bet value betting análise',
                'pattern_type': 'keyword',
                'weight': 1.0
            },
        ]
        
        for pattern_data in patterns_data:
            intent = Intent.objects.get(name=pattern_data['intent'])
            IntentPattern.objects.get_or_create(
                intent=intent,
                pattern=pattern_data['pattern'],
                pattern_type=pattern_data['pattern_type'],
                defaults={'weight': pattern_data['weight']}
            )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully loaded NLP training data!')
        )
        
        # Print summary
        self.stdout.write(f'Intents: {Intent.objects.count()}')
        self.stdout.write(f'Entity Types: {EntityType.objects.count()}')
        self.stdout.write(f'Training Phrases: {TrainingPhrase.objects.count()}')
        self.stdout.write(f'Intent Patterns: {IntentPattern.objects.count()}')
