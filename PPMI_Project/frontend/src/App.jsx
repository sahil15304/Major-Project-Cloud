import React from 'react';
import { useEffect, useMemo, useState } from 'react';
import { checkApiHealth, getApiBaseUrl, predictSeverity } from './services/api';
import PredictionForm from './components/PredictionForm';
import PredictionResults from './components/PredictionResults';
import PredictionHistory from './components/PredictionHistory';
import StatusBadge from './components/StatusBadge';

const REQUIRED_FIELDS = ['AGE', 'SEX', 'NP1TOT', 'NP2TOT', 'NP3TOT', 'MCATOT', 'SEVERITY'];
const STORAGE_KEY = 'ppmi-severity-history';

const INITIAL_VALUES = {
  AGE: '',
  SEX: '',
  NP1TOT: '',
  NP2TOT: '',
  NP3TOT: '',
  MCATOT: '',
  SEVERITY: '',
};

function readHistory() {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function normalizePrediction(response) {
  const payload = response?.prediction ?? response?.result ?? response?.data ?? response;
  return {
    severity_6m: Number(payload?.severity_6m),
    severity_12m: Number(payload?.severity_12m),
    severity_24m: Number(payload?.severity_24m),
  };
}

function friendlyError(message) {
  const text = String(message || '').toLowerCase();
  if (text.includes('400') || text.includes('validation') || text.includes('feature') || text.includes('missing')) {
    return 'Invalid input or missing features.';
  }
  if (text.includes('timeout')) {
    return 'Request timed out. Please try again.';
  }
  if (text.includes('network') || text.includes('failed to fetch') || text.includes('reachable')) {
    return 'API Down. Please check the backend connection.';
  }
  return message || 'Something went wrong.';
}

export default function App() {
  const [values, setValues] = useState(INITIAL_VALUES);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [history, setHistory] = useState(readHistory);
  const [health, setHealth] = useState({ status: 'checking', label: 'Checking...' });

  const apiBaseUrl = useMemo(() => getApiBaseUrl(), []);

  useEffect(() => {
    let alive = true;

    async function refreshHealth() {
      try {
        const result = await checkApiHealth();
        if (!alive) return;
        setHealth({
          status: result?.status === 'healthy' ? 'healthy' : 'down',
          label: result?.status === 'healthy' ? 'API Status: Healthy' : 'API Status: Down',
        });
      } catch {
        if (!alive) return;
        setHealth({ status: 'down', label: 'API Status: Down' });
      }
    }

    refreshHealth();
    return () => {
      alive = false;
    };
  }, []);

  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(history.slice(0, 5)));
  }, [history]);

  function handleChange(event) {
    const { name, value } = event.target;
    setValues((current) => ({ ...current, [name]: value }));
    setError('');
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');

    const payload = {};
    for (const field of REQUIRED_FIELDS) {
      if (values[field] === '') {
        setError('Invalid input or missing features.');
        return;
      }
      payload[field] = Number(values[field]);
    }

    try {
      setLoading(true);
      const response = await predictSeverity(payload);
      const normalized = normalizePrediction(response);

      if (!Object.values(normalized).every(Number.isFinite)) {
        throw new Error('Unexpected prediction response.');
      }

      setPrediction(normalized);
      setHistory((current) => [{ id: Date.now(), input: payload, result: normalized }, ...current].slice(0, 5));
    } catch (err) {
      setPrediction(null);
      setError(friendlyError(err.message));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-shell">
      <main className="dashboard">
        <section className="hero card">
          <div>
            <p className="eyebrow">Parkinson’s Disease Prediction</p>
            <h1>Parkinson’s Disease Severity Prediction</h1>
            <p className="hero-copy">
              Enter the clinical scores, call the live FastAPI endpoint, and review severity estimates for 6, 12, and 24 months.
            </p>
          </div>

          <div className="hero-meta">
            <StatusBadge status={health.status} label={health.label} />
            <div className="meta-chip">
              <span>Backend</span>
              <strong>{apiBaseUrl}</strong>
            </div>
          </div>
        </section>

        <section className="content-grid">
          <div className="card form-card">
            <PredictionForm
              values={values}
              onChange={handleChange}
              onSubmit={handleSubmit}
              loading={loading}
            />
          </div>

          <div className="stack">
            {error ? <div className="alert error">{error}</div> : null}
            <div className="card results-card">
              <PredictionResults prediction={prediction} loading={loading} />
            </div>
            <div className="card history-card">
              <PredictionHistory history={history} />
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
