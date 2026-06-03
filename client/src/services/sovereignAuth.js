/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║                         THE SOVEREIGN OPERATING SYSTEM FOR GLOBAL BUSINESS                                                         ║
 * ║                              UNIFIED AUTH SERVICE - BRIDGE LAYER                                                                   ║
 * ║                              v2.0.0 - TOKEN NORMALIZATION                                                                          ║
 * ║                                   NO COMPETITION. NO COMPROMISE. THE FUTURE, NOW.                                                  ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/services/sovereignAuth.js
 * VERSION: 2.0.0-UNIFIED
 * CREATED: 2026-04-02
 *
 * 🔐 PURPOSE: Bridge between superadmin auth and sales dashboard auth
 *
 * This service normalizes token storage across different auth systems:
 * - Reads from superadmin's 'sovereignToken' key
 * - Also writes to 'sovereign_token' for compatibility
 * - Provides unified methods for all services
 *
 * @team_collaboration:
 * • Wilson Khanyezi - Unified auth bridge
 * • Security Team - Token normalization
 */

import authService from './superadmin/auth.service.js';

// Legacy token keys for backward compatibility
const LEGACY_TOKEN_KEY = 'sovereign_token';
const LEGACY_USER_ID_KEY = 'user_id';
const LEGACY_TENANT_ID_KEY = 'tenant_id';

// Current token keys
const CURRENT_TOKEN_KEY = 'sovereignToken';
const CURRENT_USER_KEY = 'userData';
const CURRENT_TENANT_KEY = 'tenantId';

/**
 * Normalize token across all storage locations
 * Ensures both old and new services can find the token
 */
const normalizeToken = (token) => {
  if (!token) return null;

  // Clean the token (remove Bearer prefix if present)
  const cleanToken = String(token).trim().replace(/^Bearer\s+/i, '');

  // Store in ALL possible locations for compatibility
  localStorage.setItem(CURRENT_TOKEN_KEY, cleanToken);
  localStorage.setItem(LEGACY_TOKEN_KEY, cleanToken);

  return cleanToken;
};

/**
 * Get token from any storage location
 */
const getTokenFromAnyLocation = () => {
  // Try current location first
  let token = localStorage.getItem(CURRENT_TOKEN_KEY);
  if (token) return token;

  // Try legacy location
  token = localStorage.getItem(LEGACY_TOKEN_KEY);
  if (token) return token;

  // Try from superadmin auth service
  token = authService.getStoredToken();
  if (token) return token;

  return null;
};

/**
 * Unified Auth Service for the entire WILSY OS
 */
export const sovereignAuth = {
  /**
   * Get current authentication token from ANY storage location
   */
  getToken: () => {
    return getTokenFromAnyLocation();
  },

  /**
   * Get current user ID
   */
  getUserId: () => {
    // Try legacy location first
    let userId = localStorage.getItem(LEGACY_USER_ID_KEY);
    if (userId) return userId;

    // Try from user data
    const userData = localStorage.getItem(CURRENT_USER_KEY);
    if (userData) {
      try {
        const parsed = JSON.parse(userData);
        return parsed.id || parsed.userId || null;
      } catch (e) {}
    }

    // Try from superadmin
    const storedUser = authService.getStoredUser();
    if (storedUser) {
      return storedUser.id || storedUser.userId || null;
    }

    return null;
  },

  /**
   * Get current tenant ID
   */
  getTenantId: () => {
    // Try legacy location
    let tenantId = localStorage.getItem(LEGACY_TENANT_ID_KEY);
    if (tenantId) return tenantId;

    // Try current location
    tenantId = localStorage.getItem(CURRENT_TENANT_KEY);
    if (tenantId) return tenantId;

    // Try from user data
    const userData = localStorage.getItem(CURRENT_USER_KEY);
    if (userData) {
      try {
        const parsed = JSON.parse(userData);
        return parsed.tenantId || null;
      } catch (e) {}
    }

    // Try from superadmin
    const storedTenant = authService.getStoredTenant();
    if (storedTenant) return storedTenant;

    // Default tenant for development
    return '69cb49e30276ea90ea1a0961';
  },

  /**
   * Set unified auth data (called after successful login/3FA)
   */
  setAuthData: (token, userData) => {
    if (token) {
      normalizeToken(token);
    }

    if (userData) {
      localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(userData));
      if (userData.id) localStorage.setItem(LEGACY_USER_ID_KEY, userData.id);
      if (userData.userId) localStorage.setItem(LEGACY_USER_ID_KEY, userData.userId);
      if (userData.tenantId) {
        localStorage.setItem(CURRENT_TENANT_KEY, userData.tenantId);
        localStorage.setItem(LEGACY_TENANT_ID_KEY, userData.tenantId);
      }
    }

    console.log('[SOVEREIGN_AUTH] ✅ Auth data normalized across all storage');
  },

  /**
   * Clear all auth data
   */
  clearAuth: () => {
    localStorage.removeItem(CURRENT_TOKEN_KEY);
    localStorage.removeItem(LEGACY_TOKEN_KEY);
    localStorage.removeItem(CURRENT_USER_KEY);
    localStorage.removeItem(LEGACY_USER_ID_KEY);
    localStorage.removeItem(CURRENT_TENANT_KEY);
    localStorage.removeItem(LEGACY_TENANT_ID_KEY);
    authService.clearLocalAuth();
    console.log('[SOVEREIGN_AUTH] 🧹 All auth data cleared');
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated: () => {
    return !!sovereignAuth.getToken();
  },

  /**
   * Login using superadmin auth service
   */
  login: async (email, password) => {
    const result = await authService.login(email, password);

    if (result && result.token) {
      sovereignAuth.setAuthData(result.token, result.user);
    }

    return result;
  },

  /**
   * Verify MFA and complete authentication
   */
  verifyMFA: async (code) => {
    const result = await authService.verifyMFA(code);

    if (result && result.token) {
      sovereignAuth.setAuthData(result.token, result.user);
    }

    return result;
  },

  /**
   * Logout
   */
  logout: async () => {
    await authService.logout();
    sovereignAuth.clearAuth();
  }
};

// Expose to window for debugging
if (typeof window !== 'undefined') {
  window.__SOVEREIGN_AUTH__ = sovereignAuth;
  console.log('[SOVEREIGN_AUTH] 🔑 Unified auth service registered on window.__SOVEREIGN_AUTH__');
}

export default sovereignAuth;
