"""
Bridge command to execute seeders from database/seeders directory.
This maintains clean organization while working with Django's command system.
"""
import sys
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Execute development data seeders from database/seeders directory'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all data before seeding (DANGEROUS - will delete all data)',
        )
        parser.add_argument(
            '--modules',
            nargs='*',
            choices=[
                'users', 'core', 'content', 'polls', 'social', 
                'gamification', 'forum', 'chat', 'ai_analytics'
            ],
            help='Specific modules to seed (default: all)',
        )
        parser.add_argument(
            '--users-count',
            type=int,
            default=20,
            help='Number of test users to create (default: 20)',
        )
        parser.add_argument(
            '--quick',
            action='store_true',
            help='Quick seed with minimal data for fast testing',
        )
        parser.add_argument(
            '--no-external',
            action='store_true',
            help='Skip external API calls (teams, players, etc.)',
        )

    def handle(self, *args, **options):
        self.stdout.write('🔗 Bridge: Loading seeders from database/seeders/')
        
        # Find seeders directory (mounted as volume in Docker)
        seeders_path = Path('/database/seeders')
        
        if not seeders_path.exists():
            self.stdout.write(
                self.style.ERROR(f'❌ Seeders directory not found: {seeders_path}')
            )
            return
            
        # Add seeders directory to Python path
        seeders_str = str(seeders_path)
        if seeders_str not in sys.path:
            sys.path.insert(0, seeders_str)
        
        try:
            # Import and execute the main seeder
            self.stdout.write(f'📂 Loading from: {seeders_path}')
            
            # Import the main seeder command class
            from seed_dev_data import Command as MainSeederCommand
            
            # Create instance of the main seeder
            main_seeder = MainSeederCommand()
            main_seeder.stdout = self.stdout
            main_seeder.style = self.style
            
            # Execute with the provided options
            main_seeder.handle(*args, **options)
            
        except ImportError as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Could not import main seeder: {e}')
            )
            self.stdout.write(f'   Looking in: {seeders_path}')
            try:
                self.stdout.write(f'   Available files: {list(seeders_path.glob("*.py"))}')
            except:
                self.stdout.write('   Could not list files')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error executing seeder: {e}')
            )
            import traceback
            traceback.print_exc()
            
        finally:
            # Clean up Python path
            if seeders_str in sys.path:
                sys.path.remove(seeders_str)