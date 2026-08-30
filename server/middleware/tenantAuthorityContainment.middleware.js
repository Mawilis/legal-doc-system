/**
 * WILSY OS — NODE TENANT AUTHORITY CONTAINMENT
 * VERSION: v1.0.0-TENANT-AUTHORITY-CONTAINMENT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Earliest boundary denying the legacy direct Node tenant router while governed Python authority is unavailable.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/server/middleware/tenantAuthorityContainment.middleware.js
 * COLLABORATION / OWNERSHIP: Wilsy Core Engineering; consumed by server/index.js before tenantContext.
 * CERTIFICATION/UPDATE DATE: 2026-08-30
 * CHANGELOG: v1.0.0 adds deterministic deny-before-authentication containment for /api/tenant/* only.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY/PRIVACY POSTURE: No request identity, role, header, tenant, database, or controller state is read.
 * TENANT BOUNDARY: Applies only to the singular legacy /api/tenant route namespace; /api/tenants remains Python/Kennel-owned.
 * AUTHORITY BOUNDARY: Transport containment only; it does not authenticate, authorize, or own tenant truth.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains the exclusive financial execution authority.
 */

const VERSION = 'v1.0.0-TENANT-AUTHORITY-CONTAINMENT';

/**
 * Deny the direct legacy tenant namespace before tenant context or auth middleware.
 * @param {import('express').Request} req Express request.
 * @param {import('express').Response} res Express response.
 * @returns {void} Always emits the bounded unavailable-authority response.
 */
export function tenantAuthorityUnavailable(req, res) {
  res.status(503).json({ success: false, error: { code: 'TENANT_AUTHORITY_UNAVAILABLE' } });
}

export { VERSION };

// ARTIFACT: tenantAuthorityContainment.middleware.js
// VERSION: v1.0.0-TENANT-AUTHORITY-CONTAINMENT
// AUTHORITY BOUNDARY: early transport containment for the legacy direct Node tenant namespace only
// TENANT POSTURE: no header, role, JWT, or tenant value can bypass the denial
// FAIL-CLOSED POSTURE: deterministic HTTP 503 TENANT_AUTHORITY_UNAVAILABLE before downstream middleware
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
// END OF WILSY OS SOVEREIGN ARTIFACT
