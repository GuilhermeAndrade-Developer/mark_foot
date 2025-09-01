import re
import logging
import unicodedata
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from .models import Intent, EntityType, TrainingPhrase, EntityValue, UserQuery, IntentPattern, EntityRecognitionLog
from core.models import Team, Player, Competition, Match
from billing.models import UserSubscription

logger = logging.getLogger(__name__)


class FootballNLPService:
    """
    Main NLP service for processing football-related queries in Portuguese
    """
    
    def __init__(self):
        self.intent_patterns = self.load_intent_patterns()
        self.entity_cache = self.load_football_entities()
        
        # Portuguese-specific patterns
        self.team_indicators = [
            'time', 'clube', 'equipe', 'equipa', 'team', 'como esta', 'como ta', 
            'situacao', 'posicao', 'classificacao', 'tabela'
        ]
        
        self.player_indicators = [
            'jogador', 'atleta', 'player', 'estatisticas', 'gols', 'assists',
            'cartoes', 'idade', 'posicao', 'nacionalidade'
        ]
        
        self.match_indicators = [
            'jogo', 'partida', 'match', 'resultado', 'placar', 'quando joga',
            'proximo jogo', 'ultimo jogo', 'hoje', 'amanha'
        ]
        
        self.standings_indicators = [
            'tabela', 'classificacao', 'posicao', 'standings', 'ranking',
            'campeonato', 'brasileirao', 'liga'
        ]
        
        self.subscription_indicators = [
            'premium', 'assinar', 'assinatura', 'plano', 'pagar', 'pagamento',
            'cancelar', 'trial', 'gratuito', 'upgrade'
        ]
    
    def load_intent_patterns(self) -> Dict[str, List[Dict]]:
        """Load intent patterns from database"""
        patterns = {}
        
        try:
            for intent in Intent.objects.filter(is_active=True):
                patterns[intent.name] = []
                
                # Load patterns from IntentPattern model
                for pattern in intent.patterns.filter(is_active=True):
                    patterns[intent.name].append({
                        'pattern': pattern.pattern,
                        'type': pattern.pattern_type,
                        'weight': pattern.weight
                    })
                
                # Load training phrases as patterns
                for phrase in intent.training_phrases.filter(is_active=True):
                    patterns[intent.name].append({
                        'pattern': phrase.phrase,
                        'type': 'phrase',
                        'weight': 1.0
                    })
                    
        except Exception as e:
            logger.error(f"Error loading intent patterns: {e}")
            # Fallback patterns
            patterns = self._get_fallback_patterns()
        
        return patterns
    
    def load_football_entities(self) -> Dict[str, List[Dict]]:
        """Load football entities from database"""
        entities = {
            'teams': [],
            'players': [],
            'competitions': []
        }
        
        try:
            # Load teams
            for team in Team.objects.all():
                team_data = {
                    'id': team.id,
                    'name': team.name,
                    'short_name': team.short_name or '',
                    'tla': team.tla or '',
                    'synonyms': [team.name.lower()]
                }
                
                # Add variations
                if team.short_name:
                    team_data['synonyms'].append(team.short_name.lower())
                if team.tla:
                    team_data['synonyms'].append(team.tla.lower())
                
                entities['teams'].append(team_data)
            
            # Load players
            for player in Player.objects.select_related('team'):
                player_data = {
                    'id': player.external_id,
                    'name': player.name,
                    'short_name': player.short_name or '',
                    'team': player.team.name if player.team else '',
                    'synonyms': [player.name.lower()]
                }
                
                if player.short_name:
                    player_data['synonyms'].append(player.short_name.lower())
                
                entities['players'].append(player_data)
            
            # Load competitions
            for comp in Competition.objects.all():
                comp_data = {
                    'id': comp.id,
                    'name': comp.name,
                    'code': comp.code,
                    'synonyms': [comp.name.lower(), comp.code.lower()]
                }
                
                # Add common aliases
                if 'brasileirão' in comp.name.lower() or 'brasileiro' in comp.name.lower():
                    comp_data['synonyms'].extend(['brasileirão', 'brasileiro', 'série a'])
                
                entities['competitions'].append(comp_data)
                
        except Exception as e:
            logger.error(f"Error loading football entities: {e}")
        
        return entities
    
    def process_query(self, query_text: str, user_phone: str = None, user_id: int = None) -> Dict[str, Any]:
        """
        Main method to process user queries
        """
        start_time = datetime.now()
        
        try:
            # Normalize the query
            normalized_query = self.normalize_text(query_text)
            
            # Detect intent
            intent, intent_confidence = self.detect_intent(normalized_query)
            
            # Extract entities
            entities = self.extract_entities(normalized_query, intent)
            
            # Log the query
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            query_log = UserQuery.objects.create(
                query_text=query_text,
                normalized_query=normalized_query,
                detected_intent=intent,
                intent_confidence=intent_confidence,
                detected_entities=entities,
                processing_time_ms=processing_time,
                was_successful=True,
                whatsapp_user_phone=user_phone or '',
                user_id=user_id
            )
            
            # Log entity recognition
            self._log_entity_recognition(query_log, entities)
            
            result = {
                'intent': intent,
                'intent_confidence': intent_confidence,
                'entities': entities,
                'normalized_query': normalized_query,
                'processing_time_ms': processing_time,
                'success': True
            }
            
            logger.info(f"Query processed successfully: {intent} ({intent_confidence:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Error processing query '{query_text}': {e}")
            
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            UserQuery.objects.create(
                query_text=query_text,
                normalized_query=normalized_query if 'normalized_query' in locals() else '',
                detected_intent='error',
                processing_time_ms=processing_time,
                was_successful=False,
                error_message=str(e),
                whatsapp_user_phone=user_phone or '',
                user_id=user_id
            )
            
            return {
                'intent': 'help',
                'intent_confidence': 0.0,
                'entities': {},
                'normalized_query': query_text,
                'processing_time_ms': processing_time,
                'success': False,
                'error': str(e)
            }
    
    def normalize_text(self, text: str) -> str:
        """Normalize text by removing accents and converting to lowercase"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove accents
        text = unicodedata.normalize('NFD', text)
        text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def detect_intent(self, text: str) -> Tuple[str, float]:
        """Detect user intent from normalized text"""
        best_intent = 'help'
        best_confidence = 0.0
        
        # Check for specific patterns
        intent_scores = {}
        
        # Team statistics patterns
        if any(indicator in text for indicator in self.team_indicators):
            intent_scores['team_stats'] = 0.8
        
        # Player statistics patterns
        if any(indicator in text for indicator in self.player_indicators):
            intent_scores['player_stats'] = 0.8
        
        # Match information patterns
        if any(indicator in text for indicator in self.match_indicators):
            intent_scores['match_info'] = 0.8
        
        # Standings patterns
        if any(indicator in text for indicator in self.standings_indicators):
            intent_scores['standings'] = 0.8
        
        # Subscription patterns
        if any(indicator in text for indicator in self.subscription_indicators):
            intent_scores['subscription'] = 0.9
        
        # Betting odds patterns (premium feature)
        if any(word in text for word in ['odds', 'cotação', 'cotações', 'apostas', 'bet']):
            intent_scores['betting_odds'] = 0.9
        
        # Check database patterns
        for intent_name, patterns in self.intent_patterns.items():
            score = 0.0
            
            for pattern_data in patterns:
                pattern = pattern_data['pattern']
                pattern_type = pattern_data['type']
                weight = pattern_data['weight']
                
                if pattern_type == 'keyword':
                    keywords = pattern.split()
                    matches = sum(1 for keyword in keywords if keyword in text)
                    if keywords:
                        score += (matches / len(keywords)) * weight
                
                elif pattern_type == 'phrase':
                    if pattern in text:
                        score += weight
                
                elif pattern_type == 'regex':
                    try:
                        if re.search(pattern, text):
                            score += weight
                    except re.error:
                        continue
            
            if score > 0:
                intent_scores[intent_name] = max(intent_scores.get(intent_name, 0), score)
        
        # Select best intent
        if intent_scores:
            best_intent = max(intent_scores.items(), key=lambda x: x[1])[0]
            best_confidence = intent_scores[best_intent]
        
        # Apply confidence threshold
        threshold = 0.3
        if best_confidence < threshold:
            best_intent = 'help'
            best_confidence = 1.0
        
        return best_intent, min(best_confidence, 1.0)
    
    def extract_entities(self, text: str, intent: str) -> Dict[str, List[Dict]]:
        """Extract entities from text based on intent"""
        entities = {}
        
        # Extract teams
        teams = self._extract_teams(text)
        if teams:
            entities['teams'] = teams
        
        # Extract players
        players = self._extract_players(text)
        if players:
            entities['players'] = players
        
        # Extract competitions
        competitions = self._extract_competitions(text)
        if competitions:
            entities['competitions'] = competitions
        
        # Extract dates
        dates = self._extract_dates(text)
        if dates:
            entities['dates'] = dates
        
        # Extract numbers
        numbers = self._extract_numbers(text)
        if numbers:
            entities['numbers'] = numbers
        
        return entities
    
    def _extract_teams(self, text: str) -> List[Dict]:
        """Extract team entities from text"""
        found_teams = []
        
        for team_data in self.entity_cache['teams']:
            for synonym in team_data['synonyms']:
                if synonym in text:
                    # Calculate confidence based on exact match
                    confidence = 1.0 if synonym == team_data['name'].lower() else 0.8
                    
                    found_teams.append({
                        'id': team_data['id'],
                        'name': team_data['name'],
                        'matched_text': synonym,
                        'confidence': confidence
                    })
                    break
        
        # Remove duplicates and sort by confidence
        unique_teams = {}
        for team in found_teams:
            if team['id'] not in unique_teams or team['confidence'] > unique_teams[team['id']]['confidence']:
                unique_teams[team['id']] = team
        
        return list(unique_teams.values())
    
    def _extract_players(self, text: str) -> List[Dict]:
        """Extract player entities from text"""
        found_players = []
        
        for player_data in self.entity_cache['players']:
            for synonym in player_data['synonyms']:
                if len(synonym) > 3 and synonym in text:  # Avoid short matches
                    confidence = 1.0 if synonym == player_data['name'].lower() else 0.8
                    
                    found_players.append({
                        'id': player_data['id'],
                        'name': player_data['name'],
                        'team': player_data['team'],
                        'matched_text': synonym,
                        'confidence': confidence
                    })
                    break
        
        # Remove duplicates
        unique_players = {}
        for player in found_players:
            if player['id'] not in unique_players or player['confidence'] > unique_players[player['id']]['confidence']:
                unique_players[player['id']] = player
        
        return list(unique_players.values())
    
    def _extract_competitions(self, text: str) -> List[Dict]:
        """Extract competition entities from text"""
        found_competitions = []
        
        for comp_data in self.entity_cache['competitions']:
            for synonym in comp_data['synonyms']:
                if synonym in text:
                    confidence = 1.0 if synonym == comp_data['name'].lower() else 0.8
                    
                    found_competitions.append({
                        'id': comp_data['id'],
                        'name': comp_data['name'],
                        'code': comp_data['code'],
                        'matched_text': synonym,
                        'confidence': confidence
                    })
                    break
        
        # Remove duplicates
        unique_competitions = {}
        for comp in found_competitions:
            if comp['id'] not in unique_competitions or comp['confidence'] > unique_competitions[comp['id']]['confidence']:
                unique_competitions[comp['id']] = comp
        
        return list(unique_competitions.values())
    
    def _extract_dates(self, text: str) -> List[Dict]:
        """Extract date entities from text"""
        dates = []
        
        # Portuguese date patterns
        date_patterns = [
            (r'hoje', 'today'),
            (r'amanhã', 'tomorrow'),
            (r'ontem', 'yesterday'),
            (r'próximo (jogo|domingo|segunda|terça|quarta|quinta|sexta|sábado)', 'next_week'),
            (r'(\d{1,2})/(\d{1,2})/(\d{4})', 'date_format'),
            (r'(\d{1,2}) de (janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)', 'month_format')
        ]
        
        for pattern, date_type in date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                dates.append({
                    'text': match.group(),
                    'type': date_type,
                    'confidence': 0.9
                })
        
        return dates
    
    def _extract_numbers(self, text: str) -> List[Dict]:
        """Extract number entities from text"""
        numbers = []
        
        # Number patterns
        number_patterns = [
            r'\b\d+\b',  # Simple numbers
            r'\b\d+:\d+\b',  # Score format
            r'\b\d+x\d+\b',  # Score format alternative
        ]
        
        for pattern in number_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                numbers.append({
                    'text': match.group(),
                    'value': match.group(),
                    'confidence': 0.8
                })
        
        return numbers
    
    def _log_entity_recognition(self, query: UserQuery, entities: Dict) -> None:
        """Log entity recognition results"""
        try:
            for entity_type, entity_list in entities.items():
                for entity in entity_list:
                    EntityRecognitionLog.objects.create(
                        query=query,
                        entity_type=entity_type,
                        extracted_text=entity.get('matched_text', entity.get('text', '')),
                        canonical_value=entity.get('name', entity.get('value', '')),
                        confidence_score=entity.get('confidence', 0.0),
                        extraction_method='nlp'
                    )
        except Exception as e:
            logger.error(f"Error logging entity recognition: {e}")
    
    def _get_fallback_patterns(self) -> Dict[str, List[Dict]]:
        """Fallback patterns when database is not available"""
        return {
            'team_stats': [
                {'pattern': 'como está time clube equipe', 'type': 'keyword', 'weight': 1.0},
                {'pattern': 'situação posição classificação', 'type': 'keyword', 'weight': 1.0}
            ],
            'player_stats': [
                {'pattern': 'jogador atleta player estatisticas', 'type': 'keyword', 'weight': 1.0},
                {'pattern': 'gols assists cartões', 'type': 'keyword', 'weight': 1.0}
            ],
            'standings': [
                {'pattern': 'tabela classificação ranking', 'type': 'keyword', 'weight': 1.0}
            ],
            'subscription': [
                {'pattern': 'premium assinar assinatura plano', 'type': 'keyword', 'weight': 1.0}
            ]
        }


class ResponseGenerator:
    """
    Generates responses based on NLP processing results
    """
    
    def __init__(self):
        self.nlp_service = FootballNLPService()
    
    def generate_response(self, query_result: Dict, user_phone: str = None) -> str:
        """Generate response based on query result and user context"""
        intent = query_result.get('intent', 'help')
        entities = query_result.get('entities', {})
        
        # Check user subscription status
        user = self._get_user_context(user_phone)
        is_premium = self._is_premium_user(user)
        
        try:
            if intent == 'team_stats':
                return self.generate_team_stats_response(entities, user, is_premium)
            elif intent == 'player_stats':
                return self.generate_player_stats_response(entities, user, is_premium)
            elif intent == 'standings':
                return self.generate_standings_response(entities, user, is_premium)
            elif intent == 'betting_odds':
                return self.generate_betting_odds_response(entities, user, is_premium)
            elif intent == 'subscription':
                return self.generate_subscription_response(entities, user)
            elif intent == 'match_info':
                return self.generate_match_info_response(entities, user, is_premium)
            else:
                return self.generate_help_response()
                
        except Exception as e:
            logger.error(f"Error generating response for intent {intent}: {e}")
            return self.generate_error_response()
    
    def generate_team_stats_response(self, entities: Dict, user: Any, is_premium: bool) -> str:
        """Generate response for team statistics queries"""
        teams = entities.get('teams', [])
        
        if not teams:
            return """🤔 Não consegui identificar o time que você quer saber.

Exemplos de como perguntar:
⚽ "Como está o Flamengo?"
⚽ "Situação do Palmeiras"
⚽ "Posição do Corinthians na tabela"

Digite o nome completo ou apelido do time!"""
        
        team = teams[0]  # Get first team found
        team_name = team['name']
        
        # Basic response for all users
        response = f"⚽ **{team_name}**\n\n"
        
        try:
            # Get team from database
            team_obj = Team.objects.get(id=team['id'])
            
            # Get latest standing
            from core.models import Standing
            latest_standing = Standing.objects.filter(
                team=team_obj,
                type='TOTAL'
            ).order_by('-snapshot_date').first()
            
            if latest_standing:
                response += f"📊 **Classificação Atual:**\n"
                response += f"🏆 {latest_standing.position}º lugar - {latest_standing.points} pontos\n"
                response += f"⚽ {latest_standing.goals_for} gols feitos | {latest_standing.goals_against} gols sofridos\n"
                response += f"📈 {latest_standing.won}V {latest_standing.draw}E {latest_standing.lost}D\n\n"
            
            # Get recent matches
            recent_matches = Match.objects.filter(
                Q(home_team=team_obj) | Q(away_team=team_obj),
                status='FINISHED'
            ).order_by('-utc_date')[:3]
            
            if recent_matches:
                response += "📅 **Últimos Jogos:**\n"
                for match in recent_matches:
                    home_score = match.home_team_score or 0
                    away_score = match.away_team_score or 0
                    date_str = match.utc_date.strftime('%d/%m')
                    
                    if match.home_team == team_obj:
                        result = "🟢" if home_score > away_score else "🔴" if home_score < away_score else "🟡"
                        response += f"{result} {match.home_team.short_name or match.home_team.name} {home_score} x {away_score} {match.away_team.short_name or match.away_team.name} ({date_str})\n"
                    else:
                        result = "🟢" if away_score > home_score else "🔴" if away_score < home_score else "🟡"
                        response += f"{result} {match.away_team.short_name or match.away_team.name} {away_score} x {home_score} {match.home_team.short_name or match.home_team.name} ({date_str})\n"
                
                response += "\n"
            
        except Exception as e:
            logger.error(f"Error getting team data: {e}")
            response += "📊 Dados básicos disponíveis\n\n"
        
        # Premium upsell for free users
        if not is_premium:
            response += """🔒 **Quer mais detalhes?**

💎 Mark Foot Premium - R$ 19,90/mês
✅ Análises detalhadas de desempenho
✅ Estatísticas de jogadores
✅ Histórico completo de partidas
✅ Previsões com IA

Digite /premium para assinar!"""
        
        return response
    
    def generate_player_stats_response(self, entities: Dict, user: Any, is_premium: bool) -> str:
        """Generate response for player statistics queries"""
        players = entities.get('players', [])
        
        if not players:
            return """🤔 Não consegui identificar o jogador que você quer saber.

Exemplos de como perguntar:
👤 "Estatísticas do Gabigol"
👤 "Como está o Messi?"
👤 "Gols do Neymar"

Digite o nome completo do jogador!"""
        
        player = players[0]
        player_name = player['name']
        
        response = f"👤 **{player_name}**\n"
        if player.get('team'):
            response += f"⚽ {player['team']}\n\n"
        
        if not is_premium:
            response += """🔒 **Estatísticas Completas - Premium**

Para acessar estatísticas detalhadas de jogadores:

💎 Mark Foot Premium - R$ 19,90/mês
✅ Gols, assistências e cartões
✅ Minutos jogados por temporada
✅ Performance por competição
✅ Histórico de transferências
✅ Comparações entre jogadores

Digite /premium para assinar!"""
        else:
            # Premium users get detailed stats
            try:
                from core.models import PlayerStatistics
                player_obj = Player.objects.get(external_id=player['id'])
                
                latest_stats = PlayerStatistics.objects.filter(
                    player=player_obj
                ).order_by('-season__start_date').first()
                
                if latest_stats:
                    response += f"📊 **Temporada Atual:**\n"
                    response += f"⚽ {latest_stats.goals} gols\n"
                    response += f"🎯 {latest_stats.assists} assistências\n"
                    response += f"🟨 {latest_stats.yellow_cards} cartões amarelos\n"
                    response += f"🟥 {latest_stats.red_cards} cartões vermelhos\n"
                    response += f"⏱️ {latest_stats.minutes_played} minutos jogados\n"
                    response += f"📋 {latest_stats.appearances} jogos\n"
                else:
                    response += "📊 Estatísticas em atualização...\n"
                    
            except Exception as e:
                logger.error(f"Error getting player stats: {e}")
                response += "📊 Estatísticas temporariamente indisponíveis\n"
        
        return response
    
    def generate_standings_response(self, entities: Dict, user: Any, is_premium: bool) -> str:
        """Generate response for standings queries"""
        competitions = entities.get('competitions', [])
        
        # Default to Brasileirão if no competition specified
        if not competitions:
            try:
                brasileirao = Competition.objects.filter(
                    Q(name__icontains='brasileiro') | Q(code='BSA')
                ).first()
                if brasileirao:
                    competitions = [{'id': brasileirao.id, 'name': brasileirao.name}]
            except:
                pass
        
        if not competitions:
            return """🏆 **Tabelas Disponíveis:**

Exemplos de como perguntar:
📊 "Tabela do Brasileirão"
📊 "Classificação da Champions"
📊 "Ranking da Copa do Brasil"

Que competição você quer ver?"""
        
        competition = competitions[0]
        comp_name = competition['name']
        
        response = f"🏆 **{comp_name}**\n\n"
        
        try:
            from core.models import Standing
            comp_obj = Competition.objects.get(id=competition['id'])
            
            # Get latest standings
            standings = Standing.objects.filter(
                competition=comp_obj,
                type='TOTAL'
            ).order_by('-snapshot_date', 'position')[:10]  # Top 10
            
            if standings:
                response += "📊 **Classificação:**\n"
                for standing in standings:
                    position_emoji = "🥇" if standing.position == 1 else "🥈" if standing.position == 2 else "🥉" if standing.position == 3 else f"{standing.position}º"
                    team_name = standing.team.short_name or standing.team.name
                    response += f"{position_emoji} {team_name} - {standing.points}pts ({standing.won}V {standing.draw}E {standing.lost}D)\n"
                
                response += f"\n📅 Atualizado em: {standings[0].snapshot_date.strftime('%d/%m/%Y')}\n\n"
            else:
                response += "📊 Tabela em atualização...\n\n"
                
        except Exception as e:
            logger.error(f"Error getting standings: {e}")
            response += "📊 Tabela temporariamente indisponível\n\n"
        
        # Premium features
        if not is_premium:
            response += """💎 **Premium Features:**
✅ Tabela completa (todos os times)
✅ Histórico de classificações
✅ Estatísticas avançadas
✅ Projeções matemáticas

Digite /premium para mais!"""
        
        return response
    
    def generate_betting_odds_response(self, entities: Dict, user: Any, is_premium: bool) -> str:
        """Generate response for betting odds queries"""
        if not is_premium:
            return """🎲 **Odds e Cotações - Premium**

Para acessar análises completas de odds e explicações sobre cotações:

💎 Mark Foot Premium - R$ 19,90/mês
✅ Análise detalhada de odds
✅ Explicação do "porquê" das cotações
✅ Value bets identificados
✅ Alertas de mudanças importantes

Digite /premium para assinar!"""
        
        # Premium odds analysis would go here
        return """🎲 **Análise de Odds**

🔄 Sistema em desenvolvimento
📊 Breve: Análises completas de cotações
🎯 Aguarde: Value bets e insights

Obrigado pela sua assinatura Premium! 💎"""
    
    def generate_subscription_response(self, entities: Dict, user: Any) -> str:
        """Generate response for subscription queries"""
        return """💎 **Mark Foot Premium**

🎯 **Benefícios:**
✅ Consultas ilimitadas
✅ Estatísticas completas de jogadores
✅ Análise de odds e value bets
✅ Tabelas completas de classificação
✅ Previsões com IA
✅ Alertas personalizados
✅ Suporte prioritário

💰 **Apenas R$ 19,90/mês**

🔗 Para assinar: [LINK_PAGAMENTO]

📞 Dúvidas? Responda esta mensagem!"""
    
    def generate_match_info_response(self, entities: Dict, user: Any, is_premium: bool) -> str:
        """Generate response for match information queries"""
        teams = entities.get('teams', [])
        dates = entities.get('dates', [])
        
        response = "⚽ **Informações de Jogos**\n\n"
        
        if teams:
            team_name = teams[0]['name']
            response += f"🔍 Buscando jogos do {team_name}...\n\n"
            
            try:
                team_obj = Team.objects.get(id=teams[0]['id'])
                
                # Get upcoming matches
                upcoming = Match.objects.filter(
                    Q(home_team=team_obj) | Q(away_team=team_obj),
                    Q(status='SCHEDULED') | Q(status='LIVE'),
                    utc_date__gte=timezone.now()
                ).order_by('utc_date')[:3]
                
                if upcoming:
                    response += "📅 **Próximos Jogos:**\n"
                    for match in upcoming:
                        date_str = match.utc_date.strftime('%d/%m %H:%M')
                        home_team = match.home_team.short_name or match.home_team.name
                        away_team = match.away_team.short_name or match.away_team.name
                        response += f"⚽ {home_team} x {away_team}\n📅 {date_str}\n🏆 {match.competition.name}\n\n"
                else:
                    response += "📅 Nenhum jogo agendado encontrado\n\n"
                    
            except Exception as e:
                logger.error(f"Error getting match info: {e}")
                response += "📅 Informações temporariamente indisponíveis\n\n"
        
        else:
            response += """Exemplos de como perguntar:
⚽ "Quando joga o Flamengo?"
⚽ "Próximo jogo do Palmeiras"
⚽ "Jogos de hoje"

Que time você quer saber?"""
        
        return response
    
    def generate_help_response(self) -> str:
        """Generate help response"""
        return """🤖 **Mark Foot - Seu Assistente de Futebol!**

Exemplos de perguntas:
⚽ "Como está o Flamengo?"
🏆 "Tabela do Brasileirão"
👤 "Estatísticas do Messi"
📅 "Quando joga o Palmeiras?"
🎲 "Odds Flamengo x Palmeiras" (Premium)

**Comandos:**
/premium - Informações sobre assinatura
/help - Este menu de ajuda

💬 Digite naturalmente suas perguntas sobre futebol!"""
    
    def generate_error_response(self) -> str:
        """Generate error response"""
        return """😅 **Ops! Algo deu errado...**

Tente reformular sua pergunta ou use um dos exemplos:

⚽ "Como está o [nome do time]?"
🏆 "Tabela do Brasileirão"
👤 "Estatísticas do [nome do jogador]"

Se o problema persistir, nossa equipe será notificada! 🛠️"""
    
    def _get_user_context(self, user_phone: str) -> Any:
        """Get user context from phone number"""
        if not user_phone:
            return None
        
        try:
            from whatsapp_integration.models import WhatsAppUser
            return WhatsAppUser.objects.filter(phone_number=user_phone).first()
        except:
            return None
    
    def _is_premium_user(self, user: Any) -> bool:
        """Check if user has premium subscription"""
        if not user:
            return False
        
        try:
            from billing.models import UserSubscription
            if hasattr(user, 'user'):
                django_user = user.user
            else:
                # For WhatsAppUser, try to find linked Django user
                return False  # For now, assume no premium until proper user linking
            
            return UserSubscription.objects.filter(
                user=django_user,
                status='active'
            ).exists()
        except:
            return False
