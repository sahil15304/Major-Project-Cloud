#!/bin/bash

# Quick Start Script for PPMI Backend API
# Usage: ./quickstart.sh

echo "================================"
echo "PPMI Backend - Quick Start"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}Step 1: Creating virtual environment...${NC}"
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Error creating virtual environment. Make sure Python 3 is installed."
    exit 1
fi

echo -e "${GREEN}✓ Virtual environment created${NC}"
echo ""

echo -e "${BLUE}Step 2: Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

echo -e "${BLUE}Step 3: Installing dependencies...${NC}"
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Error installing dependencies. Check requirements.txt"
    exit 1
fi
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

echo -e "${BLUE}Step 4: Checking for models...${NC}"
if [ -f "../models/xgb_sev_6m.joblib" ] && [ -f "../models/xgb_sev_12m.joblib" ] && [ -f "../models/xgb_sev_24m.joblib" ]; then
    echo -e "${GREEN}✓ All models found${NC}"
else
    echo -e "${YELLOW}⚠ Warning: Models not found in ../models/${NC}"
    echo "Please ensure the model files are in the correct location:"
    echo "  - ../models/xgb_sev_6m.joblib"
    echo "  - ../models/xgb_sev_12m.joblib"
    echo "  - ../models/xgb_sev_24m.joblib"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
echo ""

echo -e "${BLUE}Step 5: Creating logs directory...${NC}"
mkdir -p logs
echo -e "${GREEN}✓ Logs directory created${NC}"
echo ""

echo -e "${BLUE}Step 6: Starting application...${NC}"
echo -e "${YELLOW}╔════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║     PPMI Backend API Starting          ║${NC}"
echo -e "${YELLOW}║                                        ║${NC}"
echo -e "${YELLOW}║   API will be available at:            ║${NC}"
echo -e "${YELLOW}║   http://localhost:8000                ║${NC}"
echo -e "${YELLOW}║                                        ║${NC}"
echo -e "${YELLOW}║   Swagger Docs:                        ║${NC}"
echo -e "${YELLOW}║   http://localhost:8000/docs           ║${NC}"
echo -e "${YELLOW}║                                        ║${NC}"
echo -e "${YELLOW}║   Press Ctrl+C to stop the server      ║${NC}"
echo -e "${YELLOW}╚════════════════════════════════════════╝${NC}"
echo ""

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
