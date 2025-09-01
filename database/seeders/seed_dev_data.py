"""
Master seeder command for development environment.
This command coordinates all seeders and provides a single entry point
for populating the database with development data.
"""

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.contrib.auth.models import User
from django.db import transaction
from django.conf import settings
import os
import time


class Command(BaseCommand):
    help = 'Populate database with comprehensive development data'

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
                'users', 'core', 'billing', 'content', 'polls', 'social', 
                'gamification', 'forum', 'chat', 'ai_analytics',
                'business', 'social_sharing', 'whatsapp'
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
        # Check if we're in development
        if not self.is_development_environment():
            self.stdout.write(
                self.style.ERROR(
                    '🚫 This command should only be used in development environment!\n'
                    'Current DEBUG setting: False'
                )
            )
            return

        start_time = time.time()
        
        self.stdout.write(
            self.style.SUCCESS(
                '🌱 Mark Foot Development Data Seeder\n'
                f'   Environment: {"QUICK" if options["quick"] else "FULL"}\n'
                f'   Reset data: {"YES" if options["reset"] else "NO"}\n'
                f'   Target users: {options["users_count"]}\n'
            )
        )

        try:
            with transaction.atomic():
                if options['reset']:
                    self.reset_database()

                # Determine which modules to seed
                modules_to_seed = options['modules'] or [
                    'users', 'core', 'billing', 'content', 'polls', 'social', 
                    'gamification', 'forum', 'chat', 'business', 'social_sharing', 'whatsapp'
                ]
                
                if not options['no_external']:
                    modules_to_seed.append('ai_analytics')

                # Execute seeders in order
                self.seed_base_data(options)
                
                for module in modules_to_seed:
                    self.seed_module(module, options)

                self.stdout.write('\n📊 Seeding Summary:')
                self.print_summary()

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Seeding failed: {str(e)}')
            )
            raise CommandError(f'Seeding failed: {str(e)}')

        elapsed = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Development data seeding completed!\n'
                f'   Total time: {elapsed:.2f} seconds\n'
                f'   Database populated with development data.'
            )
        )

    def is_development_environment(self):
        """Check if we're in a development environment"""
        return (
            settings.DEBUG and 
            ('dev' in str(settings.DATABASES['default']['NAME']).lower() or
             os.environ.get('ENVIRONMENT', '').lower() == 'development')
        )

    def reset_database(self):
        """Reset database (dangerous operation)"""
        self.stdout.write('🗑️  Resetting database...')
        
        # Import all models to ensure they're available
        from django.apps import apps
        
        # List of apps to reset (in reverse dependency order)
        apps_to_reset = [
            'ai_analytics', 'chat', 'forum', 'gamification', 
            'social', 'polls', 'content', 'core'
        ]
        
        for app_name in apps_to_reset:
            try:
                app_config = apps.get_app_config(app_name)
                for model in app_config.get_models():
                    if hasattr(model.objects, 'all'):
                        count = model.objects.count()
                        if count > 0:
                            model.objects.all().delete()
                            self.stdout.write(f'  🧹 Cleared {count} {model.__name__} records')
            except LookupError:
                # App doesn't exist, skip
                continue
        
        # Keep superuser but delete other users
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write('  🧹 Cleared non-superuser accounts')

    def seed_base_data(self, options):
        """Seed base/core data required by other modules"""
        self.stdout.write('\n📦 Seeding base data...')
        
        # Create base admin user if not exists
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@markfoot.dev',
                'first_name': 'Admin',
                'last_name': 'MarkFoot',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write('  ✓ Created admin user (admin/admin123)')

    def seed_module(self, module_name, options):
        """Seed specific module data"""
        self.stdout.write(f'\n🔧 Seeding {module_name} module...')
        
        try:
            if module_name == 'users':
                call_command('seed_users', count=options['users_count'], verbosity=0)
                
            elif module_name == 'core':
                if not options['no_external']:
                    call_command('seed_core_data', quick=options['quick'], verbosity=0)
                    
            elif module_name == 'billing':
                call_command('seed_billing_data', with_user_data=True, verbosity=0)
                
            elif module_name == 'content':
                call_command('seed_content_data', verbosity=0)
                
            elif module_name == 'polls':
                call_command('seed_polls_data', verbosity=0)
                
            elif module_name == 'social':
                call_command('seed_social_data', verbosity=0)
                
            elif module_name == 'gamification':
                call_command('seed_gamification_data', users=min(10, options['users_count']), verbosity=0)
                
            elif module_name == 'forum':
                call_command('seed_forum_data', verbosity=0)
                
            elif module_name == 'chat':
                call_command('seed_chat_data', verbosity=0)
                
            elif module_name == 'ai_analytics':
                if not options['quick']:
                    call_command('seed_ai_data', verbosity=0)
                    
            elif module_name == 'business':
                # Novo seeder para dados de business dashboard
                try:
                    call_command('seed_business_data', verbosity=0)
                except Exception as e:
                    self.stdout.write(f'  ⚠️  Business seeder not implemented yet: {str(e)}')
                    
            elif module_name == 'social_sharing':
                # Novo seeder para dados de compartilhamento social
                try:
                    call_command('seed_social_sharing_data', verbosity=0)
                except Exception as e:
                    self.stdout.write(f'  ⚠️  Social sharing seeder not implemented yet: {str(e)}')
            
            elif module_name == 'whatsapp':
                # Seeder para dados do WhatsApp Integration
                import subprocess
                import os
                try:
                    script_path = os.path.join(settings.BASE_DIR, '..', '..', 'database', 'seeders', 'seed_whatsapp_data.py')
                    result = subprocess.run(['python', script_path], capture_output=True, text=True, cwd=settings.BASE_DIR)
                    if result.returncode == 0:
                        self.stdout.write('  ✓ WhatsApp data seeded via external script')
                    else:
                        self.stdout.write(f'  ❌ WhatsApp seeder failed: {result.stderr}')
                except Exception as e:
                    self.stdout.write(f'  ⚠️  WhatsApp seeder error: {str(e)}')
            
            self.stdout.write(f'  ✓ {module_name} seeded successfully')
            
        except Exception as e:
            self.stdout.write(f'  ❌ Failed to seed {module_name}: {str(e)}')

    def print_summary(self):
        """Print database summary after seeding"""
        try:
            from django.contrib.auth.models import User
            from core.models import Team, Player, Competition, Match
            from content.models import UserArticle, ContentCategory
            from polls.models import Poll, PollOption
            from social.models import PrivateGroup, SocialPlatform
            from gamification.models import UserProfile, Badge
            from billing.models import SubscriptionPlan
            
            self.stdout.write(f'  👥 Users: {User.objects.count()}')
            self.stdout.write(f'  ⚽ Teams: {Team.objects.count()}')
            self.stdout.write(f'  🏃 Players: {Player.objects.count()}')
            self.stdout.write(f'  🏆 Competitions: {Competition.objects.count()}')
            self.stdout.write(f'  📊 Matches: {Match.objects.count()}')
            self.stdout.write(f'  📝 Articles: {UserArticle.objects.count()}')
            self.stdout.write(f'  📋 Categories: {ContentCategory.objects.count()}')
            self.stdout.write(f'  🗳️  Polls: {Poll.objects.count()}')
            self.stdout.write(f'  👥 Groups: {PrivateGroup.objects.count()}')
            self.stdout.write(f'  📱 Social Platforms: {SocialPlatform.objects.count()}')
            self.stdout.write(f'  🎮 User Profiles: {UserProfile.objects.count()}')
            self.stdout.write(f'  🏅 Badges: {Badge.objects.count()}')
            self.stdout.write(f'  💳 Subscription Plans: {SubscriptionPlan.objects.count()}')
            
            # WhatsApp stats
            try:
                from whatsapp_integration.models import WhatsAppUser, WhatsAppMessage, WhatsAppSession
                self.stdout.write(f'  📱 WhatsApp Users: {WhatsAppUser.objects.count()}')
                self.stdout.write(f'  💬 WhatsApp Messages: {WhatsAppMessage.objects.count()}')
                self.stdout.write(f'  🔗 WhatsApp Sessions: {WhatsAppSession.objects.count()}')
            except ImportError:
                pass
            
        except ImportError as e:
            self.stdout.write(f'  ⚠️  Could not generate summary: {str(e)}')
