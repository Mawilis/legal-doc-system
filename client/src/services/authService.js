/**
 * File: client/src/services/authService.js
 * -----------------------------------------------------------------------------
 * COLLABORATION NOTES:
 * - Purpose: Encapsulates all authentication API calls (login/logout/refresh).
 * - Refresh Token Flow:
 *   • Backend must expose POST /auth/refresh that validates refresh token
 *     (usually via HttpOnly cookie or stored token).
 *   • Returns a new { accessToken, user, tenantId }.
 *   • This method updates localStorage so interceptors keep requests alive.
 * - Engineers:
 *   • Ensure refresh endpoint is secure (rotate tokens, invalidate on logout).
 *   • Consider HttpOnly cookies for refresh token in production.
 *   • Extend with auto‑refresh logic in Axios interceptors if desired.
 * -----------------------------------------------------------------------------
 */

import { apiPost } from '../services/http';

const API_URL = '/auth';

// --- LOGIN ---
const login = async (userData) => {
  const response = await apiPost(`${API_URL}/login`, userData);

  if (response.data) {
    const { accessToken, user, tenantId } = response.data;

    const sessionData = { token: accessToken, user, tenantId };

    localStorage.setItem('user', JSON.stringify({ email: user?.email, token: accessToken }));
    localStorage.setItem('accessToken', accessToken);
    if (tenantId) localStorage.setItem('tenantId', tenantId);

    return sessionData;
  }

  throw new Error('Login failed: no response data');
};

// --- LOGOUT ---
const logout = () => {
  localStorage.removeItem('user');
  localStorage.removeItem('accessToken');
  localStorage.removeItem('tenantId');
};

// --- REFRESH TOKEN ---
const refreshToken = async () => {
  try {
    const response = await apiPost(`${API_URL}/refresh`);

    if (response.data) {
      const { accessToken, user, tenantId } = response.data;

      const sessionData = { token: accessToken, user, tenantId };

      // Update storage so interceptors use the new token
      localStorage.setItem('user', JSON.stringify({ email: user?.email, token: accessToken }));
      localStorage.setItem('accessToken', accessToken);
      if (tenantId) localStorage.setItem('tenantId', tenantId);

      console.log('🔄 [AuthService] Token refreshed successfully');
      return sessionData;
    }

    throw new Error('Refresh failed: no response data');
  } catch (err) {
    console.error('🔴 [AuthService] Refresh token failed:', err);
    // Force logout if refresh fails
    logout();
    throw err;
  }
};

// --- EXPORT ---
const authService = { login, logout, refreshToken };
export default authService;
