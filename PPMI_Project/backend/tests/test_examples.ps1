# PPMI Backend API - Test Examples (PowerShell)
# Usage: .\test_examples.ps1
# Make sure the API is running on http://localhost:8000

$API_URL = "http://localhost:8000"

Write-Host "================================" -ForegroundColor Blue
Write-Host "PPMI API Testing Examples" -ForegroundColor Blue
Write-Host "================================" -ForegroundColor Blue
Write-Host ""

function Print-Section {
    param([string]$text)
    Write-Host ">>> $text" -ForegroundColor Cyan
}

function Print-Success {
    param([string]$text)
    Write-Host "✓ $text" -ForegroundColor Green
}

# Test 1: Health Check
Print-Section "1. Health Check - GET /api/health"
$response = Invoke-RestMethod -Uri "$API_URL/api/health" -Method Get
$response | ConvertTo-Json
Write-Host ""

# Test 2: API Status
Print-Section "2. API Status - GET /status"
$response = Invoke-RestMethod -Uri "$API_URL/status" -Method Get
$response | ConvertTo-Json
Write-Host ""

# Test 3: API Version
Print-Section "3. API Version - GET /api/version"
$response = Invoke-RestMethod -Uri "$API_URL/api/version" -Method Get
$response | ConvertTo-Json
Write-Host ""

# Test 4: Models Information
Print-Section "4. Models Information - GET /api/models/info"
$response = Invoke-RestMethod -Uri "$API_URL/api/models/info" -Method Get
$response | ConvertTo-Json
Write-Host ""

# Test 5: Valid Prediction Request
Print-Section "5. Valid Prediction - POST /api/predict"
$predictionPayload = @{
    NP1TOT = 5.0
    NP2TOT = 15.0
    NP3TOT = 35.0
    MCATOT = 26.0
} | ConvertTo-Json

Write-Host "Request Payload:"
$predictionPayload | ConvertFrom-Json | ConvertTo-Json
Write-Host ""
Write-Host "Response:"
$response = Invoke-RestMethod -Uri "$API_URL/api/predict" `
    -Method Post `
    -ContentType "application/json" `
    -Body $predictionPayload
$response | ConvertTo-Json
Write-Host ""

# Test 6: Another Valid Prediction
Print-Section "6. Another Valid Prediction with Different Values"
$predictionPayload2 = @{
    NP1TOT = 10.0
    NP2TOT = 25.0
    NP3TOT = 55.0
    MCATOT = 24.0
} | ConvertTo-Json

Write-Host "Request Payload:"
$predictionPayload2 | ConvertFrom-Json | ConvertTo-Json
Write-Host ""
Write-Host "Response:"
$response = Invoke-RestMethod -Uri "$API_URL/api/predict" `
    -Method Post `
    -ContentType "application/json" `
    -Body $predictionPayload2
$response | ConvertTo-Json
Write-Host ""

# Test 7: Invalid Input - Missing Field
Print-Section "7. Invalid Input - Missing MCATOT Field (should get error)"
$invalidPayload1 = @{
    NP1TOT = 5.0
    NP2TOT = 15.0
    NP3TOT = 35.0
} | ConvertTo-Json

Write-Host "Request Payload (missing MCATOT):"
$invalidPayload1 | ConvertFrom-Json | ConvertTo-Json
Write-Host ""
Write-Host "Response (expect error):"
try {
    $response = Invoke-RestMethod -Uri "$API_URL/api/predict" `
        -Method Post `
        -ContentType "application/json" `
        -Body $invalidPayload1
    $response | ConvertTo-Json
}
catch {
    Write-Host "Error: " -ForegroundColor Red
    $_.Exception.Response | ConvertTo-Json
}
Write-Host ""

# Test 8: Invalid Input - Out of Range
Print-Section "8. Invalid Input - Out of Range (NP1TOT > 16)"
$invalidPayload2 = @{
    NP1TOT = 25.0
    NP2TOT = 15.0
    NP3TOT = 35.0
    MCATOT = 26.0
} | ConvertTo-Json

Write-Host "Request Payload (NP1TOT out of range):"
$invalidPayload2 | ConvertFrom-Json | ConvertTo-Json
Write-Host ""
Write-Host "Response (expect error):"
try {
    $response = Invoke-RestMethod -Uri "$API_URL/api/predict" `
        -Method Post `
        -ContentType "application/json" `
        -Body $invalidPayload2
    $response | ConvertTo-Json
}
catch {
    Write-Host "Error: " -ForegroundColor Red
    $_.Exception.Response | ConvertTo-Json
}
Write-Host ""

# Test 9: Edge Case - Minimum Values
Print-Section "9. Edge Case - Minimum Valid Values"
$edgeCaseMin = @{
    NP1TOT = 0.0
    NP2TOT = 0.0
    NP3TOT = 0.0
    MCATOT = 0.0
} | ConvertTo-Json

Write-Host "Request Payload (all zeros):"
$edgeCaseMin | ConvertFrom-Json | ConvertTo-Json
Write-Host ""
Write-Host "Response:"
$response = Invoke-RestMethod -Uri "$API_URL/api/predict" `
    -Method Post `
    -ContentType "application/json" `
    -Body $edgeCaseMin
$response | ConvertTo-Json
Write-Host ""

# Test 10: Edge Case - Maximum Values
Print-Section "10. Edge Case - Maximum Valid Values"
$edgeCaseMax = @{
    NP1TOT = 16.0
    NP2TOT = 52.0
    NP3TOT = 108.0
    MCATOT = 30.0
} | ConvertTo-Json

Write-Host "Request Payload (max values):"
$edgeCaseMax | ConvertFrom-Json | ConvertTo-Json
Write-Host ""
Write-Host "Response:"
$response = Invoke-RestMethod -Uri "$API_URL/api/predict" `
    -Method Post `
    -ContentType "application/json" `
    -Body $edgeCaseMax
$response | ConvertTo-Json
Write-Host ""

# Test 11: Root Endpoint
Print-Section "11. Root Endpoint - GET /"
$response = Invoke-RestMethod -Uri "$API_URL/" -Method Get
$response | ConvertTo-Json
Write-Host ""

Print-Success "All tests completed!"
Print-Section "Testing Summary:"
Write-Host @"
✓ Health Check: Verify API and models are running
✓ Valid Predictions: Test normal use cases
✓ Invalid Inputs: Test validation and error handling
✓ Edge Cases: Test boundary values
✓ Documentation: Verify Swagger UI at $API_URL/docs
"@
