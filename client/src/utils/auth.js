// ~/client/src/utils/auth.js
export function getToken() {
  try {
    const raw = localStorage.getItem('token') || localStorage.getItem('authToken');
    if (raw) return raw;
    // fallback: read cookie named "token"
    const m = document.cookie.match(/(?:^|;)\s*token=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : '';
  } catch {
    return '';
  }
}
