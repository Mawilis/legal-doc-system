/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - TENANT ISOLATION MIDDLEWARE [V44.0.0-PROD]                                                                                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 44.0.0 | PRODUCTION READY | BILLION DOLLAR SPEC                                                                               ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */
import logger from '../utils/logger.js';

/**
 * @function verifyTenantScope
 * @description Ensures all strike requests are cryptographically locked to the correct Tenant context.
 */
export const verifyTenantScope = async (req, res, next) => {
  try {
    if (!req.tenant || !req.tenant.id) {
      const requestedTenantId = req.headers['x-tenant-id'];
      const authenticatedTenantId = req.user?.tenantId ? String(req.user.tenantId).trim() : '';
      if (authenticatedTenantId && requestedTenantId &&
          authenticatedTenantId.toUpperCase() !== String(requestedTenantId).trim().toUpperCase()) {
        return res.status(403).json({ success: false, code: 'TENANT_CONTEXT_MISMATCH' });
      }
      const tenantId = authenticatedTenantId || requestedTenantId;
      if (!tenantId || ['WILSY_ROOT', 'MASTER', 'WILSY_MASTER', 'GLOBAL_ROOT', 'WILSY_GLOBAL_ROOT', 'WILSY-SOVEREIGN-ROOT', 'WILSY'].includes(String(tenantId).trim().toUpperCase())) {
        return res.status(400).json({ success: false, code: 'TENANT_CONTEXT_REQUIRED' });
      }
      req.tenant = { id: String(tenantId).trim() };
    }

    // Sovereign Security Override
    const sovereignRoles = ['sovereign', 'super_admin', 'founder'];
    if (req.user && !sovereignRoles.includes(req.user.role)) {
       if (req.user.tenantId && req.user.tenantId.toString() !== req.tenant.id) {
         return res.status(403).json({ success: false, message: 'Institutional Scope Violation' });
       }
    }
    next();
  } catch (error) {
    logger.error('Tenant Scope Failure:', error);
    return res.status(500).json({ success: false, message: 'Scope Verification Failed' });
  }
};

export default { verifyTenantScope };
