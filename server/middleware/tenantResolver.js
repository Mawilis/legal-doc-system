/* eslint-disable */
import TenantConfig from '../models/TenantConfig.js';
import chalk from 'chalk';
import { broadcastTelemetry } from '../utils/telemetryHelper.js';

const CANONICAL_TENANT_ID = 'WILSYTENANT-4CD2FZ4O';

export const resolveTenant = async (req, res, next) => {
  const start = Date.now();
  let retryCount = 0;
  const MAX_RETRIES = 2;

  try {
    const rawId = req.user?.tenantId || req.headers['x-tenant-id'] || req.query?.tenantId || req.body?.tenantId;
    if (typeof rawId !== 'string' || !rawId.trim()) {
      return res.status(400).json({ success: false, code: 'TENANT_CONTEXT_REQUIRED' });
    }

    const requestedTenantId = rawId.toUpperCase().trim();
    if (requestedTenantId !== CANONICAL_TENANT_ID) {
      return res.status(403).json({ success: false, code: 'TENANT_NOT_AUTHORIZED' });
    }

    let tenant = null;
    while (retryCount <= MAX_RETRIES) {
      tenant = await TenantConfig.findOne({
        tenantId: CANONICAL_TENANT_ID,
        status: 'ACTIVE',
      }).lean();

      if (!tenant) {
        tenant = await TenantConfig.db.collection('tenants').findOne({
          tenant_id: CANONICAL_TENANT_ID,
          status: 'ACTIVE',
        });
      }

      if (tenant) break;
      retryCount += 1;
      if (retryCount <= MAX_RETRIES) {
        await new Promise((resolve) => setTimeout(resolve, 50));
      }
    }

    if (!tenant) {
      broadcastTelemetry('SYSTEM', 'RESOLUTION_FAILURE', 'SYSTEM_GATEWAY', 'CANONICAL_TENANT_NOT_FOUND', {
        requestedTenantId,
        ip: req.ip,
        timestamp: new Date(),
      });
      return res.status(403).json({
        success: false,
        code: 'CANONICAL_TENANT_NOT_FOUND',
        message: 'The canonical WILSY tenant is not active.',
      });
    }

    const whitelist = tenant.securitySettings?.ipWhitelisting || [];
    if (whitelist.length > 0 && !whitelist.includes(req.ip)) {
      broadcastTelemetry(CANONICAL_TENANT_ID, 'SECURITY_VIOLATION', 'IP_SENTINEL', 'UNAUTHORIZED_IP', { ip: req.ip });
      return res.status(403).json({
        success: false,
        code: 'IP_SENTINEL_BLOCK',
        message: 'Access denied: IP address not authorized for this tenant.',
      });
    }

    if (tenant.status !== 'ACTIVE') {
      return res.status(403).json({
        success: false,
        code: 'TENANT_INACTIVE',
        message: `WILSY tenant is currently ${tenant.status}.`,
      });
    }

    req.tenant = tenant;
    req.tenantId = CANONICAL_TENANT_ID;
    global.currentTenantId = CANONICAL_TENANT_ID;

    broadcastTelemetry(CANONICAL_TENANT_ID, 'RESOLUTION_SUCCESS', 'SYSTEM_GATEWAY', 'TENANT_ANCHORED', {
      latency: `${Date.now() - start}ms`,
      retries: retryCount,
      method: req.method,
    });

    console.log(`${chalk.green('TENANT VERIFIED:')} ${chalk.white(tenant.name || 'WILSY')} | ${chalk.yellow(CANONICAL_TENANT_ID)}`);
    return next();
  } catch (error) {
    console.error(chalk.red('[TENANT RESOLVER FAILURE]:'), error.stack);
    return res.status(500).json({
      success: false,
      code: 'TENANT_RESOLUTION_FAILED',
      message: 'EOS could not establish the canonical tenant context.',
    });
  }
};

export default resolveTenant;
