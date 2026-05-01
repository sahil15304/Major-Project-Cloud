"""
Model loading and management module.
Handles initialization of XGBoost models from joblib files.
Models are loaded once at startup and cached in memory.
"""

import joblib
import logging
import os
from pathlib import Path
from typing import Optional, Dict
import json

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages loading and caching of pre-trained XGBoost models."""
    
    def __init__(self, models_dir: str):
        """
        Initialize the model manager.
        
        Args:
            models_dir: Directory containing the .joblib model files
        """
        self.models_dir = Path(models_dir)
        self.models = {}
        self.model_metadata = {}
        self.is_loaded = False
        
    def load_all_models(self) -> bool:
        """
        Load all required models from disk.
        
        Returns:
            bool: True if all models loaded successfully, False otherwise
            
        Raises:
            FileNotFoundError: If any required model file is missing
            Exception: If joblib fails to load a model
        """
        try:
            model_files = {
                'severity_6m': 'xgb_sev_6m.joblib',
                'severity_12m': 'xgb_sev_12m.joblib',
                'severity_24m': 'xgb_sev_24m.joblib'
            }
            
            for model_name, filename in model_files.items():
                model_path = self.models_dir / filename
                
                if not model_path.exists():
                    raise FileNotFoundError(
                        f"Model file not found: {model_path}"
                    )
                
                logger.info(f"Loading model: {model_name} from {model_path}")
                self.models[model_name] = joblib.load(model_path)
                
                # Try to load metadata if available
                metadata_path = self.models_dir / f"{model_name}.modelcard.json"
                if metadata_path.exists():
                    with open(metadata_path, 'r') as f:
                        self.model_metadata[model_name] = json.load(f)
                
                logger.info(f"✓ Successfully loaded: {model_name}")
            
            self.is_loaded = True
            logger.info("All models loaded successfully!")
            return True
            
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise
    
    def predict(self, model_name: str, features: list) -> float:
        """
        Make prediction using specified model.
        
        Args:
            model_name: Name of the model ('severity_6m', 'severity_12m', 'severity_24m')
            features: List of features in order [NP1TOT, NP2TOT, NP3TOT, MCATOT]
            
        Returns:
            float: Predicted severity value
            
        Raises:
            ValueError: If model not found or not loaded
            Exception: If prediction fails
        """
        if not self.is_loaded:
            raise ValueError("Models not loaded. Call load_all_models() first.")
        
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not found. Available models: {list(self.models.keys())}")
        
        try:
            # Reshape features for sklearn format: [[feature1, feature2, feature3, feature4]]
            prediction = self.models[model_name].predict([features])[0]
            return float(prediction)
        except Exception as e:
            logger.error(f"Prediction error for {model_name}: {e}")
            raise
    
    def get_model_status(self) -> Dict:
        """
        Get status of all loaded models.
        
        Returns:
            dict: Status information about loaded models
        """
        return {
            'is_loaded': self.is_loaded,
            'models': list(self.models.keys()),
            'count': len(self.models),
            'metadata_available': list(self.model_metadata.keys())
        }
    
    def get_model_info(self, model_name: str) -> Dict:
        """
        Get metadata information about a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            dict: Model metadata if available
        """
        return self.model_metadata.get(model_name, {})
