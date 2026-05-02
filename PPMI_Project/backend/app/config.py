"""
Configuration module for environment variables and settings.
Supports local development and AWS deployment.
"""

import os
from pathlib import Path
from typing import Optional
import json


class Settings:
    """Application settings loaded from environment variables."""
    
    # Application settings
    APP_NAME = "PPMI Parkinson's Disease Severity Prediction API"
    APP_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Server settings
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    
    # Model settings
    # Priority: S3 path > environment variable > default local path
    MODELS_SOURCE = os.getenv("MODELS_SOURCE", "local")  # "local" or "s3"
    
    # Local model path (for development and EC2 local storage)
    LOCAL_MODELS_DIR = os.getenv(
        "LOCAL_MODELS_DIR", 
        str(Path(__file__).parent.parent.parent / "models")
    )
    
    # AWS S3 settings (only used if MODELS_SOURCE="s3")
    AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET", "")
    AWS_S3_MODELS_PREFIX = os.getenv("AWS_S3_MODELS_PREFIX", "models/")
    AWS_S3_ARTIFACTS_PREFIX = os.getenv("AWS_S3_ARTIFACTS_PREFIX", "artifacts/")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    
    # IAM Role (for EC2 - no credentials needed)
    USE_IAM_ROLE = os.getenv("USE_IAM_ROLE", "False").lower() == "true"
    
    # Logging settings
    LOGS_DIR = os.getenv("LOGS_DIR", "logs")
    
    @classmethod
    def get_models_dir(cls) -> str:
        """
        Get the models directory based on configuration.
        
        Returns:
            str: Path to models directory
        """
        if cls.MODELS_SOURCE == "s3":
            return f"s3://{cls.AWS_S3_BUCKET}/{cls.AWS_S3_MODELS_PREFIX}"
        return cls.LOCAL_MODELS_DIR
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate configuration.
        
        Returns:
            bool: True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        if cls.MODELS_SOURCE == "local":
            models_path = Path(cls.LOCAL_MODELS_DIR)
            if not models_path.exists():
                raise ValueError(
                    f"Local models directory not found: {cls.LOCAL_MODELS_DIR}"
                )
        elif cls.MODELS_SOURCE == "s3":
            if not cls.AWS_S3_BUCKET:
                raise ValueError("AWS_S3_BUCKET must be set when MODELS_SOURCE='s3'")
            if not cls.AWS_S3_ARTIFACTS_PREFIX:
                raise ValueError("AWS_S3_ARTIFACTS_PREFIX must be set when using S3 artifacts")
        else:
            raise ValueError(
                f"Invalid MODELS_SOURCE: {cls.MODELS_SOURCE}. Use 'local' or 's3'"
            )
        
        return True
    
    @classmethod
    def to_dict(cls) -> dict:
        """
        Get all settings as a dictionary.
        
        Returns:
            dict: Settings as dictionary
        """
        return {
            "app_name": cls.APP_NAME,
            "app_version": cls.APP_VERSION,
            "debug": cls.DEBUG,
            "log_level": cls.LOG_LEVEL,
            "host": cls.HOST,
            "port": cls.PORT,
            "models_source": cls.MODELS_SOURCE,
            "models_dir": cls.get_models_dir(),
            "aws_s3_artifacts_prefix": cls.AWS_S3_ARTIFACTS_PREFIX if cls.MODELS_SOURCE == "s3" else None,
            "aws_region": cls.AWS_REGION if cls.MODELS_SOURCE == "s3" else None,
            "use_iam_role": cls.USE_IAM_ROLE
        }


# Global settings instance
settings = Settings()
