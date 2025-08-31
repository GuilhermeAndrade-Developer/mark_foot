from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'DEPRECATED: Use seed_dev_data instead. This command now redirects to the new seeder system.'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING(
                '⚠️  This command is deprecated!\n'
                'Please use: python manage.py seed_dev_data\n'
                'Redirecting to new seeder system...'
            )
        )
        
        # Redirect to new seeder
        call_command('seed_dev_data', modules=['content', 'polls'], verbosity=1)
