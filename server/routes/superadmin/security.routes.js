/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ 🛡️ SUPER ADMIN SECURITY ROUTES - WILSY OS 2050                            ║
  ║ Global Security Management API with Quantum-Grade Forensics               ║
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
 * @route   GET /api/superadmin/security/overview
 * @desc    Get security overview
 */
router.get('/overview', superAdminController.getSecurityOverview);

/**
 * @route   GET /api/superadmin/security/threats
 * @desc    Get active threats
 */
router.get('/threats', [
  query('severity').optional().isIn(['low','medium','high','critical']),
  validate
], superAdminController.getActiveThreats);

/**
 * @route   GET /api/superadmin/security/incidents
 * @desc    Get security incidents
 */
router.get('/incidents', [
  query('page').optional().isInt({ min: 1 }),
  query('limit').optional().isInt({ min: 1, max: 100 }),
  validate
], superAdminController.getSecurityIncidents);

/**
 * @route   GET /api/superadmin/security/mfa-status
 * @desc    Get MFA compliance status
 */
router.get('/mfa-status', superAdminController.getMFAStatus);

/**
 * @route   GET /api/superadmin/security/login-attempts
 * @desc    Get login attempt analytics
 */
router.get('/login-attempts', [
  query('period').optional().isIn(['24h','7d','30d']).default('24h'),
  validate
], superAdminController.getLoginAttempts);

/**
 * @route   GET /api/superadmin/security/ip-blacklist
 * @desc    Get IP blacklist
 */
router.get('/ip-blacklist', superAdminController.getIPBlacklist);

/**
 * @route   POST /api/superadmin/security/ip-blacklist
 * @desc    Add IP to blacklist
 */
router.post('/ip-blacklist', [
  body('ip').isIP(),
  body('reason').isString(),
  validate
], superAdminController.addIPToBlacklist);

/**
 * @route   DELETE /api/superadmin/security/ip-blacklist/:ipId
 * @desc    Remove IP from blacklist
 */
router.delete('/ip-blacklist/:ipId', [
  param('ipId').isMongoId(),
  validate
], superAdminController.removeIPFromBlacklist);

export default router;
