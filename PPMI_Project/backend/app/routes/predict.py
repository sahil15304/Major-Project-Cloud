"""
API routes for predictions and health checks.
Handles all HTTP endpoints.
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
import logging
from typing import Optional

from app.schemas import PredictionInput, SeverityPrediction, HealthStatus, ErrorResponse
from app.models import ModelManager
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["predictions"])

# Global model manager (will be initialized in main.py)
model_manager: Optional[ModelManager] = None


def set_model_manager(mm: ModelManager) -> None:
    """Set the global model manager instance."""
    global model_manager
    model_manager = mm


@router.get("/health", response_model=HealthStatus)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        HealthStatus: Current health status of the service
    """
    try:
        if model_manager is None:
            return HealthStatus(
                status="unhealthy",
                models_loaded=False,
                message="Model manager not initialized"
            )
        
        status_info = model_manager.get_model_status()
        
        if status_info['is_loaded'] and status_info['count'] == 3:
            return HealthStatus(
                status="healthy",
                models_loaded=True,
                message="All 3 models loaded successfully"
            )
        else:
            return HealthStatus(
                status="unhealthy",
                models_loaded=False,
                message=f"Only {status_info['count']}/3 models loaded"
            )
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return HealthStatus(
            status="unhealthy",
            models_loaded=False,
            message=f"Health check error: {str(e)}"
        )


@router.post("/predict", response_model=SeverityPrediction)
async def predict(patient_data: PredictionInput) -> SeverityPrediction:
    """
    Predict Parkinson's disease severity at 6, 12, and 24 months.
    
    Args:
        patient_data: Clinical features from patient assessment
            - NP1TOT: UPDRS Part I total (0-16)
            - NP2TOT: UPDRS Part II total (0-52)
            - NP3TOT: UPDRS Part III total (0-108)
            - MCATOT: Montreal Cognitive Assessment (0-30)
    
    Returns:
        SeverityPrediction: Predicted severity values for 6m, 12m, 24m horizons
        
    Raises:
        HTTPException: If prediction fails
    """
    try:
        if model_manager is None or not model_manager.is_loaded:
            logger.error("Model manager not initialized or models not loaded")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Models not loaded. Service unavailable."
            )
        
        # Prepare features in correct order
        features = [
            patient_data.NP1TOT,
            patient_data.NP2TOT,
            patient_data.NP3TOT,
            patient_data.MCATOT
        ]
        
        logger.info(f"Processing prediction request with features: {features}")
        
        # Make predictions using all three models
        severity_6m = model_manager.predict('severity_6m', features)
        severity_12m = model_manager.predict('severity_12m', features)
        severity_24m = model_manager.predict('severity_24m', features)
        
        logger.info(
            f"Predictions generated - 6m: {severity_6m:.2f}, "
            f"12m: {severity_12m:.2f}, 24m: {severity_24m:.2f}"
        )
        
        return SeverityPrediction(
            severity_6m=severity_6m,
            severity_12m=severity_12m,
            severity_24m=severity_24m
        )
        
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@router.get("/models/info")
async def models_info():
    """
    Get information about loaded models.
    
    Returns:
        dict: Information about all loaded models
    """
    try:
        if model_manager is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Model manager not initialized"
            )
        
        status_info = model_manager.get_model_status()
        
        # Get metadata for each model
        models_info = {}
        for model_name in status_info['models']:
            metadata = model_manager.get_model_info(model_name)
            models_info[model_name] = metadata or {"message": "No metadata available"}
        
        return {
            "status": status_info,
            "models": models_info
        }
    except Exception as e:
        logger.error(f"Error getting models info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving model information: {str(e)}"
        )


@router.get("/version")
async def get_version():
    """Get API version."""
    return {
        "app": "PPMI Parkinson's Disease Severity Prediction API",
        "version": "1.0.0",
        "endpoints": [
            "GET /health - Health check",
            "POST /predict - Make predictions",
            "GET /models/info - Model information",
            "GET /version - API version",
            "GET /docs - Swagger documentation"
        ]
    }
