import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone

from core.models import Player, Team, Season, PlayerStatistics
from ai_analytics.models import PlayerRecommendation
from .base_service import BaseAIService, DataPreparationMixin, ModelEvaluationMixin, FeatureEngineeringMixin, AIModelFactory

logger = logging.getLogger(__name__)


class PlayerRecommendationService(BaseAIService, DataPreparationMixin, ModelEvaluationMixin, FeatureEngineeringMixin):
    """Service for recommending players based on performance and team needs"""
    
    def __init__(self):
        super().__init__("player_recommendation", "1.0.0")
        self.similarity_model = None
        self.performance_model = None
        
    def collect_player_data(self, seasons: int = 2) -> pd.DataFrame:
        """Collect player performance data"""
        try:
            # Get recent seasons
            cutoff_date = timezone.now() - timedelta(days=365 * seasons)
            
            # Get player statistics
            stats = PlayerStatistics.objects.filter(
                season__start_date__gte=cutoff_date
            ).select_related('player', 'season', 'competition').prefetch_related(
                'player__team'
            )
            
            data = []
            for stat in stats:
                player = stat.player
                
                # Calculate per-game metrics
                appearances = max(stat.appearances, 1)
                minutes_per_game = stat.minutes_played / appearances
                goals_per_game = stat.goals / appearances
                assists_per_game = stat.assists / appearances
                
                # Performance score calculation
                performance_score = self._calculate_performance_score(stat)
                
                player_data = {
                    'player_id': player.id,
                    'player_name': player.name,
                    'team_id': player.team.id if player.team else None,
                    'team_name': player.team.name if player.team else 'Free Agent',
                    'position': player.position or 'Unknown',
                    'position_category': player.position_category or 'Unknown',
                    'age': player.age or 25,
                    'nationality': player.nationality or 'Unknown',
                    'season_id': stat.season.id,
                    'competition_id': stat.competition.id if stat.competition else None,
                    
                    # Basic stats
                    'appearances': stat.appearances,
                    'minutes_played': stat.minutes_played,
                    'starts': stat.starts,
                    'goals': stat.goals,
                    'assists': stat.assists,
                    'yellow_cards': stat.yellow_cards,
                    'red_cards': stat.red_cards,
                    
                    # Per game metrics
                    'minutes_per_game': minutes_per_game,
                    'goals_per_game': goals_per_game,
                    'assists_per_game': assists_per_game,
                    'goal_involvement_per_game': goals_per_game + assists_per_game,
                    'cards_per_game': (stat.yellow_cards + stat.red_cards * 2) / appearances,
                    
                    # Goalkeeper specific
                    'clean_sheets': stat.clean_sheets,
                    'saves': stat.saves,
                    'goals_conceded': stat.goals_conceded,
                    'clean_sheet_ratio': stat.clean_sheets / appearances if stat.clean_sheets > 0 else 0,
                    
                    # Performance metrics
                    'rating': float(stat.rating) if stat.rating else 7.0,
                    'performance_score': performance_score,
                    
                    # Derived features
                    'is_young_talent': 1 if player.age and player.age <= 23 else 0,
                    'is_experienced': 1 if player.age and player.age >= 30 else 0,
                    'is_regular_starter': 1 if stat.starts / appearances > 0.7 else 0,
                    'is_goal_threat': 1 if goals_per_game > 0.3 else 0,
                    'is_creative': 1 if assists_per_game > 0.2 else 0,
                    'is_disciplined': 1 if (stat.yellow_cards + stat.red_cards * 2) / appearances < 0.3 else 0,
                }
                
                data.append(player_data)
            
            df = pd.DataFrame(data)
            logger.info(f"Collected data for {len(df)} player-season combinations")
            return df
            
        except Exception as e:
            logger.error(f"Error collecting player data: {str(e)}")
            return pd.DataFrame()
    
    def _calculate_performance_score(self, stats: PlayerStatistics) -> float:
        """Calculate overall performance score for a player"""
        try:
            appearances = max(stats.appearances, 1)
            
            # Base score from rating
            base_score = float(stats.rating) if stats.rating else 7.0
            
            # Bonus for goals and assists
            goal_bonus = (stats.goals / appearances) * 10
            assist_bonus = (stats.assists / appearances) * 8
            
            # Penalty for cards
            card_penalty = ((stats.yellow_cards + stats.red_cards * 2) / appearances) * 5
            
            # Bonus for minutes played (consistency)
            minutes_bonus = min((stats.minutes_played / (appearances * 90)) * 2, 2)
            
            # Goalkeeper specific adjustments
            if stats.clean_sheets > 0:  # Likely a goalkeeper
                gk_bonus = (stats.clean_sheets / appearances) * 5
                goal_bonus = 0  # Remove goal bonus for GK
                base_score += gk_bonus
            
            performance_score = base_score + goal_bonus + assist_bonus + minutes_bonus - card_penalty
            
            # Normalize to 0-10 scale
            return max(0, min(10, performance_score))
            
        except Exception as e:
            logger.error(f"Error calculating performance score: {str(e)}")
            return 7.0
    
    def find_similar_players(self, target_player: Player, position_filter: bool = True, top_k: int = 10) -> List[Dict[str, Any]]:
        """Find players similar to target player"""
        try:
            # Get target player's recent performance
            target_stats = PlayerStatistics.objects.filter(
                player=target_player
            ).order_by('-season__start_date').first()
            
            if not target_stats:
                logger.warning(f"No statistics found for player {target_player.name}")
                return []
            
            # Collect data for comparison
            df = self.collect_player_data(seasons=2)
            
            if df.empty:
                return []
            
            # Filter by position if requested
            if position_filter and target_player.position_category:
                df = df[df['position_category'] == target_player.position_category]
            
            # Remove target player from comparison
            df = df[df['player_id'] != target_player.id]
            
            if df.empty:
                return []
            
            # Features for similarity calculation
            similarity_features = [
                'goals_per_game', 'assists_per_game', 'minutes_per_game',
                'cards_per_game', 'performance_score', 'age',
                'is_young_talent', 'is_experienced', 'is_regular_starter',
                'is_goal_threat', 'is_creative', 'is_disciplined'
            ]
            
            # Add goalkeeper features if applicable
            if target_player.position_category == 'GK':
                similarity_features.extend(['clean_sheet_ratio', 'saves', 'goals_conceded'])
            
            # Prepare target features
            target_features = {
                'goals_per_game': target_stats.goals / max(target_stats.appearances, 1),
                'assists_per_game': target_stats.assists / max(target_stats.appearances, 1),
                'minutes_per_game': target_stats.minutes_played / max(target_stats.appearances, 1),
                'cards_per_game': (target_stats.yellow_cards + target_stats.red_cards * 2) / max(target_stats.appearances, 1),
                'performance_score': self._calculate_performance_score(target_stats),
                'age': target_player.age or 25,
                'is_young_talent': 1 if target_player.age and target_player.age <= 23 else 0,
                'is_experienced': 1 if target_player.age and target_player.age >= 30 else 0,
                'is_regular_starter': 1 if target_stats.starts / max(target_stats.appearances, 1) > 0.7 else 0,
                'is_goal_threat': 1 if (target_stats.goals / max(target_stats.appearances, 1)) > 0.3 else 0,
                'is_creative': 1 if (target_stats.assists / max(target_stats.appearances, 1)) > 0.2 else 0,
                'is_disciplined': 1 if (target_stats.yellow_cards + target_stats.red_cards * 2) / max(target_stats.appearances, 1) < 0.3 else 0,
            }
            
            if target_player.position_category == 'GK':
                target_features.update({
                    'clean_sheet_ratio': target_stats.clean_sheets / max(target_stats.appearances, 1),
                    'saves': target_stats.saves,
                    'goals_conceded': target_stats.goals_conceded
                })
            
            # Calculate similarity scores
            similarities = []
            for _, row in df.iterrows():
                similarity_score = self._calculate_player_similarity(target_features, row, similarity_features)
                
                similarities.append({
                    'player_id': row['player_id'],
                    'player_name': row['player_name'],
                    'team_name': row['team_name'],
                    'position': row['position'],
                    'age': row['age'],
                    'nationality': row['nationality'],
                    'similarity_score': similarity_score,
                    'performance_score': row['performance_score'],
                    'goals_per_game': row['goals_per_game'],
                    'assists_per_game': row['assists_per_game'],
                    'rating': row['rating']
                })
            
            # Sort by similarity and return top K
            similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Error finding similar players: {str(e)}")
            return []
    
    def _calculate_player_similarity(self, target_features: Dict, candidate_row: pd.Series, feature_names: List[str]) -> float:
        """Calculate similarity score between two players"""
        try:
            # Calculate cosine similarity for numerical features
            target_vector = np.array([target_features.get(feat, 0) for feat in feature_names])
            candidate_vector = np.array([candidate_row.get(feat, 0) for feat in feature_names])
            
            # Handle zero vectors
            target_norm = np.linalg.norm(target_vector)
            candidate_norm = np.linalg.norm(candidate_vector)
            
            if target_norm == 0 or candidate_norm == 0:
                return 0.0
            
            cosine_sim = np.dot(target_vector, candidate_vector) / (target_norm * candidate_norm)
            
            # Normalize to 0-1 scale
            similarity = (cosine_sim + 1) / 2
            
            return similarity
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def recommend_players_for_team(self, team: Team, position: str = None, budget_limit: float = None, top_k: int = 10) -> List[Dict[str, Any]]:
        """Recommend players for a specific team based on needs"""
        try:
            # Collect player data
            df = self.collect_player_data(seasons=2)
            
            if df.empty:
                return []
            
            # Filter by position if specified
            if position:
                df = df[df['position_category'] == position]
            
            # Remove current team players
            df = df[df['team_id'] != team.id]
            
            # Analyze team's current squad
            team_analysis = self._analyze_team_needs(team)
            
            # Score players based on team needs
            recommendations = []
            for _, row in df.iterrows():
                score = self._calculate_team_fit_score(row, team_analysis, team)
                
                # Apply budget filter if specified
                if budget_limit is not None:
                    # Estimate market value (simplified)
                    estimated_value = self._estimate_market_value(row)
                    if estimated_value > budget_limit:
                        continue
                
                recommendations.append({
                    'player_id': row['player_id'],
                    'player_name': row['player_name'],
                    'current_team': row['team_name'],
                    'position': row['position'],
                    'age': row['age'],
                    'nationality': row['nationality'],
                    'fit_score': score,
                    'performance_score': row['performance_score'],
                    'goals_per_game': row['goals_per_game'],
                    'assists_per_game': row['assists_per_game'],
                    'rating': row['rating'],
                    'estimated_value': self._estimate_market_value(row) if budget_limit is not None else None,
                    'recommendation_reasons': self._get_recommendation_reasons(row, team_analysis)
                })
            
            # Sort by fit score and return top K
            recommendations.sort(key=lambda x: x['fit_score'], reverse=True)
            return recommendations[:top_k]
            
        except Exception as e:
            logger.error(f"Error recommending players: {str(e)}")
            return []
    
    def _analyze_team_needs(self, team: Team) -> Dict[str, Any]:
        """Analyze team's current squad and identify needs"""
        try:
            # Get current squad
            current_players = Player.objects.filter(team=team)
            
            # Position distribution
            position_counts = {}
            for player in current_players:
                pos = player.position_category or 'Unknown'
                position_counts[pos] = position_counts.get(pos, 0) + 1
            
            # Age distribution
            ages = [p.age for p in current_players if p.age]
            avg_age = sum(ages) / len(ages) if ages else 25
            
            # Performance analysis
            recent_stats = PlayerStatistics.objects.filter(
                player__team=team
            ).order_by('-season__start_date')[:20]  # Recent stats for squad
            
            avg_performance = sum(self._calculate_performance_score(stat) for stat in recent_stats) / len(recent_stats) if recent_stats else 7.0
            
            # Identify weaknesses
            needs = {
                'positions_needed': [],
                'age_needs': 'balanced',
                'performance_level': avg_performance,
                'priority_attributes': []
            }
            
            # Position needs (simplified)
            ideal_formation = {'GK': 2, 'DF': 8, 'MF': 8, 'FW': 6}
            for pos, ideal_count in ideal_formation.items():
                current_count = position_counts.get(pos, 0)
                if current_count < ideal_count * 0.7:  # Less than 70% of ideal
                    needs['positions_needed'].append(pos)
            
            # Age needs
            if avg_age > 29:
                needs['age_needs'] = 'young'
            elif avg_age < 24:
                needs['age_needs'] = 'experienced'
            
            # Performance needs
            if avg_performance < 7.0:
                needs['priority_attributes'].extend(['performance_score', 'rating'])
            
            return needs
            
        except Exception as e:
            logger.error(f"Error analyzing team needs: {str(e)}")
            return {'positions_needed': [], 'age_needs': 'balanced', 'performance_level': 7.0, 'priority_attributes': []}
    
    def _calculate_team_fit_score(self, player_row: pd.Series, team_needs: Dict, team: Team) -> float:
        """Calculate how well a player fits team needs"""
        try:
            score = 0.0
            
            # Base score from performance
            score += player_row['performance_score'] * 0.4
            
            # Position need bonus
            if player_row['position_category'] in team_needs['positions_needed']:
                score += 2.0
            
            # Age fit bonus
            age_needs = team_needs['age_needs']
            player_age = player_row['age']
            
            if age_needs == 'young' and player_age <= 25:
                score += 1.0
            elif age_needs == 'experienced' and player_age >= 28:
                score += 1.0
            elif age_needs == 'balanced' and 23 <= player_age <= 30:
                score += 0.5
            
            # Performance level fit
            team_performance = team_needs['performance_level']
            player_performance = player_row['performance_score']
            
            if player_performance > team_performance:
                score += (player_performance - team_performance) * 0.5
            
            # Special attributes bonus
            for attr in team_needs.get('priority_attributes', []):
                if attr in player_row and player_row[attr] > 7.0:
                    score += 0.5
            
            # Normalize to 0-10 scale
            return max(0, min(10, score))
            
        except Exception as e:
            logger.error(f"Error calculating team fit: {str(e)}")
            return 0.0
    
    def _estimate_market_value(self, player_row: pd.Series) -> float:
        """Estimate player market value (simplified)"""
        try:
            # Base value from performance and age
            base_value = player_row['performance_score'] * 1000000  # 1M per performance point
            
            # Age factor
            age = player_row['age']
            if age <= 23:
                age_multiplier = 1.5  # Young talent bonus
            elif age <= 27:
                age_multiplier = 1.2  # Peak age
            elif age <= 30:
                age_multiplier = 1.0  # Stable
            else:
                age_multiplier = 0.7  # Declining value
            
            # Position factor
            position_multipliers = {'GK': 0.8, 'DF': 0.9, 'MF': 1.1, 'FW': 1.3}
            pos_multiplier = position_multipliers.get(player_row['position_category'], 1.0)
            
            # Goals/assists factor
            offensive_factor = 1 + (player_row['goals_per_game'] + player_row['assists_per_game']) * 0.5
            
            estimated_value = base_value * age_multiplier * pos_multiplier * offensive_factor
            
            # Cap at reasonable limits
            return max(100000, min(200000000, estimated_value))  # 100K to 200M
            
        except Exception as e:
            logger.error(f"Error estimating market value: {str(e)}")
            return 1000000  # Default 1M
    
    def _get_recommendation_reasons(self, player_row: pd.Series, team_needs: Dict) -> List[str]:
        """Generate reasons for player recommendation"""
        reasons = []
        
        try:
            # Performance-based reasons
            if player_row['performance_score'] > 8.0:
                reasons.append("High overall performance rating")
            
            if player_row['goals_per_game'] > 0.5:
                reasons.append("Excellent goal-scoring record")
            
            if player_row['assists_per_game'] > 0.3:
                reasons.append("Strong assist provider")
            
            # Position-based reasons
            if player_row['position_category'] in team_needs['positions_needed']:
                reasons.append(f"Fills positional need ({player_row['position_category']})")
            
            # Age-based reasons
            age_needs = team_needs['age_needs']
            player_age = player_row['age']
            
            if age_needs == 'young' and player_age <= 23:
                reasons.append("Young talent with potential")
            elif age_needs == 'experienced' and player_age >= 28:
                reasons.append("Experienced player with leadership qualities")
            
            # Special attributes
            if player_row['is_regular_starter']:
                reasons.append("Proven starter with consistent playing time")
            
            if player_row['is_disciplined']:
                reasons.append("Good disciplinary record")
            
            if player_row['rating'] > 7.5:
                reasons.append("High average match rating")
            
            return reasons[:5]  # Limit to top 5 reasons
            
        except Exception as e:
            logger.error(f"Error generating recommendation reasons: {str(e)}")
            return ["Statistical analysis indicates good fit"]
    
    def save_recommendation(self, player: Player, team: Team, recommendation_data: Dict[str, Any], recommendation_type: str = 'SIGNING') -> PlayerRecommendation:
        """Save recommendation to database"""
        try:
            # Get current season
            current_season = Season.objects.filter(
                start_date__lte=timezone.now().date(),
                end_date__gte=timezone.now().date()
            ).first()
            
            if not current_season:
                current_season = Season.objects.order_by('-start_date').first()
            
            recommendation = PlayerRecommendation.objects.create(
                player=player,
                team=team,
                recommendation_type=recommendation_type,
                score=recommendation_data.get('fit_score', 0),
                reasons=recommendation_data.get('recommendation_reasons', []),
                attributes_analysis={
                    'performance_score': recommendation_data.get('performance_score', 0),
                    'goals_per_game': recommendation_data.get('goals_per_game', 0),
                    'assists_per_game': recommendation_data.get('assists_per_game', 0),
                    'age': recommendation_data.get('age', 0),
                    'estimated_value': recommendation_data.get('estimated_value', 0)
                },
                comparison_players=recommendation_data.get('similar_players', []),
                model_version=self.version,
                season=current_season
            )
            
            logger.info(f"Saved recommendation: {player.name} -> {team.name}")
            return recommendation
            
        except Exception as e:
            logger.error(f"Error saving recommendation: {str(e)}")
            raise
