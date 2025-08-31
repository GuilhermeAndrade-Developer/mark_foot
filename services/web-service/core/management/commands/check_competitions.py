from django.core.management.base import BaseCommand
from core.models import Competition, Area
from api_integration.football_data_client import FootballDataAPIClient


class Command(BaseCommand):
    help = 'Check and create missing competitions'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Verificando competições no banco de dados...')
        
        # Competições principais que devem existir
        required_competitions = {
            'PL': 'Premier League',
            'BL1': 'Bundesliga',
            'PD': 'Primera División',
            'SA': 'Serie A',
            'FL1': 'Ligue 1',
            'BSA': 'Campeonato Brasileiro Série A',
            'CL': 'UEFA Champions League',
            'DED': 'Eredivisie',
            'PPL': 'Primeira Liga'
        }
        
        existing_competitions = Competition.objects.all()
        self.stdout.write(f'📊 Competições existentes: {existing_competitions.count()}')
        
        for comp in existing_competitions:
            self.stdout.write(f'  ✅ {comp.code}: {comp.name}')
        
        missing_competitions = []
        for code, name in required_competitions.items():
            if not Competition.objects.filter(code=code).exists():
                missing_competitions.append((code, name))
        
        if missing_competitions:
            self.stdout.write(f'\n❌ Competições faltando: {len(missing_competitions)}')
            for code, name in missing_competitions:
                self.stdout.write(f'  - {code}: {name}')
            
            # Try to fetch from API and create them
            self.stdout.write('\n🔄 Tentando buscar da API...')
            try:
                api_client = FootballDataAPIClient()
                response = api_client.get_competitions()
                
                if response.get('data'):
                    competitions_data = response['data'].get('competitions', [])
                    
                    for comp_data in competitions_data:
                        code = comp_data.get('code')
                        if code in [c[0] for c in missing_competitions]:
                            # Create or get area
                            area_data = comp_data.get('area', {})
                            area = None
                            if area_data:
                                area, created = Area.objects.get_or_create(
                                    id=area_data['id'],
                                    defaults={
                                        'name': area_data['name'],
                                        'code': area_data.get('code', ''),
                                        'flag_url': area_data.get('flag', '')
                                    }
                                )
                            
                            # Create competition
                            competition = Competition.objects.create(
                                id=comp_data['id'],
                                name=comp_data['name'],
                                code=comp_data['code'],
                                type=comp_data.get('type', 'LEAGUE'),
                                emblem_url=comp_data.get('emblem', ''),
                                plan=comp_data.get('plan', 'TIER_ONE'),
                                area=area
                            )
                            
                            self.stdout.write(f'  ✅ Criada: {competition.code}: {competition.name}')
                
                self.stdout.write('\n✅ Verificação e criação de competições concluída!')
                            
            except Exception as e:
                self.stdout.write(f'\n❌ Erro ao buscar da API: {str(e)}')
        else:
            self.stdout.write('\n✅ Todas as competições necessárias estão presentes!')
