#!/usr/bin/env python3
"""
Analytics Data Seeder for Mark Foot Analytics System
Creates sample analytics data, user preferences, and reports.
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mark_foot_backend.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from analytics.models import (
    UserAnalyticsPreference, AnalyticsReport, TeamAnalytics,
    PlayerAnalytics, MatchAnalytics, AnalyticsDashboard
)
from core.models import Team, Player, Match, Competition
from analytics.services.report_service import AnalyticsDashboardService
import random
import uuid


def create_user_analytics_preferences():
    """Create analytics preferences for existing users"""
    print("Creating user analytics preferences...")
    
    users = User.objects.all()
    preferences_created = 0
    
    for user in users:
        # Skip if user already has preferences
        if UserAnalyticsPreference.objects.filter(user=user).exists():
            continue
            
        # Get some random teams and players as favorites
        favorite_teams = list(Team.objects.order_by('?')[:3])
        favorite_players = list(Player.objects.filter(team__isnull=False).order_by('?')[:2])
        
        preference = UserAnalyticsPreference.objects.create(
            user=user,
            report_frequency=random.choice(['weekly', 'monthly', 'never']),
            auto_generate_reports=random.choice([True, False]),
            email_reports=random.choice([True, False]),
            whatsapp_reports=random.choice([True, False]),
            enabled_widgets=[
                'team_form',
                'player_stats',
                'match_predictions',
                'league_standings',
            ] if random.choice([True, False]) else [
                'team_form',
                'match_predictions',
            ],
            widget_layout={
                'cols': 12,
                'margin': [10, 10],
                'row_height': 60,
            }
        )
        
        # Add favorite teams and players
        preference.favorite_teams.set(favorite_teams)
        preference.favorite_players.set(favorite_players)
        
        preferences_created += 1
        print(f"  Created preferences for {user.username}")
    
    print(f"✅ Created {preferences_created} user analytics preferences")
    return preferences_created


def create_team_analytics():
    """Create team analytics data"""
    print("Creating team analytics data...")
    
    teams = Team.objects.all()
    analytics_created = 0
    
    # Create analytics for different time periods
    periods = [
        (30, 'last_month'),
        (7, 'last_week'),
        (90, 'last_quarter'),
    ]
    
    for team in teams:
        for days_back, period_name in periods:
            date_to = timezone.now().date()
            date_from = date_to - timedelta(days=days_back)
            
            # Skip if analytics already exists
            if TeamAnalytics.objects.filter(
                team=team, 
                date_from=date_from, 
                date_to=date_to
            ).exists():
                continue
            
            # Generate realistic statistics
            matches_played = random.randint(5, 15) if days_back == 30 else random.randint(1, 5)
            wins = random.randint(0, matches_played)
            remaining = matches_played - wins
            draws = random.randint(0, remaining)
            losses = remaining - draws
            
            goals_for = random.randint(wins, wins * 3 + draws + losses)
            goals_against = random.randint(losses, losses * 2 + draws + wins)
            
            TeamAnalytics.objects.create(
                team=team,
                date_from=date_from,
                date_to=date_to,
                matches_played=matches_played,
                wins=wins,
                draws=draws,
                losses=losses,
                goals_for=goals_for,
                goals_against=goals_against,
                goal_difference=goals_for - goals_against,
                win_rate=(wins / matches_played * 100) if matches_played > 0 else 0,
                points_per_match=((wins * 3 + draws) / matches_played) if matches_played > 0 else 0,
                possession_avg=random.uniform(45.0, 65.0),
                passing_accuracy=random.uniform(75.0, 90.0),
                shots_per_match=random.uniform(8.0, 20.0),
                shots_on_target_ratio=random.uniform(0.25, 0.55),
                recent_form=['W', 'D', 'L'][random.randint(0, 2)] * 5,  # Random form
                home_performance={
                    'wins': random.randint(0, wins),
                    'draws': random.randint(0, draws),
                    'losses': random.randint(0, losses),
                },
                away_performance={
                    'wins': random.randint(0, wins),
                    'draws': random.randint(0, draws),
                    'losses': random.randint(0, losses),
                }
            )
            
            analytics_created += 1
    
    print(f"✅ Created {analytics_created} team analytics records")
    return analytics_created


def create_player_analytics():
    """Create player analytics data"""
    print("Creating player analytics data...")
    
    players = Player.objects.filter(team__isnull=False)[:50]  # Limit for performance
    analytics_created = 0
    
    # Create analytics for different time periods
    periods = [
        (30, 'last_month'),
        (7, 'last_week'),
    ]
    
    for player in players:
        for days_back, period_name in periods:
            date_to = timezone.now().date()
            date_from = date_to - timedelta(days=days_back)
            
            # Skip if analytics already exists
            if PlayerAnalytics.objects.filter(
                player=player, 
                date_from=date_from, 
                date_to=date_to
            ).exists():
                continue
            
            # Generate realistic statistics based on position
            appearances = random.randint(3, 10) if days_back == 30 else random.randint(1, 4)
            
            # Goals and assists vary by position
            if player.position in ['Forward', 'Striker']:
                goals = random.randint(1, appearances)
                assists = random.randint(0, appearances // 2)
            elif player.position in ['Midfielder']:
                goals = random.randint(0, appearances // 2)
                assists = random.randint(0, appearances)
            else:  # Defenders, Goalkeepers
                goals = random.randint(0, 1)
                assists = random.randint(0, appearances // 3)
            
            minutes_played = appearances * random.randint(60, 90)
            
            PlayerAnalytics.objects.create(
                player=player,
                date_from=date_from,
                date_to=date_to,
                appearances=appearances,
                goals=goals,
                assists=assists,
                yellow_cards=random.randint(0, 2),
                red_cards=random.randint(0, 1),
                minutes_played=minutes_played,
                goals_per_90=(goals / minutes_played * 90) if minutes_played > 0 else 0,
                assists_per_90=(assists / minutes_played * 90) if minutes_played > 0 else 0,
                pass_completion_rate=random.uniform(75.0, 95.0),
                expected_goals=random.uniform(0.0, goals + 0.5),
                expected_assists=random.uniform(0.0, assists + 0.5),
                progressive_passes=random.randint(10, 50),
                key_passes=random.randint(5, 25),
                estimated_market_value=Decimal(random.uniform(100000, 50000000)),
                market_value_trend=random.choice(['rising', 'stable', 'declining']),
                recent_performances=[
                    f"vs Team {i}: {random.choice(['Good', 'Average', 'Excellent'])}"
                    for i in range(1, 6)
                ],
                consistency_score=random.uniform(6.0, 9.0)
            )
            
            analytics_created += 1
    
    print(f"✅ Created {analytics_created} player analytics records")
    return analytics_created


def create_match_analytics():
    """Create match analytics data"""
    print("Creating match analytics data...")
    
    matches = Match.objects.filter(status='FINISHED').order_by('-utc_date')[:20]
    analytics_created = 0
    
    for match in matches:
        # Skip if analytics already exists
        if MatchAnalytics.objects.filter(match=match).exists():
            continue
        
        MatchAnalytics.objects.create(
            match=match,
            home_team_form_score=random.uniform(6.0, 9.0),
            away_team_form_score=random.uniform(6.0, 9.0),
            head_to_head_stats={
                'last_5_meetings': {
                    'home_wins': random.randint(0, 3),
                    'draws': random.randint(0, 2),
                    'away_wins': random.randint(0, 3),
                },
                'avg_goals_per_game': random.uniform(1.5, 3.5),
            },
            possession_home=random.uniform(35.0, 65.0),
            possession_away=random.uniform(35.0, 65.0),
            shots_home=random.randint(8, 25),
            shots_away=random.randint(8, 25),
            shots_on_target_home=random.randint(3, 12),
            shots_on_target_away=random.randint(3, 12),
            expected_goals_home=random.uniform(0.5, 3.0),
            expected_goals_away=random.uniform(0.5, 3.0),
            passing_accuracy_home=random.uniform(75.0, 90.0),
            passing_accuracy_away=random.uniform(75.0, 90.0),
            performance_ratings={
                'home_defense': random.uniform(6.0, 9.0),
                'home_midfield': random.uniform(6.0, 9.0),
                'home_attack': random.uniform(6.0, 9.0),
                'away_defense': random.uniform(6.0, 9.0),
                'away_midfield': random.uniform(6.0, 9.0),
                'away_attack': random.uniform(6.0, 9.0),
            },
            key_moments=[
                f"Goal at {random.randint(1, 90)}' - {match.home_team.name}",
                f"Yellow card at {random.randint(1, 90)}' - {match.away_team.name}",
                f"Substitution at {random.randint(45, 90)}'",
            ],
            tactical_analysis={
                'formation_home': random.choice(['4-4-2', '4-3-3', '3-5-2']),
                'formation_away': random.choice(['4-4-2', '4-3-3', '3-5-2']),
                'key_battles': ['Midfield control', 'Wing play', 'Set pieces'],
            },
            predicted_result=f"{random.randint(0, 3)}-{random.randint(0, 3)}",
            actual_result=f"{match.home_team_score or 0}-{match.away_team_score or 0}",
            prediction_accuracy=random.uniform(60.0, 95.0),
        )
        
        analytics_created += 1
    
    print(f"✅ Created {analytics_created} match analytics records")
    return analytics_created


def create_sample_reports():
    """Create sample analytics reports"""
    print("Creating sample analytics reports...")
    
    users = User.objects.all()[:5]  # Limit to first 5 users
    teams = Team.objects.all()[:10]
    players = Player.objects.filter(team__isnull=False)[:10]
    
    reports_created = 0
    
    for user in users:
        # Create team reports
        for team in teams[:3]:  # 3 team reports per user
            date_to = timezone.now().date()
            date_from = date_to - timedelta(days=30)
            
            report = AnalyticsReport.objects.create(
                user=user,
                title=f"Team Analysis: {team.name}",
                report_type='team_analysis',
                format=random.choice(['pdf', 'excel']),
                status='completed',
                date_from=date_from,
                date_to=date_to,
                parameters={
                    'team_id': team.id,
                    'team_name': team.name,
                },
                content_data={
                    'team_info': {
                        'name': team.name,
                        'founded': team.founded,
                        'venue': team.venue,
                    },
                    'statistics': {
                        'total_matches': random.randint(8, 15),
                        'wins': random.randint(3, 8),
                        'draws': random.randint(1, 4),
                        'losses': random.randint(1, 5),
                        'win_rate': random.uniform(40.0, 80.0),
                    }
                },
                generation_time=random.uniform(2.0, 8.0),
                file_size=random.randint(150000, 500000),
                download_count=random.randint(0, 5),
            )
            reports_created += 1
        
        # Create player reports
        for player in players[:2]:  # 2 player reports per user
            date_to = timezone.now().date()
            date_from = date_to - timedelta(days=30)
            
            report = AnalyticsReport.objects.create(
                user=user,
                title=f"Player Analysis: {player.name}",
                report_type='player_analysis',
                format=random.choice(['pdf', 'excel']),
                status='completed',
                date_from=date_from,
                date_to=date_to,
                parameters={
                    'player_id': player.id,
                    'player_name': player.name,
                },
                content_data={
                    'player_info': {
                        'name': player.name,
                        'position': player.position,
                        'team': player.team.name if player.team else 'Free Agent',
                    },
                    'statistics': {
                        'goals': random.randint(0, 8),
                        'assists': random.randint(0, 5),
                        'appearances': random.randint(5, 12),
                    }
                },
                generation_time=random.uniform(1.5, 6.0),
                file_size=random.randint(100000, 400000),
                download_count=random.randint(0, 3),
            )
            reports_created += 1
    
    print(f"✅ Created {reports_created} sample reports")
    return reports_created


def create_analytics_dashboards():
    """Create analytics dashboards for users"""
    print("Creating analytics dashboards...")
    
    users = User.objects.all()
    dashboards_created = 0
    
    dashboard_service = AnalyticsDashboardService()
    
    for user in users:
        # Skip if user already has a default dashboard
        if AnalyticsDashboard.objects.filter(user=user, is_default=True).exists():
            continue
        
        dashboard = dashboard_service.create_default_dashboard(user)
        dashboards_created += 1
        print(f"  Created dashboard for {user.username}")
    
    print(f"✅ Created {dashboards_created} analytics dashboards")
    return dashboards_created


def main():
    """Main seeder function"""
    print("🌱 Starting Analytics Data Seeding...")
    print("=" * 50)
    
    try:
        # Create all analytics data
        preferences_count = create_user_analytics_preferences()
        team_analytics_count = create_team_analytics()
        player_analytics_count = create_player_analytics()
        match_analytics_count = create_match_analytics()
        reports_count = create_sample_reports()
        dashboards_count = create_analytics_dashboards()
        
        print("=" * 50)
        print("🎉 Analytics Data Seeding Completed Successfully!")
        print(f"📊 Summary:")
        print(f"   • User Preferences: {preferences_count}")
        print(f"   • Team Analytics: {team_analytics_count}")
        print(f"   • Player Analytics: {player_analytics_count}")
        print(f"   • Match Analytics: {match_analytics_count}")
        print(f"   • Sample Reports: {reports_count}")
        print(f"   • Dashboards: {dashboards_count}")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
