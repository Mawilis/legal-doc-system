/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - REDIS SINGULARITY NUCLEUS [V32.8.1-ANCHOR-FORTRESS]                                                                         ║
 * ║ [DIRECT CLIENT INJECTION | CONTEXT-BOUND EXPORTS | FORENSIC METRICS | NON-BLOCKING HEALING]                                            ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 32.8.1-ANCHOR-STABLE | PRODUCTION HARDENED | BILLION DOLLAR SPEC                                                              ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL PERFORMANCE | THE NUCLEUS HEART                                    ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/config/redis.js                                                           ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated structural integrity and literal code block output to obliterate formatting noise.   ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Purged Proxy pattern. Context-bound `.set()` at the root export to eliminate TypeErrors.        ║
 * ║ • AI Engineering (Gemini) - FORTIFIED: Built connection-safe wrappers for `setex` and `set` to guarantee execution under load.         ║
 * ║ • AI Engineering (Gemini) - ALIGNED: Injected universal callback wrappers and explicit .get/.rawGet to bridge V3/V4 mismatch. [2026-05-24]║
 * ║ • AI Engineering (Gemini) - SEALED: Injected missing `getClient()` export to fix Quantum Anchor fracture and hardened default exports. ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import { createClient as createRedisClient } from 'redis';
import chalk from 'chalk';
import logger from '../utils/logger.js';
import { flushColdStorage } from '../utils/telemetryLogger.js';
import client from 'prom-client';

const REDIS_URL = process.env.REDIS_URL || 'redis://127.0.0.1:6379';
const REDIS_PASSWORD = process.env.REDIS_PASSWORD;

/** @type {client.Gauge} Prometheus metric for tracking Redis health status. */
const redisHealthGauge = new client.Gauge({
  name: 'wilsy_redis_health_status',
  help: 'Redis health status (1=healthy, 0=unhealthy)'
});

/**
 * Generates the adaptive hardware configuration for the Redis socket.
 * @function getHardwareConfig
 * @returns {Object} Redis client configuration.
 */
const getHardwareConfig = () => {
  const config = {
    url: REDIS_URL,
    socket: {
      reconnectStrategy: (retries) => Math.min(retries * 50, 2000),
      connectTimeout: 10000,
      keepAlive: 30000
    }
  };
  if (REDIS_PASSWORD && REDIS_PASSWORD.trim() !== '' && REDIS_PASSWORD !== 'null') {
    config.password = REDIS_PASSWORD;
  }
  return config;
};

/** * 🛡️ SOVEREIGN REDIS CLIENT
 * Directly instantiated. No proxies, preserving strict internal V4 contexts.
 */
export const redisClient = createRedisClient(getHardwareConfig());

// Securely bind native V4 methods to avoid recursion when we patch the client
const nativeSet = typeof redisClient.set === 'function' ? redisClient.set.bind(redisClient) : async () => {};
const nativeGet = typeof redisClient.get === 'function' ? redisClient.get.bind(redisClient) : async () => {};

/**
 * Connection-Safe Set Operation (V3 & V4 Adaptive).
 * Captures edge cases where the network drops milliseconds before a set command.
 * Supports both modern Promise-based execution and legacy callback patterns.
 * @function safeSet
 * @param {...any} args - Redis set arguments
 * @returns {Promise<any>}
 */
export const safeSet = async (...args) => {
    if (!redisClient.isOpen) {
        logger.warn(`[REDIS-NUCLEUS] .set() invoked while unanchored. Healing link...`);
        await redisClient.connect().catch(() => {});
    }

    // Handle legacy callback pattern if present
    const lastArg = args[args.length - 1];
    if (typeof lastArg === 'function') {
        const callback = args.pop();
        try {
            const res = await nativeSet(...args);
            callback(null, res);
            return res;
        } catch (err) {
            callback(err);
            return null;
        }
    }
    return await nativeSet(...args);
};

/**
 * Connection-Safe Get Operation.
 * Intercepts `rawGet` calls from legacy discovery middleware.
 * @function safeGet
 * @param {...any} args - Redis get arguments
 * @returns {Promise<any>}
 */
export const safeGet = async (...args) => {
    if (!redisClient.isOpen) {
        await redisClient.connect().catch(() => {});
    }

    const lastArg = args[args.length - 1];
    if (typeof lastArg === 'function') {
        const callback = args.pop();
        try {
            const res = await nativeGet(...args);
            callback(null, res);
            return res;
        } catch (err) {
            callback(err);
            return null;
        }
    }
    return await nativeGet(...args);
};

/**
 * Enhanced V4+ compliant set operation with Time-To-Live.
 * @function setex
 * @param {...any} args - Arguments (key, ttl, value, [callback])
 * @returns {Promise<string>} Redis command response.
 */
export const setex = async (...args) => {
    if (!redisClient.isOpen) {
        await redisClient.connect().catch(() => {});
    }

    const lastArg = args[args.length - 1];
    let hasCallback = false;
    let callback;

    if (typeof lastArg === 'function') {
        hasCallback = true;
        callback = args.pop();
    }

    try {
        // Translate to V4 syntax: .set(key, value, { EX: ttl })
        const res = await nativeSet(args[0], args[2], { EX: Number(args[1]) });
        if (hasCallback) callback(null, res);
        return res;
    } catch (err) {
        if (hasCallback) callback(err);
        return null;
    }
};

// 🛡️ HARD-PATCH THE CLIENT OBJECT
// Guarantees methods exist regardless of how the controller destructured the import
redisClient.set = safeSet;
redisClient.get = safeGet;
redisClient.rawGet = safeGet;
redisClient.setex = setex;

// ============================================================================
// 📡 NUCLEUS TELEMETRY & LIFECYCLE EVENTS
// ============================================================================

redisClient.on('connect', () => {
    console.log(chalk.cyan('🔷 Redis Singularity Nucleus: INITIATING LINK...'));
});

redisClient.on('ready', async () => {
  console.log(chalk.green(`✅ Redis Singularity Ready | Nucleus Anchored V32.8.1.`));
  redisHealthGauge.set(1);
  try {
      await flushColdStorage();
  } catch (error) {
      logger.error('❌ Telemetry Flush Failure:', { message: error.message });
  }
});

redisClient.on('error', (err) => {
  redisHealthGauge.set(0);
  if (err.message !== 'Connection is closed.') {
      logger.error('💥 [REDIS-FAILURE]', { message: err.message });
  }
});

redisClient.on('end', () => {
  redisHealthGauge.set(0);
  console.log(chalk.yellow('🔌 Redis link terminated. Telemetry buffering in Cold Storage.'));
});

/**
 * Health check monitor for the Redis Nucleus.
 * @async @function checkRedisHealth
 * @returns {Promise<{status: string, latency: number, ts: number}>}
 */
export const checkRedisHealth = async () => {
  try {
    if (!redisClient.isOpen) return { status: 'UNHEALTHY', ts: Date.now() };
    const start = Date.now();
    await redisClient.ping();
    return { status: 'HEALTHY', latency: Date.now() - start, ts: Date.now() };
  } catch (err) {
    return { status: 'UNHEALTHY', error: err.message, ts: Date.now() };
  }
};

/**
 * Establishes the connection to Redis with exponential backoff strategy.
 * @async @function createClient
 * @returns {Promise<boolean>} Success status.
 */
export const createClient = async () => {
  if (redisClient.isOpen) return true;
  try {
    await redisClient.connect();
    return true;
  } catch (error) {
    logger.error('💥 [REDIS-CONNECTION-FATAL]', { message: error.message });
    return false;
  }
};

/**
 * Seals the Redis connection during system termination.
 * @async @function disconnect
 */
export const disconnect = async () => {
  if (redisClient.isOpen) {
      try {
          await redisClient.quit();
      } catch (e) {
          await redisClient.disconnect();
      }
  }
};

/**
 * Exposes the raw client explicitly to satisfy legacy architectural demands
 * like the Quantum Anchor Snapshot.
 * @function getClient
 * @returns {Object} The Redis client instance.
 */
export const getClient = () => redisClient;

process.on('SIGINT', async () => {
    await disconnect();
    process.exit(0);
});

// ============================================================================
// 🏛️ SOVEREIGN EXPORT (Protects against default import object fractures)
// ============================================================================
export const set = safeSet;
export const get = safeGet;
export const rawGet = safeGet;

export default {
    createClient,
    disconnect,
    checkRedisHealth,
    redisClient,
    getClient,
    setex,
    set: safeSet,
    get: safeGet,
    rawGet: safeGet
};
