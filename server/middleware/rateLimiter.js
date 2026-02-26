/**
 * Rate Limiter Middleware
 * Protects API endpoints from abuse using express-rate-limit
 */

import rateLimit from 'express-rate-limit.js';

export const rateLimiter = (limits) => rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: (req) => {
    // Higher limits for authenticated users
    if (req.headers.authorization || req.headers['x-api-key']) {
      return limits?.authenticated || 1000;
    }
    return limits?.unauthenticated || 100;
  },
  standardHeaders: true,
  legacyHeaders: false,
  keyGenerator: (req) => req.headers['x-api-key'] || req.ip || 'unknown',
  handler: (req, res) => {
    res.status(429).json({
      success: false,
      error: {
        code: 'RATE_LIMIT_EXCEEDED',
        message: 'Too many requests, please try again later.',
        requestId: req.requestId,
        timestamp: new Date().toISOString(),
      },
    });
  },
});

export default rateLimiter;
