/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN COMPLIANCE ROUTES [V33.0.0-OMEGA]                                                                                ║
 * ║ [METRICS HYDRATION | STATUS PROBE | TENANT ISOLATION | STRIDE-PROTECTED]                                                               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/routes/complianceRoutes.js                                              ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import express from 'express';
import { getTenantComplianceMetrics, getComplianceStatus } from '../controllers/complianceController.js';
import { requireSovereignAuth, authorizeRoles, enforceMilitaryWhitelist } from '../middleware/auth.middleware.js';

const router = express.Router();

// Apply military-grade authentication to all compliance endpoints
router.use(requireSovereignAuth);
router.use(enforceMilitaryWhitelist);

/**
 * @route   GET /api/compliance/metrics/:tenantId
 * @desc    Fetch full statutory compliance metrics for a specific tenant
 * @access  Sovereign (JWT + Military Whitelist + Tenant Isolation)
 */
router.get('/metrics/:tenantId', getTenantComplianceMetrics);

/**
 * @route   GET /api/compliance/status
 * @desc    Lightweight health check for the compliance engine
 * @access  Sovereign (JWT + Military Whitelist)
 */
router.get('/status', getComplianceStatus);

export default router;
