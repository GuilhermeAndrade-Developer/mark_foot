import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from django.db.models import Q, Count, Avg
from django.utils import timezone

from core.models import Match, Team, Season, Standing
from ai_analytics.models import MatchPrediction
from .base_service import BaseAIService, DataPreparationMixin, ModelEvaluationMixin, FeatureEngineeringMixin, AIModelFactory

logger = logging.getLogger(__name__)


class MatchPredictionService(BaseAIService, DataPreparationMixin, ModelEvaluationMixin, FeatureEngineeringMixin):
    """Service for predicting match results using historical data"""
    
    def __init__(self):
        super().__init__("match_prediction", "1.0.0")
        self.result_model = None
        self.score_model = None
        self.goals_model = None
        
    def collect_training_data(self, seasons: int = 3) -> pd.DataFrame:
        """Collect historical match data for training"""
        try:
            # Get matches from last N seasons with results
            cutoff_date = timezone.now() - timedelta(days=365 * seasons)
            
            matches = Match.objects.filter(
                utc_date__gte=cutoff_date,
                status='FINISHED',
                home_team_score__isnull=False,
                away_team_score__isnull=False
            ).select_related('home_team', 'away_team', 'competition', 'season')
            
            data = []
            for match in matches:
                # Get team form (last 5 matches before this match)
                home_form = self._calculate_team_form(match.home_team, match.utc_date, 5)
                away_form = self._calculate_team_form(match.away_team, match.utc_date, 5)
                
                # Get head-to-head record
                h2h_stats = self._get_head_to_head_stats(match.home_team, match.away_team, match.utc_date)
                
                # Get team standings before match
                home_standing = self._get_team_standing_before_match(match.home_team, match.competition, match.utc_date)
                away_standing = self._get_team_standing_before_match(match.away_team, match.competition, match.utc_date)
                
                # Calculate result
                if match.home_team_score > match.away_team_score:
                    result = 'HOME_WIN'
                    result_numeric = 1
                elif match.away_team_score > match.home_team_score:
                    result = 'AWAY_WIN' 
                    result_numeric = 2
                else:
                    result = 'DRAW'
                    result_numeric = 0
                
                match_data = {
                    'match_id': match.id,
                    'home_team_id': match.home_team.id,
                    'away_team_id': match.away_team.id,
                    'competition_id': match.competition.id,
                    'season_id': match.season.id,
                    'matchday': match.matchday or 0,
                    'is_weekend': match.utc_date.weekday() >= 5,
                    
                    # Team form features
                    'home_form_points': home_form.get('points', 0),
                    'home_form_goals_for': home_form.get('goals_for', 0),
                    'home_form_goals_against': home_form.get('goals_against', 0),
                    'home_form_wins': home_form.get('wins', 0),
                    'home_form_draws': home_form.get('draws', 0),
                    'home_form_losses': home_form.get('losses', 0),
                    
                    'away_form_points': away_form.get('points', 0),
                    'away_form_goals_for': away_form.get('goals_for', 0),
                    'away_form_goals_against': away_form.get('goals_against', 0),
                    'away_form_wins': away_form.get('wins', 0),
                    'away_form_draws': away_form.get('draws', 0),
                    'away_form_losses': away_form.get('losses', 0),
                    
                    # Head-to-head features
                    'h2h_home_wins': h2h_stats.get('home_wins', 0),
                    'h2h_away_wins': h2h_stats.get('away_wins', 0),
                    'h2h_draws': h2h_stats.get('draws', 0),
                    'h2h_total_games': h2h_stats.get('total_games', 0),
                    'h2h_avg_goals': h2h_stats.get('avg_goals', 0),
                    
                    # Standing features
                    'home_position': home_standing.get('position', 20),
                    'away_position': away_standing.get('position', 20),
                    'position_difference': home_standing.get('position', 20) - away_standing.get('position', 20),
                    'home_points': home_standing.get('points', 0),
                    'away_points': away_standing.get('points', 0),
                    'points_difference': home_standing.get('points', 0) - away_standing.get('points', 0),
                    
                    # Target variables
                    'result': result,
                    'result_numeric': result_numeric,
                    'home_goals': match.home_team_score,
                    'away_goals': match.away_team_score,
                    'total_goals': match.home_team_score + match.away_team_score,
                    'goal_difference': match.home_team_score - match.away_team_score,
                    'both_teams_scored': 1 if match.home_team_score > 0 and match.away_team_score > 0 else 0,
                    'over_2_5_goals': 1 if (match.home_team_score + match.away_team_score) > 2.5 else 0,
                }
                
                data.append(match_data)
                
            df = pd.DataFrame(data)
            logger.info(f"Collected {len(df)} matches for training")
            return df
            
        except Exception as e:
            logger.error(f"Error collecting training data: {str(e)}")
            return pd.DataFrame()
    
    def _calculate_team_form(self, team: Team, before_date: datetime, num_matches: int = 5) -> Dict[str, Any]:
        """Calculate team form in last N matches before given date"""
        try:
            recent_matches = Match.objects.filter(
                Q(home_team=team) | Q(away_team=team),
                utc_date__lt=before_date,
                status='FINISHED',
                home_team_score__isnull=False,
                away_team_score__isnull=False
            ).order_by('-utc_date')[:num_matches]
            
            if not recent_matches:
                return {'points': 0, 'goals_for': 0, 'goals_against': 0, 'wins': 0, 'draws': 0, 'losses': 0}
            
            points = 0
            goals_for = 0
            goals_against = 0
            wins = 0
            draws = 0
            losses = 0
            
            for match in recent_matches:
                if match.home_team == team:
                    team_goals = match.home_team_score
                    opponent_goals = match.away_team_score
                else:
                    team_goals = match.away_team_score
                    opponent_goals = match.home_team_score
                
                goals_for += team_goals
                goals_against += opponent_goals
                
                if team_goals > opponent_goals:
                    wins += 1
                    points += 3
                elif team_goals == opponent_goals:
                    draws += 1
                    points += 1
                else:
                    losses += 1
            
            return {
                'points': points,
                'goals_for': goals_for,
                'goals_against': goals_against,
                'wins': wins,
                'draws': draws,
                'losses': losses,
                'games_played': len(recent_matches)
            }
            
        except Exception as e:
            logger.error(f"Error calculating team form: {str(e)}")
            return {'points': 0, 'goals_for': 0, 'goals_against': 0, 'wins': 0, 'draws': 0, 'losses': 0}
    
    def _get_head_to_head_stats(self, home_team: Team, away_team: Team, before_date: datetime, limit: int = 10) -> Dict[str, Any]:
        """Get head-to-head statistics between teams"""
        try:
            h2h_matches = Match.objects.filter(
                Q(home_team=home_team, away_team=away_team) | Q(home_team=away_team, away_team=home_team),
                utc_date__lt=before_date,
                status='FINISHED',
                home_team_score__isnull=False,
                away_team_score__isnull=False
            ).order_by('-utc_date')[:limit]
            
            if not h2h_matches:
                return {'home_wins': 0, 'away_wins': 0, 'draws': 0, 'total_games': 0, 'avg_goals': 0}
            
            home_wins = 0
            away_wins = 0
            draws = 0
            total_goals = 0
            
            for match in h2h_matches:
                total_goals += match.home_team_score + match.away_team_score
                
                # Check from home_team perspective
                if match.home_team == home_team:
                    if match.home_team_score > match.away_team_score:
                        home_wins += 1
                    elif match.home_team_score < match.away_team_score:
                        away_wins += 1
                    else:
                        draws += 1
                else:  # away_team was home in this match
                    if match.home_team_score > match.away_team_score:
                        away_wins += 1
                    elif match.home_team_score < match.away_team_score:
                        home_wins += 1
                    else:
                        draws += 1
            
            return {
                'home_wins': home_wins,
                'away_wins': away_wins,
                'draws': draws,
                'total_games': len(h2h_matches),
                'avg_goals': total_goals / len(h2h_matches) if h2h_matches else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting head-to-head stats: {str(e)}")
            return {'home_wins': 0, 'away_wins': 0, 'draws': 0, 'total_games': 0, 'avg_goals': 0}
    
    def _get_team_standing_before_match(self, team: Team, competition, before_date: datetime) -> Dict[str, Any]:
        """Get team standing before a specific match"""
        try:
            # Find the most recent standing before the match date
            standing = Standing.objects.filter(
                team=team,
                competition=competition,
                last_updated__lt=before_date
            ).order_by('-last_updated').first()
            
            if standing:
                return {
                    'position': standing.position,
                    'points': standing.points,
                    'wins': standing.wins,
                    'draws': standing.draws,
                    'losses': standing.losses,
                    'goals_for': standing.goals_for,
                    'goals_against': standing.goals_against,
                    'goal_difference': standing.goal_difference
                }
            else:
                return {'position': 20, 'points': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goals_for': 0, 'goals_against': 0, 'goal_difference': 0}
                
        except Exception as e:
            logger.error(f"Error getting team standing: {str(e)}")
            return {'position': 20, 'points': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goals_for': 0, 'goals_against': 0, 'goal_difference': 0}
    
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for model training"""
        # Create additional features
        data['form_points_difference'] = data['home_form_points'] - data['away_form_points']
        data['form_goals_difference'] = (data['home_form_goals_for'] - data['home_form_goals_against']) - (data['away_form_goals_for'] - data['away_form_goals_against'])
        
        # H2H win ratios
        data['h2h_home_win_ratio'] = data['h2h_home_wins'] / np.maximum(data['h2h_total_games'], 1)
        data['h2h_away_win_ratio'] = data['h2h_away_wins'] / np.maximum(data['h2h_total_games'], 1)
        data['h2h_draw_ratio'] = data['h2h_draws'] / np.maximum(data['h2h_total_games'], 1)
        
        # Fill missing values
        data = self.fill_missing_values(data)
        
        return data
    
    def train_models(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Train all prediction models"""
        results = {}
        
        # Prepare features
        data = self.prepare_features(data)
        
        # Define feature columns
        feature_columns = [
            'home_form_points', 'away_form_points', 'form_points_difference',
            'home_form_goals_for', 'away_form_goals_for', 
            'home_form_goals_against', 'away_form_goals_against', 'form_goals_difference',
            'h2h_home_wins', 'h2h_away_wins', 'h2h_draws', 'h2h_total_games', 'h2h_avg_goals',
            'h2h_home_win_ratio', 'h2h_away_win_ratio', 'h2h_draw_ratio',
            'home_position', 'away_position', 'position_difference',
            'home_points', 'away_points', 'points_difference',
            'matchday', 'is_weekend'
        ]
        
        X = data[feature_columns]
        
        # Train result prediction model (1X2)
        try:
            y_result = data['result_numeric']
            self.result_model = AIModelFactory.create_classifier('random_forest', n_estimators=100, random_state=42)
            self.result_model.fit(X, y_result)
            
            # Evaluate result model
            result_scores = self.cross_validate_model(self.result_model, X, y_result, cv=5, scoring='accuracy')
            results['result_model'] = {
                'accuracy': result_scores['mean_score'],
                'accuracy_std': result_scores['std_score'],
                'feature_importance': dict(zip(feature_columns, self.result_model.feature_importances_))
            }
            logger.info(f"Result prediction model trained with accuracy: {result_scores['mean_score']:.3f}")
            
        except Exception as e:
            logger.error(f"Error training result model: {str(e)}")
            results['result_model'] = {'error': str(e)}
        
        # Train total goals model
        try:
            y_goals = data['total_goals']
            self.goals_model = AIModelFactory.create_regressor('random_forest', n_estimators=100, random_state=42)
            self.goals_model.fit(X, y_goals)
            
            # Evaluate goals model
            goals_pred = self.goals_model.predict(X)
            goals_metrics = self.calculate_regression_metrics(y_goals.values, goals_pred)
            results['goals_model'] = {
                'rmse': goals_metrics['rmse'],
                'mae': goals_metrics['mae'],
                'r2': goals_metrics['r2'],
                'feature_importance': dict(zip(feature_columns, self.goals_model.feature_importances_))
            }
            logger.info(f"Goals prediction model trained with RMSE: {goals_metrics['rmse']:.3f}")
            
        except Exception as e:
            logger.error(f"Error training goals model: {str(e)}")
            results['goals_model'] = {'error': str(e)}
        
        self.is_trained = True
        return results
    
    def predict_match(self, home_team: Team, away_team: Team, match_date: datetime, competition = None) -> Dict[str, Any]:
        """Predict outcome for a specific match"""
        if not self.is_trained:
            raise ValueError("Models not trained. Call train_models() first.")
        
        try:
            # Collect match features
            home_form = self._calculate_team_form(home_team, match_date, 5)
            away_form = self._calculate_team_form(away_team, match_date, 5)
            h2h_stats = self._get_head_to_head_stats(home_team, away_team, match_date)
            
            # Get current standings if competition provided
            home_standing = {'position': 10, 'points': 15}
            away_standing = {'position': 10, 'points': 15}
            if competition:
                home_standing = self._get_team_standing_before_match(home_team, competition, match_date)
                away_standing = self._get_team_standing_before_match(away_team, competition, match_date)
            
            # Create feature vector
            features = pd.DataFrame([{
                'home_form_points': home_form.get('points', 0),
                'away_form_points': away_form.get('points', 0),
                'form_points_difference': home_form.get('points', 0) - away_form.get('points', 0),
                'home_form_goals_for': home_form.get('goals_for', 0),
                'away_form_goals_for': away_form.get('goals_for', 0),
                'home_form_goals_against': home_form.get('goals_against', 0),
                'away_form_goals_against': away_form.get('goals_against', 0),
                'form_goals_difference': (home_form.get('goals_for', 0) - home_form.get('goals_against', 0)) - (away_form.get('goals_for', 0) - away_form.get('goals_against', 0)),
                'h2h_home_wins': h2h_stats.get('home_wins', 0),
                'h2h_away_wins': h2h_stats.get('away_wins', 0),
                'h2h_draws': h2h_stats.get('draws', 0),
                'h2h_total_games': h2h_stats.get('total_games', 0),
                'h2h_avg_goals': h2h_stats.get('avg_goals', 0),
                'h2h_home_win_ratio': h2h_stats.get('home_wins', 0) / max(h2h_stats.get('total_games', 1), 1),
                'h2h_away_win_ratio': h2h_stats.get('away_wins', 0) / max(h2h_stats.get('total_games', 1), 1),
                'h2h_draw_ratio': h2h_stats.get('draws', 0) / max(h2h_stats.get('total_games', 1), 1),
                'home_position': home_standing.get('position', 10),
                'away_position': away_standing.get('position', 10),
                'position_difference': home_standing.get('position', 10) - away_standing.get('position', 10),
                'home_points': home_standing.get('points', 15),
                'away_points': away_standing.get('points', 15),
                'points_difference': home_standing.get('points', 15) - away_standing.get('points', 15),
                'matchday': 1,
                'is_weekend': match_date.weekday() >= 5
            }])
            
            predictions = {}
            
            # Predict result
            if self.result_model:
                result_proba = self.result_model.predict_proba(features)[0]
                result_pred = self.result_model.predict(features)[0]
                
                result_mapping = {0: 'DRAW', 1: 'HOME_WIN', 2: 'AWAY_WIN'}
                predictions['result'] = {
                    'prediction': result_mapping[result_pred],
                    'probabilities': {
                        'home_win': float(result_proba[1]) if len(result_proba) > 1 else 0.33,
                        'draw': float(result_proba[0]) if len(result_proba) > 0 else 0.33,
                        'away_win': float(result_proba[2]) if len(result_proba) > 2 else 0.33
                    },
                    'confidence': float(max(result_proba))
                }
            
            # Predict total goals
            if self.goals_model:
                goals_pred = self.goals_model.predict(features)[0]
                predictions['total_goals'] = {
                    'prediction': float(goals_pred),
                    'over_2_5': 1 if goals_pred > 2.5 else 0,
                    'under_2_5': 1 if goals_pred < 2.5 else 0
                }
            
            # Add feature importance for interpretation
            if self.result_model:
                feature_importance = dict(zip(features.columns, self.result_model.feature_importances_))
                predictions['feature_analysis'] = {
                    'most_important_factors': sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5],
                    'team_form_difference': features['form_points_difference'].iloc[0],
                    'position_difference': features['position_difference'].iloc[0],
                    'h2h_advantage': 'HOME' if h2h_stats.get('home_wins', 0) > h2h_stats.get('away_wins', 0) else 'AWAY' if h2h_stats.get('away_wins', 0) > h2h_stats.get('home_wins', 0) else 'NEUTRAL'
                }
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error predicting match: {str(e)}")
            raise
    
    def save_prediction(self, match: Match, predictions: Dict[str, Any]) -> List[MatchPrediction]:
        """Save predictions to database"""
        saved_predictions = []
        
        try:
            # Save result prediction
            if 'result' in predictions:
                result_pred = MatchPrediction.objects.create(
                    match=match,
                    prediction_type='RESULT',
                    predicted_value=predictions['result']['prediction'],
                    confidence_score=predictions['result']['confidence'],
                    model_version=self.version,
                    features_used=predictions.get('feature_analysis', {})
                )
                saved_predictions.append(result_pred)
            
            # Save goals prediction
            if 'total_goals' in predictions:
                goals_pred = MatchPrediction.objects.create(
                    match=match,
                    prediction_type='GOALS',
                    predicted_value=str(round(predictions['total_goals']['prediction'], 1)),
                    confidence_score=0.8,  # Default confidence for regression
                    model_version=self.version,
                    features_used=predictions.get('feature_analysis', {})
                )
                saved_predictions.append(goals_pred)
            
            logger.info(f"Saved {len(saved_predictions)} predictions for match {match.id}")
            
        except Exception as e:
            logger.error(f"Error saving predictions: {str(e)}")
        
        return saved_predictions
    
    def evaluate_past_predictions(self, days_back: int = 30) -> Dict[str, Any]:
        """Evaluate accuracy of past predictions"""
        cutoff_date = timezone.now() - timedelta(days=days_back)
        
        predictions = MatchPrediction.objects.filter(
            created_at__gte=cutoff_date,
            match__status='FINISHED',
            actual_value__isnull=False
        ).select_related('match')
        
        if not predictions.exists():
            return {'message': 'No predictions to evaluate'}
        
        evaluation = {
            'total_predictions': predictions.count(),
            'by_type': {}
        }
        
        for pred_type in ['RESULT', 'GOALS']:
            type_predictions = predictions.filter(prediction_type=pred_type)
            if type_predictions.exists():
                correct = type_predictions.filter(predicted_value=models.F('actual_value')).count()
                accuracy = correct / type_predictions.count()
                
                evaluation['by_type'][pred_type] = {
                    'total': type_predictions.count(),
                    'correct': correct,
                    'accuracy': accuracy,
                    'average_confidence': type_predictions.aggregate(avg_conf=Avg('confidence_score'))['avg_conf']
                }
        
        return evaluation
