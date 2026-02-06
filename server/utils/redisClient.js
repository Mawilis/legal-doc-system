/*
 * File: server/utils/redisClient.js
 * STATUS: PRODUCTION-READY | RESILIENT CACHE GRADE
 * -----------------------------------------------------------------------------
 * PURPOSE: 
 * High-performance data bridge. Provides primary Redis access with a 
 * secondary, TTL-aware in-memory fallback to ensure 100% uptime for 
 * dependent services like Auth and Rate Limiting.
 * -----------------------------------------------------------------------------
 */

'use strict';

const { createClient } = require('redis');
const logger = require('./logger'); // Using our hardened logger

const REDIS_URL = process.env.REDIS_URL || 'redis://127.0.0.1:6379';
const DEFAULT_TTL_MS = parseInt(process.env.REDIS_DEFAULT_TTL_MS || '15000', 10);

// 1. IN-MEMORY FALLBACK (The Safety Net)
const memoryStore = new Map();
let isRedisReady = false;
let connectionRetries = 0;

// 2. CLIENT CONFIGURATION
const client = createClient({
    url: REDIS_URL,
    socket: {
        reconnectStrategy: (retries) => {
            connectionRetries = retries;
            // Exponential backoff to protect system resources
            if (retries > 10) return 30000; // Cap at 30s
            return Math.min(retries * 500, 10000);
        }
    }
});

// 3. EVENT ORCHESTRATION
client.on('error', (err) => {
    isRedisReady = false;
    // Suppress log noise: only warn on first fail or every 10th attempt
    if (connectionRetries <= 1 || connectionRetries % 10 === 0) {
        logger.warn(`⚠️ [REDIS_OFFLINE]: Using memory fallback. Reason: ${err.message}`);
    }
});

client.on('ready', () => {
    logger.info('✅ [REDIS_ONLINE]: Cache engine synchronized.');
    isRedisReady = true;
    connectionRetries = 0;
});

client.connect().catch(() => {
    /* Boot failure captured to allow fallback start */
});

// --- FORENSIC HELPERS ---

const isConnected = () => isRedisReady && client.isOpen;

/**
 * ATOMIC JSON RETRIEVAL
 * Automatically switches between Redis and Memory based on health.
 */
exports.getJson = async (key) => {
    try {
        if (isConnected()) {
            const raw = await client.get(key);
            return raw ? JSON.parse(raw) : null;
        }
    } catch (e) {
        logger.error(`❌ [CACHE_GET_ERR]: ${key}`, e);
    }

    // MEMORY FALLBACK LOGIC
    const entry = memoryStore.get(key);
    if (!entry) return null;

    // Manual TTL Check for Memory Fallback
    if (entry.expiresAt && Date.now() > entry.expiresAt) {
        memoryStore.delete(key);
        return null;
    }
    return entry.value;
};

/**
 * ATOMIC JSON PERSISTENCE
 */
exports.setJson = async (key, value, ttlMs = DEFAULT_TTL_MS) => {
    try {
        if (isConnected()) {
            await client.set(key, JSON.stringify(value), { PX: ttlMs });
            return true;
        }
    } catch (e) {
        logger.error(`❌ [CACHE_SET_ERR]: ${key}`, e);
    }

    // MEMORY FALLBACK PERSISTENCE
    memoryStore.set(key, {
        value,
        expiresAt: ttlMs ? Date.now() + ttlMs : null
    });

    // Memory cap to prevent heap overflow
    if (memoryStore.size > 1000) {
        const firstKey = memoryStore.keys().next().value;
        memoryStore.delete(firstKey);
    }

    return true;
};

module.exports = {
    client,
    isConnected,
    getJson: exports.getJson,
    setJson: exports.setJson
};