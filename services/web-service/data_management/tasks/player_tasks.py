from celery import shared_task
from django.utils import timezone
from django.conf import settings
import logging

from data_management.collectors.player_collector import PlayerDataCollector
from core.models import ApiSyncLog, Team

logger = logging.getLogger('mark_foot')


@shared_task(bind=True, name='sync_player_data')
def sync_player_data(self, search_terms=None, team_names=None, api_key=None):
    """
    Celery task to synchronize player data from TheSportsDB API
    
    Args:
        search_terms (list): List of player names to search for
        team_names (list): List of team names to collect players for
        api_key (str): Optional API key for premium features
    """
    start_time = timezone.now()
    
    # Initialize sync log
    sync_log = ApiSyncLog.objects.create(
        task_name='sync_player_data',
        task_id=self.request.id,
        source='thesportsdb',
        status='running',
        started_at=start_time
    )
    
    try:
        # Initialize collector
        collector = PlayerDataCollector(api_key=api_key)
        
        total_stats = {
            'processed': 0,
            'created': 0,
            'updated': 0,
            'failed': 0,
            'skipped': 0
        }
        
        # Test API connection
        if not collector.test_api_connection():
            raise Exception("Failed to connect to TheSportsDB API")
        
        logger.info("🏆 Starting player data synchronization")
        
        # Sync by search terms
        if search_terms:
            logger.info(f"🔍 Syncing players by search terms: {search_terms}")
            
            for search_term in search_terms:
                try:
                    stats = collector.collect_players_by_search(search_term)
                    
                    # Aggregate stats
                    for key in total_stats:
                        total_stats[key] += stats.get(key, 0)
                    
                    logger.info(f"✅ Search '{search_term}' completed: {stats}")
                    
                except Exception as e:
                    logger.error(f"❌ Error searching for '{search_term}': {str(e)}")
                    total_stats['failed'] += 1
        
        # Sync by team names
        if team_names:
            logger.info(f"🏆 Syncing players by team names: {team_names}")
            
            for team_name in team_names:
                try:
                    stats = collector.collect_team_players(team_name)
                    
                    # Aggregate stats
                    for key in total_stats:
                        total_stats[key] += stats.get(key, 0)
                    
                    logger.info(f"✅ Team '{team_name}' completed: {stats}")
                    
                except Exception as e:
                    logger.error(f"❌ Error collecting team '{team_name}': {str(e)}")
                    total_stats['failed'] += 1
        
        # If no specific terms/teams provided, sync for existing teams
        if not search_terms and not team_names:
            logger.info("🏆 Syncing players for all existing teams")
            
            try:
                stats = collector.collect_players_for_existing_teams()
                
                # Use team stats as total stats
                total_stats = stats
                
                logger.info(f"✅ All teams sync completed: {stats}")
                
            except Exception as e:
                logger.error(f"❌ Error syncing all teams: {str(e)}")
                total_stats['failed'] += 1
        
        # Update sync log
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        sync_log.status = 'completed'
        sync_log.completed_at = end_time
        sync_log.duration_seconds = duration
        sync_log.records_processed = total_stats['processed']
        sync_log.records_created = total_stats['created']
        sync_log.records_updated = total_stats['updated']
        sync_log.records_failed = total_stats['failed']
        sync_log.response_data = {
            'stats': total_stats,
            'search_terms': search_terms,
            'team_names': team_names,
            'api_key_used': bool(api_key)
        }
        sync_log.save()
        
        success_rate = 0
        if total_stats['processed'] > 0:
            success_rate = ((total_stats['created'] + total_stats['updated']) / total_stats['processed']) * 100
        
        logger.info(
            f"🎯 Player sync completed! "
            f"Duration: {duration:.1f}s, "
            f"Processed: {total_stats['processed']}, "
            f"Created: {total_stats['created']}, "
            f"Updated: {total_stats['updated']}, "
            f"Failed: {total_stats['failed']}, "
            f"Success Rate: {success_rate:.1f}%"
        )
        
        return {
            'status': 'success',
            'duration': duration,
            'stats': total_stats,
            'success_rate': success_rate
        }
        
    except Exception as e:
        # Update sync log with error
        sync_log.status = 'failed'
        sync_log.completed_at = timezone.now()
        sync_log.duration_seconds = (timezone.now() - start_time).total_seconds()
        sync_log.error_message = str(e)
        sync_log.save()
        
        logger.error(f"❌ Player sync failed: {str(e)}")
        
        # Re-raise the exception so Celery marks the task as failed
        raise


@shared_task(bind=True, name='sync_specific_players')
def sync_specific_players(self, player_names, api_key=None):
    """
    Celery task to sync specific players by name
    
    Args:
        player_names (list): List of specific player names to search for
        api_key (str): Optional API key for premium features
    """
    logger.info(f"🔍 Starting specific player sync for: {player_names}")
    
    return sync_player_data.apply_async(
        args=[player_names, None, api_key]
    )


@shared_task(bind=True, name='sync_team_players')
def sync_team_players(self, team_names=None, api_key=None):
    """
    Celery task to sync players for specific teams
    
    Args:
        team_names (list): List of team names to collect players for.
                          If None, syncs for all teams in database
        api_key (str): Optional API key for premium features
    """
    logger.info(f"🏆 Starting team players sync for: {team_names or 'all teams'}")
    
    return sync_player_data.apply_async(
        args=[None, team_names, api_key]
    )


@shared_task(bind=True, name='sync_popular_players')
def sync_popular_players(self, api_key=None):
    """
    Celery task to sync popular/famous players
    
    Args:
        api_key (str): Optional API key for premium features
    """
    # Get popular players from seeded data instead of hardcoded list
    from core.models import Player
    popular_players_qs = Player.objects.filter(
        is_active=True,
        market_value__gte=10000000  # Players with market value >= 10M
    ).order_by('-market_value')[:15]
    
    # Use seeded data or create warning if no data exists
    if popular_players_qs.exists():
        popular_players = [player.name for player in popular_players_qs]
    else:
        logger.warning("⚠️  No players found! Please run seeders: python manage.py seed_dev_data")
        return {
            'status': 'warning',
            'message': 'No players found in database. Please run seeders first.',
            'players_synced': 0
        }
    
    logger.info(f"⭐ Starting popular players sync: {len(popular_players)} players")
    
    return sync_player_data.apply_async(
        args=[popular_players, None, api_key]
    )


@shared_task(bind=True, name='cleanup_player_data')
def cleanup_player_data(self, days_old=30):
    """
    Celery task to cleanup old player data
    
    Args:
        days_old (int): Remove players not synced in this many days
    """
    from datetime import timedelta
    from core.models import Player
    
    start_time = timezone.now()
    cutoff_date = start_time - timedelta(days=days_old)
    
    logger.info(f"🧹 Starting player data cleanup (older than {days_old} days)")
    
    # Find old players
    old_players = Player.objects.filter(
        last_sync__lt=cutoff_date
    )
    
    count = old_players.count()
    
    if count > 0:
        # Delete old players
        old_players.delete()
        logger.info(f"🗑️ Deleted {count} old player records")
    else:
        logger.info("✅ No old player records to cleanup")
    
    duration = (timezone.now() - start_time).total_seconds()
    
    return {
        'status': 'success',
        'duration': duration,
        'deleted_count': count,
        'cutoff_date': cutoff_date.isoformat()
    }
