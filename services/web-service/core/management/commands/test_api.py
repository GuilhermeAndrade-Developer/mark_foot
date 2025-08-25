from django.core.management.base import BaseCommand
from django.utils import timezone
from api_integration.football_data_client import FootballDataAPIClient, get_free_tier_competitions
from core.models import Area, Competition, Team, ApiSyncLog
import json


class Command(BaseCommand):
    help = 'Test Football Data API connection and sync basic data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--competitions-only',
            action='store_true',
            help='Only test competitions endpoint',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Testing Football Data API...'))
        
        client = FootballDataAPIClient()
        
        # Test API connection with competitions
        self.stdout.write('📡 Testing API connection...')
        result = client.get_competitions()
        
        if result.get('data'):
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ API connection successful! Status: {result['status_code']}, "
                    f"Time: {result['execution_time']}ms"
                )
            )
            
            competitions = result['data'].get('competitions', [])
            self.stdout.write(f"📊 Found {len(competitions)} competitions")
            
            # Log the API call
            ApiSyncLog.objects.create(
                endpoint='competitions',
                http_status=result['status_code'],
                records_processed=len(competitions),
                execution_time_ms=result['execution_time'],
                sync_date=timezone.now(),
                response_data={'sample': competitions[:2] if competitions else []}
            )
            
            # Show free tier competitions available
            free_tier_codes = get_free_tier_competitions()
            available_free = [c for c in competitions if c.get('code') in free_tier_codes]
            
            self.stdout.write(
                self.style.WARNING(f"🆓 Free tier competitions available: {len(available_free)}")
            )
            
            for comp in available_free:
                self.stdout.write(
                    f"  • {comp.get('name', 'Unknown')} ({comp.get('code', 'N/A')})"
                )
            
            if not options['competitions_only']:
                self.sync_basic_data(client, available_free)
                
        else:
            error_msg = result.get('error', 'Unknown error')
            self.stdout.write(
                self.style.ERROR(f"❌ API connection failed: {error_msg}")
            )
            
            # Log the failed API call
            ApiSyncLog.objects.create(
                endpoint='competitions',
                http_status=result.get('status_code'),
                execution_time_ms=result.get('execution_time', 0),
                error_message=error_msg,
                sync_date=timezone.now()
            )

    def sync_basic_data(self, client, competitions):
        """Sync basic competition and area data"""
        self.stdout.write(self.style.SUCCESS('\n🔄 Syncing basic data...'))
        
        areas_created = 0
        competitions_created = 0
        
        for comp_data in competitions:
            # Sync area if exists
            area_data = comp_data.get('area')
            area = None
            
            if area_data and area_data.get('id'):
                area, created = Area.objects.get_or_create(
                    id=area_data['id'],
                    defaults={
                        'name': area_data.get('name', ''),
                        'code': area_data.get('code', ''),
                        'flag_url': area_data.get('flag', ''),
                    }
                )
                if created:
                    areas_created += 1
                    self.stdout.write(f"  📍 Created area: {area.name}")
            
            # Sync competition
            if comp_data.get('id'):
                comp, created = Competition.objects.get_or_create(
                    id=comp_data['id'],
                    defaults={
                        'area': area,
                        'name': comp_data.get('name', ''),
                        'code': comp_data.get('code', ''),
                        'type': comp_data.get('type', 'LEAGUE'),
                        'emblem_url': comp_data.get('emblem', ''),
                        'plan': comp_data.get('plan', ''),
                        'number_of_available_seasons': comp_data.get('numberOfAvailableSeasons', 0),
                        'last_updated': timezone.now(),
                    }
                )
                
                if created:
                    competitions_created += 1
                    self.stdout.write(f"  🏆 Created competition: {comp.name}")
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Sync completed!\n"
                f"  📍 Areas created: {areas_created}\n"
                f"  🏆 Competitions created: {competitions_created}"
            )
        )
        
        # Test one specific competition endpoint
        if competitions:
            test_comp = competitions[0]
            comp_code = test_comp.get('code')
            if comp_code:
                self.stdout.write(f"\n🔍 Testing specific competition: {comp_code}")
                result = client.get_competition(comp_code)
                
                if result.get('data'):
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ Competition details retrieved successfully! "
                            f"Time: {result['execution_time']}ms"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f"❌ Failed to get competition details: {result.get('error', 'Unknown error')}"
                        )
                    )
