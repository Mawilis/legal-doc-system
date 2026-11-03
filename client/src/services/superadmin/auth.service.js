/* eslint-disable */
/**
 * Auth Service - Wilsy OS
 * Path: client/src/services/superadmin/auth.service.js
 *
 * Responsibilities:
 * - Login / logout / profile / verifyMFA
 * - Persist token and user to localStorage (normalized)
 * - Expose refreshToken() via window.__SOVEREIGN_AUTH__ for silent refresh
 * - Emit safe CustomEvents for UI and telemetry
 *
 * Security:
 * - Never log full tokens; only safe preview (first 8 chars)
 * * 🛡️ PRODUCTION READY v2.67.1:
 * • FIXED: verifyMFA body uses `otp` (server contract) + `code` alias
 * • FIXED: login always persists loginEmail for MFA step
 * • FIXED: Dynamic Tenant Resolution to prevent [GATEWAY] Sovereign breach.
 * • FIXED: 3FA endpoint now matches server (/api/auth/verify-3fa)
 * • Token persistence with proper key normalization
 * • Event emission for UI synchronization
 * • Refresh token capability for long sessions
 * • Safe preview logging for debugging
 *
 * @team Collaboration:
 * • Lead Architect: Wilson Khanyezi - Final approval
 * • Security: Dr. Priya Naidoo - Token management
 * • Frontend: Gemini - Auth integration
 * • AI Engineering (2026-08-20) — otp field parity with authController.verify3FA
 */
import api from '../api';

const TOKEN_KEY = 'sovereignToken';
const TENANT_KEY = 'tenantId';
const USER_KEY = 'userData';
const ROLE_KEY = 'userRole';
const OPERATOR_KEY = 'operatorName';

/**
 * Resolve only the tenant projection returned by the EOS discovery endpoint.
 * This is a request selector, never membership or authorization authority.
 * No hostname, role, legacy storage key, or default tenant is accepted.
 */
const getTenantContext = () => {
  try {
    const raw = localStorage.getItem('discoveredTenant');
    if (!raw) return null;
    const discovered = JSON.parse(raw);
    const tenantId = discovered?.tenantId;
    return (
      typeof tenantId === 'string'
      && tenantId === tenantId.trim()
      && /^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$/.test(tenantId)
    ) ? tenantId : null;
  } catch {
    return null;
  }
};

const safePreview = (token) => {
  if (!token) return 'NO_TOKEN';
  const t = String(token);
  return t.length > 8 ? `${t.slice(0, 8)}...` : `${t}...`;
};

const writeTokenAndUser = (token, user) => {
  try {
    if (!token) return;
    const normalized = String(token).trim().replace(/^Bearer\s+/i, '');
    localStorage.setItem(TOKEN_KEY, normalized);
    localStorage.setItem('sovereign_token', normalized);
    localStorage.setItem('token', normalized);
    if (user) {
      try {
        localStorage.setItem(USER_KEY, JSON.stringify(user));
      } catch (e) { }
      if (user.tenantId) {
        try {
          localStorage.setItem(TENANT_KEY, String(user.tenantId).trim());
          localStorage.setItem('tenant_id', String(user.tenantId).trim());
        } catch (e) { }
      }
      if (user.id || user._id) {
        localStorage.setItem('user_id', user.id || user._id);
      }
      if (user.role) {
        localStorage.setItem(ROLE_KEY, String(user.role).trim());
      }
      if (user.firstName) {
        localStorage.setItem(OPERATOR_KEY, String(user.firstName).toUpperCase());
      }
      if (user.email) {
        try {
          localStorage.setItem('loginEmail', String(user.email).trim().toLowerCase());
        } catch (e) { }
      }
    }
    const preview = safePreview(normalized);
    try {
      window.dispatchEvent(new CustomEvent('sovereign:token-saved', { detail: { preview } }));
    } catch (e) { }
    console.info('[SOVEREIGN] ✅ Token saved (preview):', preview);
  } catch (e) {
    console.warn('[SOVEREIGN] ⚠️ Failed to persist token/user', e);
  }
};

const clearAuthLocal = () => {
  try {
    [
      TOKEN_KEY,
      'sovereign_token',
      'token',
      TENANT_KEY,
      'tenant_id',
      USER_KEY,
      ROLE_KEY,
      OPERATOR_KEY,
      'user_id',
      'loginEmail',
    ].forEach((k) => localStorage.removeItem(k));
    try {
      window.dispatchEvent(new CustomEvent('sovereign:token-cleared'));
    } catch (e) { }
    console.info('[SOVEREIGN] 🧹 Auth state cleared');
  } catch (e) {
    console.warn('[SOVEREIGN] ⚠️ Failed to clear auth localStorage', e);
  }
};

export const authService = {
  login: async (email, password) => {
    const tenantId = getTenantContext();
    const normalizedEmail = String(email || '')
      .trim()
      .toLowerCase();
    // Persist email BEFORE login response so MFA step always has it
    try {
      localStorage.setItem('loginEmail', normalizedEmail);
    } catch (e) { }

    // FORENSIC LOGGING TO PROVE CONTEXT TO GATEWAY
    console.info(`[SOVEREIGN] 🔍 Handshake: Resolving dynamic context for [${tenantId}]`);
    if (!tenantId) throw new Error('Discover your organization before signing in.');
    const response = await api.post(
      '/api/auth/login',
      { email: normalizedEmail, password, tenant_id: tenantId }
    );
    const data = response?.data || {};
    if (data.token) writeTokenAndUser(data.token, data.user || null);
    // Ensure email survives MFA_SETUP / MFA_REQUIRED (no token yet)
    if (data.email) {
      try {
        localStorage.setItem('loginEmail', String(data.email).trim().toLowerCase());
      } catch (e) { }
    }
    return data;
  },

  logout: async () => {
    try {
      const tenantId = getTenantContext();
      await api.post('/api/auth/logout');
    } catch (e) {
      console.warn('[SOVEREIGN] logout request failed', e);
    } finally {
      clearAuthLocal();
    }
  },

  getProfile: async () => {
    const response = await api.get('/api/auth/workspace-bootstrap');
    return response.data;
  },

  /**
   * Verify TOTP after MFA_REQUIRED / MFA_SETUP.
   * Server contract (authController.verify3FA): { email, otp }
   * Also sends `code` alias for any legacy handlers.
   */
  verifyMFA: async (code) => {
    let email = localStorage.getItem('loginEmail');
    if (!email) {
      const userData = localStorage.getItem(USER_KEY);
      if (userData) {
        try {
          email = JSON.parse(userData).email;
        } catch (e) { }
      }
    }
    email = String(email || '')
      .trim()
      .toLowerCase();
    const otp = String(code ?? '')
      .trim()
      .replace(/\s/g, '');

    if (!email) {
      throw new Error('Missing login email for MFA. Please sign in again.');
    }
    if (!otp || otp.length < 6) {
      throw new Error('Enter the 6-digit authenticator code.');
    }

    const tenantId = getTenantContext();
    if (!tenantId) throw new Error('Discover your organization before verifying identity.');
    const response = await api.post(
      '/api/auth/verify-3fa',
      {
        email,
        otp, // ← server expects this (was `code` only → 400)
        code: otp, // alias for any dual-field handlers
        tenant_id: tenantId,
      }
    );
    const data = response?.data || {};
    if (data.token) writeTokenAndUser(data.token, data.user || null);
    return data;
  },

  refreshToken: async () => {
    try {
      const tenantId = getTenantContext();
      if (!tenantId) return null;
      const response = await api.post(
        '/api/auth/refresh',
        { tenant_id: tenantId }
      );
      const data = response?.data || {};
      if (data?.token) {
        writeTokenAndUser(data.token, data.user || null);
        return String(data.token).trim().replace(/^Bearer\s+/i, '');
      }
      return null;
    } catch (err) {
      console.warn('[SOVEREIGN] ⚠️ Token refresh failed', err?.message || err);
      return null;
    }
  },

  getStoredToken: () => {
    try {
      const raw = localStorage.getItem(TOKEN_KEY);
      return raw ? String(raw).trim().replace(/^Bearer\s+/i, '') : null;
    } catch {
      return null;
    }
  },

  getStoredUser: () => {
    try {
      const raw = localStorage.getItem(USER_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  },

  getStoredTenant: () => getTenantContext(),
  getStoredRole: () => localStorage.getItem(ROLE_KEY),
  isAuthenticated: () => !!authService.getStoredToken(),
  clearLocalAuth: () => clearAuthLocal(),
  setLoginEmail: (email) =>
    localStorage.setItem('loginEmail', String(email || '').trim().toLowerCase()),
};

// Expose hooks for Window Engine
try {
  if (typeof window !== 'undefined') {
    window.__SOVEREIGN_AUTH__ = {
      refreshToken: authService.refreshToken,
      getStoredToken: authService.getStoredToken,
      getStoredUser: authService.getStoredUser,
      isAuthenticated: authService.isAuthenticated,
    };
    console.info('[SOVEREIGN] 🔑 Auth service registered.');
  }
} catch (e) { }

export default authService;
