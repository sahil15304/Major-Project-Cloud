# API Documentation & Examples

Complete API reference with usage examples in multiple languages.

## Base URL

```
Local: http://localhost:8000
Production (AWS): https://your-api-domain.com
```

## Authentication

Currently no authentication required. For production, see README.md Security section to add JWT/API Key.

## Rate Limiting

No rate limiting currently implemented. Add based on production requirements.

## Response Format

All responses are in JSON format with consistent structure:

### Success Response
```json
{
  "data": {...},
  "status": "success",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Error Response
```json
{
  "error": "ErrorType",
  "message": "Detailed error message",
  "status_code": 400,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## API Endpoints

### 1. Health Check

**Endpoint:** `GET /api/health`

**Description:** Check if API and models are ready

**Request:**
```bash
curl http://localhost:8000/api/health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "models_loaded": true,
  "message": "All 3 models loaded successfully"
}
```

---

### 2. Predictions (Main Endpoint)

**Endpoint:** `POST /api/predict`

**Description:** Generate severity predictions for Parkinson's disease

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "NP1TOT": 5.0,
  "NP2TOT": 15.0,
  "NP3TOT": 35.0,
  "MCATOT": 26.0
}
```

**Field Descriptions:**
- `NP1TOT` (float): UPDRS Part I total score. Range: 0-16
- `NP2TOT` (float): UPDRS Part II total score. Range: 0-52
- `NP3TOT` (float): UPDRS Part III total score. Range: 0-108
- `MCATOT` (float): Montreal Cognitive Assessment score. Range: 0-30

**Response (200 OK):**
```json
{
  "severity_6m": 25.3,
  "severity_12m": 28.7,
  "severity_24m": 32.1
}
```

**Response Fields:**
- `severity_6m` (float): Predicted severity at 6 months
- `severity_12m` (float): Predicted severity at 12 months
- `severity_24m` (float): Predicted severity at 24 months

**Possible Errors:**

| Status Code | Error | Reason |
|-------------|-------|--------|
| 400 | ValidationError | Invalid input (missing fields, out of range) |
| 422 | ValidationError | Input validation failed |
| 503 | ServiceUnavailable | Models not loaded |
| 500 | InternalServerError | Unexpected error |

---

### 3. Models Information

**Endpoint:** `GET /api/models/info`

**Description:** Get information about loaded models

**Request:**
```bash
curl http://localhost:8000/api/models/info
```

**Response (200 OK):**
```json
{
  "status": {
    "is_loaded": true,
    "models": [
      "severity_6m",
      "severity_12m",
      "severity_24m"
    ],
    "count": 3,
    "metadata_available": []
  },
  "models": {
    "severity_6m": {},
    "severity_12m": {},
    "severity_24m": {}
  }
}
```

---

### 4. API Version

**Endpoint:** `GET /api/version`

**Description:** Get API version and endpoint information

**Request:**
```bash
curl http://localhost:8000/api/version
```

**Response (200 OK):**
```json
{
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
```

---

### 5. Application Status

**Endpoint:** `GET /status`

**Description:** Get overall application status

**Request:**
```bash
curl http://localhost:8000/status
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "models_loaded": true,
  "model_count": 3,
  "configured_models": [
    "severity_6m",
    "severity_12m",
    "severity_24m"
  ]
}
```

---

### 6. API Documentation

**Endpoint:** `GET /docs`

**Description:** Swagger UI interactive documentation

**Access:** Open in browser: `http://localhost:8000/docs`

---

## Usage Examples

### Python

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# 1. Check health
response = requests.get(f"{BASE_URL}/api/health")
print(f"Health: {response.json()}")

# 2. Make prediction
patient_data = {
    "NP1TOT": 5.0,
    "NP2TOT": 15.0,
    "NP3TOT": 35.0,
    "MCATOT": 26.0
}

response = requests.post(
    f"{BASE_URL}/api/predict",
    json=patient_data,
    headers={"Content-Type": "application/json"}
)

if response.status_code == 200:
    predictions = response.json()
    print(f"Severity at 6 months: {predictions['severity_6m']:.2f}")
    print(f"Severity at 12 months: {predictions['severity_12m']:.2f}")
    print(f"Severity at 24 months: {predictions['severity_24m']:.2f}")
else:
    print(f"Error: {response.json()}")

# 3. Get model info
response = requests.get(f"{BASE_URL}/api/models/info")
models_info = response.json()
print(f"Models loaded: {models_info['status']['count']}")
```

### JavaScript/Node.js

```javascript
const BASE_URL = "http://localhost:8000";

// Helper function to fetch and handle errors
async function apiCall(endpoint, options = {}) {
  try {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`API Error: ${error.message}`);
    throw error;
  }
}

// 1. Health check
async function checkHealth() {
  const health = await apiCall("/api/health");
  console.log("Health:", health);
}

// 2. Make prediction
async function makePrediction() {
  const patientData = {
    NP1TOT: 5.0,
    NP2TOT: 15.0,
    NP3TOT: 35.0,
    MCATOT: 26.0
  };
  
  const prediction = await apiCall("/api/predict", {
    method: "POST",
    body: JSON.stringify(patientData)
  });
  
  console.log(`Severity at 6 months: ${prediction.severity_6m.toFixed(2)}`);
  console.log(`Severity at 12 months: ${prediction.severity_12m.toFixed(2)}`);
  console.log(`Severity at 24 months: ${prediction.severity_24m.toFixed(2)}`);
}

// Run examples
checkHealth();
makePrediction();
```

### cURL

```bash
#!/bin/bash

API_URL="http://localhost:8000"

echo "=== Health Check ==="
curl -s "$API_URL/api/health" | jq '.'

echo ""
echo "=== Make Prediction ==="
curl -s -X POST "$API_URL/api/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "NP1TOT": 5.0,
    "NP2TOT": 15.0,
    "NP3TOT": 35.0,
    "MCATOT": 26.0
  }' | jq '.'

echo ""
echo "=== Get Models Info ==="
curl -s "$API_URL/api/models/info" | jq '.'

echo ""
echo "=== Get API Version ==="
curl -s "$API_URL/api/version" | jq '.'
```

### Java

```java
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import com.google.gson.Gson;
import com.google.gson.JsonObject;

public class PPMIClient {
    private static final String BASE_URL = "http://localhost:8000";
    private static final HttpClient client = HttpClient.newHttpClient();
    private static final Gson gson = new Gson();
    
    public static void main(String[] args) throws Exception {
        // 1. Health check
        String health = makeRequest("GET", "/api/health", null);
        System.out.println("Health: " + health);
        
        // 2. Make prediction
        JsonObject patientData = new JsonObject();
        patientData.addProperty("NP1TOT", 5.0);
        patientData.addProperty("NP2TOT", 15.0);
        patientData.addProperty("NP3TOT", 35.0);
        patientData.addProperty("MCATOT", 26.0);
        
        String prediction = makeRequest("POST", "/api/predict", patientData.toString());
        System.out.println("Prediction: " + prediction);
        
        JsonObject result = gson.fromJson(prediction, JsonObject.class);
        System.out.printf("Severity at 6m: %.2f%n", result.get("severity_6m").getAsDouble());
        System.out.printf("Severity at 12m: %.2f%n", result.get("severity_12m").getAsDouble());
        System.out.printf("Severity at 24m: %.2f%n", result.get("severity_24m").getAsDouble());
    }
    
    private static String makeRequest(String method, String endpoint, String body) throws Exception {
        HttpRequest.Builder requestBuilder = HttpRequest.newBuilder()
            .uri(new URI(BASE_URL + endpoint))
            .header("Content-Type", "application/json")
            .method(method, body == null ? 
                HttpRequest.BodyPublishers.noBody() : 
                HttpRequest.BodyPublishers.ofString(body));
        
        HttpResponse<String> response = client.send(
            requestBuilder.build(),
            HttpResponse.BodyHandlers.ofString()
        );
        
        if (response.statusCode() != 200) {
            throw new Exception("HTTP " + response.statusCode() + ": " + response.body());
        }
        
        return response.body();
    }
}
```

### R

```r
# Install required packages: install.packages(c("httr", "jsonlite"))

library(httr)
library(jsonlite)

BASE_URL <- "http://localhost:8000"

# 1. Health check
response <- GET(paste0(BASE_URL, "/api/health"))
health <- fromJSON(content(response, "text"))
print(health)

# 2. Make prediction
patient_data <- list(
  NP1TOT = 5.0,
  NP2TOT = 15.0,
  NP3TOT = 35.0,
  MCATOT = 26.0
)

response <- POST(
  paste0(BASE_URL, "/api/predict"),
  body = toJSON(patient_data),
  content_type_json()
)

if (status_code(response) == 200) {
  prediction <- fromJSON(content(response, "text"))
  cat(sprintf(
    "Severity: 6m=%.2f, 12m=%.2f, 24m=%.2f\n",
    prediction$severity_6m,
    prediction$severity_12m,
    prediction$severity_24m
  ))
} else {
  cat("Error:", content(response, "text"), "\n")
}
```

---

## Error Handling

### Common Error Scenarios

**Missing Required Field:**
```json
{
  "detail": [
    {
      "loc": ["body", "MCATOT"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Out of Range Value:**
```json
{
  "detail": [
    {
      "loc": ["body", "NP1TOT"],
      "msg": "ensure this value is less than or equal to 16",
      "type": "value_error.number.not_le",
      "ctx": {"limit_value": 16}
    }
  ]
}
```

**Models Not Loaded:**
```json
{
  "detail": "Models not loaded. Service unavailable."
}
```

---

## Performance Characteristics

- **Health Check Latency**: < 10ms
- **Prediction Latency**: 5-50ms (depends on server load)
- **Response Time p95**: < 100ms
- **Response Time p99**: < 500ms
- **Model Load Time**: 5-10s (one-time on startup)
- **Memory Usage**: ~500MB-1GB

---

## Testing the API

### Using Postman

1. Import this collection (save as `PPMI_API.postman_collection.json`):

```json
{
  "info": {
    "name": "PPMI API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": {
          "raw": "{{base_url}}/api/health",
          "host": ["{{base_url}}"],
          "path": ["api", "health"]
        }
      }
    },
    {
      "name": "Predict Severity",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\"NP1TOT\": 5.0, \"NP2TOT\": 15.0, \"NP3TOT\": 35.0, \"MCATOT\": 26.0}"
        },
        "url": {
          "raw": "{{base_url}}/api/predict",
          "host": ["{{base_url}}"],
          "path": ["api", "predict"]
        }
      }
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    }
  ]
}
```

---

## Webhooks & Notifications (Future Enhancement)

```python
# Example: Send prediction results to webhook
import requests

def send_prediction_webhook(prediction_id, predictions, webhook_url):
    payload = {
        "prediction_id": prediction_id,
        "results": predictions,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    response = requests.post(webhook_url, json=payload)
    return response.status_code == 200
```

---

## Batch Predictions (Future Enhancement)

```python
# Example: Process multiple predictions
@app.post("/api/predict/batch")
async def predict_batch(patients: List[PredictionInput]):
    results = []
    for patient in patients:
        features = [patient.NP1TOT, patient.NP2TOT, patient.NP3TOT, patient.MCATOT]
        predictions = {
            'severity_6m': model_manager.predict('severity_6m', features),
            'severity_12m': model_manager.predict('severity_12m', features),
            'severity_24m': model_manager.predict('severity_24m', features)
        }
        results.append(predictions)
    return {"predictions": results}
```

---

## Best Practices

1. **Always validate input** before sending to API
2. **Cache health check** results (don't call on every request)
3. **Implement retry logic** for network failures
4. **Use connection pooling** in production clients
5. **Monitor response times** and set appropriate timeouts
6. **Log all API interactions** for debugging
7. **Handle errors gracefully** with user-friendly messages
8. **Rate your requests** to avoid overwhelming the server

---

**Last Updated**: 2024
