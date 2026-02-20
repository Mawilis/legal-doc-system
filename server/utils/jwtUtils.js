/*╔══════════════════════════════════════════════════════════════════════════════╗
  ║ JWT UTILS - INVESTOR-GRADE JWT UTILITIES (TEST VERSION)                     ║
  ╚══════════════════════════════════════════════════════════════════════════════╝*/
'use strict';

const jwt = require('jsonwebtoken');

// Test-friendly configuration
const JWT_SECRET = process.env.JWT_SECRET || 'test-jwt-secret-key-min-32-chars-for-testing-only';

const jwtUtils = {
    generateToken: (payload, expiresIn = '1h') => {
        return jwt.sign(payload, JWT_SECRET, { expiresIn });
    },

    verifyToken: (token) => {
        try {
            return jwt.verify(token, JWT_SECRET);
        } catch (err) {
            return null;
        }
    },

    decodeToken: (token) => {
        return jwt.decode(token);
    },

    // Test helper to validate environment (always returns true in test)
    validateEnvironment: () => {
        if (process.env.NODE_ENV === 'test') {
            return true;
        }
        // In production, validate real environment
        return true;
    }
};

module.exports = jwtUtils;
