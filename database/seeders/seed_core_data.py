#!/usr/bin/env python3
"""
Seeder for core football data (teams, competitions, players).
"""

import os
import sys
import django
from datetime import datetime, timedelta, date
import random

# Add the project root to Python path
sys.path.append('/app')

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mark_foot_backend.settings')
django.setup()

from django.db import transaction
from core.models import Team, Competition, Player, Match, Season, Area, Standing
from django.utils import timezone


def seed_core_data():
    """Create core football data"""
    
    print("⚽ Creating core football data...")
    
    with transaction.atomic():
        # Create areas first
        areas_created = create_areas()
        
        # Create competitions
        competitions_created = create_competitions()
        
        # Create teams
        teams_created = create_teams()
        
        # Create seasons
        seasons_created = create_seasons()
        
        # Create players
        players_created = create_players()
        
        # Create matches
        matches_created = create_matches()
        
        # Create standings
        standings_created = create_standings()

    print(f'✅ Core data seeded successfully!')
    print(f'   🌍 Areas: {areas_created}')
    print(f'   🏆 Competitions: {competitions_created}')
    print(f'   ⚽ Teams: {teams_created}')
    print(f'   📅 Seasons: {seasons_created}')
    print(f'   🏃 Players: {players_created}')
    print(f'   📊 Matches: {matches_created}')
    print(f'   📈 Standings: {standings_created}')


def create_areas():
    """Create basic areas/countries"""
    areas_data = [
        {'id': 2032, 'name': 'Brazil', 'code': 'BRA'},
        {'id': 2114, 'name': 'Spain', 'code': 'ESP'},
        {'id': 2072, 'name': 'England', 'code': 'ENG'},
        {'id': 2081, 'name': 'Germany', 'code': 'GER'},
        {'id': 2109, 'name': 'Italy', 'code': 'ITA'},
        {'id': 2080, 'name': 'France', 'code': 'FRA'},
        {'id': 2077, 'name': 'Argentina', 'code': 'ARG'},
        {'id': 2267, 'name': 'Europe', 'code': 'EUR'},
    ]

    created_count = 0
    for area_data in areas_data:
        area, created = Area.objects.get_or_create(
            id=area_data['id'],
            defaults=area_data
        )
        if created:
            created_count += 1

    return created_count


def create_competitions():
    """Create basic competitions"""
    competitions_data = [
        {
            'id': 2013,
            'name': 'Campeonato Brasileiro Série A',
            'code': 'BSA',
            'type': 'LEAGUE',
            'plan': 'TIER_TWO',
            'area_id': 2032,  # Brazil
        },
        {
            'id': 2001,
            'name': 'UEFA Champions League',
            'code': 'CL',
            'type': 'CUP',
            'plan': 'TIER_ONE',
            'area_id': 2267,  # Europe
        },
        {
            'id': 2021,
            'name': 'Premier League',
            'code': 'PL',
            'type': 'LEAGUE',
            'plan': 'TIER_ONE',
            'area_id': 2072,  # England
        },
        {
            'id': 2014,
            'name': 'La Liga',
            'code': 'PD',
            'type': 'LEAGUE',
            'plan': 'TIER_ONE',
            'area_id': 2114,  # Spain
        },
        {
            'id': 2002,
            'name': 'Bundesliga',
            'code': 'BL1',
            'type': 'LEAGUE',
            'plan': 'TIER_ONE',
            'area_id': 2081,  # Germany
        }
    ]

    created_count = 0
    for comp_data in competitions_data:
        competition, created = Competition.objects.get_or_create(
            id=comp_data['id'],
            defaults=comp_data
        )
        if created:
            created_count += 1

    return created_count


def create_teams():
    """Create teams with Brazilian and international clubs"""
    teams_data = [
        # Brazilian teams
        {'id': 1900, 'name': 'Flamengo', 'short_name': 'Flamengo', 'tla': 'FLA', 'area_id': 2032, 'founded': 1895},
        {'id': 1901, 'name': 'São Paulo FC', 'short_name': 'São Paulo', 'tla': 'SAO', 'area_id': 2032, 'founded': 1930},
        {'id': 1902, 'name': 'Palmeiras', 'short_name': 'Palmeiras', 'tla': 'PAL', 'area_id': 2032, 'founded': 1914},
        {'id': 1903, 'name': 'Corinthians', 'short_name': 'Corinthians', 'tla': 'COR', 'area_id': 2032, 'founded': 1910},
        {'id': 1904, 'name': 'Santos FC', 'short_name': 'Santos', 'tla': 'SAN', 'area_id': 2032, 'founded': 1912},
        {'id': 1905, 'name': 'Grêmio FBPA', 'short_name': 'Grêmio', 'tla': 'GRE', 'area_id': 2032, 'founded': 1903},
        
        # International teams
        {'id': 86, 'name': 'Real Madrid CF', 'short_name': 'Real Madrid', 'tla': 'RMA', 'area_id': 2114, 'founded': 1902},
        {'id': 81, 'name': 'FC Barcelona', 'short_name': 'Barcelona', 'tla': 'BAR', 'area_id': 2114, 'founded': 1899},
        {'id': 65, 'name': 'Manchester City FC', 'short_name': 'Man City', 'tla': 'MCI', 'area_id': 2072, 'founded': 1880},
        {'id': 64, 'name': 'Liverpool FC', 'short_name': 'Liverpool', 'tla': 'LIV', 'area_id': 2072, 'founded': 1892},
        {'id': 524, 'name': 'Paris Saint-Germain FC', 'short_name': 'Paris SG', 'tla': 'PSG', 'area_id': 2080, 'founded': 1970},
        {'id': 5, 'name': 'FC Bayern München', 'short_name': 'Bayern M', 'tla': 'FCB', 'area_id': 2081, 'founded': 1900},
    ]

    created_count = 0
    for team_data in teams_data:
        team, created = Team.objects.get_or_create(
            id=team_data['id'],
            defaults=team_data
        )
        if created:
            created_count += 1

    return created_count


def create_seasons():
    """Create seasons for competitions"""
    competitions = Competition.objects.all()
    created_count = 0
    
    for competition in competitions:
        # Create 2024 season
        season, created = Season.objects.get_or_create(
            competition=competition,
            start_date=date(2024, 1, 1),
            defaults={
                'end_date': date(2024, 12, 31),
                'current_matchday': random.randint(1, 38),
                'available': True
            }
        )
        if created:
            created_count += 1
    
    return created_count


def create_players():
    """Create players for teams"""
    teams = Team.objects.all()
    if not teams.exists():
        return 0

    # Brazilian player names
    player_names = [
        ('Gabriel Jesus', 'FW'),
        ('Casemiro', 'MF'),
        ('Thiago Silva', 'DF'),
        ('Alisson Becker', 'GK'),
        ('Vinícius Júnior', 'FW'),
        ('Bruno Guimarães', 'MF'),
        ('Marquinhos', 'DF'),
        ('Ederson', 'GK'),
        ('Antony', 'FW'),
        ('Fred', 'MF'),
        ('Éder Militão', 'DF'),
        ('Weverton', 'GK'),
        ('Raphinha', 'FW'),
        ('Fabinho', 'MF'),
        ('Alex Sandro', 'DF'),
        ('Lucas Paquetá', 'MF'),
        ('Richarlison', 'FW'),
        ('Douglas Luiz', 'MF'),
        ('Danilo', 'DF'),
        ('João Paulo', 'GK'),
    ]

    created_count = 0
    player_id = 10000  # Starting ID for players

    for team in teams:
        # Create 8-12 players per team
        num_players = random.randint(8, 12)
        team_players = random.sample(player_names, min(num_players, len(player_names)))
        
        for player_name, position_cat in team_players:
            player, created = Player.objects.get_or_create(
                external_id=str(player_id),
                defaults={
                    'name': player_name,
                    'short_name': player_name.split()[-1],
                    'team': team,
                    'nationality': team.area.name if team.area else 'Unknown',
                    'age': random.randint(18, 35),
                    'position_category': position_cat,
                    'status': 'Active',
                    'height': f"{random.randint(165, 195)} cm",
                    'weight': f"{random.randint(65, 90)} kg",
                }
            )
            if created:
                created_count += 1
                player_id += 1

    return created_count


def create_matches():
    """Create sample matches"""
    teams = list(Team.objects.all())
    competitions = list(Competition.objects.all())
    seasons = list(Season.objects.all())
    
    if len(teams) < 2 or not competitions or not seasons:
        return 0

    created_count = 0
    match_id = 400000  # Starting ID for matches

    for _ in range(30):  # Create 30 matches
        # Select random teams, competition and season
        home_team, away_team = random.sample(teams, 2)
        competition = random.choice(competitions)
        season = random.choice([s for s in seasons if s.competition == competition])
        
        # Create match date (last 30 days or next 15 days)
        if random.choice([True, False]):
            # Past match
            match_date = timezone.now() - timedelta(days=random.randint(1, 30))
            status = 'FINISHED'
            home_score = random.randint(0, 4)
            away_score = random.randint(0, 4)
            if home_score > away_score:
                winner = 'HOME_TEAM'
            elif away_score > home_score:
                winner = 'AWAY_TEAM'
            else:
                winner = 'DRAW'
        else:
            # Future match
            match_date = timezone.now() + timedelta(days=random.randint(1, 15))
            status = 'SCHEDULED'
            home_score = None
            away_score = None
            winner = None

        match, created = Match.objects.get_or_create(
            id=match_id,
            defaults={
                'home_team': home_team,
                'away_team': away_team,
                'competition': competition,
                'season': season,
                'utc_date': match_date,
                'status': status,
                'home_team_score': home_score,
                'away_team_score': away_score,
                'winner': winner,
                'matchday': random.randint(1, 38),
                'stage': 'REGULAR_SEASON',
            }
        )
        if created:
            created_count += 1
            match_id += 1

    return created_count


def create_standings():
    """Create sample standings"""
    competitions = Competition.objects.filter(type='LEAGUE')
    seasons = Season.objects.all()
    
    created_count = 0
    
    for competition in competitions:
        season = seasons.filter(competition=competition).first()
        if not season:
            continue
            
        teams = Team.objects.filter(area=competition.area)[:10]  # Top 10 teams
        
        for i, team in enumerate(teams, 1):
            standing, created = Standing.objects.get_or_create(
                competition=competition,
                season=season,
                team=team,
                type='TOTAL',
                snapshot_date=timezone.now().date(),
                defaults={
                    'position': i,
                    'played_games': random.randint(10, 25),
                    'won': random.randint(5, 20),
                    'draw': random.randint(2, 8),
                    'lost': random.randint(1, 10),
                    'points': random.randint(20, 70),
                    'goals_for': random.randint(15, 60),
                    'goals_against': random.randint(10, 40),
                    'goal_difference': random.randint(-10, 30),
                }
            )
            if created:
                created_count += 1
    
    return created_count


if __name__ == '__main__':
    seed_core_data()
