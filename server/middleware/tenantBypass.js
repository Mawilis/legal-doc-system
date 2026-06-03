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
 * 🛡️ enforceTenantIsolation
 * @description Middleware that enforces tenant isolation unless the role is in SovereignBypassRoles
 * * LOGIC:
 * 1. If role can bypass tenant isolation (founder, sovereign, super_admin, admin) → ALLOW immediately
 * 2. Otherwise, enforce strict tenant matching
 * 3. If tenant mismatch → 403 FORBIDDEN with clear error message
 * * @param {Object} req - Express request object (expects req.user with role and tenantId)
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
export const enforceTenantIsolation = (req, res, next) => {
  const { role, tenantId: userTenantId } = req.user || {};
  const targetTenantId = req.params.tenantId || req.headers['x-tenant-id'];
  const traceId = req.headers['x-trace-id'] || `TRC-TENANT-${Date.now()}`;

  // 🚀 SOVEREIGN BYPASS - Registry decides, not hardcoded strings
  if (canBypassTenant(role)) {
    broadcastTelemetry(userTenantId || 'GLOBAL_ROOT', 'AUTH_EVENT', 'TENANT_BYPASS', 'tenantBypass', {
      traceId,
      role,
      targetTenant: targetTenantId,
      reason: 'SOVEREIGN_BYPASS_GRANTED'
    });
    return next();
  }

  // 🔒 TENANT LOCKDOWN - Strict isolation for non-sovereign roles
  if (!userTenantId || (targetTenantId && userTenantId !== targetTenantId)) {
    broadcastTelemetry(userTenantId || 'GLOBAL_ROOT', 'SECURITY_EVENT', 'TENANT_ISOLATION_ENFORCED', 'tenantBypass', {
      traceId,
      role: role || 'UNAUTHENTICATED',
      userTenant: userTenantId,
      targetTenant: targetTenantId,
      reason: 'TENANT_MISMATCH',
      severity: 'HIGH'
    });

    return res.status(403).json({
      success: false,
      error: 'TENANT_ISOLATION_ENFORCED',
      message: `Access denied: ${role || 'UNAUTHENTICATED'} cannot access tenant ${targetTenantId || 'UNSPECIFIED'}`,
      required: 'Sovereign clearance (founder, sovereign, super_admin, admin) or matching tenant ID',
      traceId
    });
  }

  // ✅ TENANT MATCH - Proceed
  broadcastTelemetry(userTenantId, 'AUTH_EVENT', 'TENANT_ACCESS_GRANTED', 'tenantBypass', {
    traceId,
    role,
    tenantId: userTenantId
  });
  next();
};

/**
 * 🛡️ requireTenantMatch
 * @description Simplified version for routes that don't need bypass logic
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
export const requireTenantMatch = (req, res, next) => {
  const { tenantId: userTenantId } = req.user || {};
  const targetTenantId = req.params.tenantId || req.headers['x-tenant-id'];

  if (!userTenantId || (targetTenantId && userTenantId !== targetTenantId)) {
    return res.status(403).json({
      success: false,
      error: 'TENANT_MISMATCH',
      message: 'Tenant ID does not match user context'
    });
  }
  next();
};

// Default export
export default {
  enforceTenantIsolation,
  requireTenantMatch
};

console.log(`
╔══════════════════════════════════════════════════════════════════════════╗
║              🛡️  TENANT ISOLATION SHIELD ACTIVE - MARS PROTOCOL        ║
║   Sovereign Bypass: ENABLED | 403 Killer: ARMED | Status: BOARDROOM READY ║
╚══════════════════════════════════════════════════════════════════════════╝
`);
