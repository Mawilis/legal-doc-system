/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ ⚙️ SUPER ADMIN SYSTEM ROUTES - WILSY OS 2050                              ║
  ║ System Configuration and Management API                                   ║
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
    return res.status(400).json({ success: false, errors: errors.array(), requestId: req.id || null });
  }
  next();
};

// 🔒 All routes require super admin authentication and audit logging
router.use(protect);
router.use(superAdminOnly);
router.use(auditLogger);

/**
 * @route   GET /api/superadmin/system/health
 * @desc    Get comprehensive system health
 */
router.get('/health', superAdminController.getSystemHealth);

/**
 * @route   GET /api/superadmin/system/status
 * @desc    Get system status
 */
router.get('/status', superAdminController.getSystemStatus);

/**
 * @route   GET /api/superadmin/system/config
 * @desc    Get system configuration
 */
router.get('/config', superAdminController.getSystemConfig);

/**
 * @route   PUT /api/superadmin/system/config
 * @desc    Update system configuration
 */
router.put('/config', [
  body('maintenanceMode').optional().isBoolean(),
  body('signupEnabled').optional().isBoolean(),
  body('maxTenants').optional().isInt(),
  body('features').optional().isObject(),
  validate
], superAdminController.updateSystemConfig);

/**
 * @route   POST /api/superadmin/system/maintenance
 * @desc    Toggle maintenance mode
 */
router.post('/maintenance', [
  body('enabled').isBoolean(),
  body('message').optional().isString(),
  body('duration').optional().isInt(),
  validate
], superAdminController.toggleMaintenanceMode);

/**
 * @route   GET /api/superadmin/system/logs
 * @desc    Get system logs
 */
router.get('/logs', [
  query('level').optional().isIn(['debug', 'info', 'warn', 'error']),
  query('limit').optional().isInt({ min: 1, max: 1000 }).default(100),
  validate
], superAdminController.getSystemLogs);

/**
 * @route   GET /api/superadmin/system/version
 * @desc    Get system version information
 */
router.get('/version', superAdminController.getSystemVersion);

/**
 * @route   POST /api/superadmin/system/backup
 * @desc    Create system backup
 */
router.post('/backup', superAdminController.createBackup);

/**
 * @route   GET /api/superadmin/system/backups
 * @desc    List available backups
 */
router.get('/backups', superAdminController.listBackups);

/**
 * @route   POST /api/superadmin/system/restore/:backupId
 * @desc    Restore from backup
 */
router.post('/restore/:backupId', [
  param('backupId').isMongoId(),
  validate
], superAdminController.restoreFromBackup);

export default router;
