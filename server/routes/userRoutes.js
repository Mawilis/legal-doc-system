/**
 * File: server/routes/userRoutes.js
 * PATH: server/routes/userRoutes.js
 * STATUS: GOD-TIER | EPITOME | PRODUCTION-READY
 * VERSION: 15.0.0 (The Identity Sovereign)
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * - The Identity Gateway for Wilsy OS.
 * - Orchestrates the "Handshake" between Law Firm Principals and the Core.
 * - Manages the lifecycle of Sovereign Access: Login, OTP, Refresh, and Me.
 *
 * ARCHITECTURAL SUPREMACY:
 * 1. FAIL-SAFE REGISTRY: Audits Controller exports during boot to prevent runtime 404s.
 * 2. BRUTE-FORCE PROTECTION: Layered rate limiting for public/private auth vectors.
 * 3. IDENTITY HANDSHAKE: Advanced OTP/Password resolution for white-label entry.
 * 4. FORENSIC VALIDATION: Strict express-validator schema enforcement.
 * -----------------------------------------------------------------------------
 * EPITOME:
 * Biblical worth billions no child's place. Wilsy OS to the World.
 */

'use strict';

const express = require('express');
const router = express.Router();
const { body, validationResult } = require('express-validator');
const rateLimit = require('express-rate-limit');

// --- DEPENDENCIES ---
const userController = require('../controllers/userController');
const { protect } = require('../middleware/authMiddleware');

/* ---------------------------------------------------------------------------
   1. SOVEREIGN REGISTRY AUDIT (Fail-Fast Logic)
   --------------------------------------------------------------------------- */
const requiredHandlers = [
    'login',
    'register',
    'getMe',
    'requestOtp',
    'verifyOtp',
    'refreshToken',
    'logout'
];

// Verify the integrity of the Controller before allowing the server to boot
requiredHandlers.forEach(handler => {
    if (typeof userController[handler] !== 'function') {
        // Log precisely which link in the billion-dollar chain is broken
        console.error(`[CRITICAL] Identity Handshake Failure: Missing ${handler} in userController.`);
        // We do not throw here to allow the server to report its status, 
        // but we assign a placeholder to prevent the 'undefined' TypeError.
        userController[handler] = (req, res) => res.status(501).json({ error: 'Endpoint under construction' });
    }
});

/* ---------------------------------------------------------------------------
   2. TRAFFIC GOVERNANCE (Rate Limiters)
   --------------------------------------------------------------------------- */

const authLimiter = rateLimit({
    windowMs: 60 * 1000,
    max: 20,
    standardHeaders: true,
    legacyHeaders: false,
    message: { success: false, message: 'Identity verification throttled. Please wait.' }
});

const otpLimiter = rateLimit({
    windowMs: 60 * 60 * 1000,
    max: 5,
    standardHeaders: true,
    legacyHeaders: false,
    message: { success: false, message: 'OTP limit reached. Contact Wilsy Support.' }
});

/* ---------------------------------------------------------------------------
   3. DEFENSIVE MIDDLEWARE
   --------------------------------------------------------------------------- */

const handleValidation = (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
        return res.status(400).json({
            status: 'error',
            message: 'Sovereign Validation Failure',
            errors: errors.array()
        });
    }
    next();
};

/* ---------------------------------------------------------------------------
   4. PUBLIC IDENTITY ROUTES (The Entry Handshake)
   --------------------------------------------------------------------------- */

/**
 * POST /api/auth/register
 * - The creation of a new Sovereign Identity.
 */
router.post(
    '/register',
    authLimiter,
    [
        body('name').trim().notEmpty().withMessage('Name is a biblical requirement'),
        body('email').isEmail().withMessage('Valid email required for identity'),
        body('password').isLength({ min: 8 }).withMessage('Security requires 8+ character password')
    ],
    handleValidation,
    userController.register
);

/**
 * POST /api/auth/login
 * - Primary vault entry.
 */
router.post(
    '/login',
    authLimiter,
    [
        body('email').isEmail().withMessage('Email required'),
        body('password').notEmpty().withMessage('Password required')
    ],
    handleValidation,
    userController.login
);

/**
 * POST /api/auth/otp/request
 * - Identity handshake for multi-factor/forgot-password flows.
 */
router.post(
    '/otp/request',
    otpLimiter,
    body('email').isEmail().withMessage('Email required for OTP'),
    handleValidation,
    userController.requestOtp
);

// Alias for legacy enterprise systems
router.post('/identify', otpLimiter, body('email').isEmail(), handleValidation, userController.requestOtp);

/**
 * POST /api/auth/otp/verify
 * - Verification of the one-time sovereign code.
 */
router.post(
    '/otp/verify',
    otpLimiter,
    [
        body('code').trim().notEmpty().withMessage('Verification code required'),
        body('email').optional().isEmail().withMessage('Valid email required')
    ],
    handleValidation,
    userController.verifyOtp
);

/* ---------------------------------------------------------------------------
   5. SESSION GOVERNANCE
   --------------------------------------------------------------------------- */

// Token rotation (Cookie-based)
router.post('/refresh', userController.refreshToken);

// Session termination
router.post('/logout', protect, userController.logout);

/* ---------------------------------------------------------------------------
   6. PROTECTED IDENTITY
   --------------------------------------------------------------------------- */

// Return the current Sovereign Context
router.get('/me', protect, userController.getMe);

/* ---------------------------------------------------------------------------
   SOVEREIGN EXPORT
   --------------------------------------------------------------------------- */
module.exports = router;

/**
 * ARCHITECTURAL FINALITY:
 * This route file provides the primary defense for Wilsy OS. By verifying
 * controller integrity at boot, we ensure the "Diamond Standard" of uptime.
 */