from django.core.management.base import BaseCommand
from core.models import Competition, Team, Season, Match, Standing, ApiSyncLog
from django.db.models import Count


class Command(BaseCommand):
    help = 'Show synchronized data statistics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--competition',
            type=str,
            help='Show details for specific competition code (e.g., PL, BSA)'
        )
        parser.add_argument(
            '--logs',
            action='store_true',
            help='Show API sync logs'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('📊 Football Data Statistics Dashboard')
        )
        self.stdout.write('=' * 50)
        
        # General statistics
        self.show_general_stats()
        
        # Competition details
        if options.get('competition'):
            self.show_competition_details(options['competition'])
        else:
            self.show_all_competitions()
        
        # API logs
        if options.get('logs'):
            self.show_api_logs()

    def show_general_stats(self):
        """Show general database statistics"""
        self.stdout.write('\n📈 General Statistics:')
        self.stdout.write('-' * 30)
        
        stats = {
            'Competitions': Competition.objects.count(),
            'Teams': Team.objects.count(),
            'Seasons': Season.objects.count(),
            'Matches': Match.objects.count(),
            'Standings': Standing.objects.count(),
            'API Logs': ApiSyncLog.objects.count()
        }
        
        for key, value in stats.items():
            self.stdout.write(f'  {key}: {value}')

    def show_all_competitions(self):
        """Show all competitions with their data"""
        self.stdout.write('\n🏆 Competitions Overview:')
        self.stdout.write('-' * 30)
        
        competitions = Competition.objects.all().order_by('name')
        
        for comp in competitions:
            seasons = Season.objects.filter(competition=comp).count()
            matches = Match.objects.filter(competition=comp).count()
            standings = Standing.objects.filter(competition=comp).count()
            
            # Get unique teams from matches
            home_teams = Match.objects.filter(competition=comp).values_list('home_team_id', flat=True)
            away_teams = Match.objects.filter(competition=comp).values_list('away_team_id', flat=True)
            team_ids = set(list(home_teams) + list(away_teams))
            teams_count = len(team_ids)
            
            self.stdout.write(
                f'  📅 {comp.name} ({comp.code}):'
            )
            self.stdout.write(
                f'    - Seasons: {seasons} | Teams: {teams_count} | '
                f'Matches: {matches} | Standings: {standings}'
            )

    def show_competition_details(self, competition_code):
        """Show detailed information for a specific competition"""
        try:
            competition = Competition.objects.get(code=competition_code.upper())
        except Competition.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ Competition {competition_code} not found')
            )
            return
        
        self.stdout.write(f'\n🔍 {competition.name} ({competition.code}) Details:')
        self.stdout.write('-' * 50)
        
        # Teams
        home_team_ids = Match.objects.filter(competition=competition).values_list('home_team_id', flat=True)
        away_team_ids = Match.objects.filter(competition=competition).values_list('away_team_id', flat=True)
        team_ids = set(list(home_team_ids) + list(away_team_ids))
        teams = Team.objects.filter(id__in=team_ids).distinct()
        
        self.stdout.write(f'\n👥 Teams ({teams.count()}):')
        for team in teams.order_by('name')[:10]:  # Show first 10
            self.stdout.write(f'  - {team.name} ({team.short_name or team.tla})')
        if teams.count() > 10:
            self.stdout.write(f'  ... and {teams.count() - 10} more teams')
        
        # Seasons
        seasons = Season.objects.filter(competition=competition).order_by('-start_date')
        self.stdout.write(f'\n📅 Seasons ({seasons.count()}):')
        for season in seasons:
            matches_count = Match.objects.filter(competition=competition, season=season).count()
            standings_count = Standing.objects.filter(competition=competition, season=season).count()
            self.stdout.write(
                f'  - {season.start_date.year}: {matches_count} matches, {standings_count} standings'
            )
        
        # Latest matches
        latest_matches = Match.objects.filter(
            competition=competition
        ).order_by('-utc_date')[:5]
        
        if latest_matches:
            self.stdout.write(f'\n⚽ Latest Matches:')
            for match in latest_matches:
                score = ""
                if match.home_team_score is not None and match.away_team_score is not None:
                    score = f" ({match.home_team_score}-{match.away_team_score})"
                self.stdout.write(
                    f'  - {match.home_team.short_name or match.home_team.name} vs '
                    f'{match.away_team.short_name or match.away_team.name}{score} - {match.status}'
                )
        
        # Current standings (top 5)
        if seasons:
            latest_season = seasons.first()
            top_standings = Standing.objects.filter(
                competition=competition,
                season=latest_season,
                type='TOTAL'
            ).order_by('position')[:5]
            
            if top_standings:
                self.stdout.write(f'\n📊 Current Standings (Top 5):')
                for standing in top_standings:
                    self.stdout.write(
                        f'  {standing.position}. {standing.team.short_name or standing.team.name} - '
                        f'{standing.points} pts ({standing.won}W {standing.draw}D {standing.lost}L)'
                    )

    def show_api_logs(self):
        """Show recent API synchronization logs"""
        self.stdout.write(f'\n📋 Recent API Logs:')
        self.stdout.write('-' * 30)
        
        logs = ApiSyncLog.objects.order_by('-created_at')[:10]
        
        for log in logs:
            status_icon = '✅' if log.error_message is None else '❌'
            
            self.stdout.write(
                f'  {status_icon} {log.endpoint} - HTTP {log.http_status or "N/A"} '
                f'({log.execution_time_ms}ms) - {log.created_at.strftime("%Y-%m-%d %H:%M")}'
            )
            
            if log.records_inserted or log.records_updated:
                self.stdout.write(
                    f'      📈 Inserted: {log.records_inserted}, Updated: {log.records_updated}'
                )
            
            if log.error_message:
                self.stdout.write(
                    f'      🚨 Error: {log.error_message[:100]}...'
                )
