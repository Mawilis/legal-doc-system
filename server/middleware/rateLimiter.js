#!/* eslint-disable */
/* ╔═══════════════════════════════════════════════════════════════════════════╗
  ║ WILSY OS - RATE LIMITER MIDDLEWARE                                        ║
  ║ Protects API from abuse | DDoS prevention | Production grade             ║
  ╚═══════════════════════════════════════════════════════════════════════════╝ */

import rateLimit from 'express-rate-limit';

/**
 * General API rate limiter
 * 100 requests per 15 minutes per IP
 */
export const rateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per windowMs
  message: {
    error: 'Too many requests, please try again later.',
    retryAfter: '15 minutes',
    code: 'RATE_LIMIT_EXCEEDED',
  },
  standardHeaders: true,
  legacyHeaders: false,
  skip: (req) =>
    // Skip rate limiting for health checks
    req.path === '/health' || req.path.startsWith('/health/')
  ,
});

/**
 * Strict rate limiter for sensitive endpoints
 * 10 requests per hour per IP
 */
export const strictLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 10,
  message: {
    error: 'Too many requests to this endpoint.',
    retryAfter: '1 hour',
    code: 'STRICT_RATE_LIMIT_EXCEEDED',
  },
  standardHeaders: true,
  legacyHeaders: false,
});

/**
 * Auth rate limiter for login/register endpoints
 * 5 requests per 15 minutes per IP
 */
export const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5,
  message: {
    error: 'Too many authentication attempts.',
    retryAfter: '15 minutes',
    code: 'AUTH_RATE_LIMIT_EXCEEDED',
  },
  standardHeaders: true,
  legacyHeaders: false,
});

export default rateLimiter;
