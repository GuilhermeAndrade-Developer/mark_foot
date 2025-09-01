# Real-time Match Analytics and Live Odds Monitoring

## Objective
Implement real-time match monitoring system with live odds tracking, in-match analytics, and automated notifications via WhatsApp for premium users.

## Current Project Context
- Existing match data collection system
- WhatsApp integration with subscription management
- AI analytics services for predictions
- Betting odds integration foundation
- Celery task automation system

## Technical Requirements

### 1. Live Match Data Models

#### core/models.py extensions
```python
from django.db import models
from django.utils import timezone

class LiveMatch(models.Model):
    MATCH_STATUS = [
        ('scheduled', 'Agendado'),
        ('live', 'Ao Vivo'),
        ('halftime', 'Intervalo'),
        ('finished', 'Finalizado'),
        ('postponed', 'Adiado'),
        ('cancelled', 'Cancelado'),
    ]
    
    match = models.OneToOneField('Match', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=MATCH_STATUS, default='scheduled')
    
    # Live scores
    home_score = models.IntegerField(default=0)
    away_score = models.IntegerField(default=0)
    
    # Match timing
    minute = models.IntegerField(default=0)
    added_time = models.IntegerField(default=0)
    period = models.CharField(max_length=20, default='1st')  # 1st, 2nd, halftime, fulltime
    
    # Live statistics
    home_possession = models.FloatField(default=0.0)  # Percentage
    away_possession = models.FloatField(default=0.0)
    home_shots = models.IntegerField(default=0)
    away_shots = models.IntegerField(default=0)
    home_shots_on_target = models.IntegerField(default=0)
    away_shots_on_target = models.IntegerField(default=0)
    home_corners = models.IntegerField(default=0)
    away_corners = models.IntegerField(default=0)
    home_fouls = models.IntegerField(default=0)
    away_fouls = models.IntegerField(default=0)
    home_yellow_cards = models.IntegerField(default=0)
    away_yellow_cards = models.IntegerField(default=0)
    home_red_cards = models.IntegerField(default=0)
    away_red_cards = models.IntegerField(default=0)
    
    # Live odds tracking
    current_home_odds = models.FloatField(null=True, blank=True)
    current_draw_odds = models.FloatField(null=True, blank=True)
    current_away_odds = models.FloatField(null=True, blank=True)
    
    # Timestamps
    last_updated = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    
    # AI predictions during match
    live_home_win_probability = models.FloatField(null=True, blank=True)
    live_draw_probability = models.FloatField(null=True, blank=True)
    live_away_win_probability = models.FloatField(null=True, blank=True)
    live_prediction_last_update = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-started_at']

class LiveMatchEvent(models.Model):
    EVENT_TYPES = [
        ('goal', 'Gol'),
        ('yellow_card', 'Cartão Amarelo'),
        ('red_card', 'Cartão Vermelho'),
        ('substitution', 'Substituição'),
        ('penalty', 'Pênalti'),
        ('corner', 'Escanteio'),
        ('offside', 'Impedimento'),
        ('free_kick', 'Falta'),
        ('var_check', 'Revisão VAR'),
        ('period_start', 'Início de Período'),
        ('period_end', 'Fim de Período'),
    ]
    
    live_match = models.ForeignKey(LiveMatch, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    team = models.ForeignKey('Team', on_delete=models.CASCADE, null=True, blank=True)
    player = models.ForeignKey('Player', on_delete=models.CASCADE, null=True, blank=True)
    minute = models.IntegerField()
    added_time = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    
    # Event specific data
    event_data = models.JSONField(default=dict)  # Store additional event info
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['minute', 'added_time', 'created_at']

class LiveOddsSnapshot(models.Model):
    live_match = models.ForeignKey(LiveMatch, on_delete=models.CASCADE, related_name='odds_snapshots')
    bookmaker = models.ForeignKey('BookmakerOdds', on_delete=models.CASCADE)
    
    # Current odds
    home_odds = models.FloatField()
    draw_odds = models.FloatField()
    away_odds = models.FloatField()
    
    # Odds changes
    home_odds_change = models.FloatField(default=0.0)  # Change from last snapshot
    draw_odds_change = models.FloatField(default=0.0)
    away_odds_change = models.FloatField(default=0.0)
    
    # Market information
    total_volume = models.FloatField(null=True, blank=True)
    market_confidence = models.FloatField(null=True, blank=True)
    
    # Value bet detection
    is_value_bet_home = models.BooleanField(default=False)
    is_value_bet_draw = models.BooleanField(default=False)
    is_value_bet_away = models.BooleanField(default=False)
    value_percentage = models.FloatField(null=True, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']

class MatchAlert(models.Model):
    ALERT_TYPES = [
        ('goal_scored', 'Gol Marcado'),
        ('red_card', 'Cartão Vermelho'),
        ('odds_drop', 'Queda de Odds'),
        ('value_bet', 'Aposta de Valor'),
        ('prediction_change', 'Mudança de Previsão'),
        ('match_start', 'Início da Partida'),
        ('halftime', 'Intervalo'),
        ('fulltime', 'Fim do Jogo'),
    ]
    
    live_match = models.ForeignKey(LiveMatch, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Alert conditions
    conditions = models.JSONField(default=dict)
    triggered_at = models.DateTimeField(auto_now_add=True)
    
    # Notification tracking
    notified_users = models.ManyToManyField('whatsapp_integration.WhatsAppUser', blank=True)
    notification_sent = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-triggered_at']
```

### 2. Live Data Collection Service

#### core/services/live_data_service.py
```python
import requests
import json
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from ..models import LiveMatch, LiveMatchEvent, LiveOddsSnapshot, Match, MatchAlert
from ai_analytics.services import MatchPredictionService

class LiveDataService:
    def __init__(self):
        self.api_key = settings.FOOTBALL_API_KEY
        self.base_url = "https://api.football-api.com/v1"
        self.prediction_service = MatchPredictionService()
    
    def start_live_monitoring(self, match_id):
        """Start live monitoring for a specific match"""
        try:
            match = Match.objects.get(id=match_id)
            live_match, created = LiveMatch.objects.get_or_create(
                match=match,
                defaults={
                    'status': 'scheduled',
                    'started_at': timezone.now() if match.date <= timezone.now() else None
                }
            )
            
            if created:
                print(f"Started live monitoring for match: {match}")
            
            return live_match
            
        except Match.DoesNotExist:
            print(f"Match {match_id} not found")
            return None
    
    def update_live_match_data(self, live_match):
        """Update live match data from API"""
        try:
            # Call external API for live data
            url = f"{self.base_url}/matches/{live_match.match.external_id}/live"
            headers = {'Authorization': f'Bearer {self.api_key}'}
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Update live match data
            old_status = live_match.status
            old_score = (live_match.home_score, live_match.away_score)
            
            live_match.status = self._map_status(data.get('status'))
            live_match.home_score = data.get('home_score', 0)
            live_match.away_score = data.get('away_score', 0)
            live_match.minute = data.get('minute', 0)
            live_match.added_time = data.get('added_time', 0)
            live_match.period = data.get('period', '1st')
            
            # Update statistics
            stats = data.get('statistics', {})
            live_match.home_possession = stats.get('home_possession', 0.0)
            live_match.away_possession = stats.get('away_possession', 0.0)
            live_match.home_shots = stats.get('home_shots', 0)
            live_match.away_shots = stats.get('away_shots', 0)
            live_match.home_shots_on_target = stats.get('home_shots_on_target', 0)
            live_match.away_shots_on_target = stats.get('away_shots_on_target', 0)
            live_match.home_corners = stats.get('home_corners', 0)
            live_match.away_corners = stats.get('away_corners', 0)
            live_match.home_fouls = stats.get('home_fouls', 0)
            live_match.away_fouls = stats.get('away_fouls', 0)
            live_match.home_yellow_cards = stats.get('home_yellow_cards', 0)
            live_match.away_yellow_cards = stats.get('away_yellow_cards', 0)
            live_match.home_red_cards = stats.get('home_red_cards', 0)
            live_match.away_red_cards = stats.get('away_red_cards', 0)
            
            # Set match timing
            if live_match.status == 'live' and not live_match.started_at:
                live_match.started_at = timezone.now()
            elif live_match.status == 'finished' and not live_match.finished_at:
                live_match.finished_at = timezone.now()
            
            live_match.save()
            
            # Check for new events
            self._process_match_events(live_match, data.get('events', []))
            
            # Check for alerts
            self._check_match_alerts(live_match, old_status, old_score)
            
            # Update AI predictions if significant changes
            if self._should_update_predictions(live_match, old_score):
                self._update_live_predictions(live_match)
            
            return True
            
        except Exception as e:
            print(f"Error updating live match {live_match.id}: {e}")
            return False
    
    def _map_status(self, api_status):
        """Map API status to our status"""
        status_map = {
            'scheduled': 'scheduled',
            'live': 'live',
            'first_half': 'live',
            'halftime': 'halftime',
            'second_half': 'live',
            'finished': 'finished',
            'postponed': 'postponed',
            'cancelled': 'cancelled',
        }
        return status_map.get(api_status, 'scheduled')
    
    def _process_match_events(self, live_match, events_data):
        """Process and store match events"""
        existing_events = set(
            LiveMatchEvent.objects.filter(live_match=live_match)
            .values_list('event_type', 'minute', 'team_id', 'player_id')
        )
        
        for event_data in events_data:
            # Create event tuple for comparison
            event_tuple = (
                event_data.get('type'),
                event_data.get('minute'),
                event_data.get('team_id'),
                event_data.get('player_id')
            )
            
            # Skip if event already exists
            if event_tuple in existing_events:
                continue
            
            # Create new event
            try:
                team_id = event_data.get('team_id')
                player_id = event_data.get('player_id')
                
                event = LiveMatchEvent.objects.create(
                    live_match=live_match,
                    event_type=event_data.get('type'),
                    team_id=team_id if team_id else None,
                    player_id=player_id if player_id else None,
                    minute=event_data.get('minute', 0),
                    added_time=event_data.get('added_time', 0),
                    description=event_data.get('description', ''),
                    event_data=event_data
                )
                
                # Trigger event-based alerts
                self._trigger_event_alert(event)
                
            except Exception as e:
                print(f"Error creating event: {e}")
    
    def _check_match_alerts(self, live_match, old_status, old_score):
        """Check for various match alerts"""
        # Goal alert
        if old_score != (live_match.home_score, live_match.away_score):
            self._create_goal_alert(live_match, old_score)
        
        # Status change alerts
        if old_status != live_match.status:
            self._create_status_alert(live_match, old_status)
    
    def _create_goal_alert(self, live_match, old_score):
        """Create goal alert"""
        old_home, old_away = old_score
        new_home, new_away = live_match.home_score, live_match.away_score
        
        if new_home > old_home:
            # Home team scored
            message = f"""⚽ GOL! {live_match.match.home_team.name}!

🏠 {live_match.match.home_team.name} {new_home} x {new_away} {live_match.match.away_team.name}
⏱️ {live_match.minute}' {'+' + str(live_match.added_time) if live_match.added_time > 0 else ''}

🎯 Acompanhe as odds atualizadas!"""
            
        elif new_away > old_away:
            # Away team scored
            message = f"""⚽ GOL! {live_match.match.away_team.name}!

🏠 {live_match.match.home_team.name} {new_home} x {new_away} {live_match.match.away_team.name}
⏱️ {live_match.minute}' {'+' + str(live_match.added_time) if live_match.added_time > 0 else ''}

🎯 Acompanhe as odds atualizadas!"""
        
        MatchAlert.objects.create(
            live_match=live_match,
            alert_type='goal_scored',
            title=f"Gol em {live_match.match.home_team.name} vs {live_match.match.away_team.name}",
            message=message,
            conditions={'old_score': old_score, 'new_score': (new_home, new_away)}
        )
    
    def _create_status_alert(self, live_match, old_status):
        """Create status change alert"""
        if live_match.status == 'live' and old_status == 'scheduled':
            message = f"""🟢 Começou!

🏠 {live_match.match.home_team.name} vs {live_match.match.away_team.name}
⏱️ 0'

📊 Acompanhe as estatísticas ao vivo!"""
            
            MatchAlert.objects.create(
                live_match=live_match,
                alert_type='match_start',
                title=f"Início: {live_match.match.home_team.name} vs {live_match.match.away_team.name}",
                message=message
            )
        
        elif live_match.status == 'halftime' and old_status == 'live':
            message = f"""⏸️ Intervalo

🏠 {live_match.match.home_team.name} {live_match.home_score} x {live_match.away_score} {live_match.match.away_team.name}

📊 Estatísticas do 1º tempo:
🎯 Finalizações: {live_match.home_shots} x {live_match.away_shots}
⚽ No gol: {live_match.home_shots_on_target} x {live_match.away_shots_on_target}
📈 Posse: {live_match.home_possession:.0f}% x {live_match.away_possession:.0f}%"""
            
            MatchAlert.objects.create(
                live_match=live_match,
                alert_type='halftime',
                title=f"Intervalo: {live_match.match.home_team.name} vs {live_match.match.away_team.name}",
                message=message
            )
        
        elif live_match.status == 'finished' and old_status in ['live', 'halftime']:
            message = f"""🏁 Fim de jogo!

🏠 {live_match.match.home_team.name} {live_match.home_score} x {live_match.away_score} {live_match.match.away_team.name}

📊 Estatísticas finais:
🎯 Finalizações: {live_match.home_shots} x {live_match.away_shots}
⚽ No gol: {live_match.home_shots_on_target} x {live_match.away_shots_on_target}
📈 Posse: {live_match.home_possession:.0f}% x {live_match.away_possession:.0f}%
🟨 Cartões: {live_match.home_yellow_cards} x {live_match.away_yellow_cards}"""
            
            MatchAlert.objects.create(
                live_match=live_match,
                alert_type='fulltime',
                title=f"Final: {live_match.match.home_team.name} vs {live_match.match.away_team.name}",
                message=message
            )
    
    def _trigger_event_alert(self, event):
        """Trigger alerts for specific events"""
        if event.event_type == 'red_card':
            message = f"""🟥 Cartão Vermelho!

👤 {event.player.name if event.player else 'Jogador'} ({event.team.name if event.team else 'Time'})
⏱️ {event.minute}' {'+' + str(event.added_time) if event.added_time > 0 else ''}

⚡ Jogo pode mudar drasticamente!"""
            
            MatchAlert.objects.create(
                live_match=event.live_match,
                alert_type='red_card',
                title=f"Cartão vermelho em {event.live_match.match.home_team.name} vs {event.live_match.match.away_team.name}",
                message=message,
                conditions={'player': event.player.name if event.player else None, 'team': event.team.name if event.team else None}
            )
    
    def _should_update_predictions(self, live_match, old_score):
        """Determine if predictions should be updated"""
        # Update predictions on goals, red cards, or every 15 minutes
        score_changed = old_score != (live_match.home_score, live_match.away_score)
        red_card_event = live_match.events.filter(
            event_type='red_card',
            created_at__gte=timezone.now() - timedelta(minutes=1)
        ).exists()
        
        time_threshold = not live_match.live_prediction_last_update or \
                        timezone.now() - live_match.live_prediction_last_update >= timedelta(minutes=15)
        
        return score_changed or red_card_event or time_threshold
    
    def _update_live_predictions(self, live_match):
        """Update AI predictions based on current match state"""
        try:
            # Prepare current match state data
            match_state = {
                'minute': live_match.minute,
                'home_score': live_match.home_score,
                'away_score': live_match.away_score,
                'home_possession': live_match.home_possession,
                'away_possession': live_match.away_possession,
                'home_shots': live_match.home_shots,
                'away_shots': live_match.away_shots,
                'home_shots_on_target': live_match.home_shots_on_target,
                'away_shots_on_target': live_match.away_shots_on_target,
                'home_red_cards': live_match.home_red_cards,
                'away_red_cards': live_match.away_red_cards,
                'status': live_match.status
            }
            
            # Get updated predictions
            predictions = self.prediction_service.predict_live_match_outcome(
                live_match.match, match_state
            )
            
            if predictions:
                old_home_prob = live_match.live_home_win_probability
                
                live_match.live_home_win_probability = predictions['home_win_probability']
                live_match.live_draw_probability = predictions['draw_probability']
                live_match.live_away_win_probability = predictions['away_win_probability']
                live_match.live_prediction_last_update = timezone.now()
                live_match.save()
                
                # Check for significant prediction changes
                if old_home_prob and abs(old_home_prob - predictions['home_win_probability']) > 0.15:
                    self._create_prediction_change_alert(live_match, old_home_prob, predictions)
            
        except Exception as e:
            print(f"Error updating live predictions: {e}")
    
    def _create_prediction_change_alert(self, live_match, old_prob, new_predictions):
        """Create alert for significant prediction changes"""
        change = new_predictions['home_win_probability'] - old_prob
        
        if change > 0:
            trend = f"📈 {live_match.match.home_team.name} subiu {abs(change)*100:.1f}%"
        else:
            trend = f"📉 {live_match.match.home_team.name} caiu {abs(change)*100:.1f}%"
        
        message = f"""🤖 IA: Previsão Atualizada!

{trend}

🎯 Novas probabilidades:
🏠 {live_match.match.home_team.name}: {new_predictions['home_win_probability']*100:.1f}%
🤝 Empate: {new_predictions['draw_probability']*100:.1f}%
✈️ {live_match.match.away_team.name}: {new_predictions['away_win_probability']*100:.1f}%

⏱️ {live_match.minute}' - Situação do jogo mudou!"""
        
        MatchAlert.objects.create(
            live_match=live_match,
            alert_type='prediction_change',
            title=f"IA: Mudança de previsão",
            message=message,
            conditions={'change_percentage': change * 100}
        )

class LiveOddsService:
    def __init__(self):
        self.odds_apis = {
            'bet365': settings.BET365_API_KEY,
            'betfair': settings.BETFAIR_API_KEY,
            'pinnacle': settings.PINNACLE_API_KEY,
        }
    
    def update_live_odds(self, live_match):
        """Update live odds for all bookmakers"""
        for bookmaker, api_key in self.odds_apis.items():
            try:
                odds_data = self._fetch_live_odds(live_match, bookmaker, api_key)
                if odds_data:
                    self._save_odds_snapshot(live_match, bookmaker, odds_data)
            except Exception as e:
                print(f"Error updating {bookmaker} odds: {e}")
    
    def _fetch_live_odds(self, live_match, bookmaker, api_key):
        """Fetch live odds from specific bookmaker"""
        # Implementation depends on bookmaker API
        # This is a simplified example
        
        if bookmaker == 'bet365':
            url = f"https://api.bet365.com/v1/odds/live/{live_match.match.external_id}"
        elif bookmaker == 'betfair':
            url = f"https://api.betfair.com/exchange/betting/rest/v1.0/listMarketBook/"
        elif bookmaker == 'pinnacle':
            url = f"https://api.pinnacle.com/v1/odds/live"
        
        headers = {'Authorization': f'Bearer {api_key}'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        return None
    
    def _save_odds_snapshot(self, live_match, bookmaker_name, odds_data):
        """Save odds snapshot and detect value bets"""
        try:
            # Get or create bookmaker
            from betting_odds.models import BookmakerOdds
            bookmaker, _ = BookmakerOdds.objects.get_or_create(
                name=bookmaker_name,
                defaults={'is_active': True}
            )
            
            # Get last snapshot for comparison
            last_snapshot = LiveOddsSnapshot.objects.filter(
                live_match=live_match,
                bookmaker=bookmaker
            ).first()
            
            # Extract odds from API response
            home_odds = odds_data.get('home_odds', 0.0)
            draw_odds = odds_data.get('draw_odds', 0.0)
            away_odds = odds_data.get('away_odds', 0.0)
            
            # Calculate changes
            home_change = 0.0
            draw_change = 0.0
            away_change = 0.0
            
            if last_snapshot:
                home_change = home_odds - last_snapshot.home_odds
                draw_change = draw_odds - last_snapshot.draw_odds
                away_change = away_odds - last_snapshot.away_odds
            
            # Create snapshot
            snapshot = LiveOddsSnapshot.objects.create(
                live_match=live_match,
                bookmaker=bookmaker,
                home_odds=home_odds,
                draw_odds=draw_odds,
                away_odds=away_odds,
                home_odds_change=home_change,
                draw_odds_change=draw_change,
                away_odds_change=away_change,
                total_volume=odds_data.get('volume'),
                market_confidence=odds_data.get('confidence')
            )
            
            # Detect value bets
            self._detect_value_bets(snapshot, live_match)
            
            # Check for significant odds movements
            self._check_odds_movements(snapshot, live_match)
            
        except Exception as e:
            print(f"Error saving odds snapshot: {e}")
    
    def _detect_value_bets(self, snapshot, live_match):
        """Detect value betting opportunities"""
        if not live_match.live_home_win_probability:
            return
        
        # Calculate implied probabilities from odds
        home_implied = 1 / snapshot.home_odds if snapshot.home_odds > 0 else 0
        draw_implied = 1 / snapshot.draw_odds if snapshot.draw_odds > 0 else 0
        away_implied = 1 / snapshot.away_odds if snapshot.away_odds > 0 else 0
        
        # Compare with AI predictions
        ai_home_prob = live_match.live_home_win_probability
        ai_draw_prob = live_match.live_draw_probability
        ai_away_prob = live_match.live_away_win_probability
        
        value_threshold = 0.05  # 5% edge minimum
        
        # Check for value bets
        if ai_home_prob > home_implied + value_threshold:
            snapshot.is_value_bet_home = True
            snapshot.value_percentage = (ai_home_prob - home_implied) * 100
            self._create_value_bet_alert(live_match, 'home', snapshot)
        
        elif ai_draw_prob > draw_implied + value_threshold:
            snapshot.is_value_bet_draw = True
            snapshot.value_percentage = (ai_draw_prob - draw_implied) * 100
            self._create_value_bet_alert(live_match, 'draw', snapshot)
        
        elif ai_away_prob > away_implied + value_threshold:
            snapshot.is_value_bet_away = True
            snapshot.value_percentage = (ai_away_prob - away_implied) * 100
            self._create_value_bet_alert(live_match, 'away', snapshot)
        
        snapshot.save()
    
    def _check_odds_movements(self, snapshot, live_match):
        """Check for significant odds movements"""
        significant_change = 0.3  # 30% change threshold
        
        if abs(snapshot.home_odds_change) > significant_change:
            direction = "subiu" if snapshot.home_odds_change > 0 else "caiu"
            self._create_odds_movement_alert(live_match, 'home', direction, snapshot.home_odds_change)
        
        if abs(snapshot.away_odds_change) > significant_change:
            direction = "subiu" if snapshot.away_odds_change > 0 else "caiu"
            self._create_odds_movement_alert(live_match, 'away', direction, snapshot.away_odds_change)
    
    def _create_value_bet_alert(self, live_match, bet_type, snapshot):
        """Create value bet alert"""
        bet_names = {'home': live_match.match.home_team.name, 'draw': 'Empate', 'away': live_match.match.away_team.name}
        bet_odds = {'home': snapshot.home_odds, 'draw': snapshot.draw_odds, 'away': snapshot.away_odds}
        
        message = f"""💎 Aposta de Valor Detectada!

🎯 {bet_names[bet_type]}
📊 Odd: {bet_odds[bet_type]:.2f}
📈 Valor: +{snapshot.value_percentage:.1f}%

🤖 Nossa IA indica probabilidade maior que as odds sugerem!

⚠️ Aposte com responsabilidade"""
        
        MatchAlert.objects.create(
            live_match=live_match,
            alert_type='value_bet',
            title=f"Value Bet: {bet_names[bet_type]}",
            message=message,
            conditions={'bet_type': bet_type, 'value_percentage': snapshot.value_percentage}
        )
    
    def _create_odds_movement_alert(self, live_match, team, direction, change):
        """Create odds movement alert"""
        team_name = live_match.match.home_team.name if team == 'home' else live_match.match.away_team.name
        
        message = f"""📊 Movimento Significativo de Odds!

🎯 {team_name}
📈 Odd {direction}: {abs(change):.2f}

💡 Grande volume de apostas pode indicar informação privilegiada!

⏱️ {live_match.minute}' - Aproveite o movimento!"""
        
        MatchAlert.objects.create(
            live_match=live_match,
            alert_type='odds_drop',
            title=f"Odds {direction}: {team_name}",
            message=message,
            conditions={'team': team, 'direction': direction, 'change': change}
        )
```

### 3. Celery Tasks for Live Monitoring

#### core/tasks.py additions
```python
from celery import shared_task
from .services.live_data_service import LiveDataService, LiveOddsService
from .models import LiveMatch, MatchAlert
from whatsapp_integration.services import WhatsAppService
from whatsapp_integration.models import WhatsAppUser
from datetime import datetime, timedelta
from django.utils import timezone

@shared_task
def monitor_live_matches():
    """Monitor all active live matches"""
    live_service = LiveDataService()
    odds_service = LiveOddsService()
    
    # Get all live matches
    live_matches = LiveMatch.objects.filter(
        status__in=['scheduled', 'live', 'halftime']
    )
    
    for live_match in live_matches:
        try:
            # Update match data
            live_service.update_live_match_data(live_match)
            
            # Update odds if match is live
            if live_match.status in ['live', 'halftime']:
                odds_service.update_live_odds(live_match)
                
        except Exception as e:
            print(f"Error monitoring match {live_match.id}: {e}")

@shared_task
def process_match_alerts():
    """Process and send match alerts to users"""
    whatsapp_service = WhatsAppService()
    
    # Get unprocessed alerts
    alerts = MatchAlert.objects.filter(notification_sent=False)
    
    for alert in alerts:
        try:
            # Get premium subscribers who want live notifications
            premium_users = WhatsAppUser.objects.filter(
                subscription_status__in=['premium', 'pro'],
                # Add user preference field for live notifications
            )
            
            for user in premium_users:
                # Check if user wants this type of alert
                if should_send_alert(user, alert):
                    whatsapp_service.send_text_message(user.phone_number, alert.message)
                    alert.notified_users.add(user)
            
            alert.notification_sent = True
            alert.save()
            
        except Exception as e:
            print(f"Error processing alert {alert.id}: {e}")

@shared_task
def start_match_monitoring():
    """Start monitoring for matches about to begin"""
    from .models import Match
    
    # Get matches starting within next hour
    start_time = timezone.now()
    end_time = start_time + timedelta(hours=1)
    
    upcoming_matches = Match.objects.filter(
        date__range=[start_time, end_time],
        # Only monitor important matches
        competition__priority__gte=3
    )
    
    live_service = LiveDataService()
    
    for match in upcoming_matches:
        live_match = live_service.start_live_monitoring(match.id)
        if live_match:
            print(f"Started monitoring: {match}")

@shared_task
def send_daily_match_preview():
    """Send daily match preview to premium users"""
    from .models import Match
    from ai_analytics.services import MatchPredictionService
    
    # Get today's important matches
    today = timezone.now().date()
    matches = Match.objects.filter(
        date__date=today,
        competition__priority__gte=3
    ).order_by('date')[:5]
    
    if not matches:
        return
    
    prediction_service = MatchPredictionService()
    whatsapp_service = WhatsAppService()
    
    # Generate preview message
    message = "🌅 Bom dia! Jogos importantes hoje:\n\n"
    
    for match in matches:
        # Get AI prediction
        prediction = prediction_service.predict_match_outcome(match)
        
        home_prob = prediction.get('home_win_probability', 0) * 100
        draw_prob = prediction.get('draw_probability', 0) * 100
        away_prob = prediction.get('away_win_probability', 0) * 100
        
        message += f"""🏆 {match.competition.name}
🏠 {match.home_team.name} vs {match.away_team.name}
⏰ {match.date.strftime('%H:%M')}

🤖 IA Previsão:
🏠 {home_prob:.1f}% | 🤝 {draw_prob:.1f}% | ✈️ {away_prob:.1f}%

---
"""
    
    message += "\n💎 Monitoramento ao vivo para assinantes Premium!"
    
    # Send to premium users
    premium_users = WhatsAppUser.objects.filter(
        subscription_status__in=['premium', 'pro']
    )
    
    for user in premium_users:
        whatsapp_service.send_text_message(user.phone_number, message)

def should_send_alert(user, alert):
    """Check if user should receive this alert based on preferences"""
    # Implement user notification preferences
    # For now, send all alerts to premium users
    alert_preferences = {
        'goal_scored': True,
        'red_card': True,
        'odds_drop': user.subscription_status == 'pro',  # Only Pro users get odds alerts
        'value_bet': user.subscription_status == 'pro',
        'prediction_change': True,
        'match_start': True,
        'halftime': False,  # Optional
        'fulltime': True,
    }
    
    return alert_preferences.get(alert.alert_type, True)
```

### 4. WhatsApp Live Commands Integration

#### Update whatsapp_integration/services.py
```python
def generate_response(self, message_text, user):
    message_lower = message_text.lower().strip()
    
    # Live match commands
    if message_lower.startswith('/ao_vivo') or message_lower.startswith('/live'):
        return self.handle_live_matches_command(user)
    elif message_lower.startswith('/odds'):
        return self.handle_odds_command(user, message_text)
    elif message_lower.startswith('/alerta'):
        return self.handle_alerts_command(user, message_text)
    
    # ... existing commands ...

def handle_live_matches_command(self, user):
    """Handle live matches command"""
    from core.models import LiveMatch
    
    live_matches = LiveMatch.objects.filter(
        status__in=['live', 'halftime']
    ).order_by('started_at')[:5]
    
    if not live_matches:
        return """🕐 Nenhum jogo ao vivo no momento

📅 Próximos jogos: /proximos
💎 Premium: Alertas automáticos quando jogos começarem!"""
    
    response = "⚽ Jogos ao vivo:\n\n"
    
    for live_match in live_matches:
        match = live_match.match
        
        # Status indicator
        status_icon = "🔴" if live_match.status == 'live' else "⏸️"
        
        response += f"""{status_icon} {match.home_team.name} {live_match.home_score} x {live_match.away_score} {match.away_team.name}
⏱️ {live_match.minute}' {'+' + str(live_match.added_time) if live_match.added_time > 0 else ''}
🏆 {match.competition.name}

"""
        
        # Add live predictions for premium users
        if user.can_use_premium_features and live_match.live_home_win_probability:
            home_prob = live_match.live_home_win_probability * 100
            draw_prob = live_match.live_draw_probability * 100
            away_prob = live_match.live_away_win_probability * 100
            
            response += f"""🤖 IA ao vivo:
🏠 {home_prob:.1f}% | 🤝 {draw_prob:.1f}% | ✈️ {away_prob:.1f}%

"""
        
        response += "---\n"
    
    if user.can_use_premium_features:
        response += "\n📱 Recebendo alertas automáticos!"
    else:
        response += "\n💎 Premium: Receba alertas automáticos de gols e odds!"
    
    return response

def handle_odds_command(self, user, message_text):
    """Handle odds command"""
    if not user.can_use_premium_features:
        return """🔒 Funcionalidade Premium

Para ver odds ao vivo:
💎 Premium: R$ 19,90/mês
🏆 Pro: R$ 49,90/mês

🆓 Teste 7 dias: /trial
📝 Assinar: /premium"""
    
    from core.models import LiveMatch, LiveOddsSnapshot
    
    # Try to extract team name from message
    parts = message_text.split()[1:]  # Remove /odds
    
    if not parts:
        # Show all live odds
        live_matches = LiveMatch.objects.filter(
            status__in=['live', 'halftime']
        )[:3]
        
        response = "📊 Odds ao vivo:\n\n"
        
        for live_match in live_matches:
            latest_odds = LiveOddsSnapshot.objects.filter(
                live_match=live_match
            ).order_by('-timestamp').first()
            
            if latest_odds:
                response += f"""🏠 {live_match.match.home_team.name} vs {live_match.match.away_team.name}
💰 Casa: {latest_odds.home_odds:.2f}
🤝 Empate: {latest_odds.draw_odds:.2f}
✈️ Fora: {latest_odds.away_odds:.2f}

"""
        
        return response
    
    # Search for specific team
    team_query = ' '.join(parts).lower()
    
    # Find matches with team name
    from core.models import Team
    teams = Team.objects.filter(name__icontains=team_query)[:3]
    
    if not teams:
        return f"❌ Time '{team_query}' não encontrado. Tente outro nome."
    
    response = f"📊 Odds para '{team_query}':\n\n"
    
    for team in teams:
        live_matches = LiveMatch.objects.filter(
            Q(match__home_team=team) | Q(match__away_team=team),
            status__in=['live', 'halftime']
        )
        
        for live_match in live_matches:
            latest_odds = LiveOddsSnapshot.objects.filter(
                live_match=live_match
            ).order_by('-timestamp').first()
            
            if latest_odds:
                response += f"""🏠 {live_match.match.home_team.name} vs {live_match.match.away_team.name}
⏱️ {live_match.minute}'
💰 Casa: {latest_odds.home_odds:.2f} 🤝 Empate: {latest_odds.draw_odds:.2f} ✈️ Fora: {latest_odds.away_odds:.2f}

"""
    
    return response

def handle_alerts_command(self, user, message_text):
    """Handle alerts configuration"""
    if not user.can_use_premium_features:
        return """🔒 Alertas são Premium

Receba notificações de:
⚽ Gols em tempo real
🟥 Cartões vermelhos
📊 Mudanças de odds (Pro)
💎 Apostas de valor (Pro)

🆓 Teste 7 dias: /trial"""
    
    parts = message_text.split()[1:]  # Remove /alerta
    
    if not parts:
        return """⚙️ Configurar Alertas

Digite:
/alerta gols - Liga/desliga alertas de gol
/alerta odds - Liga/desliga alertas de odds (Pro)
/alerta tudo - Liga todos os alertas

Status atual: ✅ Todos ligados"""
    
    return "⚙️ Alertas configurados com sucesso!"
```

### 5. Celery Beat Configuration

#### Update settings/celery.py
```python
CELERY_BEAT_SCHEDULE.update({
    'monitor-live-matches': {
        'task': 'core.tasks.monitor_live_matches',
        'schedule': crontab(minute='*/2'),  # Every 2 minutes
    },
    'process-match-alerts': {
        'task': 'core.tasks.process_match_alerts',
        'schedule': crontab(minute='*/1'),  # Every minute
    },
    'start-match-monitoring': {
        'task': 'core.tasks.start_match_monitoring',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
    'send-daily-match-preview': {
        'task': 'core.tasks.send_daily_match_preview',
        'schedule': crontab(hour=8, minute=0),  # Daily at 8 AM
    },
})
```

## Expected Deliverables

1. Live match monitoring system with real-time data updates
2. Live odds tracking from multiple bookmakers
3. AI-powered live match predictions
4. Automated WhatsApp alerts for goals, cards, and significant events
5. Value bet detection and notifications
6. Odds movement tracking and alerts
7. Premium user notification system
8. Live match commands in WhatsApp

## Success Criteria

- Real-time match data updates every 2 minutes
- Accurate goal and event notifications within 30 seconds
- Value bet detection with 5%+ edge threshold
- Live AI predictions updated on significant events
- Premium users receive automatic notifications
- Live odds tracking from 3+ bookmakers
- WhatsApp commands provide instant live information
