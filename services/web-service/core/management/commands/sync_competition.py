from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from api_integration.football_data_client import FootballDataAPIClient
from core.models import Competition, Team, Season, Match, Standing, ApiSyncLog
import json
from datetime import datetime


class Command(BaseCommand):
    help = 'Sync complete data for a specific competition (teams, seasons, matches, standings)'

    def add_arguments(self, parser):
        parser.add_argument(
            'competition_code',
            type=str,
            help='Competition code (e.g., PL, BSA, CL)'
        )
        parser.add_argument(
            '--season',
            type=str,
            help='Specific season to sync (e.g., 2023, 2024)',
            default='2024'
        )
        parser.add_argument(
            '--skip-teams',
            action='store_true',
            help='Skip teams synchronization'
        )
        parser.add_argument(
            '--skip-matches',
            action='store_true',
            help='Skip matches synchronization'
        )
        parser.add_argument(
            '--skip-standings',
            action='store_true',
            help='Skip standings synchronization'
        )
        parser.add_argument(
            '--limit-matches',
            type=int,
            help='Limit number of matches to sync (for testing)',
            default=None
        )

    def handle(self, *args, **options):
        competition_code = options['competition_code']
        season_year = options['season']
        
        self.stdout.write(
            self.style.SUCCESS(f'🚀 Starting sync for {competition_code} - Season {season_year}')
        )
        
        # Initialize API client
        api_client = FootballDataAPIClient()
        
        try:
            # Get competition
            competition = Competition.objects.get(code=competition_code)
            self.stdout.write(f'📊 Competition: {competition.name}')
            
        except Competition.DoesNotExist:
            raise CommandError(f'Competition {competition_code} not found. Run test_api first.')
        
        # Get or create season (using start_date year)
        from datetime import date
        start_date = date(int(season_year), 1, 1)
        end_date = date(int(season_year), 12, 31)
        
        season, created = Season.objects.get_or_create(
            competition=competition,
            start_date=start_date,
            defaults={
                'end_date': end_date,
                'current_matchday': 1
            }
        )
        
        if created:
            self.stdout.write(f'📅 Created season: {season_year}')
        else:
            self.stdout.write(f'📅 Using existing season: {season_year}')
        
        # Sync teams
        if not options['skip_teams']:
            self.sync_teams(api_client, competition, season, season_year)
        
        # Sync matches
        if not options['skip_matches']:
            self.sync_matches(api_client, competition, season, season_year, options.get('limit_matches'))
        
        # Sync standings
        if not options['skip_standings']:
            self.sync_standings(api_client, competition, season, season_year)
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Sync completed for {competition.name} - Season {season_year}!')
        )

    def sync_teams(self, api_client, competition, season, season_year):
        """Sync teams for the competition"""
        self.stdout.write('\n🔄 Syncing teams...')
        
        try:
            teams_response = api_client.get_competition_teams(competition.code, season=season_year)
            teams_data = teams_response.get('data') if teams_response else None
            
            if not teams_data:
                self.stdout.write(self.style.WARNING('⚠️ No teams data available'))
                return
            
            teams_created = 0
            teams_updated = 0
            
            for team_data in teams_data.get('teams', []):
                team, created = Team.objects.get_or_create(
                    id=team_data['id'],
                    defaults={
                        'name': team_data['name'],
                        'short_name': team_data.get('shortName', ''),
                        'tla': team_data.get('tla', ''),
                        'crest_url': team_data.get('crest', ''),
                        'address': team_data.get('address', ''),
                        'website': team_data.get('website', ''),
                        'email': team_data.get('email', ''),
                        'phone': team_data.get('phone', ''),
                        'founded': team_data.get('founded'),
                        'club_colors': team_data.get('clubColors', ''),
                        'venue': team_data.get('venue', ''),
                        'area': competition.area if hasattr(competition, 'area') else None
                    }
                )
                
                if created:
                    teams_created += 1
                    self.stdout.write(f'  👥 Created team: {team.name}')
                else:
                    teams_updated += 1
                    team.name = team_data['name']
                    team.short_name = team_data.get('shortName', '')
                    team.tla = team_data.get('tla', '')
                    team.crest_url = team_data.get('crest', '')
                    team.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Teams sync completed! Created: {teams_created}, Updated: {teams_updated}'
                )
            )
            
            # Log sync
            from django.utils import timezone
            ApiSyncLog.objects.create(
                endpoint=f'competitions/{competition.code}/teams',
                http_status=200,
                records_processed=len(teams_data.get('teams', [])),
                records_inserted=teams_created,
                records_updated=teams_updated,
                sync_date=timezone.now(),
                response_data={'teams_created': teams_created, 'teams_updated': teams_updated}
            )
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error syncing teams: {str(e)}'))
            from django.utils import timezone
            ApiSyncLog.objects.create(
                endpoint=f'competitions/{competition.code}/teams',
                http_status=500,
                error_message=str(e),
                sync_date=timezone.now(),
                response_data={'error': str(e)}
            )

    def sync_matches(self, api_client, competition, season, season_year, limit=None):
        """Sync matches for the competition"""
        self.stdout.write('\n🔄 Syncing matches...')
        
        try:
            matches_response = api_client.get_competition_matches(competition.code, season=season_year)
            matches_data = matches_response.get('data') if matches_response else None
            
            if not matches_data:
                self.stdout.write(self.style.WARNING('⚠️ No matches data available'))
                return
            
            matches_created = 0
            matches_updated = 0
            matches_list = matches_data.get('matches', [])
            
            if limit:
                matches_list = matches_list[:limit]
                self.stdout.write(f'📝 Limited to {limit} matches for testing')
            
            for match_data in matches_list:
                # Get teams
                home_team_id = match_data['homeTeam']['id']
                away_team_id = match_data['awayTeam']['id']
                
                try:
                    home_team = Team.objects.get(id=home_team_id)
                    away_team = Team.objects.get(id=away_team_id)
                except Team.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠️ Teams not found for match {match_data["id"]}, skipping...'
                        )
                    )
                    continue
                
                # Parse match date
                match_date = None
                if match_data.get('utcDate'):
                    match_date = datetime.fromisoformat(
                        match_data['utcDate'].replace('Z', '+00:00')
                    )
                
                match, created = Match.objects.get_or_create(
                    id=match_data['id'],
                    defaults={
                        'competition': competition,
                        'season': season,
                        'home_team': home_team,
                        'away_team': away_team,
                        'utc_date': match_date,
                        'status': match_data.get('status', 'SCHEDULED'),
                        'matchday': match_data.get('matchday'),
                        'stage': match_data.get('stage', ''),
                        'group_name': match_data.get('group'),
                        'home_team_score': match_data.get('score', {}).get('fullTime', {}).get('home'),
                        'away_team_score': match_data.get('score', {}).get('fullTime', {}).get('away'),
                        'winner': match_data.get('score', {}).get('winner'),
                        'duration': match_data.get('score', {}).get('duration', 'REGULAR'),
                        'venue': match_data.get('venue'),
                        'referee_name': match_data.get('referees', [{}])[0].get('name') if match_data.get('referees') else None
                    }
                )
                
                if created:
                    matches_created += 1
                    if matches_created <= 5:  # Show first 5 matches
                        self.stdout.write(
                            f'  ⚽ Created match: {home_team.name} vs {away_team.name}'
                        )
                else:
                    matches_updated += 1
                    # Update match if needed
                    if match_data.get('score', {}).get('fullTime', {}).get('home') is not None:
                        match.home_team_score = match_data['score']['fullTime']['home']
                        match.away_team_score = match_data['score']['fullTime']['away']
                        match.winner = match_data['score'].get('winner')
                        match.status = match_data.get('status', 'SCHEDULED')
                        match.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Matches sync completed! Created: {matches_created}, Updated: {matches_updated}'
                )
            )
            
            # Log sync
            from django.utils import timezone
            ApiSyncLog.objects.create(
                endpoint=f'competitions/{competition.code}/matches',
                http_status=200,
                records_processed=len(matches_list),
                records_inserted=matches_created,
                records_updated=matches_updated,
                sync_date=timezone.now(),
                response_data={'matches_created': matches_created, 'matches_updated': matches_updated}
            )
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error syncing matches: {str(e)}'))
            from django.utils import timezone
            ApiSyncLog.objects.create(
                endpoint=f'competitions/{competition.code}/matches',
                http_status=500,
                error_message=str(e),
                sync_date=timezone.now(),
                response_data={'error': str(e)}
            )

    def sync_standings(self, api_client, competition, season, season_year):
        """Sync standings for the competition"""
        self.stdout.write('\n🔄 Syncing standings...')
        
        try:
            standings_response = api_client.get_competition_standings(competition.code, season=season_year)
            standings_data = standings_response.get('data') if standings_response else None
            
            if not standings_data:
                self.stdout.write(self.style.WARNING('⚠️ No standings data available'))
                return
            
            standings_created = 0
            standings_updated = 0
            
            for standing_group in standings_data.get('standings', []):
                standing_type = standing_group.get('type', 'TOTAL')
                group = standing_group.get('group')
                
                for table_entry in standing_group.get('table', []):
                    team_id = table_entry['team']['id']
                    
                    try:
                        team = Team.objects.get(id=team_id)
                    except Team.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(f'⚠️ Team not found for standings, skipping...')
                        )
                        continue
                    
                    standing, created = Standing.objects.get_or_create(
                        competition=competition,
                        season=season,
                        team=team,
                        type=standing_type,
                        group_name=group,
                        defaults={
                            'position': table_entry.get('position'),
                            'played_games': table_entry.get('playedGames', 0),
                            'form': table_entry.get('form'),
                            'won': table_entry.get('won', 0),
                            'draw': table_entry.get('draw', 0),
                            'lost': table_entry.get('lost', 0),
                            'points': table_entry.get('points', 0),
                            'goals_for': table_entry.get('goalsFor', 0),
                            'goals_against': table_entry.get('goalsAgainst', 0),
                            'goal_difference': table_entry.get('goalDifference', 0),
                            'snapshot_date': datetime.now().date()
                        }
                    )
                    
                    if created:
                        standings_created += 1
                        if standings_created <= 3:  # Show first 3 standings
                            self.stdout.write(
                                f'  📊 Created standing: {team.name} - Position {standing.position}'
                            )
                    else:
                        standings_updated += 1
                        # Update standing data
                        standing.position = table_entry.get('position')
                        standing.played_games = table_entry.get('playedGames', 0)
                        standing.form = table_entry.get('form')
                        standing.won = table_entry.get('won', 0)
                        standing.draw = table_entry.get('draw', 0)
                        standing.lost = table_entry.get('lost', 0)
                        standing.points = table_entry.get('points', 0)
                        standing.goals_for = table_entry.get('goalsFor', 0)
                        standing.goals_against = table_entry.get('goalsAgainst', 0)
                        standing.goal_difference = table_entry.get('goalDifference', 0)
                        standing.snapshot_date = datetime.now().date()
                        standing.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Standings sync completed! Created: {standings_created}, Updated: {standings_updated}'
                )
            )
            
            # Log sync
            from django.utils import timezone
            ApiSyncLog.objects.create(
                endpoint=f'competitions/{competition.code}/standings',
                http_status=200,
                records_processed=len([table for standing_group in standings_data.get('standings', []) for table in standing_group.get('table', [])]),
                records_inserted=standings_created,
                records_updated=standings_updated,
                sync_date=timezone.now(),
                response_data={'standings_created': standings_created, 'standings_updated': standings_updated}
            )
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error syncing standings: {str(e)}'))
            from django.utils import timezone
            ApiSyncLog.objects.create(
                endpoint=f'competitions/{competition.code}/standings',
                http_status=500,
                error_message=str(e),
                sync_date=timezone.now(),
                response_data={'error': str(e)}
            )
