from django.core.management.base import BaseCommand
from data_management.tasks import health_check


class Command(BaseCommand):
    help = 'Test Celery connectivity'

    def handle(self, *args, **options):
        self.stdout.write('🧪 Testing Celery connectivity...')
        
        try:
            # Test simple task
            result = health_check.delay()
            self.stdout.write(f'✅ Task submitted with ID: {result.id}')
            
            # Wait for result with timeout
            health_data = result.get(timeout=30)
            
            self.stdout.write('📊 Health check result:')
            self.stdout.write(f'   Status: {health_data["status"]}')
            self.stdout.write(f'   Timestamp: {health_data["timestamp"]}')
            
            if health_data["status"] == "healthy":
                self.stdout.write(self.style.SUCCESS('✅ Celery is working correctly!'))
            else:
                self.stdout.write(self.style.ERROR(f'❌ Health check failed: {health_data.get("error")}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Celery test failed: {str(e)}'))
