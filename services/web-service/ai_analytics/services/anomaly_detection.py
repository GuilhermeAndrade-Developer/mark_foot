import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from django.db.models import Q, Count, Avg, Max, Min
from django.utils import timezone

from core.models import Player, PlayerStatistics, Season, Team, Match
from ai_analytics.models import AnomalyDetection
from .base_service import BaseAIService, DataPreparationMixin, ModelEvaluationMixin, AIModelFactory

logger = logging.getLogger(__name__)


class AnomalyDetectionService(BaseAIService, DataPreparationMixin, ModelEvaluationMixin):
    """Service for detecting anomalies in player and team performance"""
    
    def __init__(self):
        super().__init__("anomaly_detection", "1.0.0")
        self.performance_model = None
        self.behavioral_model = None
        self.team_model = None
        self.scaler = None
        
    def collect_anomaly_detection_data(self, seasons: int = 3) -> pd.DataFrame:
        """Collect data for anomaly detection analysis"""
        try:
            cutoff_date = timezone.now() - timedelta(days=365 * seasons)
            
            # Get player statistics and match data
            stats = PlayerStatistics.objects.filter(
                season__start_date__gte=cutoff_date
            ).select_related('player', 'season', 'competition').prefetch_related('player__team')
            
            data = []
            for stat in stats:
                player = stat.player
                
                # Calculate performance metrics
                performance_metrics = self._calculate_performance_metrics(stat)
                
                # Calculate behavioral metrics
                behavioral_metrics = self._calculate_behavioral_metrics(stat)
                
                # Calculate contextual metrics
                contextual_metrics = self._calculate_contextual_metrics(player, stat)
                
                player_data = {
                    'player_id': player.id,
                    'player_name': player.name,
                    'age': player.age or 25,
                    'position_category': player.position_category or 'MF',
                    'team_id': player.team.id if player.team else None,
                    'season_id': stat.season.id,
                    'competition_id': stat.competition.id if stat.competition else None,
                    
                    # Basic stats
                    'appearances': stat.appearances,
                    'starts': stat.starts,
                    'minutes_played': stat.minutes_played,
                    'goals': stat.goals,
                    'assists': stat.assists,
                    'rating': float(stat.rating) if stat.rating else 7.0,
                    
                    # Performance metrics
                    **performance_metrics,
                    
                    # Behavioral metrics
                    **behavioral_metrics,
                    
                    # Contextual metrics
                    **contextual_metrics
                }
                
                data.append(player_data)
            
            df = pd.DataFrame(data)
            logger.info(f"Collected anomaly detection data for {len(df)} player-season combinations")
            return df
            
        except Exception as e:
            logger.error(f"Error collecting anomaly detection data: {str(e)}")
            return pd.DataFrame()
    
    def _calculate_performance_metrics(self, stats: PlayerStatistics) -> Dict[str, float]:
        """Calculate performance metrics for anomaly detection"""
        appearances = max(stats.appearances, 1)
        minutes = max(stats.minutes_played, 1)
        
        return {
            # Rate statistics (per game)
            'goals_per_game': stats.goals / appearances,
            'assists_per_game': stats.assists / appearances,
            'minutes_per_game': minutes / appearances,
            'goals_per_90': (stats.goals / minutes) * 90 if minutes > 0 else 0,
            'assists_per_90': (stats.assists / minutes) * 90 if minutes > 0 else 0,
            
            # Derived metrics
            'goal_involvement_per_game': (stats.goals + stats.assists) / appearances,
            'start_percentage': stats.starts / appearances if appearances > 0 else 0,
            'rating_score': float(stats.rating) if stats.rating else 7.0,
            
            # Performance consistency (using rating as proxy)
            'performance_variance': abs(float(stats.rating) - 7.0) if stats.rating else 0,
            'is_regular_starter': 1 if stats.starts / appearances > 0.7 else 0,
            'high_output_player': 1 if (stats.goals + stats.assists) / appearances > 0.5 else 0
        }
    
    def _calculate_behavioral_metrics(self, stats: PlayerStatistics) -> Dict[str, float]:
        """Calculate behavioral metrics that might indicate anomalies"""
        appearances = max(stats.appearances, 1)
        
        # Simulated disciplinary and behavioral metrics
        # In real implementation, these would come from actual match data
        
        # Discipline metrics (simulated based on position and rating)
        position = stats.player.position_category or 'MF'
        rating = float(stats.rating) if stats.rating else 7.0
        
        # Simulate yellow/red cards based on position and style
        if position == 'DF':
            base_yellows = 0.3 + (8 - rating) * 0.1
        elif position == 'MF':
            base_yellows = 0.2 + (8 - rating) * 0.08
        elif position == 'FW':
            base_yellows = 0.15 + (8 - rating) * 0.06
        else:  # GK
            base_yellows = 0.05 + (8 - rating) * 0.02
        
        yellow_cards = max(0, base_yellows * appearances + np.random.normal(0, 0.5))
        red_cards = max(0, yellow_cards * 0.1 + np.random.normal(0, 0.1))
        
        # Injury patterns (simulated)
        injury_risk = max(0, 0.1 + (stats.minutes_played / 3000) + np.random.normal(0, 0.05))
        
        return {
            'yellow_cards': yellow_cards,
            'red_cards': red_cards,
            'cards_per_game': (yellow_cards + red_cards) / appearances,
            'estimated_injury_risk': injury_risk,
            'discipline_score': max(0, 10 - yellow_cards * 2 - red_cards * 5),
            'workload_minutes': stats.minutes_played,
            'workload_intensity': stats.minutes_played / (appearances * 90) if appearances > 0 else 0
        }
    
    def _calculate_contextual_metrics(self, player: Player, stats: PlayerStatistics) -> Dict[str, float]:
        """Calculate contextual metrics for anomaly detection"""
        # Team context
        team_context = self._get_team_context(player, stats)
        
        # Historical context (compare to player's own history)
        historical_context = self._get_historical_context(player, stats)
        
        # League/competition context
        competition_context = self._get_competition_context(stats)
        
        return {
            **team_context,
            **historical_context,
            **competition_context
        }
    
    def _get_team_context(self, player: Player, stats: PlayerStatistics) -> Dict[str, float]:
        """Get team-related context metrics"""
        if not player.team:
            return {
                'team_performance_rating': 7.0,
                'team_relative_performance': 1.0,
                'is_key_player': 0
            }
        
        # Get team's average performance this season
        team_stats = PlayerStatistics.objects.filter(
            player__team=player.team,
            season=stats.season
        ).exclude(player=player)
        
        if team_stats.exists():
            team_avg_rating = team_stats.aggregate(Avg('rating'))['rating__avg'] or 7.0
            player_relative_performance = (float(stats.rating) if stats.rating else 7.0) / team_avg_rating
            
            # Determine if player is key (top 3 in minutes or contributions)
            team_players = team_stats.count()
            is_key = 1 if stats.minutes_played > team_stats.aggregate(Avg('minutes_played'))['minutes_played__avg'] else 0
        else:
            team_avg_rating = 7.0
            player_relative_performance = 1.0
            is_key = 1
        
        return {
            'team_performance_rating': team_avg_rating,
            'team_relative_performance': player_relative_performance,
            'is_key_player': is_key
        }
    
    def _get_historical_context(self, player: Player, stats: PlayerStatistics) -> Dict[str, float]:
        """Get player's historical performance context"""
        # Get player's previous seasons
        previous_stats = PlayerStatistics.objects.filter(
            player=player,
            season__start_date__lt=stats.season.start_date
        ).order_by('-season__start_date')[:3]  # Last 3 seasons
        
        if not previous_stats.exists():
            return {
                'historical_avg_rating': 7.0,
                'rating_change_from_historical': 0.0,
                'goal_change_from_historical': 0.0,
                'minutes_change_from_historical': 0.0,
                'career_progression': 0.0
            }
        
        # Calculate historical averages
        historical_data = {
            'rating': [float(s.rating) if s.rating else 7.0 for s in previous_stats],
            'goals_per_game': [s.goals / max(s.appearances, 1) for s in previous_stats],
            'minutes_per_game': [s.minutes_played / max(s.appearances, 1) for s in previous_stats]
        }
        
        historical_avg_rating = np.mean(historical_data['rating'])
        historical_avg_goals = np.mean(historical_data['goals_per_game'])
        historical_avg_minutes = np.mean(historical_data['minutes_per_game'])
        
        # Current season compared to historical
        current_rating = float(stats.rating) if stats.rating else 7.0
        current_goals_per_game = stats.goals / max(stats.appearances, 1)
        current_minutes_per_game = stats.minutes_played / max(stats.appearances, 1)
        
        # Career progression (trending up/down)
        if len(historical_data['rating']) >= 2:
            career_progression = (historical_data['rating'][-1] - historical_data['rating'][0]) / len(historical_data['rating'])
        else:
            career_progression = 0.0
        
        return {
            'historical_avg_rating': historical_avg_rating,
            'rating_change_from_historical': current_rating - historical_avg_rating,
            'goal_change_from_historical': current_goals_per_game - historical_avg_goals,
            'minutes_change_from_historical': current_minutes_per_game - historical_avg_minutes,
            'career_progression': career_progression
        }
    
    def _get_competition_context(self, stats: PlayerStatistics) -> Dict[str, float]:
        """Get competition-level context"""
        if not stats.competition:
            return {
                'competition_avg_rating': 7.0,
                'competition_relative_performance': 1.0,
                'competition_goal_rate': 0.3
            }
        
        # Get competition averages
        competition_stats = PlayerStatistics.objects.filter(
            competition=stats.competition,
            season=stats.season
        ).exclude(player=stats.player)
        
        if competition_stats.exists():
            comp_avg_rating = competition_stats.aggregate(Avg('rating'))['rating__avg'] or 7.0
            comp_avg_goals = competition_stats.aggregate(Avg('goals'))['goals__avg'] or 0
            comp_avg_appearances = competition_stats.aggregate(Avg('appearances'))['appearances__avg'] or 1
            
            comp_goal_rate = comp_avg_goals / comp_avg_appearances
            player_rating = float(stats.rating) if stats.rating else 7.0
            competition_relative = player_rating / comp_avg_rating
        else:
            comp_avg_rating = 7.0
            competition_relative = 1.0
            comp_goal_rate = 0.3
        
        return {
            'competition_avg_rating': comp_avg_rating,
            'competition_relative_performance': competition_relative,
            'competition_goal_rate': comp_goal_rate
        }
    
    def train_anomaly_models(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Train anomaly detection models"""
        results = {}
        
        if data.empty:
            return {'error': 'No training data available'}
        
        # Define feature sets for different types of anomaly detection
        performance_features = [
            'goals_per_game', 'assists_per_game', 'minutes_per_game',
            'goal_involvement_per_game', 'rating_score', 'performance_variance',
            'team_relative_performance', 'rating_change_from_historical'
        ]
        
        behavioral_features = [
            'cards_per_game', 'discipline_score', 'workload_minutes',
            'workload_intensity', 'estimated_injury_risk'
        ]
        
        contextual_features = [
            'competition_relative_performance', 'career_progression',
            'goal_change_from_historical', 'minutes_change_from_historical'
        ]
        
        # Prepare data
        X_performance = data[performance_features].fillna(0)
        X_behavioral = data[behavioral_features].fillna(0)
        X_contextual = data[contextual_features].fillna(0)
        
        try:
            from sklearn.preprocessing import StandardScaler
            from sklearn.ensemble import IsolationForest
            from sklearn.svm import OneClassSVM
            
            self.scaler = StandardScaler()
            
            # Train performance anomaly model
            X_perf_scaled = self.scaler.fit_transform(X_performance)
            self.performance_model = IsolationForest(
                contamination=0.1,  # Expect 10% anomalies
                random_state=42,
                n_estimators=100
            )
            perf_anomalies = self.performance_model.fit_predict(X_perf_scaled)
            perf_scores = self.performance_model.score_samples(X_perf_scaled)
            
            # Train behavioral anomaly model
            X_behav_scaled = self.scaler.fit_transform(X_behavioral)
            self.behavioral_model = IsolationForest(
                contamination=0.05,  # Expect 5% behavioral anomalies
                random_state=42,
                n_estimators=100
            )
            behav_anomalies = self.behavioral_model.fit_predict(X_behav_scaled)
            behav_scores = self.behavioral_model.score_samples(X_behav_scaled)
            
            # Train contextual anomaly model (team/competition context)
            X_context_scaled = self.scaler.fit_transform(X_contextual)
            self.team_model = OneClassSVM(
                kernel='rbf',
                gamma='scale',
                nu=0.1  # Expect 10% contextual anomalies
            )
            context_anomalies = self.team_model.fit_predict(X_context_scaled)
            
            # Analyze anomaly patterns
            anomaly_analysis = self._analyze_anomalies(
                data, perf_anomalies, behav_anomalies, context_anomalies,
                perf_scores, behav_scores
            )
            
            results['performance_model'] = {
                'anomaly_count': np.sum(perf_anomalies == -1),
                'anomaly_rate': np.mean(perf_anomalies == -1),
                'features': performance_features
            }
            
            results['behavioral_model'] = {
                'anomaly_count': np.sum(behav_anomalies == -1),
                'anomaly_rate': np.mean(behav_anomalies == -1),
                'features': behavioral_features
            }
            
            results['contextual_model'] = {
                'anomaly_count': np.sum(context_anomalies == -1),
                'anomaly_rate': np.mean(context_anomalies == -1),
                'features': contextual_features
            }
            
            results['anomaly_analysis'] = anomaly_analysis
            
            logger.info(f"Anomaly detection models trained - Performance: {results['performance_model']['anomaly_rate']:.3f}, Behavioral: {results['behavioral_model']['anomaly_rate']:.3f}")
            
        except Exception as e:
            logger.error(f"Error training anomaly models: {str(e)}")
            results['error'] = str(e)
        
        self.is_trained = True
        return results
    
    def _analyze_anomalies(self, data: pd.DataFrame, perf_anomalies: np.ndarray, 
                          behav_anomalies: np.ndarray, context_anomalies: np.ndarray,
                          perf_scores: np.ndarray, behav_scores: np.ndarray) -> Dict[str, Any]:
        """Analyze detected anomalies"""
        
        analysis = {
            'performance_anomalies': [],
            'behavioral_anomalies': [],
            'contextual_anomalies': [],
            'combined_anomalies': []
        }
        
        # Performance anomalies
        perf_anomaly_indices = np.where(perf_anomalies == -1)[0]
        for idx in perf_anomaly_indices[:10]:  # Top 10 anomalies
            player_data = data.iloc[idx]
            analysis['performance_anomalies'].append({
                'player_name': player_data['player_name'],
                'anomaly_score': float(perf_scores[idx]),
                'rating_score': player_data['rating_score'],
                'goals_per_game': player_data['goals_per_game'],
                'team_relative_performance': player_data['team_relative_performance']
            })
        
        # Behavioral anomalies
        behav_anomaly_indices = np.where(behav_anomalies == -1)[0]
        for idx in behav_anomaly_indices[:10]:
            player_data = data.iloc[idx]
            analysis['behavioral_anomalies'].append({
                'player_name': player_data['player_name'],
                'anomaly_score': float(behav_scores[idx]),
                'cards_per_game': player_data['cards_per_game'],
                'discipline_score': player_data['discipline_score'],
                'workload_intensity': player_data['workload_intensity']
            })
        
        # Contextual anomalies
        context_anomaly_indices = np.where(context_anomalies == -1)[0]
        for idx in context_anomaly_indices[:10]:
            player_data = data.iloc[idx]
            analysis['contextual_anomalies'].append({
                'player_name': player_data['player_name'],
                'competition_relative_performance': player_data['competition_relative_performance'],
                'career_progression': player_data['career_progression'],
                'rating_change_from_historical': player_data['rating_change_from_historical']
            })
        
        # Combined anomalies (players anomalous in multiple categories)
        combined_anomaly_mask = (perf_anomalies == -1) | (behav_anomalies == -1) | (context_anomalies == -1)
        combined_indices = np.where(combined_anomaly_mask)[0]
        
        for idx in combined_indices[:10]:
            player_data = data.iloc[idx]
            anomaly_types = []
            if perf_anomalies[idx] == -1:
                anomaly_types.append('performance')
            if behav_anomalies[idx] == -1:
                anomaly_types.append('behavioral')
            if context_anomalies[idx] == -1:
                anomaly_types.append('contextual')
            
            analysis['combined_anomalies'].append({
                'player_name': player_data['player_name'],
                'anomaly_types': anomaly_types,
                'overall_risk_score': len(anomaly_types) / 3.0
            })
        
        return analysis
    
    def detect_player_anomalies(self, player: Player, season: Optional[Season] = None) -> Dict[str, Any]:
        """Detect anomalies for a specific player"""
        if not self.is_trained:
            raise ValueError("Models not trained. Call train_anomaly_models() first.")
        
        try:
            # Get player's statistics
            if season:
                stats = PlayerStatistics.objects.filter(player=player, season=season).first()
            else:
                stats = PlayerStatistics.objects.filter(player=player).order_by('-season__start_date').first()
            
            if not stats:
                logger.warning(f"No statistics found for player {player.name}")
                return self._default_anomaly_prediction(player)
            
            # Calculate all metrics
            performance_metrics = self._calculate_performance_metrics(stats)
            behavioral_metrics = self._calculate_behavioral_metrics(stats)
            contextual_metrics = self._calculate_contextual_metrics(player, stats)
            
            all_metrics = {**performance_metrics, **behavioral_metrics, **contextual_metrics}
            
            # Prepare features for each model
            performance_features = [
                'goals_per_game', 'assists_per_game', 'minutes_per_game',
                'goal_involvement_per_game', 'rating_score', 'performance_variance',
                'team_relative_performance', 'rating_change_from_historical'
            ]
            
            behavioral_features = [
                'cards_per_game', 'discipline_score', 'workload_minutes',
                'workload_intensity', 'estimated_injury_risk'
            ]
            
            contextual_features = [
                'competition_relative_performance', 'career_progression',
                'goal_change_from_historical', 'minutes_change_from_historical'
            ]
            
            # Make predictions
            anomaly_results = {}
            
            if self.performance_model and self.scaler:
                perf_features = pd.DataFrame([{f: all_metrics.get(f, 0) for f in performance_features}])
                perf_scaled = self.scaler.transform(perf_features)
                perf_anomaly = self.performance_model.predict(perf_scaled)[0]
                perf_score = self.performance_model.score_samples(perf_scaled)[0]
                
                anomaly_results['performance'] = {
                    'is_anomaly': perf_anomaly == -1,
                    'anomaly_score': float(perf_score),
                    'severity': self._calculate_severity(perf_score, 'performance'),
                    'key_factors': self._identify_anomaly_factors(all_metrics, performance_features, 'performance')
                }
            
            if self.behavioral_model:
                behav_features = pd.DataFrame([{f: all_metrics.get(f, 0) for f in behavioral_features}])
                behav_scaled = self.scaler.transform(behav_features)
                behav_anomaly = self.behavioral_model.predict(behav_scaled)[0]
                behav_score = self.behavioral_model.score_samples(behav_scaled)[0]
                
                anomaly_results['behavioral'] = {
                    'is_anomaly': behav_anomaly == -1,
                    'anomaly_score': float(behav_score),
                    'severity': self._calculate_severity(behav_score, 'behavioral'),
                    'key_factors': self._identify_anomaly_factors(all_metrics, behavioral_features, 'behavioral')
                }
            
            if self.team_model:
                context_features = pd.DataFrame([{f: all_metrics.get(f, 0) for f in contextual_features}])
                context_scaled = self.scaler.transform(context_features)
                context_anomaly = self.team_model.predict(context_scaled)[0]
                
                anomaly_results['contextual'] = {
                    'is_anomaly': context_anomaly == -1,
                    'severity': 'medium' if context_anomaly == -1 else 'low',
                    'key_factors': self._identify_anomaly_factors(all_metrics, contextual_features, 'contextual')
                }
            
            # Generate overall assessment
            overall_assessment = self._generate_overall_assessment(anomaly_results, all_metrics)
            
            # Generate recommendations
            recommendations = self._generate_anomaly_recommendations(player, anomaly_results, all_metrics)
            
            result = {
                'player_id': player.id,
                'player_name': player.name,
                'season_id': stats.season.id if stats.season else None,
                'anomaly_detection': anomaly_results,
                'overall_assessment': overall_assessment,
                'raw_metrics': all_metrics,
                'recommendations': recommendations,
                'detection_date': timezone.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error detecting anomalies for player {player.name}: {str(e)}")
            return self._default_anomaly_prediction(player)
    
    def _calculate_severity(self, score: float, anomaly_type: str) -> str:
        """Calculate severity level based on anomaly score"""
        # Lower scores indicate higher anomaly (more negative = more abnormal)
        if anomaly_type in ['performance', 'behavioral']:
            if score < -0.5:
                return 'high'
            elif score < -0.2:
                return 'medium'
            else:
                return 'low'
        else:  # contextual
            return 'medium'
    
    def _identify_anomaly_factors(self, metrics: Dict[str, float], features: List[str], anomaly_type: str) -> List[str]:
        """Identify key factors contributing to anomaly"""
        factors = []
        
        if anomaly_type == 'performance':
            if metrics.get('rating_change_from_historical', 0) < -1:
                factors.append("Significant decline in performance rating")
            if metrics.get('goal_change_from_historical', 0) < -0.2:
                factors.append("Decreased goal scoring compared to historical average")
            if metrics.get('team_relative_performance', 1) < 0.8:
                factors.append("Underperforming relative to teammates")
            if metrics.get('performance_variance', 0) > 2:
                factors.append("Inconsistent performance levels")
        
        elif anomaly_type == 'behavioral':
            if metrics.get('cards_per_game', 0) > 0.4:
                factors.append("Unusually high disciplinary issues")
            if metrics.get('workload_intensity', 0) > 0.9:
                factors.append("Extremely high workload intensity")
            if metrics.get('estimated_injury_risk', 0) > 0.8:
                factors.append("Elevated injury risk indicators")
            if metrics.get('discipline_score', 10) < 6:
                factors.append("Poor disciplinary record")
        
        elif anomaly_type == 'contextual':
            if metrics.get('competition_relative_performance', 1) < 0.7:
                factors.append("Below average for competition level")
            if metrics.get('career_progression', 0) < -0.5:
                factors.append("Declining career trajectory")
            if abs(metrics.get('minutes_change_from_historical', 0)) > 500:
                factors.append("Significant change in playing time")
        
        return factors[:3]  # Return top 3 factors
    
    def _generate_overall_assessment(self, anomaly_results: Dict[str, Dict], metrics: Dict[str, float]) -> Dict[str, Any]:
        """Generate overall anomaly assessment"""
        anomaly_count = sum(1 for result in anomaly_results.values() if result.get('is_anomaly', False))
        total_categories = len(anomaly_results)
        
        if anomaly_count == 0:
            risk_level = 'low'
            summary = "No significant anomalies detected"
        elif anomaly_count == 1:
            risk_level = 'medium'
            summary = "Minor anomalies detected in one category"
        elif anomaly_count == 2:
            risk_level = 'high'
            summary = "Anomalies detected in multiple categories"
        else:
            risk_level = 'critical'
            summary = "Widespread anomalies across all categories"
        
        # Calculate overall anomaly score
        anomaly_scores = [result.get('anomaly_score', 0) for result in anomaly_results.values() if 'anomaly_score' in result]
        overall_score = np.mean(anomaly_scores) if anomaly_scores else 0
        
        return {
            'risk_level': risk_level,
            'summary': summary,
            'anomaly_count': anomaly_count,
            'total_categories': total_categories,
            'overall_anomaly_score': float(overall_score),
            'requires_attention': anomaly_count >= 2 or any(
                result.get('severity') == 'high' for result in anomaly_results.values()
            )
        }
    
    def _generate_anomaly_recommendations(self, player: Player, anomaly_results: Dict, metrics: Dict) -> List[str]:
        """Generate recommendations based on detected anomalies"""
        recommendations = []
        
        # Performance anomaly recommendations
        if anomaly_results.get('performance', {}).get('is_anomaly', False):
            if metrics.get('rating_change_from_historical', 0) < -1:
                recommendations.append("Consider individual training to address performance decline")
            if metrics.get('team_relative_performance', 1) < 0.8:
                recommendations.append("Review role and responsibilities within the team")
            
        # Behavioral anomaly recommendations
        if anomaly_results.get('behavioral', {}).get('is_anomaly', False):
            if metrics.get('cards_per_game', 0) > 0.4:
                recommendations.append("Implement disciplinary support and anger management")
            if metrics.get('workload_intensity', 0) > 0.9:
                recommendations.append("Reduce playing time to prevent overexertion and injury")
            if metrics.get('estimated_injury_risk', 0) > 0.8:
                recommendations.append("Increase medical monitoring and injury prevention protocols")
        
        # Contextual anomaly recommendations
        if anomaly_results.get('contextual', {}).get('is_anomaly', False):
            if metrics.get('competition_relative_performance', 1) < 0.7:
                recommendations.append("Consider loan move to lower level for development")
            if metrics.get('career_progression', 0) < -0.5:
                recommendations.append("Evaluate long-term career planning and development needs")
        
        # Overall recommendations
        overall_assessment = self._generate_overall_assessment(anomaly_results, metrics)
        if overall_assessment['risk_level'] in ['high', 'critical']:
            recommendations.append("Schedule comprehensive performance review with coaching staff")
            recommendations.append("Consider sports psychology support")
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _default_anomaly_prediction(self, player: Player) -> Dict[str, Any]:
        """Return default anomaly prediction when models are not available"""
        return {
            'player_id': player.id,
            'player_name': player.name,
            'anomaly_detection': {
                'performance': {'is_anomaly': False, 'severity': 'low'},
                'behavioral': {'is_anomaly': False, 'severity': 'low'},
                'contextual': {'is_anomaly': False, 'severity': 'low'}
            },
            'overall_assessment': {
                'risk_level': 'low',
                'summary': 'No anomaly detection available (insufficient data)',
                'requires_attention': False
            },
            'recommendations': ['Collect more performance data for anomaly analysis'],
            'note': 'Prediction based on default model (limited data available)'
        }
    
    def save_anomaly_detection(self, player: Player, detection_data: Dict[str, Any], season: Optional[Season] = None) -> AnomalyDetection:
        """Save anomaly detection results to database"""
        try:
            if not season:
                season = Season.objects.filter(
                    start_date__lte=timezone.now().date(),
                    end_date__gte=timezone.now().date()
                ).first() or Season.objects.order_by('-start_date').first()
            
            # Determine anomaly type and severity
            anomaly_results = detection_data['anomaly_detection']
            overall_assessment = detection_data['overall_assessment']
            
            anomaly_types = [
                anomaly_type for anomaly_type, result in anomaly_results.items()
                if result.get('is_anomaly', False)
            ]
            
            anomaly_detection = AnomalyDetection.objects.create(
                player=player,
                anomaly_type=', '.join(anomaly_types) if anomaly_types else 'none',
                severity=overall_assessment['risk_level'],
                confidence_score=1.0 - abs(overall_assessment.get('overall_anomaly_score', 0)),
                detection_details=detection_data['anomaly_detection'],
                contributing_factors=detection_data.get('raw_metrics', {}),
                recommendations=detection_data['recommendations'],
                model_version=self.version,
                detection_date=timezone.now(),
                season=season
            )
            
            logger.info(f"Saved anomaly detection for {player.name}: {overall_assessment['risk_level']} risk")
            return anomaly_detection
            
        except Exception as e:
            logger.error(f"Error saving anomaly detection: {str(e)}")
            raise
