import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mark_foot_backend.settings')

app = Celery('mark_foot_backend')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Explicitly include tasks
app.autodiscover_tasks(['data_management'])

# Celery Beat configuration
app.conf.beat_schedule = {
    # ============ LIVE MATCH MONITORING ============
    # Monitor live matches every 2 minutes during match times
    'monitor-live-matches': {
        'task': 'core.tasks.monitor_live_matches',
        'schedule': 2.0 * 60,  # 2 minutes
    },
    # Monitor live odds every 3 minutes
    'monitor-live-odds': {
        'task': 'core.tasks.monitor_live_odds',
        'schedule': 3.0 * 60,  # 3 minutes
    },
    # Process match alerts every minute
    'process-match-alerts': {
        'task': 'core.tasks.process_match_alerts',
        'schedule': 60.0,  # 1 minute
    },
    # Start monitoring for matches beginning soon every 5 minutes
    'start-match-monitoring': {
        'task': 'core.tasks.start_match_monitoring',
        'schedule': 5.0 * 60,  # 5 minutes
    },
    # Send daily match previews at 8 AM
    'send-daily-match-preview': {
        'task': 'core.tasks.send_daily_match_preview',
        'schedule': crontab(minute=0, hour=8),
    },
    # Update live predictions every 5 minutes
    'update-live-predictions': {
        'task': 'core.tasks.update_live_predictions',
        'schedule': 5.0 * 60,  # 5 minutes
    },
    # Cleanup old alerts and data daily at 4 AM
    'cleanup-old-alerts': {
        'task': 'core.tasks.cleanup_old_alerts',
        'schedule': crontab(minute=0, hour=4),
    },
    
    # ============ EXISTING DATA SYNC TASKS ============
    # Sync matches every 30 minutes during match days
    'sync-live-matches': {
        'task': 'data_management.tasks.sync_live_matches',
        'schedule': 30.0 * 60,  # 30 minutes
    },
    # Sync standings daily at 2 AM
    'sync-daily-standings': {
        'task': 'data_management.tasks.sync_all_standings',
        'schedule': crontab(minute=0, hour=2),
    },
    # Sync teams weekly on Sunday at 1 AM
    'sync-weekly-teams': {
        'task': 'data_management.tasks.sync_all_teams',
        'schedule': crontab(minute=0, hour=1, day_of_week=0),
    },
    # Full sync monthly on 1st day at midnight
    'sync-monthly-full': {
        'task': 'data_management.tasks.sync_full_data',
        'schedule': crontab(minute=0, hour=0, day_of_month=1),
    },
    # Health check every 5 minutes
    'health-check': {
        'task': 'data_management.tasks.health_check',
        'schedule': 5.0 * 60,  # 5 minutes
    },
    # ============ PLAYER DATA TASKS ============
    # Sync popular players daily at 3 AM
    'sync-daily-popular-players': {
        'task': 'sync_popular_players',
        'schedule': crontab(minute=0, hour=3),
    },
    # Sync team players weekly on Monday at 4 AM
    'sync-weekly-team-players': {
        'task': 'sync_team_players',
        'schedule': crontab(minute=0, hour=4, day_of_week=1),
    },
    # Cleanup old player data monthly on 15th at 3 AM
    'cleanup-monthly-player-data': {
        'task': 'cleanup_player_data',
        'schedule': crontab(minute=0, hour=3, day_of_month=15),
        'kwargs': {'days_old': 60}  # Remove players not synced in 60 days
    },
    # ============ WHATSAPP SUBSCRIPTION TASKS ============
    # Check expiring subscriptions daily at 9 AM
    'check-expiring-subscriptions': {
        'task': 'whatsapp_integration.tasks.check_expiring_subscriptions',
        'schedule': crontab(minute=0, hour=9),
    },
    # Check expired subscriptions daily at 10 AM
    'check-expired-subscriptions': {
        'task': 'whatsapp_integration.tasks.check_expired_subscriptions',
        'schedule': crontab(minute=0, hour=10),
    },
    # Check trial endings daily at 8 AM
    'check-trial-endings': {
        'task': 'whatsapp_integration.tasks.check_trial_endings',
        'schedule': crontab(minute=0, hour=8),
    },
    # Reset daily query counts at midnight
    'reset-daily-query-counts': {
        'task': 'whatsapp_integration.tasks.reset_daily_query_counts',
        'schedule': crontab(minute=0, hour=0),
    },
    # Cleanup expired payment intents every 6 hours
    'cleanup-expired-payment-intents': {
        'task': 'whatsapp_integration.tasks.cleanup_expired_payment_intents',
        'schedule': crontab(minute=0, hour='*/6'),
    },
}

# Timezone configuration
app.conf.timezone = 'UTC'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
