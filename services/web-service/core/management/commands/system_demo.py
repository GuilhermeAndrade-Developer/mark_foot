from django.core.management.base import BaseCommand
from data_management.tasks import (
    sync_live_matches, sync_all_standings, sync_all_teams,
    health_check, sync_competition_data
)
from core.models import Competition, Team, Match, Standing, ApiSyncLog
from django_celery_beat.models import PeriodicTask
from django.utils import timezone


class Command(BaseCommand):
    help = 'Demonstrate the complete automated system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            choices=['demo', 'status', 'queue-tasks'],
            default='demo',
            help='Action to perform'
        )

    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'demo':
            self.run_demo()
        elif action == 'status':
            self.show_system_status()
        elif action == 'queue-tasks':
            self.queue_demo_tasks()

    def run_demo(self):
        """Run complete system demonstration"""
        self.stdout.write(
            self.style.SUCCESS('🚀 Mark Foot - Automated Football Data System Demo')
        )
        self.stdout.write('=' * 70)
        
        # 1. System Status
        self.show_system_status()
        
        # 2. Queue some tasks
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write('🔄 Queuing demonstration tasks...')
        self.queue_demo_tasks()
        
        # 3. Show what's scheduled
        self.show_scheduled_tasks()

    def show_system_status(self):
        """Show current system status"""
        self.stdout.write('\n📊 Current System Status:')
        self.stdout.write('-' * 40)
        
        # Database stats
        stats = {
            'Competitions': Competition.objects.count(),
            'Teams': Team.objects.count(),
            'Matches': Match.objects.count(),
            'Standings': Standing.objects.count(),
            'API Logs': ApiSyncLog.objects.count()
        }
        
        for key, value in stats.items():
            self.stdout.write(f'  📈 {key}: {value}')
        
        # Active competitions
        active_comps = Competition.objects.filter(
            season__start_date__lte=timezone.now().date(),
            season__end_date__gte=timezone.now().date()
        ).distinct()
        
        self.stdout.write(f'\n🏆 Active Competitions ({active_comps.count()}):')
        for comp in active_comps:
            teams_count = Match.objects.filter(competition=comp).values('home_team', 'away_team').distinct().count()
            matches_count = Match.objects.filter(competition=comp).count()
            self.stdout.write(f'  • {comp.name}: {teams_count} teams, {matches_count} matches')

    def queue_demo_tasks(self):
        """Queue demonstration tasks"""
        tasks_queued = []
        
        try:
            # Health check
            result = health_check.delay()
            tasks_queued.append(('Health Check', result.id))
            
            # Sync matches for active competitions
            result = sync_live_matches.delay()
            tasks_queued.append(('Live Matches Sync', result.id))
            
            # Sync specific competition
            result = sync_competition_data.delay('PL', sync_type='standings')
            tasks_queued.append(('PL Standings Sync', result.id))
            
            self.stdout.write('\n✅ Tasks queued successfully:')
            for task_name, task_id in tasks_queued:
                self.stdout.write(f'  📋 {task_name}: {task_id}')
            
            self.stdout.write(f'\n📊 Monitor with: docker logs mark_foot_celery_worker_dev -f')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error queuing tasks: {str(e)}'))

    def show_scheduled_tasks(self):
        """Show scheduled periodic tasks"""
        self.stdout.write('\n📅 Scheduled Periodic Tasks:')
        self.stdout.write('-' * 40)
        
        tasks = PeriodicTask.objects.filter(enabled=True)
        
        if not tasks:
            self.stdout.write('  📭 No periodic tasks configured')
            return
        
        for task in tasks:
            if task.interval:
                schedule = f'Every {task.interval.every} {task.interval.period}'
            elif task.crontab:
                schedule = f'{task.crontab.minute} {task.crontab.hour} * * {task.crontab.day_of_week}'
            else:
                schedule = 'Custom schedule'
            
            status = '🟢' if task.enabled else '🔴'
            self.stdout.write(f'  {status} {task.name}')
            self.stdout.write(f'      Schedule: {schedule}')
            if task.last_run_at:
                self.stdout.write(f'      Last run: {task.last_run_at.strftime("%Y-%m-%d %H:%M:%S")}')
            else:
                self.stdout.write('      Last run: Never')

    def epilogue(self):
        """Show system capabilities"""
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write('🎯 System Capabilities:')
        self.stdout.write('-' * 30)
        
        capabilities = [
            '✅ Automated data collection from Football-Data.org API',
            '✅ Rate limiting (10 calls/minute) with intelligent queuing',
            '✅ 12 major competitions supported (Premier League, Bundesliga, etc.)',
            '✅ Real-time match updates every 30 minutes',
            '✅ Daily standings synchronization at 2 AM',
            '✅ Weekly teams refresh on Sundays',
            '✅ Monthly full data sync on 1st of each month',
            '✅ System health monitoring every 5 minutes',
            '✅ Comprehensive API call logging and auditing',
            '✅ Django Admin interface for data management',
            '✅ Manual synchronization commands available',
            '✅ Dockerized microservices architecture',
            '✅ Redis-backed task queue with Celery',
            '✅ MySQL database with optimized indexes',
            '✅ Error handling and automatic retries'
        ]
        
        for capability in capabilities:
            self.stdout.write(f'  {capability}')
        
        self.stdout.write('\n🚀 Ready for production deployment!')
        self.stdout.write('📚 Access admin at: http://localhost:8001/admin/')
        self.stdout.write('📊 API ready for expansion to REST endpoints')
        
        self.stdout.write('\n' + '=' * 70)
