/*
 * File: server/middleware/cacheMiddleware.js
 * STATUS: PRODUCTION-READY | PERFORMANCE & SCALE GRADE
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * Implements high-speed Redis caching to reduce database load and latency.
 * This is the "Turbocharger" for the Wilsy API.
 *
 * KEY FEATURES FOR FUTURE ENGINEERS:
 * 1. Look-Aside Strategy: Checks Redis first; if empty, hits DB and populates cache.
 * 2. Cryptographic Keys: Hashes URLs to create short, efficient Redis keys.
 * 3. Multi-Tenant Safe: Namespaces every cache entry by tenant and user role.
 * 4. Observability: Injects 'X-Cache' headers (HIT/MISS) for frontend debugging.
 * -----------------------------------------------------------------------------
 */

'use strict';

const Redis = require('ioredis');
const crypto = require('crypto');

// INITIALIZE REDIS CLIENT
// Use environment variables for production; default to localhost for development.
const redis = new Redis({
    host: process.env.REDIS_HOST || '127.0.0.1',
    port: process.env.REDIS_PORT || 6379,
    password: process.env.REDIS_PASSWORD || undefined,
    retryStrategy: (times) => Math.min(times * 50, 2000), // Resilience: Auto-reconnect logic
});

redis.on('error', (err) => console.warn('⚠️ [CACHE_REDIS_ERROR]:', err.message));

/**
 * KEY GENERATOR:
 * Creates a unique, role-based, tenant-isolated key for every unique API request.
 */
const buildCacheKey = (req) => {
    const tenantId = req.user?.tenantId || 'public';
    const role = req.user?.role || 'guest';
    // Hash the URL + Query string to ensure the key is a manageable length
    const urlHash = crypto.createHash('sha256').update(req.originalUrl).digest('hex');
    return `wilsy:cache:${tenantId}:${role}:${urlHash}`;
};

/**
 * CACHE MIDDLEWARE FACTORY
 * @param {number} duration - Time to live (TTL) in seconds. Default 5 minutes.
 */
const cacheMiddleware = (duration = 300) => {
    return async (req, res, next) => {
        // Only cache GET requests. Mutation (POST/PUT/DELETE) must always be real-time.
        if (req.method !== 'GET') return next();

        const key = buildCacheKey(req);

        try {
            // 1. ATTEMPT CACHE RETRIEVAL
            const cachedData = await redis.get(key);

            if (cachedData) {
                res.setHeader('X-Cache', 'HIT'); // Informs frontend the data is from cache
                return res.json(JSON.parse(cachedData));
            }

            // 2. CACHE MISS: Wrap the response to capture the data for storage
            res.setHeader('X-Cache', 'MISS');

            // Intercept the original res.json function
            const originalJson = res.json;
            res.json = function (body) {
                // Only cache successful responses (200 OK)
                if (res.statusCode === 200) {
                    redis.set(key, JSON.stringify(body), 'EX', duration)
                        .catch(err => console.error('CACHE_STORAGE_ERR:', err));
                }

                // Call the original res.json to send the data to the user
                return originalJson.call(this, body);
            };

            next();
        } catch (err) {
            // FAIL OPEN: If Redis fails, log it and proceed to the database.
            // Never let the cache layer break the application.
            console.error('CACHE_MIDDLEWARE_CRITICAL_ERR:', err);
            next();
        }
    };
};

module.exports = cacheMiddleware;