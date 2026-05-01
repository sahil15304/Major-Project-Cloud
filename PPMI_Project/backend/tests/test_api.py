"""
Unit tests for PPMI Backend API.
Run with: pytest tests/test_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add parent directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app

# Create test client
client = TestClient(app)


class TestHealthCheck:
    """Test health check endpoints."""
    
    def test_health_check(self):
        """Test /health endpoint."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "models_loaded" in data
        assert "message" in data
    
    def test_status_endpoint(self):
        """Test /status endpoint."""
        response = client.get("/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "models_loaded" in data


class TestPredictionEndpoint:
    """Test prediction endpoint."""
    
    def test_valid_prediction(self):
        """Test prediction with valid input."""
        payload = {
            "NP1TOT": 5.0,
            "NP2TOT": 15.0,
            "NP3TOT": 35.0,
            "MCATOT": 26.0
        }
        response = client.post("/api/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "severity_6m" in data
        assert "severity_12m" in data
        assert "severity_24m" in data
        assert isinstance(data["severity_6m"], (int, float))
        assert isinstance(data["severity_12m"], (int, float))
        assert isinstance(data["severity_24m"], (int, float))
    
    def test_invalid_input_missing_field(self):
        """Test prediction with missing field."""
        payload = {
            "NP1TOT": 5.0,
            "NP2TOT": 15.0,
            "NP3TOT": 35.0
            # Missing MCATOT
        }
        response = client.post("/api/predict", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_invalid_input_out_of_range(self):
        """Test prediction with out-of-range values."""
        payload = {
            "NP1TOT": 25.0,  # Out of range (max 16)
            "NP2TOT": 15.0,
            "NP3TOT": 35.0,
            "MCATOT": 26.0
        }
        response = client.post("/api/predict", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_invalid_input_negative_values(self):
        """Test prediction with negative values."""
        payload = {
            "NP1TOT": -1.0,  # Invalid
            "NP2TOT": 15.0,
            "NP3TOT": 35.0,
            "MCATOT": 26.0
        }
        response = client.post("/api/predict", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_edge_case_min_values(self):
        """Test prediction with minimum valid values."""
        payload = {
            "NP1TOT": 0.0,
            "NP2TOT": 0.0,
            "NP3TOT": 0.0,
            "MCATOT": 0.0
        }
        response = client.post("/api/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "severity_6m" in data
    
    def test_edge_case_max_values(self):
        """Test prediction with maximum valid values."""
        payload = {
            "NP1TOT": 16.0,
            "NP2TOT": 52.0,
            "NP3TOT": 108.0,
            "MCATOT": 30.0
        }
        response = client.post("/api/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "severity_6m" in data


class TestModelsEndpoint:
    """Test models information endpoint."""
    
    def test_models_info(self):
        """Test /models/info endpoint."""
        response = client.get("/api/models/info")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "models" in data
        assert "severity_6m" in data["models"] or "severity_12m" in data["models"]


class TestVersionEndpoint:
    """Test version endpoint."""
    
    def test_version(self):
        """Test /version endpoint."""
        response = client.get("/api/version")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert "endpoints" in data
    
    def test_root(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "documentation" in data


class TestErrorHandling:
    """Test error handling."""
    
    def test_invalid_endpoint(self):
        """Test accessing non-existent endpoint."""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
    
    def test_invalid_method(self):
        """Test invalid HTTP method."""
        response = client.get("/api/predict")  # POST required
        assert response.status_code == 405


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
