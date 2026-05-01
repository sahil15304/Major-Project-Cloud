"""
Pydantic schemas for request/response validation.
Ensures type safety and automatic documentation in Swagger.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional


class PredictionInput(BaseModel):
    """Input schema for severity predictions.

    Clinical features from UPDRS and cognitive assessment and basic demographics:
    - AGE: Patient age in years - Range: 0-120
    - SEX: Sex encoded as 0/1 (0=female, 1=male)
    - NP1TOT: UPDRS Part I total (Mentation, Behavior, Mood) - Range: 0-16
    - NP2TOT: UPDRS Part II total (Activities of Daily Living) - Range: 0-52
    - NP3TOT: UPDRS Part III total (Motor Examination) - Range: 0-108
    - MCATOT: Montreal Cognitive Assessment total score - Range: 0-30
    - SEVERITY: Current severity score
    """

    AGE: float = Field(
        ...,
        ge=0,
        le=120,
        description="Patient age in years"
    )
    SEX: float = Field(
        ...,
        ge=0,
        le=1,
        description="Sex encoded as 0 (female) or 1 (male)"
    )
    NP1TOT: float = Field(
        ...,
        ge=0,
        le=16,
        description="UPDRS Part I total score (0-16)"
    )
    NP2TOT: float = Field(
        ...,
        ge=0,
        le=52,
        description="UPDRS Part II total score (0-52)"
    )
    NP3TOT: float = Field(
        ...,
        ge=0,
        le=108,
        description="UPDRS Part III total score (0-108)"
    )
    MCATOT: float = Field(
        ...,
        ge=0,
        le=30,
        description="Montreal Cognitive Assessment score (0-30)"
    )
    SEVERITY: float = Field(
        ...,
        ge=0,
        description="Current severity score"
    )

    @validator('*')
    def check_no_nan(cls, v):
        """Ensure no missing values are submitted."""
        if v is None:
            raise ValueError("All fields are required")
        return v

    @validator('SEX')
    def check_sex(cls, v):
        """Ensure SEX is encoded as 0 or 1. Adjust if different encoding is used."""
        if v not in (0, 1):
            raise ValueError("SEX must be 0 or 1")
        return v

    class Config:
        schema_extra = {
            "example": {
                "AGE": 67,
                "SEX": 1,
                "NP1TOT": 5.0,
                "NP2TOT": 15.0,
                "NP3TOT": 35.0,
                "MCATOT": 26.0,
                "SEVERITY": 20.0
            }
        }


class SeverityPrediction(BaseModel):
    """Output schema for severity predictions."""
    
    severity_6m: float = Field(
        ..., 
        description="Predicted severity at 6 months"
    )
    severity_12m: float = Field(
        ..., 
        description="Predicted severity at 12 months"
    )
    severity_24m: float = Field(
        ..., 
        description="Predicted severity at 24 months"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "severity_6m": 25.3,
                "severity_12m": 28.7,
                "severity_24m": 32.1
            }
        }


class HealthStatus(BaseModel):
    """Health check response schema."""
    
    status: str = Field(..., description="Service status")
    models_loaded: bool = Field(..., description="Whether all models are successfully loaded")
    message: str = Field(..., description="Additional status message")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "models_loaded": True,
                "message": "All 3 models loaded successfully"
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response schema."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Detailed error message")
    status_code: int = Field(..., description="HTTP status code")
    
    class Config:
        schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "NP1TOT must be between 0 and 16",
                "status_code": 400
            }
        }
