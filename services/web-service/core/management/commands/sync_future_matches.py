from django.core.management.base import BaseCommand
from api_integration.football_data_client import FootballDataAPIClient
from core.models import Competition, Team, Season, Match
from datetime import datetime, timedelta
import json


class Command(BaseCommand):
    help = 'Sync future matches for all competitions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days ahead to sync (default: 30)'
        )
        parser.add_argument(
            '--competition',
            type=str,
            help='Specific competition code to sync (e.g., PL, BSA)'
        )

    def handle(self, *args, **options):
        days_ahead = options['days']
        specific_competition = options.get('competition')
        
        self.stdout.write(
            self.style.SUCCESS(f'🔮 Starting future matches sync for next {days_ahead} days')
        )
        
        api_client = FootballDataAPIClient()
        
        # Calculate date range
        today = datetime.now()
        end_date = today + timedelta(days=days_ahead)
        
        date_from = today.strftime('%Y-%m-%d')
        date_to = end_date.strftime('%Y-%m-%d')
        
        self.stdout.write(f'📅 Date range: {date_from} to {date_to}')
        
        # Get competitions to sync
        if specific_competition:
            try:
                competitions = [Competition.objects.get(code=specific_competition)]
                self.stdout.write(f'🎯 Syncing specific competition: {specific_competition}')
            except Competition.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ Competition {specific_competition} not found')
                )
                return
        else:
            competitions = Competition.objects.all()
            self.stdout.write(f'🌍 Syncing all {competitions.count()} competitions')
        
        total_created = 0
        total_updated = 0
        total_errors = 0
        
        for competition in competitions:
            try:
                self.stdout.write(f'\n🔄 Processing {competition.name} ({competition.code})...')
                
                # Get matches from API with date filter
                response = api_client.get_competition_matches(
                    competition.code,
                    dateFrom=date_from,
                    dateTo=date_to
                )
                
                if not response or not response.get('data'):
                    self.stdout.write(f'  ⚠️ No data available for {competition.code}')
                    continue
                
                matches_data = response['data'].get('matches', [])
                
                if not matches_data:
                    self.stdout.write(f'  📭 No matches found for {competition.code}')
                    continue
                
                self.stdout.write(f'  📊 Found {len(matches_data)} matches')
                
                # Get current season for this competition
                current_season = Season.objects.filter(
                    competition=competition,
                    start_date__lte=today.date(),
                    end_date__gte=today.date()
                ).first()
                
                if not current_season:
                    # Create a default season for 2025
                    current_season, created = Season.objects.get_or_create(
                        competition=competition,
                        start_date=datetime(2025, 1, 1).date(),
                        defaults={
                            'end_date': datetime(2025, 12, 31).date(),
                            'current_matchday': 1
                        }
                    )
                    if created:
                        self.stdout.write(f'  📅 Created season 2025 for {competition.name}')
                
                created_count = 0
                updated_count = 0
                
                for match_data in matches_data:
                    try:
                        # Get teams
                        home_team_id = match_data['homeTeam']['id']
                        away_team_id = match_data['awayTeam']['id']
                        
                        try:
                            home_team = Team.objects.get(id=home_team_id)
                            away_team = Team.objects.get(id=away_team_id)
                        except Team.DoesNotExist:
                            self.stdout.write(
                                f'    ⚠️ Teams not found for match {match_data["id"]}, skipping...'
                            )
                            continue
                        
                        # Parse match date
                        match_date = None
                        if match_data.get('utcDate'):
                            match_date = datetime.fromisoformat(
                                match_data['utcDate'].replace('Z', '+00:00')
                            )
                        
                        # Create or update match
                        match, created = Match.objects.update_or_create(
                            id=match_data['id'],
                            defaults={
                                'competition': competition,
                                'season': current_season,
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
                            created_count += 1
                            if created_count <= 3:  # Show first 3 created matches
                                status = match_data.get('status', 'SCHEDULED')
                                self.stdout.write(
                                    f'    ✅ Created: {home_team.name} vs {away_team.name} - {status}'
                                )
                        else:
                            updated_count += 1
                        
                    except Exception as e:
                        self.stdout.write(
                            f'    ❌ Error processing match {match_data.get("id", "unknown")}: {str(e)}'
                        )
                        total_errors += 1
                
                total_created += created_count
                total_updated += updated_count
                
                self.stdout.write(
                    f'  ✅ {competition.code}: Created {created_count}, Updated {updated_count}'
                )
                
            except Exception as e:
                self.stdout.write(
                    f'  ❌ Error processing {competition.code}: {str(e)}'
                )
                total_errors += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Future matches sync completed!\n'
                f'   Created: {total_created}\n'
                f'   Updated: {total_updated}\n'
                f'   Errors: {total_errors}'
            )
        )
