import numpy as np
import logging
from datetime import datetime, timedelta
from django.db.models import Avg, Q, Count, Max
from django.utils import timezone
from ..models import MatchOdds, OddsAnalysis, MarketAlert
from core.models import Match, Team

logger = logging.getLogger(__name__)

class OddsAnalysisService:
    def __init__(self):
        self.value_bet_threshold = 0.05  # 5% edge minimum for value bet detection
        self.significant_movement_threshold = 0.15  # 15% movement threshold
    
    def analyze_match_odds(self, match):
        """Comprehensive analysis of odds for a specific match"""
        try:
            # Get all odds for this match
            match_odds = MatchOdds.objects.filter(match=match)
            
            if not match_odds.exists():
                logger.warning(f"No odds found for match {match}")
                return None
            
            # Calculate average odds across bookmakers
            avg_home_odds = match_odds.aggregate(Avg('home_win_odds'))['home_win_odds__avg']
            avg_draw_odds = match_odds.aggregate(Avg('draw_odds'))['draw_odds__avg']
            avg_away_odds = match_odds.aggregate(Avg('away_win_odds'))['away_win_odds__avg']
            
            # Find best odds for each market
            best_home_odds = match_odds.aggregate(Max('home_win_odds'))['home_win_odds__max']
            best_draw_odds = match_odds.aggregate(Max('draw_odds'))['draw_odds__max']
            best_away_odds = match_odds.aggregate(Max('away_win_odds'))['away_win_odds__max']
            
            # Detect value bets
            value_bet_info = self._detect_value_bets(match, match_odds)
            
            # Generate analysis summary
            analysis_summary = self._generate_analysis_summary(
                match, avg_home_odds, avg_draw_odds, avg_away_odds, value_bet_info
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(match_odds)
            
            # Save or update analysis
            analysis, created = OddsAnalysis.objects.update_or_create(
                match=match,
                defaults={
                    'average_home_odds': avg_home_odds,
                    'average_draw_odds': avg_draw_odds,
                    'average_away_odds': avg_away_odds,
                    'best_home_odds': best_home_odds,
                    'best_draw_odds': best_draw_odds,
                    'best_away_odds': best_away_odds,
                    'value_bet_detected': value_bet_info['detected'],
                    'value_bet_market': value_bet_info['market'],
                    'confidence_score': confidence_score,
                    'analysis_summary': analysis_summary
                }
            )
            
            # Check for market alerts
            self._check_market_alerts(match, match_odds)
            
            logger.info(f"Analysis completed for {match}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing odds for {match}: {str(e)}")
            return None
    
    def _detect_value_bets(self, match, match_odds):
        """Detect potential value betting opportunities"""
        try:
            # Get historical performance data for teams
            home_team_stats = self._get_team_recent_performance(match.home_team)
            away_team_stats = self._get_team_recent_performance(match.away_team)
            
            # Calculate our implied probabilities based on team stats
            our_probabilities = self._calculate_our_probabilities(
                home_team_stats, away_team_stats
            )
            
            # Compare with market probabilities
            market_probs = self._get_average_market_probabilities(match_odds)
            
            value_opportunities = []
            
            # Check each market for value
            markets = ['home', 'draw', 'away']
            for market in markets:
                our_prob = our_probabilities.get(market, 0)
                market_prob = market_probs.get(market, 0)
                
                if our_prob > market_prob + self.value_bet_threshold:
                    edge = our_prob - market_prob
                    value_opportunities.append({
                        'market': market,
                        'edge': edge,
                        'our_probability': our_prob,
                        'market_probability': market_prob
                    })
            
            if value_opportunities:
                # Return the best value opportunity
                best_value = max(value_opportunities, key=lambda x: x['edge'])
                return {
                    'detected': True,
                    'market': best_value['market'],
                    'edge': best_value['edge']
                }
            
            return {'detected': False, 'market': None}
            
        except Exception as e:
            logger.error(f"Error detecting value bets for {match}: {str(e)}")
            return {'detected': False, 'market': None}
    
    def _get_team_recent_performance(self, team, matches_count=10):
        """Get recent performance statistics for a team"""
        recent_matches = Match.objects.filter(
            Q(home_team=team) | Q(away_team=team),
            status='FINISHED',
            utc_date__gte=timezone.now() - timedelta(days=90)
        ).order_by('-utc_date')[:matches_count]
        
        stats = {
            'matches_played': recent_matches.count(),
            'wins': 0,
            'draws': 0,
            'losses': 0,
            'goals_for': 0,
            'goals_against': 0,
            'home_wins': 0,
            'away_wins': 0
        }
        
        for match in recent_matches:
            if match.home_team == team:
                # Team played at home
                if match.home_team_score > match.away_team_score:
                    stats['wins'] += 1
                    stats['home_wins'] += 1
                elif match.home_team_score == match.away_team_score:
                    stats['draws'] += 1
                else:
                    stats['losses'] += 1
                
                stats['goals_for'] += match.home_team_score or 0
                stats['goals_against'] += match.away_team_score or 0
            
            else:
                # Team played away
                if match.away_team_score > match.home_team_score:
                    stats['wins'] += 1
                    stats['away_wins'] += 1
                elif match.away_team_score == match.home_team_score:
                    stats['draws'] += 1
                else:
                    stats['losses'] += 1
                
                stats['goals_for'] += match.away_team_score or 0
                stats['goals_against'] += match.home_team_score or 0
        
        # Calculate win percentage
        if stats['matches_played'] > 0:
            stats['win_percentage'] = stats['wins'] / stats['matches_played']
            stats['draw_percentage'] = stats['draws'] / stats['matches_played']
            stats['loss_percentage'] = stats['losses'] / stats['matches_played']
            stats['avg_goals_for'] = stats['goals_for'] / stats['matches_played']
            stats['avg_goals_against'] = stats['goals_against'] / stats['matches_played']
        
        return stats
    
    def _calculate_our_probabilities(self, home_stats, away_stats):
        """Calculate our probability estimates based on team statistics"""
        # Simple model - could be made more sophisticated
        home_strength = home_stats.get('win_percentage', 0.33) + 0.1  # Home advantage
        away_strength = away_stats.get('win_percentage', 0.33)
        
        # Normalize to account for draw probability
        total_strength = home_strength + away_strength
        
        if total_strength > 0:
            home_prob = home_strength / (total_strength + 0.25)  # 0.25 for draw probability
            away_prob = away_strength / (total_strength + 0.25)
            draw_prob = 0.25 / (total_strength + 0.25)
        else:
            # Default probabilities if no data
            home_prob = 0.4
            draw_prob = 0.3
            away_prob = 0.3
        
        return {
            'home': home_prob,
            'draw': draw_prob,
            'away': away_prob
        }
    
    def _get_average_market_probabilities(self, match_odds):
        """Calculate average implied probabilities from market odds"""
        total_home_prob = 0
        total_draw_prob = 0
        total_away_prob = 0
        count = 0
        
        for odds in match_odds:
            if odds.home_win_odds and odds.draw_odds and odds.away_win_odds:
                home_prob = 1 / odds.home_win_odds
                draw_prob = 1 / odds.draw_odds
                away_prob = 1 / odds.away_win_odds
                
                # Remove bookmaker margin
                total_prob = home_prob + draw_prob + away_prob
                if total_prob > 1:
                    home_prob = home_prob / total_prob
                    draw_prob = draw_prob / total_prob
                    away_prob = away_prob / total_prob
                
                total_home_prob += home_prob
                total_draw_prob += draw_prob
                total_away_prob += away_prob
                count += 1
        
        if count > 0:
            return {
                'home': total_home_prob / count,
                'draw': total_draw_prob / count,
                'away': total_away_prob / count
            }
        
        return {'home': 0.33, 'draw': 0.33, 'away': 0.33}
    
    def _calculate_confidence_score(self, match_odds):
        """Calculate confidence score based on odds consistency and data quality"""
        if not match_odds.exists():
            return 0.0
        
        # Check number of bookmakers
        bookmaker_count = match_odds.count()
        bookmaker_score = min(bookmaker_count / 5.0, 1.0)  # Max score at 5+ bookmakers
        
        # Check odds consistency (lower variance = higher confidence)
        home_odds_list = [odds.home_win_odds for odds in match_odds if odds.home_win_odds]
        if len(home_odds_list) > 1:
            variance = np.var(home_odds_list)
            consistency_score = max(0, 1 - variance / 2.0)  # Normalized variance score
        else:
            consistency_score = 0.5
        
        # Overall confidence score
        confidence = (bookmaker_score * 0.4 + consistency_score * 0.6)
        return round(confidence, 2)
    
    def _generate_analysis_summary(self, match, avg_home_odds, avg_draw_odds, avg_away_odds, value_bet_info):
        """Generate human-readable analysis summary"""
        try:
            # Convert odds to probabilities
            home_prob = 1 / avg_home_odds
            draw_prob = 1 / avg_draw_odds
            away_prob = 1 / avg_away_odds
            
            # Remove bookmaker margin
            total_prob = home_prob + draw_prob + away_prob
            home_prob_clean = (home_prob / total_prob) * 100
            draw_prob_clean = (draw_prob / total_prob) * 100
            away_prob_clean = (away_prob / total_prob) * 100
            
            # Determine favorite
            if home_prob_clean > away_prob_clean:
                favorite = match.home_team.name
                favorite_prob = home_prob_clean
            else:
                favorite = match.away_team.name
                favorite_prob = away_prob_clean
            
            summary = f"""🎲 **Análise de Odds: {match.home_team.name} vs {match.away_team.name}**

📊 **Probabilidades do Mercado:**
• {match.home_team.name}: {home_prob_clean:.1f}%
• Empate: {draw_prob_clean:.1f}%
• {match.away_team.name}: {away_prob_clean:.1f}%

🏆 **Favorito:** {favorite} ({favorite_prob:.1f}%)

💰 **Melhores Odds:**
• Casa: {avg_home_odds:.2f}
• Empate: {avg_draw_odds:.2f}
• Visitante: {avg_away_odds:.2f}"""
            
            if value_bet_info['detected']:
                summary += f"\n\n💎 **Value Bet Detectado:** {value_bet_info['market']} com edge de {value_bet_info.get('edge', 0)*100:.1f}%"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating analysis summary: {str(e)}")
            return "Análise indisponível no momento."
    
    def _check_market_alerts(self, match, match_odds):
        """Check for significant market movements and create alerts"""
        for odds in match_odds:
            # Check recent movements
            recent_movements = odds.movements.filter(
                timestamp__gte=timezone.now() - timedelta(hours=24)
            )
            
            for movement in recent_movements:
                if abs(movement.movement_percentage) >= self.significant_movement_threshold * 100:
                    # Create alert for significant movement
                    MarketAlert.objects.get_or_create(
                        match=match,
                        alert_type='steam_move' if movement.movement_percentage < 0 else 'odds_rise',
                        market_type=movement.market_type,
                        defaults={
                            'description': f"Movimento significativo: {movement.old_odds:.2f} → {movement.new_odds:.2f} ({movement.movement_percentage:+.1f}%)",
                            'old_odds': movement.old_odds,
                            'new_odds': movement.new_odds
                        }
                    )
    
    def analyze_all_upcoming_matches(self):
        """Analyze odds for all upcoming matches"""
        upcoming_matches = Match.objects.filter(
            utc_date__gte=timezone.now(),
            utc_date__lte=timezone.now() + timedelta(days=7),
            status='SCHEDULED'
        ).filter(odds__isnull=False).distinct()
        
        analyzed_count = 0
        for match in upcoming_matches:
            try:
                self.analyze_match_odds(match)
                analyzed_count += 1
            except Exception as e:
                logger.error(f"Error analyzing match {match}: {str(e)}")
        
        logger.info(f"Analyzed {analyzed_count} matches")
        return analyzed_count
    
    def get_value_bets_summary(self, user_is_premium=False):
        """Get summary of current value betting opportunities"""
        if not user_is_premium:
            return "🔒 Análise de value bets disponível apenas para usuários Premium"
        
        recent_analyses = OddsAnalysis.objects.filter(
            value_bet_detected=True,
            match__match_date__gte=timezone.now(),
            updated_at__gte=timezone.now() - timedelta(hours=24)
        ).select_related('match', 'match__home_team', 'match__away_team')[:5]
        
        if not recent_analyses:
            return "💎 Nenhuma oportunidade de value bet detectada no momento."
        
        summary = "💎 **Value Bets Detectados:**\n\n"
        for analysis in recent_analyses:
            match = analysis.match
            summary += f"⚽ {match.home_team.name} vs {match.away_team.name}\n"
            summary += f"📈 Mercado: {analysis.value_bet_market}\n"
            summary += f"🎯 Confiança: {analysis.confidence_score}/1.0\n\n"
        
        return summary
