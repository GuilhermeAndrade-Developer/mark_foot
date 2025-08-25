import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from django.db.models import Q, Count, Avg
from django.utils import timezone

from core.models import Player, PlayerStatistics, Season, Team
from ai_analytics.models import PlayStyleCluster
from .base_service import BaseAIService, DataPreparationMixin, ModelEvaluationMixin, AIModelFactory

logger = logging.getLogger(__name__)


class PlayStyleClusteringService(BaseAIService, DataPreparationMixin, ModelEvaluationMixin):
    """Service for clustering players by play style"""
    
    def __init__(self):
        super().__init__("play_style_clustering", "1.0.0")
        self.clustering_model = None
        self.scaler = None
        self.style_profiles = {}
        
    def collect_player_style_data(self, seasons: int = 2) -> pd.DataFrame:
        """Collect player data for play style analysis"""
        try:
            cutoff_date = timezone.now() - timedelta(days=365 * seasons)
            
            # Get player statistics with sufficient playing time
            stats = PlayerStatistics.objects.filter(
                season__start_date__gte=cutoff_date,
                appearances__gte=10,  # Minimum appearances for reliable analysis
                minutes_played__gte=500  # Minimum minutes for style analysis
            ).select_related('player', 'season', 'competition').prefetch_related('player__team')
            
            data = []
            for stat in stats:
                player = stat.player
                
                # Calculate style metrics
                style_metrics = self._calculate_style_metrics(stat)
                
                player_data = {
                    'player_id': player.id,
                    'player_name': player.name,
                    'age': player.age or 25,
                    'position_category': player.position_category or 'MF',
                    'nationality': player.nationality or 'Unknown',
                    'team_id': player.team.id if player.team else None,
                    'season_id': stat.season.id,
                    
                    # Basic stats
                    'appearances': stat.appearances,
                    'starts': stat.starts,
                    'minutes_played': stat.minutes_played,
                    'goals': stat.goals,
                    'assists': stat.assists,
                    'rating': float(stat.rating) if stat.rating else 7.0,
                    
                    # Style metrics
                    **style_metrics
                }
                
                data.append(player_data)
            
            df = pd.DataFrame(data)
            logger.info(f"Collected play style data for {len(df)} player-season combinations")
            return df
            
        except Exception as e:
            logger.error(f"Error collecting play style data: {str(e)}")
            return pd.DataFrame()
    
    def _calculate_style_metrics(self, stats: PlayerStatistics) -> Dict[str, float]:
        """Calculate comprehensive play style metrics"""
        appearances = max(stats.appearances, 1)
        minutes = max(stats.minutes_played, 1)
        
        # Basic rate stats (per 90 minutes)
        minutes_per_90 = minutes / 90.0
        goals_per_90 = (stats.goals / minutes_per_90) if minutes_per_90 > 0 else 0
        assists_per_90 = (stats.assists / minutes_per_90) if minutes_per_90 > 0 else 0
        
        # Attacking metrics (simulated from available data)
        attacking_metrics = self._simulate_attacking_metrics(stats, minutes_per_90)
        
        # Defensive metrics (simulated from available data)
        defensive_metrics = self._simulate_defensive_metrics(stats, minutes_per_90)
        
        # Passing metrics (simulated from available data)
        passing_metrics = self._simulate_passing_metrics(stats, minutes_per_90)
        
        # Physical metrics (simulated from available data)
        physical_metrics = self._simulate_physical_metrics(stats, minutes_per_90)
        
        # Combine all metrics
        style_metrics = {
            # Goal involvement
            'goals_per_90': goals_per_90,
            'assists_per_90': assists_per_90,
            'goal_involvement_per_90': goals_per_90 + assists_per_90,
            
            # Attacking style
            'shots_per_90': attacking_metrics['shots_per_90'],
            'shots_on_target_per_90': attacking_metrics['shots_on_target_per_90'],
            'shot_accuracy': attacking_metrics['shot_accuracy'],
            'big_chances_created_per_90': attacking_metrics['big_chances_created_per_90'],
            'dribbles_per_90': attacking_metrics['dribbles_per_90'],
            'dribble_success_rate': attacking_metrics['dribble_success_rate'],
            
            # Defensive style
            'tackles_per_90': defensive_metrics['tackles_per_90'],
            'interceptions_per_90': defensive_metrics['interceptions_per_90'],
            'clearances_per_90': defensive_metrics['clearances_per_90'],
            'blocks_per_90': defensive_metrics['blocks_per_90'],
            'defensive_actions_per_90': defensive_metrics['defensive_actions_per_90'],
            
            # Passing style
            'passes_per_90': passing_metrics['passes_per_90'],
            'pass_accuracy': passing_metrics['pass_accuracy'],
            'long_passes_per_90': passing_metrics['long_passes_per_90'],
            'key_passes_per_90': passing_metrics['key_passes_per_90'],
            'crosses_per_90': passing_metrics['crosses_per_90'],
            
            # Physical style
            'aerial_duels_per_90': physical_metrics['aerial_duels_per_90'],
            'aerial_win_rate': physical_metrics['aerial_win_rate'],
            'fouls_per_90': physical_metrics['fouls_per_90'],
            'yellow_cards_per_90': physical_metrics['yellow_cards_per_90'],
            
            # Playing position indicators
            'is_starter': 1 if stats.starts / appearances > 0.7 else 0,
            'minutes_per_game': minutes / appearances,
            'consistency_rating': min(10, max(0, float(stats.rating) if stats.rating else 7.0))
        }
        
        return style_metrics
    
    def _simulate_attacking_metrics(self, stats: PlayerStatistics, minutes_per_90: float) -> Dict[str, float]:
        """Simulate attacking metrics based on goals and position"""
        position = stats.player.position_category
        goals = stats.goals
        rating = float(stats.rating) if stats.rating else 7.0
        
        # Base shots calculation based on goals and position
        if position == 'FW':
            shots_per_90 = max(2.0, goals * 4 + np.random.normal(2, 0.5))
            shot_accuracy = 0.3 + (rating - 6) * 0.05
        elif position == 'MF':
            shots_per_90 = max(1.0, goals * 3 + np.random.normal(1, 0.3))
            shot_accuracy = 0.25 + (rating - 6) * 0.04
        elif position == 'DF':
            shots_per_90 = max(0.2, goals * 2 + np.random.normal(0.3, 0.2))
            shot_accuracy = 0.2 + (rating - 6) * 0.03
        else:  # GK
            shots_per_90 = 0.1
            shot_accuracy = 0.1
        
        shots_on_target_per_90 = shots_per_90 * shot_accuracy
        
        # Big chances created (more for creative players)
        assists = stats.assists
        if position in ['MF', 'FW']:
            big_chances_created_per_90 = max(0.5, assists * 2 + (rating - 6) * 0.3)
        else:
            big_chances_created_per_90 = max(0.1, assists * 1.5 + (rating - 6) * 0.1)
        
        # Dribbles (more for attacking/wing players)
        if position == 'FW':
            dribbles_per_90 = max(1.0, (rating - 6) * 2 + np.random.normal(3, 1))
            dribble_success_rate = 0.6 + (rating - 7) * 0.05
        elif position == 'MF':
            dribbles_per_90 = max(0.5, (rating - 6) * 1.5 + np.random.normal(2, 0.8))
            dribble_success_rate = 0.55 + (rating - 7) * 0.04
        else:
            dribbles_per_90 = max(0.2, (rating - 6) * 0.5 + np.random.normal(0.5, 0.3))
            dribble_success_rate = 0.5 + (rating - 7) * 0.03
        
        return {
            'shots_per_90': max(0, shots_per_90),
            'shots_on_target_per_90': max(0, shots_on_target_per_90),
            'shot_accuracy': max(0, min(1, shot_accuracy)),
            'big_chances_created_per_90': max(0, big_chances_created_per_90),
            'dribbles_per_90': max(0, dribbles_per_90),
            'dribble_success_rate': max(0, min(1, dribble_success_rate))
        }
    
    def _simulate_defensive_metrics(self, stats: PlayerStatistics, minutes_per_90: float) -> Dict[str, float]:
        """Simulate defensive metrics based on position and rating"""
        position = stats.player.position_category
        rating = float(stats.rating) if stats.rating else 7.0
        
        # Defensive actions based on position
        if position == 'DF':
            tackles_per_90 = max(1.5, (rating - 5) * 2 + np.random.normal(3, 1))
            interceptions_per_90 = max(1.0, (rating - 5) * 1.5 + np.random.normal(2, 0.8))
            clearances_per_90 = max(2.0, (rating - 5) * 3 + np.random.normal(4, 1.5))
            blocks_per_90 = max(0.5, (rating - 5) * 1 + np.random.normal(1, 0.5))
        elif position == 'MF':
            tackles_per_90 = max(1.0, (rating - 5) * 1.5 + np.random.normal(2, 0.8))
            interceptions_per_90 = max(0.8, (rating - 5) * 1.2 + np.random.normal(1.5, 0.6))
            clearances_per_90 = max(0.5, (rating - 5) * 1 + np.random.normal(1, 0.5))
            blocks_per_90 = max(0.2, (rating - 5) * 0.5 + np.random.normal(0.5, 0.3))
        elif position == 'FW':
            tackles_per_90 = max(0.3, (rating - 5) * 0.5 + np.random.normal(0.8, 0.4))
            interceptions_per_90 = max(0.2, (rating - 5) * 0.3 + np.random.normal(0.5, 0.3))
            clearances_per_90 = max(0.1, (rating - 5) * 0.2 + np.random.normal(0.3, 0.2))
            blocks_per_90 = max(0.1, (rating - 5) * 0.2 + np.random.normal(0.2, 0.1))
        else:  # GK
            tackles_per_90 = 0.1
            interceptions_per_90 = 0.2
            clearances_per_90 = max(1.0, (rating - 5) * 2 + np.random.normal(2, 1))
            blocks_per_90 = 0.1
        
        defensive_actions_per_90 = tackles_per_90 + interceptions_per_90 + clearances_per_90 + blocks_per_90
        
        return {
            'tackles_per_90': max(0, tackles_per_90),
            'interceptions_per_90': max(0, interceptions_per_90),
            'clearances_per_90': max(0, clearances_per_90),
            'blocks_per_90': max(0, blocks_per_90),
            'defensive_actions_per_90': max(0, defensive_actions_per_90)
        }
    
    def _simulate_passing_metrics(self, stats: PlayerStatistics, minutes_per_90: float) -> Dict[str, float]:
        """Simulate passing metrics based on position and assists"""
        position = stats.player.position_category
        assists = stats.assists
        rating = float(stats.rating) if stats.rating else 7.0
        
        # Base passing volume and accuracy by position
        if position == 'MF':
            passes_per_90 = max(30, (rating - 5) * 15 + np.random.normal(50, 10))
            pass_accuracy = 0.75 + (rating - 6) * 0.03
            long_passes_per_90 = max(2, (rating - 5) * 3 + np.random.normal(5, 2))
        elif position == 'DF':
            passes_per_90 = max(25, (rating - 5) * 12 + np.random.normal(40, 8))
            pass_accuracy = 0.8 + (rating - 6) * 0.025
            long_passes_per_90 = max(3, (rating - 5) * 4 + np.random.normal(6, 2))
        elif position == 'FW':
            passes_per_90 = max(15, (rating - 5) * 8 + np.random.normal(25, 5))
            pass_accuracy = 0.7 + (rating - 6) * 0.035
            long_passes_per_90 = max(0.5, (rating - 5) * 1 + np.random.normal(2, 1))
        else:  # GK
            passes_per_90 = max(15, (rating - 5) * 10 + np.random.normal(20, 5))
            pass_accuracy = 0.6 + (rating - 6) * 0.04
            long_passes_per_90 = max(3, (rating - 5) * 5 + np.random.normal(8, 3))
        
        # Key passes based on assists and creativity
        key_passes_per_90 = max(0.5, assists * 3 + (rating - 6) * 0.5)
        
        # Crosses (more for wing players and some midfielders)
        if position in ['MF', 'FW']:
            crosses_per_90 = max(0.5, assists * 2 + np.random.normal(2, 1))
        else:
            crosses_per_90 = max(0.1, np.random.normal(0.5, 0.3))
        
        return {
            'passes_per_90': max(0, passes_per_90),
            'pass_accuracy': max(0, min(1, pass_accuracy)),
            'long_passes_per_90': max(0, long_passes_per_90),
            'key_passes_per_90': max(0, key_passes_per_90),
            'crosses_per_90': max(0, crosses_per_90)
        }
    
    def _simulate_physical_metrics(self, stats: PlayerStatistics, minutes_per_90: float) -> Dict[str, float]:
        """Simulate physical/disciplinary metrics"""
        position = stats.player.position_category
        rating = float(stats.rating) if stats.rating else 7.0
        
        # Aerial duels based on position and physical play
        if position == 'DF':
            aerial_duels_per_90 = max(2, (rating - 5) * 2 + np.random.normal(4, 1.5))
            aerial_win_rate = 0.6 + (rating - 6) * 0.04
        elif position == 'FW':
            aerial_duels_per_90 = max(1, (rating - 5) * 1.5 + np.random.normal(3, 1))
            aerial_win_rate = 0.5 + (rating - 6) * 0.04
        elif position == 'MF':
            aerial_duels_per_90 = max(0.5, (rating - 5) * 1 + np.random.normal(2, 0.8))
            aerial_win_rate = 0.45 + (rating - 6) * 0.03
        else:  # GK
            aerial_duels_per_90 = max(1, (rating - 5) * 1.5 + np.random.normal(2, 1))
            aerial_win_rate = 0.7 + (rating - 6) * 0.03
        
        # Fouls and cards (inverse correlation with rating for discipline)
        fouls_per_90 = max(0.2, 3 - (rating - 5) * 0.3 + np.random.normal(1, 0.5))
        yellow_cards_per_90 = max(0.05, fouls_per_90 * 0.2 + np.random.normal(0.15, 0.1))
        
        return {
            'aerial_duels_per_90': max(0, aerial_duels_per_90),
            'aerial_win_rate': max(0, min(1, aerial_win_rate)),
            'fouls_per_90': max(0, fouls_per_90),
            'yellow_cards_per_90': max(0, yellow_cards_per_90)
        }
    
    def train_clustering_model(self, data: pd.DataFrame, n_clusters: int = 8) -> Dict[str, Any]:
        """Train play style clustering model"""
        results = {}
        
        if data.empty:
            return {'error': 'No training data available'}
        
        # Define features for clustering
        clustering_features = [
            # Attacking
            'goals_per_90', 'assists_per_90', 'shots_per_90', 'shots_on_target_per_90',
            'big_chances_created_per_90', 'dribbles_per_90', 'dribble_success_rate',
            
            # Defensive
            'tackles_per_90', 'interceptions_per_90', 'clearances_per_90',
            'blocks_per_90', 'defensive_actions_per_90',
            
            # Passing
            'passes_per_90', 'pass_accuracy', 'long_passes_per_90',
            'key_passes_per_90', 'crosses_per_90',
            
            # Physical
            'aerial_duels_per_90', 'aerial_win_rate', 'fouls_per_90',
            
            # General
            'consistency_rating', 'minutes_per_game'
        ]
        
        # Prepare data for clustering
        X = data[clustering_features].fillna(0)
        
        # Normalize features
        try:
            from sklearn.preprocessing import StandardScaler
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            
            # Train clustering model
            from sklearn.cluster import KMeans
            from sklearn.metrics import silhouette_score
            
            self.clustering_model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = self.clustering_model.fit_predict(X_scaled)
            
            # Calculate clustering metrics
            silhouette_avg = silhouette_score(X_scaled, cluster_labels)
            
            # Analyze clusters
            cluster_analysis = self._analyze_clusters(data, cluster_labels, clustering_features)
            
            results['clustering'] = {
                'n_clusters': n_clusters,
                'silhouette_score': silhouette_avg,
                'feature_importance': clustering_features,
                'cluster_analysis': cluster_analysis
            }
            
            # Generate style profiles
            self.style_profiles = self._generate_style_profiles(data, cluster_labels, clustering_features)
            
            logger.info(f"Play style clustering trained with {n_clusters} clusters, silhouette score: {silhouette_avg:.3f}")
            
        except Exception as e:
            logger.error(f"Error training clustering model: {str(e)}")
            results['clustering'] = {'error': str(e)}
        
        self.is_trained = True
        return results
    
    def _analyze_clusters(self, data: pd.DataFrame, labels: np.ndarray, features: List[str]) -> Dict[str, Any]:
        """Analyze characteristics of each cluster"""
        cluster_analysis = {}
        
        data_with_clusters = data.copy()
        data_with_clusters['cluster'] = labels
        
        for cluster_id in range(len(np.unique(labels))):
            cluster_data = data_with_clusters[data_with_clusters['cluster'] == cluster_id]
            
            # Calculate cluster statistics
            cluster_stats = {}
            for feature in features:
                cluster_stats[feature] = {
                    'mean': float(cluster_data[feature].mean()),
                    'std': float(cluster_data[feature].std()),
                    'min': float(cluster_data[feature].min()),
                    'max': float(cluster_data[feature].max())
                }
            
            # Position distribution
            position_dist = cluster_data['position_category'].value_counts().to_dict()
            
            # Representative players
            representative_players = cluster_data.nlargest(3, 'consistency_rating')[
                ['player_name', 'position_category', 'consistency_rating']
            ].to_dict('records')
            
            cluster_analysis[f'cluster_{cluster_id}'] = {
                'size': len(cluster_data),
                'statistics': cluster_stats,
                'position_distribution': position_dist,
                'representative_players': representative_players
            }
        
        return cluster_analysis
    
    def _generate_style_profiles(self, data: pd.DataFrame, labels: np.ndarray, features: List[str]) -> Dict[str, Dict]:
        """Generate human-readable style profiles for each cluster"""
        profiles = {}
        
        data_with_clusters = data.copy()
        data_with_clusters['cluster'] = labels
        
        for cluster_id in range(len(np.unique(labels))):
            cluster_data = data_with_clusters[data_with_clusters['cluster'] == cluster_id]
            
            # Calculate normalized feature means (0-1 scale)
            feature_means = {}
            for feature in features:
                mean_val = cluster_data[feature].mean()
                global_mean = data[feature].mean()
                global_std = data[feature].std()
                
                # Normalize relative to global distribution
                normalized_score = (mean_val - global_mean) / (global_std + 1e-6)
                feature_means[feature] = normalized_score
            
            # Determine style characteristics
            style_name, style_description = self._determine_style_name(feature_means, cluster_data)
            
            profiles[f'cluster_{cluster_id}'] = {
                'style_name': style_name,
                'description': style_description,
                'key_attributes': self._get_key_attributes(feature_means),
                'typical_positions': list(cluster_data['position_category'].mode().values),
                'size': len(cluster_data)
            }
        
        return profiles
    
    def _determine_style_name(self, feature_means: Dict[str, float], cluster_data: pd.DataFrame) -> Tuple[str, str]:
        """Determine style name and description based on feature characteristics"""
        # Analyze key characteristics
        is_attacking = feature_means.get('goals_per_90', 0) > 0.5 or feature_means.get('shots_per_90', 0) > 0.5
        is_creative = feature_means.get('assists_per_90', 0) > 0.5 or feature_means.get('key_passes_per_90', 0) > 0.5
        is_defensive = feature_means.get('defensive_actions_per_90', 0) > 0.5
        is_possession = feature_means.get('passes_per_90', 0) > 0.5 and feature_means.get('pass_accuracy', 0) > 0.3
        is_physical = feature_means.get('aerial_duels_per_90', 0) > 0.5
        is_technical = feature_means.get('dribbles_per_90', 0) > 0.5
        
        # Determine style based on characteristics
        if is_attacking and is_technical:
            return "Technical Finisher", "Skillful attackers who combine technical ability with goal threat"
        elif is_attacking and is_physical:
            return "Physical Striker", "Powerful forwards who dominate in aerial duels and physical battles"
        elif is_creative and is_possession:
            return "Playmaker", "Creative players who control the game through passing and vision"
        elif is_defensive and is_physical:
            return "Defensive Enforcer", "Strong defenders who win duels and clear danger"
        elif is_defensive and is_technical:
            return "Ball-Playing Defender", "Technical defenders comfortable with possession"
        elif is_possession and not is_attacking:
            return "Possession Controller", "Players who maintain possession and control tempo"
        elif is_technical and is_creative:
            return "Technical Creator", "Skillful players who create chances through dribbling and passing"
        else:
            return "Versatile Player", "Well-rounded players without extreme specialization"
    
    def _get_key_attributes(self, feature_means: Dict[str, float], top_n: int = 5) -> List[str]:
        """Get top attributes that define this cluster"""
        # Sort features by absolute normalized score
        sorted_features = sorted(feature_means.items(), key=lambda x: abs(x[1]), reverse=True)
        
        key_attributes = []
        for feature, score in sorted_features[:top_n]:
            if abs(score) > 0.3:  # Only include significant attributes
                attribute_name = self._format_attribute_name(feature)
                intensity = "High" if score > 0.5 else "Above Average" if score > 0 else "Below Average"
                key_attributes.append(f"{intensity} {attribute_name}")
        
        return key_attributes[:top_n]
    
    def _format_attribute_name(self, feature: str) -> str:
        """Format feature name for human readability"""
        name_mapping = {
            'goals_per_90': 'Goal Scoring',
            'assists_per_90': 'Assist Production',
            'shots_per_90': 'Shot Taking',
            'dribbles_per_90': 'Dribbling',
            'tackles_per_90': 'Tackling',
            'interceptions_per_90': 'Interceptions',
            'passes_per_90': 'Passing Volume',
            'pass_accuracy': 'Passing Accuracy',
            'key_passes_per_90': 'Chance Creation',
            'aerial_duels_per_90': 'Aerial Ability',
            'defensive_actions_per_90': 'Defensive Work',
            'consistency_rating': 'Consistency'
        }
        
        return name_mapping.get(feature, feature.replace('_', ' ').title())
    
    def predict_player_style(self, player: Player, season: Optional[Season] = None) -> Dict[str, Any]:
        """Predict play style cluster for a specific player"""
        if not self.is_trained:
            raise ValueError("Model not trained. Call train_clustering_model() first.")
        
        try:
            # Get player's recent statistics
            recent_stats = PlayerStatistics.objects.filter(
                player=player
            ).order_by('-season__start_date').first()
            
            if not recent_stats:
                logger.warning(f"No statistics found for player {player.name}")
                return self._default_style_prediction(player)
            
            # Calculate style metrics
            style_metrics = self._calculate_style_metrics(recent_stats)
            
            # Prepare features for prediction
            clustering_features = [
                'goals_per_90', 'assists_per_90', 'shots_per_90', 'shots_on_target_per_90',
                'big_chances_created_per_90', 'dribbles_per_90', 'dribble_success_rate',
                'tackles_per_90', 'interceptions_per_90', 'clearances_per_90',
                'blocks_per_90', 'defensive_actions_per_90',
                'passes_per_90', 'pass_accuracy', 'long_passes_per_90',
                'key_passes_per_90', 'crosses_per_90',
                'aerial_duels_per_90', 'aerial_win_rate', 'fouls_per_90',
                'consistency_rating', 'minutes_per_game'
            ]
            
            features = pd.DataFrame([{feature: style_metrics.get(feature, 0) for feature in clustering_features}])
            
            # Make prediction
            if self.clustering_model and self.scaler:
                features_scaled = self.scaler.transform(features)
                predicted_cluster = self.clustering_model.predict(features_scaled)[0]
                
                # Get cluster distances for confidence
                cluster_distances = self.clustering_model.transform(features_scaled)[0]
                confidence = 1.0 / (1.0 + cluster_distances[predicted_cluster])
                
                # Get style profile
                style_profile = self.style_profiles.get(f'cluster_{predicted_cluster}', {})
                
                # Find similar players in same cluster
                similar_players = self._find_similar_players_in_cluster(player, predicted_cluster)
                
                prediction_result = {
                    'player_id': player.id,
                    'player_name': player.name,
                    'predicted_cluster': int(predicted_cluster),
                    'style_name': style_profile.get('style_name', 'Unknown Style'),
                    'style_description': style_profile.get('description', ''),
                    'key_attributes': style_profile.get('key_attributes', []),
                    'confidence': float(confidence),
                    'style_metrics': style_metrics,
                    'cluster_distances': {f'cluster_{i}': float(dist) for i, dist in enumerate(cluster_distances)},
                    'similar_players': similar_players,
                    'recommendations': self._generate_style_recommendations(player, style_metrics, style_profile)
                }
                
                return prediction_result
            else:
                return self._default_style_prediction(player)
                
        except Exception as e:
            logger.error(f"Error predicting play style: {str(e)}")
            return self._default_style_prediction(player)
    
    def _default_style_prediction(self, player: Player) -> Dict[str, Any]:
        """Return default style prediction when model is not available"""
        position = player.position_category or 'MF'
        
        # Simple position-based style assignment
        position_styles = {
            'GK': ('Goalkeeper', 'Shot-stopping and distribution specialist'),
            'DF': ('Defender', 'Defensive-minded player focused on preventing goals'),
            'MF': ('Midfielder', 'Versatile player involved in both attack and defense'),
            'FW': ('Forward', 'Attacking player focused on scoring goals')
        }
        
        style_name, description = position_styles.get(position, ('Unknown', 'Player style not determined'))
        
        return {
            'player_id': player.id,
            'player_name': player.name,
            'predicted_cluster': -1,
            'style_name': style_name,
            'style_description': description,
            'key_attributes': [f"Plays as {position}"],
            'confidence': 0.5,
            'note': 'Prediction based on position (limited data available)'
        }
    
    def _find_similar_players_in_cluster(self, player: Player, cluster_id: int) -> List[Dict[str, Any]]:
        """Find similar players in the same style cluster"""
        try:
            # This would query the database for players with same cluster
            # For now, return empty list as we don't have stored cluster assignments
            return []
        except Exception as e:
            logger.error(f"Error finding similar players: {str(e)}")
            return []
    
    def _generate_style_recommendations(self, player: Player, metrics: Dict, profile: Dict) -> List[str]:
        """Generate recommendations based on player's style analysis"""
        recommendations = []
        
        position = player.position_category
        style_name = profile.get('style_name', '')
        
        # Position-specific recommendations
        if position == 'FW':
            if metrics.get('shots_per_90', 0) < 2:
                recommendations.append("Increase shot frequency to improve goal threat")
            if metrics.get('dribbles_per_90', 0) < 2:
                recommendations.append("Work on dribbling to create more scoring opportunities")
        
        elif position == 'MF':
            if metrics.get('key_passes_per_90', 0) < 1:
                recommendations.append("Focus on creating more scoring chances for teammates")
            if metrics.get('defensive_actions_per_90', 0) < 3:
                recommendations.append("Improve defensive contribution in midfield")
        
        elif position == 'DF':
            if metrics.get('clearances_per_90', 0) < 2:
                recommendations.append("Increase defensive clearances and interceptions")
            if metrics.get('pass_accuracy', 0) < 0.8:
                recommendations.append("Improve passing accuracy for better ball retention")
        
        # Style-specific recommendations
        if 'Technical' in style_name and metrics.get('dribble_success_rate', 0) < 0.6:
            recommendations.append("Work on dribbling efficiency to maintain technical style")
        
        if 'Creative' in style_name and metrics.get('assists_per_90', 0) < 0.2:
            recommendations.append("Focus on final ball delivery to maximize creative impact")
        
        return recommendations[:3]  # Return top 3 recommendations
    
    def save_play_style_prediction(self, player: Player, prediction_data: Dict[str, Any], season: Optional[Season] = None) -> PlayStyleCluster:
        """Save play style prediction to database"""
        try:
            if not season:
                season = Season.objects.filter(
                    start_date__lte=timezone.now().date(),
                    end_date__gte=timezone.now().date()
                ).first() or Season.objects.order_by('-start_date').first()
            
            style_prediction = PlayStyleCluster.objects.create(
                player=player,
                cluster_id=prediction_data['predicted_cluster'],
                style_name=prediction_data['style_name'],
                style_description=prediction_data['style_description'],
                key_attributes=prediction_data['key_attributes'],
                confidence_score=prediction_data['confidence'],
                style_metrics=prediction_data['style_metrics'],
                model_version=self.version,
                analysis_date=timezone.now(),
                season=season
            )
            
            logger.info(f"Saved play style prediction for {player.name}: {prediction_data['style_name']}")
            return style_prediction
            
        except Exception as e:
            logger.error(f"Error saving play style prediction: {str(e)}")
            raise
