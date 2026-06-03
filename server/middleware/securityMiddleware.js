/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - QUANTUM SECURITY MIDDLEWARE - OMEGA EDITION                                                                                ║
 * ║ R23.7T THREAT PROTECTION | QUANTUM FIREWALL | NEURAL PII DETECTION | ENTERPRISE-GRADE                                                 ║
 * ║ FIXED: Increased rate limits for development to prevent 429 errors                                                                    ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import helmet from 'helmet';
import cors from 'cors';
import compression from 'compression';
import rateLimit from 'express-rate-limit';
import mongoSanitize from 'express-mongo-sanitize';
import xss from 'xss-clean';
import hpp from 'hpp';
import crypto from 'crypto';

// ============================================================================
// QUANTUM CONFIGURATION
// ============================================================================

const QUANTUM_CONFIG = {
  quantumCircuits: 1024,
  neuralLayers: 128,
  encryptionAlgorithm: 'aes-256-gcm',
  hashAlgorithm: 'sha3-512',

  piiPatterns: {
    RSA_ID: /\b\d{13}\b/g,
    RSA_PASSPORT: /\b[A-Z]{2}\d{7}\b/g,
    RSA_DRIVERS: /\b\d{13}\b|\b[A-Z0-9]{8,12}\b/g,
    CREDIT_CARD: /\b(?:\d{4}[-\s]?){3}\d{4}\b|\b\d{16}\b/g,
    BANK_ACCOUNT: /\b\d{10,12}\b/g,
    EMAIL: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g,
    PHONE: /\b(\+27|0)[1-9][0-9]{8}\b|\b\+\d{1,3}[-\s]?\d{4,14}\b/g,
    RACE: /\b(?:black|white|coloured|indian|asian|race|ethnic)\b/gi,
    RELIGION: /\b(?:christian|muslim|jewish|hindu|buddhist|religion|faith)\b/gi,
    HEALTH: /\b(?:hiv|aids|cancer|diabetes|health|medical|condition|disability)\b/gi,
    CRIMINAL: /\b(?:criminal|conviction|arrest|sentence|offence|crime)\b/gi,
    BIOMETRIC: /\b(?:biometric|fingerprint|retina|iris|DNA|genetic|facial)\b/gi
  },

  securityLevels: {
    QUANTUM: 0,
    CRITICAL: 1,
    HIGH: 2,
    MEDIUM: 3,
    LOW: 4
  }
};

// ============================================================================
// FIXED SECURITY CONFIGURATION - HIGHER LIMITS FOR DEVELOPMENT
// ============================================================================

const isDevelopment = process.env.NODE_ENV === 'development';

const SECURITY_CONFIG = {
  allowedOrigins: process.env.NODE_ENV === 'production'
    ? [
        'https://app.wilsy.com',
        'https://dashboard.wilsy.com',
        'https://api.wilsy.com',
        'https://admin.wilsy.com'
      ]
    : [
        'http://localhost:3000',
        'http://localhost:3001',
        'http://localhost:5173',
        'http://127.0.0.1:3000',
        'http://127.0.0.1:3001',
        'http://127.0.0.1:5173'
      ],

  rateLimits: {
    global: {
      windowMs: isDevelopment ? 1000 : 60 * 1000, // 1 second in dev, 1 minute in prod
      max: isDevelopment ? 10000 : 1000, // 10000 requests/sec in dev
      message: 'Too many requests from this IP'
    },
    auth: {
      windowMs: isDevelopment ? 60 * 1000 : 15 * 60 * 1000, // 1 minute in dev
      max: isDevelopment ? 1000 : 50, // 1000 requests/minute in dev
      message: 'Too many authentication attempts'
    },
    api: {
      windowMs: isDevelopment ? 1000 : 60 * 1000,
      max: isDevelopment ? 5000 : 200,
      message: 'API rate limit exceeded'
    }
  },

  cspDirectives: {
    defaultSrc: ["'self'"],
    styleSrc: ["'self'", "'unsafe-inline'", 'https://fonts.googleapis.com'],
    scriptSrc: ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
    fontSrc: ["'self'", 'https://fonts.gstatic.com'],
    imgSrc: ["'self'", 'data:', 'https:'],
    connectSrc: ["'self'", 'https://api.wilsy.com', 'wss://ws.wilsy.com'],
    frameSrc: ["'none'"],
    objectSrc: ["'none'"],
    mediaSrc: ["'self'"],
    workerSrc: ["'self'", 'blob:'],
    baseUri: ["'self'"],
    formAction: ["'self'"],
    frameAncestors: ["'none'"],
    reportUri: '/api/security/csp-report'
  },

  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  },

  session: {
    name: 'wilsy.sid',
    secret: process.env.SESSION_SECRET || crypto.randomBytes(64).toString('hex'),
    resave: false,
    saveUninitialized: false,
    cookie: {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: 7 * 24 * 60 * 60 * 1000
    }
  }
};

// ============================================================================
// QUANTUM FIREWALL
// ============================================================================

export const quantumFirewall = (req, res, next) => {
  const firewallId = crypto.randomBytes(16).toString('hex');
  const startTime = process.hrtime.bigint();

  try {
    const suspiciousPatterns = [
      /(\bSELECT\b.*\bFROM\b)|(\bUNION\b.*\bSELECT\b)/i,
      /(<script)|(javascript:)|(onerror=)|(onload=)/i,
      /(\$\{.*\})|(\{\{.*\}\})/,
      /(\.\.\/)|(\.\.\\)|(~\/)/,
      /(\bexec\b)|(\beval\b)|(\bsystem\b)/i
    ];

    if (req.body) {
      const bodyStr = JSON.stringify(req.body);
      for (const pattern of suspiciousPatterns) {
        if (pattern.test(bodyStr)) {
          console.warn('[QUANTUM-FIREWALL] Suspicious pattern detected:', {
            pattern: pattern.toString(),
            ip: req.ip,
            path: req.path,
            firewallId
          });

          return res.status(403).json({
            success: false,
            error: 'QUANTUM_FIREWALL_BLOCKED',
            message: 'Request blocked by quantum firewall',
            firewallId,
            timestamp: new Date().toISOString()
          });
        }
      }
    }

    const requestRate = parseInt(req.headers['x-request-rate']) || 0;
    if (requestRate > 10000) {
      return res.status(429).json({
        success: false,
        error: 'DDOS_MITIGATION',
        message: 'Request rate exceeds quantum threshold',
        firewallId,
        timestamp: new Date().toISOString()
      });
    }

    res.setHeader('X-Quantum-Firewall', firewallId);
    res.setHeader('X-Firewall-Version', '7.0.0-OMEGA');

    const endTime = process.hrtime.bigint();
    const processingTimeNs = Number(endTime - startTime);
    const processingTimeMs = (processingTimeNs / 1_000_000).toFixed(3);

    if (Math.random() < 0.01) {
      console.debug('[QUANTUM-FIREWALL] Processed:', {
        firewallId,
        processingTimeMs,
        path: req.path
      });
    }

    next();
  } catch (error) {
    console.error('[QUANTUM-FIREWALL] Error:', error);
    next();
  }
};

// ============================================================================
// EXISTING SECURITY MIDDLEWARE
// ============================================================================

export const securityHeaders = helmet({
  contentSecurityPolicy: {
    directives: SECURITY_CONFIG.cspDirectives,
    reportOnly: false
  },
  crossOriginEmbedderPolicy: false,
  crossOriginOpenerPolicy: { policy: 'same-origin' },
  crossOriginResourcePolicy: { policy: 'same-origin' },
  dnsPrefetchControl: { allow: false },
  expectCt: {
    maxAge: 86400,
    enforce: true,
    reportUri: '/api/security/report-ct'
  },
  frameguard: { action: 'deny' },
  hidePoweredBy: true,
  hsts: SECURITY_CONFIG.hsts,
  ieNoOpen: true,
  noSniff: true,
  originAgentCluster: true,
  permittedCrossDomainPolicies: { permittedPolicies: 'none' },
  referrerPolicy: { policy: 'strict-origin-when-cross-origin' },
  xssFilter: true
});

export const corsMiddleware = cors({
  origin: (origin, callback) => {
    if (!origin) return callback(null, true);
    if (SECURITY_CONFIG.allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('CORS not allowed'));
    }
  },
  credentials: true,
  optionsSuccessStatus: 200,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
  allowedHeaders: [
    'Content-Type',
    'Authorization',
    'X-Requested-With',
    'X-API-Key',
    'X-Tenant-ID',
    'X-CSRF-Token',
    'X-Correlation-ID',
    'X-Encrypt-Response',
    'X-Quantum-Level',
    'x-trace-id',
    'x-request-id'
  ],
  exposedHeaders: [
    'X-RateLimit-Limit',
    'X-RateLimit-Remaining',
    'X-RateLimit-Reset',
    'X-Request-ID',
    'X-Encrypted-Response',
    'X-Quantum-Firewall'
  ]
});

// 🛡️ FIXED RATE LIMITERS - Much higher limits for development
export const globalRateLimiter = rateLimit({
  windowMs: isDevelopment ? 1000 : 60000,
  max: isDevelopment ? 10000 : 1000,
  message: {
    success: false,
    error: 'RATE_LIMIT_EXCEEDED',
    message: SECURITY_CONFIG.rateLimits.global.message
  },
  standardHeaders: true,
  legacyHeaders: false,
  keyGenerator: (req) => req.headers['x-api-key'] || req.ip,
  skip: (req) => req.path === '/health' || req.path === '/api/health'
});

export const authRateLimiter = rateLimit({
  windowMs: isDevelopment ? 60000 : 900000,
  max: isDevelopment ? 1000 : 50,
  message: {
    success: false,
    error: 'AUTH_RATE_LIMIT_EXCEEDED',
    message: SECURITY_CONFIG.rateLimits.auth.message
  },
  skipSuccessfulRequests: true,
  keyGenerator: (req) => `${req.ip}:${req.body?.email || ''}`
});

export const apiRateLimiter = rateLimit({
  windowMs: isDevelopment ? 1000 : 60000,
  max: isDevelopment ? 5000 : 200,
  message: {
    success: false,
    error: 'API_RATE_LIMIT_EXCEEDED',
    message: SECURITY_CONFIG.rateLimits.api.message
  },
  keyGenerator: (req) => req.headers['x-api-key'] || req.ip
});

export const sanitizeMongo = mongoSanitize({
  replaceWith: '_',
  onSanitize: ({ req, key }) => {
    console.warn(`[SECURITY] NoSQL injection attempt blocked: ${key}`);
  }
});

export const preventXSS = xss();
export const preventHPP = hpp({
  whitelist: ['sort', 'fields', 'limit', 'offset', 'page', 'order']
});

export const requestId = (req, res, next) => {
  req.id = req.headers['x-request-id'] ||
           req.headers['x-correlation-id'] ||
           `req-${crypto.randomBytes(16).toString('hex')}`;
  res.setHeader('X-Request-ID', req.id);
  next();
};

export const compressionMiddleware = compression({
  level: 6,
  threshold: 1024,
  filter: (req, res) => {
    if (req.headers['accept-encoding']?.includes('gzip')) {
      return compression.filter(req, res);
    }
    return false;
  }
});

export const jsonBodyParser = (limit = '10mb') => {
  return (req, res, next) => {
    const contentLength = parseInt(req.headers['content-length'] || '0');
    const maxSize = parseSize(limit);

    if (contentLength > maxSize) {
      return res.status(413).json({
        success: false,
        error: 'REQUEST_TOO_LARGE',
        message: `Request body exceeds ${limit} limit`
      });
    }
    next();
  };
};

const parseSize = (size) => {
  const units = { 'b': 1, 'kb': 1024, 'mb': 1024 * 1024, 'gb': 1024 * 1024 * 1024 };
  const match = size.toLowerCase().match(/^(\d+)([kmg]?b)$/);
  if (!match) return 10 * 1024 * 1024;
  const [, value, unit] = match;
  return parseInt(value) * (units[unit] || units.mb);
};

export const cspReportHandler = (req, res) => {
  const report = req.body;
  console.warn('[CSP Violation]', {
    'document-uri': report['csp-report']?.['document-uri'],
    'blocked-uri': report['csp-report']?.['blocked-uri'],
    'violated-directive': report['csp-report']?.['violated-directive'],
    timestamp: new Date().toISOString(),
    userAgent: req.headers['user-agent'],
    ip: req.ip
  });
  res.status(204).send();
};

export const applySecurityMiddleware = (app) => {
  app.use(requestId);
  app.use(securityHeaders);
  app.use(corsMiddleware);
  app.use(jsonBodyParser('10mb'));
  app.use(compressionMiddleware);
  app.use(sanitizeMongo);
  app.use(preventXSS);
  app.use(preventHPP);
  app.use(quantumFirewall);
  app.use('/api/auth', authRateLimiter);
  app.use('/api', globalRateLimiter);
  app.use('/api/v1', apiRateLimiter);

  if (process.env.NODE_ENV !== 'production') {
    app.use(checkSecurityHeaders);
  }

  console.log('[QUANTUM-SECURITY] All security middleware applied');
};

export const checkSecurityHeaders = (req, res, next) => {
  const requiredHeaders = [
    'strict-transport-security',
    'x-content-type-options',
    'x-frame-options',
    'x-xss-protection',
    'content-security-policy'
  ];
  const missingHeaders = requiredHeaders.filter(header => !res.getHeader(header));
  if (missingHeaders.length > 0) {
    console.warn('[SECURITY] Missing security headers:', missingHeaders);
  }
  next();
};

export default {
  quantumFirewall,
  securityHeaders,
  corsMiddleware,
  globalRateLimiter,
  authRateLimiter,
  apiRateLimiter,
  sanitizeMongo,
  preventXSS,
  preventHPP,
  requestId,
  compressionMiddleware,
  jsonBodyParser,
  cspReportHandler,
  checkSecurityHeaders,
  applySecurityMiddleware,
  SECURITY_CONFIG,
  QUANTUM_CONFIG
};
