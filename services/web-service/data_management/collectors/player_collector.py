import logging
import time
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
from django.utils import timezone
from django.db import transaction
from django.db.models import Q

from core.models import Player, Team, PlayerStatistics, PlayerTransfer, ApiSyncLog
from api_integration.thesportsdb_client import TheSportsDBClient

logger = logging.getLogger('mark_foot')


class PlayerDataCollector:
    """
    Collector for player data from TheSportsDB API
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = TheSportsDBClient(api_key)
        self.stats = {
            'processed': 0,
            'created': 0,
            'updated': 0,
            'failed': 0,
            'skipped': 0
        }
    
    def test_api_connection(self):
        """Test API connection and return status"""
        try:
            # Try to search for a common player
            result = self.client.search_players("Ronaldo")
            return bool(result)
        except Exception as e:
            logger.error(f"API connection test failed: {str(e)}")
            return False

    def collect_player_transfers(self, external_id: str) -> Dict[str, int]:
        """
        Collect transfer history for a specific player
        
        Args:
            external_id: TheSportsDB player ID
            
        Returns:
            Dictionary with collection statistics
        """
        stats = {
            'processed': 0,
            'created': 0,
            'updated': 0,
            'failed': 0,
            'skipped': 0
        }
        
        try:
            # Get player instance
            player = Player.objects.filter(external_id=external_id).first()
            if not player:
                logger.warning(f"Player with external_id {external_id} not found")
                return stats
            
            # Get transfers from API
            transfers_data = self.client.get_player_transfers(external_id)
            
            if not transfers_data:
                logger.info(f"No transfer data available for player {player.name}")
                return stats
            
            for transfer_data in transfers_data:
                try:
                    transfer, status = self._create_or_update_transfer(transfer_data, player)
                    
                    if transfer:
                        stats[status] += 1
                    else:
                        stats['skipped'] += 1
                    
                    stats['processed'] += 1
                    
                except Exception as e:
                    logger.error(f"Error processing transfer: {str(e)}")
                    stats['failed'] += 1
            
            logger.info(f"✅ Transfer collection completed for {player.name}: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error collecting transfers for player {external_id}: {str(e)}")
            stats['failed'] += 1
            return stats

    def collect_player_statistics(self, external_id: str, season: str = None) -> Dict[str, int]:
        """
        Collect statistics for a specific player
        
        Args:
            external_id: TheSportsDB player ID
            season: Specific season (optional)
            
        Returns:
            Dictionary with collection statistics
        """
        stats = {
            'processed': 0,
            'created': 0,
            'updated': 0,
            'failed': 0,
            'skipped': 0
        }
        
        try:
            # Get player instance
            player = Player.objects.filter(external_id=external_id).first()
            if not player:
                logger.warning(f"Player with external_id {external_id} not found")
                return stats
            
            # Get statistics from API
            stats_data = self.client.get_player_stats_by_season(external_id, season)
            
            if not stats_data:
                logger.info(f"No statistics data available for player {player.name}")
                return stats
            
            for stat_data in stats_data:
                try:
                    statistic, status = self._create_or_update_statistic(stat_data, player)
                    
                    if statistic:
                        stats[status] += 1
                    else:
                        stats['skipped'] += 1
                    
                    stats['processed'] += 1
                    
                except Exception as e:
                    logger.error(f"Error processing statistic: {str(e)}")
                    stats['failed'] += 1
            
            logger.info(f"✅ Statistics collection completed for {player.name}: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error collecting statistics for player {external_id}: {str(e)}")
            stats['failed'] += 1
            return stats

    def collect_comprehensive_player_data(self, external_id: str) -> Dict[str, Dict[str, int]]:
        """
        Collect all available data for a player (transfers, statistics, career)
        
        Args:
            external_id: TheSportsDB player ID
            
        Returns:
            Dictionary with collection statistics for each data type
        """
        logger.info(f"🔄 Starting comprehensive data collection for player {external_id}")
        
        results = {
            'transfers': {'processed': 0, 'created': 0, 'updated': 0, 'failed': 0, 'skipped': 0},
            'statistics': {'processed': 0, 'created': 0, 'updated': 0, 'failed': 0, 'skipped': 0},
            'career': {'processed': 0, 'created': 0, 'updated': 0, 'failed': 0, 'skipped': 0}
        }
        
        # Collect transfers
        time.sleep(1)  # Rate limiting
        results['transfers'] = self.collect_player_transfers(external_id)
        
        # Collect statistics
        time.sleep(1)  # Rate limiting
        results['statistics'] = self.collect_player_statistics(external_id)
        
        # Collect career data (via transfers if available)
        time.sleep(1)  # Rate limiting
        career_stats = self._collect_career_data(external_id)
        results['career'] = career_stats
        
        logger.info(f"✅ Comprehensive collection completed for player {external_id}")
        return results

    def _create_or_update_transfer(self, transfer_data: Dict, player: Player) -> Tuple[Optional[PlayerTransfer], str]:
        """
        Create or update player transfer record
        
        Args:
            transfer_data: Transfer data from API
            player: Player instance
            
        Returns:
            Tuple of (PlayerTransfer instance, status)
        """
        try:
            # Extract transfer information
            from_team_name = transfer_data.get('strTeamFrom', '').strip()
            to_team_name = transfer_data.get('strTeamTo', '').strip()
            transfer_date = self._parse_date(transfer_data.get('strDate', ''))
            season = transfer_data.get('strSeason', '').strip()
            fee = transfer_data.get('strFee', '').strip()
            transfer_type = transfer_data.get('strType', 'Transfer').strip()
            
            # Find or create teams
            from_team = self._find_or_create_team(from_team_name) if from_team_name else None
            to_team = self._find_or_create_team(to_team_name) if to_team_name else None
            
            # Create unique identifier for this transfer
            transfer_key = f"{player.external_id}_{from_team_name}_{to_team_name}_{season}"
            
            # Get or create transfer
            transfer, created = PlayerTransfer.objects.get_or_create(
                player=player,
                from_team=from_team,
                to_team=to_team,
                season=season,
                defaults={
                    'transfer_date': transfer_date,
                    'fee': fee,
                    'transfer_type': transfer_type,
                    'source': 'thesportsdb',
                    'last_sync': timezone.now()
                }
            )
            
            # Update existing transfer
            if not created:
                transfer.transfer_date = transfer_date or transfer.transfer_date
                transfer.fee = fee or transfer.fee
                transfer.transfer_type = transfer_type or transfer.transfer_type
                transfer.last_sync = timezone.now()
                transfer.save()
            
            return transfer, 'created' if created else 'updated'
            
        except Exception as e:
            logger.error(f"Error creating/updating transfer: {str(e)}")
            return None, 'failed'

    def _create_or_update_statistic(self, stat_data: Dict, player: Player) -> Tuple[Optional[PlayerStatistics], str]:
        """
        Create or update player statistics record
        
        Args:
            stat_data: Statistics data from API
            player: Player instance
            
        Returns:
            Tuple of (PlayerStatistics instance, status)
        """
        try:
            # Extract statistics information
            season = stat_data.get('strSeason', '').strip()
            competition = stat_data.get('strCompetition', '').strip()
            
            # Numeric statistics
            appearances = self._parse_int(stat_data.get('intAppearances'))
            goals = self._parse_int(stat_data.get('intGoals'))
            assists = self._parse_int(stat_data.get('intAssists'))
            yellow_cards = self._parse_int(stat_data.get('intYellow'))
            red_cards = self._parse_int(stat_data.get('intRed'))
            minutes_played = self._parse_int(stat_data.get('intMinutes'))
            
            # Get or create statistics
            statistic, created = PlayerStatistics.objects.get_or_create(
                player=player,
                season=season,
                competition=competition,
                defaults={
                    'appearances': appearances,
                    'goals': goals,
                    'assists': assists,
                    'yellow_cards': yellow_cards,
                    'red_cards': red_cards,
                    'minutes_played': minutes_played,
                    'source': 'thesportsdb',
                    'last_sync': timezone.now()
                }
            )
            
            # Update existing statistics
            if not created:
                statistic.appearances = appearances or statistic.appearances
                statistic.goals = goals or statistic.goals
                statistic.assists = assists or statistic.assists
                statistic.yellow_cards = yellow_cards or statistic.yellow_cards
                statistic.red_cards = red_cards or statistic.red_cards
                statistic.minutes_played = minutes_played or statistic.minutes_played
                statistic.last_sync = timezone.now()
                statistic.save()
            
            return statistic, 'created' if created else 'updated'
            
        except Exception as e:
            logger.error(f"Error creating/updating statistic: {str(e)}")
            return None, 'failed'

    def _collect_career_data(self, external_id: str) -> Dict[str, int]:
        """
        Collect career data (simplified - using transfer data)
        """
        stats = {
            'processed': 0,
            'created': 0,
            'updated': 0,
            'failed': 0,
            'skipped': 0
        }
        
        try:
            career_data = self.client.get_player_career(external_id)
            
            if career_data:
                stats['processed'] = len(career_data)
                stats['created'] = len(career_data)  # Simplified
                logger.info(f"Career data available: {len(career_data)} entries")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error collecting career data: {str(e)}")
            stats['failed'] += 1
            return stats

    def _find_or_create_team(self, team_name: str) -> Optional[Team]:
        """
        Find existing team or create placeholder
        
        Args:
            team_name: Name of the team
            
        Returns:
            Team instance or None
        """
        if not team_name:
            return None
        
        # Try to find existing team
        team = self._find_matching_team(team_name)
        
        if not team:
            # Create placeholder team for transfer history
            team, created = Team.objects.get_or_create(
                name=team_name,
                defaults={
                    'short_name': team_name[:10],
                    'source': 'placeholder_thesportsdb',
                    'last_sync': timezone.now()
                }
            )
            
            if created:
                logger.info(f"Created placeholder team: {team_name}")
        
        return team

    def _parse_int(self, value: str) -> Optional[int]:
        """
        Parse integer value from string
        
        Args:
            value: String value to parse
            
        Returns:
            Integer value or None
        """
        if not value:
            return None
        
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def collect_players_for_existing_teams(self):
        """Collect players for all teams in the database"""
        stats = {
            'processed': 0,
            'created': 0,
            'updated': 0,
            'failed': 0,
            'skipped': 0
        }
        
        teams = Team.objects.all()
        
        for team in teams:
            logger.info(f"Collecting players for team: {team.name}")
            
            try:
                team_stats = self.collect_team_players(team.name)
                
                # Aggregate stats
                for key in stats:
                    stats[key] += team_stats.get(key, 0)
                    
                # Add delay between team requests
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error collecting players for team {team.name}: {str(e)}")
                stats['failed'] += 1
        
        return stats

    def _parse_date(self, date_string: str) -> Optional[date]:
        """Parse date string from API"""
        if not date_string:
            return None
        
        try:
            # Try different date formats
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
                try:
                    return datetime.strptime(date_string, fmt).date()
                except ValueError:
                    continue
            
            logger.warning(f"Could not parse date: {date_string}")
            return None
            
        except Exception as e:
            logger.warning(f"Error parsing date '{date_string}': {str(e)}")
            return None
    
    def _determine_position_category(self, position: str) -> str:
        """Determine position category from position string"""
        if not position:
            return ''
        
        position_lower = position.lower()
        
        # Goalkeeper
        if any(word in position_lower for word in ['goalkeeper', 'keeper', 'gk']):
            return 'GK'
        
        # Defenders
        elif any(word in position_lower for word in [
            'defender', 'defence', 'back', 'centre-back', 'center-back',
            'left-back', 'right-back', 'full-back', 'wing-back'
        ]):
            return 'DF'
        
        # Midfielders
        elif any(word in position_lower for word in [
            'midfielder', 'midfield', 'central', 'attacking midfielder',
            'defensive midfielder', 'wing', 'winger'
        ]):
            return 'MF'
        
        # Forwards
        elif any(word in position_lower for word in [
            'forward', 'striker', 'attacker', 'centre-forward'
        ]):
            return 'FW'
        
        # Coach/Manager
        elif any(word in position_lower for word in ['manager', 'coach', 'head coach']):
            return 'COACH'
        
        return ''
    
    def _find_matching_team(self, team_name: str) -> Optional[Team]:
        """Find matching team in our database"""
        if not team_name:
            return None
        
        # Try exact match first
        team = Team.objects.filter(name__iexact=team_name).first()
        if team:
            return team
        
        # Try short name match
        team = Team.objects.filter(short_name__iexact=team_name).first()
        if team:
            return team
        
        # Try partial match
        team = Team.objects.filter(
            Q(name__icontains=team_name) | Q(short_name__icontains=team_name)
        ).first()
        
        if team:
            logger.info(f"Found partial team match: '{team_name}' -> '{team.name}'")
            return team
        
        logger.warning(f"No matching team found for: '{team_name}'")
        return None
    
    def _create_or_update_player(self, player_data: Dict) -> Tuple[Player, bool]:
        """
        Create or update player from API data
        
        Returns:
            Tuple of (Player instance, created_flag)
        """
        external_id = player_data.get('idPlayer')
        if not external_id:
            raise ValueError("Player data missing idPlayer")
        
        # Parse player data
        name = player_data.get('strPlayer', '').strip()
        if not name:
            raise ValueError("Player data missing name")
        
        team_name = player_data.get('strTeam', '').strip()
        team = self._find_matching_team(team_name) if team_name else None
        
        nationality = player_data.get('strNationality', '').strip()
        date_of_birth = self._parse_date(player_data.get('dateBorn', ''))
        gender = player_data.get('strGender', 'Male').strip()
        position = player_data.get('strPosition', '').strip()
        position_category = self._determine_position_category(position)
        status = player_data.get('strStatus', 'Active').strip()
        
        # Media URLs
        photo_url = player_data.get('strThumb', '').strip()
        cutout_url = player_data.get('strCutout', '').strip()
        
        # Additional info
        description = player_data.get('strDescription', '').strip()
        height = player_data.get('strHeight', '').strip()
        weight = player_data.get('strWeight', '').strip()
        wage = player_data.get('strWage', '').strip()
        
        # Try to get or create player
        player, created = Player.objects.get_or_create(
            external_id=external_id,
            defaults={
                'name': name,
                'team': team,
                'nationality': nationality,
                'date_of_birth': date_of_birth,
                'gender': gender,
                'position': position,
                'position_category': position_category,
                'status': status,
                'photo_url': photo_url,
                'cutout_url': cutout_url,
                'description': description,
                'height': height,
                'weight': weight,
                'wage': wage,
                'last_sync': timezone.now()
            }
        )
        
        # Update existing player if not created
        if not created:
            updated_fields = []
            
            if player.name != name:
                player.name = name
                updated_fields.append('name')
            
            if player.team != team:
                player.team = team
                updated_fields.append('team')
            
            if player.nationality != nationality:
                player.nationality = nationality
                updated_fields.append('nationality')
            
            if player.date_of_birth != date_of_birth:
                player.date_of_birth = date_of_birth
                updated_fields.append('date_of_birth')
            
            if player.position != position:
                player.position = position
                updated_fields.append('position')
            
            if player.position_category != position_category:
                player.position_category = position_category
                updated_fields.append('position_category')
            
            if player.status != status:
                player.status = status
                updated_fields.append('status')
            
            if player.photo_url != photo_url:
                player.photo_url = photo_url
                updated_fields.append('photo_url')
            
            if player.cutout_url != cutout_url:
                player.cutout_url = cutout_url
                updated_fields.append('cutout_url')
            
            if updated_fields:
                updated_fields.extend(['last_sync', 'updated_at'])
                player.last_sync = timezone.now()
                player.save(update_fields=updated_fields)
                logger.info(f"Updated player: {name} (fields: {', '.join(updated_fields)})")
        
        # Update calculated age
        if player.date_of_birth:
            player.update_age()
        
        return player, created
    
    def collect_players_by_search(self, search_term: str) -> Dict:
        """
        Collect players by searching for a specific term
        
        Args:
            search_term: Search term (player name, team name, etc.)
            
        Returns:
            Dictionary with collection statistics
        """
        logger.info(f"🔍 Searching players for: '{search_term}'")
        
        start_time = timezone.now()
        self.stats = {'processed': 0, 'created': 0, 'updated': 0, 'failed': 0, 'skipped': 0}
        
        try:
            # Search for players
            players_data = self.client.search_players(search_term)
            
            if not players_data:
                logger.info(f"No players found for search term: '{search_term}'")
                return self.stats
            
            # Process each player
            with transaction.atomic():
                for player_data in players_data:
                    try:
                        self.stats['processed'] += 1
                        
                        player, created = self._create_or_update_player(player_data)
                        
                        if created:
                            self.stats['created'] += 1
                            logger.info(f"✅ Created player: {player.name}")
                        else:
                            self.stats['updated'] += 1
                            logger.info(f"🔄 Updated player: {player.name}")
                    
                    except Exception as e:
                        self.stats['failed'] += 1
                        logger.error(f"❌ Error processing player: {str(e)}")
                        continue
            
            # Log the operation
            execution_time = int((timezone.now() - start_time).total_seconds() * 1000)
            
            ApiSyncLog.objects.create(
                endpoint=f"TheSportsDB - Search Players: {search_term}",
                http_status=200,
                records_processed=self.stats['processed'],
                records_inserted=self.stats['created'],
                records_updated=self.stats['updated'],
                records_failed=self.stats['failed'],
                execution_time_ms=execution_time,
                sync_date=start_time
            )
            
            logger.info(f"✅ Player search completed: {self.stats}")
            return self.stats
            
        except Exception as e:
            logger.error(f"❌ Error in player search for '{search_term}': {str(e)}")
            self.stats['failed'] += 1
            return self.stats
    
    def collect_team_players(self, team_name: str) -> Dict:
        """
        Collect all players from a specific team
        
        Args:
            team_name: Name of the team
            
        Returns:
            Dictionary with collection statistics
        """
        logger.info(f"🏆 Collecting players for team: '{team_name}'")
        
        start_time = timezone.now()
        self.stats = {'processed': 0, 'created': 0, 'updated': 0, 'failed': 0, 'skipped': 0}
        
        try:
            # Get team players
            players_data = self.client.get_team_players(team_name)
            
            if not players_data:
                logger.info(f"No players found for team: '{team_name}'")
                return self.stats
            
            # Process each player
            with transaction.atomic():
                for player_data in players_data:
                    try:
                        self.stats['processed'] += 1
                        
                        player, created = self._create_or_update_player(player_data)
                        
                        if created:
                            self.stats['created'] += 1
                            logger.info(f"✅ Created player: {player.name}")
                        else:
                            self.stats['updated'] += 1
                            logger.info(f"🔄 Updated player: {player.name}")
                    
                    except Exception as e:
                        self.stats['failed'] += 1
                        logger.error(f"❌ Error processing player: {str(e)}")
                        continue
            
            # Log the operation
            execution_time = int((timezone.now() - start_time).total_seconds() * 1000)
            
            ApiSyncLog.objects.create(
                endpoint=f"TheSportsDB - Team Players: {team_name}",
                http_status=200,
                records_processed=self.stats['processed'],
                records_inserted=self.stats['created'],
                records_updated=self.stats['updated'],
                records_failed=self.stats['failed'],
                execution_time_ms=execution_time,
                sync_date=start_time
            )
            
            logger.info(f"✅ Team players collection completed: {self.stats}")
            return self.stats
            
        except Exception as e:
            logger.error(f"❌ Error collecting team players for '{team_name}': {str(e)}")
            self.stats['failed'] += 1
            return self.stats
    
    def collect_players_for_existing_teams(self) -> Dict:
        """
        Collect players for all teams we have in our database
        
        Returns:
            Dictionary with collection statistics
        """
        logger.info("🏆 Collecting players for all existing teams...")
        
        start_time = timezone.now()
        total_stats = {'processed': 0, 'created': 0, 'updated': 0, 'failed': 0, 'skipped': 0}
        
        # Get all teams from our database
        teams = Team.objects.all()
        teams_count = teams.count()
        
        logger.info(f"Found {teams_count} teams to process")
        
        for i, team in enumerate(teams, 1):
            logger.info(f"Processing team {i}/{teams_count}: {team.name}")
            
            try:
                # Collect players for this team
                team_stats = self.collect_team_players(team.name)
                
                # Aggregate stats
                for key in total_stats:
                    total_stats[key] += team_stats[key]
                
                logger.info(f"Team {team.name} completed: {team_stats}")
                
                # Small delay to be respectful to the API
                import time
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Error processing team '{team.name}': {str(e)}")
                total_stats['failed'] += 1
                continue
        
        # Log the overall operation
        execution_time = int((timezone.now() - start_time).total_seconds() * 1000)
        
        ApiSyncLog.objects.create(
            endpoint="TheSportsDB - All Teams Players",
            http_status=200,
            records_processed=total_stats['processed'],
            records_inserted=total_stats['created'],
            records_updated=total_stats['updated'],
            records_failed=total_stats['failed'],
            execution_time_ms=execution_time,
            sync_date=start_time
        )
        
        logger.info(f"✅ All teams players collection completed: {total_stats}")
        return total_stats
    
    def test_api_connection(self) -> bool:
        """Test API connection"""
        return self.client.test_connection()
    
    def get_collection_stats(self) -> Dict:
        """Get current collection statistics"""
        return self.stats.copy()
