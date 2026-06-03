/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ 📋 SUPER ADMIN AUDIT ROUTES - WILSY OS 2050                               ║
  ║ Global Audit Trail Management API                                         ║
  ║ Supreme Architect: Wilson Khanyezi - 10th Generation                      ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import express from 'express';
import { body, param, query, validationResult } from 'express-validator';
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
 * @route   GET /api/superadmin/audit/logs
 * @desc    Get audit logs with comprehensive filtering
 */
router.get('/logs', [
  query('page').optional().isInt({ min: 1 }).default(1),
  query('limit').optional().isInt({ min: 1, max: 200 }).default(50),
  query('tenantId').optional().isMongoId(),
  query('userId').optional().isMongoId(),
  query('action').optional().isString(),
  query('severity').optional().isIn(['info','warning','error','critical','audit']),
  query('startDate').optional().isISO8601(),
  query('endDate').optional().isISO8601(),
  validate
], superAdminController.getAuditLogs);

/**
 * @route   GET /api/superadmin/audit/logs/:logId
 * @desc    Get single audit log entry
 */
router.get('/logs/:logId', [
  param('logId').isMongoId(),
  validate
], superAdminController.getAuditLogById);

/**
 * @route   GET /api/superadmin/audit/forensic-chain
 * @desc    Get complete forensic chain
 */
router.get('/forensic-chain', [
  query('limit').optional().isInt({ min: 1, max: 1000 }).default(100),
  validate
], superAdminController.getForensicChain);

/**
 * @route   GET /api/superadmin/audit/forensic-chain/verify
 * @desc    Verify forensic chain integrity
 */
router.get('/forensic-chain/verify', superAdminController.verifyForensicChain);

/**
 * @route   GET /api/superadmin/audit/statistics
 * @desc    Get audit statistics
 */
router.get('/statistics', [
  query('period').optional().isIn(['24h','7d','30d','90d','1y']).default('30d'),
  validate
], superAdminController.getAuditStatistics);

/**
 * @route   GET /api/superadmin/audit/user-activity/:userId
 * @desc    Get user activity trail
 */
router.get('/user-activity/:userId', [
  param('userId').isMongoId(),
  validate
], superAdminController.getUserActivityTrail);

/**
 * @route   GET /api/superadmin/audit/tenant-activity/:tenantId
 * @desc    Get tenant activity trail
 */
router.get('/tenant-activity/:tenantId', [
  param('tenantId').isMongoId(),
  validate
], superAdminController.getTenantActivityTrail);

/**
 * @route   POST /api/superadmin/audit/export
 * @desc    Export audit logs
 */
router.post('/export', [
  body('format').isIn(['json','csv','pdf']),
  body('dateRange').optional().isObject(),
  validate
], superAdminController.exportAuditLogs);

export default router;
