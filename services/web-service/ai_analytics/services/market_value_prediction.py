import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from django.db.models import Q, Count, Avg
from django.utils import timezone

from core.models import Player, PlayerStatistics, Season, Team
from ai_analytics.models import MarketValuePrediction
from .base_service import BaseAIService, DataPreparationMixin, ModelEvaluationMixin, AIModelFactory

logger = logging.getLogger(__name__)


class MarketValuePredictionService(BaseAIService, DataPreparationMixin, ModelEvaluationMixin):
    """Service for predicting player market values"""
    
    def __init__(self):
        super().__init__("market_value_prediction", "1.0.0")
        self.value_model = None
        
    def collect_player_value_data(self, seasons: int = 3) -> pd.DataFrame:
        """Collect player data for market value analysis"""
        try:
            cutoff_date = timezone.now() - timedelta(days=365 * seasons)
            
            # Get player statistics
            stats = PlayerStatistics.objects.filter(
                season__start_date__gte=cutoff_date
            ).select_related('player', 'season', 'competition').prefetch_related('player__team')
            
            data = []
            for stat in stats:
                player = stat.player
                
                # Calculate performance metrics
                performance_metrics = self._calculate_performance_metrics(stat)
                
                # Calculate market factors
                market_factors = self._calculate_market_factors(player, stat)
                
                # Simulate current market value (in real implementation, this would be actual data)
                current_value = self._simulate_market_value(player, performance_metrics, market_factors)
                
                player_data = {
                    'player_id': player.id,
                    'player_name': player.name,
                    'age': player.age or 25,
                    'position_category': player.position_category or 'MF',
                    'nationality': player.nationality or 'Unknown',
                    'team_id': player.team.id if player.team else None,
                    'season_id': stat.season.id,
                    
                    # Performance metrics
                    'appearances': stat.appearances,
                    'goals': stat.goals,
                    'assists': stat.assists,
                    'minutes_played': stat.minutes_played,
                    'rating': float(stat.rating) if stat.rating else 7.0,
                    
                    # Calculated performance metrics
                    'goals_per_game': performance_metrics['goals_per_game'],
                    'assists_per_game': performance_metrics['assists_per_game'],
                    'minutes_per_game': performance_metrics['minutes_per_game'],
                    'goal_involvement': performance_metrics['goal_involvement'],
                    'performance_score': performance_metrics['performance_score'],
                    
                    # Market factors
                    'age_factor': market_factors['age_factor'],
                    'position_factor': market_factors['position_factor'],
                    'league_factor': market_factors['league_factor'],
                    'nationality_factor': market_factors['nationality_factor'],
                    'contract_factor': market_factors['contract_factor'],
                    'hype_factor': market_factors['hype_factor'],
                    
                    # Derived features
                    'is_young_talent': 1 if player.age and player.age <= 23 else 0,
                    'is_peak_age': 1 if player.age and 24 <= player.age <= 28 else 0,
                    'is_experienced': 1 if player.age and player.age >= 29 else 0,
                    'is_key_player': 1 if stat.starts > stat.appearances * 0.8 else 0,
                    'is_goal_threat': 1 if performance_metrics['goals_per_game'] > 0.3 else 0,
                    'is_creative': 1 if performance_metrics['assists_per_game'] > 0.2 else 0,
                    'is_consistent': 1 if performance_metrics['performance_score'] > 7.5 else 0,
                    
                    # Target variable (market value in EUR)
                    'market_value': current_value
                }
                
                data.append(player_data)
            
            df = pd.DataFrame(data)
            logger.info(f"Collected market value data for {len(df)} player-season combinations")
            return df
            
        except Exception as e:
            logger.error(f"Error collecting market value data: {str(e)}")
            return pd.DataFrame()
    
    def _calculate_performance_metrics(self, stats: PlayerStatistics) -> Dict[str, float]:
        """Calculate performance metrics for market value assessment"""
        appearances = max(stats.appearances, 1)
        
        goals_per_game = stats.goals / appearances
        assists_per_game = stats.assists / appearances
        minutes_per_game = stats.minutes_played / appearances
        
        # Goal involvement (goals + assists)
        goal_involvement = goals_per_game + assists_per_game
        
        # Performance score calculation
        base_rating = float(stats.rating) if stats.rating else 7.0
        performance_bonus = goal_involvement * 2
        consistency_bonus = 1 if minutes_per_game > 60 else 0.5
        
        performance_score = base_rating + performance_bonus + consistency_bonus
        performance_score = min(10, max(0, performance_score))  # Normalize to 0-10
        
        return {
            'goals_per_game': goals_per_game,
            'assists_per_game': assists_per_game,
            'minutes_per_game': minutes_per_game,
            'goal_involvement': goal_involvement,
            'performance_score': performance_score
        }
    
    def _calculate_market_factors(self, player: Player, stats: PlayerStatistics) -> Dict[str, float]:
        """Calculate market factors that affect player value"""
        age = player.age or 25
        position = player.position_category or 'MF'
        nationality = player.nationality or 'Unknown'
        
        # Age factor (peak value around 24-27)
        if age <= 20:
            age_factor = 0.7  # Young, potential but unproven
        elif age <= 23:
            age_factor = 1.2  # Rising talent
        elif age <= 27:
            age_factor = 1.0  # Peak age
        elif age <= 30:
            age_factor = 0.8  # Still valuable but declining
        else:
            age_factor = 0.5  # Veteran, lower value
        
        # Position factor (attacking players typically more expensive)
        position_factors = {
            'GK': 0.6,  # Specialized but lower transfer fees
            'DF': 0.8,  # Important but generally lower fees
            'MF': 1.0,  # Balanced
            'FW': 1.3   # Highest transfer fees for goal scorers
        }
        position_factor = position_factors.get(position, 1.0)
        
        # League factor (simplified - would be based on actual league strength)
        # For now, assume all teams are in similar strength leagues
        league_factor = 1.0
        
        # Nationality factor (some nationalities have premium)
        premium_nationalities = ['Brazil', 'Argentina', 'France', 'Germany', 'Spain', 'England']
        nationality_factor = 1.2 if nationality in premium_nationalities else 1.0
        
        # Contract factor (simplified - assuming average contract situation)
        contract_factor = 1.0
        
        # Hype factor (based on performance and age)
        performance_score = self._calculate_performance_metrics(stats)['performance_score']
        if age <= 23 and performance_score > 8.0:
            hype_factor = 1.5  # Young superstar
        elif performance_score > 8.5:
            hype_factor = 1.2  # Proven star
        elif performance_score > 7.5:
            hype_factor = 1.0  # Good player
        else:
            hype_factor = 0.8  # Average player
        
        return {
            'age_factor': age_factor,
            'position_factor': position_factor,
            'league_factor': league_factor,
            'nationality_factor': nationality_factor,
            'contract_factor': contract_factor,
            'hype_factor': hype_factor
        }
    
    def _simulate_market_value(self, player: Player, performance: Dict, factors: Dict) -> float:
        """Simulate market value based on performance and factors"""
        try:
            # Base value calculation
            base_value = 1000000  # 1M EUR base
            
            # Performance multiplier
            performance_multiplier = performance['performance_score'] / 5.0  # 0.0 to 2.0
            
            # Goals and assists bonus
            offensive_bonus = (performance['goals_per_game'] + performance['assists_per_game']) * 5000000
            
            # Apply all factors
            total_factor = (
                factors['age_factor'] *
                factors['position_factor'] *
                factors['league_factor'] *
                factors['nationality_factor'] *
                factors['contract_factor'] *
                factors['hype_factor']
            )
            
            # Calculate final value
            market_value = (base_value * performance_multiplier + offensive_bonus) * total_factor
            
            # Add some randomness to simulate market volatility
            volatility = np.random.normal(1.0, 0.1)  # ±10% volatility
            market_value *= volatility
            
            # Apply reasonable bounds
            market_value = max(50000, min(200000000, market_value))  # 50K to 200M EUR
            
            return round(market_value, -3)  # Round to nearest thousand
            
        except Exception as e:
            logger.error(f"Error simulating market value: {str(e)}")
            return 1000000  # Default 1M EUR
    
    def train_value_model(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Train market value prediction model"""
        results = {}
        
        if data.empty:
            return {'error': 'No training data available'}
        
        # Prepare features
        feature_columns = [
            'age', 'appearances', 'goals_per_game', 'assists_per_game', 'minutes_per_game',
            'rating', 'performance_score', 'goal_involvement',
            'age_factor', 'position_factor', 'nationality_factor', 'hype_factor',
            'is_young_talent', 'is_peak_age', 'is_experienced',
            'is_key_player', 'is_goal_threat', 'is_creative', 'is_consistent'
        ]
        
        # Handle categorical variables
        data_encoded = pd.get_dummies(data, columns=['position_category'], prefix='pos')
        
        # Update feature columns to include encoded positions
        position_cols = [col for col in data_encoded.columns if col.startswith('pos_')]
        feature_columns.extend(position_cols)
        
        X = data_encoded[feature_columns].fillna(0)
        y = data_encoded['market_value']
        
        # Train market value model
        try:
            self.value_model = AIModelFactory.create_regressor('random_forest', n_estimators=100, random_state=42)
            self.value_model.fit(X, y)
            
            # Evaluate model
            y_pred = self.value_model.predict(X)
            value_metrics = self.calculate_regression_metrics(y.values, y_pred)
            
            results['value_model'] = {
                'rmse': value_metrics['rmse'],
                'mae': value_metrics['mae'],
                'r2': value_metrics['r2'],
                'mape': value_metrics['mape'],
                'feature_importance': dict(zip(feature_columns, self.value_model.feature_importances_))
            }
            
            logger.info(f"Market value model trained with R²: {value_metrics['r2']:.3f}")
            
        except Exception as e:
            logger.error(f"Error training value model: {str(e)}")
            results['value_model'] = {'error': str(e)}
        
        self.is_trained = True
        return results
    
    def predict_market_value(self, player: Player, season: Optional[Season] = None) -> Dict[str, Any]:
        """Predict market value for a specific player"""
        if not self.is_trained:
            raise ValueError("Model not trained. Call train_value_model() first.")
        
        try:
            # Get player's recent statistics
            recent_stats = PlayerStatistics.objects.filter(
                player=player
            ).order_by('-season__start_date').first()
            
            if not recent_stats:
                logger.warning(f"No statistics found for player {player.name}")
                return self._default_value_prediction(player)
            
            # Calculate metrics and factors
            performance_metrics = self._calculate_performance_metrics(recent_stats)
            market_factors = self._calculate_market_factors(player, recent_stats)
            
            # Prepare features for prediction
            features = pd.DataFrame([{
                'age': player.age or 25,
                'appearances': recent_stats.appearances,
                'goals_per_game': performance_metrics['goals_per_game'],
                'assists_per_game': performance_metrics['assists_per_game'],
                'minutes_per_game': performance_metrics['minutes_per_game'],
                'rating': float(recent_stats.rating) if recent_stats.rating else 7.0,
                'performance_score': performance_metrics['performance_score'],
                'goal_involvement': performance_metrics['goal_involvement'],
                'age_factor': market_factors['age_factor'],
                'position_factor': market_factors['position_factor'],
                'nationality_factor': market_factors['nationality_factor'],
                'hype_factor': market_factors['hype_factor'],
                'is_young_talent': 1 if player.age and player.age <= 23 else 0,
                'is_peak_age': 1 if player.age and 24 <= player.age <= 28 else 0,
                'is_experienced': 1 if player.age and player.age >= 29 else 0,
                'is_key_player': 1 if recent_stats.starts > recent_stats.appearances * 0.8 else 0,
                'is_goal_threat': 1 if performance_metrics['goals_per_game'] > 0.3 else 0,
                'is_creative': 1 if performance_metrics['assists_per_game'] > 0.2 else 0,
                'is_consistent': 1 if performance_metrics['performance_score'] > 7.5 else 0,
                
                # Position encoding
                'pos_DF': 1 if player.position_category == 'DF' else 0,
                'pos_FW': 1 if player.position_category == 'FW' else 0,
                'pos_GK': 1 if player.position_category == 'GK' else 0,
                'pos_MF': 1 if player.position_category == 'MF' else 0,
            }])
            
            # Make prediction
            if self.value_model:
                predicted_value = self.value_model.predict(features)[0]
                
                # Calculate confidence interval (simplified)
                std_error = predicted_value * 0.2  # Assume 20% standard error
                confidence_low = max(50000, predicted_value - 1.96 * std_error)
                confidence_high = predicted_value + 1.96 * std_error
                
                # Analyze value factors
                value_factors = self._analyze_value_factors(player, performance_metrics, market_factors)
                
                # Generate trend analysis
                trend_analysis = self._analyze_value_trend(player, predicted_value)
                
                # Find comparable players
                comparable_players = self._find_comparable_players(player, predicted_value)
                
                prediction_result = {
                    'player_id': player.id,
                    'player_name': player.name,
                    'predicted_value': float(predicted_value),
                    'currency': 'EUR',
                    'confidence_interval': {
                        'low': float(confidence_low),
                        'high': float(confidence_high)
                    },
                    'value_factors': value_factors,
                    'trend_analysis': trend_analysis,
                    'comparable_players': comparable_players,
                    'value_breakdown': {
                        'base_performance': performance_metrics['performance_score'] * 1000000,
                        'offensive_contribution': (performance_metrics['goals_per_game'] + performance_metrics['assists_per_game']) * 5000000,
                        'age_adjustment': market_factors['age_factor'],
                        'position_premium': market_factors['position_factor'],
                        'nationality_premium': market_factors['nationality_factor']
                    }
                }
                
                return prediction_result
            else:
                return self._default_value_prediction(player)
                
        except Exception as e:
            logger.error(f"Error predicting market value: {str(e)}")
            return self._default_value_prediction(player)
    
    def _default_value_prediction(self, player: Player) -> Dict[str, Any]:
        """Return default value prediction when model is not available"""
        age = player.age or 25
        position = player.position_category or 'MF'
        
        # Simple position and age-based valuation
        base_values = {'GK': 2000000, 'DF': 5000000, 'MF': 8000000, 'FW': 12000000}
        base_value = base_values.get(position, 5000000)
        
        # Age adjustment
        if age <= 23:
            age_multiplier = 1.5
        elif age <= 27:
            age_multiplier = 1.0
        elif age <= 30:
            age_multiplier = 0.7
        else:
            age_multiplier = 0.4
        
        predicted_value = base_value * age_multiplier
        
        return {
            'player_id': player.id,
            'player_name': player.name,
            'predicted_value': predicted_value,
            'currency': 'EUR',
            'confidence_interval': {
                'low': predicted_value * 0.7,
                'high': predicted_value * 1.3
            },
            'value_factors': {'age': age_multiplier, 'position': base_value},
            'note': 'Prediction based on default model (limited data available)'
        }
    
    def _analyze_value_factors(self, player: Player, performance: Dict, factors: Dict) -> Dict[str, Any]:
        """Analyze factors contributing to player value"""
        return {
            'primary_factors': {
                'performance_score': performance['performance_score'],
                'goal_involvement': performance['goal_involvement'],
                'age': player.age,
                'position': player.position_category
            },
            'market_multipliers': {
                'age_factor': factors['age_factor'],
                'position_factor': factors['position_factor'],
                'nationality_factor': factors['nationality_factor'],
                'hype_factor': factors['hype_factor']
            },
            'strengths': self._identify_value_strengths(player, performance),
            'weaknesses': self._identify_value_weaknesses(player, performance)
        }
    
    def _identify_value_strengths(self, player: Player, performance: Dict) -> List[str]:
        """Identify factors that increase player value"""
        strengths = []
        
        if player.age and player.age <= 23:
            strengths.append("Young age with high potential")
        
        if performance['goals_per_game'] > 0.5:
            strengths.append("Excellent goal-scoring record")
        
        if performance['assists_per_game'] > 0.3:
            strengths.append("High assist production")
        
        if performance['performance_score'] > 8.0:
            strengths.append("Consistently high performance ratings")
        
        if player.position_category == 'FW':
            strengths.append("Striker position commands premium")
        
        if performance['minutes_per_game'] > 70:
            strengths.append("Regular starter with high playing time")
        
        return strengths
    
    def _identify_value_weaknesses(self, player: Player, performance: Dict) -> List[str]:
        """Identify factors that decrease player value"""
        weaknesses = []
        
        if player.age and player.age > 30:
            weaknesses.append("Advanced age may limit future value")
        
        if performance['goals_per_game'] < 0.1 and player.position_category == 'FW':
            weaknesses.append("Low goal output for attacking player")
        
        if performance['performance_score'] < 6.5:
            weaknesses.append("Below average performance ratings")
        
        if performance['minutes_per_game'] < 45:
            weaknesses.append("Limited playing time indicates squad role")
        
        return weaknesses
    
    def _analyze_value_trend(self, player: Player, current_value: float) -> Dict[str, Any]:
        """Analyze predicted value trend"""
        age = player.age or 25
        
        # Predict value in 1-2 years based on age trajectory
        if age <= 22:
            trend = "increasing"
            future_multiplier = 1.3
            trend_reason = "Young player entering peak years"
        elif age <= 26:
            trend = "stable"
            future_multiplier = 1.0
            trend_reason = "Player in peak age range"
        elif age <= 29:
            trend = "gradually_declining"
            future_multiplier = 0.9
            trend_reason = "Approaching end of peak years"
        else:
            trend = "declining"
            future_multiplier = 0.7
            trend_reason = "Advanced age affecting market value"
        
        return {
            'current_trend': trend,
            'future_value_estimate': current_value * future_multiplier,
            'trend_reason': trend_reason,
            'optimal_transfer_window': "next_2_years" if future_multiplier >= 1.0 else "immediate"
        }
    
    def _find_comparable_players(self, player: Player, predicted_value: float) -> List[Dict[str, Any]]:
        """Find players with similar market value and characteristics"""
        try:
            # Get players in similar value range and position
            value_range = predicted_value * 0.3  # ±30%
            similar_players = Player.objects.filter(
                position_category=player.position_category,
                age__range=(max(16, (player.age or 25) - 3), min(40, (player.age or 25) + 3))
            ).exclude(id=player.id)[:5]
            
            comparables = []
            for similar_player in similar_players:
                # Simulate their value for comparison
                try:
                    similar_prediction = self.predict_market_value(similar_player)
                    if abs(similar_prediction['predicted_value'] - predicted_value) <= value_range:
                        comparables.append({
                            'name': similar_player.name,
                            'age': similar_player.age,
                            'position': similar_player.position_category,
                            'team': similar_player.team.name if similar_player.team else 'Free Agent',
                            'estimated_value': similar_prediction['predicted_value']
                        })
                except:
                    continue
            
            return comparables[:3]  # Return top 3 comparable players
            
        except Exception as e:
            logger.error(f"Error finding comparable players: {str(e)}")
            return []
    
    def save_market_value_prediction(self, player: Player, prediction_data: Dict[str, Any], season: Optional[Season] = None) -> MarketValuePrediction:
        """Save market value prediction to database"""
        try:
            if not season:
                season = Season.objects.filter(
                    start_date__lte=timezone.now().date(),
                    end_date__gte=timezone.now().date()
                ).first() or Season.objects.order_by('-start_date').first()
            
            market_prediction = MarketValuePrediction.objects.create(
                player=player,
                predicted_value=prediction_data['predicted_value'],
                currency=prediction_data['currency'],
                confidence_interval_low=prediction_data['confidence_interval']['low'],
                confidence_interval_high=prediction_data['confidence_interval']['high'],
                value_factors=prediction_data['value_factors'],
                trend_analysis=prediction_data['trend_analysis'],
                comparable_players=prediction_data['comparable_players'],
                model_version=self.version,
                prediction_date=timezone.now(),
                season=season
            )
            
            logger.info(f"Saved market value prediction for {player.name}: €{prediction_data['predicted_value']:,.0f}")
            return market_prediction
            
        except Exception as e:
            logger.error(f"Error saving market value prediction: {str(e)}")
            raise
