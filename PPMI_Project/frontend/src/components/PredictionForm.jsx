import React from 'react';

const REQUIRED_FIELDS = [
  { name: 'AGE', label: 'AGE', min: 0, max: 120, helper: 'Patient age in years' },
  { name: 'SEX', label: 'SEX', min: 0, max: 1, helper: 'Encode as 0 (female) or 1 (male)' },
  { name: 'NP1TOT', label: 'NP1TOT', min: 0, max: 16, helper: 'Non-motor experiences total score' },
  { name: 'NP2TOT', label: 'NP2TOT', min: 0, max: 52, helper: 'Motor experiences total score' },
  { name: 'NP3TOT', label: 'NP3TOT', min: 0, max: 108, helper: 'Motor examination score' },
  { name: 'MCATOT', label: 'MCATOT', min: 0, max: 30, helper: 'Cognitive assessment total' },
  { name: 'SEVERITY', label: 'SEVERITY', min: 0, max: 100, helper: 'Current severity score' },
];

export default function PredictionForm({ values, onChange, onSubmit, loading }) {
  return (
    <form onSubmit={onSubmit} className="form">
      <div className="section-head">
        <div>
          <p className="eyebrow">Clinical input</p>
          <h2>Enter the required scores</h2>
        </div>
      </div>

      <div className="field-grid">
        {REQUIRED_FIELDS.map((field) => (
          <label key={field.name} className="field">
            <span>
              {field.label}
              <small>{field.min} to {field.max}</small>
            </span>
            <input
              type="number"
              name={field.name}
              value={values[field.name]}
              min={field.min}
              max={field.max}
              step="0.01"
              onChange={onChange}
              placeholder={`${field.min} - ${field.max}`}
            />
            <small className="helper">{field.helper}</small>
          </label>
        ))}
      </div>

      <div className="button-row">
        <button type="submit" className="primary-button" disabled={loading}>
          {loading ? 'Predicting...' : 'Predict'}
        </button>
      </div>
    </form>
  );
}
