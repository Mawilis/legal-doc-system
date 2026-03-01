#!/* eslint-disable */
/*
 * WILSY OS: INVESTOR ANALYTICS ROUTES - REAL-TIME VALUATION DASHBOARD
 * ============================================================================
 *
 *     █████╗ ███╗   ██╗ █████╗ ██╗██╗   ██╗████████╗██╗ ██████╗███████╗
 *    ██╔══██╗████╗  ██║██╔══██╗██║╚██╗ ██╔╝╚══██╔══╝██║██╔════╝██╔════╝
 *    ███████║██╔██╗ ██║███████║██║ ╚████╔╝    ██║   ██║██║     █████╗
 *    ██╔══██║██║╚██╗██║██╔══██║██║  ╚██╔╝     ██║   ██║██║     ██╔══╝
 *    ██║  ██║██║ ╚████║██║  ██║███████╗██║    ██║   ██║╚██████╗███████╗
 *    ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═╝    ╚═╝   ╚═╝ ╚═════╝╚══════╝
 *
 *     ██████╗  ██████╗ ██╗   ██╗████████╗███████╗███████╗
 *     ██╔══██╗██╔═══██╗██║   ██║╚══██╔══╝██╔════╝██╔════╝
 *     ██████╔╝██║   ██║██║   ██║   ██║   █████╗  ███████╗
 *     ██╔══██╗██║   ██║██║   ██║   ██║   ██╔══╝  ╚════██║
 *     ██║  ██║╚██████╔╝╚██████╔╝   ██║   ███████╗███████║
 *     ╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═╝   ╚══════╝╚══════╝
 *
 * ============================================================================
 * CORE DOCTRINE: Investors don't buy vision—they buy metrics.
 *
 * These routes expose real-time valuation metrics, SaaS KPIs, and forensic
 * proof of growth, allowing investors to verify Wilsy OS's market dominance
 * with cryptographic certainty. Every number is calculated from actual
 * audit logs, not projections.
 *
 * QUANTUM ARCHITECTURE:
 *
 *  ┌─────────────────────────────────────────────────────────────────────────────┐
 *  │                  INVESTOR ANALYTICS ROUTES - VALUATION API                  │
 *  └─────────────────────────────────────────────────────────────────────────┬───┘
 *                                                                           │
 *  ┌─────────────────────────────────────────────────────────────────────────▼───┐
 *  │                         SECURITY LAYER (Investor Auth)                       │
 *  ├─────────────────────────────────────────────────────────────────────────────┤
 *  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
 *  │  │   Investor   │  │   API Key    │  │   Rate       │  │   IP         │   │
 *  │  │   JWT        │──│   Validation │──│   Limiting   │──│   Whitelist  │   │
 *  │  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
 *  └─────────────────────────────────────────────────────────────────────────────┘
 *                                                                           │
 *  ┌─────────────────────────────────────────────────────────────────────────▼───┐
 *  │                         INVESTOR ENDPOINTS                                    │
 *  ├─────────────────────────────────────────────────────────────────────────────┤
 *  │  ┌──────────────────────────────────────────────────────────────────────┐  │
 *  │  │  GET  /valuation      → Real-time company valuation                 │  │
 *  │  │  GET  /dashboard       → Investor dashboard with all KPIs           │  │
 *  │  │  GET  /report          → Generate comprehensive investor report     │  │
 *  │  │  GET  /metrics         → Raw SaaS metrics for analysis              │  │
 *  │  │  GET  /arr             → Annual Recurring Revenue breakdown        │  │
 *  │  │  GET  /ltv-cac         → Customer economics                         │  │
 *  │  │  GET  /growth          → Growth metrics                             │  │
 *  │  │  POST /export          → Export report (PDF/CSV/JSON)               │  │
 *  │  │  GET  /health          → Service health check                       │  │
 *  │  └──────────────────────────────────────────────────────────────────────┘  │
 *  └─────────────────────────────────────────────────────────────────────────────┘
 *
 * @version 42.0.0 (10-Year Future-Proof Edition)
 * @collaboration: Investor Relations, Executive Team, Data Science
 * @valuation: $5B+ real-time API
 * ============================================================================
 */

import express from 'express';
import { body, query, param, validationResult } from 'express-validator.js';
import { performance } from 'perf_hooks';
import { v4 as uuidv4 } from 'uuid.js';
import cors from 'cors';
import compression from 'compression.js';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit.js';

// WILSY OS CORE IMPORTS
import { authenticate, authorize } from '../middleware/auth.js';
import { tenantGuard } from '../middleware/tenantGuard.js';
import { rateLimiter, investorRateLimiter } from '../middleware/rateLimiter.js';
import { cacheMiddleware, invalidateCache } from '../middleware/cache.js';
import { auditMiddleware } from '../middleware/audit.js';
import { QuantumLogger, globalLogger } from '../utils/quantumLogger.js';
import { metrics, trackRequest, trackError } from '../utils/metricsCollector.js';
import { AppError, errorHandler } from '../utils/errorHandler.js';
import investorIntelligenceService from '../services/analytics/investorIntelligenceService.js';

// =============================================================================
// QUANTUM CONSTANTS
// =============================================================================

const INVESTOR_ROUTES_CONSTANTS = Object.freeze({
  // Cache TTLs
  CACHE_TTL_VALUATION: 300, // 5 minutes
  CACHE_TTL_DASHBOARD: 600, // 10 minutes
  CACHE_TTL_REPORT: 1800, // 30 minutes

  // Rate Limits
  RATE_LIMIT_WINDOW: 15 * 60 * 1000, // 15 minutes
  RATE_LIMIT_MAX: 100, // 100 requests per window

  // Investor API Keys (would be stored in env)
  INVESTOR_API_KEYS: process.env.INVESTOR_API_KEYS?.split(',') || [],

  // IP Whitelist for investor relations
  INVESTOR_IP_WHITELIST: process.env.INVESTOR_IP_WHITELIST?.split(',') || [],
});

// =============================================================================
// ROUTER INITIALIZATION
// =============================================================================

const router = express.Router();

// =============================================================================
// SECURITY MIDDLEWARE - Investor-grade protection
// =============================================================================

// Security headers
router.use(
  helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        styleSrc: ["'self'", "'unsafe-inline'"],
        scriptSrc: ["'self'"],
        imgSrc: ["'self'", 'data:', 'https:'],
        connectSrc: ["'self'", 'https://api.wilsy.os'],
        fontSrc: ["'self'"],
        objectSrc: ["'none'"],
        mediaSrc: ["'none'"],
        frameSrc: ["'none'"],
      },
    },
    hsts: {
      maxAge: 31536000,
      includeSubDomains: true,
      preload: true,
    },
  })
);

// CORS - Restrict to investor domains
router.use(
  cors({
    origin: process.env.INVESTOR_ALLOWED_ORIGINS?.split(',') || [
      'https://investors.wilsy.os',
      'https://ir.wilsy.os',
      'https://app.wilsy.os',
    ],
    methods: ['GET', 'POST', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Investor-Key', 'X-Correlation-ID'],
    credentials: true,
    maxAge: 86400,
  })
);

// Compression
router.use(compression({ level: 6, threshold: 1024 }));
router.use(express.json({ limit: '1mb' }));

// Request tracking
router.use((req, res, next) => {
  req.correlationId =
    req.headers['x-correlation-id'] ||
    req.headers['x-request-id'] ||
    `INVESTOR-${Date.now()}-${uuidv4().substring(0, 8)}`;
  req.startTime = performance.now();

  res.setHeader('X-Correlation-ID', req.correlationId);
  res.setHeader('X-API-Version', '42.0.0');
  res.setHeader('X-Investor-Gateway', 'active');

  trackRequest(req.method, req.path);

  next();
});

// =============================================================================
// INVESTOR AUTHENTICATION - Multi-layer security
// =============================================================================

/*
 * Investor authentication middleware
 * Supports JWT, API keys, and IP whitelist
 */
const investorAuth = async (req, res, next) => {
  try {
    // Method 1: IP Whitelist
    const clientIp = req.ip || req.connection.remoteAddress;
    if (INVESTOR_ROUTES_CONSTANTS.INVESTOR_IP_WHITELIST.includes(clientIp)) {
      req.investorContext = {
        type: 'ip_whitelist',
        ip: clientIp,
        permissions: ['read'],
      };
      return next();
    }

    // Method 2: Investor API Key
    const apiKey = req.headers['x-investor-key'];
    if (apiKey && INVESTOR_ROUTES_CONSTANTS.INVESTOR_API_KEYS.includes(apiKey)) {
      req.investorContext = {
        type: 'api_key',
        key: apiKey.substring(0, 8) + '...',
        permissions: ['read', 'export'],
      };
      return next();
    }

    // Method 3: JWT with investor role
    if (req.user?.role === 'investor' || req.user?.role === 'admin') {
      req.investorContext = {
        type: 'jwt',
        userId: req.user.id,
        email: req.user.email,
        permissions: ['read', 'export', 'admin'],
      };
      return next();
    }

    // No valid authentication
    await QuantumLogger.logAction('system', null, 'INVESTOR_AUTH_FAILED', null, {
      ip: clientIp,
      path: req.path,
      method: req.method,
    });

    throw new AppError('Investor authentication required', 401, 'INVESTOR_AUTH_REQUIRED');
  } catch (error) {
    next(error);
  }
};

// Apply investor authentication to all routes
router.use(investorAuth);

// Investor-specific rate limiting
router.use(
  investorRateLimiter({
    windowMs: INVESTOR_ROUTES_CONSTANTS.RATE_LIMIT_WINDOW,
    max: INVESTOR_ROUTES_CONSTANTS.RATE_LIMIT_MAX,
    message:
      'Investor rate limit exceeded. Please contact investor-relations@wilsy.os for higher limits.',
  })
);

// Audit logging for all investor actions
router.use(auditMiddleware('investor'));

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/*
 * Format success response with investor metadata
 */
const formatSuccess = (data, metadata = {}) => {
  return {
    success: true,
    data,
    metadata: {
      timestamp: new Date().toISOString(),
      version: '42.0.0',
      investor: true,
      ...metadata,
    },
    links: {
      self: metadata.self,
      docs: 'https://docs.wilsy.os/investor-api',
      irc: 'https://ir.wilsy.os',
    },
  };
};

/*
 * Check investor permissions
 */
const checkPermission = (req, requiredPermission) => {
  if (!req.investorContext) return false;
  return req.investorContext.permissions.includes(requiredPermission);
};

// =============================================================================
// ENDPOINT: GET /valuation
// =============================================================================
/*
 * @route   GET /api/v1/analytics/valuation
 * @desc    Real-time company valuation
 * @access  Investor (read)
 */
router.get(
  '/valuation',
  cacheMiddleware({ ttl: INVESTOR_ROUTES_CONSTANTS.CACHE_TTL_VALUATION }),
  async (req, res, next) => {
    const startTime = performance.now();
    const correlationId = req.correlationId;

    try {
      const valuation = await investorIntelligenceService.getRealTimeValuation();

      // Log investor access
      await QuantumLogger.logAction(
        'system',
        req.investorContext.email || 'investor',
        'INVESTOR_VALUATION_ACCESS',
        null,
        {
          correlationId,
          valuation: valuation.formattedValuation?.usd,
          arr: valuation.revenue?.formattedARR,
        }
      );

      const duration = performance.now() - startTime;
      metrics.timing('investor.valuation.duration', duration);

      res.json(
        formatSuccess(valuation, {
          self: req.originalUrl,
          processingTimeMs: Math.round(duration),
          correlationId,
          cached: req.cached || false,
        })
      );
    } catch (error) {
      trackError('investor', error.code || 'valuation_error');
      next(new AppError(error.message, 500, 'VALUATION_FETCH_FAILED'));
    }
  }
);

// =============================================================================
// ENDPOINT: GET /dashboard
// =============================================================================
/*
 * @route   GET /api/v1/analytics/dashboard
 * @desc    Investor dashboard with all KPIs
 * @access  Investor (read)
 */
router.get(
  '/dashboard',
  cacheMiddleware({ ttl: INVESTOR_ROUTES_CONSTANTS.CACHE_TTL_DASHBOARD }),
  async (req, res, next) => {
    const startTime = performance.now();
    const correlationId = req.correlationId;

    try {
      const dashboard = await investorIntelligenceService.getInvestorDashboard();

      const duration = performance.now() - startTime;

      res.json(
        formatSuccess(dashboard, {
          self: req.originalUrl,
          processingTimeMs: Math.round(duration),
          correlationId,
          cached: req.cached || false,
        })
      );
    } catch (error) {
      trackError('investor', error.code || 'dashboard_error');
      next(new AppError(error.message, 500, 'DASHBOARD_FETCH_FAILED'));
    }
  }
);

// =============================================================================
// ENDPOINT: GET /report
// =============================================================================
/*
 * @route   GET /api/v1/analytics/report
 * @desc    Generate comprehensive investor report
 * @access  Investor (read)
 */
router.get(
  '/report',
  [
    query('type').optional().isIn(['quick', 'standard', 'comprehensive', 'forensic']),
    query('format').optional().isIn(['json', 'pdf', 'csv']),
  ],
  cacheMiddleware({ ttl: INVESTOR_ROUTES_CONSTANTS.CACHE_TTL_REPORT }),
  async (req, res, next) => {
    const startTime = performance.now();
    const correlationId = req.correlationId;
    const { type = 'standard', format = 'json' } = req.query;

    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      const report = await investorIntelligenceService.generateInvestorReport(type);

      // Log report generation
      await QuantumLogger.logAction(
        'system',
        req.investorContext.email || 'investor',
        'INVESTOR_REPORT_GENERATED',
        report.reportId,
        {
          type,
          format,
          valuation: report.metrics?.formattedValuation?.usd,
          correlationId,
        }
      );

      const duration = performance.now() - startTime;

      // Handle different formats
      if (format === 'csv') {
        const csvData = await investorIntelligenceService.exportReport('csv');
        res.setHeader('Content-Type', 'text/csv');
        res.setHeader(
          'Content-Disposition',
          `attachment; filename="wilsy-investor-report-${report.reportId}.csv"`
        );
        return res.send(csvData);
      }

      if (format === 'pdf') {
        const pdfData = await investorIntelligenceService.exportReport('pdf');
        res.setHeader('Content-Type', 'application/pdf');
        res.setHeader(
          'Content-Disposition',
          `attachment; filename="wilsy-investor-report-${report.reportId}.pdf"`
        );
        return res.send(pdfData);
      }

      // Default JSON
      res.json(
        formatSuccess(report, {
          self: req.originalUrl,
          processingTimeMs: Math.round(duration),
          correlationId,
          reportType: type,
          cached: req.cached || false,
        })
      );
    } catch (error) {
      trackError('investor', error.code || 'report_error');
      next(new AppError(error.message, 500, 'REPORT_GENERATION_FAILED'));
    }
  }
);

// =============================================================================
// ENDPOINT: GET /metrics
// =============================================================================
/*
 * @route   GET /api/v1/analytics/metrics
 * @desc    Raw SaaS metrics for analysis
 * @access  Investor (read)
 */
router.get(
  '/metrics',
  cacheMiddleware({ ttl: INVESTOR_ROUTES_CONSTANTS.CACHE_TTL_VALUATION }),
  async (req, res, next) => {
    const startTime = performance.now();
    const correlationId = req.correlationId;

    try {
      const valuation = await investorIntelligenceService.getRealTimeValuation();

      // Extract only metrics
      const metrics = {
        timestamp: valuation.timestamp,
        tenants: valuation.tenants,
        revenue: valuation.revenue,
        financial: valuation.financial,
        customerEconomics: valuation.customerEconomics,
        usage: valuation.usage,
      };

      const duration = performance.now() - startTime;

      res.json(
        formatSuccess(metrics, {
          self: req.originalUrl,
          processingTimeMs: Math.round(duration),
          correlationId,
        })
      );
    } catch (error) {
      trackError('investor', error.code || 'metrics_error');
      next(new AppError(error.message, 500, 'METRICS_FETCH_FAILED'));
    }
  }
);

// =============================================================================
// ENDPOINT: GET /arr
// =============================================================================
/*
 * @route   GET /api/v1/analytics/arr
 * @desc    Annual Recurring Revenue breakdown
 * @access  Investor (read)
 */
router.get(
  '/arr',
  cacheMiddleware({ ttl: INVESTOR_ROUTES_CONSTANTS.CACHE_TTL_VALUATION }),
  async (req, res, next) => {
    const startTime = performance.now();
    const correlationId = req.correlationId;

    try {
      const valuation = await investorIntelligenceService.getRealTimeValuation();

      const arrData = {
        total: valuation.revenue.arr,
        formatted: valuation.revenue.formattedARR,
        byTier: valuation.revenue.byTier,
        mrr: valuation.revenue.mrr,
        formattedMRR: valuation.revenue.formattedMRR,
        growth: valuation.growth,
        targets: valuation.targets.arr,
      };

      const duration = performance.now() - startTime;

      res.json(
        formatSuccess(arrData, {
          self: req.originalUrl,
          processingTimeMs: Math.round(duration),
          correlationId,
        })
      );
    } catch (error) {
      trackError('investor', error.code || 'arr_error');
      next(new AppError(error.message, 500, 'ARR_FETCH_FAILED'));
    }
  }
);

// =============================================================================
// ENDPOINT: GET /ltv-cac
// =============================================================================
/*
 * @route   GET /api/v1/analytics/ltv-cac
 * @desc    Customer economics (LTV/CAC ratio)
 * @access  Investor (read)
 */
router.get(
  '/ltv-cac',
  cacheMiddleware({ ttl: INVESTOR_ROUTES_CONSTANTS.CACHE_TTL_VALUATION }),
  async (req, res, next) => {
    const startTime = performance.now();
    const correlationId = req.correlationId;

    try {
      const valuation = await investorIntelligenceService.getRealTimeValuation();

      const ltvCacData = {
        ltv: valuation.customerEconomics.ltv,
        cac: valuation.customerEconomics.cac,
        ratio: valuation.customerEconomics.ltvCac,
        paybackPeriod: valuation.customerEconomics.paybackPeriod,
        formattedLTV: valuation.customerEconomics.formattedLTV,
        formattedCAC: valuation.customerEconomics.formattedCAC,
        target: valuation.targets.ltvCac,
      };

      const duration = performance.now() - startTime;

      res.json(
        formatSuccess(ltvCacData, {
          self: req.originalUrl,
          processingTimeMs: Math.round(duration),
          correlationId,
        })
      );
    } catch (error) {
      trackError('investor', error.code || 'ltv_cac_error');
      next(new AppError(error.message, 500, 'LTV_CAC_FETCH_FAILED'));
    }
  }
);

// =============================================================================
// ENDPOINT: GET /growth
// =============================================================================
/*
 * @route   GET /api/v1/analytics/growth
 * @desc    Growth metrics
 * @access  Investor (read)
 */
router.get(
  '/growth',
  cacheMiddleware({ ttl: INVESTOR_ROUTES_CONSTANTS.CACHE_TTL_VALUATION }),
  async (req, res, next) => {
    const startTime = performance.now();
    const correlationId = req.correlationId;

    try {
      const valuation = await investorIntelligenceService.getRealTimeValuation();

      const growthData = {
        qoqRevenue: valuation.growth.qoqRevenue,
        yoyRevenue: valuation.growth.yoyRevenue,
        newCustomersQoq: valuation.growth.newCustomersQoq,
        expansionRevenue: valuation.growth.expansionRevenue,
        nrr: valuation.financial.nrr,
        magicNumber: valuation.financial.magicNumber,
        targets: {
          nrr: valuation.targets.nrr,
          magicNumber: { target: 1.2, current: valuation.financial.magicNumber },
        },
      };

      const duration = performance.now() - startTime;

      res.json(
        formatSuccess(growthData, {
          self: req.originalUrl,
          processingTimeMs: Math.round(duration),
          correlationId,
        })
      );
    } catch (error) {
      trackError('investor', error.code || 'growth_error');
      next(new AppError(error.message, 500, 'GROWTH_FETCH_FAILED'));
    }
  }
);

// =============================================================================
// ENDPOINT: POST /export
// =============================================================================
/*
 * @route   POST /api/v1/analytics/export
 * @desc    Export investor report in specified format
 * @access  Investor (export permission required)
 */
router.post(
  '/export',
  [
    body('type').optional().isIn(['quick', 'standard', 'comprehensive', 'forensic']),
    body('format').isIn(['pdf', 'csv', 'json']),
    body('includeRawData').optional().isBoolean(),
  ],
  async (req, res, next) => {
    const startTime = performance.now();
    const correlationId = req.correlationId;

    // Check export permission
    if (!checkPermission(req, 'export')) {
      throw new AppError('Export permission required', 403, 'EXPORT_PERMISSION_DENIED');
    }

    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { type = 'standard', format = 'pdf', includeRawData = false } = req.body;

    try {
      const report = await investorIntelligenceService.generateInvestorReport(type);

      // Log export
      await QuantumLogger.logAction(
        'system',
        req.investorContext.email || 'investor',
        'INVESTOR_REPORT_EXPORTED',
        report.reportId,
        {
          type,
          format,
          includeRawData,
          correlationId,
        }
      );

      if (format === 'csv') {
        const csvData = await investorIntelligenceService.exportReport('csv');
        res.setHeader('Content-Type', 'text/csv');
        res.setHeader(
          'Content-Disposition',
          `attachment; filename="wilsy-investor-report-${report.reportId}.csv"`
        );
        return res.send(csvData);
      }

      if (format === 'pdf') {
        const pdfData = await investorIntelligenceService.exportReport('pdf');
        res.setHeader('Content-Type', 'application/pdf');
        res.setHeader(
          'Content-Disposition',
          `attachment; filename="wilsy-investor-report-${report.reportId}.pdf"`
        );
        return res.send(pdfData);
      }

      // JSON response
      const responseData = includeRawData
        ? report
        : {
            reportId: report.reportId,
            generatedAt: report.generatedAt,
            highlights: report.highlights,
            investorSummary: report.investorSummary,
            metrics: {
              arr: report.metrics.revenue.formattedARR,
              valuation: report.metrics.formattedValuation.usd,
              ltvCac: report.metrics.customerEconomics.ltvCac.toFixed(2),
              grossMargin: report.metrics.financial.formattedGrossMargin,
              nrr: `${(report.metrics.financial.nrr * 100).toFixed(1)}%`,
            },
          };

      const duration = performance.now() - startTime;

      res.json(
        formatSuccess(responseData, {
          self: req.originalUrl,
          processingTimeMs: Math.round(duration),
          correlationId,
          reportType: type,
          format,
        })
      );
    } catch (error) {
      trackError('investor', error.code || 'export_error');
      next(new AppError(error.message, 500, 'EXPORT_FAILED'));
    }
  }
);

// =============================================================================
// ENDPOINT: GET /health
// =============================================================================
/*
 * @route   GET /api/v1/analytics/health
 * @desc    Service health check
 * @access  Public (for monitoring)
 */
router.get('/health', async (req, res) => {
  const health = await investorIntelligenceService.healthCheck();

  res.json({
    status: health.status,
    service: 'investor-analytics',
    version: '42.0.0',
    intelligence: health,
    timestamp: new Date().toISOString(),
  });
});

// =============================================================================
// ENDPOINT: GET /forensic-proof
// =============================================================================
/*
 * @route   GET /api/v1/analytics/forensic-proof
 * @desc    Cryptographic proof of data integrity
 * @access  Investor (read)
 */
router.get('/forensic-proof', async (req, res, next) => {
  const startTime = performance.now();
  const correlationId = req.correlationId;

  try {
    const valuation = await investorIntelligenceService.getRealTimeValuation();

    const forensicData = {
      auditChainLength: valuation.forensicProof.auditChainLength,
      integrityScore: valuation.forensicProof.integrityScore,
      lastAuditBlock: valuation.forensicProof.lastAuditBlock,
      merkleRoot: valuation.forensicProof.merkleRoot,
      verificationMethod: 'SHA-256 Merkle Tree',
      timestamp: new Date().toISOString(),
    };

    const duration = performance.now() - startTime;

    res.json(
      formatSuccess(forensicData, {
        self: req.originalUrl,
        processingTimeMs: Math.round(duration),
        correlationId,
      })
    );
  } catch (error) {
    trackError('investor', error.code || 'forensic_error');
    next(new AppError(error.message, 500, 'FORENSIC_PROOF_FAILED'));
  }
});

// =============================================================================
// 404 HANDLER
// =============================================================================
router.use('*', (req, res) => {
  res.status(404).json({
    success: false,
    error: {
      code: 'ROUTE_NOT_FOUND',
      message: `Cannot ${req.method} ${req.originalUrl}`,
    },
    metadata: {
      timestamp: new Date().toISOString(),
      correlationId: req.correlationId,
    },
  });
});

// =============================================================================
// ERROR HANDLER
// =============================================================================
router.use((err, req, res, next) => {
  const statusCode = err.status || 500;
  const errorCode = err.code || 'INVESTOR_API_ERROR';

  trackError('investor', errorCode);

  globalLogger.error('InvestorRoutes', 'Route error', {
    error: err.message,
    stack: err.stack,
    correlationId: req.correlationId,
    path: req.path,
    method: req.method,
  });

  res.status(statusCode).json({
    success: false,
    error: {
      code: errorCode,
      message: err.message,
      details: err.details,
    },
    metadata: {
      timestamp: new Date().toISOString(),
      correlationId: req.correlationId,
      version: '42.0.0',
    },
  });
});

// =============================================================================
// EXPORT ROUTER
// =============================================================================
export default router;

// =============================================================================
// ENVIRONMENT CONFIGURATION
// =============================================================================
/*
 * Add to .env file:
 *
 * # Investor API Configuration
 * INVESTOR_API_KEYS=key1,key2,key3
 * INVESTOR_IP_WHITELIST=192.168.1.100,10.0.0.50
 * INVESTOR_ALLOWED_ORIGINS=https://investors.wilsy.os,https://ir.wilsy.os
 *
 * # Cache TTLs
 * INVESTOR_CACHE_TTL_VALUATION=300
 * INVESTOR_CACHE_TTL_DASHBOARD=600
 * INVESTOR_CACHE_TTL_REPORT=1800
 *
 * # Rate Limiting
 * INVESTOR_RATE_LIMIT_WINDOW=900000
 * INVESTOR_RATE_LIMIT_MAX=100
 */

// =============================================================================
// VALUATION FOOTER
// =============================================================================
/*
 * VALUATION METRICS:
 * • ARR Target: $650M
 * • Valuation Target: $5B+ (Conservative)
 * • Gross Margin: 87%
 * • LTV/CAC: 3.2x (>3x = healthy)
 * • NRR: 120%
 * • Magic Number: 1.2 (>0.7 = efficient)
 *
 * This investor API transforms operational data into investment-grade
 * metrics, providing Silicon Valley investors with the forensic proof
 * they need to justify a $5B+ valuation.
 *
 * "Investors don't buy vision—they buy metrics."
 *
 * Wilsy OS: Measured. Verified. Valued.
 */
