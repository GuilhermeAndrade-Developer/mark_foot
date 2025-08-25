import requests
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import quote

logger = logging.getLogger('mark_foot')


class TheSportsDBClient:
    """
    Client for TheSportsDB API
    Documentation: https://www.thesportsdb.com/api.php
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://www.thesportsdb.com/api/v1/json"
        self.api_key = api_key
        self.session = requests.Session()
        
        # Rate limiting - Be respectful to free API
        self.last_request_time = 0
        self.min_request_interval = 0.5  # 0.5 seconds between requests
        
        # Configure session headers
        self.session.headers.update({
            'User-Agent': 'MarkFoot-FootballDataCollector/1.0',
            'Accept': 'application/json',
        })
    
    def _wait_for_rate_limit(self):
        """Ensure we don't exceed rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            wait_time = self.min_request_interval - time_since_last
            logger.debug(f"Rate limiting: waiting {wait_time:.2f} seconds")
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make HTTP request to TheSportsDB API"""
        self._wait_for_rate_limit()
        
        try:
            # Build URL
            if self.api_key:
                url = f"{self.base_url}/{self.api_key}/{endpoint}"
            else:
                url = f"{self.base_url}/3/{endpoint}"  # Free tier uses /3/
            
            logger.info(f"🔗 TheSportsDB Request: {endpoint}")
            start_time = time.time()
            
            response = self.session.get(url, params=params, timeout=30)
            
            execution_time = int((time.time() - start_time) * 1000)
            logger.info(f"📊 TheSportsDB Response: {response.status_code} - Time: {execution_time}ms")
            
            response.raise_for_status()
            data = response.json()
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ TheSportsDB API Error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error in TheSportsDB request: {str(e)}")
            return None
    
    def search_players(self, player_name: str) -> List[Dict]:
        """
        Search for players by name
        
        Args:
            player_name: Name of player to search for
            
        Returns:
            List of player dictionaries
        """
        if not player_name or len(player_name.strip()) < 2:
            logger.warning("Player name too short for search")
            return []
        
        # URL encode the player name
        encoded_name = quote(player_name.strip())
        endpoint = f"searchplayers.php?p={encoded_name}"
        
        try:
            data = self._make_request(endpoint)
            
            if data and 'player' in data and data['player']:
                players = data['player']
                logger.info(f"✅ Found {len(players)} players for '{player_name}'")
                return players
            else:
                logger.info(f"🔍 No players found for '{player_name}'")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error searching players for '{player_name}': {str(e)}")
            return []
    
    def get_player_by_id(self, player_id: str) -> Optional[Dict]:
        """
        Get detailed player information by ID
        
        Args:
            player_id: TheSportsDB player ID
            
        Returns:
            Player dictionary or None
        """
        endpoint = f"lookupplayer.php?id={player_id}"
        
        try:
            data = self._make_request(endpoint)
            
            if data and 'players' in data and data['players']:
                player = data['players'][0]  # Should return single player
                logger.info(f"✅ Retrieved player details for ID: {player_id}")
                return player
            else:
                logger.warning(f"🔍 No player found for ID: {player_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting player by ID {player_id}: {str(e)}")
            return None
    
    def get_team_players(self, team_name: str) -> List[Dict]:
        """
        Get all players for a specific team
        
        Args:
            team_name: Name of the team
            
        Returns:
            List of player dictionaries
        """
        if not team_name or len(team_name.strip()) < 2:
            logger.warning("Team name too short for search")
            return []
        
        # URL encode the team name
        encoded_name = quote(team_name.strip())
        endpoint = f"searchplayers.php?t={encoded_name}"
        
        try:
            data = self._make_request(endpoint)
            
            if data and 'player' in data and data['player']:
                players = data['player']
                logger.info(f"✅ Found {len(players)} players for team '{team_name}'")
                return players
            else:
                logger.info(f"🔍 No players found for team '{team_name}'")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error getting team players for '{team_name}': {str(e)}")
            return []
    
    def search_teams(self, team_name: str) -> List[Dict]:
        """
        Search for teams by name
        
        Args:
            team_name: Name of team to search for
            
        Returns:
            List of team dictionaries
        """
        if not team_name or len(team_name.strip()) < 2:
            logger.warning("Team name too short for search")
            return []
        
        encoded_name = quote(team_name.strip())
        endpoint = f"searchteams.php?t={encoded_name}"
        
        try:
            data = self._make_request(endpoint)
            
            if data and 'teams' in data and data['teams']:
                teams = data['teams']
                logger.info(f"✅ Found {len(teams)} teams for '{team_name}'")
                return teams
            else:
                logger.info(f"🔍 No teams found for '{team_name}'")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error searching teams for '{team_name}': {str(e)}")
            return []
    
    def get_league_players(self, league_name: str) -> List[Dict]:
        """
        Get players from a specific league
        
        Args:
            league_name: Name of the league
            
        Returns:
            List of player dictionaries
        """
        # First search for teams in the league, then get players from those teams
        teams = self.search_teams(league_name)
        all_players = []
        
        for team in teams[:10]:  # Limit to first 10 teams to avoid too many requests
            team_name = team.get('strTeam', '')
            if team_name:
                players = self.get_team_players(team_name)
                all_players.extend(players)
                time.sleep(0.5)  # Be extra careful with rate limiting
        
        logger.info(f"✅ Found {len(all_players)} total players for league '{league_name}'")
        return all_players
    
    def test_connection(self) -> bool:
        """
        Test API connection by searching for a famous player
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            logger.info("🧪 Testing TheSportsDB API connection...")
            players = self.search_players("Lionel Messi")
            
            if players and len(players) > 0:
                logger.info("✅ TheSportsDB API connection successful!")
                return True
            else:
                logger.warning("⚠️ TheSportsDB API connected but no test data returned")
                return False
                
        except Exception as e:
            logger.error(f"❌ TheSportsDB API connection failed: {str(e)}")
            return False
    
    def get_api_info(self) -> Dict[str, Any]:
        """
        Get information about current API usage and limits
        
        Returns:
            Dictionary with API information
        """
        return {
            'base_url': self.base_url,
            'has_api_key': self.api_key is not None,
            'tier': 'Premium' if self.api_key else 'Free',
            'rate_limit': f"1 request per {self.min_request_interval} seconds",
            'features': {
                'player_search': True,
                'team_search': True,
                'player_details': True,
                'team_players': True,
                'premium_features': self.api_key is not None
            }
        }
