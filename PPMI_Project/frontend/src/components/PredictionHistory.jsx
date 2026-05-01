import React from 'react';

export default function PredictionHistory({ history }) {
  return (
    <div className="history">
      <div className="section-head compact">
        <div>
          <p className="eyebrow">History</p>
          <h2>Previous predictions</h2>
        </div>
      </div>

      {history.length === 0 ? (
        <p className="muted">No prediction history yet.</p>
      ) : (
        <ul className="history-list">
          {history.map((item) => (
            <li key={item.id}>
              <strong>6m:</strong> {item.result.severity_6m.toFixed(2)} · <strong>12m:</strong> {item.result.severity_12m.toFixed(2)} · <strong>24m:</strong> {item.result.severity_24m.toFixed(2)}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
