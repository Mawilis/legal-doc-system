/* eslint-disable */
/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * Wilsy OS — Sovereign Revenue Router Proxy
 * ═══════════════════════════════════════════════════════════════════════════════
 * File:           server/routes/revenue.js
 * Version:        v1.0.0-PROXY-SOVEREIGN
 * Authority:      Wilsy OS Core Governance
 * Epitome:        Surgical import bridge - delegates directly to the existing certified revenueRoutes.js contract without modifying core index.js.
 * Classification: Production Artifact
 *
 * Contributors:
 *   - Wilson Khanyezi (CEO/Lead Architect) — Mandated zero-touch architectural bridging.
 *   - AI Engineering — Rectified: Delegated to the existing revenueRoutes.js to satisfy the import constraint without overwriting the Sovereign index.
 *
 * Change Log:
 *   2026-07-30 v1.0.0-PROXY-SOVEREIGN — Initial surgical proxy created to align ./revenue.js import with the existing revenueRoutes.js artifact.
 *
 * Forensic Relationships:
 *   Upstream:   server/index.js (Mount point: /api/revenue)
 *   Downstream: ./revenueRoutes.js (Actual certified Sovereign Route Contract)
 *   Shared Crypto / Events / Config: N/A
 *
 * Certification Seal: PRODUCTION_READY_v1.0.0-PROXY-SOVEREIGN
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import router from './revenueRoutes.js';

export default router;
