from celery import shared_task
from django.utils import timezone
from datetime import datetime, timedelta
from .services.live_data_service import LiveDataService, LiveOddsService
from .models import LiveMatch, MatchAlert, Match
from whatsapp_integration.services import WhatsAppService
from whatsapp_integration.models import WhatsAppUser
from ai_analytics.services import MatchPredictionService
import logging

logger = logging.getLogger(__name__)


@shared_task
def monitor_live_matches():
    """Monitor all active live matches"""
    try:
        live_service = LiveDataService()
        live_service.monitor_live_matches()
        logger.info("Live matches monitoring completed")
    except Exception as e:
        logger.error(f"Error in monitor_live_matches task: {str(e)}")


@shared_task
def monitor_live_odds():
    """Monitor live odds for active matches"""
    try:
        odds_service = LiveOddsService()
        
        # Get active live matches
        live_matches = LiveMatch.objects.filter(
            is_active=True,
            status__in=['FIRST_HALF', 'SECOND_HALF', 'EXTRA_TIME_FIRST', 'EXTRA_TIME_SECOND']
        )
        
        for live_match in live_matches:
            try:
                odds_service.update_live_odds(live_match)
            except Exception as e:
                logger.error(f"Error updating odds for match {live_match.id}: {str(e)}")
                
        logger.info(f"Live odds monitoring completed for {live_matches.count()} matches")
        
    except Exception as e:
        logger.error(f"Error in monitor_live_odds task: {str(e)}")


@shared_task
def process_match_alerts():
    """Process and send match alerts to users"""
    try:
        whatsapp_service = WhatsAppService()
        
        # Get unsent alerts that are ready to send
        alerts = MatchAlert.objects.filter(
            is_sent=False,
            send_after__lte=timezone.now()
        ).order_by('priority', 'created_at')[:50]  # Limit to avoid overload
        
        for alert in alerts:
            try:
                send_match_alert.delay(alert.id)
            except Exception as e:
                logger.error(f"Error queuing alert {alert.id}: {str(e)}")
                
        logger.info(f"Queued {alerts.count()} alerts for processing")
        
    except Exception as e:
        logger.error(f"Error in process_match_alerts task: {str(e)}")


@shared_task
def send_match_alert(alert_id):
    """Send individual match alert to WhatsApp users"""
    try:
        alert = MatchAlert.objects.get(id=alert_id)
        whatsapp_service = WhatsAppService()
        
        # Get target users based on subscription levels
        target_users = WhatsAppUser.objects.filter(
            subscription_status__in=alert.target_subscription_levels
        )
        
        # Filter by team preferences if specified
        if alert.target_teams.exists():
            # This would need user preferences implementation
            pass
        
        sent_count = 0
        for user in target_users:
            try:
                # Check if user has daily query limit available
                if user.can_make_query():
                    message_sent = whatsapp_service.send_alert_message(user.phone_number, alert)
                    if message_sent:
                        sent_count += 1
                        user.increment_query_count()
                        
            except Exception as e:
                logger.error(f"Error sending alert to user {user.phone_number}: {str(e)}")
        
        # Update alert status
        alert.sent_count = sent_count
        alert.is_sent = True
        alert.sent_at = timezone.now()
        alert.save()
        
        logger.info(f"Alert {alert_id} sent to {sent_count} users")
        
    except MatchAlert.DoesNotExist:
        logger.error(f"Alert {alert_id} not found")
    except Exception as e:
        logger.error(f"Error sending alert {alert_id}: {str(e)}")


@shared_task
def start_match_monitoring():
    """Start monitoring for matches about to begin"""
    try:
        live_service = LiveDataService()
        
        # Get matches starting in the next 15 minutes
        now = timezone.now()
        start_window = now + timedelta(minutes=15)
        
        upcoming_matches = Match.objects.filter(
            utc_date__gte=now,
            utc_date__lte=start_window,
            status='SCHEDULED'
        ).exclude(
            live_data__isnull=False  # Don't re-monitor
        )
        
        for match in upcoming_matches:
            try:
                live_service.start_match_monitoring(match)
                logger.info(f"Started monitoring for match {match.id}")
            except Exception as e:
                logger.error(f"Error starting monitoring for match {match.id}: {str(e)}")
                
        logger.info(f"Started monitoring for {upcoming_matches.count()} upcoming matches")
        
    except Exception as e:
        logger.error(f"Error in start_match_monitoring task: {str(e)}")


@shared_task
def send_daily_match_preview():
    """Send daily match preview to premium users"""
    try:
        whatsapp_service = WhatsAppService()
        prediction_service = MatchPredictionService()
        
        # Get today's matches
        today = timezone.now().date()
        today_matches = Match.objects.filter(
            utc_date__date=today,
            status='SCHEDULED'
        ).order_by('utc_date')[:10]  # Limit to 10 matches
        
        if not today_matches.exists():
            logger.info("No matches today for preview")
            return
        
        # Generate preview message
        preview_text = "🏆 *Prévia do Dia - Mark Foot*\n\n"
        
        for match in today_matches:
            # Get AI prediction
            prediction = prediction_service.get_latest_prediction(match)
            
            if prediction:
                home_prob = prediction.features_used.get('home_win_probability', 0.33) * 100
                draw_prob = prediction.features_used.get('draw_probability', 0.33) * 100
                away_prob = prediction.features_used.get('away_win_probability', 0.33) * 100
            else:
                home_prob = draw_prob = away_prob = 33.3
            
            preview_text += f"""🏠 {match.home_team.name} vs {match.away_team.name}
⏰ {match.utc_date.strftime('%H:%M')}

🤖 IA Previsão:
🏠 {home_prob:.1f}% | 🤝 {draw_prob:.1f}% | ✈️ {away_prob:.1f}%

---
"""
        
        preview_text += "\n💎 Premium: Alertas automáticos quando jogos começarem!"
        
        # Send to premium users
        premium_users = WhatsAppUser.objects.filter(
            subscription_status__in=['premium', 'pro', 'trial']
        )
        
        sent_count = 0
        for user in premium_users:
            try:
                if user.can_make_query():
                    message_sent = whatsapp_service.send_message(user.phone_number, preview_text)
                    if message_sent:
                        sent_count += 1
                        user.increment_query_count()
            except Exception as e:
                logger.error(f"Error sending preview to user {user.phone_number}: {str(e)}")
        
        logger.info(f"Daily preview sent to {sent_count} premium users")
        
    except Exception as e:
        logger.error(f"Error in send_daily_match_preview task: {str(e)}")


@shared_task
def update_live_predictions():
    """Update AI predictions for live matches"""
    try:
        prediction_service = MatchPredictionService()
        
        # Get active live matches
        live_matches = LiveMatch.objects.filter(
            is_active=True,
            status__in=['FIRST_HALF', 'SECOND_HALF']
        )
        
        for live_match in live_matches:
            try:
                # Update predictions every 10 minutes during live matches
                if live_match.minute % 10 == 0:
                    prediction_service.update_live_predictions(live_match)
            except Exception as e:
                logger.error(f"Error updating predictions for match {live_match.id}: {str(e)}")
        
        logger.info(f"Updated predictions for {live_matches.count()} live matches")
        
    except Exception as e:
        logger.error(f"Error in update_live_predictions task: {str(e)}")


@shared_task
def cleanup_old_alerts():
    """Clean up old alerts and live data"""
    try:
        # Delete old alerts (older than 7 days)
        cutoff_date = timezone.now() - timedelta(days=7)
        
        old_alerts = MatchAlert.objects.filter(created_at__lt=cutoff_date)
        deleted_count = old_alerts.count()
        old_alerts.delete()
        
        # Clean up old live odds snapshots (older than 3 days)
        odds_cutoff = timezone.now() - timedelta(days=3)
        old_odds = LiveOddsSnapshot.objects.filter(timestamp__lt=odds_cutoff)
        odds_deleted = old_odds.count()
        old_odds.delete()
        
        # Deactivate finished live matches
        finished_matches = LiveMatch.objects.filter(
            status__in=['FULL_TIME', 'ABANDONED'],
            is_active=True
        )
        finished_count = finished_matches.count()
        finished_matches.update(is_active=False)
        
        logger.info(f"Cleanup completed - Alerts: {deleted_count}, Odds: {odds_deleted}, Deactivated: {finished_count}")
        
    except Exception as e:
        logger.error(f"Error in cleanup_old_alerts task: {str(e)}")


def should_send_alert(user, alert):
    """Check if user should receive this alert based on preferences"""
    # This would implement user alert preferences
    # For now, basic subscription level check
    alert_preferences = {
        'MATCH_START': True,
        'GOAL': True,
        'RED_CARD': True,
        'PENALTY': True,
        'HALF_TIME': False,  # Only for Pro users
        'FULL_TIME': True,
        'ODDS_MOVEMENT': True,  # Only for Pro users
        'VALUE_BET': True,  # Only for Pro users
        'SCORE_PREDICTION': False,  # Only for Pro users
    }
    
    # Basic filtering based on subscription
    if alert.alert_type in ['HALF_TIME', 'SCORE_PREDICTION'] and user.subscription_status not in ['pro']:
        return False
    
    if alert.alert_type in ['ODDS_MOVEMENT', 'VALUE_BET'] and user.subscription_status not in ['premium', 'pro']:
        return False
    
    return alert_preferences.get(alert.alert_type, True)
