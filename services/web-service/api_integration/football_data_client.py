import requests
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger('mark_foot')


class RateLimiter:
    """Rate limiter for API calls"""
    
    def __init__(self, max_calls: int = 10, time_window: int = 60):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    def wait_if_needed(self):
        """Wait if we've exceeded the rate limit"""
        now = time.time()
        
        # Remove calls outside the time window
        self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
        
        # If we've reached the limit, wait
        if len(self.calls) >= self.max_calls:
            wait_time = self.time_window - (now - self.calls[0]) + 1
            if wait_time > 0:
                logger.info(f"Rate limit reached. Waiting {wait_time:.2f} seconds...")
                time.sleep(wait_time)
                # Clean up calls again after waiting
                now = time.time()
                self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
        
        # Record this call
        self.calls.append(now)


class FootballDataAPIClient:
    """Client for Football-Data.org API"""
    
    def __init__(self):
        self.base_url = settings.FOOTBALL_DATA_BASE_URL
        self.api_key = settings.FOOTBALL_DATA_API_KEY
        self.rate_limiter = RateLimiter(
            max_calls=settings.FOOTBALL_DATA_RATE_LIMIT,
            time_window=60
        )
        self.session = requests.Session()
        self.session.headers.update({
            'X-Auth-Token': self.api_key,
            'User-Agent': 'Mark-Foot/1.0'
        })
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a request to the API with rate limiting"""
        self.rate_limiter.wait_if_needed()
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        start_time = time.time()
        try:
            response = self.session.get(url, params=params)
            execution_time = int((time.time() - start_time) * 1000)
            
            logger.info(f"API Request: {endpoint} - Status: {response.status_code} - Time: {execution_time}ms")
            
            response.raise_for_status()
            return {
                'data': response.json(),
                'status_code': response.status_code,
                'execution_time': execution_time
            }
        
        except requests.exceptions.RequestException as e:
            execution_time = int((time.time() - start_time) * 1000)
            logger.error(f"API Request failed: {endpoint} - Error: {str(e)} - Time: {execution_time}ms")
            
            return {
                'data': None,
                'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None,
                'execution_time': execution_time,
                'error': str(e)
            }
    
    def get_competitions(self, areas: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get all available competitions"""
        params = {}
        if areas:
            params['areas'] = ','.join(areas)
        
        return self._make_request('competitions', params)
    
    def get_competition(self, competition_id: str) -> Dict[str, Any]:
        """Get details of a specific competition"""
        return self._make_request(f'competitions/{competition_id}')
    
    def get_competition_teams(self, competition_id: str, season: Optional[str] = None) -> Dict[str, Any]:
        """Get teams for a specific competition"""
        params = {}
        if season:
            params['season'] = season
        
        return self._make_request(f'competitions/{competition_id}/teams', params)
    
    def get_competition_matches(self, competition_id: str, **kwargs) -> Dict[str, Any]:
        """Get matches for a specific competition"""
        params = {}
        
        # Supported parameters
        supported_params = [
            'dateFrom', 'dateTo', 'stage', 'status', 'matchday', 'group', 'season'
        ]
        
        for param in supported_params:
            if param in kwargs:
                params[param] = kwargs[param]
        
        return self._make_request(f'competitions/{competition_id}/matches', params)
    
    def get_competition_standings(self, competition_id: str, **kwargs) -> Dict[str, Any]:
        """Get standings for a specific competition"""
        params = {}
        
        # Supported parameters
        supported_params = ['matchday', 'season', 'date']
        
        for param in supported_params:
            if param in kwargs:
                params[param] = kwargs[param]
        
        return self._make_request(f'competitions/{competition_id}/standings', params)
    
    def get_team(self, team_id: str) -> Dict[str, Any]:
        """Get details of a specific team"""
        return self._make_request(f'teams/{team_id}')
    
    def get_team_matches(self, team_id: str, **kwargs) -> Dict[str, Any]:
        """Get matches for a specific team"""
        params = {}
        
        # Supported parameters
        supported_params = [
            'dateFrom', 'dateTo', 'season', 'competitions', 'status', 'venue', 'limit'
        ]
        
        for param in supported_params:
            if param in kwargs:
                params[param] = kwargs[param]
        
        return self._make_request(f'teams/{team_id}/matches', params)
    
    def get_match(self, match_id: str) -> Dict[str, Any]:
        """Get details of a specific match"""
        return self._make_request(f'matches/{match_id}')
    
    def get_matches(self, **kwargs) -> Dict[str, Any]:
        """Get matches across competitions"""
        params = {}
        
        # Supported parameters
        supported_params = [
            'competitions', 'ids', 'dateFrom', 'dateTo', 'status'
        ]
        
        for param in supported_params:
            if param in kwargs:
                params[param] = kwargs[param]
        
        return self._make_request('matches', params)
    
    def get_areas(self) -> Dict[str, Any]:
        """Get all available areas"""
        return self._make_request('areas')
    
    def get_area(self, area_id: str) -> Dict[str, Any]:
        """Get details of a specific area"""
        return self._make_request(f'areas/{area_id}')


# Convenience functions for common operations
def get_free_tier_competitions() -> List[str]:
    """Get list of competition codes available in free tier"""
    return [
        'WC',   # FIFA World Cup
        'CL',   # UEFA Champions League
        'BL1',  # Bundesliga
        'DED',  # Eredivisie
        'BSA',  # Campeonato Brasileiro Série A
        'PD',   # Primera División
        'FL1',  # Ligue 1
        'ELC',  # Championship
        'PPL',  # Primeira Liga
        'EC',   # European Championship
        'SA',   # Serie A
        'PL',   # Premier League
    ]


def get_current_season_dates():
    """Get approximate current season date range"""
    now = datetime.now()
    
    # European season typically runs from August to May
    if now.month >= 8:
        season_start = datetime(now.year, 8, 1)
        season_end = datetime(now.year + 1, 5, 31)
    else:
        season_start = datetime(now.year - 1, 8, 1)
        season_end = datetime(now.year, 5, 31)
    
    return season_start.strftime('%Y-%m-%d'), season_end.strftime('%Y-%m-%d')
