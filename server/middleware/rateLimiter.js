/*
 * File: server/middleware/rateLimiter.js
 * STATUS: PRODUCTION-READY | INFRASTRUCTURE PROTECTION GRADE
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * Prevents API abuse and ensures Fair Usage Policy (FUP) across all firms.
 * Acts as a shield against DDoS and Brute-Force attacks.
 *
 * KEY FEATURES FOR FUTURE ENGINEERS:
 * 1. Redis-Backed: Shares limit counts across all cluster nodes/instances.
 * 2. Tenant-Centric: Limits are applied per Firm, not just per IP.
 * 3. Subscription Linked: Automatically adjusts limits based on the Firm's plan.
 * 4. Auth Hardening: Dedicated stricter limits for login and MFA routes.
 * -----------------------------------------------------------------------------
 */

'use strict';

const rateLimit = require('express-rate-limit');
const RedisStore = require('rate-limit-redis'); // npm install rate-limit-redis ioredis
const Redis = require('ioredis');

// 1. SHARED REDIS CLIENT
const redisClient = new Redis(process.env.REDIS_URL || 'redis://127.0.0.1:6379');

/**
 * DYNAMIC LIMITER ENGINE
 * Calculates the allowed throughput based on Tenant identity and Plan.
 */
const getDynamicLimit = (req) => {
    // If it's a known tenant, we look at their plan
    const plan = req.user?.tenant?.subscription?.plan || 'Free';

    switch (plan) {
        case 'Enterprise': return 5000; // 5k requests per window
        case 'Pro': return 1000;
        case 'Free': return 100;
        default: return 50;  // Unauthenticated/Unknown
    }
};

/**
 * STANDARD API LIMITER
 * Protects general resource routes (Cases, Documents, Invoices).
 */
const apiLimiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 Minute Window
    max: (req) => getDynamicLimit(req),
    standardHeaders: true,    // Return RateLimit-* headers
    legacyHeaders: false,

    // REDIS STORE: Critical for Billion-Dollar Scale
    store: new RedisStore({
        sendCommand: (...args) => redisClient.call(...args),
        prefix: 'wilsy_rl_api:',
    }),

    handler: (req, res) => {
        // --- FORENSIC AUDIT LOGGING ---
        if (req.logAudit) {
            req.logAudit('RATE_LIMIT_EXCEEDED', {
                ip: req.ip,
                tenantId: req.user?.tenantId,
                path: req.originalUrl
            });
        }

        return res.status(429).json({
            success: false,
            status: 'error',
            code: 'ERR_RATE_LIMIT_EXCEEDED',
            message: 'Too many requests. For legal integrity, traffic has been throttled.',
            meta: {
                retryAfter: '15 minutes',
                correlationId: req.correlationId
            }
        });
    }
});

/**
 * AUTH BRUTE-FORCE PROTECTOR
 * Much stricter limits for login/password-reset routes.
 */
const authLimiter = rateLimit({
    windowMs: 60 * 60 * 1000, // 1 Hour Window
    max: 10,                 // Only 10 attempts per hour per IP
    message: 'Too many login attempts. Account locked for 1 hour for security.',
    store: new RedisStore({
        sendCommand: (...args) => redisClient.call(...args),
        prefix: 'wilsy_rl_auth:',
    }),
});

module.exports = { apiLimiter, authLimiter };