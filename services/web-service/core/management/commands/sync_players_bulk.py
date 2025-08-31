from django.core.management.base import BaseCommand
from django.db import transaction
from api_integration.football_data_client import FootballDataAPIClient
from core.models import Team, Player, Area, ApiSyncLog
from django.utils import timezone
import time


class Command(BaseCommand):
    help = 'Bulk sync players from Football-Data.org API using teams data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--competition',
            type=str,
            help='Sync players only from teams in specific competition (e.g., PL, BL1)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of teams to process (for testing)',
            default=None
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip confirmation prompt'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Bulk Player Sync from Football-Data.org')
        )
        self.stdout.write('=' * 60)
        
        # Initialize API client
        api_client = FootballDataAPIClient()
        
        # Get teams to process
        teams = self.get_teams_to_process(options.get('competition'))
        
        if options.get('limit'):
            teams = teams[:options['limit']]
            self.stdout.write(f'📝 Limited to {options["limit"]} teams for testing')
        
        total_teams = len(teams)
        
        if total_teams == 0:
            self.stdout.write(self.style.WARNING('⚠️ No teams found to process'))
            return
        
        self.stdout.write(f'🏆 Found {total_teams} teams to process')
        
        if not options.get('dry_run') and not options.get('force'):
            # Confirm execution
            confirm = input(f'\nThis will sync players for {total_teams} teams. Continue? (y/N): ')
            if confirm.lower() not in ['y', 'yes']:
                self.stdout.write('Operation cancelled.')
                return
        
        # Process teams
        stats = {
            'teams_processed': 0,
            'teams_with_squad': 0,
            'players_created': 0,
            'players_updated': 0,
            'players_failed': 0,
            'api_errors': 0
        }
        
        start_time = timezone.now()
        
        for i, team in enumerate(teams, 1):
            self.stdout.write(f'\n📊 [{i}/{total_teams}] Processing: {team.name}')
            
            try:
                team_stats = self.sync_team_players(api_client, team, options.get('dry_run', False))
                
                # Update overall stats
                stats['teams_processed'] += 1
                if team_stats['players_processed'] > 0:
                    stats['teams_with_squad'] += 1
                stats['players_created'] += team_stats['players_created']
                stats['players_updated'] += team_stats['players_updated']
                stats['players_failed'] += team_stats['players_failed']
                
                self.stdout.write(
                    f'  ✅ {team_stats["players_created"]} created, '
                    f'{team_stats["players_updated"]} updated, '
                    f'{team_stats["players_failed"]} failed'
                )
                
            except Exception as e:
                stats['api_errors'] += 1
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Error processing team: {str(e)}')
                )
        
        # Show final results
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('🎯 BULK SYNC COMPLETED!'))
        self.stdout.write('=' * 60)
        
        self.stdout.write(f'⏱️  Duration: {duration:.1f} seconds')
        self.stdout.write(f'🏆 Teams processed: {stats["teams_processed"]}')
        self.stdout.write(f'👥 Teams with squad data: {stats["teams_with_squad"]}')
        self.stdout.write(f'✅ Players created: {stats["players_created"]}')
        self.stdout.write(f'🔄 Players updated: {stats["players_updated"]}')
        self.stdout.write(f'❌ Players failed: {stats["players_failed"]}')
        self.stdout.write(f'🚨 API errors: {stats["api_errors"]}')
        
        if stats['teams_processed'] > 0:
            success_rate = ((stats['players_created'] + stats['players_updated']) / 
                          max(1, stats['players_created'] + stats['players_updated'] + stats['players_failed'])) * 100
            self.stdout.write(f'📊 Success rate: {success_rate:.1f}%')
            
            avg_players_per_team = (stats['players_created'] + stats['players_updated']) / stats['teams_with_squad'] if stats['teams_with_squad'] > 0 else 0
            self.stdout.write(f'📈 Avg players per team: {avg_players_per_team:.1f}')

    def get_teams_to_process(self, competition_code=None):
        """Get teams to process players for"""
        if competition_code:
            # Get teams from specific competition
            from core.models import Competition, Match
            try:
                competition = Competition.objects.get(code=competition_code.upper())
                
                # Get teams that have played in this competition
                home_team_ids = Match.objects.filter(competition=competition).values_list('home_team_id', flat=True)
                away_team_ids = Match.objects.filter(competition=competition).values_list('away_team_id', flat=True)
                team_ids = set(list(home_team_ids) + list(away_team_ids))
                
                teams = Team.objects.filter(id__in=team_ids).order_by('name')
                self.stdout.write(f'🏆 Processing teams from {competition.name}')
                
            except Competition.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ Competition {competition_code} not found')
                )
                return Team.objects.none()
        else:
            # Get all teams
            teams = Team.objects.all().order_by('name')
            self.stdout.write('🌍 Processing all teams')
        
        return teams

    def sync_team_players(self, api_client, team, dry_run=False):
        """Sync players for a specific team"""
        stats = {
            'players_processed': 0,
            'players_created': 0,
            'players_updated': 0,
            'players_failed': 0
        }
        
        try:
            # Get team details with squad
            response = api_client.get_team(str(team.id))
            
            if not response.get('data'):
                self.stdout.write(f'  ⚠️ No data returned for team {team.name}')
                return stats
            
            team_data = response['data']
            squad = team_data.get('squad', [])
            
            if not squad:
                self.stdout.write(f'  ⚠️ No squad data for team {team.name}')
                return stats
            
            stats['players_processed'] = len(squad)
            
            if dry_run:
                self.stdout.write(f'  🔍 [DRY RUN] Would process {len(squad)} players')
                for player_data in squad[:3]:  # Show first 3 players
                    self.stdout.write(f'    - {player_data.get("name", "N/A")} ({player_data.get("position", "N/A")})')
                if len(squad) > 3:
                    self.stdout.write(f'    ... and {len(squad) - 3} more players')
                return stats
            
            # Process each player
            for player_data in squad:
                try:
                    player_stats = self.process_player(player_data, team)
                    
                    if player_stats['created']:
                        stats['players_created'] += 1
                    elif player_stats['updated']:
                        stats['players_updated'] += 1
                        
                except Exception as e:
                    stats['players_failed'] += 1
                    self.stdout.write(f'    ❌ Failed to process player: {str(e)[:50]}...')
            
            # Log successful sync
            ApiSyncLog.objects.create(
                endpoint=f'teams/{team.id}/squad',
                http_status=response.get('status_code', 200),
                records_processed=stats['players_processed'],
                records_inserted=stats['players_created'],
                records_updated=stats['players_updated'],
                sync_date=timezone.now(),
                execution_time_ms=response.get('execution_time', 0),
                response_data={
                    'team_name': team.name,
                    'squad_size': len(squad)
                }
            )
            
        except Exception as e:
            # Log error
            ApiSyncLog.objects.create(
                endpoint=f'teams/{team.id}/squad',
                http_status=500,
                error_message=str(e),
                sync_date=timezone.now(),
                response_data={'team_name': team.name, 'error': str(e)}
            )
            raise e
        
        return stats

    def process_player(self, player_data, team):
        """Process individual player data"""
        stats = {'created': False, 'updated': False}
        
        # Extract player data
        external_id = str(player_data.get('id'))
        name = player_data.get('name', '').strip()
        position = player_data.get('position', '').strip()
        date_of_birth = player_data.get('dateOfBirth')
        nationality = player_data.get('nationality', '').strip()
        
        if not name or not external_id:
            raise ValueError("Player name and ID are required")
        
        # Convert position to category
        position_category = self.get_position_category(position)
        
        # Parse date of birth
        birth_date = None
        if date_of_birth:
            try:
                from datetime import datetime
                birth_date = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # Get or create player
        player, created = Player.objects.get_or_create(
            external_id=external_id,
            defaults={
                'name': name,
                'position': position,
                'position_category': position_category or 'UNKNOWN',
                'date_of_birth': birth_date,
                'nationality': nationality,
                'team': team,
                'status': 'Active',
                'last_sync': timezone.now()
            }
        )
        
        if created:
            stats['created'] = True
        else:
            # Update existing player
            player.name = name
            player.position = position
            player.position_category = position_category
            player.date_of_birth = birth_date or player.date_of_birth
            player.nationality = nationality or player.nationality
            player.team = team
            player.status = 'Active'
            player.last_sync = timezone.now()
            player.save()
            stats['updated'] = True
        
        return stats

    def get_position_category(self, position):
        """Convert position to category"""
        if not position:
            return None
        
        position = position.lower()
        
        if 'goalkeeper' in position or 'keeper' in position:
            return 'GK'
        elif any(word in position for word in ['defence', 'defender', 'back']):
            return 'DF'
        elif any(word in position for word in ['midfield', 'midfielder']):
            return 'MF'
        elif any(word in position for word in ['forward', 'striker', 'winger', 'attack']):
            return 'FW'
        else:
            return None
