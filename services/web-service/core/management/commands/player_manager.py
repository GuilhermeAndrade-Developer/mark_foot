from django.core.management.base import BaseCommand
from data_management.collectors.player_collector import PlayerDataCollector
from core.models import Player, Team
from django.utils import timezone


class Command(BaseCommand):
    help = 'Manage player data collection from TheSportsDB API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            choices=['test', 'search', 'team', 'all-teams', 'stats'],
            default='test',
            help='Action to perform'
        )
        
        parser.add_argument(
            '--search',
            type=str,
            help='Search term for players'
        )
        
        parser.add_argument(
            '--team',
            type=str,
            help='Team name to collect players for'
        )
        
        parser.add_argument(
            '--api-key',
            type=str,
            help='TheSportsDB API key (optional, uses free tier if not provided)'
        )

    def handle(self, *args, **options):
        action = options['action']
        api_key = options.get('api_key')
        
        # Initialize collector
        collector = PlayerDataCollector(api_key=api_key)
        
        self.stdout.write(
            self.style.SUCCESS('🏆 Mark Foot - Player Data Manager')
        )
        self.stdout.write('=' * 60)
        
        if action == 'test':
            self.test_connection(collector)
        elif action == 'search':
            self.search_players(collector, options)
        elif action == 'team':
            self.collect_team_players(collector, options)
        elif action == 'all-teams':
            self.collect_all_teams_players(collector)
        elif action == 'stats':
            self.show_player_stats()

    def test_connection(self, collector):
        """Test API connection"""
        self.stdout.write('\n🧪 Testing TheSportsDB API connection...')
        self.stdout.write('-' * 40)
        
        if collector.test_api_connection():
            self.stdout.write(
                self.style.SUCCESS('✅ TheSportsDB API connection successful!')
            )
            
            # Show API info
            api_info = collector.client.get_api_info()
            self.stdout.write(f'\n📊 API Information:')
            self.stdout.write(f'  • Base URL: {api_info["base_url"]}')
            self.stdout.write(f'  • Tier: {api_info["tier"]}')
            self.stdout.write(f'  • Rate Limit: {api_info["rate_limit"]}')
            self.stdout.write(f'  • Has API Key: {api_info["has_api_key"]}')
            
        else:
            self.stdout.write(
                self.style.ERROR('❌ TheSportsDB API connection failed!')
            )

    def search_players(self, collector, options):
        """Search for players"""
        search_term = options.get('search')
        
        if not search_term:
            self.stdout.write(
                self.style.ERROR('❌ Search term is required. Use --search "player name"')
            )
            return
        
        self.stdout.write(f'\n🔍 Searching players for: "{search_term}"')
        self.stdout.write('-' * 40)
        
        try:
            stats = collector.collect_players_by_search(search_term)
            self.show_collection_results(stats)
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error searching players: {str(e)}')
            )

    def collect_team_players(self, collector, options):
        """Collect players for a specific team"""
        team_name = options.get('team')
        
        if not team_name:
            self.stdout.write(
                self.style.ERROR('❌ Team name is required. Use --team "team name"')
            )
            return
        
        self.stdout.write(f'\n🏆 Collecting players for team: "{team_name}"')
        self.stdout.write('-' * 40)
        
        try:
            stats = collector.collect_team_players(team_name)
            self.show_collection_results(stats)
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error collecting team players: {str(e)}')
            )

    def collect_all_teams_players(self, collector):
        """Collect players for all teams in database"""
        teams_count = Team.objects.count()
        
        if teams_count == 0:
            self.stdout.write(
                self.style.WARNING('⚠️ No teams found in database. Please sync teams first.')
            )
            return
        
        self.stdout.write(f'\n🏆 Collecting players for all {teams_count} teams...')
        self.stdout.write('-' * 40)
        
        # Show confirmation
        confirm = input(f'\nThis will attempt to collect players for {teams_count} teams. '
                       f'This may take a while. Continue? (y/N): ')
        
        if confirm.lower() not in ['y', 'yes']:
            self.stdout.write('Operation cancelled.')
            return
        
        try:
            start_time = timezone.now()
            stats = collector.collect_players_for_existing_teams()
            end_time = timezone.now()
            
            duration = (end_time - start_time).total_seconds()
            
            self.stdout.write(f'\n⏱️ Collection completed in {duration:.1f} seconds')
            self.show_collection_results(stats)
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error collecting all team players: {str(e)}')
            )

    def show_collection_results(self, stats):
        """Show collection results"""
        self.stdout.write(f'\n📊 Collection Results:')
        self.stdout.write(f'  📈 Processed: {stats["processed"]}')
        self.stdout.write(f'  ✅ Created: {stats["created"]}')
        self.stdout.write(f'  🔄 Updated: {stats["updated"]}')
        self.stdout.write(f'  ❌ Failed: {stats["failed"]}')
        self.stdout.write(f'  ⏭️ Skipped: {stats["skipped"]}')
        
        if stats['processed'] > 0:
            success_rate = ((stats['created'] + stats['updated']) / stats['processed']) * 100
            self.stdout.write(f'  📊 Success Rate: {success_rate:.1f}%')

    def show_player_stats(self):
        """Show current player statistics"""
        self.stdout.write('\n📊 Current Player Statistics:')
        self.stdout.write('-' * 40)
        
        # Basic counts
        total_players = Player.objects.count()
        active_players = Player.objects.filter(status='Active').count()
        retired_players = Player.objects.filter(status='Retired').count()
        
        self.stdout.write(f'  📈 Total Players: {total_players}')
        self.stdout.write(f'  ✅ Active Players: {active_players}')
        self.stdout.write(f'  🛑 Retired Players: {retired_players}')
        
        # Players by position
        self.stdout.write(f'\n🎯 Players by Position:')
        positions = Player.objects.values('position_category').distinct()
        
        position_choices = {
            'GK': 'Goalkeeper',
            'DF': 'Defender', 
            'MF': 'Midfielder',
            'FW': 'Forward',
            'SUB': 'Substitute',
            'COACH': 'Coach/Manager'
        }
        
        for pos in positions:
            category = pos['position_category']
            if category:
                count = Player.objects.filter(position_category=category).count()
                category_name = position_choices.get(category, category)
                self.stdout.write(f'  • {category_name}: {count}')
        
        # Players with teams
        players_with_teams = Player.objects.filter(team__isnull=False).count()
        players_without_teams = Player.objects.filter(team__isnull=True).count()
        
        self.stdout.write(f'\n🏆 Team Assignment:')
        self.stdout.write(f'  • With Teams: {players_with_teams}')
        self.stdout.write(f'  • Without Teams: {players_without_teams}')
        
        # Top nationalities
        self.stdout.write(f'\n🌍 Top Nationalities:')
        from django.db.models import Count
        
        nationalities = (Player.objects
                        .values('nationality')
                        .annotate(count=Count('nationality'))
                        .filter(nationality__isnull=False, nationality__gt='')
                        .order_by('-count')[:10])
        
        for nat in nationalities:
            nationality = nat['nationality']
            count = nat['count']
            self.stdout.write(f'  • {nationality}: {count}')
        
        # Recently synced
        from datetime import timedelta
        recent_sync = timezone.now() - timedelta(days=7)
        recently_synced = Player.objects.filter(last_sync__gte=recent_sync).count()
        
        self.stdout.write(f'\n🔄 Recently Synced (last 7 days): {recently_synced}')
        
        # Sample players
        if total_players > 0:
            self.stdout.write(f'\n👥 Sample Players:')
            sample_players = Player.objects.select_related('team')[:5]
            
            for player in sample_players:
                team_name = player.team.name if player.team else "No Team"
                self.stdout.write(f'  • {player.name} ({team_name}) - {player.position or "Unknown Position"}')
