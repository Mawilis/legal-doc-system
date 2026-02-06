/**
 * File: server/lib/redisClient.js
 * PATH: server/lib/redisClient.js
 * STATUS: PRODUCTION-READY | BIBLICAL | ARCHITECT-GRADE
 * VERSION: 20.0.0 (The Iron Circuit)
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * - The high-velocity data artery for Wilsy OS.
 * - Handles identity caching, rate-limiting, and elastic plan lookups.
 * - Engineered for maximum resilience against South African power/network grid instability.
 *
 * SOVEREIGN SECURITY REQUIREMENTS:
 * 1. STRICT TLS: Rejects all unverified certificates in production. No exceptions.
 * 2. COMMAND TIMEOUTS: Prevents blocked threads by timing out zombie requests.
 * 3. CONNECTION POOLING: Singleton architecture to manage TCP overhead.
 * 4. ATOMIC FAILFAST: Triggers the L1-Heuristic fallback immediately if Redis is unreachable.
 *
 * COLLABORATION (NON-NEGOTABLE):
 * - CHIEF ARCHITECT: Wilson Khanyezi
 * - SECURITY: @Wilsy-Security (Zero-Trust Enforcement)
 * - SRE: @Infra-Guard (Connection Lifecycle)
 * -----------------------------------------------------------------------------
 * EPITOME:
 * Biblical worth billions no child's place. Wilsy OS to the World.
 */

'use strict';

const IORedis = require('ioredis');

// --- 1. SECURE ENVIRONMENT RESOLUTION ---
const {
    REDIS_URL,
    REDIS_HOST,
    REDIS_PORT = 6379,
    REDIS_PASSWORD,
    REDIS_TLS = 'true', // Default to secure in the future
    NODE_ENV = 'development'
} = process.env;

/* ---------------------------------------------------------------------------
   2. RECONNECTION PROTOCOL
   - Sophisticated exponential backoff to handle Load Shedding/Network Recovery.
   --------------------------------------------------------------------------- */
const retryStrategy = (times) => {
    // Stop retrying after 20 attempts (~1 minute of total downtime) 
    // to allow the OS to stay in L1-Only mode without wasting CPU cycles.
    if (times > 20) {
        console.error('🔥 [REDIS] FATAL: Max retries exceeded. Lock-in L1-Fallback.');
        return null;
    }
    const delay = Math.min(times * 200, 5000);
    return delay;
};

/* ---------------------------------------------------------------------------
   3. SECURE OPTION FACTORY
   --------------------------------------------------------------------------- */
const createSecureOptions = () => {
    const isProd = NODE_ENV === 'production';

    const options = {
        retryStrategy,
        connectTimeout: 10000, // 10s Genesis Handshake
        commandTimeout: 3000,  // 3s Execution Ceiling (Billion-dollar speed)
        enableOfflineQueue: false, // Prevent Memory Bloat during outages
        reconnectOnError: (err) => {
            // Force reconnection if we hit a Read-Only slave during AWS/Azure failover
            return err.message.includes('READONLY');
        }
    };

    // --- ENFORCE PRODUCTION TLS ---
    if (REDIS_TLS === 'true' || isProd) {
        options.tls = {
            // In Production, we MUST verify certificates.
            // rejectUnauthorized: true (Secure) vs false (Childish)
            rejectUnauthorized: isProd,
            servername: REDIS_HOST || (REDIS_URL ? new URL(REDIS_URL).hostname : undefined)
        };
    }

    return options;
};

/* ---------------------------------------------------------------------------
   4. SINGLETON INITIALIZATION
   --------------------------------------------------------------------------- */
let redis = null;

try {
    const options = createSecureOptions();

    if (REDIS_URL) {
        redis = new IORedis(REDIS_URL, options);
    } else if (REDIS_HOST) {
        redis = new IORedis({
            host: REDIS_HOST,
            port: Number(REDIS_PORT),
            password: REDIS_PASSWORD || undefined,
            ...options
        });
    }

    if (redis) {
        // --- FORENSIC OBSERVABILITY ---
        redis.on('connect', () => console.log('✅ [REDIS] Sovereign Connection Established.'));
        redis.on('ready', () => console.log('⚡ [REDIS] IO Ready: Cache Engine Online.'));
        redis.on('error', (err) => console.error('❌ [REDIS] Security/Transport Error:', err.message));
        redis.on('close', () => console.warn('⚠️ [REDIS] Connection Closed.'));
    } else {
        console.warn('⚠️ [REDIS] Missing Configuration. Wilsy OS running on L1-Heuristics.');
    }
} catch (error) {
    console.error('🔥 [REDIS] Genesis Failure:', error.message);
}

/* ---------------------------------------------------------------------------
   5. DEPLOYMENT EXPORT
   --------------------------------------------------------------------------- */
module.exports = redis;

/**
 * ARCHITECTURAL FINALITY:
 * This file is now secured against Man-in-the-Middle attacks. 
 * By using 'rejectUnauthorized: true' in production, we ensure that Wilsy OS 
 * only talks to verified, encrypted Redis clusters. 
 * This is the standard for Billion-Dollar Financial/Legal software.
 */