/**
 * ============================================================================
 * 🛤️🔗 ANALYTICS QUANTUM ROUTES: API GATEWAYS TO INTELLIGENCE NEXUS 🛤️🔗
 * ============================================================================
 */

const express = require('express');
const router = express.Router();
const analyticsController = require('../controllers/analyticsController');

// QUANTUM MIDDLEWARE IMPORTS
const { authenticate, authorize } = require('../middleware/auth');
const { validateAnalyticsQuery } = require('../validators/analyticsValidator');
const { rateLimitByTenant } = require('../middleware/rateLimiter');
const { auditTrail } = require('../middleware/security');

/**
 * ----------------------------------------------------------------------------
 * FINANCIAL INTELLIGENCE ROUTES
 * ----------------------------------------------------------------------------
 */

// GET /api/analytics/monetization - Financial metrics
router.get(
    '/monetization',
    authenticate,
    authorize(['SUPER_ADMIN', 'TENANT_ADMIN']),
    rateLimitByTenant(100, 900), // 100 requests per 15 minutes per tenant
    auditTrail('ANALYTICS_ACCESS'),
    analyticsController.getMonetization
);

// GET /api/analytics/compliance-heatmap - Security heatmap
router.get(
    '/compliance-heatmap',
    authenticate,
    authorize(['SUPER_ADMIN', 'SECURITY_ADMIN']),
    rateLimitByTenant(50, 900),
    validateAnalyticsQuery,
    auditTrail('SECURITY_ANALYTICS'),
    analyticsController.getComplianceHeatmap
);

// GET /api/analytics/plan-mix - Subscription distribution
router.get(
    '/plan-mix',
    authenticate,
    authorize(['SUPER_ADMIN']), // SUPER_ADMIN only
    rateLimitByTenant(20, 3600), // 20 requests per hour
    auditTrail('PLATFORM_ANALYTICS'),
    analyticsController.getPlanMix
);

/**
 * ----------------------------------------------------------------------------
 * FORENSICS & SECURITY ROUTES
 * ----------------------------------------------------------------------------
 */

// GET /api/analytics/audit-logs - Immutable audit trail
router.get(
    '/audit-logs',
    authenticate,
    authorize(['SUPER_ADMIN', 'SECURITY_ADMIN', 'COMPLIANCE_OFFICER']),
    rateLimitByTenant(200, 900),
    auditTrail('AUDIT_TRAIL_ACCESS'),
    analyticsController.getAuditLogs
);

// GET /api/analytics/dashboard-stats - Real-time dashboard
router.get(
    '/dashboard-stats',
    authenticate,
    authorize(['SUPER_ADMIN', 'TENANT_ADMIN']),
    rateLimitByTenant(60, 300), // 60 requests per 5 minutes
    auditTrail('DASHBOARD_VIEW'),
    analyticsController.getDashboardStats
);

/**
 * ----------------------------------------------------------------------------
 * ADVANCED ANALYTICS & AI ROUTES
 * ----------------------------------------------------------------------------
 */

// GET /api/analytics/predictive-churn - AI churn prediction
router.get(
    '/predictive-churn',
    authenticate,
    authorize(['SUPER_ADMIN', 'TENANT_ADMIN']),
    rateLimitByTenant(30, 3600), // CPU-intensive, limit heavily
    validateAnalyticsQuery,
    auditTrail('PREDICTIVE_ANALYTICS'),
    analyticsController.getPredictiveChurn
);

// GET /api/analytics/health-check - System health
router.get(
    '/health-check',
    authenticate,
    authorize(['SUPER_ADMIN', 'SYSTEM_ADMIN']),
    rateLimitByTenant(10, 60),
    analyticsController.getSystemHealth
);

/**
 * ----------------------------------------------------------------------------
 * COMPLIANCE & REGULATORY ROUTES
 * ----------------------------------------------------------------------------
 */

// GET /api/analytics/compliance-report - POPIA/GDPR compliance
router.get(
    '/compliance-report',
    authenticate,
    authorize(['SUPER_ADMIN', 'COMPLIANCE_OFFICER']),
    rateLimitByTenant(20, 3600),
    auditTrail('COMPLIANCE_REPORT'),
    analyticsController.getComplianceReport
);

// POST /api/analytics/data-export - DSAR data export (POPIA Section 23)
router.post(
    '/data-export',
    authenticate,
    authorize(['SUPER_ADMIN', 'COMPLIANCE_OFFICER']),
    rateLimitByTenant(5, 86400), // 5 per day max
    auditTrail('DSAR_EXECUTION'),
    analyticsController.exportComplianceData
);

/**
 * ----------------------------------------------------------------------------
 * VALUATION & BUSINESS INTELLIGENCE ROUTES
 * ----------------------------------------------------------------------------
 */

// GET /api/analytics/valuation-metrics - Investor-ready metrics
router.get(
    '/valuation-metrics',
    authenticate,
    authorize(['SUPER_ADMIN']), // Investors/Super Admins only
    rateLimitByTenant(10, 3600),
    auditTrail('VALUATION_ACCESS'),
    analyticsController.getValuationMetrics
);

module.exports = router;