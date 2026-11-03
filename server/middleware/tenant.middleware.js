/* eslint-disable */
import logger from '../utils/logger.js';

const CANONICAL_TENANT_ID = 'WILSYTENANT-4CD2FZ4O';

/**
 * Ensures every request is scoped to the one canonical WILSY tenant.
 * Elevated roles do not grant cross-tenant scope.
 */
export const verifyTenantScope = async (req, res, next) => {
  try {
    const authenticatedTenantId = req.user?.tenantId
      ? String(req.user.tenantId).trim().toUpperCase()
      : '';
    const requestedTenantId = req.headers?.['x-tenant-id']
      ? String(req.headers['x-tenant-id']).trim().toUpperCase()
      : '';
    const attachedTenantId = req.tenant?.id || req.tenant?.tenantId
      ? String(req.tenant.id || req.tenant.tenantId).trim().toUpperCase()
      : '';

    for (const tenantId of [authenticatedTenantId, requestedTenantId, attachedTenantId]) {
      if (tenantId && tenantId !== CANONICAL_TENANT_ID) {
        return res.status(403).json({ success: false, code: 'TENANT_NOT_AUTHORIZED' });
      }
    }

    if (!authenticatedTenantId && !requestedTenantId && !attachedTenantId) {
      return res.status(400).json({ success: false, code: 'TENANT_CONTEXT_REQUIRED' });
    }

    req.tenantId = CANONICAL_TENANT_ID;
    req.tenant = req.tenant || { id: CANONICAL_TENANT_ID };
    req.tenant.id = CANONICAL_TENANT_ID;

    return next();
  } catch (error) {
    logger.error('Tenant Scope Failure:', error);
    return res.status(500).json({ success: false, code: 'TENANT_SCOPE_VERIFICATION_FAILED' });
  }
};

export default { verifyTenantScope };
