/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║  📊 SUPER ADMIN DASHBOARD ROUTES - WILSY OS 2050                         ║
  ║  Supreme Command Center Dashboard API with Forensic Compliance            ║
  ║  Supreme Architect: Wilson Khanyezi - 10th Generation                     ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import express from 'express';
import { query, validationResult } from 'express-validator';
import { protect, superAdminOnly } from '../../middleware/auth.js';
import superAdminController from '../../controllers/superAdminController.js';
import auditLogger from '../../middleware/auditLogger.js';

const router = express.Router();

/**
 * Validation middleware: ensures all express-validator checks are enforced
 */
const validate = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      success: false,
      errors: errors.array(),
      requestId: req.id || null
    });
  }
  next();
};

// 🔒 All routes require super admin authentication and audit logging
router.use(protect);
router.use(superAdminOnly);
router.use(auditLogger);

/**
 * 📊 Dashboard Statistics
 * EXPECTS: res.body.data.stats
 */
router.get('/stats', [
  query('timeframe').optional().isIn(['24h','7d','30d','90d','1y']).default('7d'),
  validate
], superAdminController.getDashboardStats);

/**
 * 🕒 Recent Activity
 * EXPECTS: res.body.data.activity
 */
router.get('/recent-activity', [
  query('limit').optional().isInt({ min: 1, max: 100 }).default(20),
  validate
], superAdminController.getRecentActivity);

/**
 * ❤️ System Health
 * EXPECTS: res.body.data.status
 */
router.get('/health', superAdminController.getSystemHealth);

/**
 * ⚡ Performance Metrics
 * EXPECTS: res.body.data.metrics
 */
router.get('/performance', [
  query('period').optional().isIn(['hour','day','week','month']).default('day'),
  validate
], superAdminController.getPerformanceMetrics);

/**
 * 🚨 Active Alerts
 * EXPECTS: res.body.data.alerts
 */
router.get('/alerts', superAdminController.getActiveAlerts);

/**
 * 🔍 Forensic Audit Summary
 * EXPECTS: res.body.data.summary
 */
router.get('/forensic-summary', superAdminController.getForensicSummary);

/**
 * 💎 Wealth Vision
 * EXPECTS: res.body.data.vision
 */
router.get('/wealth-vision', superAdminController.getWealthVision);

/**
 * 🛡️ Risk Assessment
 * EXPECTS: res.body.data.risk
 */
router.get('/risk-assessment', superAdminController.getRiskAssessment);

/**
 * 📜 Compliance Status
 * EXPECTS: res.body.data.compliance
 */
router.get('/compliance-status', superAdminController.getComplianceStatus);

/**
 * 🔐 Quantum Security Metrics
 * EXPECTS: res.body.data.quantum
 */
router.get('/quantum-metrics', superAdminController.getQuantumMetrics);

export default router;
