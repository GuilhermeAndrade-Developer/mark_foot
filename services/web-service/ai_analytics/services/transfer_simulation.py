import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone

from core.models import Player, PlayerStatistics, Season, Team, Competition
from ai_analytics.models import TransferSimulation
from .base_service import BaseAIService, DataPreparationMixin, ModelEvaluationMixin, AIModelFactory

logger = logging.getLogger(__name__)


class TransferSimulationService(BaseAIService, DataPreparationMixin, ModelEvaluationMixin):
    """Service for simulating player transfers and their impact"""
    
    def __init__(self):
        super().__init__("transfer_simulation", "1.0.0")
        self.transfer_success_model = None
        self.performance_impact_model = None
        self.team_chemistry_model = None
        self.scaler = None
        
    def collect_transfer_simulation_data(self, seasons: int = 5) -> pd.DataFrame:
        """Collect data for transfer simulation analysis"""
        try:
            cutoff_date = timezone.now() - timedelta(days=365 * seasons)
            
            # Get player statistics across multiple seasons to identify transfers
            stats = PlayerStatistics.objects.filter(
                season__start_date__gte=cutoff_date
            ).select_related('player', 'season', 'competition').prefetch_related('player__team')
            
            data = []
            
            # Group by player to identify potential transfers
            player_seasons = {}
            for stat in stats:
                player_id = stat.player.id
                if player_id not in player_seasons:
                    player_seasons[player_id] = []
                player_seasons[player_id].append(stat)
            
            # Analyze each player's career for transfer patterns
            for player_id, season_stats in player_seasons.items():
                # Sort by season
                season_stats.sort(key=lambda x: x.season.start_date)
                
                # Look for team changes (simulated transfers)
                for i in range(1, len(season_stats)):
                    current_stat = season_stats[i]
                    previous_stat = season_stats[i-1]
                    
                    # Check if there's a team change or significant performance change
                    has_team_change = current_stat.player.team != previous_stat.player.team
                    
                    transfer_data = self._analyze_transfer_scenario(
                        previous_stat, current_stat, has_team_change
                    )
                    
                    if transfer_data:
                        data.append(transfer_data)
            
            df = pd.DataFrame(data)
            logger.info(f"Collected transfer simulation data for {len(df)} transfer scenarios")
            return df
            
        except Exception as e:
            logger.error(f"Error collecting transfer simulation data: {str(e)}")
            return pd.DataFrame()
    
    def _analyze_transfer_scenario(self, previous_stat: PlayerStatistics, 
                                 current_stat: PlayerStatistics, 
                                 has_team_change: bool) -> Optional[Dict[str, Any]]:
        """Analyze a transfer scenario between two seasons"""
        try:
            player = current_stat.player
            
            # Calculate pre-transfer metrics
            pre_metrics = self._calculate_season_metrics(previous_stat)
            
            # Calculate post-transfer metrics
            post_metrics = self._calculate_season_metrics(current_stat)
            
            # Calculate transfer characteristics
            transfer_characteristics = self._calculate_transfer_characteristics(
                previous_stat, current_stat, has_team_change
            )
            
            # Calculate success metrics
            success_metrics = self._calculate_transfer_success(pre_metrics, post_metrics)
            
            transfer_data = {
                'player_id': player.id,
                'player_name': player.name,
                'age_at_transfer': player.age or 25,
                'position_category': player.position_category or 'MF',
                'nationality': player.nationality or 'Unknown',
                
                # Transfer characteristics
                'has_team_change': 1 if has_team_change else 0,
                'league_change': transfer_characteristics['league_change'],
                'level_change': transfer_characteristics['level_change'],
                'competition_change': transfer_characteristics['competition_change'],
                
                # Pre-transfer performance
                'pre_rating': pre_metrics['rating'],
                'pre_goals_per_game': pre_metrics['goals_per_game'],
                'pre_assists_per_game': pre_metrics['assists_per_game'],
                'pre_minutes_per_game': pre_metrics['minutes_per_game'],
                'pre_consistency': pre_metrics['consistency'],
                
                # Post-transfer performance
                'post_rating': post_metrics['rating'],
                'post_goals_per_game': post_metrics['goals_per_game'],
                'post_assists_per_game': post_metrics['assists_per_game'],
                'post_minutes_per_game': post_metrics['minutes_per_game'],
                'post_consistency': post_metrics['consistency'],
                
                # Success metrics
                'rating_improvement': success_metrics['rating_improvement'],
                'goal_improvement': success_metrics['goal_improvement'],
                'playing_time_improvement': success_metrics['playing_time_improvement'],
                'overall_success_score': success_metrics['overall_success_score'],
                
                # Transfer context
                'season_from': previous_stat.season.id,
                'season_to': current_stat.season.id,
                'transfer_success': 1 if success_metrics['overall_success_score'] > 0.1 else 0
            }
            
            return transfer_data
            
        except Exception as e:
            logger.error(f"Error analyzing transfer scenario: {str(e)}")
            return None
    
    def _calculate_season_metrics(self, stats: PlayerStatistics) -> Dict[str, float]:
        """Calculate key metrics for a season"""
        appearances = max(stats.appearances, 1)
        
        return {
            'rating': float(stats.rating) if stats.rating else 7.0,
            'goals_per_game': stats.goals / appearances,
            'assists_per_game': stats.assists / appearances,
            'minutes_per_game': stats.minutes_played / appearances,
            'consistency': 1.0 if stats.starts / appearances > 0.7 else 0.5,
            'total_contributions': stats.goals + stats.assists
        }
    
    def _calculate_transfer_characteristics(self, previous_stat: PlayerStatistics, 
                                          current_stat: PlayerStatistics, 
                                          has_team_change: bool) -> Dict[str, float]:
        """Calculate characteristics of the transfer"""
        
        # League change (simplified - assume all are same league for now)
        league_change = 0.0
        
        # Competition level change
        competition_change = 0.0
        if previous_stat.competition and current_stat.competition:
            competition_change = 1.0 if previous_stat.competition != current_stat.competition else 0.0
        
        # Performance level change (based on team performance)
        pre_team_performance = self._estimate_team_performance(previous_stat)
        post_team_performance = self._estimate_team_performance(current_stat)
        level_change = post_team_performance - pre_team_performance
        
        return {
            'league_change': league_change,
            'competition_change': competition_change,
            'level_change': level_change
        }
    
    def _estimate_team_performance(self, stats: PlayerStatistics) -> float:
        """Estimate team performance level (simplified)"""
        # In real implementation, this would use actual team standings/rankings
        # For now, use average team player ratings as proxy
        try:
            if stats.player.team:
                team_stats = PlayerStatistics.objects.filter(
                    player__team=stats.player.team,
                    season=stats.season
                ).exclude(player=stats.player)
                
                if team_stats.exists():
                    avg_rating = team_stats.aggregate(Avg('rating'))['rating__avg'] or 7.0
                    return float(avg_rating)
            
            return 7.0  # Default average performance
            
        except Exception:
            return 7.0
    
    def _calculate_transfer_success(self, pre_metrics: Dict[str, float], 
                                  post_metrics: Dict[str, float]) -> Dict[str, float]:
        """Calculate transfer success metrics"""
        
        rating_improvement = post_metrics['rating'] - pre_metrics['rating']
        goal_improvement = post_metrics['goals_per_game'] - pre_metrics['goals_per_game']
        assist_improvement = post_metrics['assists_per_game'] - pre_metrics['assists_per_game']
        playing_time_improvement = post_metrics['minutes_per_game'] - pre_metrics['minutes_per_game']
        
        # Calculate overall success score (weighted combination)
        overall_success_score = (
            rating_improvement * 0.4 +
            goal_improvement * 2.0 +  # Goals weighted heavily
            assist_improvement * 1.5 + # Assists weighted moderately
            (playing_time_improvement / 90) * 0.3  # Playing time normalized
        )
        
        return {
            'rating_improvement': rating_improvement,
            'goal_improvement': goal_improvement,
            'assist_improvement': assist_improvement,
            'playing_time_improvement': playing_time_improvement,
            'overall_success_score': overall_success_score
        }
    
    def train_transfer_models(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Train transfer simulation models"""
        results = {}
        
        if data.empty:
            return {'error': 'No training data available'}
        
        # Define feature sets for different models
        transfer_success_features = [
            'age_at_transfer', 'league_change', 'level_change', 'competition_change',
            'pre_rating', 'pre_goals_per_game', 'pre_assists_per_game',
            'pre_minutes_per_game', 'pre_consistency'
        ]
        
        performance_impact_features = [
            'age_at_transfer', 'level_change', 'pre_rating', 'pre_goals_per_game',
            'pre_assists_per_game', 'has_team_change'
        ]
        
        # Prepare data
        X_success = data[transfer_success_features].fillna(0)
        y_success = data['transfer_success']
        
        X_performance = data[performance_impact_features].fillna(0)
        y_performance = data['overall_success_score']
        
        # Handle categorical variables
        data_encoded = pd.get_dummies(data, columns=['position_category'], prefix='pos')
        position_cols = [col for col in data_encoded.columns if col.startswith('pos_')]
        
        # Add position features
        X_success_encoded = pd.concat([X_success, data_encoded[position_cols]], axis=1).fillna(0)
        X_performance_encoded = pd.concat([X_performance, data_encoded[position_cols]], axis=1).fillna(0)
        
        try:
            from sklearn.preprocessing import StandardScaler
            from sklearn.model_selection import train_test_split
            
            # Initialize scaler
            self.scaler = StandardScaler()
            
            # Train transfer success model (classification)
            self.transfer_success_model = AIModelFactory.create_classifier('random_forest', n_estimators=100, random_state=42)
            
            X_success_scaled = self.scaler.fit_transform(X_success_encoded)
            self.transfer_success_model.fit(X_success_scaled, y_success)
            
            # Evaluate transfer success model
            y_success_pred = self.transfer_success_model.predict(X_success_scaled)
            success_metrics = self.calculate_classification_metrics(y_success.values, y_success_pred)
            
            results['transfer_success_model'] = {
                'accuracy': success_metrics['accuracy'],
                'precision': success_metrics['precision'],
                'recall': success_metrics['recall'],
                'f1': success_metrics['f1'],
                'feature_importance': dict(zip(
                    list(transfer_success_features) + position_cols,
                    self.transfer_success_model.feature_importances_
                ))
            }
            
            # Train performance impact model (regression)
            self.performance_impact_model = AIModelFactory.create_regressor('random_forest', n_estimators=100, random_state=42)
            
            X_performance_scaled = self.scaler.fit_transform(X_performance_encoded)
            self.performance_impact_model.fit(X_performance_scaled, y_performance)
            
            # Evaluate performance impact model
            y_performance_pred = self.performance_impact_model.predict(X_performance_scaled)
            performance_metrics = self.calculate_regression_metrics(y_performance.values, y_performance_pred)
            
            results['performance_impact_model'] = {
                'rmse': performance_metrics['rmse'],
                'mae': performance_metrics['mae'],
                'r2': performance_metrics['r2'],
                'feature_importance': dict(zip(
                    list(performance_impact_features) + position_cols,
                    self.performance_impact_model.feature_importances_
                ))
            }
            
            # Analyze transfer patterns
            transfer_patterns = self._analyze_transfer_patterns(data)
            results['transfer_patterns'] = transfer_patterns
            
            logger.info(f"Transfer simulation models trained - Success accuracy: {success_metrics['accuracy']:.3f}, Performance R²: {performance_metrics['r2']:.3f}")
            
        except Exception as e:
            logger.error(f"Error training transfer models: {str(e)}")
            results['error'] = str(e)
        
        self.is_trained = True
        return results
    
    def _analyze_transfer_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze patterns in transfer data"""
        patterns = {}
        
        # Success rate by age group
        age_groups = pd.cut(data['age_at_transfer'], bins=[0, 21, 25, 29, 40], labels=['Young', 'Prime', 'Mature', 'Veteran'])
        success_by_age = data.groupby(age_groups)['transfer_success'].mean().to_dict()
        patterns['success_by_age_group'] = success_by_age
        
        # Success rate by position
        success_by_position = data.groupby('position_category')['transfer_success'].mean().to_dict()
        patterns['success_by_position'] = success_by_position
        
        # Average performance improvement by transfer type
        team_change_impact = data.groupby('has_team_change')['overall_success_score'].mean().to_dict()
        patterns['team_change_impact'] = {
            'no_change': team_change_impact.get(0, 0),
            'team_change': team_change_impact.get(1, 0)
        }
        
        # Risk factors for transfer failure
        failed_transfers = data[data['transfer_success'] == 0]
        risk_factors = {
            'avg_age': float(failed_transfers['age_at_transfer'].mean()),
            'avg_pre_rating': float(failed_transfers['pre_rating'].mean()),
            'common_positions': failed_transfers['position_category'].value_counts().head(3).to_dict()
        }
        patterns['failure_risk_factors'] = risk_factors
        
        return patterns
    
    def simulate_transfer(self, player: Player, target_team: Optional[Team] = None, 
                         transfer_type: str = 'permanent') -> Dict[str, Any]:
        """Simulate a transfer for a specific player"""
        if not self.is_trained:
            raise ValueError("Models not trained. Call train_transfer_models() first.")
        
        try:
            # Get player's current statistics
            current_stats = PlayerStatistics.objects.filter(
                player=player
            ).order_by('-season__start_date').first()
            
            if not current_stats:
                logger.warning(f"No statistics found for player {player.name}")
                return self._default_transfer_simulation(player)
            
            # Calculate current performance metrics
            current_metrics = self._calculate_season_metrics(current_stats)
            
            # Simulate transfer characteristics
            transfer_characteristics = self._simulate_transfer_characteristics(
                player, current_stats, target_team
            )
            
            # Prepare features for prediction
            features = self._prepare_transfer_features(
                player, current_metrics, transfer_characteristics
            )
            
            # Make predictions
            simulation_results = {}
            
            if self.transfer_success_model and self.scaler:
                # Predict transfer success probability
                features_scaled = self.scaler.transform(features)
                success_prob = self.transfer_success_model.predict_proba(features_scaled)[0][1]
                success_prediction = self.transfer_success_model.predict(features_scaled)[0]
                
                simulation_results['success_probability'] = float(success_prob)
                simulation_results['predicted_success'] = bool(success_prediction)
            
            if self.performance_impact_model:
                # Predict performance impact
                features_scaled = self.scaler.transform(features)
                performance_impact = self.performance_impact_model.predict(features_scaled)[0]
                
                simulation_results['performance_impact'] = float(performance_impact)
                simulation_results['expected_rating_change'] = performance_impact * 0.4  # Approximate rating change
            
            # Generate detailed analysis
            detailed_analysis = self._generate_transfer_analysis(
                player, current_metrics, transfer_characteristics, simulation_results
            )
            
            # Calculate risks and benefits
            risks_benefits = self._calculate_transfer_risks_benefits(
                player, transfer_characteristics, simulation_results
            )
            
            # Generate recommendations
            recommendations = self._generate_transfer_recommendations(
                player, simulation_results, transfer_characteristics
            )
            
            result = {
                'player_id': player.id,
                'player_name': player.name,
                'target_team': target_team.name if target_team else 'Not specified',
                'transfer_type': transfer_type,
                'current_performance': current_metrics,
                'transfer_characteristics': transfer_characteristics,
                'simulation_results': simulation_results,
                'detailed_analysis': detailed_analysis,
                'risks_and_benefits': risks_benefits,
                'recommendations': recommendations,
                'simulation_date': timezone.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error simulating transfer for player {player.name}: {str(e)}")
            return self._default_transfer_simulation(player)
    
    def _simulate_transfer_characteristics(self, player: Player, current_stats: PlayerStatistics, 
                                         target_team: Optional[Team]) -> Dict[str, float]:
        """Simulate characteristics of the proposed transfer"""
        
        # Current team performance
        current_team_performance = self._estimate_team_performance(current_stats)
        
        # Target team performance (if specified)
        if target_team:
            # Get target team's recent performance
            target_team_stats = PlayerStatistics.objects.filter(
                player__team=target_team
            ).order_by('-season__start_date')[:20]  # Recent players
            
            if target_team_stats.exists():
                target_team_performance = target_team_stats.aggregate(Avg('rating'))['rating__avg'] or 7.0
            else:
                target_team_performance = 7.0
        else:
            # Assume average team performance for general simulation
            target_team_performance = 7.0
        
        return {
            'has_team_change': 1.0 if target_team and target_team != player.team else 0.0,
            'league_change': 0.0,  # Simplified - assume same league
            'level_change': float(target_team_performance - current_team_performance),
            'competition_change': 0.0,  # Simplified
            'target_team_performance': target_team_performance
        }
    
    def _prepare_transfer_features(self, player: Player, current_metrics: Dict[str, float], 
                                 transfer_characteristics: Dict[str, float]) -> pd.DataFrame:
        """Prepare features for transfer prediction"""
        features = {
            'age_at_transfer': player.age or 25,
            'league_change': transfer_characteristics['league_change'],
            'level_change': transfer_characteristics['level_change'],
            'competition_change': transfer_characteristics['competition_change'],
            'pre_rating': current_metrics['rating'],
            'pre_goals_per_game': current_metrics['goals_per_game'],
            'pre_assists_per_game': current_metrics['assists_per_game'],
            'pre_minutes_per_game': current_metrics['minutes_per_game'],
            'pre_consistency': current_metrics['consistency'],
            'has_team_change': transfer_characteristics['has_team_change'],
            
            # Position encoding
            'pos_DF': 1 if player.position_category == 'DF' else 0,
            'pos_FW': 1 if player.position_category == 'FW' else 0,
            'pos_GK': 1 if player.position_category == 'GK' else 0,
            'pos_MF': 1 if player.position_category == 'MF' else 0,
        }
        
        return pd.DataFrame([features])
    
    def _generate_transfer_analysis(self, player: Player, current_metrics: Dict[str, float], 
                                  transfer_characteristics: Dict[str, float], 
                                  simulation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed transfer analysis"""
        
        analysis = {
            'player_profile': {
                'current_rating': current_metrics['rating'],
                'goal_involvement': current_metrics['goals_per_game'] + current_metrics['assists_per_game'],
                'playing_time': current_metrics['minutes_per_game'],
                'consistency': current_metrics['consistency']
            },
            'transfer_context': {
                'level_change': transfer_characteristics['level_change'],
                'team_change': transfer_characteristics['has_team_change'] > 0,
                'target_level': transfer_characteristics.get('target_team_performance', 7.0)
            },
            'predicted_outcomes': {
                'success_likelihood': simulation_results.get('success_probability', 0.5),
                'performance_change': simulation_results.get('performance_impact', 0.0),
                'rating_projection': current_metrics['rating'] + simulation_results.get('expected_rating_change', 0.0)
            }
        }
        
        # Add contextual insights
        if transfer_characteristics['level_change'] > 0.5:
            analysis['insights'] = ['Moving to higher quality team', 'May face increased competition for playing time']
        elif transfer_characteristics['level_change'] < -0.5:
            analysis['insights'] = ['Moving to lower quality team', 'Likely to have more impact and playing time']
        else:
            analysis['insights'] = ['Similar level transfer', 'Change of environment may be key factor']
        
        return analysis
    
    def _calculate_transfer_risks_benefits(self, player: Player, transfer_characteristics: Dict[str, float], 
                                         simulation_results: Dict[str, Any]) -> Dict[str, List[str]]:
        """Calculate risks and benefits of the transfer"""
        
        risks = []
        benefits = []
        
        # Age-related factors
        age = player.age or 25
        if age > 30:
            risks.append("Advanced age may limit adaptation to new environment")
        elif age < 22:
            risks.append("Young player may struggle with pressure of transfer")
            benefits.append("High potential for development in new environment")
        
        # Level change factors
        level_change = transfer_characteristics['level_change']
        if level_change > 0.5:
            benefits.append("Opportunity to play at higher level")
            risks.append("Increased competition for starting position")
        elif level_change < -0.5:
            benefits.append("Likely to be key player in new team")
            risks.append("May not fulfill potential at lower level")
        
        # Performance factors
        success_prob = simulation_results.get('success_probability', 0.5)
        if success_prob > 0.7:
            benefits.append("High probability of successful adaptation")
        elif success_prob < 0.4:
            risks.append("Low probability of successful adaptation")
        
        performance_impact = simulation_results.get('performance_impact', 0.0)
        if performance_impact > 0.2:
            benefits.append("Expected significant performance improvement")
        elif performance_impact < -0.2:
            risks.append("Risk of performance decline")
        
        # Position-specific factors
        position = player.position_category
        if position == 'FW':
            benefits.append("Strikers typically adapt well to new tactical systems")
        elif position == 'GK':
            risks.append("Goalkeepers face unique adaptation challenges")
        
        return {
            'risks': risks[:5],  # Top 5 risks
            'benefits': benefits[:5]  # Top 5 benefits
        }
    
    def _generate_transfer_recommendations(self, player: Player, simulation_results: Dict[str, Any], 
                                         transfer_characteristics: Dict[str, float]) -> List[str]:
        """Generate transfer recommendations"""
        recommendations = []
        
        success_prob = simulation_results.get('success_probability', 0.5)
        performance_impact = simulation_results.get('performance_impact', 0.0)
        
        # Overall recommendation
        if success_prob > 0.7 and performance_impact > 0.1:
            recommendations.append("Highly recommended transfer - high success probability and positive impact expected")
        elif success_prob > 0.6:
            recommendations.append("Recommended transfer - good probability of success")
        elif success_prob < 0.4:
            recommendations.append("Not recommended - low probability of successful adaptation")
        else:
            recommendations.append("Neutral recommendation - consider other factors")
        
        # Specific recommendations
        level_change = transfer_characteristics['level_change']
        if level_change > 0.5:
            recommendations.append("Ensure gradual integration into higher-level team")
            recommendations.append("Focus on physical and tactical preparation")
        elif level_change < -0.5:
            recommendations.append("Leverage opportunity to be key player immediately")
        
        # Age-specific recommendations
        age = player.age or 25
        if age < 23:
            recommendations.append("Prioritize development opportunities over immediate success")
        elif age > 29:
            recommendations.append("Consider short-term contract to minimize risk")
        
        # Performance-specific recommendations
        if performance_impact < 0:
            recommendations.append("Address potential adaptation challenges with support staff")
        
        return recommendations[:5]  # Top 5 recommendations
    
    def _default_transfer_simulation(self, player: Player) -> Dict[str, Any]:
        """Return default transfer simulation when models are not available"""
        age = player.age or 25
        position = player.position_category or 'MF'
        
        # Simple age and position-based assessment
        if age < 25:
            success_prob = 0.7
            impact = 0.2
        elif age < 30:
            success_prob = 0.6
            impact = 0.0
        else:
            success_prob = 0.4
            impact = -0.1
        
        return {
            'player_id': player.id,
            'player_name': player.name,
            'simulation_results': {
                'success_probability': success_prob,
                'performance_impact': impact,
                'predicted_success': success_prob > 0.5
            },
            'recommendations': [
                f"Age {age} player in {position} position",
                "Simulation based on simplified model (limited data available)",
                "Consider detailed scouting analysis"
            ],
            'note': 'Simulation based on default model (limited data available)'
        }
    
    def save_transfer_simulation(self, player: Player, simulation_data: Dict[str, Any], 
                               target_team: Optional[Team] = None, season: Optional[Season] = None) -> TransferSimulation:
        """Save transfer simulation results to database"""
        try:
            if not season:
                season = Season.objects.filter(
                    start_date__lte=timezone.now().date(),
                    end_date__gte=timezone.now().date()
                ).first() or Season.objects.order_by('-start_date').first()
            
            simulation_results = simulation_data['simulation_results']
            
            transfer_simulation = TransferSimulation.objects.create(
                player=player,
                target_team=target_team,
                transfer_type=simulation_data.get('transfer_type', 'permanent'),
                success_probability=simulation_results.get('success_probability', 0.5),
                predicted_impact=simulation_results.get('performance_impact', 0.0),
                risk_factors=simulation_data.get('risks_and_benefits', {}).get('risks', []),
                expected_benefits=simulation_data.get('risks_and_benefits', {}).get('benefits', []),
                recommendations=simulation_data.get('recommendations', []),
                simulation_details=simulation_data,
                model_version=self.version,
                simulation_date=timezone.now(),
                season=season
            )
            
            logger.info(f"Saved transfer simulation for {player.name}: {simulation_results.get('success_probability', 0.5):.2f} success probability")
            return transfer_simulation
            
        except Exception as e:
            logger.error(f"Error saving transfer simulation: {str(e)}")
            raise
