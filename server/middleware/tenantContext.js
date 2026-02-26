/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - TENANT CONTEXT MIDDLEWARE                                      ║
 * ║ [Multi-Tenant Isolation | POPIA §19 | Forensic Traceability]              ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 * 
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/middleware/tenantContext.js
 * VERSION: 1.0.0
 * CREATED: 2026-02-26
 * 
 * PURPOSE:
 * • Extracts and validates tenant context from requests
 * • Ensures multi-tenant isolation for all operations
 * • Adds tenantId to request object for downstream use
 * • Validates tenant ID format and access permissions
 */

import logger from '../utils/logger.js';

/**
 * Tenant Context Middleware
 * Extracts tenant information from headers and validates it
 */
export const extractTenant = (req, res, next) => {
  try {
    // Extract tenant ID from various sources (header, query, user)
    const tenantId = req.headers['x-tenant-id'] || 
                     req.query.tenantId || 
                     req.body?.tenantId ||
                     req.user?.tenantId;

    // Validate tenant ID format (if provided)
    if (tenantId) {
      const tenantIdRegex = /^[a-zA-Z0-9_-]{8,64}$/;
      if (!tenantIdRegex.test(tenantId)) {
        logger.warn('Invalid tenant ID format', { 
          tenantId, 
          path: req.path,
          ip: req.ip 
        });
        
        return res.status(400).json({
          error: 'INVALID_TENANT_ID',
          message: 'Tenant ID must be 8-64 alphanumeric characters'
        });
      }
      
      // Attach to request object
      req.tenantContext = {
        tenantId,
        extractedFrom: tenantId === req.headers['x-tenant-id'] ? 'header' :
                       tenantId === req.query.tenantId ? 'query' :
                       tenantId === req.body?.tenantId ? 'body' : 'user'
      };
    }

    next();
  } catch (error) {
    logger.error('Tenant context extraction failed', { error: error.message });
    next(error);
  }
};

/**
 * Validate tenant access middleware
 * Ensures user has access to the requested tenant
 */
export const validateTenantAccess = (req, res, next) => {
  const userTenantId = req.user?.tenantId;
  const requestTenantId = req.tenantContext?.tenantId;

  // If no tenant context, skip validation
  if (!requestTenantId) {
    return next();
  }

  // If user is super admin (Wilson), allow all
  if (req.user?.email?.includes('wilson') || req.user?.role === 'super_admin') {
    return next();
  }

  // Check if user has access to this tenant
  if (userTenantId && userTenantId !== requestTenantId) {
    logger.warn('Tenant access violation', {
      userTenantId,
      requestTenantId,
      userId: req.user?.id,
      path: req.path
    });

    return res.status(403).json({
      error: 'TENANT_ACCESS_DENIED',
      message: 'You do not have access to this tenant'
    });
  }

  next();
};

/**
 * Get current tenant context
 */
export const getTenantContext = (req) => {
  return req.tenantContext || null;
};

export default {
  extractTenant,
  validateTenantAccess,
  getTenantContext
};
