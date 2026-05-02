import React from 'react';

function ResultCard({ label, value }) {
  return (
    <div className="result-card-mini">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

export default function PredictionResults({ prediction, loading, storage }) {
  if (loading) {
    return (
      <div className="empty-state">
        <div className="spinner" />
        <h2>Predicting...</h2>
        <p>Please wait while the backend returns severity values.</p>
      </div>
    );
  }

  if (!prediction) {
    return (
      <div className="empty-state">
        <div className="empty-icon">↗</div>
        <h2>Prediction results will appear here</h2>
        <p>Fill the form and click Predict to see the 6, 12, and 24 month severity estimates.</p>
      </div>
    );
  }

  return (
    <div className="results">
      <div className="section-head compact">
        <div>
          <p className="eyebrow">Prediction result</p>
          <h2>Severity forecast</h2>
        </div>
      </div>

      <div className="result-grid">
        <ResultCard label="6 months" value={prediction.severity_6m.toFixed(2)} />
        <ResultCard label="12 months" value={prediction.severity_12m.toFixed(2)} />
        <ResultCard label="24 months" value={prediction.severity_24m.toFixed(2)} />
      </div>

      {/* Intentionally hide storage metadata for a clean, formal UI */}
    </div>
  );
}
