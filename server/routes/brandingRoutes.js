/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - INSTITUTIONAL BRANDING ROUTER [V1.2.0-FORENSIC-FINAL]                                                                       ║
 * ║ [ZERO-TRUST API GATEWAY | HTTP SEMANTIC ENFORCEMENT | ACTOR VERIFICATION PERIMETER]                                                    ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.2.0 | PRODUCTION READY | TRILLION DOLLAR SPEC                                                                               ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/routes/brandingRoutes.js                                                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated zero‑trust perimeter, requiring authentication and tenant isolation at route level.  ║
 * ║ • AI Engineering (DeepSeek) - EPITOMISED: Added full JSDoc, PATCH semantic enforcement, and boardroom‑ready response headers.         ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * 💎 WHY THIS ROUTER OBLITERATES COMPETITION:
 *   - **Authentication & Tenant Isolation** – Every request passes through `authenticateToken` and `enforceTenantIsolation`
 *     before reaching the controller. Competitors often forget tenant scoping, leading to data leaks.
 *   - **Semantic HTTP Methods** – Uses `GET` for retrieval and `PATCH` for partial updates (instead of overloading `PUT`),
 *     complying with REST best practices and preventing accidental full‑document overwrites.
 *   - **CORS Pre‑flight** – Explicit `OPTIONS` handler with proper allowed methods, ensuring smooth integration with frontend dashboards.
 *   - **Execution Metrics** – The router itself doesn’t add metrics, but it passes the tenant ID to the controller,
 *     which already returns `executionDurationMs` – perfect for boardroom monitoring.
 */

import express from 'express';
import { authenticateToken } from '../middleware/auth.js';
import { enforceTenantIsolation } from '../middleware/tenantBypass.js';
import { fetchTenantBranding, updateTenantBranding } from '../controllers/brandingController.js';

const router = express.Router();

/**
 * Apply authentication and tenant isolation to all routes in this router.
 * This guarantees that only verified users can access or modify branding,
 * and that they can only see/update their own tenant’s data.
 */
router.use(authenticateToken);
router.use(enforceTenantIsolation);

/**
 * GET /api/branding/:tenantId
 * @description Retrieves the tenant's verified branding configuration.
 *              The data passes through cryptographic seal verification before being returned.
 * @param {string} tenantId - Tenant identifier from URL parameter.
 * @returns {Object} 200 - Branding payload with telemetry.
 * @returns {Object} 400 - Missing tenant ID.
 * @returns {Object} 500 - Service failure.
 *
 * 🔐 Requires authentication and tenant isolation.
 * 🧠 Innovation: The response includes `executionDurationMs` for real‑time performance monitoring.
 *
 * @example
 * // Request
 * GET /api/branding/WILSY_GLOBAL_ROOT
 * Authorization: Bearer <token>
 *
 * // Response
 * {
 *   "success": true,
 *   "executionDurationMs": "12.34",
 *   "timestamp": "2026-05-19T14:32:18.123Z",
 *   "data": { ...branding }
 * }
 */
router.get('/:tenantId', fetchTenantBranding);

/**
 * PATCH /api/branding/:tenantId
 * @description Partially updates the tenant's branding configuration.
 *              The controller captures the authenticated user ID (`req.user.id`)
 *              as the `updatedBy` actor, then saves the document – triggering the
 *              cryptographic pre‑save hook (SHA3‑512 seal). Only provided fields are updated.
 * @param {string} tenantId - Tenant identifier from URL parameter.
 * @param {Object} req.body - Partial branding object (any subset of the TenantBranding schema).
 * @returns {Object} 200 - Success with redacted data and execution duration.
 * @returns {Object} 400 - Missing tenant ID or invalid payload.
 * @returns {Object} 500 - Update failure.
 *
 * 🔐 Requires authentication and tenant isolation.
 * 🧠 Innovation: Uses `PATCH` (semantic partial update) instead of `PUT` to avoid accidental
 *                 overwriting of unprovided fields. The controller merges the payload.
 *
 * @example
 * // Request
 * PATCH /api/branding/WILSY_GLOBAL_ROOT
 * Authorization: Bearer <token>
 * Content-Type: application/json
 * {
 *   "bankDetails": { "accountNumber": "1234567890" }
 * }
 *
 * // Response
 * {
 *   "success": true,
 *   "executionDurationMs": "45.12",
 *   "message": "Institutional branding successfully secured and cryptographically sealed.",
 *   "timestamp": "2026-05-19T14:32:18.123Z",
 *   "data": { ...redactedBranding }
 * }
 */
router.patch('/:tenantId', updateTenantBranding);

/**
 * OPTIONS /api/branding/:tenantId
 * @description Handles CORS pre‑flight requests for the branding endpoints.
 *              Allows `GET`, `PATCH`, and `OPTIONS` methods.
 * @returns {void} 200 – No body, only headers.
 */
router.options('/:tenantId', (req, res) => {
  res.header('Access-Control-Allow-Methods', 'GET, PATCH, OPTIONS');
  res.sendStatus(200);
});

export default router;
