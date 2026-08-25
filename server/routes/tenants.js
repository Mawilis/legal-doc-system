/* eslint-disable */
/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * Wilsy OS — Sovereign Tenants Router Proxy
 * ═══════════════════════════════════════════════════════════════════════════════
 * File:           server/routes/tenants.js
 * Version:        v1.0.0-PROXY-SOVEREIGN
 * Authority:      Wilsy OS Core Governance
 * Epitome:        Surgical import bridge - delegates directly to the existing certified tenantRoutes.js contract without modifying core index.js.
 * Classification: Production Artifact
 *
 * Contributors:
 *   - Wilson Khanyezi (CEO/Lead Architect) — Mandated zero-touch architectural bridging.
 *   - AI Engineering — Rectified: Delegated to the existing tenantRoutes.js to satisfy the import constraint without overwriting the Sovereign index.
 *
 * Change Log:
 *   2026-07-30 v1.0.0-PROXY-SOVEREIGN — Initial surgical proxy created to align ./tenants.js import with the existing tenantRoutes.js artifact.
 *
 * Forensic Relationships:
 *   Upstream:   server/index.js (Mount point: /api/tenants)
 *   Downstream: ./tenantRoutes.js (Actual certified Sovereign Route Contract)
 *   Shared Crypto / Events / Config: N/A
 *
 * Certification Seal: PRODUCTION_READY_v1.0.0-PROXY-SOVEREIGN
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import router from './tenantRoutes.js';

export default router;
