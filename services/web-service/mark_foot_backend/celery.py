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
}

# Timezone configuration
app.conf.timezone = 'UTC'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
