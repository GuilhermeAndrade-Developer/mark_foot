#!/usr/bin/env python3
"""
Seeder for player statistics and transfers data.
"""

import os
import sys
import django
from datetime import datetime, timedelta, date
import random
from decimal import Decimal

# Add the project root to Python path
sys.path.append('/app')

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mark_foot_backend.settings')
django.setup()

from django.db import transaction
from core.models import Player, PlayerStatistic, PlayerTransfer, Team, Season


def seed_player_data():
    """Create sample player statistics and transfers"""
    
    print("🚀 Creating player statistics and transfers data...")
    
    with transaction.atomic():
        # Get players, teams and seasons
        players = list(Player.objects.all())
        teams = list(Team.objects.all())
        seasons = list(Season.objects.all())
        
        if not players:
            print("❌ No players found. Please run core seeder first.")
            return
        
        if not teams:
            print("❌ No teams found. Please run core seeder first.")
            return
        
        # Create Player Statistics
        print("📊 Creating player statistics...")
        statistics_created = 0
        
        for player in players:
            # Create statistics for current season and maybe previous season
            seasons_for_player = random.sample(seasons, min(2, len(seasons))) if seasons else []
            
            for season in seasons_for_player:
                # Generate stats based on player position
                stats = generate_player_stats(player.position)
                
                statistic = PlayerStatistic.objects.create(
                    player=player,
                    season=season,
                    team=player.team,
                    games_played=stats['games_played'],
                    minutes_played=stats['minutes_played'],
                    goals=stats['goals'],
                    assists=stats['assists'],
                    yellow_cards=stats['yellow_cards'],
                    red_cards=stats['red_cards'],
                    shots=stats['shots'],
                    shots_on_target=stats['shots_on_target'],
                    pass_accuracy=stats['pass_accuracy'],
                    crosses=stats['crosses'],
                    tackles=stats['tackles'],
                    interceptions=stats['interceptions'],
                    clean_sheets=stats['clean_sheets'],
                    saves=stats['saves'],
                    rating=stats['rating']
                )
                statistics_created += 1
        
        print(f"✅ Created {statistics_created} player statistics")
        
        # Create Player Transfers
        print("🔄 Creating player transfers...")
        transfers_created = 0
        
        # Create some historical transfers
        for _ in range(min(50, len(players) // 2)):  # About half the players have transfer history
            player = random.choice(players)
            
            # Generate 1-3 transfers per selected player
            num_transfers = random.randint(1, 3)
            
            current_team = player.team
            transfer_date = datetime.now() - timedelta(days=random.randint(365, 1825))  # 1-5 years ago
            
            for i in range(num_transfers):
                # Select a different team for transfer
                available_teams = [team for team in teams if team != current_team]
                if not available_teams:
                    break
                
                from_team = current_team
                to_team = random.choice(available_teams)
                
                # Generate transfer details
                transfer_type = random.choices(
                    ['permanent', 'loan', 'free_transfer'],
                    weights=[70, 20, 10]
                )[0]
                
                # Generate transfer fee (in euros)
                if transfer_type == 'free_transfer':
                    transfer_fee = Decimal('0.00')
                elif transfer_type == 'loan':
                    transfer_fee = Decimal(random.randint(100000, 2000000))  # Loan fee
                else:
                    # Permanent transfer fee based on player position and age
                    base_fee = 1000000  # 1M base
                    if player.position == 'Forward':
                        base_fee = 5000000
                    elif player.position == 'Midfielder':
                        base_fee = 3000000
                    elif player.position == 'Defender':
                        base_fee = 2000000
                    else:  # Goalkeeper
                        base_fee = 1500000
                    
                    # Age factor (younger players cost more)
                    age_factor = max(0.5, (35 - player.age) / 17)  # Players over 35 have min 0.5 factor
                    
                    transfer_fee = Decimal(base_fee * age_factor * random.uniform(0.3, 3.0))
                
                transfer = PlayerTransfer.objects.create(
                    player=player,
                    from_team=from_team,
                    to_team=to_team,
                    transfer_date=transfer_date.date(),
                    transfer_type=transfer_type,
                    transfer_fee=transfer_fee,
                    contract_length=random.randint(1, 5),  # years
                    announcement_date=transfer_date.date() - timedelta(days=random.randint(1, 30)),
                    is_confirmed=True
                )
                transfers_created += 1
                
                # Update for next transfer
                current_team = to_team
                transfer_date += timedelta(days=random.randint(365, 730))  # 1-2 years later
                
                # Don't create transfers in the future
                if transfer_date > datetime.now():
                    break
        
        print(f"✅ Created {transfers_created} player transfers")
        
        print('\n🎉 Player data seeded successfully!')
        
        # Display summary
        print(f'\n📊 Summary:')
        print(f'   Player Statistics: {PlayerStatistic.objects.count()}')
        print(f'   Player Transfers: {PlayerTransfer.objects.count()}')
        print(f'   - Permanent: {PlayerTransfer.objects.filter(transfer_type="permanent").count()}')
        print(f'   - Loans: {PlayerTransfer.objects.filter(transfer_type="loan").count()}')
        print(f'   - Free Transfers: {PlayerTransfer.objects.filter(transfer_type="free_transfer").count()}')
        
        # Calculate total transfer value
        total_transfer_value = sum(transfer.transfer_fee for transfer in PlayerTransfer.objects.all())
        print(f'   Total Transfer Value: €{total_transfer_value:,.2f}')


def generate_player_stats(position):
    """Generate realistic statistics based on player position"""
    
    # Base stats
    games_played = random.randint(15, 35)
    minutes_played = games_played * random.randint(60, 90)
    
    # Position-specific stats
    if position == 'Forward':
        goals = random.randint(8, 25)
        assists = random.randint(2, 12)
        shots = random.randint(60, 150)
        shots_on_target = int(shots * random.uniform(0.3, 0.6))
        pass_accuracy = random.uniform(70, 85)
        crosses = random.randint(5, 30)
        tackles = random.randint(10, 40)
        interceptions = random.randint(5, 25)
        clean_sheets = 0
        saves = 0
        rating = random.uniform(6.5, 8.5)
        
    elif position == 'Midfielder':
        goals = random.randint(2, 12)
        assists = random.randint(5, 18)
        shots = random.randint(30, 80)
        shots_on_target = int(shots * random.uniform(0.25, 0.5))
        pass_accuracy = random.uniform(80, 95)
        crosses = random.randint(20, 80)
        tackles = random.randint(30, 80)
        interceptions = random.randint(20, 60)
        clean_sheets = 0
        saves = 0
        rating = random.uniform(6.0, 8.0)
        
    elif position == 'Defender':
        goals = random.randint(0, 5)
        assists = random.randint(0, 8)
        shots = random.randint(5, 25)
        shots_on_target = int(shots * random.uniform(0.2, 0.4))
        pass_accuracy = random.uniform(75, 90)
        crosses = random.randint(10, 50)
        tackles = random.randint(50, 120)
        interceptions = random.randint(40, 100)
        clean_sheets = random.randint(5, 15)
        saves = 0
        rating = random.uniform(6.0, 7.8)
        
    else:  # Goalkeeper
        goals = 0
        assists = random.randint(0, 2)
        shots = 0
        shots_on_target = 0
        pass_accuracy = random.uniform(60, 80)
        crosses = 0
        tackles = random.randint(0, 5)
        interceptions = random.randint(5, 20)
        clean_sheets = random.randint(8, 20)
        saves = random.randint(50, 150)
        rating = random.uniform(6.0, 8.2)
    
    # Common stats for all positions
    yellow_cards = random.randint(0, 8)
    red_cards = random.randint(0, 2)
    
    return {
        'games_played': games_played,
        'minutes_played': minutes_played,
        'goals': goals,
        'assists': assists,
        'yellow_cards': yellow_cards,
        'red_cards': red_cards,
        'shots': shots,
        'shots_on_target': shots_on_target,
        'pass_accuracy': pass_accuracy,
        'crosses': crosses,
        'tackles': tackles,
        'interceptions': interceptions,
        'clean_sheets': clean_sheets,
        'saves': saves,
        'rating': rating
    }


if __name__ == '__main__':
    seed_player_data()
