/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN SUPERADMIN ROUTER [V2.0.2-SINGULARITY]                                                                            ║
 * ║ [HUD MOUNTING | INSTITUTIONAL AUTHORITY | BILLION DOLLAR SPEC | NO CHILD'S PLACE]                                                      ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 2.0.2-SINGULARITY | PRODUCTION READY | BIBLICAL WORTH BILLIONS                                                                ║
 * ║ EPITOME: INSTITUTIONAL FINALITY | FORENSIC INTEGRITY | REVENUE READY                                                                   ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/routes/superAdminRoutes.js                                               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated 10/10 route integrity for the Founder Dashboard.                                      ║
 * ║ • Gemini (AI Engineering) - RECTIFIED: Created missing route file to resolve ERR_MODULE_NOT_FOUND crash.                                ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import express from 'express';
import superAdminController from '../controllers/superAdminController.js';
import { protect, admin } from '../middleware/authMiddleware.js';

const router = express.Router();

/**
 * 🏛️ FOUNDER DASHBOARD HUD
 * Path: GET /api/superadmin/dashboard/overview
 * RECTIFIED: Explicitly mounted to satisfy dashboard telemetry requests.
 */
router.get('/dashboard/overview', protect, admin, (req, res, next) => {
  console.log("[SUPERADMIN_ROUTES] 🏛️ Dashboard Overview Requested by Identity:", req.user?.id || 'ROOT');
  return superAdminController.getDashboardOverview(req, res, next);
});

export default router;
