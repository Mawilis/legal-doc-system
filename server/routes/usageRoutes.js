/* eslint-disable */
/*
 * WILSY OS: USAGE ROUTES - REAL-TIME QUOTA DASHBOARD API
 * ============================================================================
 */

import express from 'express.js';
import { body, query, param, validationResult } from 'express-validator.js';
import { performance } from 'perf_hooks.js';
import { v4 as uuidv4 } from 'uuid.js';

import { tenantGuard } from '../middleware/tenantGuard.js.js';
import { authenticate, authorize } from '../middleware/auth.js.js';
import { rateLimiter } from '../middleware/rateLimiter.js.js';
import { cacheMiddleware } from '../middleware/cache.js.js';
import { auditMiddleware } from '../middleware/audit.js.js';
import { QuantumLogger } from '../utils/quantumLogger.js.js';
import { trackRequest, trackError } from '../utils/metricsCollector.js.js';
import { AppError } from '../utils/errorHandler.js.js';
import usageService from '../services/monitoring/UsageService.js.js';

const router = express.Router();

// Apply tenant isolation
router.use(tenantGuard);

// Apply audit logging
router.use(auditMiddleware('usage'));

// Request tracking
router.use((req, res, next) => {
  req.requestId = req.headers['x-request-id'] || uuidv4();
  req.startTime = performance.now();

  res.setHeader('X-Request-ID', req.requestId);
  res.setHeader('X-Usage-API-Version', '42.0.0');

  trackRequest(req.method, req.path);
  next();
});

// =============================================================================
// GET CURRENT USAGE STATS
// =============================================================================
router.get(
  '/current',
  authenticate,
  rateLimiter({ windowMs: 60000, max: 30 }),
  cacheMiddleware({ ttl: 60 }), // 1 minute cache
  async (req, res, next) => {
    try {
      const { id: tenantId } = req.tenantContext;
      const tier = req.tenantContext.tier || req.user?.subscription?.tier || 'premium';

      const stats = await usageService.getTenantUsageStats(tenantId, tier, {
        includeHistory: req.query.history === 'true',
        includePredictions: req.query.predictions === 'true',
        includeAlerts: req.query.alerts === 'true',
        requestId: req.requestId,
      });

      const duration = performance.now() - req.startTime;

      res.json({
        success: true,
        data: stats,
        metadata: {
          processingTimeMs: Math.round(duration),
          requestId: req.requestId,
          cached: req.cached || false,
        },
      });
    } catch (error) {
      trackError('usage', error.code || 'current_error');
      next(new AppError(error.message, 500, 'USAGE_FETCH_FAILED'));
    }
  }
);

// =============================================================================
// GET USAGE HISTORY
// =============================================================================
router.get(
  '/history',
  authenticate,
  rateLimiter({ windowMs: 60000, max: 20 }),
  [
    query('period').optional().isIn(['hour', 'day', 'week', 'month']),
    query('days').optional().isInt({ min: 1, max: 365 }).toInt(),
    query('startDate').optional().isISO8601(),
    query('endDate').optional().isISO8601(),
  ],
  async (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      const { id: tenantId } = req.tenantContext;
      const { period = 'day', days = 30, startDate, endDate } = req.query;

      const history = await usageService.getUsageHistory(tenantId, {
        period,
        days,
        startDate,
        endDate,
      });

      const duration = performance.now() - req.startTime;

      res.json({
        success: true,
        data: history,
        metadata: {
          processingTimeMs: Math.round(duration),
          requestId: req.requestId,
        },
      });
    } catch (error) {
      trackError('usage', error.code || 'history_error');
      next(new AppError(error.message, 500, 'HISTORY_FETCH_FAILED'));
    }
  }
);

// =============================================================================
// GET USAGE PREDICTIONS
// =============================================================================
router.get(
  '/predictions',
  authenticate,
  rateLimiter({ windowMs: 60000, max: 10 }),
  [query('days').optional().isInt({ min: 7, max: 90 }).toInt()],
  async (req, res, next) => {
    try {
      const { id: tenantId } = req.tenantContext;
      const tier = req.tenantContext.tier || req.user?.subscription?.tier || 'premium';
      const { days = 30 } = req.query;

      const predictions = await usageService.predictUsage(tenantId, tier, { days });

      const duration = performance.now() - req.startTime;

      res.json({
        success: true,
        data: predictions,
        metadata: {
          processingTimeMs: Math.round(duration),
          requestId: req.requestId,
        },
      });
    } catch (error) {
      trackError('usage', error.code || 'prediction_error');
      next(new AppError(error.message, 500, 'PREDICTION_FAILED'));
    }
  }
);

// =============================================================================
// GET ACTIVE ALERTS
// =============================================================================
router.get(
  '/alerts',
  authenticate,
  rateLimiter({ windowMs: 60000, max: 30 }),
  cacheMiddleware({ ttl: 30 }), // 30 second cache
  async (req, res, next) => {
    try {
      const { id: tenantId } = req.tenantContext;
      const alerts = await usageService.getActiveAlerts(tenantId);

      const duration = performance.now() - req.startTime;

      res.json({
        success: true,
        data: alerts,
        metadata: {
          count: alerts.length,
          processingTimeMs: Math.round(duration),
          requestId: req.requestId,
        },
      });
    } catch (error) {
      trackError('usage', error.code || 'alerts_error');
      next(new AppError(error.message, 500, 'ALERTS_FETCH_FAILED'));
    }
  }
);

// =============================================================================
// ACKNOWLEDGE ALERT
// =============================================================================
router.post(
  '/alerts/:alertId/acknowledge',
  authenticate,
  rateLimiter({ windowMs: 60000, max: 20 }),
  [param('alertId').isUUID()],
  async (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      const { id: tenantId } = req.tenantContext;
      const { alertId } = req.params;

      await usageService.acknowledgeAlert(tenantId, alertId);

      await QuantumLogger.logAction(tenantId, req.user?.id, 'ALERT_ACKNOWLEDGED', alertId, {
        requestId: req.requestId,
      });

      res.json({
        success: true,
        message: 'Alert acknowledged',
        metadata: {
          requestId: req.requestId,
        },
      });
    } catch (error) {
      trackError('usage', error.code || 'acknowledge_error');
      next(new AppError(error.message, 500, 'ACKNOWLEDGE_FAILED'));
    }
  }
);

// =============================================================================
// GET UPGRADE RECOMMENDATIONS
// =============================================================================
router.get(
  '/upgrade-recommendations',
  authenticate,
  rateLimiter({ windowMs: 60000, max: 20 }),
  cacheMiddleware({ ttl: 300 }), // 5 minute cache
  async (req, res, next) => {
    try {
      const { id: tenantId } = req.tenantContext;
      const tier = req.tenantContext.tier || req.user?.subscription?.tier || 'premium';

      const stats = await usageService.getTenantUsageStats(tenantId, tier);
      const percentUsed = parseFloat(stats.quota.percentUsed);

      let recommendations = null;
      if (percentUsed >= 70) {
        recommendations = usageService.getUpgradeRecommendations(tier, percentUsed);
      }

      res.json({
        success: true,
        data: {
          currentTier: tier,
          percentUsed,
          showUpgrade: percentUsed >= 70,
          recommendations,
        },
        metadata: {
          requestId: req.requestId,
        },
      });
    } catch (error) {
      trackError('usage', error.code || 'recommendations_error');
      next(new AppError(error.message, 500, 'RECOMMENDATIONS_FAILED'));
    }
  }
);

// =============================================================================
// EXPORT USAGE DATA
// =============================================================================
router.get(
  '/export',
  authenticate,
  rateLimiter({ windowMs: 60000, max: 5 }),
  [
    query('format').isIn(['json', 'csv', 'pdf']),
    query('startDate').optional().isISO8601(),
    query('endDate').optional().isISO8601(),
  ],
  async (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      const { id: tenantId } = req.tenantContext;
      const { format = 'json', startDate, endDate } = req.query;

      const exported = await usageService.exportUsage(tenantId, {
        format,
        startDate,
        endDate,
      });

      // Set headers for download
      const filename = `wilsy-usage-${tenantId}-${Date.now()}`;

      if (format === 'csv') {
        res.setHeader('Content-Type', 'text/csv');
        res.setHeader('Content-Disposition', `attachment; filename="${filename}.csv"`);
        return res.send(exported);
      } else if (format === 'pdf') {
        res.setHeader('Content-Type', 'application/pdf');
        res.setHeader('Content-Disposition', `attachment; filename="${filename}.pdf"`);
        return res.send(exported);
      }

      res.json({
        success: true,
        data: exported,
        metadata: {
          requestId: req.requestId,
        },
      });
    } catch (error) {
      trackError('usage', error.code || 'export_error');
      next(new AppError(error.message, 500, 'EXPORT_FAILED'));
    }
  }
);

// =============================================================================
// ADMIN: GET ALL TENANTS USAGE (Enterprise only)
// =============================================================================
router.get(
  '/admin/all',
  authenticate,
  authorize(['admin', 'enterprise']),
  rateLimiter({ windowMs: 60000, max: 100 }),
  async (req, res, next) => {
    try {
      const tenantIds = await usageService.getActiveTenants();
      const stats = [];

      for (const tenantId of tenantIds) {
        const stat = await usageService.getTenantUsageStats(tenantId);
        stats.push(stat);
      }

      res.json({
        success: true,
        data: {
          total: stats.length,
          tenants: stats,
        },
        metadata: {
          requestId: req.requestId,
        },
      });
    } catch (error) {
      trackError('usage', error.code || 'admin_error');
      next(new AppError(error.message, 500, 'ADMIN_FETCH_FAILED'));
    }
  }
);

// =============================================================================
// HEALTH CHECK
// =============================================================================
router.get('/health', async (req, res) => {
  const health = await usageService.healthCheck();
  res.json(health);
});

export default router;
