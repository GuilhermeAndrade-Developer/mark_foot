import os
import django
from celery import shared_task

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mark_foot_backend.settings')
django.setup()

from django.utils import timezone
from datetime import datetime, timedelta
import logging

from core.models import Competition, Season, Match, Team, Standing, ApiSyncLog
from api_integration.football_data_client import FootballDataAPIClient

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def sync_live_matches(self):
    """
    Sync matches that are currently live or scheduled for today
    """
    logger.info("Starting live matches sync task")
    
    try:
        api_client = FootballDataAPIClient()
        today = timezone.now().date()
        
        # Get competitions that have active seasons
        active_competitions = Competition.objects.filter(
            season__start_date__lte=today,
            season__end_date__gte=today
        ).distinct()
        
        total_updated = 0
        total_errors = 0
        
        for competition in active_competitions:
            try:
                logger.info(f"Syncing matches for {competition.name}")
                
                # Get matches for today
                matches_response = api_client.get_competition_matches(
                    competition.code,
                    dateFrom=today.isoformat(),
                    dateTo=today.isoformat()
                )
                
                if not matches_response or not matches_response.get('data'):
                    continue
                
                matches_data = matches_response['data']
                updated_count = 0
                
                for match_data in matches_data.get('matches', []):
                    try:
                        match = Match.objects.get(id=match_data['id'])
                        
                        # Update match status and scores if available
                        match.status = match_data.get('status', match.status)
                        
                        if match_data.get('score', {}).get('fullTime', {}).get('home') is not None:
                            match.home_team_score = match_data['score']['fullTime']['home']
                            match.away_team_score = match_data['score']['fullTime']['away']
                            match.winner = match_data['score'].get('winner')
                        
                        match.save()
                        updated_count += 1
                        
                    except Match.DoesNotExist:
                        logger.warning(f"Match {match_data['id']} not found in database")
                        continue
                    except Exception as e:
                        logger.error(f"Error updating match {match_data['id']}: {str(e)}")
                        total_errors += 1
                
                total_updated += updated_count
                logger.info(f"Updated {updated_count} matches for {competition.name}")
                
                # Log sync
                ApiSyncLog.objects.create(
                    endpoint=f'competitions/{competition.code}/matches',
                    http_status=matches_response.get('status_code', 200),
                    records_processed=len(matches_data.get('matches', [])),
                    records_updated=updated_count,
                    execution_time_ms=matches_response.get('execution_time', 0),
                    sync_date=timezone.now()
                )
                
            except Exception as e:
                logger.error(f"Error syncing matches for {competition.name}: {str(e)}")
                total_errors += 1
                
                ApiSyncLog.objects.create(
                    endpoint=f'competitions/{competition.code}/matches',
                    http_status=500,
                    error_message=str(e),
                    sync_date=timezone.now()
                )
        
        logger.info(f"Live matches sync completed. Updated: {total_updated}, Errors: {total_errors}")
        return {"updated": total_updated, "errors": total_errors}
        
    except Exception as e:
        logger.error(f"Critical error in live matches sync: {str(e)}")
        raise self.retry(exc=e, countdown=300, max_retries=3)


@shared_task(bind=True)
def sync_all_standings(self):
    """
    Sync standings for all active competitions
    """
    logger.info("Starting daily standings sync task")
    
    try:
        api_client = FootballDataAPIClient()
        today = timezone.now().date()
        
        # Get competitions with active seasons
        active_competitions = Competition.objects.filter(
            season__start_date__lte=today,
            season__end_date__gte=today
        ).distinct()
        
        total_updated = 0
        total_created = 0
        total_errors = 0
        
        for competition in active_competitions:
            try:
                logger.info(f"Syncing standings for {competition.name}")
                
                # Get current season
                season = Season.objects.filter(
                    competition=competition,
                    start_date__lte=today,
                    end_date__gte=today
                ).first()
                
                if not season:
                    continue
                
                standings_response = api_client.get_competition_standings(
                    competition.code,
                    season=str(season.start_date.year)
                )
                
                if not standings_response or not standings_response.get('data'):
                    continue
                
                standings_data = standings_response['data']
                created_count = 0
                updated_count = 0
                
                for standing_group in standings_data.get('standings', []):
                    standing_type = standing_group.get('type', 'TOTAL')
                    group = standing_group.get('group')
                    
                    for table_entry in standing_group.get('table', []):
                        try:
                            team_id = table_entry['team']['id']
                            team = Team.objects.get(id=team_id)
                            
                            standing, created = Standing.objects.update_or_create(
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
                                    'snapshot_date': today
                                }
                            )
                            
                            if created:
                                created_count += 1
                            else:
                                updated_count += 1
                                
                        except Team.DoesNotExist:
                            logger.warning(f"Team {team_id} not found for standings")
                            continue
                        except Exception as e:
                            logger.error(f"Error updating standing for team {team_id}: {str(e)}")
                            total_errors += 1
                
                total_created += created_count
                total_updated += updated_count
                logger.info(f"Standings for {competition.name}: Created {created_count}, Updated {updated_count}")
                
                # Log sync
                ApiSyncLog.objects.create(
                    endpoint=f'competitions/{competition.code}/standings',
                    http_status=standings_response.get('status_code', 200),
                    records_processed=len([t for sg in standings_data.get('standings', []) for t in sg.get('table', [])]),
                    records_inserted=created_count,
                    records_updated=updated_count,
                    execution_time_ms=standings_response.get('execution_time', 0),
                    sync_date=timezone.now()
                )
                
            except Exception as e:
                logger.error(f"Error syncing standings for {competition.name}: {str(e)}")
                total_errors += 1
                
                ApiSyncLog.objects.create(
                    endpoint=f'competitions/{competition.code}/standings',
                    http_status=500,
                    error_message=str(e),
                    sync_date=timezone.now()
                )
        
        logger.info(f"Standings sync completed. Created: {total_created}, Updated: {total_updated}, Errors: {total_errors}")
        return {"created": total_created, "updated": total_updated, "errors": total_errors}
        
    except Exception as e:
        logger.error(f"Critical error in standings sync: {str(e)}")
        raise self.retry(exc=e, countdown=600, max_retries=3)


@shared_task(bind=True)
def sync_all_teams(self):
    """
    Weekly sync of all teams for all competitions
    """
    logger.info("Starting weekly teams sync task")
    
    try:
        api_client = FootballDataAPIClient()
        competitions = Competition.objects.all()
        
        total_updated = 0
        total_created = 0
        total_errors = 0
        
        for competition in competitions:
            try:
                logger.info(f"Syncing teams for {competition.name}")
                
                teams_response = api_client.get_competition_teams(
                    competition.code,
                    season="2024"  # Current season
                )
                
                if not teams_response or not teams_response.get('data'):
                    continue
                
                teams_data = teams_response['data']
                created_count = 0
                updated_count = 0
                
                for team_data in teams_data.get('teams', []):
                    try:
                        team, created = Team.objects.update_or_create(
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
                            created_count += 1
                        else:
                            updated_count += 1
                            
                    except Exception as e:
                        logger.error(f"Error updating team {team_data['id']}: {str(e)}")
                        total_errors += 1
                
                total_created += created_count
                total_updated += updated_count
                logger.info(f"Teams for {competition.name}: Created {created_count}, Updated {updated_count}")
                
                # Log sync
                ApiSyncLog.objects.create(
                    endpoint=f'competitions/{competition.code}/teams',
                    http_status=teams_response.get('status_code', 200),
                    records_processed=len(teams_data.get('teams', [])),
                    records_inserted=created_count,
                    records_updated=updated_count,
                    execution_time_ms=teams_response.get('execution_time', 0),
                    sync_date=timezone.now()
                )
                
            except Exception as e:
                logger.error(f"Error syncing teams for {competition.name}: {str(e)}")
                total_errors += 1
        
        logger.info(f"Teams sync completed. Created: {total_created}, Updated: {total_updated}, Errors: {total_errors}")
        return {"created": total_created, "updated": total_updated, "errors": total_errors}
        
    except Exception as e:
        logger.error(f"Critical error in teams sync: {str(e)}")
        raise self.retry(exc=e, countdown=900, max_retries=3)


@shared_task(bind=True)
def sync_full_data(self):
    """
    Monthly full data synchronization
    """
    logger.info("Starting monthly full data sync task")
    
    try:
        # Execute all sync tasks in sequence
        teams_result = sync_all_teams.delay()
        teams_result.get()  # Wait for completion
        
        standings_result = sync_all_standings.delay()
        standings_result.get()  # Wait for completion
        
        matches_result = sync_live_matches.delay()
        matches_result.get()  # Wait for completion
        
        logger.info("Monthly full sync completed successfully")
        return {"status": "completed", "message": "Full data sync successful"}
        
    except Exception as e:
        logger.error(f"Critical error in full data sync: {str(e)}")
        raise self.retry(exc=e, countdown=1800, max_retries=2)


@shared_task
def health_check():
    """
    Health check task to monitor system status
    """
    try:
        # Check database connectivity
        competition_count = Competition.objects.count()
        
        # Check API client
        api_client = FootballDataAPIClient()
        
        # Check Redis connectivity (this task running proves Redis works)
        
        logger.info(f"Health check passed. {competition_count} competitions in database.")
        
        return {
            "status": "healthy",
            "timestamp": timezone.now().isoformat(),
            "competitions": competition_count
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": timezone.now().isoformat(),
            "error": str(e)
        }


@shared_task(bind=True)
def sync_competition_data(self, competition_code, season_year="2024", sync_type="all"):
    """
    Manual task to sync specific competition data
    """
    logger.info(f"Starting manual sync for {competition_code} - {sync_type}")
    
    try:
        from django.core.management import call_command
        
        if sync_type == "all":
            # Use our existing management command
            call_command('sync_competition', competition_code, season=season_year)
        elif sync_type == "teams":
            call_command('sync_competition', competition_code, season=season_year, skip_matches=True, skip_standings=True)
        elif sync_type == "matches":
            call_command('sync_competition', competition_code, season=season_year, skip_teams=True, skip_standings=True)
        elif sync_type == "standings":
            call_command('sync_competition', competition_code, season=season_year, skip_teams=True, skip_matches=True)
        
        logger.info(f"Manual sync completed for {competition_code}")
        return {"status": "completed", "competition": competition_code, "type": sync_type}
        
    except Exception as e:
        logger.error(f"Error in manual sync for {competition_code}: {str(e)}")
        raise self.retry(exc=e, countdown=300, max_retries=2)
