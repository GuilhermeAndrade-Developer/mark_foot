#!/usr/bin/env python
"""
Seeder for NLP Engine with Brazilian football specific data
"""
import os
import sys
import django

# Setup Django environment
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mark_foot_backend.settings')
django.setup()

from nlp_engine.models import EntityValue, EntityType
from core.models import Team, Player, Competition

def seed_nlp_entities():
    """Seed NLP entities with Brazilian football data"""
    print("🧠 Seeding NLP entities with Brazilian football data...")
    
    # Get entity types
    team_entity_type, _ = EntityType.objects.get_or_create(name='team')
    player_entity_type, _ = EntityType.objects.get_or_create(name='player')
    competition_entity_type, _ = EntityType.objects.get_or_create(name='competition')
    
    # Seed team entities with popular synonyms
    teams_data = [
        {
            'canonical': 'flamengo',
            'synonyms': ['fla', 'mengão', 'rubro-negro', 'clube de regatas do flamengo']
        },
        {
            'canonical': 'palmeiras',
            'synonyms': ['alviverde', 'verdão', 'palestra', 'sociedade esportiva palmeiras']
        },
        {
            'canonical': 'corinthians',
            'synonyms': ['timão', 'corintians', 'sport club corinthians paulista']
        },
        {
            'canonical': 'são paulo',
            'synonyms': ['spfc', 'tricolor', 'são paulo fc']
        },
        {
            'canonical': 'santos',
            'synonyms': ['peixe', 'santos fc', 'alvinegro praiano']
        },
        {
            'canonical': 'vasco',
            'synonyms': ['vasco da gama', 'gigante da colina', 'cruz-maltino']
        },
        {
            'canonical': 'botafogo',
            'synonyms': ['bota', 'fogão', 'estrela solitária']
        },
        {
            'canonical': 'fluminense',
            'synonyms': ['flu', 'tricolor carioca', 'nense']
        },
        {
            'canonical': 'grêmio',
            'synonyms': ['tricolor gaúcho', 'imortal', 'grêmio fbpa']
        },
        {
            'canonical': 'internacional',
            'synonyms': ['inter', 'colorado', 'sport club internacional']
        },
        {
            'canonical': 'atlético mineiro',
            'synonyms': ['galo', 'atlético-mg', 'clube atlético mineiro']
        },
        {
            'canonical': 'cruzeiro',
            'synonyms': ['raposa', 'celeste', 'cruzeiro esporte clube']
        }
    ]
    
    for team_data in teams_data:
        EntityValue.objects.get_or_create(
            entity_type=team_entity_type,
            canonical_value=team_data['canonical'],
            defaults={
                'value': team_data['canonical'],
                'synonyms': team_data['synonyms'],
                'confidence_score': 1.0
            }
        )
    
    # Seed famous Brazilian players
    players_data = [
        {
            'canonical': 'gabigol',
            'synonyms': ['gabriel barbosa', 'gabriel', 'gabigol']
        },
        {
            'canonical': 'neymar',
            'synonyms': ['neymar jr', 'ney', 'neymar santos']
        },
        {
            'canonical': 'vinicius junior',
            'synonyms': ['vini jr', 'vinicius', 'vini']
        },
        {
            'canonical': 'casemiro',
            'synonyms': ['case', 'casemiro']
        },
        {
            'canonical': 'alisson',
            'synonyms': ['alisson becker', 'goleiro alisson']
        },
        {
            'canonical': 'rodrygo',
            'synonyms': ['rodrygo goes', 'rodrigo']
        },
        {
            'canonical': 'raphinha',
            'synonyms': ['raphael dias', 'raphinha']
        },
        {
            'canonical': 'bruno henrique',
            'synonyms': ['bruno henrique pinto', 'bh']
        },
        {
            'canonical': 'hulk',
            'synonyms': ['givanildo vieira', 'hulk paraíba']
        },
        {
            'canonical': 'dudu',
            'synonyms': ['eduardo pereira', 'dudu palmeiras']
        }
    ]
    
    for player_data in players_data:
        EntityValue.objects.get_or_create(
            entity_type=player_entity_type,
            canonical_value=player_data['canonical'],
            defaults={
                'value': player_data['canonical'],
                'synonyms': player_data['synonyms'],
                'confidence_score': 1.0
            }
        )
    
    # Seed competitions with Brazilian names
    competitions_data = [
        {
            'canonical': 'brasileirão',
            'synonyms': ['campeonato brasileiro', 'série a', 'brasileiro', 'brasileirao']
        },
        {
            'canonical': 'copa do brasil',
            'synonyms': ['copa brasil', 'cbf']
        },
        {
            'canonical': 'libertadores',
            'synonyms': ['copa libertadores', 'conmebol libertadores', 'liberta']
        },
        {
            'canonical': 'champions league',
            'synonyms': ['liga dos campeões', 'champions', 'ucl']
        },
        {
            'canonical': 'carioca',
            'synonyms': ['campeonato carioca', 'estadual rio']
        },
        {
            'canonical': 'paulista',
            'synonyms': ['campeonato paulista', 'estadual são paulo']
        }
    ]
    
    for comp_data in competitions_data:
        EntityValue.objects.get_or_create(
            entity_type=competition_entity_type,
            canonical_value=comp_data['canonical'],
            defaults={
                'value': comp_data['canonical'],
                'synonyms': comp_data['synonyms'],
                'confidence_score': 1.0
            }
        )
    
    print("✅ NLP entities seeded successfully!")
    print(f"Team entities: {EntityValue.objects.filter(entity_type=team_entity_type).count()}")
    print(f"Player entities: {EntityValue.objects.filter(entity_type=player_entity_type).count()}")
    print(f"Competition entities: {EntityValue.objects.filter(entity_type=competition_entity_type).count()}")

if __name__ == "__main__":
    seed_nlp_entities()
