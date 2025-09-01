# Betting Odds Integration and Analysis

## Objective
Integrate multiple betting odds APIs and implement AI-powered analysis to explain why odds are set at specific values for football matches.

## Current Project Context
- WhatsApp chatbot with NLP engine implemented
- Existing AI analytics services in ai_analytics app
- Premium subscription system via billing app
- Football data from Football-Data.org and TheSportsDB
- Django backend with MySQL database

## Technical Requirements

### 1. Create Odds Django App
```bash
cd services/web-service
python manage.py startapp betting_odds
```

### 2. Models Implementation

#### betting_odds/models.py
```python
from django.db import models
from core.models import Match, Team
from django.utils import timezone

class BookmakerProvider(models.Model):
    name = models.CharField(max_length=100, unique=True)
    api_endpoint = models.URLField()
    api_key_required = models.BooleanField(default=True)
    rate_limit_per_minute = models.IntegerField(default=60)
    is_active = models.BooleanField(default=True)
    reliability_score = models.FloatField(default=0.8)
    created_at = models.DateTimeField(auto_now_add=True)

class MatchOdds(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='odds')
    bookmaker = models.ForeignKey(BookmakerProvider, on_delete=models.CASCADE)
    home_win_odds = models.FloatField()
    draw_odds = models.FloatField()
    away_win_odds = models.FloatField()
    total_goals_over_2_5 = models.FloatField(null=True, blank=True)
    total_goals_under_2_5 = models.FloatField(null=True, blank=True)
    both_teams_score_yes = models.FloatField(null=True, blank=True)
    both_teams_score_no = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

class OddsMovement(models.Model):
    match_odds = models.ForeignKey(MatchOdds, on_delete=models.CASCADE, related_name='movements')
    market_type = models.CharField(max_length=50)  # home_win, draw, away_win, etc.
    old_odds = models.FloatField()
    new_odds = models.FloatField()
    movement_percentage = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
class OddsAnalysis(models.Model):
    match = models.OneToOneField(Match, on_delete=models.CASCADE, related_name='odds_analysis')
    average_home_odds = models.FloatField()
    average_draw_odds = models.FloatField()
    average_away_odds = models.FloatField()
    
    # Implied probabilities
    home_probability = models.FloatField()
    draw_probability = models.FloatField()
    away_probability = models.FloatField()
    
    # AI Analysis
    home_team_form_score = models.FloatField()
    away_team_form_score = models.FloatField()
    head_to_head_factor = models.FloatField()
    home_advantage_factor = models.FloatField()
    injuries_impact_score = models.FloatField()
    weather_impact_score = models.FloatField(default=0.0)
    
    # Value betting
    value_bet_detected = models.BooleanField(default=False)
    value_bet_market = models.CharField(max_length=50, blank=True)
    value_bet_explanation = models.TextField(blank=True)
    
    # AI explanation
    odds_explanation = models.TextField()
    confidence_score = models.FloatField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class MarketAlert(models.Model):
    ALERT_TYPES = [
        ('odds_drop', 'Significant Odds Drop'),
        ('odds_surge', 'Significant Odds Surge'),
        ('value_bet', 'Value Bet Detected'),
        ('arbitrage', 'Arbitrage Opportunity'),
        ('line_movement', 'Significant Line Movement'),
    ]
    
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    market = models.CharField(max_length=50)
    trigger_odds = models.FloatField()
    current_odds = models.FloatField()
    movement_percentage = models.FloatField()
    explanation = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### 3. Odds Data Collection Services

#### betting_odds/services/odds_collectors.py
```python
import requests
import time
from datetime import datetime, timedelta
from django.conf import settings
from ..models import BookmakerProvider, MatchOdds, OddsMovement
from core.models import Match

class BaseOddsCollector:
    def __init__(self, provider):
        self.provider = provider
        self.rate_limit_delay = 60 / provider.rate_limit_per_minute
        self.last_request_time = 0
    
    def rate_limit(self):
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
    
    def collect_odds_for_match(self, match):
        raise NotImplementedError

class BetfairCollector(BaseOddsCollector):
    def __init__(self):
        provider = BookmakerProvider.objects.get(name='Betfair')
        super().__init__(provider)
        self.api_key = settings.BETFAIR_API_KEY
        self.session_token = self._authenticate()
    
    def _authenticate(self):
        # Betfair authentication implementation
        auth_url = "https://identitysso-cert.betfair.com/api/certlogin"
        headers = {
            'X-Application': self.api_key,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        payload = {
            'username': settings.BETFAIR_USERNAME,
            'password': settings.BETFAIR_PASSWORD
        }
        
        response = requests.post(auth_url, headers=headers, data=payload)
        if response.status_code == 200:
            return response.json().get('sessionToken')
        return None
    
    def collect_odds_for_match(self, match):
        if not self.session_token:
            return None
        
        self.rate_limit()
        
        url = "https://api.betfair.com/exchange/betting/rest/v1.0/listMarketBook/"
        headers = {
            'X-Application': self.api_key,
            'X-Authentication': self.session_token,
            'Content-Type': 'application/json'
        }
        
        # Implementation for fetching odds
        # This is a simplified version - actual implementation would be more complex
        
        try:
            # Create or update odds record
            odds, created = MatchOdds.objects.get_or_create(
                match=match,
                bookmaker=self.provider,
                defaults={
                    'home_win_odds': 2.0,  # Replace with actual API data
                    'draw_odds': 3.2,
                    'away_win_odds': 3.5,
                }
            )
            
            if not created:
                # Track odds movement
                self._track_odds_movement(odds, {
                    'home_win_odds': 2.0,
                    'draw_odds': 3.2,
                    'away_win_odds': 3.5,
                })
            
            return odds
        except Exception as e:
            print(f"Error collecting Betfair odds: {e}")
            return None
    
    def _track_odds_movement(self, match_odds, new_odds):
        movements = []
        
        for market, new_value in new_odds.items():
            old_value = getattr(match_odds, market)
            if old_value != new_value:
                movement_pct = ((new_value - old_value) / old_value) * 100
                
                OddsMovement.objects.create(
                    match_odds=match_odds,
                    market_type=market,
                    old_odds=old_value,
                    new_odds=new_value,
                    movement_percentage=movement_pct
                )
                
                # Update the odds record
                setattr(match_odds, market, new_value)
        
        match_odds.save()

class Bet365Collector(BaseOddsCollector):
    def __init__(self):
        provider = BookmakerProvider.objects.get(name='Bet365')
        super().__init__(provider)
        self.api_key = settings.BET365_API_KEY
    
    def collect_odds_for_match(self, match):
        self.rate_limit()
        
        # Implement Bet365 API integration
        # Note: Bet365 doesn't have a public API, so this would need to be
        # replaced with an odds aggregation service like OddsAPI
        
        try:
            # Using OddsAPI as alternative
            url = f"https://api.the-odds-api.com/v4/sports/soccer_brazil_campeonato/odds"
            params = {
                'api_key': settings.ODDS_API_KEY,
                'regions': 'us,uk,eu',
                'markets': 'h2h,totals,spreads',
                'oddsFormat': 'decimal',
                'dateFormat': 'iso'
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return self._process_odds_data(match, data)
        except Exception as e:
            print(f"Error collecting odds: {e}")
            return None
    
    def _process_odds_data(self, match, api_data):
        # Process and store odds data
        for game in api_data:
            if self._match_game_to_match(game, match):
                # Extract odds from bookmakers
                for bookmaker in game.get('bookmakers', []):
                    if bookmaker['title'] == 'Bet365':
                        markets = bookmaker.get('markets', [])
                        h2h_market = next((m for m in markets if m['key'] == 'h2h'), None)
                        
                        if h2h_market:
                            outcomes = h2h_market['outcomes']
                            home_odds = next((o['price'] for o in outcomes if match.home_team.name in o['name']), None)
                            away_odds = next((o['price'] for o in outcomes if match.away_team.name in o['name']), None)
                            draw_odds = next((o['price'] for o in outcomes if o['name'] == 'Draw'), None)
                            
                            if all([home_odds, away_odds, draw_odds]):
                                odds, created = MatchOdds.objects.get_or_create(
                                    match=match,
                                    bookmaker=self.provider,
                                    defaults={
                                        'home_win_odds': home_odds,
                                        'draw_odds': draw_odds,
                                        'away_win_odds': away_odds,
                                    }
                                )
                                return odds
        return None
    
    def _match_game_to_match(self, game_data, match):
        # Logic to match API game data with database match
        home_team = game_data.get('home_team', '')
        away_team = game_data.get('away_team', '')
        
        return (match.home_team.name.lower() in home_team.lower() and 
                match.away_team.name.lower() in away_team.lower())

class OddsCollectionService:
    def __init__(self):
        self.collectors = [
            BetfairCollector(),
            Bet365Collector(),
        ]
    
    def collect_odds_for_upcoming_matches(self):
        upcoming_matches = Match.objects.filter(
            utc_date__gte=timezone.now(),
            utc_date__lte=timezone.now() + timedelta(days=7)
        )
        
        for match in upcoming_matches:
            for collector in self.collectors:
                try:
                    collector.collect_odds_for_match(match)
                except Exception as e:
                    print(f"Error with collector {collector.__class__.__name__}: {e}")
    
    def collect_odds_for_match(self, match_id):
        match = Match.objects.get(id=match_id)
        results = []
        
        for collector in self.collectors:
            result = collector.collect_odds_for_match(match)
            if result:
                results.append(result)
        
        return results
```

### 4. AI Odds Analysis Service

#### betting_odds/services/odds_analyzer.py
```python
import numpy as np
from datetime import datetime, timedelta
from django.db.models import Avg, Q
from ..models import MatchOdds, OddsAnalysis, MarketAlert
from core.models import Match, Team
from ai_analytics.services import TeamAnalyticsService

class OddsAnalysisService:
    def __init__(self):
        self.team_analytics = TeamAnalyticsService()
    
    def analyze_match_odds(self, match):
        # Get all odds for this match
        match_odds = MatchOdds.objects.filter(match=match)
        if not match_odds.exists():
            return None
        
        # Calculate average odds
        avg_odds = match_odds.aggregate(
            avg_home=Avg('home_win_odds'),
            avg_draw=Avg('draw_odds'),
            avg_away=Avg('away_win_odds')
        )
        
        # Calculate implied probabilities
        home_prob = 1 / avg_odds['avg_home']
        draw_prob = 1 / avg_odds['avg_draw']
        away_prob = 1 / avg_odds['avg_away']
        
        # Normalize probabilities (remove bookmaker margin)
        total_prob = home_prob + draw_prob + away_prob
        home_prob_norm = home_prob / total_prob
        draw_prob_norm = draw_prob / total_prob
        away_prob_norm = away_prob / total_prob
        
        # Analyze factors affecting odds
        analysis_factors = self._analyze_odds_factors(match)
        
        # Generate explanation
        explanation = self._generate_odds_explanation(match, analysis_factors, {
            'home_prob': home_prob_norm,
            'draw_prob': draw_prob_norm,
            'away_prob': away_prob_norm
        })
        
        # Detect value bets
        value_bet_info = self._detect_value_bets(match, analysis_factors, avg_odds)
        
        # Create or update analysis
        analysis, created = OddsAnalysis.objects.update_or_create(
            match=match,
            defaults={
                'average_home_odds': avg_odds['avg_home'],
                'average_draw_odds': avg_odds['avg_draw'],
                'average_away_odds': avg_odds['avg_away'],
                'home_probability': home_prob_norm,
                'draw_probability': draw_prob_norm,
                'away_probability': away_prob_norm,
                'home_team_form_score': analysis_factors['home_form'],
                'away_team_form_score': analysis_factors['away_form'],
                'head_to_head_factor': analysis_factors['h2h_factor'],
                'home_advantage_factor': analysis_factors['home_advantage'],
                'injuries_impact_score': analysis_factors['injuries_impact'],
                'value_bet_detected': value_bet_info['detected'],
                'value_bet_market': value_bet_info['market'],
                'value_bet_explanation': value_bet_info['explanation'],
                'odds_explanation': explanation,
                'confidence_score': analysis_factors['confidence']
            }
        )
        
        return analysis
    
    def _analyze_odds_factors(self, match):
        home_team = match.home_team
        away_team = match.away_team
        
        # Team form analysis (last 5 matches)
        home_form = self._calculate_team_form(home_team)
        away_form = self._calculate_team_form(away_team)
        
        # Head-to-head analysis
        h2h_factor = self._calculate_h2h_factor(home_team, away_team)
        
        # Home advantage
        home_advantage = self._calculate_home_advantage(home_team)
        
        # Injuries impact (simplified - would need injury data)
        injuries_impact = 0.0
        
        # Overall confidence in analysis
        confidence = min(0.95, (home_form['confidence'] + away_form['confidence']) / 2)
        
        return {
            'home_form': home_form['score'],
            'away_form': away_form['score'],
            'h2h_factor': h2h_factor,
            'home_advantage': home_advantage,
            'injuries_impact': injuries_impact,
            'confidence': confidence
        }
    
    def _calculate_team_form(self, team):
        # Get last 5 matches
        recent_matches = Match.objects.filter(
            Q(home_team=team) | Q(away_team=team),
            utc_date__lt=timezone.now()
        ).order_by('-utc_date')[:5]
        
        if not recent_matches:
            return {'score': 0.5, 'confidence': 0.2}
        
        points = 0
        total_matches = len(recent_matches)
        
        for match in recent_matches:
            if match.status != 'FINISHED':
                continue
                
            home_score = match.score.get('fullTime', {}).get('home', 0) if match.score else 0
            away_score = match.score.get('fullTime', {}).get('away', 0) if match.score else 0
            
            if match.home_team == team:
                if home_score > away_score:
                    points += 3  # Win
                elif home_score == away_score:
                    points += 1  # Draw
            else:
                if away_score > home_score:
                    points += 3  # Win
                elif home_score == away_score:
                    points += 1  # Draw
        
        # Normalize to 0-1 scale
        max_points = total_matches * 3
        form_score = points / max_points if max_points > 0 else 0.5
        
        return {
            'score': form_score,
            'confidence': min(0.9, total_matches / 5)  # Higher confidence with more data
        }
    
    def _calculate_h2h_factor(self, home_team, away_team):
        # Get historical matches between teams
        h2h_matches = Match.objects.filter(
            Q(home_team=home_team, away_team=away_team) |
            Q(home_team=away_team, away_team=home_team),
            utc_date__gte=timezone.now() - timedelta(days=365*3),  # Last 3 years
            status='FINISHED'
        )[:10]  # Last 10 meetings
        
        if not h2h_matches:
            return 0.0  # Neutral if no history
        
        home_wins = 0
        away_wins = 0
        draws = 0
        
        for match in h2h_matches:
            if not match.score:
                continue
                
            home_score = match.score.get('fullTime', {}).get('home', 0)
            away_score = match.score.get('fullTime', {}).get('away', 0)
            
            # Determine winner from perspective of current home team
            if match.home_team == home_team:
                if home_score > away_score:
                    home_wins += 1
                elif home_score < away_score:
                    away_wins += 1
                else:
                    draws += 1
            else:
                if away_score > home_score:
                    home_wins += 1
                elif away_score < home_score:
                    away_wins += 1
                else:
                    draws += 1
        
        total_games = len(h2h_matches)
        if total_games == 0:
            return 0.0
        
        # Return factor favoring home team (-1 to +1)
        home_dominance = (home_wins - away_wins) / total_games
        return home_dominance
    
    def _calculate_home_advantage(self, home_team):
        # Calculate home team's performance at home vs away
        home_matches = Match.objects.filter(
            home_team=home_team,
            utc_date__gte=timezone.now() - timedelta(days=365),
            status='FINISHED'
        )
        
        away_matches = Match.objects.filter(
            away_team=home_team,
            utc_date__gte=timezone.now() - timedelta(days=365),
            status='FINISHED'
        )
        
        home_points = self._calculate_points_from_matches(home_matches, is_home=True)
        away_points = self._calculate_points_from_matches(away_matches, is_home=False)
        
        if home_matches.count() == 0 or away_matches.count() == 0:
            return 0.15  # Default home advantage
        
        home_ppg = home_points / home_matches.count()
        away_ppg = away_points / away_matches.count()
        
        # Home advantage factor
        advantage = (home_ppg - away_ppg) / 3  # Normalize
        return max(-0.3, min(0.5, advantage))  # Cap between -0.3 and 0.5
    
    def _calculate_points_from_matches(self, matches, is_home):
        points = 0
        for match in matches:
            if not match.score:
                continue
                
            home_score = match.score.get('fullTime', {}).get('home', 0)
            away_score = match.score.get('fullTime', {}).get('away', 0)
            
            if is_home:
                if home_score > away_score:
                    points += 3
                elif home_score == away_score:
                    points += 1
            else:
                if away_score > home_score:
                    points += 3
                elif home_score == away_score:
                    points += 1
        
        return points
    
    def _detect_value_bets(self, match, factors, avg_odds):
        # Calculate our own probabilities based on analysis
        base_home_prob = 0.4 + (factors['home_form'] - 0.5) * 0.3
        base_away_prob = 0.3 + (factors['away_form'] - 0.5) * 0.3
        base_draw_prob = 1 - base_home_prob - base_away_prob
        
        # Adjust for factors
        home_prob = base_home_prob + factors['home_advantage'] + factors['h2h_factor'] * 0.1
        away_prob = base_away_prob - factors['home_advantage'] - factors['h2h_factor'] * 0.1
        draw_prob = base_draw_prob
        
        # Normalize
        total = home_prob + away_prob + draw_prob
        home_prob /= total
        away_prob /= total
        draw_prob /= total
        
        # Compare with market odds
        market_home_prob = 1 / avg_odds['avg_home']
        market_away_prob = 1 / avg_odds['avg_away']
        market_draw_prob = 1 / avg_odds['avg_draw']
        
        value_threshold = 0.05  # 5% edge required
        
        # Check for value bets
        if home_prob - market_home_prob > value_threshold:
            return {
                'detected': True,
                'market': 'home_win',
                'explanation': f"Nossa análise indica {home_prob:.1%} de chance vs {market_home_prob:.1%} implícita nas odds. Valor detectado!"
            }
        elif away_prob - market_away_prob > value_threshold:
            return {
                'detected': True,
                'market': 'away_win',
                'explanation': f"Nossa análise indica {away_prob:.1%} de chance vs {market_away_prob:.1%} implícita nas odds. Valor detectado!"
            }
        elif draw_prob - market_draw_prob > value_threshold:
            return {
                'detected': True,
                'market': 'draw',
                'explanation': f"Nossa análise indica {draw_prob:.1%} de chance vs {market_draw_prob:.1%} implícita nas odds. Valor detectado!"
            }
        
        return {'detected': False, 'market': '', 'explanation': ''}
    
    def _generate_odds_explanation(self, match, factors, probabilities):
        home_team = match.home_team.name
        away_team = match.away_team.name
        
        explanation = f"Análise das odds {home_team} x {away_team}:\n\n"
        
        # Favorite identification
        if probabilities['home_prob'] > probabilities['away_prob']:
            favorite = home_team
            underdog = away_team
            fav_prob = probabilities['home_prob']
        else:
            favorite = away_team
            underdog = home_team
            fav_prob = probabilities['away_prob']
        
        explanation += f"🏆 Favorito: {favorite} ({fav_prob:.1%} de chance)\n\n"
        
        # Form analysis
        if factors['home_form'] > 0.6:
            explanation += f"✅ {home_team} em boa forma recente\n"
        elif factors['home_form'] < 0.4:
            explanation += f"⚠️ {home_team} com forma irregular\n"
        
        if factors['away_form'] > 0.6:
            explanation += f"✅ {away_team} em boa forma recente\n"
        elif factors['away_form'] < 0.4:
            explanation += f"⚠️ {away_team} com forma irregular\n"
        
        # Home advantage
        if factors['home_advantage'] > 0.2:
            explanation += f"🏠 {home_team} tem forte vantagem em casa\n"
        elif factors['home_advantage'] < -0.1:
            explanation += f"🏠 {home_team} não tem vantagem clara em casa\n"
        
        # Head-to-head
        if factors['h2h_factor'] > 0.2:
            explanation += f"📊 {home_team} dominante no histórico recente\n"
        elif factors['h2h_factor'] < -0.2:
            explanation += f"📊 {away_team} dominante no histórico recente\n"
        
        explanation += f"\n🎯 Confiança da análise: {factors['confidence']:.0%}"
        
        return explanation
```

### 5. Integration with WhatsApp Bot

#### Update nlp_engine/services.py ResponseGenerator
```python
# Add odds response method
def generate_odds_response(self, entities, user):
    if not user.is_premium:
        return """🎲 Análise de Odds - Premium

Para acessar análises completas de odds:

💎 Premium - R$ 19,90/mês
✅ Análise detalhada de odds
✅ Explicação do "porquê" das cotações
✅ Value bets identificados
✅ Alertas de mudanças importantes

Digite /premium para assinar"""
    
    # For premium users, get odds analysis
    from betting_odds.services.odds_analyzer import OddsAnalysisService
    from core.models import Match
    
    if 'teams' in entities and len(entities['teams']) >= 2:
        # Find match between specified teams
        team_ids = [team['id'] for team in entities['teams'][:2]]
        match = Match.objects.filter(
            Q(home_team_id=team_ids[0], away_team_id=team_ids[1]) |
            Q(home_team_id=team_ids[1], away_team_id=team_ids[0]),
            utc_date__gte=timezone.now()
        ).first()
        
        if match:
            analyzer = OddsAnalysisService()
            analysis = analyzer.analyze_match_odds(match)
            
            if analysis:
                response = f"🎲 {match.home_team.name} x {match.away_team.name}\n\n"
                response += f"📊 Odds médias:\n"
                response += f"• Casa: {analysis.average_home_odds:.2f} ({analysis.home_probability:.1%})\n"
                response += f"• Empate: {analysis.average_draw_odds:.2f} ({analysis.draw_probability:.1%})\n"
                response += f"• Visitante: {analysis.average_away_odds:.2f} ({analysis.away_probability:.1%})\n\n"
                
                if analysis.value_bet_detected:
                    response += f"💎 Value Bet: {analysis.value_bet_market}\n"
                    response += f"{analysis.value_bet_explanation}\n\n"
                
                response += f"🧠 Explicação:\n{analysis.odds_explanation[:500]}..."
                
                return response
    
    return "🎲 Especifique dois times para análise de odds. Ex: 'Odds Flamengo x Palmeiras'"
```

### 6. Celery Tasks for Odds Collection

#### betting_odds/tasks.py
```python
from celery import shared_task
from .services.odds_collectors import OddsCollectionService
from .services.odds_analyzer import OddsAnalysisService

@shared_task(bind=True, max_retries=3)
def collect_upcoming_match_odds(self):
    try:
        collector = OddsCollectionService()
        collector.collect_odds_for_upcoming_matches()
    except Exception as exc:
        self.retry(countdown=300, exc=exc)  # Retry in 5 minutes

@shared_task(bind=True, max_retries=3)
def analyze_match_odds(self, match_id):
    try:
        from core.models import Match
        match = Match.objects.get(id=match_id)
        analyzer = OddsAnalysisService()
        analyzer.analyze_match_odds(match)
    except Exception as exc:
        self.retry(countdown=60, exc=exc)

@shared_task
def update_all_odds_analysis():
    from core.models import Match
    from django.utils import timezone
    from datetime import timedelta
    
    upcoming_matches = Match.objects.filter(
        utc_date__gte=timezone.now(),
        utc_date__lte=timezone.now() + timedelta(days=3)
    )
    
    for match in upcoming_matches:
        analyze_match_odds.delay(match.id)
```

### 7. Environment Configuration

#### Add to .env
```
# Betting APIs
BETFAIR_API_KEY=your_betfair_api_key
BETFAIR_USERNAME=your_betfair_username
BETFAIR_PASSWORD=your_betfair_password
BET365_API_KEY=your_bet365_api_key
ODDS_API_KEY=your_odds_api_key
```

### 8. Management Commands

#### betting_odds/management/commands/setup_bookmakers.py
```python
from django.core.management.base import BaseCommand
from betting_odds.models import BookmakerProvider

class Command(BaseCommand):
    help = 'Setup initial bookmaker providers'
    
    def handle(self, *args, **options):
        providers = [
            {
                'name': 'Betfair',
                'api_endpoint': 'https://api.betfair.com/exchange/betting/rest/v1.0/',
                'rate_limit_per_minute': 100,
                'reliability_score': 0.95
            },
            {
                'name': 'Bet365',
                'api_endpoint': 'https://api.the-odds-api.com/v4/',
                'rate_limit_per_minute': 500,
                'reliability_score': 0.90
            },
            {
                'name': 'Pinnacle',
                'api_endpoint': 'https://api.pinnacle.com/v1/',
                'rate_limit_per_minute': 200,
                'reliability_score': 0.92
            }
        ]
        
        for provider_data in providers:
            provider, created = BookmakerProvider.objects.get_or_create(
                name=provider_data['name'],
                defaults=provider_data
            )
            
            if created:
                self.stdout.write(f'Created provider: {provider.name}')
            else:
                self.stdout.write(f'Provider {provider.name} already exists')
```

## Integration Requirements

### Dependencies
```
# Add to requirements.txt
requests>=2.31.0
numpy>=1.24.0
```

### Settings Configuration
```python
# Add to INSTALLED_APPS
'betting_odds',

# Celery beat schedule
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE.update({
    'collect-odds-every-hour': {
        'task': 'betting_odds.tasks.collect_upcoming_match_odds',
        'schedule': crontab(minute=0),  # Every hour
    },
    'analyze-odds-daily': {
        'task': 'betting_odds.tasks.update_all_odds_analysis',
        'schedule': crontab(hour=6, minute=0),  # Daily at 6 AM
    },
})
```

## Expected Deliverables

1. Odds collection from multiple bookmakers
2. AI-powered odds analysis and explanation
3. Value bet detection system
4. Odds movement tracking
5. Integration with WhatsApp bot for premium users
6. Real-time alerts for significant odds changes
7. Historical odds data storage
8. Responsible gambling features

## Success Criteria

- Successfully collects odds from at least 2 major bookmakers
- Provides accurate explanations for why odds are set at specific values
- Detects value betting opportunities with reasonable accuracy
- Integrates seamlessly with WhatsApp premium features
- Maintains data collection within API rate limits
- Provides educational content about odds and probability
