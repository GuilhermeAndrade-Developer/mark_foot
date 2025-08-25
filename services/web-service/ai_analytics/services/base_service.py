# Base service class for AI models
import logging
import joblib
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from django.db import models
from django.utils import timezone

logger = logging.getLogger(__name__)


class BaseAIService:
    """Base class for all AI services"""
    
    def __init__(self, model_name: str, version: str = "1.0.0"):
        self.model_name = model_name
        self.version = version
        self.model = None
        self.is_trained = False
        
    def load_model(self, model_path: str) -> bool:
        """Load a trained model from disk"""
        try:
            if os.path.exists(model_path):
                self.model = joblib.load(model_path)
                self.is_trained = True
                logger.info(f"Model {self.model_name} loaded successfully from {model_path}")
                return True
        except Exception as e:
            logger.error(f"Error loading model {self.model_name}: {str(e)}")
        return False
        
    def save_model(self, model_path: str) -> bool:
        """Save trained model to disk"""
        try:
            if self.model is not None:
                os.makedirs(os.path.dirname(model_path), exist_ok=True)
                joblib.dump(self.model, model_path)
                logger.info(f"Model {self.model_name} saved successfully to {model_path}")
                return True
        except Exception as e:
            logger.error(f"Error saving model {self.model_name}: {str(e)}")
        return False
        
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for model training/prediction"""
        # Override in subclasses
        return data
        
    def validate_input(self, data: Any) -> bool:
        """Validate input data"""
        # Override in subclasses
        return True
        
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            'name': self.model_name,
            'version': self.version,
            'is_trained': self.is_trained,
            'created_at': datetime.now().isoformat()
        }


class DataPreparationMixin:
    """Mixin for common data preparation methods"""
    
    @staticmethod
    def fill_missing_values(df: pd.DataFrame, strategy: str = 'mean') -> pd.DataFrame:
        """Fill missing values in dataframe"""
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        if strategy == 'mean':
            df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].mean())
        elif strategy == 'median':
            df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].median())
        elif strategy == 'zero':
            df[numeric_columns] = df[numeric_columns].fillna(0)
            
        # Fill categorical with mode or 'Unknown'
        categorical_columns = df.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            df[col] = df[col].fillna(df[col].mode().iloc[0] if not df[col].mode().empty else 'Unknown')
            
        return df
    
    @staticmethod
    def create_rolling_features(df: pd.DataFrame, windows: List[int] = [3, 5, 10]) -> pd.DataFrame:
        """Create rolling window features"""
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for window in windows:
            for col in numeric_columns:
                df[f'{col}_rolling_{window}'] = df[col].rolling(window=window, min_periods=1).mean()
                df[f'{col}_rolling_std_{window}'] = df[col].rolling(window=window, min_periods=1).std()
                
        return df
    
    @staticmethod
    def create_lag_features(df: pd.DataFrame, lags: List[int] = [1, 2, 3]) -> pd.DataFrame:
        """Create lagged features"""
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for lag in lags:
            for col in numeric_columns:
                df[f'{col}_lag_{lag}'] = df[col].shift(lag)
                
        return df
    
    @staticmethod
    def normalize_features(df: pd.DataFrame, method: str = 'standard') -> Tuple[pd.DataFrame, Dict]:
        """Normalize features"""
        from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        if method == 'standard':
            scaler = StandardScaler()
        elif method == 'minmax':
            scaler = MinMaxScaler()
        elif method == 'robust':
            scaler = RobustScaler()
        else:
            raise ValueError(f"Unknown normalization method: {method}")
            
        df_scaled = df.copy()
        df_scaled[numeric_columns] = scaler.fit_transform(df[numeric_columns])
        
        scaler_info = {
            'method': method,
            'feature_names': list(numeric_columns),
            'scaler': scaler
        }
        
        return df_scaled, scaler_info


class ModelEvaluationMixin:
    """Mixin for model evaluation methods"""
    
    @staticmethod
    def calculate_regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Calculate regression metrics"""
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
        
        return {
            'mse': mean_squared_error(y_true, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
            'mae': mean_absolute_error(y_true, y_pred),
            'r2': r2_score(y_true, y_pred),
            'mape': np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        }
    
    @staticmethod
    def calculate_classification_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_pred_proba: Optional[np.ndarray] = None) -> Dict[str, float]:
        """Calculate classification metrics"""
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
        
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, average='weighted'),
            'recall': recall_score(y_true, y_pred, average='weighted'),
            'f1': f1_score(y_true, y_pred, average='weighted')
        }
        
        if y_pred_proba is not None:
            try:
                metrics['auc'] = roc_auc_score(y_true, y_pred_proba, multi_class='ovr')
            except ValueError:
                # Binary classification
                metrics['auc'] = roc_auc_score(y_true, y_pred_proba[:, 1] if y_pred_proba.ndim > 1 else y_pred_proba)
                
        return metrics
    
    @staticmethod
    def cross_validate_model(model, X: pd.DataFrame, y: pd.Series, cv: int = 5, scoring: str = 'accuracy') -> Dict[str, float]:
        """Perform cross-validation"""
        from sklearn.model_selection import cross_val_score
        
        scores = cross_val_score(model, X, y, cv=cv, scoring=scoring)
        
        return {
            'mean_score': scores.mean(),
            'std_score': scores.std(),
            'scores': scores.tolist()
        }


class FeatureEngineeringMixin:
    """Mixin for feature engineering methods"""
    
    @staticmethod
    def create_team_features(team_stats: pd.DataFrame) -> pd.DataFrame:
        """Create team-level features"""
        # Goals per game
        team_stats['goals_per_game'] = team_stats['goals_scored'] / team_stats['games_played']
        team_stats['goals_conceded_per_game'] = team_stats['goals_conceded'] / team_stats['games_played']
        
        # Goal difference
        team_stats['goal_difference'] = team_stats['goals_scored'] - team_stats['goals_conceded']
        team_stats['goal_difference_per_game'] = team_stats['goal_difference'] / team_stats['games_played']
        
        # Win/draw/loss ratios
        team_stats['win_ratio'] = team_stats['wins'] / team_stats['games_played']
        team_stats['draw_ratio'] = team_stats['draws'] / team_stats['games_played']
        team_stats['loss_ratio'] = team_stats['losses'] / team_stats['games_played']
        
        # Points per game
        team_stats['points'] = team_stats['wins'] * 3 + team_stats['draws']
        team_stats['points_per_game'] = team_stats['points'] / team_stats['games_played']
        
        return team_stats
    
    @staticmethod
    def create_player_features(player_stats: pd.DataFrame) -> pd.DataFrame:
        """Create player-level features"""
        # Goals per game
        player_stats['goals_per_game'] = player_stats['goals'] / np.maximum(player_stats['appearances'], 1)
        player_stats['assists_per_game'] = player_stats['assists'] / np.maximum(player_stats['appearances'], 1)
        player_stats['minutes_per_game'] = player_stats['minutes_played'] / np.maximum(player_stats['appearances'], 1)
        
        # Efficiency metrics
        player_stats['goal_involvement'] = player_stats['goals'] + player_stats['assists']
        player_stats['goal_involvement_per_game'] = player_stats['goal_involvement'] / np.maximum(player_stats['appearances'], 1)
        
        # Disciplinary metrics
        player_stats['cards_per_game'] = (player_stats['yellow_cards'] + player_stats['red_cards']) / np.maximum(player_stats['appearances'], 1)
        
        # Performance consistency (coefficient of variation)
        if 'goals_per_match' in player_stats.columns:
            player_stats['goal_consistency'] = player_stats['goals_per_match'].std() / np.maximum(player_stats['goals_per_match'].mean(), 0.1)
        
        return player_stats
    
    @staticmethod
    def create_match_features(match_data: pd.DataFrame) -> pd.DataFrame:
        """Create match-level features"""
        # Head-to-head history
        match_data['h2h_home_wins'] = 0  # To be filled with historical data
        match_data['h2h_away_wins'] = 0
        match_data['h2h_draws'] = 0
        
        # Form features (last 5 games)
        match_data['home_form'] = 0  # To be filled with form calculation
        match_data['away_form'] = 0
        
        # Days since last match
        match_data['home_rest_days'] = 0
        match_data['away_rest_days'] = 0
        
        # Home advantage
        match_data['is_home_game'] = 1  # For home team
        
        return match_data


class AIModelFactory:
    """Factory class for creating AI models"""
    
    @staticmethod
    def create_classifier(model_type: str, **kwargs):
        """Create a classification model"""
        if model_type == 'random_forest':
            from sklearn.ensemble import RandomForestClassifier
            return RandomForestClassifier(**kwargs)
        elif model_type == 'xgboost':
            import xgboost as xgb
            return xgb.XGBClassifier(**kwargs)
        elif model_type == 'lightgbm':
            import lightgbm as lgb
            return lgb.LGBMClassifier(**kwargs)
        elif model_type == 'logistic':
            from sklearn.linear_model import LogisticRegression
            return LogisticRegression(**kwargs)
        else:
            raise ValueError(f"Unknown classifier type: {model_type}")
    
    @staticmethod
    def create_regressor(model_type: str, **kwargs):
        """Create a regression model"""
        if model_type == 'random_forest':
            from sklearn.ensemble import RandomForestRegressor
            return RandomForestRegressor(**kwargs)
        elif model_type == 'xgboost':
            import xgboost as xgb
            return xgb.XGBRegressor(**kwargs)
        elif model_type == 'lightgbm':
            import lightgbm as lgb
            return lgb.LGBMRegressor(**kwargs)
        elif model_type == 'linear':
            from sklearn.linear_model import LinearRegression
            return LinearRegression(**kwargs)
        elif model_type == 'ridge':
            from sklearn.linear_model import Ridge
            return Ridge(**kwargs)
        else:
            raise ValueError(f"Unknown regressor type: {model_type}")
    
    @staticmethod
    def create_clusterer(model_type: str, **kwargs):
        """Create a clustering model"""
        if model_type == 'kmeans':
            from sklearn.cluster import KMeans
            return KMeans(**kwargs)
        elif model_type == 'dbscan':
            from sklearn.cluster import DBSCAN
            return DBSCAN(**kwargs)
        elif model_type == 'hierarchical':
            from sklearn.cluster import AgglomerativeClustering
            return AgglomerativeClustering(**kwargs)
        else:
            raise ValueError(f"Unknown clustering type: {model_type}")
