const DEFAULT_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
const KNOWN_BACKENDS = [
  DEFAULT_BASE_URL,
  'http://127.0.0.1:8000',
  'http://localhost:8000',
  'http://54.89.118.72:8000',
];

function normalizeBaseUrl(url) {
  return String(url || '').replace(/\/$/, '');
}

async function request(path, options = {}, timeoutMs = 15000) {
  const { baseUrl, ...requestOptions } = options;
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), timeoutMs);
  const resolvedBaseUrl = normalizeBaseUrl(baseUrl || DEFAULT_BASE_URL);

  try {
    const response = await fetch(`${resolvedBaseUrl}${path}`, {
      headers: {
        'Content-Type': 'application/json',
        ...(requestOptions.headers || {}),
      },
      ...requestOptions,
      signal: controller.signal,
    });

    const text = await response.text();
    let data = null;

    if (text) {
      try {
        data = JSON.parse(text);
      } catch {
        data = { detail: text };
      }
    }

    if (!response.ok) {
      throw new Error(data?.detail || data?.message || 'Request failed');
    }

    return data;
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('Request timed out');
    }
    if (error instanceof TypeError) {
      throw new Error('API Down');
    }
    throw error;
  } finally {
    window.clearTimeout(timeout);
  }
}

export function getApiBaseUrl() {
  return normalizeBaseUrl(DEFAULT_BASE_URL);
}

export function getKnownApiBaseUrls(preferredUrl) {
  const ordered = [preferredUrl, ...KNOWN_BACKENDS]
    .map((url) => normalizeBaseUrl(url))
    .filter(Boolean);
  return [...new Set(ordered)];
}

export async function checkApiHealth(baseUrl) {
  return request('/api/health', { method: 'GET', baseUrl });
}

export async function predictSeverity(payload, baseUrl) {
  return request('/api/predict', {
    method: 'POST',
    body: JSON.stringify(payload),
    baseUrl,
  });
}

export async function predictAndStoreSeverity(payload, baseUrl) {
  return request('/ingest/predict-store', {
    method: 'POST',
    body: JSON.stringify(payload),
    baseUrl,
  });
}
