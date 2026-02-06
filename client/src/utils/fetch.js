/**
 * client/src/utils/fetch.js
 * Production-ready, secure, and pluggable HTTP client for browser apps.
 *
 * Author: Wilson Khanyezi
 * Version: 1.0.3
 *
 * Collaboration notes:
 * - Token provider is pluggable at app bootstrap (main.jsx).
 * - Default uses localStorage for access token and cookie-based refresh.
 * - Backend contract: POST /api/auth/refresh returns { accessToken } on success.
 */

const DEFAULT_BASE_URL = (import.meta && import.meta.env && import.meta.env.VITE_API_URL) || 'http://localhost:3001';
const DEFAULT_ACCESS_TOKEN_KEY = 'wilsy_access_token';

class ApiError extends Error {
    constructor(message, { status = null, body = null, headers = null } = {}) {
        super(message);
        this.name = 'ApiError';
        this.status = status;
        this.body = body;
        this.headers = headers;
    }
}
class NetworkError extends Error { constructor(message) { super(message); this.name = 'NetworkError'; } }
class TimeoutError extends Error { constructor(message) { super(message); this.name = 'TimeoutError'; } }
class UnauthorizedError extends ApiError { constructor(message = 'Unauthorized', opts = {}) { super(message, opts); this.name = 'UnauthorizedError'; } }

function ensureLeadingSlash(path) {
    if (!path) return '/';
    return path.startsWith('/') ? path : `/${path}`;
}
function buildUrl(base, endpoint, query) {
    const baseUrl = base.endsWith('/') ? base.slice(0, -1) : base;
    const path = ensureLeadingSlash(endpoint);
    const url = new URL(path, baseUrl);
    if (query && typeof query === 'object') {
        Object.keys(query).forEach((k) => {
            const v = query[k];
            if (v === undefined || v === null) return;
            if (Array.isArray(v)) {
                v.forEach((item) => url.searchParams.append(k, String(item)));
            } else {
                url.searchParams.set(k, String(v));
            }
        });
    }
    return url.toString();
}
function sleep(ms) { return new Promise((resolve) => setTimeout(resolve, ms)); }
function jitterBackoff(attempt, base = 100, cap = 2000) {
    const exp = Math.min(cap, base * 2 ** attempt);
    return Math.floor(Math.random() * exp);
}

/* Safe localStorage helpers */
function safeLocalGet(key) {
    try {
        if (typeof window === 'undefined') return null;
        return localStorage.getItem(key);
    } catch { return null; }
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

/* Default token provider (pluggable) */
const defaultTokenProvider = {
    async getToken() {
        return safeLocalGet(DEFAULT_ACCESS_TOKEN_KEY);
    },
    async onUnauthorized(res) {
        // Attempt cookie-based refresh once
        try {
            const refreshRes = await fetch(`${DEFAULT_BASE_URL}/api/auth/refresh`, {
                method: 'POST',
                headers: { Accept: 'application/json' },
                credentials: 'include'
            });
            if (!refreshRes.ok) return false;
            const contentType = refreshRes.headers.get('content-type') || '';
            let parsed = null;
            if (contentType.includes('application/json')) parsed = await refreshRes.json();
            if (parsed && parsed.accessToken) {
                safeLocalSet(DEFAULT_ACCESS_TOKEN_KEY, parsed.accessToken);
                return true;
            }
            return false;
        } catch {
            return false;
        }
    }
};

/* Factory */
export function createApiClient({
    baseUrl = DEFAULT_BASE_URL,
    tokenProvider = defaultTokenProvider,
    defaultTimeoutMs = 15000,
    maxRetries = 2,
    retryOn = [502, 503, 504],
    logger = console,
    sanitizeResponse = (r) => r,
    defaultCredentials = 'include'
} = {}) {
    if (!baseUrl) throw new Error('baseUrl is required for API client');

    async function safeParseBody(res) {
        try {
            const ct = res.headers.get('content-type') || '';
            if (ct.includes('application/json')) return await res.json();
            if (ct.includes('text/')) return await res.text();
            return null;
        } catch { return null; }
    }

    async function request(endpoint, {
        method = 'GET',
        headers = {},
        body = undefined,
        query = undefined,
        timeoutMs = defaultTimeoutMs,
        retries = maxRetries,
        allowRetry = true,
        signal = undefined,
        credentials = defaultCredentials
    } = {}) {
        const url = buildUrl(baseUrl, endpoint, query);
        const hdrs = Object.assign({}, headers);
        let payload;
        const isFormData = typeof FormData !== 'undefined' && body instanceof FormData;
        if (!isFormData && body !== undefined && body !== null) {
            hdrs['Content-Type'] = hdrs['Content-Type'] || 'application/json';
            if (hdrs['Content-Type'].includes('application/json')) payload = JSON.stringify(body);
            else payload = body;
        } else if (isFormData) payload = body;

        try {
            const token = await tokenProvider.getToken();
            if (token) hdrs['Authorization'] = `Bearer ${token}`;
        } catch (e) {
            logger?.warn?.('tokenProvider.getToken failed', e?.message || e);
        }

        let attempt = 0;
        let lastErr = null;

        while (attempt <= retries) {
            attempt++;
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
            let composedSignal = controller.signal;
            if (signal) {
                const proxy = new AbortController();
                signal.addEventListener('abort', () => proxy.abort(), { once: true });
                controller.signal.addEventListener('abort', () => proxy.abort(), { once: true });
                composedSignal = proxy.signal;
            }

            try {
                const res = await fetch(url, {
                    method,
                    headers: hdrs,
                    body: payload,
                    signal: composedSignal,
                    credentials
                });
                clearTimeout(timeoutId);

                if (res.status === 401) {
                    const retried = typeof tokenProvider.onUnauthorized === 'function'
                        ? await tokenProvider.onUnauthorized(res)
                        : false;
                    if (retried && attempt < retries) {
                        await sleep(jitterBackoff(attempt));
                        continue;
                    }
                    const bodyText = await safeParseBody(res);
                    throw new UnauthorizedError('Unauthorized', { status: res.status, body: bodyText, headers: res.headers });
                }

                if (allowRetry && retryOn.includes(res.status) && attempt < retries) {
                    await sleep(jitterBackoff(attempt));
                    continue;
                }

                if (!res.ok) {
                    const parsed = await safeParseBody(res);
                    const message = (parsed && (parsed.message || parsed.error)) || `HTTP Error ${res.status}`;
                    throw new ApiError(message, { status: res.status, body: parsed, headers: res.headers });
                }

                if (res.status === 204) return null;
                const contentType = res.headers.get('content-type') || '';
                let parsedBody = null;
                if (contentType.includes('application/json')) parsedBody = await res.json();
                else if (contentType.includes('text/')) parsedBody = await res.text();
                else parsedBody = await res.blob();

                return sanitizeResponse(parsedBody, res);
            } catch (err) {
                clearTimeout(timeoutId);
                if (err && err.name === 'AbortError') {
                    lastErr = new TimeoutError(`Request timed out after ${timeoutMs} ms`);
                    if (signal && signal.aborted) throw lastErr;
                } else if (err instanceof ApiError || err instanceof UnauthorizedError) {
                    throw err;
                } else {
                    lastErr = new NetworkError(err && err.message ? err.message : String(err));
                }

                if (attempt < retries) {
                    await sleep(jitterBackoff(attempt));
                    continue;
                }
                throw lastErr;
            }
        }
        throw lastErr || new NetworkError('Unknown network error');
    }

    async function fetchJson(endpoint, opts = {}) {
        const { method = 'GET', body, headers = {}, query, timeoutMs, retries, credentials } = opts;
        const res = await request(endpoint, {
            method,
            headers: Object.assign({ Accept: 'application/json' }, headers),
            body,
            query,
            timeoutMs,
            retries,
            credentials
        });
        return res;
    }

    async function postForm(endpoint, formData, opts = {}) {
        const headers = Object.assign({}, opts.headers || {});
        return request(endpoint, Object.assign({}, opts, { method: 'POST', headers, body: formData }));
    }

    return {
        request,
        fetchJson,
        postForm,
        errors: { ApiError, NetworkError, TimeoutError, UnauthorizedError }
    };
}

/* Default client instance */
export const apiclient = createApiClient({
    baseUrl: DEFAULT_BASE_URL,
    tokenProvider: defaultTokenProvider,
    defaultTimeoutMs: 15000,
    maxRetries: 2,
    logger: console,
    defaultCredentials: 'include'
});

/* Export error classes and convenience function */
export { ApiError, NetworkError, TimeoutError, UnauthorizedError };
export const fetchJson = apiclient.fetchJson;
