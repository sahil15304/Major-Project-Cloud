# PPMI Parkinson's Disease Severity Prediction API

Production-ready backend service for Parkinson's disease severity prediction using pre-trained XGBoost models.

## Overview

This FastAPI-based service exposes three pre-trained machine learning models that predict Parkinson's disease severity at 6, 12, and 24-month horizons based on clinical features:

- **NP1TOT**: UPDRS Part I (Mentation, Behavior, Mood) - Range: 0-16
- **NP2TOT**: UPDRS Part II (Activities of Daily Living) - Range: 0-52
- **NP3TOT**: UPDRS Part III (Motor Examination) - Range: 0-108
- **MCATOT**: Montreal Cognitive Assessment - Range: 0-30

## Features

✅ **Production-Ready**
- Clean, modular architecture
- Comprehensive error handling
- Structured logging
- Input validation with Pydantic
- Health check endpoints

✅ **High Performance**
- Models loaded once at startup (not per request)
- Efficient XGBoost inference
- Minimal memory footprint

✅ **AWS-Ready**
- Environment-based configuration
- Support for S3 model loading (optional)
- IAM role support for EC2 authentication

✅ **Developer-Friendly**
- Automatic API documentation (Swagger/OpenAPI)
- Comprehensive logging
- Unit tests included
- Example requests provided

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── models.py               # Model loading and management
│   ├── schemas.py              # Pydantic data models
│   ├── routes/
│   │   ├── __init__.py
│   │   └── predict.py          # API endpoints
│   └── utils/
│       ├── __init__.py
│       └── logger.py           # Logging configuration
├── tests/
│   ├── test_api.py             # Unit tests
│   └── test_examples.sh        # curl examples
├── main.py                     # Entry point (wrapper)
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
├── README.md                   # This file
└── .gitignore
```

## Quick Start (Local Development)

### 1. Clone/Navigate to Backend Directory

```bash
cd backend/
```

### 2. Create Virtual Environment

```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env as needed (optional for local development with default values)
# LOCAL_MODELS_DIR should point to ../models relative to backend/
```

### 5. Run Application

```bash
# Development mode (with auto-reload)
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or for production-like behavior
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at: **http://localhost:8000**

### 6. Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Testing the API

### Using Swagger UI (Easiest)

1. Navigate to http://localhost:8000/docs
2. Click on the `/predict` endpoint
3. Click "Try it out"
4. Enter sample data:
```json
{
  "NP1TOT": 5.0,
  "NP2TOT": 15.0,
  "NP3TOT": 35.0,
  "MCATOT": 26.0
}
```
5. Click "Execute" to see predictions

### Using curl

```bash
# Health check
curl http://localhost:8000/api/health

# Make prediction
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "NP1TOT": 5.0,
    "NP2TOT": 15.0,
    "NP3TOT": 35.0,
    "MCATOT": 26.0
  }'

# Get models information
curl http://localhost:8000/api/models/info

# Get API version
curl http://localhost:8000/api/version
```

### Using Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Health check
health = requests.get(f"{BASE_URL}/api/health")
print(health.json())

# Make prediction
payload = {
    "NP1TOT": 5.0,
    "NP2TOT": 15.0,
    "NP3TOT": 35.0,
    "MCATOT": 26.0
}

response = requests.post(
    f"{BASE_URL}/api/predict",
    json=payload
)
print(response.json())
```

### Using Postman

1. Create a new POST request
2. URL: `http://localhost:8000/api/predict`
3. Body (raw JSON):
```json
{
  "NP1TOT": 5.0,
  "NP2TOT": 15.0,
  "NP3TOT": 35.0,
  "MCATOT": 26.0
}
```
4. Send the request

## Running Tests

```bash
# Run all tests with verbose output
pytest tests/test_api.py -v

# Run specific test
pytest tests/test_api.py::TestPredictionEndpoint::test_valid_prediction -v

# Run with coverage
pytest tests/test_api.py --cov=app --cov-report=html
```

## AWS EC2 Deployment

### Prerequisites

- AWS EC2 instance (Amazon Linux 2 or Ubuntu 20.04+)
- Security group with port 8000 open (or 80/443 with reverse proxy)
- IAM role with S3 read access (if using S3 for models)
- SSH access configured

### Deployment Steps

1. **Connect to EC2 and install dependencies**
```bash
ssh -i your-key.pem ec2-user@your-instance-ip

sudo yum update -y
sudo yum install python3 python3-pip -y
```

2. **Setup application**
```bash
cd /opt  # or your preferred location
git clone your-repo.git ppmi-backend
cd ppmi-backend/backend
```

3. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. **Create systemd service**
```bash
sudo nano /etc/systemd/system/ppmi-api.service
```

Paste:
```ini
[Unit]
Description=PPMI Parkinson API
After=network.target

[Service]
Type=notify
User=ec2-user
WorkingDirectory=/opt/ppmi-backend/backend
Environment="PATH=/opt/ppmi-backend/backend/venv/bin"
ExecStart=/opt/ppmi-backend/backend/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

5. **Enable and start service**
```bash
sudo systemctl daemon-reload
sudo systemctl enable ppmi-api
sudo systemctl start ppmi-api
sudo systemctl status ppmi-api
```

6. **View logs**
```bash
sudo journalctl -u ppmi-api -f
```

### Using S3 for Models (Optional)

1. **Upload models to S3**
```bash
aws s3 cp xgb_sev_6m.joblib s3://your-bucket/models/
aws s3 cp xgb_sev_12m.joblib s3://your-bucket/models/
aws s3 cp xgb_sev_24m.joblib s3://your-bucket/models/
```

2. **Create IAM Role for EC2**
   - Go to IAM → Roles → Create Role
   - Select EC2 as trusted entity
   - Add policy: `AmazonS3ReadOnlyAccess`
   - Attach to EC2 instance

3. **Configure environment**
```bash
export MODELS_SOURCE=s3
export AWS_S3_BUCKET=your-bucket
export AWS_S3_MODELS_PREFIX=models/
export AWS_REGION=us-east-1
export USE_IAM_ROLE=True
```

### Setting Up Reverse Proxy (nginx)

For production, use nginx as reverse proxy:

```bash
sudo yum install nginx -y
sudo nano /etc/nginx/conf.d/ppmi-api.conf
```

Paste:
```nginx
upstream ppmi_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name _;

    client_max_body_size 10M;

    location / {
        proxy_pass http://ppmi_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

Then:
```bash
sudo systemctl start nginx
sudo systemctl enable nginx
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | False | Enable debug mode |
| `LOG_LEVEL` | INFO | Logging level |
| `HOST` | 0.0.0.0 | Server host |
| `PORT` | 8000 | Server port |
| `MODELS_SOURCE` | local | Model location: 'local' or 's3' |
| `LOCAL_MODELS_DIR` | ../models | Local models directory |
| `AWS_S3_BUCKET` | - | S3 bucket (if using S3) |
| `AWS_S3_MODELS_PREFIX` | models/ | S3 prefix for models |
| `AWS_REGION` | us-east-1 | AWS region |
| `USE_IAM_ROLE` | False | Use EC2 IAM role for AWS auth |
| `LOGS_DIR` | logs | Logs directory |

### Configuration Priority

1. Environment variables (highest priority)
2. .env file
3. Hardcoded defaults (lowest priority)

## API Endpoints

### Health Check
```
GET /api/health
Response: {
  "status": "healthy",
  "models_loaded": true,
  "message": "All 3 models loaded successfully"
}
```

### Make Prediction
```
POST /api/predict
Request: {
  "NP1TOT": 5.0,
  "NP2TOT": 15.0,
  "NP3TOT": 35.0,
  "MCATOT": 26.0
}
Response: {
  "severity_6m": 25.3,
  "severity_12m": 28.7,
  "severity_24m": 32.1
}
```

### Models Information
```
GET /api/models/info
Response: {
  "status": {
    "is_loaded": true,
    "models": ["severity_6m", "severity_12m", "severity_24m"],
    "count": 3,
    "metadata_available": []
  },
  "models": {...}
}
```

### API Version
```
GET /api/version
Response: {
  "app": "PPMI Parkinson's Disease Severity Prediction API",
  "version": "1.0.0",
  "endpoints": [...]
}
```

## Monitoring & Logging

Logs are stored in the `logs/` directory:
- `app_YYYYMMDD.log` - All application logs
- `errors_YYYYMMDD.log` - Errors only

Monitor using:
```bash
# Tail logs
tail -f logs/app_*.log

# Search for errors
grep ERROR logs/app_*.log

# Count predictions
grep "Predictions generated" logs/app_*.log | wc -l
```

## Performance Optimization

### Current Performance

- Model load time: ~5-10 seconds (one-time on startup)
- Prediction latency: ~5-50ms per request (XGBoost inference)
- Memory usage: ~500MB-1GB (depending on model size)

### Scaling Recommendations

1. **Horizontal Scaling**: Load balance multiple EC2 instances
   - Use AWS ELB or ALB
   - Each instance runs independent API container

2. **Container Orchestration**: Use AWS ECS/Fargate
   - Auto-scaling based on CPU/memory
   - Blue-green deployments for updates

3. **Caching**: Add Redis for prediction caching
   - Cache common patient profiles
   - Reduce model inference load

4. **Async Processing**: For batch predictions
   - Queue system with Celery
   - Process batch predictions in background

## Troubleshooting

### Models Not Loading
```
Error: Model file not found: ../models/xgb_sev_6m.joblib
```
**Solution**: Verify models directory path and ensure .joblib files exist

### Port Already in Use
```
Error: Address already in use
```
**Solution**: Change port or kill existing process
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux
lsof -i :8000
kill -9 <PID>
```

### Import Errors
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solution**: Install dependencies and activate virtual environment
```bash
pip install -r requirements.txt
```

### Validation Errors
```
Ensure feature values are within valid ranges:
- NP1TOT: 0-16
- NP2TOT: 0-52
- NP3TOT: 0-108
- MCATOT: 0-30
```

## Security Considerations

1. **Input Validation**: All inputs validated with Pydantic
2. **Error Messages**: Generic error messages in production
3. **CORS**: Configure for specific domains in production
4. **Authentication**: Add JWT/OAuth if needed for production
5. **HTTPS**: Use SSL/TLS in production with nginx/ALB
6. **Rate Limiting**: Consider adding rate limiting middleware

Example production CORS:
```python
# In main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domain
    allow_credentials=True,
    allow_methods=["POST"],  # Only POST for /predict
    allow_headers=["Content-Type"],
)
```

## Contributing & Maintenance

### Adding New Features

1. Create feature branch
2. Add endpoint to `app/routes/predict.py`
3. Add tests to `tests/test_api.py`
4. Update documentation
5. Create pull request

### Model Updates

To update models:
1. Train new models following the same naming convention
2. Replace .joblib files in models/ directory
3. Restart application (models reload on startup)
4. Verify predictions in /docs

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [XGBoost Documentation](https://xgboost.readthedocs.io/)
- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)

## License

[Your License Here]

## Support

For issues or questions:
1. Check troubleshooting section
2. Review logs in `logs/` directory
3. Enable DEBUG mode and check detailed output
4. Contact development team

---

**Last Updated**: 2024
**Status**: Production Ready
