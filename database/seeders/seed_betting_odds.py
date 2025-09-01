#!/usr/bin/env python
"""
Seeder for betting odds data - creates sample odds for testing
"""
import os
import sys
import django
import random
from decimal import Decimal

# Add the project path to the Python path
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mark_foot_backend.settings')
django.setup()

from core.models import Match
from betting_odds.models import BookmakerProvider, MatchOdds, OddsAnalysis
from betting_odds.services.odds_analyzer import OddsAnalysisService

def seed_betting_odds():
    """Seed sample betting odds data"""
    print("🎲 Starting betting odds seeding...")
    
    # Get scheduled matches for today
    from django.utils import timezone
    from datetime import timedelta
    
    scheduled_matches = Match.objects.filter(
        status='SCHEDULED',
        utc_date__gte=timezone.now(),
        utc_date__lte=timezone.now() + timedelta(days=1)
    )[:5]  # Limit to 5 matches for testing
    
    if not scheduled_matches:
        print("❌ No scheduled matches found for today")
        return
    
    print(f"📊 Found {scheduled_matches.count()} scheduled matches")
    
    # Get active bookmakers
    bookmakers = BookmakerProvider.objects.filter(is_active=True)
    if not bookmakers.exists():
        print("❌ No active bookmakers found. Run setup_bookmakers first.")
        return
    
    created_odds = 0
    
    for match in scheduled_matches:
        print(f"\n⚽ Processing: {match.home_team.name} vs {match.away_team.name}")
        
        for bookmaker in bookmakers:
            # Generate realistic odds
            # Home team slightly favored in most cases
            home_odds = round(random.uniform(1.5, 3.5), 2)
            draw_odds = round(random.uniform(3.0, 4.5), 2)
            away_odds = round(random.uniform(1.8, 4.0), 2)
            
            # Ensure proper probability distribution
            total_implied_prob = (1/home_odds + 1/draw_odds + 1/away_odds)
            if total_implied_prob < 1.0:
                # Add bookmaker margin
                margin = random.uniform(0.05, 0.12)  # 5-12% margin
                home_odds = round(home_odds * (1 + margin), 2)
                draw_odds = round(draw_odds * (1 + margin), 2)
                away_odds = round(away_odds * (1 + margin), 2)
            
            # Generate additional markets
            over_2_5 = round(random.uniform(1.6, 2.4), 2)
            under_2_5 = round(random.uniform(1.5, 2.3), 2)
            btts_yes = round(random.uniform(1.7, 2.5), 2)
            btts_no = round(random.uniform(1.4, 2.2), 2)
            
            odds_data = {
                'home_win_odds': home_odds,
                'draw_odds': draw_odds,
                'away_win_odds': away_odds,
                'total_goals_over_2_5': over_2_5,
                'total_goals_under_2_5': under_2_5,
                'both_teams_score_yes': btts_yes,
                'both_teams_score_no': btts_no,
            }
            
            # Create or update odds
            match_odds, created = MatchOdds.objects.update_or_create(
                match=match,
                bookmaker=bookmaker,
                defaults=odds_data
            )
            
            if created:
                created_odds += 1
                print(f"  ✅ Created odds for {bookmaker.name}: {home_odds}/{draw_odds}/{away_odds}")
            else:
                print(f"  🔄 Updated odds for {bookmaker.name}: {home_odds}/{draw_odds}/{away_odds}")
    
    print(f"\n📈 Created {created_odds} new odds records")
    
    # Generate analysis for matches with odds
    print("\n🤖 Generating AI analysis...")
    analyzer = OddsAnalysisService()
    
    analyzed_count = 0
    for match in scheduled_matches:
        if match.odds.exists():
            try:
                analysis = analyzer.analyze_match_odds(match)
                if analysis:
                    analyzed_count += 1
                    print(f"  ✅ Analysis generated for {match.home_team.name} vs {match.away_team.name}")
                    
                    # Print summary for verification
                    if analysis.value_bet_detected:
                        print(f"    💎 Value bet detected: {analysis.value_bet_market}")
                    print(f"    🎯 Confidence: {analysis.confidence_score}")
            except Exception as e:
                print(f"  ❌ Error analyzing {match}: {str(e)}")
    
    print(f"\n🎯 Generated analysis for {analyzed_count} matches")
    
    # Print summary
    print(f"\n🏆 Seeding completed successfully!")
    print(f"   • Matches processed: {scheduled_matches.count()}")
    print(f"   • Odds created: {created_odds}")
    print(f"   • Analyses generated: {analyzed_count}")
    print(f"   • Active bookmakers: {bookmakers.count()}")

if __name__ == "__main__":
    try:
        seed_betting_odds()
    except Exception as e:
        print(f"❌ Error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
