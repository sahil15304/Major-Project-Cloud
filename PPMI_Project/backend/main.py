"""
Main FastAPI application.
Entry point for the PPMI Parkinson's Disease Severity Prediction API.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys

from app.config import settings
from app.models import ModelManager
from app.utils.logger import setup_logging, get_logger
from app.routes import predict
from app.routes import data_ingest
import os

# Setup logging
logger_instance = setup_logging(log_dir=settings.LOGS_DIR, log_level=settings.LOG_LEVEL)
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-ready API for Parkinson's disease severity prediction using XGBoost models",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware - configure for AWS deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model manager
model_manager: ModelManager = None


@app.on_event("startup")
async def startup_event():
    """Initialize models on startup."""
    global model_manager
    
    logger.info("=" * 60)
    logger.info(f"Starting {settings.APP_NAME}")
    logger.info("=" * 60)
    
    try:
        # Log configuration
        logger.info(f"Configuration: {settings.to_dict()}")
        
        # Validate settings
        settings.validate()
        logger.info("✓ Configuration validated")
        
        # Optionally skip model loading in local dev to avoid heavy ML deps.
        skip_models = os.getenv("PPMI_SKIP_MODEL_LOAD", "0") in ("1", "true", "True")

        if skip_models:
            logger.warning("PPMI_SKIP_MODEL_LOAD is set — skipping model initialization (dev mode).")
            model_manager = None
            predict.set_model_manager(None)
        else:
            # Initialize model manager
            models_dir = settings.LOCAL_MODELS_DIR
            logger.info(f"Loading models from: {models_dir}")

            model_manager = ModelManager(models_dir)
            model_manager.load_all_models()

            # Set the model manager in routes
            predict.set_model_manager(model_manager)
        
        logger.info("✓ All startup tasks completed successfully")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Startup failed: {e}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    logger.info("Shutting down application...")
    logger.info("Models unloaded from memory")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests and responses."""
    # Log request
    logger.debug(f"→ {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    logger.debug(f"← {request.method} {request.url.path} {response.status_code}")
    
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "path": str(request.url.path)
        }
    )


# Include routers
app.include_router(predict.router)
app.include_router(data_ingest.router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to PPMI Parkinson's Disease Severity Prediction API",
        "version": settings.APP_VERSION,
        "documentation": "http://localhost:8000/docs",
        "health": "http://localhost:8000/api/health",
        "models": "http://localhost:8000/api/models/info"
    }


@app.get("/status")
async def status():
    """Get application status."""
    global model_manager
    
    if model_manager is None or not model_manager.is_loaded:
        return {
            "status": "unhealthy",
            "reason": "Models not loaded"
        }
    
    status_info = model_manager.get_model_status()
    
    return {
        "status": "healthy" if status_info['is_loaded'] else "unhealthy",
        "models_loaded": status_info['is_loaded'],
        "model_count": status_info['count'],
        "configured_models": status_info['models']
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {settings.HOST}:{settings.PORT}")
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
