/**
 * File: src/features/superadmin/services/MetricsService.js
 * -----------------------------------------------------------------------------
 * STATUS: EPITOME | Wilsy OS Metrics Service (System Health Pulse)
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * - Fetches low-latency system health metrics for dashboards and investors.
 * - Monitors database connectivity, gateway uptime, socket clients, queue depth, latency.
 * - Provides resilience: retries, caching, and graceful fallbacks.
 * -----------------------------------------------------------------------------
 * DESIGN NOTES:
 * - Axios instance with interceptors for auth headers and error logging.
 * - Retry logic with exponential backoff for flaky networks.
 * - In-memory cache with TTL for hot paths (dashboard refresh).
 * - Normalized output for UI Pulse Tiles (consistent keys).
 * - Extensible: add metrics (CPU, memory, latency) without breaking consumers.
 * -----------------------------------------------------------------------------
 */

import axios from 'axios';

const BASE_URL = process.env.REACT_APP_GATEWAY_URL || 'http://localhost:3001';
const API = axios.create({
    baseURL: `${BASE_URL}/api`,
    timeout: 10000,
});

// Attach token automatically
API.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
});

// Retry helper
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function withRetry(fn, { attempts = 3, baseDelay = 300 } = {}) {
    let lastError;
    for (let i = 0; i < attempts; i++) {
        try {
            return await fn();
        } catch (err) {
            lastError = err;
            const delay = baseDelay * Math.pow(2, i);
            await sleep(delay);
        }
    }
    throw lastError;
}

// Cache
const cache = new Map();
function setCache(key, value, ttlMs = 5000) {
    cache.set(key, { value, expires: Date.now() + ttlMs });
}
function getCache(key) {
    const entry = cache.get(key);
    if (!entry) return null;
    if (Date.now() > entry.expires) {
        cache.delete(key);
        return null;
    }
    return entry.value;
}

// Normalizer
function normalizeMetrics(raw = {}) {
    return {
        dbState: raw.dbState || 'unknown',
        status: raw.status || 'offline',
        socketClients: Number(raw.socketClients ?? 0),
        uptime: Number(raw.uptime ?? 0),
        latency: Number(raw.latency ?? 0),
        queues: raw.queues || {},
        version: raw.version || 'v3.0',
        timestamp: Date.now(),
    };
}

function syntheticFallback() {
    return normalizeMetrics({
        dbState: 'disconnected',
        status: 'error',
        socketClients: 0,
        uptime: 0,
        latency: 0,
        queues: {},
        version: 'v3.0',
    });
}

/**
 * Fetch system metrics for dashboard pulse tiles.
 * Returns normalized object:
 * {
 *   dbState: 'connected' | 'disconnected' | 'unknown',
 *   status: 'online' | 'offline' | 'error' | 'degraded',
 *   socketClients: number,
 *   uptime: seconds,
 *   latency: ms,
 *   queues: { name: depth },
 *   version: string,
 *   timestamp: number
 * }
 */
export async function getSystemMetrics({ useCache = true } = {}) {
    const cacheKey = 'systemMetrics';
    if (useCache) {
        const cached = getCache(cacheKey);
        if (cached) return cached;
    }

    try {
        // Connects to AnalyticsController.getSystemHealth
        const res = await withRetry(() => API.get('/admin/metrics'));
        const metrics = normalizeMetrics(res.data || {});
        setCache(cacheKey, metrics);
        return metrics;
    } catch (err) {
        console.warn('⚠️ [MetricsService] Health check failed, using fallback.', err?.message);
        const fallback = syntheticFallback();
        setCache(cacheKey, fallback);
        return fallback;
    }
}
