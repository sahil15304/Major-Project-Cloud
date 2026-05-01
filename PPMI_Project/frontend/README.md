# PPMI Severity Frontend

Clean React frontend for the Parkinson's Disease Severity Prediction system.

## Run locally

```bash
npm install
npm run dev
```

## API configuration

Set `VITE_API_BASE_URL` if your backend is hosted elsewhere.

## What it does

- Shows API health status
- Sends clinical values to the FastAPI backend
- Displays 6, 12, and 24 month severity predictions
- Keeps a small local history of recent predictions
