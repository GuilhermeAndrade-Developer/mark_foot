import requests
import time
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from ..models import BookmakerProvider, MatchOdds, OddsMovement
from core.models import Match

logger = logging.getLogger(__name__)

class BaseOddsCollector:
    def __init__(self, provider):
        self.provider = provider
        self.session = requests.Session()
        self.last_request_time = 0
        
    def rate_limit(self):
        """Implement rate limiting based on provider settings"""
        time_since_last_request = time.time() - self.last_request_time
        min_interval = 60 / self.provider.rate_limit_per_minute
        
        if time_since_last_request < min_interval:
            sleep_time = min_interval - time_since_last_request
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def make_request(self, url, headers=None, params=None):
        """Make a rate-limited request"""
        self.rate_limit()
        try:
            response = self.session.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {self.provider.name}: {str(e)}")
            return None
    
    def collect_odds_for_match(self, match):
        """Abstract method to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement collect_odds_for_match")

class OddsAPICollector(BaseOddsCollector):
    """Collector for The Odds API (odds-api.com)"""
    
    def __init__(self):
        provider = BookmakerProvider.objects.get(name="The Odds API")
        super().__init__(provider)
        self.api_key = getattr(settings, 'ODDS_API_KEY', None)
        self.base_url = "https://api.the-odds-api.com/v4"
    
    def collect_odds_for_match(self, match):
        """Collect odds for a specific match"""
        if not self.api_key:
            logger.error("ODDS_API_KEY not configured")
            return None
            
        # Format match date for API
        match_date = match.utc_date.strftime('%Y-%m-%d')
        
        headers = {
            'X-API-Key': self.api_key
        }
        
        params = {
            'sport': 'soccer_epl',  # This would need to be dynamic based on competition
            'regions': 'uk,us,eu',
            'markets': 'h2h,totals,btts',
            'oddsFormat': 'decimal',
            'dateFormat': 'iso'
        }
        
        url = f"{self.base_url}/sports/soccer_epl/odds"
        data = self.make_request(url, headers=headers, params=params)
        
        if not data:
            return None
            
        # Find odds for this specific match
        for event in data:
            # Match by team names (this would need more sophisticated matching)
            if (match.home_team.name.lower() in event.get('home_team', '').lower() and 
                match.away_team.name.lower() in event.get('away_team', '').lower()):
                
                return self._process_odds_data(match, event)
        
        return None
    
    def _process_odds_data(self, match, event_data):
        """Process and save odds data"""
        for bookmaker_data in event_data.get('bookmakers', []):
            try:
                # Get or create bookmaker
                bookmaker, created = BookmakerProvider.objects.get_or_create(
                    name=bookmaker_data['title'],
                    defaults={
                        'api_endpoint': 'https://api.the-odds-api.com',
                        'is_active': True,
                        'reliability_score': 0.8
                    }
                )
                
                # Process markets
                odds_data = {}
                for market in bookmaker_data.get('markets', []):
                    if market['key'] == 'h2h':
                        outcomes = market['outcomes']
                        for outcome in outcomes:
                            if outcome['name'] == match.home_team.name:
                                odds_data['home_win_odds'] = outcome['price']
                            elif outcome['name'] == match.away_team.name:
                                odds_data['away_win_odds'] = outcome['price']
                            elif outcome['name'] == 'Draw':
                                odds_data['draw_odds'] = outcome['price']
                    
                    elif market['key'] == 'totals':
                        for outcome in market['outcomes']:
                            if outcome['name'] == 'Over' and outcome.get('point') == 2.5:
                                odds_data['total_goals_over_2_5'] = outcome['price']
                            elif outcome['name'] == 'Under' and outcome.get('point') == 2.5:
                                odds_data['total_goals_under_2_5'] = outcome['price']
                    
                    elif market['key'] == 'btts':
                        for outcome in market['outcomes']:
                            if outcome['name'] == 'Yes':
                                odds_data['both_teams_score_yes'] = outcome['price']
                            elif outcome['name'] == 'No':
                                odds_data['both_teams_score_no'] = outcome['price']
                
                # Save or update match odds
                if all(k in odds_data for k in ['home_win_odds', 'draw_odds', 'away_win_odds']):
                    match_odds, created = MatchOdds.objects.update_or_create(
                        match=match,
                        bookmaker=bookmaker,
                        defaults=odds_data
                    )
                    
                    if not created:
                        # Track odds movements
                        self._track_odds_movements(match_odds, odds_data)
                    
                    logger.info(f"Updated odds for {match} from {bookmaker.name}")
                    return match_odds
                    
            except Exception as e:
                logger.error(f"Error processing odds for {bookmaker_data.get('title', 'Unknown')}: {str(e)}")
        
        return None
    
    def _track_odds_movements(self, match_odds, new_odds_data):
        """Track significant odds movements"""
        movements = []
        
        # Check home win odds
        if abs(match_odds.home_win_odds - new_odds_data['home_win_odds']) > 0.1:
            movements.append({
                'market_type': 'home_win',
                'old_odds': match_odds.home_win_odds,
                'new_odds': new_odds_data['home_win_odds']
            })
        
        # Check draw odds
        if abs(match_odds.draw_odds - new_odds_data['draw_odds']) > 0.1:
            movements.append({
                'market_type': 'draw',
                'old_odds': match_odds.draw_odds,
                'new_odds': new_odds_data['draw_odds']
            })
        
        # Check away win odds
        if abs(match_odds.away_win_odds - new_odds_data['away_win_odds']) > 0.1:
            movements.append({
                'market_type': 'away_win',
                'old_odds': match_odds.away_win_odds,
                'new_odds': new_odds_data['away_win_odds']
            })
        
        # Save movements
        for movement in movements:
            OddsMovement.objects.create(
                match_odds=match_odds,
                **movement
            )

class OddsCollectionService:
    def __init__(self):
        self.collectors = {
            'odds_api': OddsAPICollector(),
        }
    
    def collect_odds_for_upcoming_matches(self, days_ahead=7):
        """Collect odds for matches in the next N days"""
        start_date = timezone.now()
        end_date = start_date + timedelta(days=days_ahead)
        
        upcoming_matches = Match.objects.filter(
            utc_date__range=[start_date, end_date],
            status='SCHEDULED'
        )
        
        collected_count = 0
        for match in upcoming_matches:
            for collector_name, collector in self.collectors.items():
                try:
                    result = collector.collect_odds_for_match(match)
                    if result:
                        collected_count += 1
                        logger.info(f"Collected odds for {match} via {collector_name}")
                except Exception as e:
                    logger.error(f"Error collecting odds for {match} via {collector_name}: {str(e)}")
        
        logger.info(f"Collected odds for {collected_count} matches")
        return collected_count
    
    def collect_odds_for_match(self, match):
        """Collect odds for a specific match from all collectors"""
        results = []
        for collector_name, collector in self.collectors.items():
            try:
                result = collector.collect_odds_for_match(match)
                if result:
                    results.append(result)
                    logger.info(f"Collected odds for {match} via {collector_name}")
            except Exception as e:
                logger.error(f"Error collecting odds for {match} via {collector_name}: {str(e)}")
        
        return results
