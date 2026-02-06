/**
 * File: server/services/idpService.js
 * Path: server/services/idpService.js
 * STATUS: PRODUCTION-READY | IDP INTEGRATION | ROLE RESYNC
 * VERSION: 1.0.0
 *
 * PURPOSE
 * - Fetch and normalize identity claims from configured Identity Providers (OIDC/OAuth2/custom).
 * - Provide deterministic output for role resync and token introspection used by auth/admin controllers.
 *
 * COLLABORATION & OWNERSHIP
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - PRIMARY OWNER: @backend-team (implement provider mappings, maintain)
 * - SECURITY OWNER: @security (validate claim keys, secrets, redaction policy)
 * - SRE OWNER: @sre (tune retries, timeouts, caching)
 * - QA OWNER: @qa (unit + integration tests)
 *
 * REVIEW CHECKLIST (must be completed before merge)
 * - @backend-team: confirm model path ../models/userModel exists and idpSub field is present
 * - @security: ensure IDP_CLIENT_SECRET stored in secret manager (never in repo)
 * - @sre: confirm Redis available at app.locals.redis if caching desired
 * - @qa: add tests for normalizeRoleFromClaims with multiple IdP claim shapes
 *
 * DEPENDENCIES
 * - axios, async-retry (install via npm/yarn)
 *
 * ENVIRONMENT VARIABLES (examples)
 * - IDP_TYPE=oidc
 * - USERINFO_URL=https://idp.example.com/oauth2/userinfo
 * - INTROSPECT_URL=https://idp.example.com/oauth2/introspect
 * - IDP_CLIENT_ID=...
 * - IDP_CLIENT_SECRET=...
 * - IDP_ROLE_CLAIM_KEYS=role,roles,groups,http://schemas.microsoft.com/ws/2008/06/identity/claims/role
 *
 * SECURITY NOTES
 * - Do not log raw claims containing PII. Use redaction in audit entries.
 * - Use secret manager for IDP_CLIENT_SECRET and rotate regularly.
 */

'use strict';

const axios = require('axios').default;
const retry = require('async-retry');
const logger = (() => { try { return require('../utils/logger'); } catch (e) { return console; } })();
const User = (() => { try { return require('../models/userModel'); } catch (e) { return null; } })();

// Configuration from environment
const IDP_TYPE = process.env.IDP_TYPE || 'oidc';
const USERINFO_URL = process.env.USERINFO_URL || '';
const INTROSPECT_URL = process.env.INTROSPECT_URL || '';
const IDP_CLIENT_ID = process.env.IDP_CLIENT_ID || '';
const IDP_CLIENT_SECRET = process.env.IDP_CLIENT_SECRET || '';
const ROLE_CLAIM_KEYS = (process.env.IDP_ROLE_CLAIM_KEYS || 'role,roles,groups').split(',').map(k => k.trim()).filter(Boolean);

/* -------------------------
   Helpers
   ------------------------- */

function safeLogTelemetry(payload = {}) {
    try {
        if (process.env.NODE_ENV !== 'production') {
            // eslint-disable-next-line no-console
            console.debug('[idpService]', payload);
        }
        // Non-blocking: integrate with telemetry client here if available
    } catch (e) { /* swallow */ }
}

/**
 * normalizeRoleFromClaims
 * - Scans configured claim keys and common namespaced claims to return a canonical uppercase role string.
 */
function normalizeRoleFromClaims(claims) {
    if (!claims || typeof claims !== 'object') return null;

    // 1) Check configured claim keys in order
    for (const key of ROLE_CLAIM_KEYS) {
        const val = claims[key];
        if (!val) continue;
        if (Array.isArray(val) && val.length) return String(val[0]).trim().toUpperCase();
        if (typeof val === 'string' && val.trim()) return String(val).trim().toUpperCase();
        if (typeof val === 'object' && val.name) return String(val.name).trim().toUpperCase();
    }

    // 2) Fallback: scan keys for 'role' or 'group' substrings
    for (const k of Object.keys(claims)) {
        const lower = k.toLowerCase();
        if (lower.includes('role') || lower.includes('group') || lower.includes('roles')) {
            const v = claims[k];
            if (Array.isArray(v) && v.length) return String(v[0]).trim().toUpperCase();
            if (typeof v === 'string' && v.trim()) return String(v).trim().toUpperCase();
        }
    }

    return null;
}

/* HTTP GET with retry and jitter */
async function httpGetWithRetry(url, opts = {}) {
    const timeout = opts.timeout || 8000;
    const maxAttempts = opts.retries || 3;
    const headers = opts.headers || {};
    return retry(async (bail, attempt) => {
        try {
            const res = await axios.get(url, { headers, timeout });
            return res;
        } catch (err) {
            const status = err && err.response && err.response.status;
            // Do not retry on client errors except 429
            if (status && status >= 400 && status < 500 && status !== 429) return bail(err);
            safeLogTelemetry({ event: 'idp.http.error', url, attempt, status, message: err.message });
            throw err;
        }
    }, { retries: maxAttempts - 1, minTimeout: 200, maxTimeout: 2000 });
}

/* Token introspection POST with retry */
async function introspectToken(token, opts = {}) {
    if (!INTROSPECT_URL) throw new Error('INTROSPECT_URL not configured');
    const timeout = opts.timeout || 8000;
    const auth = IDP_CLIENT_ID && IDP_CLIENT_SECRET ? { username: IDP_CLIENT_ID, password: IDP_CLIENT_SECRET } : null;
    return retry(async (bail) => {
        try {
            const res = await axios.post(INTROSPECT_URL, new URLSearchParams({ token }).toString(), {
                auth,
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                timeout
            });
            return res;
        } catch (err) {
            const status = err && err.response && err.response.status;
            if (status && status >= 400 && status < 500 && status !== 429) return bail(err);
            throw err;
        }
    }, { retries: opts.retries || 2 });
}

/* -------------------------
   Public API
   ------------------------- */

/**
 * fetchClaimsForUser
 * - Accepts either a userId (internal) or an object { idpSub, userId }.
 * - options: { req, token, email, customFetchUrl, correlationId }
 * - Returns: { ok: boolean, claims, normalizedRole, source, raw, error? }
 *
 * Notes:
 * - Uses short Redis cache if available at req.app.locals.redis (non-blocking).
 * - Designed to be tolerant of different IdP shapes.
 */
async function fetchClaimsForUser(userIdOrOptions = {}, options = {}) {
    let userId = null;
    let idpSub = null;

    if (typeof userIdOrOptions === 'string' || typeof userIdOrOptions === 'number') {
        userId = String(userIdOrOptions);
    } else if (typeof userIdOrOptions === 'object' && userIdOrOptions !== null) {
        idpSub = userIdOrOptions.idpSub || null;
        userId = userIdOrOptions.userId || null;
    }

    const req = options.req || null;
    const correlationId = req?.context?.correlationId || options.correlationId || `idp_${Date.now()}`;

    try {
        // If userId provided, try to load user to get idpSub
        if (userId && User) {
            const userDoc = await User.findById(userId).lean().catch(() => null);
            if (userDoc) idpSub = idpSub || userDoc.idpSub || userDoc.sub || null;
        }

        // If email provided and no idpSub, try lookup
        if (!idpSub && options.email && User) {
            const byEmail = await User.findOne({ email: String(options.email).toLowerCase() }).lean().catch(() => null);
            if (byEmail) idpSub = byEmail.idpSub || byEmail.sub || null;
        }

        // Try short cache (non-blocking)
        try {
            const redis = req?.app?.locals?.redis;
            if (redis && idpSub) {
                const cached = await redis.get(`idp:claims:${idpSub}`);
                if (cached) {
                    const parsed = JSON.parse(cached);
                    safeLogTelemetry({ event: 'idp.cache.hit', idpSub, correlationId });
                    return { ok: true, claims: parsed, normalizedRole: normalizeRoleFromClaims(parsed), source: 'cache', raw: parsed };
                }
            }
        } catch (e) {
            safeLogTelemetry({ event: 'idp.cache.error', message: e.message, correlationId });
        }

        // Strategy: prefer USERINFO (if configured), then introspect token, then custom fetch
        let claims = null;
        let source = null;

        if (USERINFO_URL && idpSub) {
            try {
                const url = `${USERINFO_URL}${USERINFO_URL.includes('?') ? '&' : '?'}sub=${encodeURIComponent(idpSub)}`;
                const res = await httpGetWithRetry(url, { timeout: 8000, retries: 3 });
                claims = res.data;
                source = 'userinfo';
            } catch (err) {
                safeLogTelemetry({ event: 'idp.userinfo.failed', idpSub, message: err.message, correlationId });
            }
        }

        if (!claims && options.token && INTROSPECT_URL) {
            try {
                const res = await introspectToken(options.token, { retries: 2 });
                claims = res.data;
                source = 'introspect';
            } catch (err) {
                safeLogTelemetry({ event: 'idp.introspect.failed', message: err.message, correlationId });
            }
        }

        if (!claims && IDP_TYPE === 'custom' && options.customFetchUrl) {
            try {
                const res = await httpGetWithRetry(options.customFetchUrl, { timeout: 8000, retries: 2 });
                claims = res.data;
                source = 'custom';
            } catch (err) {
                safeLogTelemetry({ event: 'idp.custom.failed', message: err.message, correlationId });
            }
        }

        if (!claims) {
            safeLogTelemetry({ event: 'idp.noClaims', idpSub, userId, correlationId });
            return { ok: false, error: 'No claims found', idpSub, userId };
        }

        const normalizedRole = normalizeRoleFromClaims(claims);

        // Cache short-lived if redis available
        try {
            const redis = req?.app?.locals?.redis;
            if (redis && idpSub) {
                await redis.set(`idp:claims:${idpSub}`, JSON.stringify(claims), 'EX', 60);
            }
        } catch (e) {
            safeLogTelemetry({ event: 'idp.cache.set.failed', message: e.message, correlationId });
        }

        safeLogTelemetry({ event: 'idp.fetch.success', source, idpSub, userId, normalizedRole, correlationId });

        return { ok: true, claims, normalizedRole, source, raw: claims };
    } catch (err) {
        logger.error && logger.error('idpService.fetchClaimsForUser error', err && (err.stack || err));
        safeLogTelemetry({ event: 'idp.fetch.error', message: err.message, correlationId });
        return { ok: false, error: err.message };
    }
}

/**
 * introspectToken (public)
 * - Lightweight wrapper to expose token introspection result.
 */
async function introspectTokenPublic(token) {
    try {
        const res = await introspectToken(token, { retries: 2 });
        return { ok: true, data: res.data };
    } catch (err) {
        safeLogTelemetry({ event: 'idp.introspect.public.error', message: err.message });
        return { ok: false, error: err.message };
    }
}

module.exports = {
    fetchClaimsForUser,
    introspectToken: introspectTokenPublic,
    normalizeRoleFromClaims
};
