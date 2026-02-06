/**
 * File: server/routes/systemRoutes.js
 * STATUS: PRODUCTION-READY | SOVEREIGN GOD-MODE ROUTES
 * VERSION: 2026.01.19 (Global Legal OS)
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * - System-level routes for SUPER_ADMIN management
 * - Multi-tenant orchestration across 5000+ law firms
 * - Investor dashboard and analytics
 * - System configuration and monitoring
 * -----------------------------------------------------------------------------
 * ROUTES:
 * GET    /api/system/dashboard          - System analytics dashboard
 * GET    /api/system/firms              - List all legal firms
 * POST   /api/system/firms              - Create new law firm
 * GET    /api/system/firms/:id          - Get firm details
 * PUT    /api/system/firms/:id          - Update firm configuration
 * GET    /api/system/analytics          - Advanced analytics
 * GET    /api/system/health             - System health check
 * POST   /api/system/broadcast          - System-wide notification
 * GET    /api/system/compliance         - Compliance status
 * -----------------------------------------------------------------------------
 */

'use strict';

const express = require('express');
const router = express.Router();
const { protect, requireRole } = require('../middleware/authMiddleware');
const SystemController = require('../controllers/systemController');
const FirmController = require('../controllers/firmController');

// SUPER_ADMIN only routes
router.use(protect);
router.use(requireRole('SUPER_ADMIN'));

/**
 * @route   GET /api/system/dashboard
 * @desc    Main system dashboard for SUPER_ADMIN
 * @access  SUPER_ADMIN only
 * @feature Real-time analytics across all firms
 * @feature Revenue monitoring and forecasting
 * @feature System health and compliance
 */
router.get('/dashboard', SystemController.getAdminDashboard);

/**
 * @route   GET /api/system/firms
 * @desc    List all legal firms with pagination
 * @access  SUPER_ADMIN only
 * @query   page, limit, search, status, tier
 */
router.get('/firms', FirmController.getAllFirms);

/**
 * @route   POST /api/system/firms
 * @desc    Create new law firm (onboarding)
 * @access  SUPER_ADMIN only
 * @body    { name, email, domain, plan, address }
 */
router.post('/firms', FirmController.createFirm);

/**
 * @route   GET /api/system/firms/:id
 * @desc    Get detailed firm information
 * @access  SUPER_ADMIN only
 * @params  id - Firm/Tenant ID
 */
router.get('/firms/:id', FirmController.getFirmDetails);

/**
 * @route   PUT /api/system/firms/:id
 * @desc    Update firm configuration
 * @access  SUPER_ADMIN only
 * @params  id - Firm/Tenant ID
 * @body    { status, plan, settings, limits }
 */
router.put('/firms/:id', FirmController.updateFirm);

/**
 * @route   GET /api/system/analytics
 * @desc    Advanced analytics and reporting
 * @access  SUPER_ADMIN only
 * @query   startDate, endDate, metrics, granularity
 */
router.get('/analytics', SystemController.getAdvancedAnalytics);

/**
 * @route   GET /api/system/health
 * @desc    Comprehensive system health check
 * @access  SUPER_ADMIN only
 * @feature Database, Redis, Storage, Email, API
 */
router.get('/health', SystemController.getSystemHealth);

/**
 * @route   POST /api/system/broadcast
 * @desc    Send system-wide notification
 * @access  SUPER_ADMIN only
 * @body    { title, message, type, recipients }
 */
router.post('/broadcast', SystemController.sendBroadcast);

/**
 * @route   GET /api/system/compliance
 * @desc    System compliance status
 * @access  SUPER_ADMIN only
 * @feature POPIA, FICA, LPC, GDPR compliance
 */
router.get('/compliance', SystemController.getComplianceStatus);

/**
 * @route   GET /api/system/revenue
 * @desc    Revenue analytics and forecasting
 * @access  SUPER_ADMIN only
 * @feature MRR, ARR, churn, growth, projections
 */
router.get('/revenue', SystemController.getRevenueAnalytics);

/**
 * @route   GET /api/system/users
 * @desc    System-wide user management
 * @access  SUPER_ADMIN only
 * @query   role, status, firm, search
 */
router.get('/users', SystemController.getAllUsers);

/**
 * @route   POST /api/system/impersonate/:userId
 * @desc    Impersonate user for support
 * @access  SUPER_ADMIN only
 * @params  userId - User to impersonate
 */
router.post('/impersonate/:userId', SystemController.impersonateUser);

/**
 * @route   GET /api/system/logs
 * @desc    System logs and audit trail
 * @access  SUPER_ADMIN only
 * @query   level, module, startDate, endDate
 */
router.get('/logs', SystemController.getSystemLogs);

/**
 * @route   POST /api/system/maintenance
 * @desc    Enable/disable maintenance mode
 * @access  SUPER_ADMIN only
 * @body    { enabled, message, duration }
 */
router.post('/maintenance', SystemController.toggleMaintenance);

module.exports = router;