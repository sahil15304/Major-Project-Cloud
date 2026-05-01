import React from 'react';

export default function StatusBadge({ status, label }) {
  return (
    <div className={`status-badge status-${status}`}>
      <span className="dot" />
      <span>{label}</span>
    </div>
  );
}
