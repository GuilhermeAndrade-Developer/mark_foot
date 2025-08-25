from django.core.management.base import BaseCommand
from data_management.tasks import (
    sync_live_matches, sync_all_standings, sync_all_teams,
    sync_full_data, health_check, sync_competition_data
)
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
import json


class Command(BaseCommand):
    help = 'Manage Celery tasks for data synchronization'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['run', 'schedule', 'status', 'health'],
            help='Action to perform'
        )
        parser.add_argument(
            '--task',
            choices=['live_matches', 'standings', 'teams', 'full_sync', 'health_check', 'competition'],
            help='Specific task to run/schedule'
        )
        parser.add_argument(
            '--competition',
            type=str,
            help='Competition code for manual sync'
        )
        parser.add_argument(
            '--sync-type',
            choices=['all', 'teams', 'matches', 'standings'],
            default='all',
            help='Type of sync for competition'
        )

    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'run':
            self.run_task(options)
        elif action == 'schedule':
            self.schedule_tasks()
        elif action == 'status':
            self.show_status()
        elif action == 'health':
            self.run_health_check()

    def run_task(self, options):
        """Run a specific task manually"""
        task_name = options.get('task')
        
        if not task_name:
            self.stdout.write(self.style.ERROR('❌ Please specify a task to run'))
            return
        
        self.stdout.write(f'🚀 Running task: {task_name}')
        
        try:
            if task_name == 'live_matches':
                result = sync_live_matches.delay()
                
            elif task_name == 'standings':
                result = sync_all_standings.delay()
                
            elif task_name == 'teams':
                result = sync_all_teams.delay()
                
            elif task_name == 'full_sync':
                result = sync_full_data.delay()
                
            elif task_name == 'health_check':
                result = health_check.delay()
                
            elif task_name == 'competition':
                competition = options.get('competition')
                if not competition:
                    self.stdout.write(self.style.ERROR('❌ Please specify a competition code'))
                    return
                
                sync_type = options.get('sync_type', 'all')
                result = sync_competition_data.delay(competition, sync_type=sync_type)
            
            self.stdout.write(f'✅ Task queued with ID: {result.id}')
            self.stdout.write('📊 Use "celery -A mark_foot_backend events" to monitor progress')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error running task: {str(e)}'))

    def schedule_tasks(self):
        """Set up periodic tasks for automatic synchronization"""
        self.stdout.write('📅 Setting up periodic tasks...')
        
        try:
            # Create schedules
            
            # Every 30 minutes for live matches
            schedule_30min, _ = IntervalSchedule.objects.get_or_create(
                every=30,
                period=IntervalSchedule.MINUTES,
            )
            
            # Daily at 2 AM for standings
            schedule_daily_2am, _ = CrontabSchedule.objects.get_or_create(
                minute=0,
                hour=2,
                day_of_week='*',
                day_of_month='*',
                month_of_year='*',
            )
            
            # Weekly on Sunday at 1 AM for teams
            schedule_weekly_sunday, _ = CrontabSchedule.objects.get_or_create(
                minute=0,
                hour=1,
                day_of_week=0,  # Sunday
                day_of_month='*',
                month_of_year='*',
            )
            
            # Monthly on 1st at midnight for full sync
            schedule_monthly, _ = CrontabSchedule.objects.get_or_create(
                minute=0,
                hour=0,
                day_of_week='*',
                day_of_month=1,
                month_of_year='*',
            )
            
            # Every 5 minutes for health check
            schedule_5min, _ = IntervalSchedule.objects.get_or_create(
                every=5,
                period=IntervalSchedule.MINUTES,
            )
            
            # Create periodic tasks
            tasks = [
                {
                    'name': 'Sync Live Matches',
                    'task': 'data_management.tasks.sync_live_matches',
                    'schedule': schedule_30min,
                    'description': 'Sync live and today\'s matches every 30 minutes'
                },
                {
                    'name': 'Daily Standings Sync',
                    'task': 'data_management.tasks.sync_all_standings',
                    'schedule': schedule_daily_2am,
                    'description': 'Sync all standings daily at 2 AM'
                },
                {
                    'name': 'Weekly Teams Sync',
                    'task': 'data_management.tasks.sync_all_teams',
                    'schedule': schedule_weekly_sunday,
                    'description': 'Sync all teams weekly on Sunday at 1 AM'
                },
                {
                    'name': 'Monthly Full Sync',
                    'task': 'data_management.tasks.sync_full_data',
                    'schedule': schedule_monthly,
                    'description': 'Full data synchronization monthly on 1st at midnight'
                },
                {
                    'name': 'Health Check',
                    'task': 'data_management.tasks.health_check',
                    'schedule': schedule_5min,
                    'description': 'System health check every 5 minutes'
                }
            ]
            
            created_count = 0
            updated_count = 0
            
            for task_config in tasks:
                task, created = PeriodicTask.objects.get_or_create(
                    name=task_config['name'],
                    defaults={
                        'task': task_config['task'],
                        'interval': task_config['schedule'] if isinstance(task_config['schedule'], IntervalSchedule) else None,
                        'crontab': task_config['schedule'] if isinstance(task_config['schedule'], CrontabSchedule) else None,
                        'enabled': True,
                        'description': task_config['description']
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f'  ✅ Created: {task_config["name"]}')
                else:
                    updated_count += 1
                    self.stdout.write(f'  🔄 Updated: {task_config["name"]}')
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n📅 Periodic tasks setup completed!\n'
                    f'   Created: {created_count}\n'
                    f'   Updated: {updated_count}'
                )
            )
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error setting up periodic tasks: {str(e)}'))

    def show_status(self):
        """Show status of scheduled tasks"""
        self.stdout.write('📊 Celery Tasks Status')
        self.stdout.write('=' * 50)
        
        try:
            tasks = PeriodicTask.objects.all()
            
            if not tasks:
                self.stdout.write('📭 No periodic tasks configured')
                return
            
            for task in tasks:
                status = '✅ Enabled' if task.enabled else '❌ Disabled'
                
                if task.interval:
                    schedule = f'Every {task.interval.every} {task.interval.period}'
                elif task.crontab:
                    schedule = f'Cron: {task.crontab.minute} {task.crontab.hour} * * {task.crontab.day_of_week}'
                else:
                    schedule = 'No schedule'
                
                self.stdout.write(f'\n📋 {task.name}')
                self.stdout.write(f'   Status: {status}')
                self.stdout.write(f'   Task: {task.task}')
                self.stdout.write(f'   Schedule: {schedule}')
                if task.description:
                    self.stdout.write(f'   Description: {task.description}')
                if task.last_run_at:
                    self.stdout.write(f'   Last Run: {task.last_run_at}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error getting task status: {str(e)}'))

    def run_health_check(self):
        """Run immediate health check"""
        self.stdout.write('🏥 Running health check...')
        
        try:
            result = health_check.delay()
            health_data = result.get(timeout=30)  # Wait up to 30 seconds
            
            if health_data['status'] == 'healthy':
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ System is healthy!\n'
                        f'   Timestamp: {health_data["timestamp"]}\n'
                        f'   Competitions: {health_data["competitions"]}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ System is unhealthy!\n'
                        f'   Timestamp: {health_data["timestamp"]}\n'
                        f'   Error: {health_data.get("error", "Unknown")}'
                    )
                )
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Health check failed: {str(e)}'))
