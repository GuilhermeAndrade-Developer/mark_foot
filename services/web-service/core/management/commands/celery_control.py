from django.core.management.base import BaseCommand
from django.conf import settings
import subprocess
import sys


class Command(BaseCommand):
    help = 'Manage Celery services'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            type=str,
            choices=['start', 'stop', 'restart', 'status'],
            help='Action to perform on Celery services'
        )

    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'start':
            self.start_celery()
        elif action == 'stop':
            self.stop_celery()
        elif action == 'restart':
            self.restart_celery()
        elif action == 'status':
            self.check_status()

    def start_celery(self):
        self.stdout.write('🚀 Starting Celery services...')
        try:
            # Start Celery worker
            result = subprocess.run([
                'docker', 'start', 'mark_foot_celery_worker_dev'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.stdout.write('✅ Celery worker started')
            else:
                self.stdout.write(f'❌ Error starting worker: {result.stderr}')
            
            # Start Celery beat
            result = subprocess.run([
                'docker', 'start', 'mark_foot_celery_beat_dev'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.stdout.write('✅ Celery beat started')
            else:
                self.stdout.write(f'❌ Error starting beat: {result.stderr}')
                
        except Exception as e:
            self.stdout.write(f'❌ Error: {e}')

    def stop_celery(self):
        self.stdout.write('🛑 Stopping Celery services...')
        try:
            # Stop Celery beat
            result = subprocess.run([
                'docker', 'stop', 'mark_foot_celery_beat_dev'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.stdout.write('✅ Celery beat stopped')
            else:
                self.stdout.write(f'❌ Error stopping beat: {result.stderr}')
            
            # Stop Celery worker
            result = subprocess.run([
                'docker', 'stop', 'mark_foot_celery_worker_dev'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.stdout.write('✅ Celery worker stopped')
            else:
                self.stdout.write(f'❌ Error stopping worker: {result.stderr}')
                
        except Exception as e:
            self.stdout.write(f'❌ Error: {e}')

    def restart_celery(self):
        self.stop_celery()
        self.stdout.write('⏳ Waiting 3 seconds...')
        import time
        time.sleep(3)
        self.start_celery()

    def check_status(self):
        self.stdout.write('📊 Checking Celery services status...')
        try:
            # Check worker
            result = subprocess.run([
                'docker', 'ps', '--filter', 'name=mark_foot_celery_worker_dev', '--format', 'table {{.Names}}\t{{.Status}}'
            ], capture_output=True, text=True)
            
            if 'mark_foot_celery_worker_dev' in result.stdout:
                status_line = [line for line in result.stdout.split('\n') if 'mark_foot_celery_worker_dev' in line][0]
                self.stdout.write(f'🔧 Worker: {status_line}')
            else:
                self.stdout.write('❌ Worker: Not running')
            
            # Check beat
            result = subprocess.run([
                'docker', 'ps', '--filter', 'name=mark_foot_celery_beat_dev', '--format', 'table {{.Names}}\t{{.Status}}'
            ], capture_output=True, text=True)
            
            if 'mark_foot_celery_beat_dev' in result.stdout:
                status_line = [line for line in result.stdout.split('\n') if 'mark_foot_celery_beat_dev' in line][0]
                self.stdout.write(f'📅 Beat: {status_line}')
            else:
                self.stdout.write('❌ Beat: Not running')
                
        except Exception as e:
            self.stdout.write(f'❌ Error checking status: {e}')
