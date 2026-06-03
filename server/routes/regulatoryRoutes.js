/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN REGULATORY & JURISPRUDENCE ROUTES                                                                                 ║
 * ║ [PQE-256 SECURED | POPIA §11 COMPLIANT | R10B+ AUDITABLE]                                                                              ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 15.2.0-SINGULARITY-OMEGA | PRODUCTION READY                                                                                 ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL GRADE                                                              ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/routes/regulatoryRoutes.js                                                ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Regulatory Sovereignty & Jurisprudence Strategy                                               ║
 * ║ • Gemini (AI Engineering) - ESM Traffic Orchestration & Middleware Alignment                                                           ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import express from 'express';
import { regulatoryController } from '../controllers/regulatoryController.js';
import { protect, restrictTo } from '../middleware/authMiddleware.js';
import tenantGuard from '../middleware/tenantGuard.js';
import { body, param, query } from 'express-validator';

const router = express.Router();

// 🏛️ PUBLIC VITALITY ENDPOINTS
router.get('/health', (req, res) => regulatoryController.healthCheck(req, res));
router.get('/status', (req, res) => regulatoryController.getSystemStatus(req, res));

// 🔐 SOVEREIGN SECURED ZONE
router.use(protect);
router.use(tenantGuard);

/**
 * @section MONITORING & ENFORCEMENT
 */
router.post(
  '/monitor/start',
  restrictTo('founder', 'super_admin', 'tenant_owner'),
  body('jurisdiction').optional().isString(),
  (req, res) => regulatoryController.startMonitoring(req, res)
);

router.get('/monitor/metrics', (req, res) => regulatoryController.getMonitoringMetrics(req, res));

/**
 * @section LEGISLATION & CHANGES
 */
router.get(
  '/changes',
  query('limit').optional().isInt({ min: 1, max: 100 }),
  (req, res) => regulatoryController.getRegulatoryChanges(req, res)
);

router.get(
  '/legislation',
  query('jurisdiction').optional().isString(),
  (req, res) => regulatoryController.getLegislation(req, res)
);

/**
 * @section COMPLIANCE & AUDIT
 */
router.get(
  '/compliance/report',
  restrictTo('founder', 'super_admin', 'auditor'),
  (req, res) => regulatoryController.generateComplianceReport(req, res)
);

router.post(
  '/compliance/scan',
  restrictTo('founder', 'super_admin', 'tenant_owner'),
  (req, res) => regulatoryController.performComplianceScan(req, res)
);

/**
 * @section ADMINISTRATIVE COMMANDS
 */
router.post(
  '/admin/clear-cache',
  restrictTo('founder', 'super_admin'),
  (req, res) => regulatoryController.adminClearCache(req, res)
);

router.get(
  '/admin/audit',
  restrictTo('founder', 'super_admin', 'auditor'),
  (req, res) => regulatoryController.getAuditLog(req, res)
);

export default router;
