/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - LEGAL SECURITY MIDDLEWARE v1.0                                 ║
 * ║ [Production Grade | POPIA Compliant | Request/Response Security]         ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 * 
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/middleware/legal-security/security.js
 * VERSION: 1.0.0
 * CREATED: 2026-02-24
 * 
 * PURPOSE:
 * • Security middleware for all HTTP requests
 * • POPIA §19 security safeguards enforcement
 * • Request validation and sanitization
 * • Response header security
 * • Rate limiting and brute force protection
 * 
 * DEPENDENCIES:
 * • express - HTTP server framework
 * • helmet - Security headers
 * • cors - Cross-origin resource sharing
 * • express-rate-limit - Rate limiting
 * • xss-clean - XSS protection
 * • hpp - HTTP parameter pollution protection
 * • express-mongo-sanitize - NoSQL injection prevention
 */

import helmet from 'helmet';
import cors from 'cors';
import rateLimit from 'express-rate-limit';
import xss from 'xss-clean';
import hpp from 'hpp';
import mongoSanitize from 'express-mongo-sanitize';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import crypto from 'crypto';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

/**
 * Security Headers Configuration
 * Implements OWASP recommended security headers
 */
const securityHeaders = helmet({
    contentSecurityPolicy: {
        directives: {
            defaultSrc: ["'self'"],
            styleSrc: ["'self'", "'unsafe-inline'"],
            scriptSrc: ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
            imgSrc: ["'self'", "data:", "https:"],
            connectSrc: ["'self'"],
            fontSrc: ["'self'"],
            objectSrc: ["'none'"],
            mediaSrc: ["'self'"],
            frameSrc: ["'none'"],
            upgradeInsecureRequests: []
        }
    },
    hsts: {
        maxAge: 31536000,
        includeSubDomains: true,
        preload: true
    },
    referrerPolicy: {
        policy: 'strict-origin-when-cross-origin'
    },
    noSniff: true,
    ieNoOpen: true,
    xssFilter: true,
    hidePoweredBy: true
});

/**
 * CORS Configuration
 * Restrict cross-origin requests to trusted domains
 */
const corsOptions = {
    origin: function (origin, callback) {
        const allowedOrigins = [
            'https://app.wilsyos.com',
            'https://api.wilsyos.com',
            'https://admin.wilsyos.com',
            'http://localhost:3000',
            'http://localhost:3001'
        ];

        // Allow requests with no origin (like mobile apps or curl)
        if (!origin || allowedOrigins.indexOf(origin) !== -1) {
            callback(null, true);
        } else {
            callback(new Error('CORS policy violation'), false);
        }
    },
    credentials: true,
    optionsSuccessStatus: 200,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
    allowedHeaders: [
        'Content-Type',
        'Authorization',
        'X-Requested-With',
        'X-Request-ID',
        'X-Tenant-ID',
        'X-Correlation-ID'
    ],
    exposedHeaders: [
        'X-Request-ID',
        'X-RateLimit-Limit',
        'X-RateLimit-Remaining',
        'X-RateLimit-Reset'
    ],
    maxAge: 86400 // 24 hours
};

/**
 * Rate Limiting Configuration
 * Protects against brute force and DoS attacks
 */
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // Limit each IP to 100 requests per windowMs
    message: {
        error: 'Too many requests',
        message: 'Rate limit exceeded. Please try again later.',
        retryAfter: '15 minutes'
    },
    standardHeaders: true, // Return rate limit info in headers
    legacyHeaders: false, // Disable deprecated headers
    keyGenerator: (req) => {
        // Use IP address as key, but also consider tenant ID for multi-tenant
        return req.headers['x-forwarded-for'] || req.ip || req.connection?.remoteAddress || 'unknown';
    },
    skip: (req) => {
        // Skip rate limiting for health checks and internal services
        return req.path === '/health' || req.path === '/live' || req.path === '/ready';
    }
});

/**
 * Strict Rate Limiter for Authentication Endpoints
 * More aggressive limits for auth routes
 */
const authLimiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 10, // Limit each IP to 10 auth requests per windowMs
    message: {
        error: 'Too many authentication attempts',
        message: 'Rate limit exceeded. Please try again later.',
        retryAfter: '15 minutes'
    },
    standardHeaders: true,
    legacyHeaders: false,
    skipSuccessfulRequests: true // Don't count successful logins
});

/**
 * API Rate Limiter for High-Traffic Endpoints
 */
const apiLimiter = rateLimit({
    windowMs: 60 * 1000, // 1 minute
    max: 60, // 60 requests per minute
    message: {
        error: 'API rate limit exceeded',
        message: 'Please slow down your requests.',
        retryAfter: '60 seconds'
    },
    standardHeaders: true,
    legacyHeaders: false
});

/**
 * Generate security headers for response
 */
const setSecurityHeaders = (req, res, next) => {
    // Additional security headers beyond helmet
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('X-Frame-Options', 'DENY');
    res.setHeader('X-XSS-Protection', '1; mode=block');
    res.setHeader('Permissions-Policy', 'geolocation=(), microphone=(), camera=()');

    // Cache control for sensitive endpoints
    if (req.path.startsWith('/api') && req.method === 'GET') {
        res.setHeader('Cache-Control', 'private, no-cache, no-store, must-revalidate');
        res.setHeader('Pragma', 'no-cache');
        res.setHeader('Expires', '0');
    }

    next();
};

/**
 * Request ID middleware
 * Adds unique ID to each request for tracing
 */
const requestId = (req, res, next) => {
    req.id = req.headers['x-request-id'] ||
        req.headers['x-correlation-id'] ||
        crypto.randomBytes(16).toString('hex');

    res.setHeader('x-request-id', req.id);
    next();
};

/**
 * Request sanitization
 * Removes any malicious content from requests
 */
const sanitizeRequest = (req, res, next) => {
    // Sanitize query parameters
    if (req.query) {
        Object.keys(req.query).forEach(key => {
            if (typeof req.query[key] === 'string') {
                req.query[key] = req.query[key].replace(/[<>$]/g, '');
            }
        });
    }

    // Sanitize body
    if (req.body && typeof req.body === 'object') {
        // xss-clean will handle this, but we add additional checks
        const bodyString = JSON.stringify(req.body);
        if (bodyString.includes('__proto__') || bodyString.includes('constructor')) {
            return res.status(400).json({
                error: 'Bad request',
                message: 'Invalid request body'
            });
        }
    }

    next();
};

/**
 * Validate content type
 * Ensures requests have proper content-type headers
 */
const validateContentType = (req, res, next) => {
    if (req.method === 'POST' || req.method === 'PUT' || req.method === 'PATCH') {
        const contentType = req.headers['content-type'];

        if (!contentType || !contentType.includes('application/json')) {
            return res.status(415).json({
                error: 'Unsupported Media Type',
                message: 'Content-Type must be application/json'
            });
        }
    }

    next();
};

/**
 * SQL injection prevention
 * Basic SQL injection pattern detection
 */
const preventSQLInjection = (req, res, next) => {
    const sqlPatterns = [
        /(\bSELECT\b.*\bFROM\b)/i,
        /(\bINSERT\b.*\bINTO\b)/i,
        /(\bUPDATE\b.*\bSET\b)/i,
        /(\bDELETE\b.*\bFROM\b)/i,
        /(\bDROP\b.*\bTABLE\b)/i,
        /(\bUNION\b.*\bSELECT\b)/i,
        /(--)/,
        /(;\s*DROP)/i,
        /(\bOR\b.*=.*\bOR\b)/i
    ];

    const checkValue = (value) => {
        if (typeof value === 'string') {
            for (const pattern of sqlPatterns) {
                if (pattern.test(value)) {
                    return true;
                }
            }
        }
        return false;
    };

    // Check query parameters
    if (req.query) {
        for (const value of Object.values(req.query)) {
            if (checkValue(value)) {
                return res.status(400).json({
                    error: 'Bad request',
                    message: 'Invalid query parameters'
                });
            }
        }
    }

    // Check body
    if (req.body && typeof req.body === 'object') {
        const bodyStr = JSON.stringify(req.body);
        for (const pattern of sqlPatterns) {
            if (pattern.test(bodyStr)) {
                return res.status(400).json({
                    error: 'Bad request',
                    message: 'Invalid request body'
                });
            }
        }
    }

    next();
};

/**
 * Export all security middleware
 */
export default {
    // Core security middleware
    securityHeaders,
    cors: cors(corsOptions),
    limiter,
    authLimiter,
    apiLimiter,

    // Request processing middleware
    requestId,
    sanitizeRequest,
    validateContentType,
    preventSQLInjection,
    setSecurityHeaders,

    // Third-party security middleware
    xss: xss(),
    hpp: hpp(),
    mongoSanitize: mongoSanitize({
        allowDots: true,
        replaceWith: '_',
        onSanitize: ({ req, key }) => {
            console.warn(`Sanitized ${key} from request to ${req.path}`);
        }
    }),

    // Combined middleware for easy application
    all: [
        requestId,
        securityHeaders,
        cors(corsOptions),
        setSecurityHeaders,
        validateContentType,
        mongoSanitize({
            allowDots: true,
            replaceWith: '_'
        }),
        xss(),
        hpp(),
        sanitizeRequest,
        preventSQLInjection
    ],

    // Route-specific middleware
    forRoutes: {
        auth: [authLimiter, validateContentType],
        api: [apiLimiter],
        public: [limiter]
    }
};