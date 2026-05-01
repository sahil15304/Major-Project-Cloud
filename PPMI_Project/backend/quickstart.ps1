# Quick Start Script for PPMI Backend API (PowerShell)
# Usage: .\quickstart.ps1

Write-Host "================================" -ForegroundColor Blue
Write-Host "PPMI Backend - Quick Start" -ForegroundColor Blue
Write-Host "================================" -ForegroundColor Blue
Write-Host ""

# Function to print section headers
function Print-Step {
    param([int]$step, [string]$text)
    Write-Host "Step $step`: $text" -ForegroundColor Cyan
}

# Function to print success
function Print-Success {
    param([string]$text)
    Write-Host "✓ $text" -ForegroundColor Green
}

# Function to print warning
function Print-Warning {
    param([string]$text)
    Write-Host "⚠ $text" -ForegroundColor Yellow
}

# Step 1: Create virtual environment
Print-Step 1 "Creating virtual environment..."
python -m venv venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error creating virtual environment. Make sure Python 3 is installed." -ForegroundColor Red
    exit 1
}
Print-Success "Virtual environment created"
Write-Host ""

# Step 2: Activate virtual environment
Print-Step 2 "Activating virtual environment..."
& .\venv\Scripts\Activate.ps1
Print-Success "Virtual environment activated"
Write-Host ""

# Step 3: Install dependencies
Print-Step 3 "Installing dependencies..."
python -m pip install --upgrade pip | Out-Null
python -m pip install -r requirements.txt | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error installing dependencies. Check requirements.txt" -ForegroundColor Red
    exit 1
}
Print-Success "Dependencies installed"
Write-Host ""

# Step 4: Check for models
Print-Step 4 "Checking for models..."
$models_exist = (Test-Path "../models/xgb_sev_6m.joblib") -and `
                (Test-Path "../models/xgb_sev_12m.joblib") -and `
                (Test-Path "../models/xgb_sev_24m.joblib")

if ($models_exist) {
    Print-Success "All models found"
}
else {
    Print-Warning "Models not found in ../models/"
    Write-Host "Please ensure the model files are in the correct location:" -ForegroundColor Yellow
    Write-Host "  - ../models/xgb_sev_6m.joblib" -ForegroundColor Yellow
    Write-Host "  - ../models/xgb_sev_12m.joblib" -ForegroundColor Yellow
    Write-Host "  - ../models/xgb_sev_24m.joblib" -ForegroundColor Yellow
    Write-Host ""
    
    $response = Read-Host "Continue anyway? (y/n)"
    if ($response -ne "y" -and $response -ne "Y") {
        exit 1
    }
}
Write-Host ""

# Step 5: Create logs directory
Print-Step 5 "Creating logs directory..."
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}
Print-Success "Logs directory created"
Write-Host ""

# Step 6: Start application
Print-Step 6 "Starting application..."
Write-Host ""
Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Yellow
Write-Host "║     PPMI Backend API Starting          ║" -ForegroundColor Yellow
Write-Host "║                                        ║" -ForegroundColor Yellow
Write-Host "║   API will be available at:            ║" -ForegroundColor Yellow
Write-Host "║   http://localhost:8000                ║" -ForegroundColor Yellow
Write-Host "║                                        ║" -ForegroundColor Yellow
Write-Host "║   Swagger Docs:                        ║" -ForegroundColor Yellow
Write-Host "║   http://localhost:8000/docs           ║" -ForegroundColor Yellow
Write-Host "║                                        ║" -ForegroundColor Yellow
Write-Host "║   Press Ctrl+C to stop the server      ║" -ForegroundColor Yellow
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Yellow
Write-Host ""

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
