from celery import shared_task
import logging
from django.utils import timezone
from datetime import timedelta
from .services.odds_collectors import OddsCollectionService
from .services.odds_analyzer import OddsAnalysisService
from .models import MarketAlert, OddsAnalysis
from core.models import Match

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def collect_upcoming_match_odds(self):
    """Collect odds for upcoming matches"""
    try:
        logger.info("Starting odds collection task")
        service = OddsCollectionService()
        collected_count = service.collect_odds_for_upcoming_matches(days_ahead=7)
        
        logger.info(f"Odds collection completed. Collected odds for {collected_count} matches")
        return {
            'status': 'success',
            'collected_count': collected_count,
            'message': f'Successfully collected odds for {collected_count} matches'
        }
        
    except Exception as e:
        logger.error(f"Error in odds collection task: {str(e)}")
        # Retry with exponential backoff
        raise self.retry(countdown=60 * (2 ** self.request.retries), exc=e)

@shared_task(bind=True, max_retries=3)
def analyze_match_odds(self, match_id):
    """Analyze odds for a specific match"""
    try:
        logger.info(f"Starting odds analysis for match {match_id}")
        
        match = Match.objects.get(id=match_id)
        analyzer = OddsAnalysisService()
        analysis = analyzer.analyze_match_odds(match)
        
        if analysis:
            logger.info(f"Odds analysis completed for match {match}")
            return {
                'status': 'success',
                'match_id': match_id,
                'value_bet_detected': analysis.value_bet_detected,
                'confidence_score': analysis.confidence_score
            }
        else:
            logger.warning(f"No analysis could be generated for match {match}")
            return {
                'status': 'warning',
                'match_id': match_id,
                'message': 'No analysis could be generated'
            }
            
    except Match.DoesNotExist:
        logger.error(f"Match {match_id} not found")
        return {
            'status': 'error',
            'match_id': match_id,
            'message': 'Match not found'
        }
    except Exception as e:
        logger.error(f"Error in odds analysis task for match {match_id}: {str(e)}")
        raise self.retry(countdown=60 * (2 ** self.request.retries), exc=e)

@shared_task
def update_all_odds_analysis():
    """Update odds analysis for all upcoming matches with odds data"""
    try:
        logger.info("Starting bulk odds analysis update")
        
        analyzer = OddsAnalysisService()
        analyzed_count = analyzer.analyze_all_upcoming_matches()
        
        logger.info(f"Bulk odds analysis completed. Analyzed {analyzed_count} matches")
        return {
            'status': 'success',
            'analyzed_count': analyzed_count,
            'message': f'Successfully analyzed {analyzed_count} matches'
        }
        
    except Exception as e:
        logger.error(f"Error in bulk odds analysis task: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }

@shared_task
def cleanup_old_odds_data():
    """Clean up old odds data and alerts"""
    try:
        logger.info("Starting odds data cleanup")
        
        # Remove odds data older than 30 days
        cutoff_date = timezone.now() - timedelta(days=30)
        
        from .models import MatchOdds, OddsMovement
        
        # Delete old odds movements
        old_movements = OddsMovement.objects.filter(timestamp__lt=cutoff_date)
        movements_count = old_movements.count()
        old_movements.delete()
        
        # Delete old match odds for finished matches
        old_odds = MatchOdds.objects.filter(
            match__match_date__lt=cutoff_date,
            match__status='finished'
        )
        odds_count = old_odds.count()
        old_odds.delete()
        
        # Deactivate old market alerts
        old_alerts = MarketAlert.objects.filter(
            created_at__lt=cutoff_date,
            is_active=True
        )
        alerts_count = old_alerts.count()
        old_alerts.update(is_active=False)
        
        logger.info(f"Cleanup completed: {movements_count} movements, {odds_count} odds records, {alerts_count} alerts")
        
        return {
            'status': 'success',
            'movements_deleted': movements_count,
            'odds_deleted': odds_count,
            'alerts_deactivated': alerts_count
        }
        
    except Exception as e:
        logger.error(f"Error in cleanup task: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }

@shared_task
def collect_odds_for_specific_match(match_id):
    """Collect odds for a specific match"""
    try:
        logger.info(f"Collecting odds for specific match {match_id}")
        
        match = Match.objects.get(id=match_id)
        service = OddsCollectionService()
        results = service.collect_odds_for_match(match)
        
        if results:
            # Trigger analysis after collection
            analyze_match_odds.delay(match_id)
            
            logger.info(f"Odds collection completed for match {match}")
            return {
                'status': 'success',
                'match_id': match_id,
                'odds_collected': len(results)
            }
        else:
            logger.warning(f"No odds collected for match {match}")
            return {
                'status': 'warning',
                'match_id': match_id,
                'message': 'No odds could be collected'
            }
            
    except Match.DoesNotExist:
        logger.error(f"Match {match_id} not found")
        return {
            'status': 'error',
            'match_id': match_id,
            'message': 'Match not found'
        }
    except Exception as e:
        logger.error(f"Error collecting odds for match {match_id}: {str(e)}")
        return {
            'status': 'error',
            'match_id': match_id,
            'message': str(e)
        }

@shared_task
def check_value_bet_alerts():
    """Check for new value betting opportunities and send alerts"""
    try:
        logger.info("Checking for value bet alerts")
        
        # Get recent analyses with value bets
        recent_value_bets = OddsAnalysis.objects.filter(
            value_bet_detected=True,
            updated_at__gte=timezone.now() - timedelta(hours=1),
            match__match_date__gte=timezone.now()
        ).select_related('match', 'match__home_team', 'match__away_team')
        
        alerts_created = 0
        for analysis in recent_value_bets:
            # Create alert if doesn't exist
            alert, created = MarketAlert.objects.get_or_create(
                match=analysis.match,
                alert_type='value_bet',
                market_type=analysis.value_bet_market or 'unknown',
                defaults={
                    'description': f"Value bet detectado: {analysis.value_bet_market} com confiança {analysis.confidence_score}",
                    'is_active': True
                }
            )
            
            if created:
                alerts_created += 1
        
        logger.info(f"Value bet check completed. Created {alerts_created} new alerts")
        return {
            'status': 'success',
            'alerts_created': alerts_created
        }
        
    except Exception as e:
        logger.error(f"Error in value bet alerts task: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }
