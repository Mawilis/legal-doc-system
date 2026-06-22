/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - TENANT ISOLATION SHIELD [V1.0.0-MARS-FINALITY]                                                                              ║
 * ║ [SINGLE SOURCE OF TRUTH | SOVEREIGN BYPASS | 403 FRACTURE KILLER]                                                                      ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/middleware/tenantBypass.js                                               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated zero hardcoded role checks. All access flows through MARS Protocol. [2026-05-15]     ║
 * ║ • AI Engineering (DeepSeek) - RECTIFIED: Created tenant isolation middleware using SovereignBypassRoles registry. [2026-05-15]         ║
 * ║ • AI Engineering (Gemini) - FORTIFIED: Added collaboration comments and institutional logging. [2026-05-15]                            ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import { canBypassTenant } from '../config/roles.registry.js';
import { broadcastTelemetry } from '../utils/telemetryHelper.js';

/**
 * @function enforceTenantIsolation
 * @description Enforces tenant isolation while allowing safe read-only operating bridge routes.
 * @param {Object} req - Express request object carrying user and tenant context.
 * @param {Object} res - Express response object.
 * @param {Function} next - Express next middleware function.
 * @returns {void} Continues request handling or returns a tenant isolation response.
 * @collaboration Protects tenant boundaries while allowing source-registry and Account identity posture read-only proof routes.
 */
export const enforceTenantIsolation = (req, res, next) => {
  // WILSY_SOURCE_REGISTRY_READONLY_TENANT_ISOLATION_BYPASS
  // Allows non-mutating Source Registry inspection without weakening protected POST operations.
  const sourceRegistryReadOnlyTenantIsolationBypass =
    ['GET', 'HEAD', 'OPTIONS'].includes(String(req.method || 'GET').toUpperCase()) &&
    [
      '/api/source-registry/health',
      '/api/source-registry/status',
      '/api/account/identity-posture',
      '/api/account/compliance-command',
    ].some((path) => String(req.originalUrl || req.url || '').startsWith(path));

  if (sourceRegistryReadOnlyTenantIsolationBypass) {
    req.tenantId =
      req.headers?.['x-tenant-id'] ||
      req.headers?.['X-Tenant-Id'] ||
      req.headers?.['x-wilsy-tenant-id'] ||
      req.headers?.['X-Wilsy-Tenant-ID'] ||
      req.tenantId ||
      'MASTER';

    req.tenant = req.tenant || {
      id: req.tenantId,
      tenantId: req.tenantId,
      source: 'READONLY_OPERATING_BRIDGE_TENANT_BYPASS',
      readOnly: true,
    };

    res.setHeader('X-Wilsy-Tenant-Isolation-Bypass', 'SOURCE_REGISTRY_READ_ONLY');
    return next();
  }

  const { role, tenantId: userTenantId } = req.user || {};
  const targetTenantId = req.params.tenantId || req.headers['x-tenant-id'];
  const traceId = req.headers['x-trace-id'] || `TRC-TENANT-${Date.now()}`;

  // 🚀 SOVEREIGN BYPASS - Registry decides, not hardcoded strings
  if (canBypassTenant(role)) {
    broadcastTelemetry(
      userTenantId || 'GLOBAL_ROOT',
      'AUTH_EVENT',
      'TENANT_BYPASS',
      'tenantBypass',
      {
        traceId,
        role,
        targetTenant: targetTenantId,
        reason: 'SOVEREIGN_BYPASS_GRANTED',
      }
    );
    return next();
  }

  // 🔒 TENANT LOCKDOWN - Strict isolation for non-sovereign roles
  if (!userTenantId || (targetTenantId && userTenantId !== targetTenantId)) {
    broadcastTelemetry(
      userTenantId || 'GLOBAL_ROOT',
      'SECURITY_EVENT',
      'TENANT_ISOLATION_ENFORCED',
      'tenantBypass',
      {
        traceId,
        role: role || 'UNAUTHENTICATED',
        userTenant: userTenantId,
        targetTenant: targetTenantId,
        reason: 'TENANT_MISMATCH',
        severity: 'HIGH',
      }
    );

    return res.status(403).json({
      success: false,
      error: 'TENANT_ISOLATION_ENFORCED',
      message: `Access denied: ${role || 'UNAUTHENTICATED'} cannot access tenant ${targetTenantId || 'UNSPECIFIED'}`,
      required:
        'Sovereign clearance (founder, sovereign, super_admin, admin) or matching tenant ID',
      traceId,
    });
  }

  // ✅ TENANT MATCH - Proceed
  broadcastTelemetry(userTenantId, 'AUTH_EVENT', 'TENANT_ACCESS_GRANTED', 'tenantBypass', {
    traceId,
    role,
    tenantId: userTenantId,
  });
  next();
};

/**
 * @function requireTenantMatch
 * @description Creates middleware that requires the active request tenant to match the supplied tenant id.
 * @param {string} tenantId - Required tenant id.
 * @returns {Function} Express middleware enforcing tenant match.
 * @collaboration Gives legacy routes a reusable tenant-match guard without weakening sovereign bypass rules.
 */
export const requireTenantMatch = (req, res, next) => {
  const { tenantId: userTenantId } = req.user || {};
  const targetTenantId = req.params.tenantId || req.headers['x-tenant-id'];

  if (!userTenantId || (targetTenantId && userTenantId !== targetTenantId)) {
    return res.status(403).json({
      success: false,
      error: 'TENANT_MISMATCH',
      message: 'Tenant ID does not match user context',
    });
  }
  next();
};

// Default export
export default {
  enforceTenantIsolation,
  requireTenantMatch,
};

console.log(`
╔══════════════════════════════════════════════════════════════════════════╗
║              🛡️  TENANT ISOLATION SHIELD ACTIVE - MARS PROTOCOL        ║
║   Sovereign Bypass: ENABLED | 403 Killer: ARMED | Status: BOARDROOM READY ║
╚══════════════════════════════════════════════════════════════════════════╝
`);
