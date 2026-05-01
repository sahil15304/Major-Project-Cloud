const DEFAULT_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://54.89.118.72:8000';

function normalizeBaseUrl(url) {
  return String(url || '').replace(/\/$/, '');
}

async function request(path, options = {}, timeoutMs = 15000) {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(`${normalizeBaseUrl(DEFAULT_BASE_URL)}${path}`, {
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
      ...options,
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

export async function checkApiHealth() {
  return request('/api/health', { method: 'GET' });
}

export async function predictSeverity(payload) {
  return request('/api/predict', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
