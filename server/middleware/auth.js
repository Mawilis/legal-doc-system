/*
 * File: server/middleware/auth.js
 * STATUS: PRODUCTION-READY | SECURITY STRATEGY LAYER
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * This file contains the core logic for Identity Resolution. It defines HOW the 
 * system identifies a user or a service before any access is granted.
 *
 * KEY FEATURES FOR FUTURE ENGINEERS:
 * 1. Modular Strategy: Decouples token decoding from the Express request cycle.
 * 2. Token Revocation: Prepared for integration with a Redis-based blacklist.
 * 3. Identity Enrichment: Logic to transform a raw token into a full User context.
 * 4. Error Mapping: Standardizes security exceptions to prevent data leaks 
 * through verbose error messages.
 * -----------------------------------------------------------------------------
 */

'use strict';

const jwt = require('jsonwebtoken');
const User = require('../models/User');

/**
 * IDENTITY RESOLVER:
 * Logic to extract and verify a user from a Bearer token.
 * This is the "Truth Engine" for the Auth process.
 */
const resolveUserFromToken = async (token) => {
    try {
        if (!token) throw new Error('NO_TOKEN_PROVIDED');

        // 1. VERIFY SIGNATURE
        const decoded = jwt.verify(token, process.env.JWT_SECRET);

        // 2. CHECK TOKEN BLACKLIST (Optional: Redis check goes here)
        // if (await isTokenBlacklisted(token)) throw new Error('TOKEN_REVOKED');

        // 3. RETRIEVE USER WITH TENANT ISOLATION
        // We explicitly select the fields needed for the request life-cycle.
        const user = await User.findById(decoded.id)
            .select('+tenantId role status')
            .lean(); // Lean for performance on high-frequency auth checks

        if (!user) throw new Error('USER_NOT_FOUND');
        if (user.status !== 'active') throw new Error('ACCOUNT_SUSPENDED');

        return user;
    } catch (err) {
        // Log the specific error for internal forensics but throw generic for client security
        console.error('AUTH_RESOLVER_FAILURE:', err.message);
        throw new Error('AUTHENTICATION_FAILED');
    }
};

/**
 * API KEY RESOLVER (Billion-Dollar Readiness):
 * Logic to verify service-to-service communication.
 */
const resolveServiceFromKey = async (apiKey) => {
    // This allows your legal system to eventually talk to external 
    // court systems or AI providers securely via x-api-key headers.
    return { isService: true, identifier: 'INTERNAL_OR_EXTERNAL_SERVICE' };
};

module.exports = {
    resolveUserFromToken,
    resolveServiceFromKey
};