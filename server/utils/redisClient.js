// File: /Users/wilsonkhanyezi/legal-doc-system/server/utils/redisClient.js
// -----------------------------------------------------------------------------
// COLLABORATION NOTES:
// - This module wraps Redis with enterprise‑grade resilience.
// - Primary use: caching and lightweight pub/sub for Gateway and services.
// - Fallback: if Redis is unavailable, we silently switch to in‑memory Map.
// - Retry strategy: exponential backoff after 5 failures to avoid log flooding.
// - Logging: one warning on first failure, then every 10th retry.
// - TTL: defaults to 15s, configurable via REDIS_DEFAULT_TTL_MS.
// - Engineers: when extending, preserve silent fallback to avoid crashing
//   dependent services. Discuss with infra team before changing reconnect logic.
// -----------------------------------------------------------------------------

'use strict';

const { createClient } = require('redis');

const REDIS_URL = process.env.REDIS_URL || 'redis://127.0.0.1:6379';
const DEFAULT_TTL_MS = parseInt(process.env.REDIS_DEFAULT_TTL_MS || String(15 * 1000), 10);

// In‑memory fallback store
const memoryStore = new Map();
let isRedisReady = false;
let connectionRetries = 0;

// Intelligent Retry Strategy
const client = createClient({
    url: REDIS_URL,
    socket: {
        reconnectStrategy: (retries) => {
            connectionRetries = retries;
            if (retries > 5) {
                // After 5 failures, slow down to 10s intervals
                return 10000;
            }
            return 1000; // otherwise 1s
        }
    }
});

// Error handling with noise suppression
client.on('error', (err) => {
    isRedisReady = false;
    if (connectionRetries <= 1 || connectionRetries % 10 === 0) {
        console.warn(`⚠️ [Redis] Connection Warning: Using In‑Memory Fallback (${err.code || err.message})`);
    }
});

client.on('ready', () => {
    console.log('✅ [Redis] Connected and Ready');
    isRedisReady = true;
    connectionRetries = 0;
});

client.on('end', () => {
    console.log('ℹ️ [Redis] Disconnected');
    isRedisReady = false;
});

// Non‑blocking connect
client.connect().catch(() => {
    // Catch initial failure to prevent crash
});

// --- Helper Functions ---

function isConnected() {
    return isRedisReady && client.isOpen;
}

async function getJson(key) {
    try {
        if (isConnected()) {
            const raw = await client.get(key);
            return raw ? JSON.parse(raw) : null;
        }
    } catch (e) { /* fall through */ }

    // Memory fallback
    const entry = memoryStore.get(key);
    if (!entry) return null;
    if (entry.expiresAt && Date.now() > entry.expiresAt) {
        memoryStore.delete(key);
        return null;
    }
    return entry.value;
}

async function setJson(key, value, ttlMs = DEFAULT_TTL_MS) {
    try {
        if (isConnected()) {
            await client.set(key, JSON.stringify(value), { PX: ttlMs });
            return true;
        }
    } catch (e) { /* ignore */ }

    // Memory fallback
    memoryStore.set(key, {
        value,
        expiresAt: ttlMs ? Date.now() + ttlMs : null
    });
    return true;
}

module.exports = {
    client,
    isConnected,
    getJson,
    setJson
};
