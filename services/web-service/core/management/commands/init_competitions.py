from django.core.management.base import BaseCommand
from core.models import Competition, Area
from django.db import transaction


class Command(BaseCommand):
    help = 'Initialize basic competitions data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Initializing basic competitions...'))
        
        # Create default area if not exists
        area, created = Area.objects.get_or_create(
            id=2077,  # World area
            defaults={
                'name': 'World',
                'code': 'WOR',
                'flag_url': ''
            }
        )
        
        if created:
            self.stdout.write(f'✅ Created area: {area.name}')
        
        # Basic competitions data
        competitions_data = [
            {
                'id': 2021,
                'code': 'PL',
                'name': 'Premier League',
                'type': 'LEAGUE',
                'emblem_url': 'https://crests.football-data.org/PL.png'
            },
            {
                'id': 2002,
                'code': 'BL1',
                'name': 'Bundesliga',
                'type': 'LEAGUE',
                'emblem_url': 'https://crests.football-data.org/BL1.png'
            },
            {
                'id': 2014,
                'code': 'PD',
                'name': 'Primera División',
                'type': 'LEAGUE',
                'emblem_url': 'https://crests.football-data.org/PD.png'
            },
            {
                'id': 2019,
                'code': 'SA',
                'name': 'Serie A',
                'type': 'LEAGUE',
                'emblem_url': 'https://crests.football-data.org/SA.png'
            },
            {
                'id': 2015,
                'code': 'FL1',
                'name': 'Ligue 1',
                'type': 'LEAGUE',
                'emblem_url': 'https://crests.football-data.org/FL1.png'
            },
            {
                'id': 2013,
                'code': 'BSA',
                'name': 'Campeonato Brasileiro Série A',
                'type': 'LEAGUE',
                'emblem_url': 'https://crests.football-data.org/BSA.png'
            },
            {
                'id': 2001,
                'code': 'CL',
                'name': 'UEFA Champions League',
                'type': 'CUP',
                'emblem_url': 'https://crests.football-data.org/CL.png'
            },
            {
                'id': 2003,
                'code': 'DED',
                'name': 'Eredivisie',
                'type': 'LEAGUE',
                'emblem_url': 'https://crests.football-data.org/DED.png'
            },
            {
                'id': 2017,
                'code': 'PPL',
                'name': 'Primeira Liga',
                'type': 'LEAGUE',
                'emblem_url': 'https://crests.football-data.org/PPL.png'
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        with transaction.atomic():
            for comp_data in competitions_data:
                competition, created = Competition.objects.get_or_create(
                    code=comp_data['code'],
                    defaults={
                        'id': comp_data['id'],
                        'name': comp_data['name'],
                        'type': comp_data['type'],
                        'area': area,
                        'emblem_url': comp_data['emblem_url'],
                        'plan': 'TIER_ONE',
                        'current_season_start_date': '2024-08-01',
                        'current_season_end_date': '2025-05-31',
                        'number_of_available_seasons': 1,
                        'last_updated': '2024-08-01T00:00:00Z'
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f'✅ Created competition: {competition.name} ({competition.code})')
                else:
                    # Update existing competition
                    competition.name = comp_data['name']
                    competition.emblem_url = comp_data['emblem_url']
                    competition.save()
                    updated_count += 1
                    self.stdout.write(f'🔄 Updated competition: {competition.name} ({competition.code})')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'🎉 Initialization completed! Created: {created_count}, Updated: {updated_count}'
            )
        )
        
        # Show all competitions
        self.stdout.write('\n📊 Available competitions:')
        for comp in Competition.objects.all().order_by('code'):
            self.stdout.write(f'  {comp.code}: {comp.name}')
