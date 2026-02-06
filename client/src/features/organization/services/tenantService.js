/**
 * File: client/src/features/organization/services/tenantService.js
 * STATUS: PRODUCTION-READY | TENANT API BRIDGE
 *
 * NOTE: ESLint rule requires assigning the default export to a variable
 * before exporting. We collect the functions into `tenantService` and
 * export it as the default at the end.
 */

import { fetchJson as baseFetchJson } from '../../../utils/fetch';

// FIX: Use import.meta.env for Vite compatibility (replaces process.env)
const DEFAULT_TIMEOUT_MS = parseInt(import.meta.env.VITE_API_TIMEOUT_MS || '15000', 10);
const DEFAULT_RETRIES = parseInt(import.meta.env.VITE_API_RETRIES || '1', 10);

const getHeaders = (token) => {
    const headers = {
        'Content-Type': 'application/json',
        Accept: 'application/json'
    };
    if (token) headers.Authorization = `Bearer ${token}`;
    return headers;
};

async function safeFetchJson(url, opts = {}) {
    const { timeoutMs = DEFAULT_TIMEOUT_MS, retries = DEFAULT_RETRIES, body, headers = {}, ...rest } = opts;
    const method = (rest.method || 'GET').toUpperCase();
    const payload = (body && method !== 'GET') ? JSON.stringify(body) : undefined;
    const mergedHeaders = Object.assign({}, headers);

    let attempt = 0;
    let lastErr = null;

    while (attempt <= retries) {
        attempt += 1;
        try {
            if (typeof baseFetchJson === 'function') {
                const response = await baseFetchJson(url, {
                    ...rest,
                    method,
                    headers: mergedHeaders,
                    body: payload,
                    timeoutMs
                });
                return response;
            }

            const controller = new AbortController();
            const id = setTimeout(() => controller.abort(), timeoutMs);

            const res = await fetch(url, {
                method,
                headers: mergedHeaders,
                body: payload,
                signal: controller.signal
            });

            clearTimeout(id);

            const contentType = res.headers.get('content-type') || '';
            let parsed = null;
            if (contentType.includes('application/json')) {
                parsed = await res.json();
            } else {
                parsed = await res.text();
            }

            if (!res.ok) {
                const message = parsed && parsed.message ? parsed.message : res.statusText || 'Request failed';
                return { ok: false, status: res.status, message, details: parsed };
            }

            return { ok: true, status: res.status, data: parsed };
        } catch (err) {
            lastErr = err;
            if (attempt > retries) break;
            await new Promise((r) => setTimeout(r, 200 * attempt));
        }
    }

    return {
        ok: false,
        status: 0,
        message: lastErr && lastErr.message ? lastErr.message : 'Network request failed',
        details: lastErr
    };
}

/* -------------------------
   Tenant API functions
   ------------------------- */

export const getTenantDashboard = async (token) => {
    const headers = getHeaders(token);
    return safeFetchJson('/api/tenant/dashboard', { method: 'GET', headers });
};

export const getTenantSettings = async (token) => {
    const headers = getHeaders(token);
    return safeFetchJson('/api/tenant/settings', { method: 'GET', headers });
};

export const updateTenantSettings = async (token, data) => {
    const headers = getHeaders(token);
    return safeFetchJson('/api/tenant/settings', { method: 'PUT', headers, body: data });
};

export const getTeamMembers = async (token) => {
    const headers = getHeaders(token);
    return safeFetchJson('/api/tenant/users', { method: 'GET', headers });
};

export const inviteTeamMember = async (token, userData) => {
    const headers = getHeaders(token);
    return safeFetchJson('/api/tenant/users', { method: 'POST', headers, body: userData });
};

export const updateUserStatus = async (token, userId, isActive) => {
    const headers = getHeaders(token);
    return safeFetchJson(`/api/tenant/users/${encodeURIComponent(userId)}/status`, {
        method: 'PUT',
        headers,
        body: { isActive }
    });
};

/* -------------------------
   Default export (assigned to variable to satisfy linters)
   ------------------------- */

const tenantService = {
    getTenantDashboard,
    getTenantSettings,
    updateTenantSettings,
    getTeamMembers,
    inviteTeamMember,
    updateUserStatus
};

export default tenantService;
