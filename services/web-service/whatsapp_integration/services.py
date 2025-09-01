import requests
import json
import logging
from django.conf import settings
from .models import WhatsAppUser, WhatsAppMessage, WhatsAppSession
from billing.models import UserSubscription
from ai_analytics.services.base_service import BaseAIService
from core.models import Team, Match, Player
from nlp_engine.services import FootballNLPService, ResponseGenerator

logger = logging.getLogger(__name__)

class WhatsAppService:
    """Service for sending messages via WhatsApp Business API"""
    
    def __init__(self):
        self.api_url = f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_ID}/messages"
        self.headers = {
            'Authorization': f'Bearer {settings.WHATSAPP_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
    
    def send_text_message(self, phone_number, message):
        """Send a text message"""
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {"body": message}
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            raise
    
    def send_interactive_message(self, phone_number, header, body, footer, buttons):
        """Send an interactive message with buttons"""
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "header": {"type": "text", "text": header},
                "body": {"text": body},
                "footer": {"text": footer},
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {"id": btn["id"], "title": btn["title"]}
                        } for btn in buttons
                    ]
                }
            }
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error sending WhatsApp interactive message: {str(e)}")
            raise

    def send_premium_promotion(self, phone_number):
        """Send premium subscription promotion"""
        message = """
🏆 Mark Foot Premium

✅ Consultas ilimitadas
✅ Análise completa de odds
✅ Previsões com IA
✅ Alertas personalizados
✅ Estatísticas avançadas

💰 Apenas R$ 19,90/mês

Para assinar: Digite *PREMIUM* ou acesse nosso site
        """.strip()
        
        return self.send_text_message(phone_number, message)

class MessageProcessor:
    """Process incoming WhatsApp messages"""
    
    def __init__(self):
        self.whatsapp_service = WhatsAppService()
        self.nlp_service = FootballNLPService()
        self.response_generator = ResponseGenerator()
    
    def process_message(self, webhook_data):
        """Process incoming webhook message"""
        try:
            # Extract message data from webhook
            entry = webhook_data.get('entry', [])[0]
            changes = entry.get('changes', [])[0]
            value = changes.get('value', {})
            
            # Check if it's a message
            if 'messages' not in value:
                return
            
            message_data = value['messages'][0]
            phone_number = message_data['from']
            message_id = message_data['id']
            
            # Get or create WhatsApp user
            whatsapp_user, created = WhatsAppUser.objects.get_or_create(
                phone_number=phone_number,
                defaults={
                    'display_name': value.get('contacts', [{}])[0].get('profile', {}).get('name', '')
                }
            )
            
            # Save incoming message
            message_content = self._extract_message_content(message_data)
            WhatsAppMessage.objects.create(
                whatsapp_user=whatsapp_user,
                message_id=message_id,
                message_type=message_data['type'],
                content=message_content,
                is_incoming=True
            )
            
            # Process the message
            self._handle_user_message(whatsapp_user, message_content)
            
        except Exception as e:
            logger.error(f"Error processing WhatsApp message: {str(e)}")
    
    def _extract_message_content(self, message_data):
        """Extract content from message based on type"""
        message_type = message_data['type']
        
        if message_type == 'text':
            return message_data['text']['body']
        elif message_type == 'interactive':
            if 'button_reply' in message_data['interactive']:
                return message_data['interactive']['button_reply']['id']
            elif 'list_reply' in message_data['interactive']:
                return message_data['interactive']['list_reply']['id']
        
        return f"Unsupported message type: {message_type}"
    
    def _handle_user_message(self, whatsapp_user, message_content):
        """Handle user message and send appropriate response"""
        message_lower = message_content.lower().strip()
        
        # Check rate limiting
        if not whatsapp_user.can_make_query():
            self._send_rate_limit_message(whatsapp_user)
            return
        
        # Handle premium subscription request
        if 'premium' in message_lower:
            self._handle_premium_request(whatsapp_user)
            return
        
        # Handle help requests (before NLP processing to avoid counting against limits)
        if any(keyword in message_lower for keyword in ['ajuda', 'help', 'como', 'menu']):
            self._send_help_message(whatsapp_user)
            return
        
        # Use NLP to process the query
        whatsapp_user.increment_query_count()
        
        try:
            # Process query with NLP service
            query_result = self.nlp_service.process_query(
                message_content, 
                user_phone=whatsapp_user.phone_number,
                user_id=whatsapp_user.id
            )
            
            # Generate response based on NLP results
            response_text = self.response_generator.generate_response(
                query_result, 
                user_phone=whatsapp_user.phone_number
            )
            
            # Send response
            self.whatsapp_service.send_text_message(whatsapp_user.phone_number, response_text)
            
            # Log the successful interaction
            WhatsAppMessage.objects.create(
                whatsapp_user=whatsapp_user,
                message_type='text',
                content=response_text,
                is_incoming=False
            )
            
        except Exception as e:
            logger.error(f"Error processing message with NLP: {str(e)}")
            # Fallback to simple processing
            self._handle_football_query_fallback(whatsapp_user, message_content)
    
    def _send_rate_limit_message(self, whatsapp_user):
        """Send rate limit exceeded message"""
        message = """
⚠️ Limite de consultas diárias atingido!

Usuários gratuitos têm direito a 5 consultas por dia.

🏆 Quer consultas ilimitadas? 
Digite *PREMIUM* para conhecer nossos planos!
        """.strip()
        
        self.whatsapp_service.send_text_message(whatsapp_user.phone_number, message)
    
    def _handle_premium_request(self, whatsapp_user):
        """Handle premium subscription request"""
        self.whatsapp_service.send_premium_promotion(whatsapp_user.phone_number)
    
    def _handle_football_query_fallback(self, whatsapp_user, query):
        """Fallback football query handler when NLP fails"""
        try:
            # Use existing simple processing as fallback
            response = self._process_football_query(query)
            
            # Send response
            self.whatsapp_service.send_text_message(whatsapp_user.phone_number, response)
            
        except Exception as e:
            logger.error(f"Error in fallback football query processing: {str(e)}")
            error_message = """😅 Desculpe, estou com dificuldades técnicas no momento.

Tente reformular sua pergunta ou use comandos mais simples como:
⚽ "Como está o Flamengo?"
📊 "Tabela do Brasileirão"

Nossa equipe foi notificada do problema! 🛠️"""
            self.whatsapp_service.send_text_message(whatsapp_user.phone_number, error_message)
    
    def _process_football_query(self, query):
        """Process football query using AI analytics"""
        # Simple keyword-based processing (can be enhanced with NLP)
        query_lower = query.lower()
        
        # Team information queries
        if 'palmeiras' in query_lower:
            return self._get_team_info('Palmeiras')
        elif 'flamengo' in query_lower:
            return self._get_team_info('Flamengo')
        elif 'corinthians' in query_lower:
            return self._get_team_info('Corinthians')
        elif 'santos' in query_lower:
            return self._get_team_info('Santos')
        
        # Match queries
        elif any(word in query_lower for word in ['jogo', 'partida', 'próximo']):
            return self._get_upcoming_matches()
        
        # Results queries
        elif any(word in query_lower for word in ['resultado', 'placar']):
            return self._get_recent_results()
        
        # Default football response
        return """
⚽ Mark Foot - Seu assistente de futebol!

Posso ajudar com:
• Informações de times
• Próximos jogos
• Resultados recentes
• Estatísticas de jogadores

Exemplo: "Como está o Palmeiras?" ou "Próximos jogos do Flamengo"
        """.strip()
    
    def _get_team_info(self, team_name):
        """Get team information"""
        try:
            team = Team.objects.filter(name__icontains=team_name).first()
            if team:
                return f"""
🏆 {team.name}

📊 Informações básicas:
• Liga: {team.league}
• Fundação: {team.founded or 'N/A'}

⚽ Para mais estatísticas detalhadas, considere nosso plano Premium!
                """.strip()
            else:
                return f"Desculpe, não encontrei informações sobre o time {team_name}."
        except Exception as e:
            logger.error(f"Error getting team info: {str(e)}")
            return "Erro ao buscar informações do time."
    
    def _get_upcoming_matches(self):
        """Get upcoming matches"""
        try:
            upcoming_matches = Match.objects.filter(
                status='SCHEDULED'
            ).order_by('utc_date')[:5]
            
            if upcoming_matches:
                response = "⚽ Próximos jogos:\n\n"
                for match in upcoming_matches:
                    response += f"🏟️ {match.home_team.name} vs {match.away_team.name}\n"
                    response += f"📅 {match.utc_date.strftime('%d/%m %H:%M')}\n\n"
                return response
            else:
                return "Não há jogos agendados no momento."
        except Exception as e:
            logger.error(f"Error getting upcoming matches: {str(e)}")
            return "Erro ao buscar próximos jogos."
    
    def _get_recent_results(self):
        """Get recent match results"""
        try:
            recent_matches = Match.objects.filter(
                status='FINISHED'
            ).order_by('-utc_date')[:5]
            
            if recent_matches:
                response = "📊 Resultados recentes:\n\n"
                for match in recent_matches:
                    response += f"⚽ {match.home_team.name} {match.score_home} x {match.score_away} {match.away_team.name}\n"
                    response += f"📅 {match.utc_date.strftime('%d/%m')}\n\n"
                return response
            else:
                return "Não há resultados recentes disponíveis."
        except Exception as e:
            logger.error(f"Error getting recent results: {str(e)}")
            return "Erro ao buscar resultados recentes."
    
    def _send_help_message(self, whatsapp_user):
        """Send help message"""
        message = """
🤖 Mark Foot - Assistente de Futebol

Como posso ajudar:

⚽ Informações de times:
• "Como está o Palmeiras?"
• "Estatísticas do Flamengo"

🏟️ Jogos e resultados:
• "Próximos jogos"
• "Resultados de ontem"

🏆 Premium:
• Digite "PREMIUM" para planos

Digite sua pergunta sobre futebol!
        """.strip()
        
        self.whatsapp_service.send_text_message(whatsapp_user.phone_number, message)
    
    def _send_default_message(self, whatsapp_user):
        """Send default welcome message"""
        message = """
👋 Olá! Sou o assistente Mark Foot!

Posso ajudar com informações sobre:
⚽ Times e jogadores
🏟️ Jogos e resultados
📊 Estatísticas

Digite "AJUDA" para mais opções ou faça sua pergunta sobre futebol!
        """.strip()
        
        self.whatsapp_service.send_text_message(whatsapp_user.phone_number, message)
