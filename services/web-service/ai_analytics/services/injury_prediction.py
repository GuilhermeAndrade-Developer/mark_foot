import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from django.db.models import Q, Count, Avg
from django.utils import timezone

from core.models import Player, PlayerStatistics, Season
from ai_analytics.models import InjuryPrediction
from .base_service import BaseAIService, DataPreparationMixin, ModelEvaluationMixin, AIModelFactory

logger = logging.getLogger(__name__)


class InjuryPredictionService(BaseAIService, DataPreparationMixin, ModelEvaluationMixin):
    """Service for predicting injury risks for players"""
    
    def __init__(self):
        super().__init__("injury_prediction", "1.0.0")
        self.risk_model = None
        self.injury_type_model = None
        
    def collect_player_workload_data(self, seasons: int = 2) -> pd.DataFrame:
        """Collect player workload and injury risk data"""
        try:
            cutoff_date = timezone.now() - timedelta(days=365 * seasons)
            
            # Get player statistics
            stats = PlayerStatistics.objects.filter(
                season__start_date__gte=cutoff_date
            ).select_related('player', 'season').prefetch_related('player__team')
            
            data = []
            for stat in stats:
                player = stat.player
                
                # Calculate workload metrics
                workload_data = self._calculate_workload_metrics(stat)
                
                # Get injury history (simulated for now)
                injury_history = self._get_injury_history(player)
                
                # Calculate risk factors
                risk_factors = self._calculate_risk_factors(player, stat, workload_data)
                
                player_data = {
                    'player_id': player.id,
                    'player_name': player.name,
                    'age': player.age or 25,
                    'position_category': player.position_category or 'Unknown',
                    'season_id': stat.season.id,
                    
                    # Workload metrics
                    'appearances': stat.appearances,
                    'minutes_played': stat.minutes_played,
                    'minutes_per_game': workload_data['minutes_per_game'],
                    'games_started': stat.starts,
                    'substitutions_in': stat.substitutions_in,
                    'substitutions_out': stat.substitutions_out,
                    
                    # Physical demand indicators
                    'cards_received': stat.yellow_cards + stat.red_cards * 2,
                    'cards_per_game': workload_data['cards_per_game'],
                    
                    # Performance under pressure
                    'rating': float(stat.rating) if stat.rating else 7.0,
                    'goals_per_game': workload_data['goals_per_game'],
                    'assists_per_game': workload_data['assists_per_game'],
                    
                    # Risk factors
                    'age_risk': risk_factors['age_risk'],
                    'workload_risk': risk_factors['workload_risk'],
                    'intensity_risk': risk_factors['intensity_risk'],
                    'position_risk': risk_factors['position_risk'],
                    'fatigue_risk': risk_factors['fatigue_risk'],
                    
                    # Historical injury data (simulated)
                    'previous_injuries': injury_history['count'],
                    'injury_prone': injury_history['prone'],
                    'last_injury_months': injury_history['last_injury_months'],
                    
                    # Target variables (simulated for training)
                    'injury_occurred': self._simulate_injury_occurrence(risk_factors),
                    'injury_severity': self._simulate_injury_severity(risk_factors),
                    'injury_type': self._simulate_injury_type(player.position_category, risk_factors)
                }
                
                data.append(player_data)
            
            df = pd.DataFrame(data)
            logger.info(f"Collected workload data for {len(df)} player-season combinations")
            return df
            
        except Exception as e:
            logger.error(f"Error collecting workload data: {str(e)}")
            return pd.DataFrame()
    
    def _calculate_workload_metrics(self, stats: PlayerStatistics) -> Dict[str, float]:
        """Calculate workload metrics for a player"""
        appearances = max(stats.appearances, 1)
        
        return {
            'minutes_per_game': stats.minutes_played / appearances,
            'goals_per_game': stats.goals / appearances,
            'assists_per_game': stats.assists / appearances,
            'cards_per_game': (stats.yellow_cards + stats.red_cards * 2) / appearances,
            'start_ratio': stats.starts / appearances if appearances > 0 else 0,
            'substitution_ratio': (stats.substitutions_in + stats.substitutions_out) / appearances if appearances > 0 else 0
        }
    
    def _get_injury_history(self, player: Player) -> Dict[str, Any]:
        """Get player's injury history (simulated for demonstration)"""
        # In real implementation, this would query injury database
        # For now, simulate based on age and position
        
        age = player.age or 25
        position = player.position_category or 'MF'
        
        # Simulate injury proneness based on age and position
        if age > 30:
            injury_count = np.random.randint(2, 6)
            injury_prone = np.random.choice([True, False], p=[0.7, 0.3])
        elif age < 23:
            injury_count = np.random.randint(0, 3)
            injury_prone = np.random.choice([True, False], p=[0.3, 0.7])
        else:
            injury_count = np.random.randint(1, 4)
            injury_prone = np.random.choice([True, False], p=[0.5, 0.5])
        
        # Position-based adjustments
        if position in ['DF', 'GK']:
            injury_count = max(0, injury_count - 1)
        elif position == 'FW':
            injury_count += 1
        
        last_injury_months = np.random.randint(6, 24) if injury_count > 0 else 24
        
        return {
            'count': injury_count,
            'prone': injury_prone,
            'last_injury_months': last_injury_months
        }
    
    def _calculate_risk_factors(self, player: Player, stats: PlayerStatistics, workload: Dict) -> Dict[str, float]:
        """Calculate various injury risk factors"""
        age = player.age or 25
        position = player.position_category or 'MF'
        
        # Age risk (higher for older players)
        if age < 20:
            age_risk = 0.3  # Young players still developing
        elif age < 25:
            age_risk = 0.2  # Peak physical condition
        elif age < 30:
            age_risk = 0.4  # Starting to accumulate wear
        else:
            age_risk = 0.8  # Higher injury risk
        
        # Workload risk (based on minutes played)
        minutes_per_game = workload['minutes_per_game']
        if minutes_per_game > 80:
            workload_risk = 0.8  # Very high workload
        elif minutes_per_game > 60:
            workload_risk = 0.6  # High workload
        elif minutes_per_game > 30:
            workload_risk = 0.4  # Moderate workload
        else:
            workload_risk = 0.2  # Low workload
        
        # Intensity risk (based on cards and substitutions)
        cards_per_game = workload['cards_per_game']
        intensity_risk = min(0.9, cards_per_game * 0.3 + workload['substitution_ratio'] * 0.2)
        
        # Position risk
        position_risks = {
            'GK': 0.2,  # Low contact sport
            'DF': 0.6,  # Moderate contact and physical duels
            'MF': 0.5,  # Balanced
            'FW': 0.7   # High contact, sprinting, jumping
        }
        position_risk = position_risks.get(position, 0.5)
        
        # Fatigue risk (based on game frequency)
        if stats.appearances > 35:  # Very frequent player
            fatigue_risk = 0.8
        elif stats.appearances > 25:
            fatigue_risk = 0.6
        elif stats.appearances > 15:
            fatigue_risk = 0.4
        else:
            fatigue_risk = 0.2
        
        return {
            'age_risk': age_risk,
            'workload_risk': workload_risk,
            'intensity_risk': intensity_risk,
            'position_risk': position_risk,
            'fatigue_risk': fatigue_risk
        }
    
    def _simulate_injury_occurrence(self, risk_factors: Dict) -> int:
        """Simulate whether injury occurred (for training data)"""
        # Calculate overall risk
        total_risk = (
            risk_factors['age_risk'] * 0.2 +
            risk_factors['workload_risk'] * 0.3 +
            risk_factors['intensity_risk'] * 0.2 +
            risk_factors['position_risk'] * 0.15 +
            risk_factors['fatigue_risk'] * 0.15
        )
        
        # Simulate injury occurrence based on risk
        return 1 if np.random.random() < total_risk else 0
    
    def _simulate_injury_severity(self, risk_factors: Dict) -> str:
        """Simulate injury severity"""
        total_risk = sum(risk_factors.values()) / len(risk_factors)
        
        if total_risk > 0.7:
            return np.random.choice(['MEDIUM', 'HIGH'], p=[0.4, 0.6])
        elif total_risk > 0.4:
            return np.random.choice(['LOW', 'MEDIUM'], p=[0.6, 0.4])
        else:
            return 'LOW'
    
    def _simulate_injury_type(self, position: str, risk_factors: Dict) -> str:
        """Simulate injury type based on position and risk factors"""
        # Position-specific injury patterns
        if position == 'GK':
            return np.random.choice(['MUSCLE', 'BONE'], p=[0.7, 0.3])
        elif position == 'FW':
            return np.random.choice(['MUSCLE', 'LIGAMENT', 'FATIGUE'], p=[0.5, 0.3, 0.2])
        elif position == 'DF':
            return np.random.choice(['MUSCLE', 'LIGAMENT', 'BONE'], p=[0.4, 0.4, 0.2])
        else:  # MF
            return np.random.choice(['MUSCLE', 'FATIGUE', 'LIGAMENT'], p=[0.5, 0.3, 0.2])
    
    def train_injury_models(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Train injury prediction models"""
        results = {}
        
        if data.empty:
            return {'error': 'No training data available'}
        
        # Prepare features
        feature_columns = [
            'age', 'appearances', 'minutes_per_game', 'cards_per_game',
            'age_risk', 'workload_risk', 'intensity_risk', 'position_risk', 'fatigue_risk',
            'previous_injuries', 'injury_prone', 'last_injury_months'
        ]
        
        # Handle categorical variables
        data_encoded = pd.get_dummies(data, columns=['position_category'], prefix='pos')
        
        # Update feature columns to include encoded positions
        position_cols = [col for col in data_encoded.columns if col.startswith('pos_')]
        feature_columns.extend(position_cols)
        
        X = data_encoded[feature_columns].fillna(0)
        
        # Train injury occurrence model
        try:
            y_injury = data_encoded['injury_occurred']
            self.risk_model = AIModelFactory.create_classifier('random_forest', n_estimators=100, random_state=42)
            self.risk_model.fit(X, y_injury)
            
            # Evaluate model
            injury_scores = self.cross_validate_model(self.risk_model, X, y_injury, cv=5, scoring='accuracy')
            results['injury_model'] = {
                'accuracy': injury_scores['mean_score'],
                'accuracy_std': injury_scores['std_score'],
                'feature_importance': dict(zip(feature_columns, self.risk_model.feature_importances_))
            }
            logger.info(f"Injury prediction model trained with accuracy: {injury_scores['mean_score']:.3f}")
            
        except Exception as e:
            logger.error(f"Error training injury model: {str(e)}")
            results['injury_model'] = {'error': str(e)}
        
        self.is_trained = True
        return results
    
    def predict_injury_risk(self, player: Player, prediction_period: int = 30) -> Dict[str, Any]:
        """Predict injury risk for a specific player"""
        if not self.is_trained:
            raise ValueError("Model not trained. Call train_injury_models() first.")
        
        try:
            # Get player's recent statistics
            recent_stats = PlayerStatistics.objects.filter(
                player=player
            ).order_by('-season__start_date').first()
            
            if not recent_stats:
                logger.warning(f"No statistics found for player {player.name}")
                return self._default_risk_prediction(player)
            
            # Calculate current workload and risk factors
            workload_data = self._calculate_workload_metrics(recent_stats)
            risk_factors = self._calculate_risk_factors(player, recent_stats, workload_data)
            injury_history = self._get_injury_history(player)
            
            # Prepare features for prediction
            features = pd.DataFrame([{
                'age': player.age or 25,
                'appearances': recent_stats.appearances,
                'minutes_per_game': workload_data['minutes_per_game'],
                'cards_per_game': workload_data['cards_per_game'],
                'age_risk': risk_factors['age_risk'],
                'workload_risk': risk_factors['workload_risk'],
                'intensity_risk': risk_factors['intensity_risk'],
                'position_risk': risk_factors['position_risk'],
                'fatigue_risk': risk_factors['fatigue_risk'],
                'previous_injuries': injury_history['count'],
                'injury_prone': int(injury_history['prone']),
                'last_injury_months': injury_history['last_injury_months'],
                
                # Position encoding (simplified)
                'pos_DF': 1 if player.position_category == 'DF' else 0,
                'pos_FW': 1 if player.position_category == 'FW' else 0,
                'pos_GK': 1 if player.position_category == 'GK' else 0,
                'pos_MF': 1 if player.position_category == 'MF' else 0,
            }])
            
            # Make prediction
            if self.risk_model:
                risk_proba = self.risk_model.predict_proba(features)[0]
                risk_prediction = self.risk_model.predict(features)[0]
                
                # Determine risk level
                injury_probability = risk_proba[1] if len(risk_proba) > 1 else 0.5
                
                if injury_probability > 0.7:
                    risk_level = 'CRITICAL'
                elif injury_probability > 0.5:
                    risk_level = 'HIGH'
                elif injury_probability > 0.3:
                    risk_level = 'MEDIUM'
                else:
                    risk_level = 'LOW'
                
                # Predict most likely injury type
                injury_type = self._simulate_injury_type(player.position_category, risk_factors)
                
                # Generate recommendations
                recommendations = self._generate_injury_prevention_recommendations(
                    player, risk_factors, risk_level
                )
                
                prediction_result = {
                    'player_id': player.id,
                    'player_name': player.name,
                    'risk_level': risk_level,
                    'injury_probability': float(injury_probability),
                    'predicted_injury_type': injury_type,
                    'prediction_period_days': prediction_period,
                    'risk_factors': {
                        'age_risk': risk_factors['age_risk'],
                        'workload_risk': risk_factors['workload_risk'],
                        'intensity_risk': risk_factors['intensity_risk'],
                        'position_risk': risk_factors['position_risk'],
                        'fatigue_risk': risk_factors['fatigue_risk']
                    },
                    'current_workload': {
                        'minutes_per_game': workload_data['minutes_per_game'],
                        'games_played': recent_stats.appearances,
                        'cards_per_game': workload_data['cards_per_game']
                    },
                    'recommendations': recommendations,
                    'feature_importance': dict(zip(features.columns, self.risk_model.feature_importances_)) if hasattr(self.risk_model, 'feature_importances_') else {}
                }
                
                return prediction_result
            else:
                return self._default_risk_prediction(player)
                
        except Exception as e:
            logger.error(f"Error predicting injury risk: {str(e)}")
            return self._default_risk_prediction(player)
    
    def _default_risk_prediction(self, player: Player) -> Dict[str, Any]:
        """Return default risk prediction when model is not available"""
        age = player.age or 25
        
        # Simple age-based risk assessment
        if age > 32:
            risk_level = 'HIGH'
            probability = 0.6
        elif age > 28:
            risk_level = 'MEDIUM'
            probability = 0.4
        else:
            risk_level = 'LOW'
            probability = 0.2
        
        return {
            'player_id': player.id,
            'player_name': player.name,
            'risk_level': risk_level,
            'injury_probability': probability,
            'predicted_injury_type': 'GENERAL',
            'prediction_period_days': 30,
            'risk_factors': {
                'age_risk': 0.5,
                'workload_risk': 0.4,
                'intensity_risk': 0.3,
                'position_risk': 0.4,
                'fatigue_risk': 0.3
            },
            'recommendations': ['Regular fitness monitoring', 'Adequate rest periods'],
            'note': 'Prediction based on default model (limited data available)'
        }
    
    def _generate_injury_prevention_recommendations(self, player: Player, risk_factors: Dict, risk_level: str) -> List[str]:
        """Generate personalized injury prevention recommendations"""
        recommendations = []
        
        # Age-based recommendations
        if risk_factors['age_risk'] > 0.6:
            recommendations.append("Implement enhanced recovery protocols for veteran player")
            recommendations.append("Consider reduced training intensity during heavy fixture periods")
        
        # Workload recommendations
        if risk_factors['workload_risk'] > 0.6:
            recommendations.append("Monitor and potentially reduce playing minutes")
            recommendations.append("Implement rotation policy for this player")
        
        # Intensity recommendations
        if risk_factors['intensity_risk'] > 0.5:
            recommendations.append("Focus on discipline training to reduce cards")
            recommendations.append("Monitor physical challenges and duels in training")
        
        # Position-specific recommendations
        position = player.position_category
        if position == 'GK':
            recommendations.append("Focus on shoulder and back strengthening exercises")
        elif position == 'DF':
            recommendations.append("Emphasize knee and ankle stability training")
        elif position == 'MF':
            recommendations.append("Balance endurance and strength training")
        elif position == 'FW':
            recommendations.append("Focus on hamstring and groin injury prevention")
        
        # Fatigue recommendations
        if risk_factors['fatigue_risk'] > 0.6:
            recommendations.append("Mandatory rest days between intense training sessions")
            recommendations.append("Monitor sleep quality and nutrition")
        
        # Risk level specific
        if risk_level == 'CRITICAL':
            recommendations.append("Consider immediate medical evaluation")
            recommendations.append("Implement daily fitness monitoring")
        elif risk_level == 'HIGH':
            recommendations.append("Weekly fitness assessments recommended")
            recommendations.append("Enhanced warm-up and cool-down protocols")
        
        return recommendations[:6]  # Limit to 6 recommendations
    
    def save_injury_prediction(self, player: Player, prediction_data: Dict[str, Any]) -> InjuryPrediction:
        """Save injury prediction to database"""
        try:
            injury_prediction = InjuryPrediction.objects.create(
                player=player,
                risk_level=prediction_data['risk_level'],
                injury_type=prediction_data['predicted_injury_type'],
                risk_score=prediction_data['injury_probability'] * 100,
                prediction_period=prediction_data['prediction_period_days'],
                risk_factors=prediction_data['risk_factors'],
                recommended_actions=prediction_data['recommendations'],
                model_version=self.version,
                prediction_date=timezone.now()
            )
            
            logger.info(f"Saved injury prediction for {player.name}: {prediction_data['risk_level']}")
            return injury_prediction
            
        except Exception as e:
            logger.error(f"Error saving injury prediction: {str(e)}")
            raise
    
    def analyze_team_injury_risks(self, team_players: List[Player]) -> Dict[str, Any]:
        """Analyze injury risks for an entire team"""
        try:
            team_analysis = {
                'total_players': len(team_players),
                'risk_distribution': {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'CRITICAL': 0},
                'high_risk_players': [],
                'position_risks': {},
                'recommendations': []
            }
            
            for player in team_players:
                try:
                    prediction = self.predict_injury_risk(player)
                    risk_level = prediction['risk_level']
                    
                    # Update distribution
                    team_analysis['risk_distribution'][risk_level] += 1
                    
                    # Track high risk players
                    if risk_level in ['HIGH', 'CRITICAL']:
                        team_analysis['high_risk_players'].append({
                            'name': player.name,
                            'position': player.position_category,
                            'risk_level': risk_level,
                            'probability': prediction['injury_probability']
                        })
                    
                    # Position risk analysis
                    position = player.position_category or 'Unknown'
                    if position not in team_analysis['position_risks']:
                        team_analysis['position_risks'][position] = []
                    team_analysis['position_risks'][position].append(prediction['injury_probability'])
                    
                except Exception as e:
                    logger.warning(f"Could not analyze {player.name}: {str(e)}")
            
            # Calculate position averages
            for position, risks in team_analysis['position_risks'].items():
                team_analysis['position_risks'][position] = {
                    'avg_risk': sum(risks) / len(risks),
                    'player_count': len(risks),
                    'high_risk_count': len([r for r in risks if r > 0.5])
                }
            
            # Generate team recommendations
            high_risk_count = team_analysis['risk_distribution']['HIGH'] + team_analysis['risk_distribution']['CRITICAL']
            
            if high_risk_count > len(team_players) * 0.3:  # More than 30% high risk
                team_analysis['recommendations'].append("Consider squad rotation to manage workload")
                team_analysis['recommendations'].append("Implement team-wide injury prevention program")
            
            if team_analysis['risk_distribution']['CRITICAL'] > 0:
                team_analysis['recommendations'].append("Immediate medical review for critical risk players")
            
            return team_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing team injury risks: {str(e)}")
            return {'error': str(e)}
