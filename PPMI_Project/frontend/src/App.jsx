import React from 'react';
import { useEffect, useMemo, useState } from 'react';
import { checkApiHealth, getApiBaseUrl, getKnownApiBaseUrls, predictAndStoreSeverity } from './services/api';
import PredictionForm from './components/PredictionForm';
import PredictionResults from './components/PredictionResults';
import PredictionHistory from './components/PredictionHistory';
import StatusBadge from './components/StatusBadge';

  const REQUIRED_FIELDS = ['AGE', 'SEX', 'NP1TOT', 'NP2TOT', 'NP3TOT', 'MCATOT', 'SEVERITY'];
const STORAGE_KEY = 'ppmi-severity-history';
const API_URL_STORAGE_KEY = 'ppmi-api-base-url';

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

function normalizeStorage(response) {
  return response?.storage ?? response?.cloud ?? null;
}

function friendlyError(message) {
  const text = String(message || '').toLowerCase();
  if (text.includes('models not loaded') || text.includes('service unavailable')) {
    return 'Backend is connected, but ML models are not loaded on this server.';
  }
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
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [cloudStorage, setCloudStorage] = useState(null);
  const [history, setHistory] = useState(readHistory);
  const [health, setHealth] = useState({ status: 'checking', label: 'Checking...' });

  const apiBaseUrl = useMemo(() => {
    const saved = window.localStorage.getItem(API_URL_STORAGE_KEY);
    return saved || getApiBaseUrl();
  }, []);
  const [activeApiUrl, setActiveApiUrl] = useState(apiBaseUrl);
  const [apiInputUrl, setApiInputUrl] = useState(apiBaseUrl);

  async function connectBackend(preferredUrl) {
    setConnecting(true);
    setHealth({ status: 'checking', label: 'Checking...' });

    const candidates = getKnownApiBaseUrls(preferredUrl);
    for (const candidate of candidates) {
      try {
        const result = await checkApiHealth(candidate);
        const isHealthy = result?.status === 'healthy';

        setActiveApiUrl(candidate);
        setApiInputUrl(candidate);
        window.localStorage.setItem(API_URL_STORAGE_KEY, candidate);
        setHealth({
          status: isHealthy ? 'healthy' : 'down',
          label: isHealthy ? 'API Status: Healthy' : 'API Reachable (Models Not Loaded)',
        });
        setConnecting(false);
        return;
      } catch {
        // Try next candidate backend URL.
      }
    }

    setActiveApiUrl(preferredUrl || apiBaseUrl);
    setHealth({ status: 'down', label: 'API Status: Down' });
    setConnecting(false);
  }

  useEffect(() => {
    let alive = true;

    (async () => {
      await connectBackend(apiBaseUrl);
      if (!alive) return;
    })();

    return () => {
      alive = false;
    };
  }, [apiBaseUrl]);

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
      // SEVERITY is now hidden and considered 1 for every submission
      if (field === 'SEVERITY') {
        payload[field] = 1;
        continue;
      }

      if (values[field] === '') {
        setError('Invalid input or missing features.');
        return;
      }
      payload[field] = Number(values[field]);
    }

    try {
      setLoading(true);
      const response = await predictAndStoreSeverity(payload, activeApiUrl);
      const normalized = normalizePrediction(response);
      const storage = normalizeStorage(response);

      if (!Object.values(normalized).every(Number.isFinite)) {
        throw new Error('Unexpected prediction response.');
      }

      // Enforce monotonic (non-decreasing) severities client-side as a safety-net
      const s6 = Number(normalized.severity_6m);
      const s12 = Number(normalized.severity_12m);
      const s24 = Number(normalized.severity_24m);
      const s12_adj = Math.max(s6, s12);
      const s24_adj = Math.max(s12_adj, s24);
      const adjusted = {
        severity_6m: s6,
        severity_12m: s12_adj,
        severity_24m: s24_adj,
      };

      setPrediction(adjusted);
      setCloudStorage(storage);
      setHistory((current) => [{ id: Date.now(), input: payload, result: adjusted, storage }, ...current].slice(0, 5));
    } catch (err) {
      setPrediction(null);
      setCloudStorage(null);
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
              <strong>{activeApiUrl}</strong>
            </div>
            <form
              className="connection-form"
              onSubmit={(event) => {
                event.preventDefault();
                connectBackend(apiInputUrl);
              }}
            >
              <label htmlFor="backend-url" className="connection-label">Backend URL</label>
              <input
                id="backend-url"
                name="backend-url"
                type="url"
                value={apiInputUrl}
                onChange={(event) => setApiInputUrl(event.target.value)}
                placeholder="http://127.0.0.1:8000"
              />
              <button type="submit" className="ghost-button" disabled={connecting}>
                {connecting ? 'Connecting...' : 'Connect'}
              </button>
            </form>
            <div className="meta-chip compact">
              <span>Tip</span>
              <strong>Use local backend for latest 7-field schema.</strong>
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
              <PredictionResults prediction={prediction} loading={loading} storage={cloudStorage} />
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
