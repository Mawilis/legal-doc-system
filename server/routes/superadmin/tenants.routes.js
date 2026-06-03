/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ 🏢 SUPER ADMIN TENANTS ROUTES - WILSY OS 2050                             ║
  ║ Global Tenant Management API with Forensic Compliance                     ║
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
 * 📑 Get all tenants
 */
router.get('/', [
  query('page').optional().isInt({ min: 1 }).default(1),
  query('limit').optional().isInt({ min: 1, max: 100 }).default(20),
  query('search').optional().isString().trim(),
  query('status').optional().isIn(['active','inactive','suspended','trial']),
  query('plan').optional().isString(),
  query('sortBy').optional().isIn(['createdAt','name','usersCount','status']).default('createdAt'),
  query('sortOrder').optional().isIn(['asc','desc']).default('desc'),
  validate
], superAdminController.getAllTenants);

/**
 * 🔍 Get tenant by ID
 */
router.get('/:tenantId', [
  param('tenantId').isMongoId(),
  validate
], superAdminController.getTenantById);

/**
 * ➕ Create tenant
 */
router.post('/', [
  body('name').isString().trim().notEmpty(),
  body('domain').optional().isString().trim(),
  body('industry').optional().isString(),
  body('region').optional().isString(),
  body('plan').isIn(['basic','professional','enterprise','custom']),
  body('ownerEmail').isEmail().normalizeEmail(),
  body('ownerName').isString().trim().notEmpty(),
  validate
], superAdminController.createTenant);

/**
 * ✏️ Update tenant
 */
router.put('/:tenantId', [
  param('tenantId').isMongoId(),
  body('name').optional().isString().trim(),
  body('domain').optional().isString().trim(),
  body('industry').optional().isString(),
  body('region').optional().isString(),
  body('plan').optional().isIn(['basic','professional','enterprise','custom']),
  body('status').optional().isIn(['active','inactive','suspended','trial']),
  validate
], superAdminController.updateTenant);

/**
 * 🗑️ Delete tenant
 */
router.delete('/:tenantId', [
  param('tenantId').isMongoId(),
  body('hardDelete').optional().isBoolean(),
  validate
], superAdminController.deleteTenant);

/**
 * ⏸️ Suspend tenant
 */
router.post('/:tenantId/suspend', [
  param('tenantId').isMongoId(),
  body('reason').isString().notEmpty(),
  validate
], superAdminController.suspendTenant);

/**
 * ▶️ Activate tenant
 */
router.post('/:tenantId/activate', [
  param('tenantId').isMongoId(),
  validate
], superAdminController.activateTenant);

/**
 * 👥 Get tenant users
 */
router.get('/:tenantId/users', [
  param('tenantId').isMongoId(),
  query('page').optional().isInt({ min: 1 }),
  query('limit').optional().isInt({ min: 1, max: 100 }),
  validate
], superAdminController.getTenantUsers);

/**
 * 📊 Tenant statistics
 */
router.get('/stats/summary', superAdminController.getTenantStats);

export default router;
