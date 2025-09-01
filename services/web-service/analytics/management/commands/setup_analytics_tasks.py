from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, CrontabSchedule, IntervalSchedule
import json


class Command(BaseCommand):
    help = 'Setup Analytics Celery Beat tasks for automated reports'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up Analytics Celery Beat tasks...'))

        # Weekly reports (every Sunday at 9 AM)
        weekly_schedule, created = CrontabSchedule.objects.get_or_create(
            minute=0,
            hour=9,
            day_of_week=0,  # Sunday
            day_of_month='*',
            month_of_year='*',
        )

        weekly_task, created = PeriodicTask.objects.get_or_create(
            name='Send Weekly Analytics Reports',
            defaults={
                'crontab': weekly_schedule,
                'task': 'analytics.tasks.send_weekly_reports',
                'enabled': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✅ Created weekly reports task'))
        else:
            self.stdout.write(self.style.WARNING('⚠️ Weekly reports task already exists'))

        # Monthly reports (first day of month at 10 AM)
        monthly_schedule, created = CrontabSchedule.objects.get_or_create(
            minute=0,
            hour=10,
            day_of_week='*',
            day_of_month=1,
            month_of_year='*',
        )

        monthly_task, created = PeriodicTask.objects.get_or_create(
            name='Send Monthly Analytics Reports',
            defaults={
                'crontab': monthly_schedule,
                'task': 'analytics.tasks.send_monthly_reports',
                'enabled': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✅ Created monthly reports task'))
        else:
            self.stdout.write(self.style.WARNING('⚠️ Monthly reports task already exists'))

        # Cleanup old reports (every day at 2 AM)
        cleanup_schedule, created = CrontabSchedule.objects.get_or_create(
            minute=0,
            hour=2,
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
        )

        cleanup_task, created = PeriodicTask.objects.get_or_create(
            name='Cleanup Old Analytics Reports',
            defaults={
                'crontab': cleanup_schedule,
                'task': 'analytics.tasks.cleanup_old_reports',
                'enabled': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✅ Created cleanup task'))
        else:
            self.stdout.write(self.style.WARNING('⚠️ Cleanup task already exists'))

        # Analytics summary update (every 6 hours)
        summary_schedule, created = IntervalSchedule.objects.get_or_create(
            every=6,
            period=IntervalSchedule.HOURS,
        )

        # Create multiple dashboard update tasks for all users
        from django.contrib.auth.models import User
        users = User.objects.all()
        
        for user in users:
            task_name = f'Update Analytics Summary for {user.username}'
            summary_task, created = PeriodicTask.objects.get_or_create(
                name=task_name,
                defaults={
                    'interval': summary_schedule,
                    'task': 'analytics.tasks.generate_analytics_summary',
                    'args': json.dumps([user.id]),
                    'enabled': True,
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Created analytics summary task for {user.username}'))

        self.stdout.write(self.style.SUCCESS('🎉 Analytics Celery Beat tasks setup completed!'))
        self.stdout.write('')
        self.stdout.write('Scheduled tasks:')
        self.stdout.write('📅 Weekly reports: Every Sunday at 9:00 AM')
        self.stdout.write('📅 Monthly reports: 1st day of month at 10:00 AM')
        self.stdout.write('🗑️ Cleanup old reports: Every day at 2:00 AM')
        self.stdout.write('📊 Analytics summary: Every 6 hours')
        self.stdout.write('')
        self.stdout.write('To verify tasks are running:')
        self.stdout.write('1. Check Celery Beat logs')
        self.stdout.write('2. Check Django Admin > Periodic Tasks')
        self.stdout.write('3. Monitor task execution in Celery Worker logs')
