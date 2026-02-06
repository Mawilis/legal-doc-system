/**
 * File: client/src/store/authStore.js
 * Path: client/src/store/authStore.js
 * STATUS: PRODUCTION-READY | POPIA-COMPLIANT | ENTERPRISE
 * VERSION: 2026-01-17
 *
 * PURPOSE
 * - Global identity state using Zustand for Wilsy OS.
 * - Responsibilities: login, register, logout, token lifecycle, auto-logout,
 *   cross-tab sync, tenant switching, refresh user, consent & deletion requests,
 *   MFA hooks, legal-hold awareness, and safe persistence.
 *
 * COLLABORATION & OWNERSHIP (MANDATORY)
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - PRIMARY OWNER: @frontend-team (store maintenance, UI integration)
 * - BACKEND OWNER: @backend-team (API contract: /api/auth/*, /api/privacy/*, /api/tenants/*)
 * - SECURITY OWNER: @security (storage policy, redaction, MFA)
 * - SRE OWNER: @sre (availability, telemetry)
 * - QA OWNER: @qa (unit & integration tests)
 * - LEGAL OWNER: @legal (DSAR/export format and retention policy)
 * - DPO: @dpo (PII handling and compliance)
 *
 * REQUIRED REVIEWERS (PRE-MERGE)
 * - @backend-team: confirm server sets httpOnly Secure SameSite cookies and endpoints match spec.
 * - @security: approve localStorage usage and consent flows; review PII surface.
 * - @sre: validate telemetry hooks and rate limits for auth endpoints.
 * - @qa: add tests for token-less session flows, consent requests, legal-hold behavior, and cross-tab sync.
 *
 * MERGE GATE (must be satisfied before merging to main)
 * - Security approval (KMS/token handling)
 * - Legal approval (retention/DSAR)
 * - SRE approval (observability & rate limits)
 * - QA approval (unit & integration tests)
 *
 * DEPLOY NOTES
 * - Prefer httpOnly cookies for session; client may optionally use short-lived access tokens.
 * - Do not persist raw IdP claims or PII in localStorage.
 * - Ensure client-side code uses getAuthHeaders() for protected requests.
 */

'use strict';

import { create } from 'zustand';
import { fetchJson } from '../utils/fetch'; // must exist in your project

/* -------------------------
   Configuration
   ------------------------- */
const ACCESS_TOKEN_KEY = 'wilsy_access_token';
const USER_KEY = 'wilsy_user';
const AUTH_EVENT_KEY = 'wilsy_auth_event';
const CHANNEL_NAME = 'wilsy_auth_channel';
const DEFAULT_LEEWAY_MS = 5000;

/* -------------------------
   Safe storage helpers
   ------------------------- */
function safeLocalGet(key) {
    try {
        if (typeof window === 'undefined') return null;
        return localStorage.getItem(key);
    } catch {
        return null;
    }
}
function safeLocalSet(key, value) {
    try {
        if (typeof window === 'undefined') return;
        localStorage.setItem(key, value);
    } catch { /* swallow */ }
}
function safeLocalRemove(key) {
    try {
        if (typeof window === 'undefined') return;
        localStorage.removeItem(key);
    } catch { /* swallow */ }
}

/* -------------------------
   JWT helpers
   ------------------------- */
function parseJwt(token) {
    if (!token || typeof token !== 'string') return null;
    try {
        const parts = token.split('.');
        if (parts.length < 2) return null;
        const payload = parts[1];
        // base64url -> base64
        const base64 = payload.replace(/-/g, '+').replace(/_/g, '/');
        // pad base64 string
        const pad = base64.length % 4;
        const padded = pad ? base64 + '='.repeat(4 - pad) : base64;
        const json = atob(padded);
        return JSON.parse(json);
    } catch {
        return null;
    }
}

function tokenExpiresAt(token) {
    const payload = parseJwt(token);
    if (!payload || !payload.exp) return null;
    return payload.exp * 1000;
}
function isExpired(token, leewayMs = DEFAULT_LEEWAY_MS) {
    const exp = tokenExpiresAt(token);
    if (!exp) return true;
    return Date.now() + leewayMs >= exp;
}

/* -------------------------
   Sanitization (POPIA)
   ------------------------- */
function sanitizeUserForClient(user) {
    if (!user) return null;
    // Keep minimal fields client-side; PII remains server-side unless approved
    return {
        id: user.id || user._id || null,
        displayName: user.displayName || `${user.firstName || ''} ${user.lastName || ''}`.trim() || null,
        role: user.role || null,
        tenantId: user.tenantId || null,
        tenants: user.tenants || [],
        avatarUrl: user.avatarUrl || null,
        logoUrl: user.logoUrl || null
    };
}

/* -------------------------
   Cross-tab / Broadcast helpers
   ------------------------- */
function createBroadcast() {
    if (typeof window === 'undefined') return null;
    if ('BroadcastChannel' in window) {
        try { return new BroadcastChannel(CHANNEL_NAME); } catch { return null; }
    }
    return null;
}
function emitAuthEventLocal(event) {
    try {
        safeLocalSet(AUTH_EVENT_KEY, JSON.stringify(event));
    } catch { /* swallow */ }
}

/* -------------------------
   Auto-logout scheduler
   ------------------------- */
function scheduleAutoLogoutInternal(set, get, accessToken) {
    try {
        const expAt = tokenExpiresAt(accessToken);
        if (!expAt) return null;
        const timeout = Math.max(0, expAt - Date.now());
        const existing = get()._logoutTimer;
        if (existing) clearTimeout(existing);
        const t = setTimeout(() => { get().logout().catch(() => { }); }, timeout + 1000);
        set({ _logoutTimer: t });
        return t;
    } catch {
        return null;
    }
}

/* -------------------------
   Initialize store
   ------------------------- */
const useAuthStore = create((set, get) => {
    // load initial state
    const rawUser = safeLocalGet(USER_KEY);
    const initialUser = rawUser ? JSON.parse(rawUser) : null;
    const rawAccess = safeLocalGet(ACCESS_TOKEN_KEY);
    const isAuthenticated = !!initialUser;

    const bc = createBroadcast();
    // cross-tab listener
    if (bc) {
        bc.onmessage = (m) => {
            try {
                const ev = m.data;
                if (!ev || !ev.type) return;
                if (ev.type === 'logout') get().logout().catch(() => { });
                if (ev.type === 'login' || ev.type === 'register') {
                    const user = safeLocalGet(USER_KEY) ? JSON.parse(safeLocalGet(USER_KEY)) : null;
                    set({ user, isAuthenticated: !!user, tenants: (user && user.tenants) || [] });
                }
                if (ev.type === 'tenant_switch') get().refreshUser().catch(() => { });
            } catch { /* swallow */ }
        };
    } else if (typeof window !== 'undefined') {
        window.addEventListener('storage', (e) => {
            try {
                if (!e.key) return;
                if (e.key === AUTH_EVENT_KEY) {
                    const ev = e.newValue ? JSON.parse(e.newValue) : null;
                    if (!ev || !ev.type) return;
                    if (ev.type === 'logout') get().logout().catch(() => { });
                    if (ev.type === 'login' || ev.type === 'register') {
                        const user = safeLocalGet(USER_KEY) ? JSON.parse(safeLocalGet(USER_KEY)) : null;
                        set({ user, isAuthenticated: !!user, tenants: (user && user.tenants) || [] });
                    }
                    if (ev.type === 'tenant_switch') get().refreshUser().catch(() => { });
                }
            } catch { /* swallow */ }
        });
    }

    // schedule auto-logout if token present
    if (rawAccess && !isExpired(rawAccess)) {
        scheduleAutoLogoutInternal(set, get, rawAccess);
    }

    return {
        // state
        user: initialUser,
        isAuthenticated,
        isLoading: false,
        error: null,
        tenants: (initialUser && initialUser.tenants) || [],
        _logoutTimer: null,

        /* -------------------------
           Selectors / helpers
           ------------------------- */
        getAuthHeaders: () => {
            // Prefer cookie-based auth; include optional short-lived access token if present
            const token = safeLocalGet(ACCESS_TOKEN_KEY);
            const headers = { 'Content-Type': 'application/json', Accept: 'application/json' };
            if (token && !isExpired(token)) headers.Authorization = `Bearer ${token}`;
            return headers;
        },

        getTenantId: () => (get().user ? get().user.tenantId : null),

        isTenantAdmin: () => {
            const role = (get().user && get().user.role) || '';
            return role === 'TENANT_ADMIN' || role === 'SUPER_ADMIN';
        },

        /* -------------------------
           Actions
           ------------------------- */

        login: async ({ email, password, mfaCode = null }) => {
            set({ isLoading: true, error: null });
            try {
                const body = { email, password };
                if (mfaCode) body.mfaCode = mfaCode;
                // fetchJson should throw on non-2xx and return parsed JSON
                const data = await fetchJson('/api/auth/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body });
                if (!data || !data.user) throw new Error('Invalid auth response');

                const userSummary = sanitizeUserForClient(data.user);
                safeLocalSet(USER_KEY, JSON.stringify(userSummary));
                if (data.accessToken) safeLocalSet(ACCESS_TOKEN_KEY, data.accessToken);

                set({ user: userSummary, isAuthenticated: true, tenants: userSummary.tenants || [], isLoading: false, error: null });
                if (data.accessToken) scheduleAutoLogoutInternal(set, get, data.accessToken);

                // cross-tab + local event
                const event = { type: 'login', ts: Date.now(), userId: userSummary.id };
                try { if (bc) bc.postMessage(event); } catch { /* swallow */ }
                emitAuthEventLocal(event);
                // non-blocking audit hook
                try { if (window && window.WilsyAudit && typeof window.WilsyAudit.log === 'function') window.WilsyAudit.log('AUTH_EVENT', event); } catch { /* swallow */ }

                return userSummary;
            } catch (err) {
                set({ error: (err && err.message) || 'Login failed', isLoading: false, isAuthenticated: false });
                throw err;
            }
        },

        register: async (userData) => {
            set({ isLoading: true, error: null });
            try {
                const data = await fetchJson('/api/auth/register', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: userData });
                if (!data || !data.user) throw new Error('Invalid register response');

                const userSummary = sanitizeUserForClient(data.user);
                safeLocalSet(USER_KEY, JSON.stringify(userSummary));
                if (data.accessToken) safeLocalSet(ACCESS_TOKEN_KEY, data.accessToken);

                set({ user: userSummary, isAuthenticated: true, tenants: userSummary.tenants || [], isLoading: false, error: null });
                if (data.accessToken) scheduleAutoLogoutInternal(set, get, data.accessToken);

                const event = { type: 'register', ts: Date.now(), userId: userSummary.id };
                try { if (bc) bc.postMessage(event); } catch { /* swallow */ }
                emitAuthEventLocal(event);
                return userSummary;
            } catch (err) {
                set({ error: (err && err.message) || 'Registration failed', isLoading: false });
                throw err;
            }
        },

        logout: async () => {
            set({ isLoading: true, error: null });
            try {
                // best-effort server logout; ignore errors
                try { await fetchJson('/api/auth/logout', { method: 'POST', headers: get().getAuthHeaders() }); } catch { /* swallow */ }

                safeLocalRemove(USER_KEY);
                safeLocalRemove(ACCESS_TOKEN_KEY);
                set({ user: null, isAuthenticated: false, tenants: [], isLoading: false, error: null });

                const event = { type: 'logout', ts: Date.now() };
                try { if (bc) bc.postMessage(event); } catch { /* swallow */ }
                emitAuthEventLocal(event);
            } catch (err) {
                set({ error: (err && err.message) || 'Logout failed', isLoading: false });
                throw err;
            }
        },

        refreshUser: async () => {
            set({ isLoading: true, error: null });
            try {
                const data = await fetchJson('/api/auth/me', { method: 'GET', headers: get().getAuthHeaders() });
                if (!data || !data.user) throw new Error('Failed to refresh user');
                const userSummary = sanitizeUserForClient(data.user);
                safeLocalSet(USER_KEY, JSON.stringify(userSummary));
                set({ user: userSummary, tenants: userSummary.tenants || [], isAuthenticated: true, isLoading: false });
                return userSummary;
            } catch (err) {
                safeLocalRemove(USER_KEY);
                set({ user: null, isAuthenticated: false, isLoading: false, error: (err && err.message) || 'Failed to refresh user' });
                return null;
            }
        },

        switchTenant: async (tenantId) => {
            if (!tenantId) throw new Error('tenantId is required');
            set({ isLoading: true, error: null });
            try {
                // Try server switch-tenant endpoint
                try {
                    const resp = await fetchJson('/api/auth/switch-tenant', { method: 'POST', headers: get().getAuthHeaders(), body: { tenantId } });
                    if (resp && resp.user) {
                        const userSummary = sanitizeUserForClient(resp.user);
                        safeLocalSet(USER_KEY, JSON.stringify(userSummary));
                        if (resp.accessToken) safeLocalSet(ACCESS_TOKEN_KEY, resp.accessToken);
                        set({ user: userSummary, tenants: userSummary.tenants || [], isLoading: false });
                        if (resp.accessToken) scheduleAutoLogoutInternal(set, get, resp.accessToken);
                        const event = { type: 'tenant_switch', ts: Date.now(), tenantId };
                        try { if (bc) bc.postMessage(event); } catch { /* swallow */ }
                        emitAuthEventLocal(event);
                        return userSummary.tenantId || tenantId;
                    }
                } catch { /* fallback below */ }

                // Fallback: call tenant activation then refresh user
                try { await fetchJson(`/api/tenants/${encodeURIComponent(tenantId)}/activate`, { method: 'POST', headers: get().getAuthHeaders() }); } catch { /* swallow */ }
                const refreshed = await get().refreshUser();
                if (refreshed) {
                    safeLocalSet('tenantId', tenantId);
                    set({ isLoading: false });
                    const event = { type: 'tenant_switch', ts: Date.now(), tenantId };
                    try { if (bc) bc.postMessage(event); } catch { /* swallow */ }
                    emitAuthEventLocal(event);
                    return tenantId;
                }
                throw new Error('Tenant switch failed');
            } catch (err) {
                set({ error: (err && err.message) || 'Tenant switch failed', isLoading: false });
                throw err;
            }
        },

        requestDataAccess: async () => {
            set({ isLoading: true, error: null });
            try {
                const data = await fetchJson('/api/privacy/access-request', { method: 'POST', headers: get().getAuthHeaders() });
                set({ isLoading: false });
                return data;
            } catch (err) {
                set({ error: (err && err.message) || 'Request failed', isLoading: false });
                throw err;
            }
        },

        requestDeletion: async () => {
            set({ isLoading: true, error: null });
            try {
                const data = await fetchJson('/api/privacy/deletion-request', { method: 'POST', headers: get().getAuthHeaders() });
                set({ isLoading: false });
                return data;
            } catch (err) {
                set({ error: (err && err.message) || 'Deletion request failed', isLoading: false });
                throw err;
            }
        },

        mfaStatus: async () => {
            try {
                const data = await fetchJson('/api/auth/mfa/status', { method: 'GET', headers: get().getAuthHeaders() });
                return data;
            } catch {
                return { enrolled: false };
            }
        },

        requireMfa: async () => {
            try {
                const data = await fetchJson('/api/auth/mfa/require', { method: 'POST', headers: get().getAuthHeaders() });
                return data;
            } catch (err) {
                throw err;
            }
        },

        isUnderLegalHold: async () => {
            try {
                const data = await fetchJson('/api/privacy/legal-hold-status', { method: 'GET', headers: get().getAuthHeaders() });
                return !!(data && data.legalHold === true);
            } catch {
                return false;
            }
        }
    };
});

/* Export */
export default useAuthStore;
