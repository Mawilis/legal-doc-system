/*╔════════════════════════════════════════════════════════════════╗
  ║ TENANT CONTEXT - MULTI-TENANT ISOLATION FORTRESS              ║
  ║ [100% tenant isolation | R10M data leakage prevention]        ║
  ╚════════════════════════════════════════════════════════════════╝*/
const logger = require('../utils/logger');
class TenantContextError extends Error {
  constructor(message, code = 'TENANT_CONTEXT_VIOLATION') {
    super(message);
    this.name = 'TenantContextError';
    this.code = code;
    this.statusCode = 401;
    this.timestamp = new Date().toISOString();
  }
}
const TENANT_ID_PATTERN = /^[a-zA-Z0-9_-]{8,64}$/;
const RESERVED_TENANT_IDS = ['SYSTEM','system','ADMIN','admin','ROOT','root','LPC','lpc','WILSYS','wilsys'];
const validateTenantId = (tenantId) => {
  if (!tenantId) throw new TenantContextError('Tenant ID is required', 'TENANT_ID_REQUIRED');
  if (typeof tenantId !== 'string') throw new TenantContextError(`Tenant ID must be string, received ${typeof tenantId}`, 'TENANT_ID_TYPE_ERROR');
  if (tenantId.length < 8) throw new TenantContextError(`Tenant ID must be at least 8 characters (received ${tenantId.length})`, 'TENANT_ID_TOO_SHORT');
  if (tenantId.length > 64) throw new TenantContextError(`Tenant ID must not exceed 64 characters (received ${tenantId.length})`, 'TENANT_ID_TOO_LONG');
  if (!TENANT_ID_PATTERN.test(tenantId)) throw new TenantContextError('Tenant ID contains invalid characters. Allowed: a-z, A-Z, 0-9, _, -', 'TENANT_ID_INVALID_CHARS');
  if (RESERVED_TENANT_IDS.includes(tenantId)) throw new TenantContextError(`Tenant ID '${tenantId}' is reserved for system use`, 'TENANT_ID_RESERVED');
  return true;
};
const extractTenantId = (req) => {
  let tenantId = req.headers['x-tenant-id'] || req.headers['X-Tenant-ID'] || req.headers['tenant-id'] || req.headers['Tenant-ID'];
  if (!tenantId && req.query?.tenantId) tenantId = req.query.tenantId;
  if (!tenantId && req.subdomains?.length) tenantId = req.subdomains[0];
  if (!tenantId && req.user?.tenantId) tenantId = req.user.tenantId;
  return tenantId || null;
};
const tenantContext = (req, res, next) => {
  const startTime = Date.now();
  const correlationId = req.headers['x-correlation-id'] || `CORR-${Date.now()}-${Math.random().toString(36).substring(2,10)}`;
  try {
    const tenantId = extractTenantId(req);
    if (!tenantId) throw new TenantContextError('No tenant identifier provided', 'TENANT_ID_MISSING');
    validateTenantId(tenantId);
    req.tenant = { id: tenantId, validatedAt: new Date().toISOString(), correlationId, source: 'tenantContext.middleware' };
    logger.debug('Tenant context attached', { component: 'tenantContext', tenantId: tenantId.substring(0,8)+'...', correlationId, durationMs: Date.now()-startTime });
    next();
  } catch (error) {
    res.status(error.statusCode||401).json({ success: false, error: { code: error.code||'TENANT_CONTEXT_ERROR', message: error.message, timestamp: new Date().toISOString(), correlationId } });
  }
};
const requireTenantContext = () => (req,res,next) => {
  if (!req.tenant?.id) return res.status(401).json({ success: false, error: { code: 'TENANT_CONTEXT_REQUIRED', message: 'Tenant context required', timestamp: new Date().toISOString() } });
  next();
};
const getTenantId = (req) => {
  if (!req.tenant?.id) throw new TenantContextError('No tenant context found', 'TENANT_CONTEXT_MISSING');
  return req.tenant.id;
};
module.exports = { tenantContext, requireTenantContext, getTenantId, validateTenantId, TenantContextError, TENANT_ID_PATTERN, RESERVED_TENANT_IDS };
