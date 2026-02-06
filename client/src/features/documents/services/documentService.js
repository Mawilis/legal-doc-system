/**
 * File: client/src/features/documents/services/documentService.js
 * PATH: client/src/features/documents/services/documentService.js
 * STATUS: PRODUCTION-READY | API BRIDGE | EPITOME
 * VERSION: 1.1.1
 * -----------------------------------------------------------------------------
 * PURPOSE
 * - Client-side API bridge for Document lifecycle: list, create, fetch, generate.
 * - Resilient network behavior (timeouts, retries), consistent error shapes,
 *   defensive validation, and clear collaboration notes for future engineers.
 *
 * GUIDING PRINCIPLES
 * - Small, deterministic functions that are easy to unit test and mock.
 * - Stable response contract: { ok, status, data?, message?, details? }.
 * - Prefer app-level fetchJson when available (token injection, telemetry).
 * - Fail-safe defaults and conservative retry/backoff for idempotent requests.
 *
 * COLLABORATION & OWNERSHIP
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - PRIMARY OWNER: @frontend (service maintenance)
 * - BACKEND: @backend-team (API contract & schema)
 * - SECURITY: @security (auth, token handling, XSS)
 * - QA: @qa (unit & integration tests)
 * - SRE: @sre (timeouts, retries, observability)
 *
 * REVIEW & DEPLOYMENT GATES
 * - Any change to endpoints, request/response shapes, or retry/timeouts must:
 *   1) Update unit/integration tests
 *   2) Be reviewed by @backend-team and @security
 *   3) Include a CHANGELOG entry if behavior changes
 *
 * TESTING
 * - Unit tests: tests/features/documents/documentService.unit.test.js
 * - Integration tests: tests/integration/documents.*.test.js (staging)
 *
 * USAGE
 * - import documentService, { getDocuments } from 'client/src/features/documents/services/documentService';
 * -----------------------------------------------------------------------------
 */

import { fetchJson as baseFetchJson } from '../../../utils/fetch';
import AuthStore from '../../../store/authStore';

/* -------------------------
   Configuration (Vite-friendly)
   ------------------------- */
const DEFAULT_TIMEOUT_MS = Number.parseInt(import.meta.env.VITE_API_TIMEOUT_MS || '15000', 10);
const DEFAULT_RETRIES = Math.max(0, Number.parseInt(import.meta.env.VITE_API_RETRIES || '1', 10));
const SAFETY_MAX_RETRIES = 3; // absolute safety cap
const BACKOFF_BASE_MS = 120;

/* -------------------------
   Response contract
   - All functions return this shape for predictable handling:
   * { ok: boolean, status: number, data?: any, message?: string, details?: any }
   ------------------------- */

/* -------------------------
   Helpers
   ------------------------- */

function _getTokenFromStore() {
    try {
        if (AuthStore && typeof AuthStore.getState === 'function') {
            const s = AuthStore.getState();
            return s && s.token ? String(s.token) : null;
        }
    } catch (e) {
        // swallow; fallback to null
    }
    return null;
}

const getHeaders = (token, extra = {}) => {
    const resolvedToken = token || _getTokenFromStore();
    const headers = {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        ...extra
    };
    if (resolvedToken) headers.Authorization = `Bearer ${resolvedToken}`;
    return headers;
};

function _sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

function _jitterBackoff(attempt) {
    // exponential with jitter, capped
    const exp = Math.min(2000, BACKOFF_BASE_MS * 2 ** Math.max(0, attempt - 1));
    return Math.floor(Math.random() * exp) + BACKOFF_BASE_MS;
}

/* -------------------------
   Core network wrapper
   ------------------------- */

async function safeFetch(url, opts = {}) {
    const {
        timeoutMs = DEFAULT_TIMEOUT_MS,
        retries = DEFAULT_RETRIES,
        method = 'GET',
        headers = {},
        body,
        signal: callerSignal,
        ...rest
    } = opts;

    const methodUpper = String(method || 'GET').toUpperCase();
    const isIdempotent = methodUpper === 'GET' || methodUpper === 'HEAD';

    // Cap retries to safety limit
    const effectiveRetries = Math.min(Math.max(0, Number.parseInt(retries, 10) || 0), SAFETY_MAX_RETRIES);
    const maxAttempts = isIdempotent ? Math.max(1, effectiveRetries + 1) : 1;

    const payload = body !== undefined ? body : undefined;

    let attempt = 0;
    let lastErr = null;

    while (attempt < maxAttempts) {
        attempt += 1;

        // Prefer app-level baseFetchJson if available
        if (typeof baseFetchJson === 'function') {
            try {
                const res = await baseFetchJson(url, {
                    method: methodUpper,
                    headers,
                    body: payload,
                    timeoutMs,
                    signal: callerSignal,
                    ...rest
                });

                // If baseFetchJson returns normalized shape, pass through
                if (res && typeof res === 'object' && ('ok' in res || 'status' in res)) {
                    if (typeof res.ok === 'boolean') return res;
                    return { ok: true, status: res.status || 200, data: res };
                }

                return { ok: true, status: 200, data: res };
            } catch (err) {
                lastErr = err;
                if (attempt >= maxAttempts) break;
                await _sleep(_jitterBackoff(attempt));
                continue;
            }
        }

        // Fallback to native fetch
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

            // If caller provided a signal, wire it to abort our controller
            if (callerSignal) {
                if (callerSignal.aborted) {
                    clearTimeout(timeoutId);
                    return { ok: false, status: 0, message: 'Request aborted by caller', details: null };
                }
                const onAbort = () => controller.abort();
                callerSignal.addEventListener('abort', onAbort, { once: true });
                // ensure we remove listener after fetch completes
                try {
                    const fetchOpts = {
                        method: methodUpper,
                        headers,
                        body: (() => {
                            // normalize header key lookup case-insensitively
                            const ctKey = Object.keys(headers).find(k => k.toLowerCase() === 'content-type');
                            const ct = ctKey ? headers[ctKey] : '';
                            if (payload !== undefined && methodUpper !== 'GET' && ct && ct.includes('application/json')) {
                                return JSON.stringify(payload);
                            }
                            return payload;
                        })(),
                        signal: controller.signal
                    };

                    const res = await fetch(url, fetchOpts);
                    clearTimeout(timeoutId);
                    callerSignal.removeEventListener('abort', onAbort);

                    const contentType = (res.headers.get('content-type') || '').toLowerCase();
                    let parsed = null;
                    if (contentType.includes('application/json')) {
                        parsed = await res.json().catch(() => null);
                    } else {
                        parsed = await res.text().catch(() => null);
                    }

                    if (!res.ok) {
                        const message = (parsed && (parsed.message || parsed.error)) || res.statusText || `Request failed (${res.status})`;
                        return { ok: false, status: res.status, message, details: parsed };
                    }

                    return { ok: true, status: res.status, data: parsed };
                } catch (err) {
                    clearTimeout(timeoutId);
                    callerSignal.removeEventListener('abort', onAbort);
                    lastErr = err;
                    if (err && err.name === 'AbortError') {
                        if (attempt >= maxAttempts) {
                            return { ok: false, status: 0, message: `Request timed out after ${timeoutMs}ms`, details: err };
                        }
                    }
                    if (attempt >= maxAttempts) break;
                    await _sleep(_jitterBackoff(attempt));
                }
            } else {
                // No caller signal
                try {
                    const fetchOpts = {
                        method: methodUpper,
                        headers,
                        body: (() => {
                            const ctKey = Object.keys(headers).find(k => k.toLowerCase() === 'content-type');
                            const ct = ctKey ? headers[ctKey] : '';
                            if (payload !== undefined && methodUpper !== 'GET' && ct && ct.includes('application/json')) {
                                return JSON.stringify(payload);
                            }
                            return payload;
                        })(),
                        signal: controller.signal
                    };

                    const res = await fetch(url, fetchOpts);
                    clearTimeout(timeoutId);

                    const contentType = (res.headers.get('content-type') || '').toLowerCase();
                    let parsed = null;
                    if (contentType.includes('application/json')) {
                        parsed = await res.json().catch(() => null);
                    } else {
                        parsed = await res.text().catch(() => null);
                    }

                    if (!res.ok) {
                        const message = (parsed && (parsed.message || parsed.error)) || res.statusText || `Request failed (${res.status})`;
                        return { ok: false, status: res.status, message, details: parsed };
                    }

                    return { ok: true, status: res.status, data: parsed };
                } catch (err) {
                    clearTimeout(timeoutId);
                    lastErr = err;
                    if (err && err.name === 'AbortError') {
                        if (attempt >= maxAttempts) {
                            return { ok: false, status: 0, message: `Request timed out after ${timeoutMs}ms`, details: err };
                        }
                    }
                    if (attempt >= maxAttempts) break;
                    await _sleep(_jitterBackoff(attempt));
                }
            }
        } catch (err) {
            lastErr = err;
            if (attempt >= maxAttempts) break;
            await _sleep(_jitterBackoff(attempt));
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
   Validation helpers
   ------------------------- */

function assertPayload(payload, required = []) {
    if (!payload || typeof payload !== 'object') {
        throw new TypeError('Payload must be a plain object');
    }
    for (const key of required) {
        if (payload[key] === undefined || payload[key] === null || payload[key] === '') {
            throw new Error(`Missing required field: ${key}`);
        }
    }
}

/* -------------------------
   Document API methods
   ------------------------- */

export async function getDocuments(token, filters = {}) {
    const query = new URLSearchParams(filters).toString();
    const url = `/api/documents${query ? `?${query}` : ''}`;
    return safeFetch(url, {
        method: 'GET',
        headers: getHeaders(token)
    });
}

export async function createDocument(token, payload) {
    try {
        assertPayload(payload, ['title', 'type', 'category']);
    } catch (err) {
        return { ok: false, status: 400, message: err.message };
    }

    return safeFetch('/api/documents', {
        method: 'POST',
        headers: getHeaders(token),
        body: payload
    });
}

export async function generateDocumentPdf(token, documentId) {
    if (!documentId) {
        return { ok: false, status: 400, message: 'documentId is required' };
    }

    return safeFetch(`/api/documents/${encodeURIComponent(String(documentId))}/generate`, {
        method: 'POST',
        headers: getHeaders(token)
    });
}

export async function getDocumentById(token, id) {
    if (!id) {
        return { ok: false, status: 400, message: 'id is required' };
    }

    return safeFetch(`/api/documents/${encodeURIComponent(String(id))}`, {
        method: 'GET',
        headers: getHeaders(token)
    });
}

/* -------------------------
   Export service object
   ------------------------- */

const documentService = {
    getDocuments,
    createDocument,
    generateDocumentPdf,
    getDocumentById
};

export default documentService;
