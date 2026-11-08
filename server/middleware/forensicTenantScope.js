/**
 * TITLE: WILSY EOS Authenticated Forensic Tenant Scope
 * VERSION: v1.0.1
 * AUTHORITY: WILSY EOS Security Engineering; request-scope validation only
 * EPITOME: Binds every forensic route to the tenant already established by canonical authentication and tenant middleware.
 * ABSOLUTE PATH: server/middleware/forensicTenantScope.js
 * COLLABORATION: WILSY EOS API Engineering; consumed by forensicRoutes.
 * CHANGELOG:
 * - v1.0.0: Reject caller-selected tenant scope and expose only authenticated request tenant.
 * - v1.0.1: Add the mandatory sovereign artifact end seal.
 * TENANT BOUNDARY: Caller parameters, query, body and headers can never establish tenant authority.
 * SECURITY POSTURE: Missing, inconsistent or mismatched scope fails closed with HTTP 403.
 * AUTHORITY BOUNDARY: This module grants no role or permission; upstream authentication and IAM remain authoritative.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */

const readSuppliedTenantScopes = (request) => [
  request?.params?.tenantId,
  request?.query?.tenantId,
  request?.body?.tenantId,
  request?.headers?.['x-tenant-id'],
  request?.headers?.['x-wilsy-tenant-id'],
];

export function resolveForensicTenantScope(request) {
  const authenticatedTenantId =
    typeof request?.tenantId === 'string' ? request.tenantId.trim() : '';
  if (!authenticatedTenantId || !request?.user) return null;

  const principalTenantId =
    typeof request.user.tenantId === 'string' ? request.user.tenantId.trim() : '';
  if (
    principalTenantId &&
    principalTenantId.toUpperCase() !== authenticatedTenantId.toUpperCase()
  ) {
    return null;
  }

  const expected = authenticatedTenantId.toUpperCase();
  for (const supplied of readSuppliedTenantScopes(request)) {
    if (supplied === undefined || supplied === null || supplied === '') continue;
    if (typeof supplied !== 'string' || supplied.trim().toUpperCase() !== expected) {
      return null;
    }
  }

  return authenticatedTenantId;
}

export function requireForensicTenantScope(request, response, next) {
  const tenantId = resolveForensicTenantScope(request);
  if (!tenantId) {
    return response.status(403).json({
      success: false,
      code: 'FORENSIC_TENANT_SCOPE_INVALID',
    });
  }

  request.forensicTenantId = tenantId;
  return next();
}

/*
 * ARTIFACT: WILSY EOS Authenticated Forensic Tenant Scope
 * VERSION: v1.0.1
 * AUTHORITY BOUNDARY: Validates scope only; canonical authentication and IAM remain authoritative.
 * TENANT POSTURE: Uses the middleware-established tenant and rejects mismatched path/query/body/header hints.
 * FAIL-CLOSED POSTURE: Missing, inconsistent or caller-selected tenant scope returns HTTP 403.
 * FINANCIAL EXECUTION AUTHORITY: None.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
