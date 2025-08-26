from django.core.management.base import BaseCommand
from django.db import transaction
from api_integration.thesportsdb_client import TheSportsDBClient
from core.models import Player, ApiSyncLog
from django.utils import timezone
import time


class Command(BaseCommand):
    """
    Update player photos from TheSportsDB API
    
    This command fetches photos for players in the database using TheSportsDB API.
    Rate limit: 30 requests per minute (2.1 seconds between requests)
    Based on official API documentation
    """
    help = 'Update player photos from TheSportsDB API for existing players'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of players to process (for testing)',
            default=None
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            help='Number of players to process per batch',
            default=50  # Increased from 10 for better efficiency
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
            self.style.SUCCESS('📸 Updating Player Photos from TheSportsDB')
        )
        self.stdout.write('=' * 60)
        
        # Initialize API client
        api_client = TheSportsDBClient()
        
        # Test connection first
        if not api_client.test_connection():
            self.stdout.write(
                self.style.ERROR('❌ TheSportsDB API connection failed')
            )
            return
        
        # Get players without photos
        players_without_photos = Player.objects.filter(
            photo_url__in=['', None]
        ).order_by('name')
        
        if options.get('limit'):
            players_without_photos = players_without_photos[:options['limit']]
            self.stdout.write(f'📝 Limited to {options["limit"]} players for testing')
        
        total_players = players_without_photos.count()
        
        if total_players == 0:
            self.stdout.write(self.style.WARNING('⚠️ No players without photos found'))
            return
        
        self.stdout.write(f'📸 Found {total_players} players without photos')
        
        if not options.get('dry_run') and not options.get('force'):
            # Confirm execution
            confirm = input(f'\nThis will attempt to find photos for {total_players} players. Continue? (y/N): ')
            if confirm.lower() not in ['y', 'yes']:
                self.stdout.write('Operation cancelled.')
                return
        
        # Process players
        stats = {
            'players_processed': 0,
            'photos_found': 0,
            'photos_updated': 0,
            'api_errors': 0,
            'not_found': 0
        }
        
        start_time = timezone.now()
        batch_size = options.get('batch_size', 50)  # Increased from 10 for better efficiency
        
        for i in range(0, total_players, batch_size):
            batch = players_without_photos[i:i + batch_size]
            self.stdout.write(f'\n📊 Processing batch {i//batch_size + 1} ({i+1}-{min(i+batch_size, total_players)}/{total_players})')
            
            for player in batch:
                try:
                    self.stdout.write(f'  🔍 Searching: {player.name}')
                    
                    # Search for player on TheSportsDB
                    players_data = api_client.search_players(player.name)
                    
                    if not players_data:
                        stats['not_found'] += 1
                        self.stdout.write(f'    ❌ Not found on TheSportsDB')
                        stats['players_processed'] += 1
                        continue
                    
                    # Find best match
                    best_match = self.find_best_match(player, players_data)
                    
                    if best_match and best_match.get('strThumb'):
                        photo_url = best_match['strThumb'].strip()
                        cutout_url = best_match.get('strCutout', '').strip()
                        
                        if options.get('dry_run'):
                            self.stdout.write(f'    🔍 [DRY RUN] Would update photo: {photo_url}')
                            stats['photos_found'] += 1
                        else:
                            # Update player with photo
                            player.photo_url = photo_url
                            if cutout_url:
                                player.cutout_url = cutout_url
                            
                            # Also update other missing info if available
                            if not player.nationality and best_match.get('strNationality'):
                                player.nationality = best_match['strNationality'].strip()
                            
                            if not player.date_of_birth and best_match.get('dateBorn'):
                                try:
                                    from datetime import datetime
                                    player.date_of_birth = datetime.strptime(
                                        best_match['dateBorn'], '%Y-%m-%d'
                                    ).date()
                                except ValueError:
                                    pass
                            
                            if not player.description and best_match.get('strDescription'):
                                player.description = best_match['strDescription'].strip()
                            
                            if not player.height and best_match.get('strHeight'):
                                player.height = best_match['strHeight'].strip()
                            
                            if not player.weight and best_match.get('strWeight'):
                                player.weight = best_match['strWeight'].strip()
                            
                            player.last_sync = timezone.now()
                            player.save()
                            
                            stats['photos_updated'] += 1
                            self.stdout.write(f'    ✅ Photo updated: {photo_url}')
                    else:
                        stats['not_found'] += 1
                        self.stdout.write(f'    ❌ No photo available')
                    
                    stats['players_processed'] += 1
                    
                    # Rate limiting - 30 requests per minute = 1 request every 2 seconds
                    time.sleep(2.1)  # Safe margin for API rate limit
                    
                except Exception as e:
                    stats['api_errors'] += 1
                    self.stdout.write(
                        self.style.ERROR(f'    ❌ Error processing player: {str(e)}')
                    )
                    stats['players_processed'] += 1
                    continue
            
            # Small break between batches
            if i + batch_size < total_players:
                self.stdout.write(f'  ⏸️ Batch completed. Brief pause...')
                time.sleep(2)
        
        # Show final results
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('📸 PHOTO UPDATE COMPLETED!'))
        self.stdout.write('=' * 60)
        
        self.stdout.write(f'⏱️  Duration: {duration:.1f} seconds')
        self.stdout.write(f'👥 Players processed: {stats["players_processed"]}')
        self.stdout.write(f'📸 Photos found: {stats["photos_found"] if options.get("dry_run") else stats["photos_updated"]}')
        self.stdout.write(f'❌ Not found: {stats["not_found"]}')
        self.stdout.write(f'🚨 API errors: {stats["api_errors"]}')
        
        if stats['players_processed'] > 0:
            success_rate = (stats['photos_updated'] / stats['players_processed']) * 100
            self.stdout.write(f'📊 Photo success rate: {success_rate:.1f}%')
        
        # Log the operation
        if not options.get('dry_run'):
            ApiSyncLog.objects.create(
                endpoint='TheSportsDB - Player Photos Update',
                http_status=200,
                records_processed=stats['players_processed'],
                records_inserted=0,
                records_updated=stats['photos_updated'],
                records_failed=stats['api_errors'],
                execution_time_ms=int(duration * 1000),
                sync_date=start_time,
                response_data={
                    'photos_found': stats['photos_updated'],
                    'not_found': stats['not_found'],
                    'operation': 'photo_update'
                }
            )

    def find_best_match(self, our_player, thesportsdb_players):
        """
        Find the best matching player from TheSportsDB results
        
        Args:
            our_player: Our Player model instance
            thesportsdb_players: List of player data from TheSportsDB
            
        Returns:
            Best matching player data or None
        """
        if not thesportsdb_players:
            return None
        
        our_name = our_player.name.lower().strip()
        our_team_name = our_player.team.name.lower().strip() if our_player.team else ''
        
        # Score each potential match
        best_match = None
        best_score = 0
        
        for player_data in thesportsdb_players:
            score = 0
            
            api_name = player_data.get('strPlayer', '').lower().strip()
            api_team = player_data.get('strTeam', '').lower().strip()
            
            # Name matching (most important)
            if api_name == our_name:
                score += 100  # Exact match
            elif our_name in api_name or api_name in our_name:
                score += 80   # Partial match
            elif self.similar_names(our_name, api_name):
                score += 60   # Similar names
            else:
                continue  # Skip if names don't match at all
            
            # Team matching (if we have team info)
            if our_team_name and api_team:
                if our_team_name in api_team or api_team in our_team_name:
                    score += 30
                elif self.similar_team_names(our_team_name, api_team):
                    score += 15
            
            # Position matching (if available)
            if our_player.position and player_data.get('strPosition'):
                our_pos = our_player.position.lower()
                api_pos = player_data.get('strPosition', '').lower()
                if our_pos in api_pos or api_pos in our_pos:
                    score += 10
            
            # Nationality matching (if available)
            if our_player.nationality and player_data.get('strNationality'):
                if our_player.nationality.lower() == player_data.get('strNationality', '').lower():
                    score += 20
            
            # Check if this is the best match so far
            if score > best_score:
                best_score = score
                best_match = player_data
        
        # Only return match if score is good enough
        if best_score >= 60:  # Minimum score threshold
            return best_match
        
        return None

    def similar_names(self, name1, name2):
        """Check if two names are similar"""
        # Simple similarity check - could be improved with fuzzy matching
        name1_parts = set(name1.split())
        name2_parts = set(name2.split())
        
        # Check if they share at least one significant part
        common_parts = name1_parts.intersection(name2_parts)
        return len(common_parts) > 0 and any(len(part) > 2 for part in common_parts)

    def similar_team_names(self, team1, team2):
        """Check if two team names are similar"""
        # Remove common words
        common_words = {'fc', 'cf', 'ac', 'united', 'city', 'club', 'football', 'soccer'}
        
        team1_clean = ' '.join([word for word in team1.split() if word not in common_words])
        team2_clean = ' '.join([word for word in team2.split() if word not in common_words])
        
        return team1_clean in team2_clean or team2_clean in team1_clean
