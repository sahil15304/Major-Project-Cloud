const DEFAULT_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://54.89.118.72:8000';

function normalizeBaseUrl(baseUrl) {
  return baseUrl.replace(/\/$/, '');
}

function buildUrl(path) {
  return `${normalizeBaseUrl(DEFAULT_BASE_URL)}${path}`;
}

async function parseResponse(response) {
  const contentType = response.headers.get('content-type') || '';
  const text = await response.text();

  let data = null;
  if (text) {
    if (contentType.includes('application/json')) {
      try {
        data = JSON.parse(text);
      } catch {
        data = { detail: text };
      }
    } else {
      data = { detail: text };
    }
  }

  if (!response.ok) {
    const detail = data?.detail || data?.message || 'Request failed';
    throw new Error(detail);
  }

  return data;
}

async function request(path, options = {}, timeoutMs = 15000) {
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(buildUrl(path), {
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
      ...options,
      signal: controller.signal,
    });

    return await parseResponse(response);
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('Request timed out. Please try again.');
    }

    if (error instanceof TypeError) {
      throw new Error('Server not reachable. Please check the API URL or network connection.');
    }

    throw error;
  } finally {
    window.clearTimeout(timeoutId);
  }
}

export async function fetchHealthStatus() {
  return request('/api/health', { method: 'GET' });
}

export async function predictSeverity(payload) {
  // Send all 6 features: NP1TOT, NP2TOT, NP3TOT, MCATOT, AGE, SEX
  return request('/api/predict', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function getApiBaseUrl() {
  return normalizeBaseUrl(DEFAULT_BASE_URL);
}