import { useEffect, useMemo, useState } from 'react';
import Card from '../components/Card';
import ClinicalForm from '../components/ClinicalForm';
import PredictionResults from '../components/PredictionResults';
import StatusBadge from '../components/StatusBadge';
import ActionButton from '../components/ActionButton';
import { fetchHealthStatus, getApiBaseUrl, predictSeverity } from '../services/api';

const INITIAL_VALUES = {
  NP1TOT: '',
  NP2TOT: '',
  NP3TOT: '',
  MCATOT: '',
  AGE: '',
  SEX: '1',
};

const SAMPLE_INPUT = {
  NP1TOT: '6',
  NP2TOT: '18',
  NP3TOT: '42',
  MCATOT: '25',
  AGE: '68',
  SEX: '1',
};

const LIMITS = {
  NP1TOT: { min: 0, max: 16 },
  NP2TOT: { min: 0, max: 52 },
  NP3TOT: { min: 0, max: 108 },
  MCATOT: { min: 0, max: 30 },
  AGE: { min: 0, max: 120 },
};

function validate(values) {
  const errors = {};

  for (const [field, limits] of Object.entries(LIMITS)) {
    const raw = values[field];

    if (raw === '') {
      errors[field] = 'This field is required.';
      continue;
    }

    const value = Number(raw);
    if (!Number.isFinite(value)) {
      errors[field] = 'Enter a valid number.';
      continue;
    }

    if (value < limits.min || value > limits.max) {
      errors[field] = `Must be between ${limits.min} and ${limits.max}.`;
    }
  }

  if (values.SEX !== '0' && values.SEX !== '1') {
    errors.SEX = 'Please choose Male or Female.';
  }

  return errors;
}

function normalizePrediction(response) {
  const candidate = response?.prediction ?? response?.result ?? response?.data ?? response;
  const prediction = {
    severity_6m: Number(candidate?.severity_6m),
    severity_12m: Number(candidate?.severity_12m),
    severity_24m: Number(candidate?.severity_24m),
  };

  if (Object.values(prediction).some((value) => !Number.isFinite(value))) {
    throw new Error('Unexpected API response. The backend returned an invalid prediction payload.');
  }

  return prediction;
}

function friendlyError(message) {
  const lowerMessage = String(message || '').toLowerCase();

  if (lowerMessage.includes('feature') || lowerMessage.includes('validation') || lowerMessage.includes('422')) {
    return 'Invalid input. Please check all six fields and try again.';
  }

  if (lowerMessage.includes('timed out')) {
    return 'The request timed out. Please try again.';
  }

  if (lowerMessage.includes('not reachable') || lowerMessage.includes('network')) {
    return 'Server not reachable. Please confirm the backend URL and network connection.';
  }

  return message || 'Something went wrong while requesting the prediction.';
}

export default function DashboardPage() {
  const [values, setValues] = useState(INITIAL_VALUES);
  const [errors, setErrors] = useState({});
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [submissionMessage, setSubmissionMessage] = useState('');
  const [submissionError, setSubmissionError] = useState('');
  const [apiStatus, setApiStatus] = useState({ state: 'checking', label: 'Checking API', checkedAt: null });

  const apiBaseUrl = useMemo(() => getApiBaseUrl(), []);

  useEffect(() => {
    let cancelled = false;

    async function checkApi() {
      try {
        const health = await fetchHealthStatus();
        if (!cancelled) {
          setApiStatus({
            state: 'online',
            label: health?.status ? `API ${health.status}` : 'API reachable',
            checkedAt: new Date(),
          });
        }
      } catch (error) {
        if (!cancelled) {
          setApiStatus({
            state: 'offline',
            label: 'API offline',
            checkedAt: new Date(),
          });
        }
      }
    }

    checkApi();
    const intervalId = window.setInterval(checkApi, 60000);

    return () => {
      cancelled = true;
      window.clearInterval(intervalId);
    };
  }, []);

  function handleChange(event) {
    const { name, value } = event.target;
    setValues((current) => ({ ...current, [name]: value }));
    setErrors((current) => ({ ...current, [name]: undefined }));
    setSubmissionError('');
    setSubmissionMessage('');
  }

  function handleExample() {
    setValues(SAMPLE_INPUT);
    setErrors({});
    setSubmissionError('');
    setSubmissionMessage('Example input loaded. You can adjust any value before predicting.');
    setPrediction(null);
  }

  function handleReset() {
    setValues(INITIAL_VALUES);
    setErrors({});
    setPrediction(null);
    setSubmissionError('');
    setSubmissionMessage('Form cleared.');
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmissionError('');
    setSubmissionMessage('');

    const nextErrors = validate(values);
    setErrors(nextErrors);

    if (Object.keys(nextErrors).length > 0) {
      setPrediction(null);
      return;
    }

    const payload = {
      NP1TOT: Number(values.NP1TOT),
      NP2TOT: Number(values.NP2TOT),
      NP3TOT: Number(values.NP3TOT),
      MCATOT: Number(values.MCATOT),
      AGE: Number(values.AGE),
      SEX: Number(values.SEX),
    };

    try {
      setLoading(true);
      const response = await predictSeverity(payload);
      const normalized = normalizePrediction(response);
      setPrediction(normalized);
      setSubmissionMessage('Prediction completed successfully.');
    } catch (error) {
      setPrediction(null);
      setSubmissionError(friendlyError(error.message));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="dashboard-grid">
      <section className="mb-6 overflow-hidden rounded-[2rem] border border-white/70 bg-white/75 px-6 py-8 shadow-soft backdrop-blur sm:px-8 lg:px-10">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl space-y-5">
            <div className="flex flex-wrap items-center gap-3">
              <StatusBadge state={apiStatus.state} label={apiStatus.label} />
              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600 ring-1 ring-slate-200">
                Backend: {apiBaseUrl}
              </span>
            </div>

            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.24em] text-teal-700">
                Parkinson’s Disease Severity Prediction
              </p>
              <h1 className="mt-3 text-3xl font-extrabold tracking-tight text-slate-950 sm:text-4xl lg:text-5xl">
                Clinical dashboard for 6, 12, and 24 month severity forecasting.
              </h1>
              <p className="mt-4 max-w-2xl text-base leading-7 text-slate-600 sm:text-lg">
                Enter six clinical features, send them to the deployed FastAPI backend, and visualize the predicted severity progression in a clean, research-friendly interface.
              </p>
            </div>
          </div>

          <div className="grid gap-3 sm:grid-cols-3 lg:min-w-[360px] lg:grid-cols-1">
            <Card className="p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Model input</p>
              <p className="mt-2 text-xl font-bold text-slate-900">6 features</p>
              <p className="mt-1 text-sm text-slate-500">Includes AGE and SEX to prevent feature mismatch.</p>
            </Card>
            <Card className="p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">API endpoint</p>
              <p className="mt-2 text-xl font-bold text-slate-900">/api/predict</p>
              <p className="mt-1 text-sm text-slate-500">Connected to the live FastAPI service.</p>
            </Card>
            <Card className="p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Health check</p>
              <p className="mt-2 text-xl font-bold text-slate-900">
                {apiStatus.state === 'online' ? 'Online' : apiStatus.state === 'offline' ? 'Offline' : 'Checking'}
              </p>
              <p className="mt-1 text-sm text-slate-500">
                {apiStatus.checkedAt ? `Checked at ${apiStatus.checkedAt.toLocaleTimeString()}` : 'Checking backend status...'}
              </p>
            </Card>
          </div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.06fr_0.94fr]">
        <div className="space-y-6">
          <Card className="p-6 sm:p-7">
            <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
              <div>
                <h2 className="text-2xl font-bold tracking-tight text-slate-950">Clinical Input Form</h2>
                <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                  The backend expects NP1TOT, NP2TOT, NP3TOT, MCATOT, AGE, and SEX. All fields are validated before the request is sent.
                </p>
              </div>
              <div className="rounded-2xl bg-teal-50 px-4 py-3 text-sm text-teal-800 ring-1 ring-teal-100">
                Use the example button for a quick test case.
              </div>
            </div>

            <ClinicalForm
              values={values}
              errors={errors}
              loading={loading}
              onChange={handleChange}
              onSubmit={handleSubmit}
              onReset={handleReset}
              onExample={handleExample}
            />
          </Card>

          <Card className="p-6 sm:p-7">
            <h3 className="text-lg font-semibold text-slate-950">Prediction workflow</h3>
            <div className="mt-4 grid gap-4 md:grid-cols-3">
              {[
                {
                  title: '1. Fill the form',
                  copy: 'Enter all six clinical features to keep the request aligned with the trained model.',
                },
                {
                  title: '2. Run prediction',
                  copy: 'The app sends JSON to the live FastAPI backend and waits for a response.',
                },
                {
                  title: '3. Review results',
                  copy: 'Severity values and progression are rendered as cards and a line chart.',
                },
              ].map((item) => (
                <div key={item.title} className="rounded-2xl bg-slate-50 p-4 ring-1 ring-slate-200/80">
                  <p className="font-semibold text-slate-900">{item.title}</p>
                  <p className="mt-2 text-sm leading-6 text-slate-500">{item.copy}</p>
                </div>
              ))}
            </div>
          </Card>
        </div>

        <div className="space-y-4">
          {submissionError ? (
            <Card className="border-rose-200 bg-rose-50/80 p-5 text-rose-800 ring-1 ring-rose-200">
              <p className="text-sm font-semibold uppercase tracking-wide text-rose-700">Request failed</p>
              <p className="mt-2 text-sm leading-6">{submissionError}</p>
            </Card>
          ) : null}

          {submissionMessage ? (
            <Card className="border-emerald-200 bg-emerald-50/80 p-5 text-emerald-800 ring-1 ring-emerald-200">
              <p className="text-sm font-semibold uppercase tracking-wide text-emerald-700">Status</p>
              <p className="mt-2 text-sm leading-6">{submissionMessage}</p>
            </Card>
          ) : null}

          <PredictionResults prediction={prediction} />

          <Card className="p-5">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h3 className="text-lg font-semibold text-slate-900">API status</h3>
                <p className="mt-1 text-sm text-slate-500">Refresh the health endpoint if you want to re-check the backend.</p>
              </div>
              <ActionButton
                variant="secondary"
                onClick={async () => {
                  setApiStatus((current) => ({ ...current, state: 'checking', label: 'Checking API' }));
                  try {
                    const health = await fetchHealthStatus();
                    setApiStatus({
                      state: 'online',
                      label: health?.status ? `API ${health.status}` : 'API reachable',
                      checkedAt: new Date(),
                    });
                  } catch {
                    setApiStatus({ state: 'offline', label: 'API offline', checkedAt: new Date() });
                  }
                }}
              >
                Refresh status
              </ActionButton>
            </div>
            <div className="mt-4 rounded-2xl bg-slate-50 p-4 ring-1 ring-slate-200">
              <p className="text-sm leading-6 text-slate-600">
                If you see a feature mismatch error, verify that AGE and SEX are included. This dashboard always sends all six features.
              </p>
            </div>
          </Card>
        </div>
      </section>
    </main>
  );
}