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
    
    def get_player_transfers(self, player_id: str) -> Optional[List[Dict]]:
        """
        Get player transfer history from TheSportsDB
        
        Args:
            player_id: TheSportsDB player ID
            
        Returns:
            List of transfer records or None if error
        """
        endpoint = f"lookuptransfers.php?id={player_id}"
        
        try:
            response = self._make_request(endpoint)
            
            if response and 'transfers' in response:
                transfers = response['transfers']
                logger.info(f"✅ Found {len(transfers) if transfers else 0} transfers for player {player_id}")
                return transfers or []
            
            logger.warning(f"⚠️ No transfers found for player {player_id}")
            return []
            
        except Exception as e:
            logger.error(f"❌ Error fetching transfers for player {player_id}: {str(e)}")
            return None

    def get_player_career(self, player_id: str) -> Optional[List[Dict]]:
        """
        Get player career history (all teams/clubs)
        
        Args:
            player_id: TheSportsDB player ID
            
        Returns:
            List of career records or None if error
        """
        endpoint = f"lookupcareer.php?id={player_id}"
        
        try:
            response = self._make_request(endpoint)
            
            if response and 'career' in response:
                career = response['career']
                logger.info(f"✅ Found {len(career) if career else 0} career entries for player {player_id}")
                return career or []
            
            logger.warning(f"⚠️ No career data found for player {player_id}")
            return []
            
        except Exception as e:
            logger.error(f"❌ Error fetching career for player {player_id}: {str(e)}")
            return None

    def get_player_stats_by_season(self, player_id: str, season: str = None) -> Optional[List[Dict]]:
        """
        Get player statistics by season
        
        Args:
            player_id: TheSportsDB player ID
            season: Specific season (e.g., "2023-2024"), if None gets all
            
        Returns:
            List of statistics records or None if error
        """
        endpoint = f"lookupstats.php?id={player_id}"
        if season:
            endpoint += f"&s={season}"
        
        try:
            response = self._make_request(endpoint)
            
            if response and 'playerstats' in response:
                stats = response['playerstats']
                logger.info(f"✅ Found {len(stats) if stats else 0} stat records for player {player_id}")
                return stats or []
            
            logger.warning(f"⚠️ No stats found for player {player_id}")
            return []
            
        except Exception as e:
            logger.error(f"❌ Error fetching stats for player {player_id}: {str(e)}")
            return None

    def get_player_milestones(self, player_id: str) -> Optional[List[Dict]]:
        """
        Get player career milestones and achievements
        
        Args:
            player_id: TheSportsDB player ID
            
        Returns:
            List of milestone records or None if error
        """
        endpoint = f"lookupmilestones.php?id={player_id}"
        
        try:
            response = self._make_request(endpoint)
            
            if response and 'milestones' in response:
                milestones = response['milestones']
                logger.info(f"✅ Found {len(milestones) if milestones else 0} milestones for player {player_id}")
                return milestones or []
            
            logger.warning(f"⚠️ No milestones found for player {player_id}")
            return []
            
        except Exception as e:
            logger.error(f"❌ Error fetching milestones for player {player_id}: {str(e)}")
            return None

    def search_players_advanced(self, search_term: str, team: str = None, nationality: str = None) -> Optional[List[Dict]]:
        """
        Advanced player search with filters
        
        Args:
            search_term: Player name to search for
            team: Filter by team name (optional)
            nationality: Filter by nationality (optional)
            
        Returns:
            List of filtered player records or None if error
        """
        players = self.search_players(search_term)
        
        if not players:
            return None
        
        # Apply filters
        filtered_players = players
        
        if team:
            team_lower = team.lower()
            filtered_players = [
                p for p in filtered_players 
                if p.get('strTeam', '').lower().find(team_lower) != -1
            ]
        
        if nationality:
            nationality_lower = nationality.lower()
            filtered_players = [
                p for p in filtered_players 
                if p.get('strNationality', '').lower().find(nationality_lower) != -1
            ]
        
        logger.info(f"🔍 Advanced search: {len(filtered_players)} players after filtering")
        return filtered_players

    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
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
