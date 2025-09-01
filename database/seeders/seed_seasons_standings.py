#!/usr/bin/env python3
"""
Seeder for football seasons and standings data.
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
from core.models import Season, Standing, Team, Competition


def seed_seasons_and_standings():
    """Create sample seasons and standings"""
    
    print("🚀 Creating seasons and standings data...")
    
    with transaction.atomic():
        # Get competitions and teams
        competitions = list(Competition.objects.all())
        teams = list(Team.objects.all())
        
        if not competitions:
            print("❌ No competitions found. Please run core seeder first.")
            return
        
        if not teams:
            print("❌ No teams found. Please run core seeder first.")
            return
        
        # Create Seasons
        print("📅 Creating seasons...")
        seasons_created = 0
        
        # Create seasons for 2022, 2023, 2024
        for year in [2022, 2023, 2024]:
            for competition in competitions:
                # Determine season format based on competition type
                if competition.type == 'league':
                    season_name = str(year)
                    start_date = date(year, 1, 15)
                    end_date = date(year, 12, 15)
                else:  # cup
                    season_name = f"{year}-{year+1}"
                    start_date = date(year, 8, 1)
                    end_date = date(year+1, 6, 30)
                
                # Check if season already exists
                season, created = Season.objects.get_or_create(
                    competition=competition,
                    name=season_name,
                    defaults={
                        'start_date': start_date,
                        'end_date': end_date,
                        'is_current': year == 2024,
                        'total_rounds': 38 if competition.type == 'league' else random.randint(5, 8)
                    }
                )
                
                if created:
                    seasons_created += 1
        
        print(f"✅ Created {seasons_created} seasons")
        
        # Create Standings
        print("📊 Creating standings...")
        standings_created = 0
        
        # Get current seasons
        current_seasons = Season.objects.filter(is_current=True)
        
        for season in current_seasons:
            # Get teams for this competition (based on country/region)
            if season.competition.country == 'Brazil':
                # Brazilian teams for Brazilian competitions
                competition_teams = [team for team in teams if team.country == 'Brazil']
            elif season.competition.country in ['Europe', 'International']:
                # Mix of teams for international competitions
                competition_teams = random.sample(teams, min(16, len(teams)))
            else:
                # Teams from specific countries
                country_teams = [team for team in teams if team.country == season.competition.country]
                if not country_teams:
                    country_teams = random.sample(teams, min(20, len(teams)))
                competition_teams = country_teams
            
            # Limit teams for league format
            if season.competition.type == 'league':
                competition_teams = competition_teams[:20]  # Max 20 teams in league
            else:
                competition_teams = competition_teams[:16]  # Max 16 teams in cup
            
            # Create standings for each team
            for position, team in enumerate(competition_teams, 1):
                # Generate realistic stats based on position
                games_played = random.randint(15, 25)
                
                # Better teams (lower position) have better stats
                position_factor = (len(competition_teams) - position + 1) / len(competition_teams)
                
                # Wins - better teams win more
                wins = int(games_played * position_factor * random.uniform(0.4, 0.8))
                
                # Losses - worse teams lose more
                losses = int(games_played * (1 - position_factor) * random.uniform(0.3, 0.7))
                
                # Draws - fill the remaining games
                draws = games_played - wins - losses
                if draws < 0:
                    draws = 0
                    wins = games_played - losses
                
                # Goals - better teams score more and concede less
                goals_for = int(wins * random.uniform(1.5, 3.0) + draws * random.uniform(0.8, 1.5) + losses * random.uniform(0.5, 1.2))
                goals_against = int(losses * random.uniform(1.2, 2.5) + draws * random.uniform(0.8, 1.5) + wins * random.uniform(0.3, 1.0))
                
                # Points calculation
                points = wins * 3 + draws
                
                standing = Standing.objects.create(
                    season=season,
                    team=team,
                    position=position,
                    games_played=games_played,
                    wins=wins,
                    draws=draws,
                    losses=losses,
                    goals_for=goals_for,
                    goals_against=goals_against,
                    goal_difference=goals_for - goals_against,
                    points=points,
                    form=generate_form_string(),
                    last_updated=datetime.now() - timedelta(days=random.randint(0, 7))
                )
                standings_created += 1
        
        print(f"✅ Created {standings_created} standings")
        
        print('\n🎉 Seasons and standings data seeded successfully!')
        
        # Display summary
        print(f'\n📊 Summary:')
        print(f'   Seasons: {Season.objects.count()}')
        print(f'   - Current Seasons: {Season.objects.filter(is_current=True).count()}')
        print(f'   Standings: {Standing.objects.count()}')
        
        # Show current season standings summary
        for season in Season.objects.filter(is_current=True)[:3]:
            standings_count = Standing.objects.filter(season=season).count()
            print(f'   - {season.competition.name} ({season.name}): {standings_count} teams')


def generate_form_string():
    """Generate a form string like 'WWDLL' representing last 5 games"""
    results = ['W', 'D', 'L']
    weights = [50, 25, 25]  # 50% wins, 25% draws, 25% losses
    
    form_length = random.randint(3, 5)
    form = []
    
    for _ in range(form_length):
        result = random.choices(results, weights=weights)[0]
        form.append(result)
    
    return ''.join(form)


if __name__ == '__main__':
    seed_seasons_and_standings()
