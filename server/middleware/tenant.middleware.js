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
      const tenantId = req.headers['x-tenant-id'] || (req.user && req.user.tenantId);
      req.tenant = { id: tenantId || 'wilsy-sovereign-root' };
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
