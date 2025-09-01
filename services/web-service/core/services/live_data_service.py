import requests
import json
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from ..models import LiveMatch, LiveMatchEvent, LiveOddsSnapshot, Match, MatchAlert
from ai_analytics.services import MatchPredictionService
from whatsapp_integration.services import WhatsAppService
from betting_odds.services import OddsAnalysisService
import logging

logger = logging.getLogger(__name__)


class LiveDataService:
    """Service for collecting and processing live match data"""
    
    def __init__(self):
        self.football_data_api_key = getattr(settings, 'FOOTBALL_DATA_API_KEY', '')
        self.football_data_base_url = getattr(settings, 'FOOTBALL_DATA_BASE_URL', 'https://api.football-data.org/v4')
        self.whatsapp_service = WhatsAppService()
        self.prediction_service = MatchPredictionService()
        
    def monitor_live_matches(self):
        """Monitor all currently live matches"""
        try:
            live_matches = LiveMatch.objects.filter(
                is_active=True,
                status__in=['FIRST_HALF', 'SECOND_HALF', 'EXTRA_TIME_FIRST', 'EXTRA_TIME_SECOND']
            )
            
            logger.info(f"Monitoring {live_matches.count()} live matches")
            
            for live_match in live_matches:
                try:
                    self.update_live_match_data(live_match)
                except Exception as e:
                    logger.error(f"Error updating live match {live_match.id}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Error in monitor_live_matches: {str(e)}")
    
    def update_live_match_data(self, live_match):
        """Update live match data from API"""
        try:
            # Get live data from Football Data API
            url = f"{self.football_data_base_url}/matches/{live_match.match.id}"
            headers = {'X-Auth-Token': self.football_data_api_key}
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self._process_live_match_data(live_match, data)
            else:
                logger.warning(f"API request failed for match {live_match.match.id}: {response.status_code}")
                
        except requests.RequestException as e:
            logger.error(f"Network error updating match {live_match.match.id}: {str(e)}")
        except Exception as e:
            logger.error(f"Error updating match {live_match.match.id}: {str(e)}")
    
    def _process_live_match_data(self, live_match, data):
        """Process live match data and update database"""
        with transaction.atomic():
            # Update basic match info
            score = data.get('score', {})
            full_time = score.get('fullTime', {})
            
            old_home_score = live_match.home_score
            old_away_score = live_match.away_score
            old_minute = live_match.minute
            
            # Update scores and time
            live_match.home_score = full_time.get('home', 0) or 0
            live_match.away_score = full_time.get('away', 0) or 0
            live_match.minute = data.get('minute', 0) or 0
            live_match.status = self._map_status(data.get('status', 'SCHEDULED'))
            
            # Update statistics if available
            if 'statistics' in data:
                self._update_live_statistics(live_match, data['statistics'])
            
            live_match.save()
            
            # Check for new goals
            if (live_match.home_score != old_home_score or 
                live_match.away_score != old_away_score):
                self._handle_goal_scored(live_match, old_home_score, old_away_score)
            
            # Check for significant time changes (events)
            if live_match.minute != old_minute:
                self._check_for_events(live_match, data)
    
    def _map_status(self, api_status):
        """Map API status to our live status"""
        status_mapping = {
            'SCHEDULED': 'PRE_MATCH',
            'TIMED': 'PRE_MATCH',
            'IN_PLAY': 'FIRST_HALF',
            'PAUSED': 'HALF_TIME',
            'FINISHED': 'FULL_TIME',
            'SUSPENDED': 'SUSPENDED',
            'POSTPONED': 'PRE_MATCH',
            'CANCELLED': 'ABANDONED',
        }
        return status_mapping.get(api_status, 'PRE_MATCH')
    
    def _update_live_statistics(self, live_match, statistics):
        """Update live match statistics"""
        # This is a simplified version - actual implementation would depend on API structure
        for stat in statistics:
            team_id = stat.get('team', {}).get('id')
            if team_id == live_match.match.home_team.id:
                live_match.home_possession = stat.get('possession', 0)
                live_match.home_shots = stat.get('shots', 0)
                live_match.home_shots_on_target = stat.get('shotsOnTarget', 0)
                live_match.home_corners = stat.get('corners', 0)
                live_match.home_fouls = stat.get('fouls', 0)
                live_match.home_yellow_cards = stat.get('yellowCards', 0)
                live_match.home_red_cards = stat.get('redCards', 0)
            elif team_id == live_match.match.away_team.id:
                live_match.away_possession = stat.get('possession', 0)
                live_match.away_shots = stat.get('shots', 0)
                live_match.away_shots_on_target = stat.get('shotsOnTarget', 0)
                live_match.away_corners = stat.get('corners', 0)
                live_match.away_fouls = stat.get('fouls', 0)
                live_match.away_yellow_cards = stat.get('yellowCards', 0)
                live_match.away_red_cards = stat.get('redCards', 0)
    
    def _handle_goal_scored(self, live_match, old_home_score, old_away_score):
        """Handle goal scored event"""
        try:
            # Determine which team scored
            if live_match.home_score > old_home_score:
                team = live_match.match.home_team
                new_home = live_match.home_score
                new_away = live_match.away_score
            else:
                team = live_match.match.away_team
                new_home = live_match.home_score
                new_away = live_match.away_score
            
            # Create event
            event = LiveMatchEvent.objects.create(
                live_match=live_match,
                event_type='GOAL',
                minute=live_match.minute,
                team=team,
                description=f"Goal! {team.name}"
            )
            
            # Create and send alert
            alert = MatchAlert.objects.create(
                match=live_match.match,
                alert_type='GOAL',
                priority='HIGH',
                title=f"⚽ GOL! {live_match.match.home_team.name} vs {live_match.match.away_team.name}",
                message=f"""⚽ GOOOOOL! {team.name}!

🏠 {live_match.match.home_team.name} {new_home} x {new_away} {live_match.match.away_team.name}
⏱️ {live_match.minute}' {'+' + str(live_match.added_time) if live_match.added_time > 0 else ''}

🎯 Acompanhe as odds atualizadas!""",
                target_subscription_levels=['premium', 'pro'],
                data={'event_id': event.id, 'scorer_team': team.name}
            )
            
            # Queue alert for sending
            self._queue_alert_for_sending(alert)
            
        except Exception as e:
            logger.error(f"Error handling goal: {str(e)}")
    
    def _check_for_events(self, live_match, data):
        """Check for other match events"""
        # This would parse events from the API data
        # For now, we'll create basic time-based events
        
        if live_match.minute == 45 and live_match.status == 'HALF_TIME':
            self._create_half_time_event(live_match)
        elif live_match.minute >= 90 and live_match.status == 'FULL_TIME':
            self._create_full_time_event(live_match)
    
    def _create_half_time_event(self, live_match):
        """Create half-time event"""
        try:
            event = LiveMatchEvent.objects.create(
                live_match=live_match,
                event_type='HALF_TIME',
                minute=45,
                description="Half Time"
            )
            
            alert = MatchAlert.objects.create(
                match=live_match.match,
                alert_type='HALF_TIME',
                priority='MEDIUM',
                title=f"📊 Intervalo - {live_match.match.home_team.name} vs {live_match.match.away_team.name}",
                message=f"""🏠 {live_match.match.home_team.name} {live_match.home_score} x {live_match.away_score} {live_match.match.away_team.name}

📊 Estatísticas do 1º tempo:
🎯 Finalizações: {live_match.home_shots} x {live_match.away_shots}
⚽ No gol: {live_match.home_shots_on_target} x {live_match.away_shots_on_target}
📈 Posse: {live_match.home_possession:.0f}% x {live_match.away_possession:.0f}%""",
                target_subscription_levels=['premium', 'pro']
            )
            
            self._queue_alert_for_sending(alert)
            
        except Exception as e:
            logger.error(f"Error creating half-time event: {str(e)}")
    
    def _create_full_time_event(self, live_match):
        """Create full-time event"""
        try:
            event = LiveMatchEvent.objects.create(
                live_match=live_match,
                event_type='FULL_TIME',
                minute=90,
                description="Full Time"
            )
            
            alert = MatchAlert.objects.create(
                match=live_match.match,
                alert_type='FULL_TIME',
                priority='HIGH',
                title=f"🏁 Final - {live_match.match.home_team.name} vs {live_match.match.away_team.name}",
                message=f"""🏠 {live_match.match.home_team.name} {live_match.home_score} x {live_match.away_score} {live_match.match.away_team.name}

📊 Estatísticas finais:
🎯 Finalizações: {live_match.home_shots} x {live_match.away_shots}
⚽ No gol: {live_match.home_shots_on_target} x {live_match.away_shots_on_target}
📈 Posse: {live_match.home_possession:.0f}% x {live_match.away_possession:.0f}%
🟨 Cartões: {live_match.home_yellow_cards} x {live_match.away_yellow_cards}""",
                target_subscription_levels=['premium', 'pro']
            )
            
            self._queue_alert_for_sending(alert)
            
            # Mark match as inactive
            live_match.is_active = False
            live_match.save()
            
        except Exception as e:
            logger.error(f"Error creating full-time event: {str(e)}")
    
    def _queue_alert_for_sending(self, alert):
        """Queue alert for WhatsApp sending"""
        # This would integrate with Celery to send alerts
        from core.tasks import send_match_alert
        send_match_alert.delay(alert.id)
    
    def create_red_card_alert(self, live_match, player, team):
        """Create red card alert"""
        try:
            event = LiveMatchEvent.objects.create(
                live_match=live_match,
                event_type='RED_CARD',
                minute=live_match.minute,
                player=player,
                team=team,
                description=f"Red Card: {player.name if player else 'Player'}"
            )
            
            alert = MatchAlert.objects.create(
                match=live_match.match,
                alert_type='RED_CARD',
                priority='URGENT',
                title=f"🟥 Cartão Vermelho! {live_match.match.home_team.name} vs {live_match.match.away_team.name}",
                message=f"""🟥 CARTÃO VERMELHO!

👤 {player.name if player else 'Jogador'} ({team.name if team else 'Time'})
⏱️ {live_match.minute}' {'+' + str(live_match.added_time) if live_match.added_time > 0 else ''}

⚡ Jogo pode mudar drasticamente!""",
                target_subscription_levels=['premium', 'pro'],
                data={'event_id': event.id, 'player_name': player.name if player else 'Unknown'}
            )
            
            self._queue_alert_for_sending(alert)
            
        except Exception as e:
            logger.error(f"Error creating red card alert: {str(e)}")
    
    def update_ai_predictions(self, live_match):
        """Update AI predictions based on live data"""
        try:
            # Get updated predictions from AI service
            new_predictions = self.prediction_service.predict_live_match_outcome(live_match)
            
            if new_predictions:
                # Check if predictions changed significantly
                old_predictions = live_match.match.predictions.filter(
                    prediction_type='RESULT'
                ).order_by('-created_at').first()
                
                if self._predictions_changed_significantly(old_predictions, new_predictions):
                    self._create_prediction_update_alert(live_match, new_predictions)
                    
        except Exception as e:
            logger.error(f"Error updating AI predictions: {str(e)}")
    
    def _predictions_changed_significantly(self, old_predictions, new_predictions, threshold=10):
        """Check if predictions changed by more than threshold percentage"""
        if not old_predictions:
            return True
            
        # Compare probability changes
        old_data = old_predictions.features_used
        home_change = abs(new_predictions['home_win_probability'] - old_data.get('home_win_probability', 0))
        
        return home_change > (threshold / 100)
    
    def _create_prediction_update_alert(self, live_match, new_predictions):
        """Create alert for significant prediction changes"""
        try:
            # Determine trend
            if new_predictions['home_win_probability'] > 0.6:
                trend = f"📈 {live_match.match.home_team.name} favorito!"
            elif new_predictions['away_win_probability'] > 0.6:
                trend = f"📈 {live_match.match.away_team.name} favorito!"
            else:
                trend = "⚖️ Jogo equilibrado!"
            
            alert = MatchAlert.objects.create(
                match=live_match.match,
                alert_type='SCORE_PREDICTION',
                priority='MEDIUM',
                title=f"🤖 IA: Previsão Atualizada",
                message=f"""{trend}

🎯 Novas probabilidades:
🏠 {live_match.match.home_team.name}: {new_predictions['home_win_probability']*100:.1f}%
🤝 Empate: {new_predictions['draw_probability']*100:.1f}%
✈️ {live_match.match.away_team.name}: {new_predictions['away_win_probability']*100:.1f}%

⏱️ {live_match.minute}' - Situação do jogo mudou!""",
                target_subscription_levels=['premium', 'pro'],
                data=new_predictions
            )
            
            self._queue_alert_for_sending(alert)
            
        except Exception as e:
            logger.error(f"Error creating prediction alert: {str(e)}")
    
    def start_match_monitoring(self, match):
        """Start monitoring a match when it begins"""
        try:
            live_match, created = LiveMatch.objects.get_or_create(
                match=match,
                defaults={
                    'status': 'PRE_MATCH',
                    'is_active': True,
                }
            )
            
            if created:
                alert = MatchAlert.objects.create(
                    match=match,
                    alert_type='MATCH_START',
                    priority='HIGH',
                    title=f"🚀 Começou! {match.home_team.name} vs {match.away_team.name}",
                    message=f"""🏠 {match.home_team.name} vs {match.away_team.name}
⏱️ 0'

📊 Acompanhe as estatísticas ao vivo!""",
                    target_subscription_levels=['premium', 'pro']
                )
                
                self._queue_alert_for_sending(alert)
                
            return live_match
            
        except Exception as e:
            logger.error(f"Error starting match monitoring: {str(e)}")
            return None


class LiveOddsService:
    """Service for monitoring live odds during matches"""
    
    def __init__(self):
        self.odds_service = OddsAnalysisService()
        
    def update_live_odds(self, live_match):
        """Update live odds for a match"""
        try:
            # Get current odds from betting service
            current_odds = self._fetch_live_odds(live_match.match)
            
            if current_odds:
                # Create odds snapshot
                snapshot = LiveOddsSnapshot.objects.create(
                    live_match=live_match,
                    minute=live_match.minute,
                    home_odds=current_odds['home'],
                    draw_odds=current_odds['draw'],
                    away_odds=current_odds['away'],
                    over_2_5_odds=current_odds.get('over_2_5'),
                    under_2_5_odds=current_odds.get('under_2_5'),
                    both_teams_score_yes=current_odds.get('btts_yes'),
                    both_teams_score_no=current_odds.get('btts_no'),
                )
                
                # Check for value bets
                self._analyze_value_bets(snapshot, live_match)
                
                # Check for significant odds movements
                self._check_odds_movements(snapshot, live_match)
                
        except Exception as e:
            logger.error(f"Error updating live odds: {str(e)}")
    
    def _fetch_live_odds(self, match):
        """Fetch live odds from betting APIs"""
        # This would integrate with actual betting APIs
        # For now, return mock data
        return {
            'home': 2.10,
            'draw': 3.20,
            'away': 3.50,
            'over_2_5': 1.80,
            'under_2_5': 2.00,
            'btts_yes': 1.70,
            'btts_no': 2.10,
        }
    
    def _analyze_value_bets(self, snapshot, live_match):
        """Analyze for value betting opportunities"""
        try:
            # Get AI predictions for comparison
            predictions = live_match.match.predictions.filter(
                prediction_type='RESULT'
            ).order_by('-created_at').first()
            
            if predictions:
                pred_data = predictions.features_used
                
                # Calculate value percentages
                value_checks = [
                    ('home', snapshot.home_odds, pred_data.get('home_win_probability', 0)),
                    ('draw', snapshot.draw_odds, pred_data.get('draw_probability', 0)),
                    ('away', snapshot.away_odds, pred_data.get('away_win_probability', 0)),
                ]
                
                for bet_type, odds, probability in value_checks:
                    if probability > 0:
                        implied_prob = 1 / odds
                        value_percent = ((probability - implied_prob) / implied_prob) * 100
                        
                        if value_percent > 15:  # 15% value threshold
                            self._create_value_bet_alert(live_match, bet_type, odds, value_percent, snapshot)
                            snapshot.is_value_bet = True
                            snapshot.value_percentage = value_percent
                            snapshot.save()
                            
        except Exception as e:
            logger.error(f"Error analyzing value bets: {str(e)}")
    
    def _create_value_bet_alert(self, live_match, bet_type, odds, value_percent, snapshot):
        """Create value bet alert"""
        try:
            bet_names = {
                'home': f"Vitória {live_match.match.home_team.name}",
                'draw': "Empate",
                'away': f"Vitória {live_match.match.away_team.name}"
            }
            
            bet_odds = {
                'home': snapshot.home_odds,
                'draw': snapshot.draw_odds,
                'away': snapshot.away_odds
            }
            
            alert = MatchAlert.objects.create(
                match=live_match.match,
                alert_type='VALUE_BET',
                priority='URGENT',
                title=f"💰 Value Bet Detectado!",
                message=f"""🎯 {bet_names[bet_type]}
📊 Odd: {bet_odds[bet_type]:.2f}
📈 Valor: +{snapshot.value_percentage:.1f}%

🤖 Nossa IA indica probabilidade maior que as odds sugerem!

⚠️ Aposte com responsabilidade""",
                target_subscription_levels=['pro'],  # Only for Pro users
                data={
                    'bet_type': bet_type,
                    'odds': odds,
                    'value_percentage': value_percent,
                    'minute': live_match.minute
                }
            )
            
            # Queue for immediate sending
            from core.tasks import send_match_alert
            send_match_alert.delay(alert.id)
            
        except Exception as e:
            logger.error(f"Error creating value bet alert: {str(e)}")
    
    def _check_odds_movements(self, current_snapshot, live_match):
        """Check for significant odds movements"""
        try:
            # Get previous snapshot
            previous = LiveOddsSnapshot.objects.filter(
                live_match=live_match
            ).exclude(id=current_snapshot.id).order_by('-minute').first()
            
            if previous:
                movements = [
                    ('home', previous.home_odds, current_snapshot.home_odds, live_match.match.home_team.name),
                    ('draw', previous.draw_odds, current_snapshot.draw_odds, 'Empate'),
                    ('away', previous.away_odds, current_snapshot.away_odds, live_match.match.away_team.name),
                ]
                
                for bet_type, old_odds, new_odds, team_name in movements:
                    if old_odds and new_odds:
                        change = new_odds - old_odds
                        change_percent = (change / old_odds) * 100
                        
                        # Alert for movements > 10%
                        if abs(change_percent) > 10:
                            self._create_odds_movement_alert(
                                live_match, bet_type, old_odds, new_odds, change, team_name
                            )
                            
        except Exception as e:
            logger.error(f"Error checking odds movements: {str(e)}")
    
    def _create_odds_movement_alert(self, live_match, bet_type, old_odds, new_odds, change, team_name):
        """Create odds movement alert"""
        try:
            direction = "subiu" if change > 0 else "caiu"
            
            alert = MatchAlert.objects.create(
                match=live_match.match,
                alert_type='ODDS_MOVEMENT',
                priority='HIGH',
                title=f"📊 Movimento de Odds!",
                message=f"""🎯 {team_name}
📈 Odd {direction}: {abs(change):.2f}

💡 Grande volume de apostas pode indicar informação privilegiada!

⏱️ {live_match.minute}' - Aproveite o movimento!""",
                target_subscription_levels=['premium', 'pro'],
                data={
                    'bet_type': bet_type,
                    'old_odds': old_odds,
                    'new_odds': new_odds,
                    'change': change,
                    'team_name': team_name
                }
            )
            
            # Queue for sending
            from core.tasks import send_match_alert
            send_match_alert.delay(alert.id)
            
        except Exception as e:
            logger.error(f"Error creating odds movement alert: {str(e)}")
