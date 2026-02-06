/**
 * ============================================================================
 * ⚡️🧠 QUANTUM CACHE ENGINE: REDIS-POWERED INTELLIGENCE ACCELERATOR ⚡️🧠
 * ============================================================================
 */

const redis = require('redis');
const { promisify } = require('util');

// ENV VALIDATION
if (!process.env.REDIS_URL) {
    console.error('QUANTUM BREACH: REDIS_URL missing from .env');
    // Fallback to in-memory cache for development
}

// CACHE KEYS ENUMERATION
const CACHE_KEYS = {
    MONETIZATION: 'monetization',
    PLAN_MIX: 'planmix',
    DASHBOARD: 'dashboard',
    COMPLIANCE_HEATMAP: 'compliance:heatmap',
    AUDIT_LOGS: 'audit:logs',
    SYSTEM_HEALTH: 'system:health',
    VALIDATION_TOKENS: 'validation:tokens',
    RATE_LIMITS: 'ratelimit'
};

class QuantumCache {
    constructor() {
        this.client = null;
        this.ready = false;
        this.memoryCache = new Map(); // Fallback cache

        if (process.env.REDIS_URL) {
            this.initRedis();
        }
    }

    async initRedis() {
        try {
            this.client = redis.createClient({
                url: process.env.REDIS_URL,
                password: process.env.REDIS_PASSWORD,
                socket: {
                    tls: process.env.NODE_ENV === 'production',
                    reconnectStrategy: (retries) => {
                        if (retries > 10) {
                            console.error('QUANTUM CACHE: Redis connection failed after 10 retries');
                            return new Error('Max retries exceeded');
                        }
                        return Math.min(retries * 100, 3000);
                    }
                }
            });

            this.client.on('error', (err) => {
                console.error('QUANTUM CACHE ERROR:', err);
                this.ready = false;
            });

            this.client.on('connect', () => {
                console.log('QUANTUM CACHE: Redis connected successfully');
                this.ready = true;
            });

            await this.client.connect();

            // Promisify methods
            this.getAsync = this.client.get.bind(this.client);
            this.setAsync = this.client.set.bind(this.client);
            this.delAsync = this.client.del.bind(this.client);
            this.expireAsync = this.client.expire.bind(this.client);
            this.incrAsync = this.client.incr.bind(this.client);

        } catch (error) {
            console.error('QUANTUM CACHE: Failed to initialize Redis:', error);
            this.ready = false;
        }
    }

    /**
     * Get value from cache with fallback
     * @param {string} key - Cache key
     * @returns {Promise<any>} Cached value or null
     */
    async get(key) {
        if (this.ready && this.client) {
            try {
                const value = await this.getAsync(key);
                return value ? JSON.parse(value) : null;
            } catch (error) {
                console.warn('QUANTUM CACHE: Redis get failed, falling back to memory:', error);
                return this.memoryCache.get(key) || null;
            }
        }
        return this.memoryCache.get(key) || null;
    }

    /**
     * Set value in cache with TTL
     * @param {string} key - Cache key
     * @param {any} value - Value to cache (will be JSON stringified)
     * @param {number} ttlSeconds - Time to live in seconds
     * @returns {Promise<boolean>} Success status
     */
    async set(key, value, ttlSeconds = 300) {
        const stringValue = JSON.stringify(value);

        if (this.ready && this.client) {
            try {
                await this.setAsync(key, stringValue);
                if (ttlSeconds > 0) {
                    await this.expireAsync(key, ttlSeconds);
                }
                return true;
            } catch (error) {
                console.warn('QUANTUM CACHE: Redis set failed, falling back to memory:', error);
                this.memoryCache.set(key, value);
                // Auto-expire from memory cache
                setTimeout(() => this.memoryCache.delete(key), ttlSeconds * 1000);
                return false;
            }
        }

        this.memoryCache.set(key, value);
        setTimeout(() => this.memoryCache.delete(key), ttlSeconds * 1000);
        return true;
    }

    /**
     * Delete key from cache
     * @param {string} key - Cache key to delete
     */
    async delete(key) {
        if (this.ready && this.client) {
            try {
                await this.delAsync(key);
            } catch (error) {
                console.warn('QUANTUM CACHE: Redis delete failed:', error);
            }
        }
        this.memoryCache.delete(key);
    }

    /**
     * Increment counter with rate limiting
     * @param {string} key - Counter key
     * @param {number} ttlSeconds - Reset after seconds
     * @returns {Promise<number>} New count
     */
    async increment(key, ttlSeconds = 60) {
        if (this.ready && this.client) {
            try {
                const count = await this.incrAsync(key);
                if (count === 1) {
                    await this.expireAsync(key, ttlSeconds);
                }
                return count;
            } catch (error) {
                console.warn('QUANTUM CACHE: Redis increment failed:', error);
            }
        }

        // Memory fallback
        const current = this.memoryCache.get(key) || 0;
        const newCount = current + 1;
        this.memoryCache.set(key, newCount);

        if (!this.memoryCache.has(`${key}:ttl`)) {
            this.memoryCache.set(`${key}:ttl`, true);
            setTimeout(() => {
                this.memoryCache.delete(key);
                this.memoryCache.delete(`${key}:ttl`);
            }, ttlSeconds * 1000);
        }

        return newCount;
    }

    /**
     * Clear cache by pattern (for tenant-specific invalidation)
     * @param {string} pattern - Redis pattern to match
     */
    async clearPattern(pattern) {
        if (this.ready && this.client) {
            try {
                const keys = await this.client.keys(pattern);
                if (keys.length > 0) {
                    await this.client.del(keys);
                }
            } catch (error) {
                console.error('QUANTUM CACHE: Clear pattern failed:', error);
            }
        }

        // Clear from memory cache
        for (const key of this.memoryCache.keys()) {
            if (key.includes(pattern.replace('*', ''))) {
                this.memoryCache.delete(key);
            }
        }
    }
}

// Singleton instance
const quantumCache = new QuantumCache();

module.exports = {
    quantumCache,
    CACHE_KEYS,
    cacheGet: (key) => quantumCache.get(key),
    cacheSet: (key, value, ttl) => quantumCache.set(key, value, ttl),
    cacheDelete: (key) => quantumCache.delete(key),
    cacheIncrement: (key, ttl) => quantumCache.increment(key, ttl),
    clearCachePattern: (pattern) => quantumCache.clearPattern(pattern)
};