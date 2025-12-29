// File: /Users/wilsonkhanyezi/legal-doc-system/server/routes/dashboardRoutes.js
// Status: PRODUCTION-READY | Caching Enabled
'use strict';

const express = require('express');
const router = express.Router();
const controller = require('../controllers/dashboardController');
const authMiddleware = require('../middleware/authMiddleware');

// ---- Collaboration Note ----
// @Engineer: This route now implements the "Look-Aside Cache" pattern.
// If valid cache exists, we return it instantly (0ms latency).
// If not, we await the controller and update the cache.
// ----------------------------

// 1. Async Wrapper (The Safety Net)
// Catches any rejected promises in the controller to prevent server crashes
const asyncHandler = (fn) => (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch((err) => {
        console.error(`🔴 [Dashboard Route Error] ${err.message}`);
        next(err);
    });
};

// 2. Resilient Auth Fallback
// Ensures development continues even if auth middleware is temporarily broken
const protect = (authMiddleware && typeof authMiddleware.protect === 'function')
    ? authMiddleware.protect
    : (req, res, next) => {
        if (process.env.NODE_ENV !== 'production') {
            console.warn('⚠️ AuthMiddleware bypassed for Dev');
            return next();
        }
        res.status(500).json({ message: 'Auth Module Missing in Production' });
    };

// 3. In-Memory Cache Strategy
// Scale Note: Move to Redis when running >1 instance
const cache = { payload: null, expiresAt: 0 };
const CACHE_TTL = parseInt(process.env.DASHBOARD_CACHE_TTL_MS || '15000', 10); // 15 seconds

/**
 * @route   GET /api/dashboard
 * @desc    Get Sheriff Ops overview with caching
 * @access  Protected
 */
router.get('/', protect, asyncHandler(async (req, res) => {
    const requestId = req.headers['x-request-id'] || 'trace-unknown';

    // A. Cache Hit Check
    if (cache.payload && Date.now() < cache.expiresAt) {
        // console.debug(`⚡ Cache Hit [${requestId}]`); // Uncomment for verbose debug
        return res.json({
            success: true,
            cached: true,
            requestId: requestId,
            data: cache.payload
        });
    }

    // B. Cache Miss - Fetch from Controller
    // Note: Controller must RETURN data, not send res.json()
    const payload = await controller.getStats(req);

    // C. Write to Cache
    if (payload) {
        cache.payload = payload;
        cache.expiresAt = Date.now() + CACHE_TTL;
    }

    // D. Send Response
    res.json({
        success: true,
        cached: false,
        requestId: requestId,
        data: payload
    });
}));

module.exports = router;