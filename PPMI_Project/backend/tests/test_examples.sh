#!/bin/bash

# PPMI Backend API - Test Examples
# Usage: ./test_examples.sh
# Make sure the API is running on http://localhost:8000

API_URL="http://localhost:8000"

echo "================================"
echo "PPMI API Testing Examples"
echo "================================"
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print section
print_section() {
    echo -e "${BLUE}>>> $1${NC}"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Test 1: Health Check
print_section "1. Health Check - GET /api/health"
curl -s "$API_URL/api/health" | python -m json.tool
echo ""

# Test 2: API Status
print_section "2. API Status - GET /status"
curl -s "$API_URL/status" | python -m json.tool
echo ""

# Test 3: API Version
print_section "3. API Version - GET /api/version"
curl -s "$API_URL/api/version" | python -m json.tool
echo ""

# Test 4: Models Information
print_section "4. Models Information - GET /api/models/info"
curl -s "$API_URL/api/models/info" | python -m json.tool
echo ""

# Test 5: Valid Prediction Request
print_section "5. Valid Prediction - POST /api/predict"
PREDICTION_PAYLOAD=$(cat <<EOF
{
  "NP1TOT": 5.0,
  "NP2TOT": 15.0,
  "NP3TOT": 35.0,
  "MCATOT": 26.0
}
EOF
)

echo "Request Payload:"
echo "$PREDICTION_PAYLOAD" | python -m json.tool
echo ""
echo "Response:"
curl -s -X POST "$API_URL/api/predict" \
  -H "Content-Type: application/json" \
  -d "$PREDICTION_PAYLOAD" | python -m json.tool
echo ""

# Test 6: Another Valid Prediction (Different Values)
print_section "6. Another Valid Prediction with Different Values"
PREDICTION_PAYLOAD2=$(cat <<EOF
{
  "NP1TOT": 10.0,
  "NP2TOT": 25.0,
  "NP3TOT": 55.0,
  "MCATOT": 24.0
}
EOF
)

echo "Request Payload:"
echo "$PREDICTION_PAYLOAD2" | python -m json.tool
echo ""
echo "Response:"
curl -s -X POST "$API_URL/api/predict" \
  -H "Content-Type: application/json" \
  -d "$PREDICTION_PAYLOAD2" | python -m json.tool
echo ""

# Test 7: Invalid Input - Missing Field
print_section "7. Invalid Input - Missing MCATOT Field (should get 422 error)"
INVALID_PAYLOAD1=$(cat <<EOF
{
  "NP1TOT": 5.0,
  "NP2TOT": 15.0,
  "NP3TOT": 35.0
}
EOF
)

echo "Request Payload (missing MCATOT):"
echo "$INVALID_PAYLOAD1" | python -m json.tool
echo ""
echo "Response (expect error):"
curl -s -X POST "$API_URL/api/predict" \
  -H "Content-Type: application/json" \
  -d "$INVALID_PAYLOAD1" | python -m json.tool
echo ""

# Test 8: Invalid Input - Out of Range
print_section "8. Invalid Input - Out of Range (NP1TOT > 16)"
INVALID_PAYLOAD2=$(cat <<EOF
{
  "NP1TOT": 25.0,
  "NP2TOT": 15.0,
  "NP3TOT": 35.0,
  "MCATOT": 26.0
}
EOF
)

echo "Request Payload (NP1TOT out of range):"
echo "$INVALID_PAYLOAD2" | python -m json.tool
echo ""
echo "Response (expect error):"
curl -s -X POST "$API_URL/api/predict" \
  -H "Content-Type: application/json" \
  -d "$INVALID_PAYLOAD2" | python -m json.tool
echo ""

# Test 9: Edge Case - Minimum Values
print_section "9. Edge Case - Minimum Valid Values"
EDGE_CASE_MIN=$(cat <<EOF
{
  "NP1TOT": 0.0,
  "NP2TOT": 0.0,
  "NP3TOT": 0.0,
  "MCATOT": 0.0
}
EOF
)

echo "Request Payload (all zeros):"
echo "$EDGE_CASE_MIN" | python -m json.tool
echo ""
echo "Response:"
curl -s -X POST "$API_URL/api/predict" \
  -H "Content-Type: application/json" \
  -d "$EDGE_CASE_MIN" | python -m json.tool
echo ""

# Test 10: Edge Case - Maximum Values
print_section "10. Edge Case - Maximum Valid Values"
EDGE_CASE_MAX=$(cat <<EOF
{
  "NP1TOT": 16.0,
  "NP2TOT": 52.0,
  "NP3TOT": 108.0,
  "MCATOT": 30.0
}
EOF
)

echo "Request Payload (max values):"
echo "$EDGE_CASE_MAX" | python -m json.tool
echo ""
echo "Response:"
curl -s -X POST "$API_URL/api/predict" \
  -H "Content-Type: application/json" \
  -d "$EDGE_CASE_MAX" | python -m json.tool
echo ""

# Test 11: Root Endpoint
print_section "11. Root Endpoint - GET /"
curl -s "$API_URL/" | python -m json.tool
echo ""

print_success "All tests completed!"
print_section "Testing Summary:"
echo "
✓ Health Check: Verify API and models are running
✓ Valid Predictions: Test normal use cases
✓ Invalid Inputs: Test validation and error handling
✓ Edge Cases: Test boundary values
✓ Documentation: Verify Swagger UI at $API_URL/docs
"
