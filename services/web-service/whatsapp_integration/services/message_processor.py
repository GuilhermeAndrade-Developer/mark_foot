import logging
from django.utils import timezone
from ..models import WhatsAppUser, WhatsAppMessage, WhatsAppSession
from .subscription_service import WhatsAppSubscriptionService
from .whatsapp_service import WhatsAppService
from billing.models import UserSubscription
from ai_analytics.services.base_service import BaseAIService
from core.models import Team, Match, Player
from nlp_engine.services import FootballNLPService, ResponseGenerator

logger = logging.getLogger(__name__)

class MessageProcessor:
    """Process incoming WhatsApp messages"""
    
    def __init__(self):
        self.whatsapp_service = WhatsAppService()
        self.nlp_service = FootballNLPService()
        self.response_generator = ResponseGenerator()
        self.subscription_service = WhatsAppSubscriptionService()
    
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
        
        # Update subscription status first
        self.subscription_service.check_subscription_status(whatsapp_user)
        
        # Handle subscription commands
        if message_lower in ['/trial', 'trial', 'teste', 'teste gratis']:
            self._handle_trial_request(whatsapp_user)
            return
            
        if message_lower in ['/premium', 'premium', 'assinar']:
            self._handle_premium_request(whatsapp_user)
            return
            
        if message_lower in ['/status', 'status', 'minha conta']:
            self._handle_status_request(whatsapp_user)
            return
            
        if message_lower in ['/renovar', 'renovar']:
            self._handle_renewal_request(whatsapp_user)
            return
            
        if message_lower in ['/cancelar', 'cancelar']:
            self._handle_cancellation_request(whatsapp_user)
            return
        
        # Check rate limiting for regular queries
        if not whatsapp_user.can_make_query():
            self._send_rate_limit_message(whatsapp_user)
            return
        
        # Handle help requests (before NLP processing to avoid counting against limits)
        if any(keyword in message_lower for keyword in ['ajuda', 'help', 'como', 'menu']):
            self._send_help_message(whatsapp_user)
            return
        
        # Handle live matches commands
        if message_lower in ['/ao vivo', 'ao vivo', 'live', '/live']:
            self._handle_live_matches_command(whatsapp_user)
            return
            
        if message_lower.startswith('/odds') or 'odds' in message_lower:
            self._handle_odds_command(whatsapp_user, message_content)
            return
            
        if message_lower.startswith('/alertas') or 'alertas' in message_lower:
            self._handle_alerts_command(whatsapp_user, message_content)
            return
            
        if message_lower in ['/proximos', 'proximos', 'próximos']:
            self._handle_upcoming_matches_command(whatsapp_user)
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
        # Check current status for appropriate message
        status = whatsapp_user.subscription_status
        daily_used = whatsapp_user.daily_queries_count
        daily_limit = whatsapp_user.get_daily_limit()
        
        if status == 'expired':
            message = f"""⏰ Sua assinatura expirou!

💎 Quer consultas ilimitadas?
Premium: R$ 19,90/mês
Pro: R$ 49,90/mês

🆓 Teste grátis 7 dias: Digite /trial
💳 Assinar agora: Digite /premium"""
        
        elif status == 'trial_ended':
            message = f"""🏁 Seu teste gratuito terminou!

Renove agora e continue aproveitando:
✅ Consultas ilimitadas
✅ Análise completa de odds
✅ Previsões com IA

Digite /renovar para continuar"""
        else:  # trial_ended
            message = f"""⚠️ Limite diário atingido! ({daily_used}/{daily_limit})

Gostou? Assine agora:
💎 Premium: R$ 19,90/mês
🏆 Pro: R$ 49,90/mês

Digite /premium para assinar"""
        
        self.whatsapp_service.send_text_message(whatsapp_user.phone_number, message)
    
    def _handle_trial_request(self, whatsapp_user):
        """Handle trial subscription request"""
        result = self.subscription_service.start_trial(whatsapp_user)
        
        if result['success']:
            message = f"""🎉 Trial Premium ativado!

✅ 7 dias de acesso completo
✅ Todas as funcionalidades Premium
⏰ Válido até {result['trial_end_date'].strftime('%d/%m/%Y')}

Aproveite! Digite qualquer pergunta sobre futebol."""
        else:
            message = f"""❌ Não foi possível ativar o trial.

{result['message']}

💳 Veja nossos planos: /premium"""
        
        self.whatsapp_service.send_text_message(whatsapp_user.phone_number, message)
    
    def _handle_premium_request(self, whatsapp_user):
        """Handle premium subscription request"""
        message = f"""🏆 Mark Foot - Planos Premium

🥉 Premium (R$ 19,90/mês):
✅ Consultas ilimitadas
✅ Análise de odds
✅ Previsões IA

🥇 Pro (R$ 49,90/mês):
✅ Tudo do Premium +
✅ Relatórios PDF
✅ Suporte prioritário
✅ Grupos VIP

🔗 Escolha seu plano:"""
        
        # Send interactive message with plan options
        buttons = [
            {"id": "plan_premium", "title": "Premium R$ 19,90"},
            {"id": "plan_pro", "title": "Pro R$ 49,90"},
            {"id": "trial_7days", "title": "Trial 7 dias"}
        ]
        
        try:
            self.whatsapp_service.send_interactive_message(
                whatsapp_user.phone_number,
                "🏆 Mark Foot Premium",
                message,
                "Clique na opção desejada",
                buttons
            )
        except:
            # Fallback to text message
            message += "\n\nPara assinar:\n• Premium: Digite 'premium'\n• Pro: Digite 'pro'\n• Trial: Digite '/trial'"
            self.whatsapp_service.send_text_message(whatsapp_user.phone_number, message)
    
    def _handle_status_request(self, whatsapp_user):
        """Handle subscription status request"""
        info = self.subscription_service.get_subscription_info(whatsapp_user)
        status = info['status']
        
        if status == 'free':
            daily_used = info['daily_used']
            daily_limit = info['daily_limit']
            message = f"""🆓 Status da Conta

🆓 Plano: Gratuito
📱 Consultas hoje: {daily_used}/{daily_limit}
📅 Renovação: Diária

💎 Upgrade para Premium: /premium"""
        
        elif status in ['premium', 'pro']:
            days_left = info.get('days_remaining', 0)
            message = f"""💎 Status da Conta

💎 Plano: {status.title()}
📅 Expira em: {days_left} dias
📱 Consultas: Ilimitadas
✅ Status: Ativo

❌ Cancelar: /cancelar"""
        
        elif status == 'expired':
            message = f"""⏰ Status da Conta

⏰ Status: Expirado
📱 Consultas: Limitado (5/dia)

🔄 Renovar: /renovar"""
        
        elif status == 'trial':
            trial_days = info.get('trial_days_remaining', 0)
            message = f"""🎉 Status da Conta

🎉 Plano: Trial Premium
📅 Expira em: {trial_days} dias
📱 Consultas: Ilimitadas
✅ Status: Ativo

💎 Assinar antes do fim: /premium"""
        
        else:
            message = f"""📊 Status da Conta

Status: {status}
Consultas hoje: {info['daily_used']}/{info['daily_limit'] or '∞'}

Para mais informações: /premium"""
        
        self.whatsapp_service.send_text_message(whatsapp_user.phone_number, message)
    
    def _handle_renewal_request(self, whatsapp_user):
        """Handle subscription renewal request"""
        if whatsapp_user.subscription_status in ['expired', 'cancelled', 'trial_ended']:
            self._handle_premium_request(whatsapp_user)
        else:
            message = """✅ Sua assinatura ainda está ativa!

📊 Veja o status: /status
❓ Dúvidas? Responda esta mensagem"""
            self.whatsapp_service.send_text_message(whatsapp_user.phone_number, message)
    
    def _handle_cancellation_request(self, whatsapp_user):
        """Handle subscription cancellation request"""
        if whatsapp_user.subscription_status in ['premium', 'pro']:
            result = self.subscription_service.cancel_subscription(whatsapp_user)
            
            if result['success']:
                message = """😞 Assinatura cancelada com sucesso.

Você ainda pode usar os benefícios até o fim do período pago.

💭 Sua opinião é importante! O que posso melhorar?
🔄 Reativar: /premium"""
            else:
                message = """❌ Erro ao cancelar assinatura.

Por favor, tente novamente ou entre em contato conosco."""
        else:
            message = """ℹ️ Você não possui assinatura ativa para cancelar.

📊 Status atual: /status
💎 Conhecer planos: /premium"""
        
        self.whatsapp_service.send_text_message(whatsapp_user.phone_number, message)
    
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
• "Próximos jogos" ou /proximos
• "Ao vivo" ou /live
• "Resultados de ontem"

💰 Odds e apostas (Premium):
• /odds - Ver odds atuais
• /alertas - Configurar alertas

🏆 Premium:
• Digite "PREMIUM" para planos

Digite sua pergunta sobre futebol!
        """.strip()
        
        self.whatsapp_service.send_text_message(whatsapp_user.phone_number, message)
    
    def _handle_live_matches_command(self, whatsapp_user):
        """Handle live matches command"""
        try:
            from core.models import LiveMatch
            
            live_matches = LiveMatch.objects.filter(
                is_active=True,
                status__in=['FIRST_HALF', 'SECOND_HALF', 'HALF_TIME', 'EXTRA_TIME_FIRST', 'EXTRA_TIME_SECOND']
            ).order_by('minute')
            
            if not live_matches.exists():
                response = """⚽ Nenhum jogo ao vivo no momento.

📅 Próximos jogos: /proximos
💎 Premium: Alertas automáticos quando jogos começarem!"""
                
                self.whatsapp_service.send_text_message(whatsapp_user.phone_number, response)
                return
            
            response = "🔴 *JOGOS AO VIVO*\n\n"
            
            for live_match in live_matches[:5]:  # Limit to 5 matches
                match = live_match.match
                
                # Basic match info
                response += f"🏠 {match.home_team.name} {live_match.home_score} x {live_match.away_score} {match.away_team.name}\n"
                response += f"⏱️ {live_match.minute}' {'+' + str(live_match.added_time) if live_match.added_time > 0 else ''}\n"
                response += f"🏆 {match.competition.name}\n\n"
                
                # Add AI prediction if available (premium feature)
                if whatsapp_user.subscription_status in ['premium', 'pro', 'trial']:
                    from ai_analytics.models import MatchPrediction
                    prediction = MatchPrediction.objects.filter(
                        match=match,
                        prediction_type='RESULT'
                    ).order_by('-created_at').first()
                    
                    if prediction:
                        pred_data = prediction.features_used
                        home_prob = pred_data.get('home_win_probability', 0.33) * 100
                        draw_prob = pred_data.get('draw_probability', 0.33) * 100
                        away_prob = pred_data.get('away_win_probability', 0.33) * 100
                        
                        response += f"🤖 IA: 🏠 {home_prob:.1f}% | 🤝 {draw_prob:.1f}% | ✈️ {away_prob:.1f}%\n\n"
                
                response += "---\n\n"
            
            self.whatsapp_service.send_text_message(whatsapp_user.phone_number, response)
            
        except Exception as e:
            logger.error(f"Error in live matches command: {str(e)}")
            self.whatsapp_service.send_text_message(
                whatsapp_user.phone_number, 
                "❌ Erro ao buscar jogos ao vivo. Tente novamente."
            )
    
    def _handle_odds_command(self, whatsapp_user, message_text):
        """Handle odds command"""
        try:
            # Check if user has premium access
            if whatsapp_user.subscription_status not in ['premium', 'pro', 'trial']:
                response = """💰 *Odds ao Vivo* - Recurso Premium

Para ver odds ao vivo:
💎 Premium: R$ 19,90/mês
🏆 Pro: R$ 49,90/mês

🆓 Teste 7 dias: /trial
📝 Assinar: /premium"""
                
                self.whatsapp_service.send_text_message(whatsapp_user.phone_number, response)
                return
            
            from core.models import LiveMatch, LiveOddsSnapshot
            
            # Get live matches with recent odds
            live_matches = LiveMatch.objects.filter(
                is_active=True,
                status__in=['FIRST_HALF', 'SECOND_HALF', 'HALF_TIME']
            ).prefetch_related('odds_snapshots')
            
            if not live_matches.exists():
                response = "💰 Nenhuma odd ao vivo disponível no momento."
                self.whatsapp_service.send_text_message(whatsapp_user.phone_number, response)
                return
            
            response = "💰 *ODDS AO VIVO*\n\n"
            
            for live_match in live_matches[:3]:  # Limit to 3 matches
                match = live_match.match
                
                # Get latest odds
                latest_odds = live_match.odds_snapshots.order_by('-minute').first()
                
                if latest_odds:
                    response += f"🏠 {match.home_team.name} vs {match.away_team.name}\n"
                    response += f"💰 Casa: {latest_odds.home_odds:.2f}\n"
                    response += f"🤝 Empate: {latest_odds.draw_odds:.2f}\n"
                    response += f"✈️ Fora: {latest_odds.away_odds:.2f}\n\n"
                    
                    if latest_odds.is_value_bet:
                        response += f"🎯 VALUE BET DETECTADO! (+{latest_odds.value_percentage:.1f}%)\n\n"
                else:
                    response += f"⏱️ {live_match.minute}'\n"
                    response += f"💰 Casa: {latest_odds.home_odds:.2f} 🤝 Empate: {latest_odds.draw_odds:.2f} ✈️ Fora: {latest_odds.away_odds:.2f}\n\n"
                
                response += "---\n\n"
            
            response += "⚠️ *Aposte com responsabilidade*"
            self.whatsapp_service.send_text_message(whatsapp_user.phone_number, response)
            
        except Exception as e:
            logger.error(f"Error in odds command: {str(e)}")
            self.whatsapp_service.send_text_message(
                whatsapp_user.phone_number, 
                "❌ Erro ao buscar odds. Tente novamente."
            )
    
    def _handle_alerts_command(self, whatsapp_user, message_text):
        """Handle alerts configuration"""
        try:
            # Check if user has premium access
            if whatsapp_user.subscription_status not in ['premium', 'pro', 'trial']:
                response = """🔔 *Alertas Automáticos* - Recurso Premium

Com alertas você recebe:
⚽ Gols em tempo real
🟥 Cartões vermelhos
💰 Movimentos de odds (Pro)
🎯 Value bets (Pro)

💎 Premium: R$ 19,90/mês
🏆 Pro: R$ 49,90/mês

🆓 Teste 7 dias: /trial"""
                
                self.whatsapp_service.send_text_message(whatsapp_user.phone_number, response)
                return
            
            # For now, show current alert settings
            response = """🔔 *Seus Alertas Ativos*

✅ Início de jogos
✅ Gols marcados
✅ Cartões vermelhos
✅ Pênaltis"""
            
            if whatsapp_user.subscription_status == 'pro':
                response += """\n✅ Movimentos de odds
✅ Value bets
✅ Previsões da IA"""
            
            response += """\n\n💡 Os alertas são enviados automaticamente durante os jogos!

Para times específicos, digite:
"Alertas do Flamengo"
"Alertas do Palmeiras\""""
            
            self.whatsapp_service.send_text_message(whatsapp_user.phone_number, response)
            
        except Exception as e:
            logger.error(f"Error in alerts command: {str(e)}")
            self.whatsapp_service.send_text_message(
                whatsapp_user.phone_number, 
                "❌ Erro ao configurar alertas. Tente novamente."
            )
    
    def _handle_upcoming_matches_command(self, whatsapp_user):
        """Handle upcoming matches command"""
        try:
            from core.models import Match
            from datetime import datetime, timedelta
            
            # Get matches for today and tomorrow
            now = timezone.now()
            tomorrow = now + timedelta(days=1)
            
            upcoming_matches = Match.objects.filter(
                utc_date__gte=now,
                utc_date__lte=tomorrow,
                status='SCHEDULED'
            ).order_by('utc_date')[:8]
            
            if not upcoming_matches.exists():
                response = "📅 Nenhum jogo agendado para hoje/amanhã."
                self.whatsapp_service.send_text_message(whatsapp_user.phone_number, response)
                return
            
            response = "📅 *PRÓXIMOS JOGOS*\n\n"
            
            for match in upcoming_matches:
                response += f"🏠 {match.home_team.name} vs {match.away_team.name}\n"
                response += f"⏰ {match.utc_date.strftime('%d/%m %H:%M')}\n"
                response += f"🏆 {match.competition.name}\n"
                
                # Add AI prediction for premium users
                if whatsapp_user.subscription_status in ['premium', 'pro', 'trial']:
                    from ai_analytics.models import MatchPrediction
                    prediction = MatchPrediction.objects.filter(
                        match=match,
                        prediction_type='RESULT'
                    ).order_by('-created_at').first()
                    
                    if prediction:
                        pred_data = prediction.features_used
                        home_prob = pred_data.get('home_win_probability', 0.33) * 100
                        draw_prob = pred_data.get('draw_probability', 0.33) * 100
                        away_prob = pred_data.get('away_win_probability', 0.33) * 100
                        
                        response += f"🤖 IA: 🏠 {home_prob:.1f}% | 🤝 {draw_prob:.1f}% | ✈️ {away_prob:.1f}%\n"
                
                response += "\n---\n\n"
            
            if whatsapp_user.subscription_status in ['premium', 'pro', 'trial']:
                response += "💎 Alertas automáticos quando os jogos começarem!"
            else:
                response += "💎 Premium: Receba alertas quando os jogos começarem!"
            
            self.whatsapp_service.send_text_message(whatsapp_user.phone_number, response)
            
        except Exception as e:
            logger.error(f"Error in upcoming matches command: {str(e)}")
            self.whatsapp_service.send_text_message(
                whatsapp_user.phone_number, 
                "❌ Erro ao buscar próximos jogos. Tente novamente."
            )
    
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
