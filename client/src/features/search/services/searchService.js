const API_BASE =
  (typeof process !== 'undefined' && process.env.REACT_APP_API_URL) ||
  (window.__API_URL__ || 'http://localhost:3001/api');

/**
 * Call backend search endpoint: GET /api/search?q=...
 * Attaches Bearer token when available.
 * Returns { results: [...] } ideally, but also tolerates array bodies.
 */
export async function searchAll(query, token) {
  const url = `${API_BASE}/search?q=${encodeURIComponent(query || '')}`;
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(url, { method: 'GET', headers });

  // Graceful 404 -> caller can fallback to local demo
  if (res.status === 404) {
    const body = await res.text().catch(() => '');
    const err = new Error('SEARCH_ENDPOINT_NOT_FOUND');
    err.status = 404;
    err.body = body;
    throw err;
  }

  if (!res.ok) {
    const body = await res.text().catch(() => '');
    const err = new Error(`HTTP_${res.status}`);
    err.status = res.status;
    err.body = body;
    throw err;
  }

  const data = await res.json().catch(() => ({}));
  // Accept either {results:[...]} or [...]
  if (Array.isArray(data)) return { results: data };
  return { results: Array.isArray(data.results) ? data.results : [] };
}
