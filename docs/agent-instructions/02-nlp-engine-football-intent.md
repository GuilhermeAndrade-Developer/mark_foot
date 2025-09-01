# NLP Engine and Football Intent Recognition

## Objective
Implement Natural Language Processing engine to understand football-related queries in Portuguese and extract relevant entities for the WhatsApp chatbot.

## Current Project Context
- WhatsApp integration implemented
- Existing football data: teams, players, matches, competitions
- Database models: Team, Player, Match, Competition, Standings
- AI services already available in ai_analytics app
- Portuguese language focus with future multi-language support

## Technical Requirements

### 1. Create NLP Django App
```bash
cd services/web-service
python manage.py startapp nlp_engine
```

### 2. Models Implementation

#### nlp_engine/models.py
```python
from django.db import models

class Intent(models.Model):
    INTENT_TYPES = [
        ('team_stats', 'Team Statistics'),
        ('player_stats', 'Player Statistics'),
        ('match_info', 'Match Information'),
        ('odds_analysis', 'Odds Analysis'),
        ('predictions', 'Match Predictions'),
        ('standings', 'League Standings'),
        ('help', 'Help Request'),
        ('subscription', 'Subscription Related'),
    ]
    
    name = models.CharField(max_length=50, choices=INTENT_TYPES, unique=True)
    description = models.TextField()
    confidence_threshold = models.FloatField(default=0.7)
    is_active = models.BooleanField(default=True)

class EntityType(models.Model):
    name = models.CharField(max_length=50, unique=True)  # team, player, competition, date
    pattern_regex = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

class TrainingPhrase(models.Model):
    intent = models.ForeignKey(Intent, on_delete=models.CASCADE)
    phrase = models.TextField()
    language = models.CharField(max_length=5, default='pt')
    confidence_score = models.FloatField(null=True, blank=True)

class EntityValue(models.Model):
    entity_type = models.ForeignKey(EntityType, on_delete=models.CASCADE)
    value = models.CharField(max_length=200)
    canonical_value = models.CharField(max_length=200)
    synonyms = models.JSONField(default=list)
    
class UserQuery(models.Model):
    query_text = models.TextField()
    detected_intent = models.CharField(max_length=50, blank=True)
    detected_entities = models.JSONField(default=dict)
    confidence_score = models.FloatField(null=True, blank=True)
    response_generated = models.TextField(blank=True)
    processing_time_ms = models.IntegerField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    whatsapp_user_phone = models.CharField(max_length=20, blank=True)
```

### 3. Core NLP Service

#### nlp_engine/services.py
```python
import re
import spacy
from datetime import datetime
from django.conf import settings
from .models import Intent, EntityType, TrainingPhrase, EntityValue, UserQuery
from core.models import Team, Player, Competition

class FootballNLPService:
    def __init__(self):
        self.load_nlp_model()
        self.load_football_entities()
        self.intent_patterns = self.load_intent_patterns()
    
    def load_nlp_model(self):
        try:
            self.nlp = spacy.load("pt_core_news_sm")
        except IOError:
            # Fallback to basic processing if spaCy model not available
            self.nlp = None
    
    def load_football_entities(self):
        # Load teams from database
        self.teams_dict = {}
        for team in Team.objects.all():
            self.teams_dict[team.name.lower()] = team.id
            self.teams_dict[team.short_name.lower()] = team.id
            if team.tla:
                self.teams_dict[team.tla.lower()] = team.id
        
        # Load players from database
        self.players_dict = {}
        for player in Player.objects.all():
            self.players_dict[player.name.lower()] = player.id
        
        # Load competitions
        self.competitions_dict = {}
        for comp in Competition.objects.all():
            self.competitions_dict[comp.name.lower()] = comp.id
    
    def load_intent_patterns(self):
        return {
            'team_stats': [
                r'.*\b(como está|situacao|posicao|classificacao|tabela).*\b(.*?)\b',
                r'.*\b(estatisticas?|stats?|dados?).*\b(.*?)\b',
                r'.*\b(.*?)\b.*(temporada|campeonato|liga)',
            ],
            'player_stats': [
                r'.*\b(gols?|assistencias?).*\b(.*?)\b',
                r'.*\b(jogador|atleta).*\b(.*?)\b',
                r'.*\b(.*?)\b.*(quantos gols|estatisticas)',
            ],
            'match_info': [
                r'.*\b(jogo|partida|confronto).*\b(.*?)\b.*\b(.*?)\b',
                r'.*\b(.*?)\b.*\b(x|vs|contra).*\b(.*?)\b',
                r'.*\b(quando|que horas).*\b(joga|jogar)',
            ],
            'odds_analysis': [
                r'.*\b(odds?|cotacoes?|apostas?).*',
                r'.*\b(casa de apostas|bookmaker).*',
                r'.*\b(favorito|zebra).*',
            ],
            'predictions': [
                r'.*\b(previsao|palpite|predicao).*',
                r'.*\b(quem vai ganhar|resultado).*',
                r'.*\b(chance|probabilidade).*',
            ],
            'standings': [
                r'.*\b(tabela|classificacao|posicao).*\b(brasileirao|campeonato|liga)',
                r'.*\b(lider|primeiro|ultimo).*\b(colocado|posicao)',
            ],
            'help': [
                r'.*\b(ajuda|help|como usar|comandos).*',
                r'.*\b(o que voce faz|funcionalidades).*',
            ],
            'subscription': [
                r'.*\b(premium|assinatura|planos?).*',
                r'.*\b(pagar|pagamento|preco).*',
            ]
        }
    
    def process_query(self, query_text, user_phone=None):
        start_time = datetime.now()
        
        # Clean and normalize query
        normalized_query = self.normalize_text(query_text)
        
        # Detect intent
        intent, intent_confidence = self.detect_intent(normalized_query)
        
        # Extract entities
        entities = self.extract_entities(normalized_query, intent)
        
        # Calculate processing time
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        # Save query for analysis
        query_record = UserQuery.objects.create(
            query_text=query_text,
            detected_intent=intent,
            detected_entities=entities,
            confidence_score=intent_confidence,
            processing_time_ms=processing_time,
            whatsapp_user_phone=user_phone or ''
        )
        
        return {
            'intent': intent,
            'entities': entities,
            'confidence': intent_confidence,
            'query_id': query_record.id
        }
    
    def normalize_text(self, text):
        # Remove accents and normalize
        text = text.lower().strip()
        
        # Handle common Portuguese variations
        replacements = {
            'flamengo': ['fla', 'mengao', 'urubu'],
            'corinthians': ['coringao', 'timao'],
            'palmeiras': ['palestra', 'verdao'],
            'sao paulo': ['spfc', 'tricolor'],
            'santos': ['peixe', 'santastico'],
            'vasco': ['gigante da colina', 'cruzmaltino'],
            'gremio': ['tricolor gaucho', 'imortal'],
            'internacional': ['inter', 'colorado'],
        }
        
        for canonical, variants in replacements.items():
            for variant in variants:
                text = re.sub(r'\b' + variant + r'\b', canonical, text)
        
        return text
    
    def detect_intent(self, text):
        best_intent = 'help'
        best_confidence = 0.0
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    confidence = 0.8  # Base confidence for regex match
                    
                    # Boost confidence based on keyword density
                    if intent == 'team_stats' and any(team in text for team in self.teams_dict.keys()):
                        confidence += 0.15
                    elif intent == 'player_stats' and any(player in text for player in self.players_dict.keys()):
                        confidence += 0.15
                    elif intent == 'odds_analysis' and any(word in text for word in ['odds', 'aposta', 'cotacao']):
                        confidence += 0.1
                    
                    if confidence > best_confidence:
                        best_intent = intent
                        best_confidence = confidence
        
        return best_intent, best_confidence
    
    def extract_entities(self, text, intent):
        entities = {}
        
        # Extract teams
        found_teams = []
        for team_name, team_id in self.teams_dict.items():
            if team_name in text:
                found_teams.append({
                    'name': team_name,
                    'id': team_id,
                    'confidence': 0.9
                })
        
        if found_teams:
            entities['teams'] = found_teams
        
        # Extract players
        found_players = []
        for player_name, player_id in self.players_dict.items():
            if player_name in text:
                found_players.append({
                    'name': player_name,
                    'id': player_id,
                    'confidence': 0.85
                })
        
        if found_players:
            entities['players'] = found_players
        
        # Extract competitions
        found_competitions = []
        for comp_name, comp_id in self.competitions_dict.items():
            if comp_name in text:
                found_competitions.append({
                    'name': comp_name,
                    'id': comp_id,
                    'confidence': 0.8
                })
        
        if found_competitions:
            entities['competitions'] = found_competitions
        
        # Extract dates (basic implementation)
        date_patterns = [
            r'\b(hoje|today)\b',
            r'\b(amanha|tomorrow)\b',
            r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',
            r'\b(ontem|yesterday)\b'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                entities['date'] = {
                    'value': match.group(0),
                    'confidence': 0.7
                }
                break
        
        return entities

class ResponseGenerator:
    def __init__(self):
        self.nlp_service = FootballNLPService()
    
    def generate_response(self, query_result, user):
        intent = query_result['intent']
        entities = query_result['entities']
        
        if intent == 'team_stats':
            return self.generate_team_stats_response(entities, user)
        elif intent == 'player_stats':
            return self.generate_player_stats_response(entities, user)
        elif intent == 'match_info':
            return self.generate_match_info_response(entities, user)
        elif intent == 'odds_analysis':
            return self.generate_odds_response(entities, user)
        elif intent == 'predictions':
            return self.generate_predictions_response(entities, user)
        elif intent == 'standings':
            return self.generate_standings_response(entities, user)
        elif intent == 'subscription':
            return self.generate_subscription_response(user)
        else:
            return self.generate_help_response()
    
    def generate_team_stats_response(self, entities, user):
        if 'teams' not in entities or not entities['teams']:
            return "Por favor, especifique qual time você gostaria de saber as estatísticas."
        
        team_id = entities['teams'][0]['id']
        team = Team.objects.get(id=team_id)
        
        # Get team statistics from existing services
        from ai_analytics.services import TeamAnalyticsService
        analytics = TeamAnalyticsService()
        stats = analytics.get_team_summary(team_id)
        
        response = f"📊 {team.name} - Estatísticas\n\n"
        response += f"🏆 Posição atual: {stats.get('position', 'N/A')}\n"
        response += f"⚽ Jogos: {stats.get('games_played', 0)}\n"
        response += f"✅ Vitórias: {stats.get('wins', 0)}\n"
        response += f"🤝 Empates: {stats.get('draws', 0)}\n"
        response += f"❌ Derrotas: {stats.get('losses', 0)}\n"
        response += f"⚽ Gols pró: {stats.get('goals_for', 0)}\n"
        response += f"🥅 Gols contra: {stats.get('goals_against', 0)}\n"
        
        if not user.is_premium:
            response += "\n💎 Quer análise mais detalhada? Digite /premium"
        
        return response
    
    def generate_player_stats_response(self, entities, user):
        if 'players' not in entities or not entities['players']:
            return "Por favor, especifique qual jogador você gostaria de saber as estatísticas."
        
        player_id = entities['players'][0]['id']
        player = Player.objects.get(id=player_id)
        
        response = f"⚽ {player.name}\n\n"
        response += f"🏃 Posição: {player.position}\n"
        response += f"🏳️ Nacionalidade: {player.nationality}\n"
        response += f"🏆 Time: {player.team.name if player.team else 'N/A'}\n"
        
        if not user.is_premium:
            response += "\n💎 Estatísticas detalhadas disponíveis no Premium"
        
        return response
    
    def generate_odds_response(self, entities, user):
        if not user.is_premium:
            return """🎲 Análise de Odds - Premium

Para acessar análises completas de odds e explicações sobre cotações:

💎 Mark Foot Premium - R$ 19,90/mês
✅ Análise detalhada de odds
✅ Explicação do "porquê" das cotações
✅ Value bets identificados
✅ Alertas de mudanças importantes

Digite /premium para assinar"""
        
        return "🎲 Funcionalidade de odds em desenvolvimento para usuários Premium."
    
    def generate_help_response(self):
        return """🤖 Mark Foot Bot - Como usar

Exemplos de perguntas:
⚽ "Como está o Flamengo?"
🏆 "Tabela do Brasileirão"
👤 "Estatísticas do Messi"
🎲 "Odds Flamengo x Palmeiras" (Premium)

Comandos:
/premium - Informações sobre assinatura
/help - Este menu de ajuda

💬 Digite naturalmente suas perguntas sobre futebol!"""
    
    def generate_subscription_response(self, user):
        if user.is_premium:
            return "✅ Você já é usuário Premium! Aproveite todos os recursos."
        
        return """💎 Mark Foot Premium

Benefícios:
✅ Consultas ilimitadas
✅ Análise completa de odds
✅ Previsões com IA
✅ Alertas personalizados
✅ Relatórios PDF

💰 Apenas R$ 19,90/mês

🔗 Link para assinar: [URL_PAGAMENTO]

Dúvidas? Responda esta mensagem."""
```

### 4. Integration with WhatsApp Service

#### Update whatsapp_integration/services.py
```python
# Add to MessageProcessor class
from nlp_engine.services import FootballNLPService, ResponseGenerator

class MessageProcessor:
    def __init__(self):
        self.whatsapp_service = WhatsAppService()
        self.nlp_service = FootballNLPService()
        self.response_generator = ResponseGenerator()
    
    def generate_response(self, message_text, user):
        # Process with NLP
        query_result = self.nlp_service.process_query(message_text, user.phone_number)
        
        # Generate contextual response
        response = self.response_generator.generate_response(query_result, user)
        
        return response
```

### 5. Management Commands

#### nlp_engine/management/commands/load_training_data.py
```python
from django.core.management.base import BaseCommand
from nlp_engine.models import Intent, TrainingPhrase

class Command(BaseCommand):
    help = 'Load initial training data for NLP'
    
    def handle(self, *args, **options):
        # Create intents
        intents_data = [
            ('team_stats', 'Team statistics and information'),
            ('player_stats', 'Player statistics and information'),
            ('match_info', 'Match information and schedules'),
            ('odds_analysis', 'Betting odds analysis'),
            ('predictions', 'Match predictions'),
            ('standings', 'League standings and tables'),
            ('help', 'Help and usage information'),
            ('subscription', 'Subscription and premium features'),
        ]
        
        for intent_name, description in intents_data:
            intent, created = Intent.objects.get_or_create(
                name=intent_name,
                defaults={'description': description}
            )
            if created:
                self.stdout.write(f'Created intent: {intent_name}')
        
        # Load training phrases
        training_phrases = [
            ('team_stats', 'Como está o Flamengo?'),
            ('team_stats', 'Situação do Palmeiras na temporada'),
            ('team_stats', 'Estatísticas do Corinthians'),
            ('player_stats', 'Quantos gols o Messi fez?'),
            ('player_stats', 'Estatísticas do Cristiano Ronaldo'),
            ('match_info', 'Quando joga o Flamengo?'),
            ('match_info', 'Flamengo x Palmeiras que horas'),
            ('odds_analysis', 'Odds do jogo de hoje'),
            ('predictions', 'Quem vai ganhar Flamengo x Palmeiras'),
            ('standings', 'Tabela do Brasileirão'),
            ('help', 'Como usar este bot'),
            ('subscription', 'Quero ser premium'),
        ]
        
        for intent_name, phrase in training_phrases:
            intent = Intent.objects.get(name=intent_name)
            TrainingPhrase.objects.get_or_create(
                intent=intent,
                phrase=phrase,
                defaults={'language': 'pt'}
            )
        
        self.stdout.write('Training data loaded successfully')
```

## Integration Requirements

### Dependencies
```
# Add to requirements.txt
spacy>=3.7.0
```

### Install Portuguese model
```bash
python -m spacy download pt_core_news_sm
```

### Settings Configuration
```python
# Add to INSTALLED_APPS
'nlp_engine',

# NLP Configuration
NLP_CONFIDENCE_THRESHOLD = 0.7
NLP_DEFAULT_LANGUAGE = 'pt'
```

## Expected Deliverables

1. NLP service for intent recognition
2. Entity extraction for football-related terms
3. Training data management system
4. Integration with WhatsApp message processor
5. Response generation based on intent and entities
6. Analytics for query processing
7. Multi-language preparation structure

## Success Criteria

- Correctly identifies football-related intents with >70% accuracy
- Extracts team, player, and competition entities from user queries
- Generates appropriate responses based on user context
- Handles Portuguese language variations and slang
- Integrates seamlessly with existing WhatsApp service
- Provides fallback responses for unrecognized queries
- Supports premium/free user differentiation in responses
