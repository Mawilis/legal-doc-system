/**
 * API base URL used everywhere in the client.
 * Reads from REACT_APP_API_URL and falls back to same-host dev proxy pattern.
 */
const fromEnv = process.env.REACT_APP_API_URL;

// Fallback for local dev if env var is missing
const fallback = (() => {
  const proto = window.location.protocol.startsWith('https') ? 'https' : 'http';
  return `${proto}://${window.location.hostname}:3001/api`;
})();

const API_URL = fromEnv || fallback;

// Debug (dev only)
if (process.env.NODE_ENV === 'development') {
  // eslint-disable-next-line no-console
  console.log('[config/api] API_URL =', API_URL, '(fromEnv:', !!fromEnv, ')');
}

export default API_URL;
