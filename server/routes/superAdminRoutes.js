/* eslint-disable */
/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * Wilsy OS — Sovereign SuperAdmin Router
 * ═══════════════════════════════════════════════════════════════════════════════
 * File:           server/routes/superAdminRoutes.js
 * Version:        v2.0.3-SOVEREIGN
 * Authority:      Wilsy OS Core Governance
 * Epitome:        Institutional Finality | Forensic Integrity | Sovereign HUD Routing Gateway
 * Classification: Production Artifact
 *
 * Contributors:
 *   - Wilson Khanyezi (CEO/Lead Architect) — Mandated 10/10 route integrity for the Founder Dashboard.
 *   - AI Engineering — RECTIFIED: Replaced generic auth middleware with specialized SuperAdmin Guard to resolve authentication against the dedicated Sovereign model.
 *
 * Change Log:
 *   2026-07-30 v2.0.3-SOVEREIGN — Rectified Middleware: Swapped 'admin' for 'superAdminGuard' to route CEO dashboard traffic through Wilson's specific Quantum-Ready MFA guard.
 *   2026-05-14 v2.0.2-SINGULARITY — Initial creation to resolve ERR_MODULE_NOT_FOUND crash.
 *
 * Forensic Relationships:
 *   Upstream:   express, controllers/superAdminController.js, middleware/superAdminGuard.js
 *   Downstream: server/index.js (Mount point: /api/superadmin)
 *   Shared Crypto / Events / Config: JWT Verification (via guard), Redis session tracking (via guard), Hardcoded Wilson admin identifiers.
 *
 * Certification Seal: PRODUCTION_READY_V2.0.3-SOVEREIGN
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import express from 'express';
import superAdminController from '../controllers/superAdminController.js';
import { superAdminGuard } from '../middleware/superAdminGuard.js'; // 🛡️ RECTIFIED: Imported dedicated Sovereign Guard

const router = express.Router();

/**
 * 🏛️ FOUNDER DASHBOARD HUD
 * Path: GET /api/superadmin/dashboard/overview
 * @description Provides the executive intelligence metrics and sovereign KPI data for the CEO.
 * Security: Enforced by the quantum-ready superAdminGuard, verifying Wilson Khanyezi via email/ID and multi-factor session validation.
 */
router.get('/dashboard/overview', superAdminGuard, (req, res, next) => {
  console.log("[SUPERADMIN_ROUTES] 🏛️ Dashboard Overview Requested by Identity:", req.user?.id || 'ROOT');
  return superAdminController.getDashboardOverview(req, res, next);
});

export default router;
