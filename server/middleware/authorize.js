/* eslint-disable */
/**
 * ####################################################################################################
 * # WILSY OS - SOVEREIGN AUTHORIZATION MIDDLEWARE v2.0.0                                            #
 * # [ROLE-BASED ACCESS CONTROL | PERMISSION CHECKING | TENANT ISOLATION]                           #
 * # EPITOME: BIBLICAL WORTH BILLIONS | INSTITUTIONAL GRADE                                          #
 * ####################################################################################################
 *
 * @team Collaboration Notes:
 * - Role-based access control (RBAC) with hierarchy
 * - Permission-based authorization
 * - Tenant isolation and data segregation
 * - Resource ownership verification
 * - 101/10 security standard
 *
 * @last_updated: 2026-03-30
 * @lead_architect: Wilson Khanyezi
 */

// ============================================================================
// CONFIGURATION
// ============================================================================

const AUTHORIZATION_CONFIG = {
  // Role hierarchy (higher index = more privileges)
  roleHierarchy: [
    'user',
    'tenant_admin',
    'compliance_officer',
    'auditor',
    'admin',
    'superadmin'
  ],

  // Permission definitions
  permissions: {
    'user:read': ['user', 'tenant_admin', 'compliance_officer', 'auditor', 'admin', 'superadmin'],
    'user:write': ['user', 'tenant_admin', 'admin', 'superadmin'],
    'user:delete': ['tenant_admin', 'admin', 'superadmin'],
    'tenant:read': ['tenant_admin', 'compliance_officer', 'auditor', 'admin', 'superadmin'],
    'tenant:write': ['tenant_admin', 'admin', 'superadmin'],
    'tenant:delete': ['superadmin'],
    'document:read': ['user', 'tenant_admin', 'compliance_officer', 'auditor', 'admin', 'superadmin'],
    'document:write': ['user', 'tenant_admin', 'admin', 'superadmin'],
    'document:delete': ['tenant_admin', 'admin', 'superadmin'],
    'document:share': ['user', 'tenant_admin', 'admin', 'superadmin'],
    'billing:read': ['tenant_admin', 'compliance_officer', 'auditor', 'admin', 'superadmin'],
    'billing:write': ['tenant_admin', 'admin', 'superadmin'],
    'billing:delete': ['superadmin'],
    'compliance:read': ['compliance_officer', 'auditor', 'admin', 'superadmin'],
    'compliance:write': ['compliance_officer', 'admin', 'superadmin'],
    'compliance:audit': ['auditor', 'admin', 'superadmin'],
    'node:read': ['user', 'tenant_admin', 'admin', 'superadmin'],
    'node:write': ['tenant_admin', 'admin', 'superadmin'],
    'node:delete': ['superadmin'],
    'admin:read': ['admin', 'superadmin'],
    'admin:write': ['admin', 'superadmin'],
    'admin:delete': ['superadmin'],
    'system:configure': ['superadmin'],
    'system:monitor': ['admin', 'superadmin'],
    'system:audit': ['auditor', 'admin', 'superadmin']
  },

  resourceTypes: {
    USER: 'user',
    TENANT: 'tenant',
    DOCUMENT: 'document',
    NODE: 'node',
    INVOICE: 'invoice',
    API_KEY: 'apiKey'
  }
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

const hasRequiredRole = (userRole, requiredRoles) => {
  if (!userRole) return false;
  const roles = Array.isArray(requiredRoles) ? requiredRoles : [requiredRoles];
  const userRoleIndex = AUTHORIZATION_CONFIG.roleHierarchy.indexOf(userRole);
  if (userRoleIndex === -1) return false;
  return roles.some(role => {
    if (role === '*') return true;
    const requiredIndex = AUTHORIZATION_CONFIG.roleHierarchy.indexOf(role);
    return requiredIndex !== -1 && userRoleIndex >= requiredIndex;
  });
};

const hasPermission = (userRole, permission) => {
  if (!userRole || !permission) return false;
  const allowedRoles = AUTHORIZATION_CONFIG.permissions[permission];
  if (!allowedRoles) return false;
  return allowedRoles.includes(userRole) || allowedRoles.includes('*');
};

const isResourceOwner = (user, resource, resourceType) => {
  if (!user || !resource) return false;
  switch (resourceType) {
    case 'user': return resource._id.toString() === user.id.toString();
    case 'tenant': return resource.tenantId?.toString() === user.tenantId?.toString();
    case 'document': return resource.createdBy?.toString() === user.id.toString() ||
           resource.tenantId?.toString() === user.tenantId?.toString();
    case 'node': return resource.tenantId?.toString() === user.tenantId?.toString();
    case 'invoice': return resource.tenantId?.toString() === user.tenantId?.toString();
    case 'apiKey': return resource.userId?.toString() === user.id.toString() ||
           resource.tenantId?.toString() === user.tenantId?.toString();
    default: return false;
  }
};

// ============================================================================
// AUTHORIZATION MIDDLEWARE
// ============================================================================

export const authorize = (roles, options = {}) => {
  const { requireAll = false, allowOwner = false, resourceType = null, resourceIdParam = 'id', errorMessage = 'Insufficient permissions' } = options;

  return async (req, res, next) => {
    try {
      if (!req.user) {
        return res.status(401).json({ success: false, error: 'UNAUTHORIZED', message: 'Authentication required' });
      }

      const userRole = req.user.role;
      if (userRole === 'superadmin') return next();

      let authorized = false;
      if (requireAll && Array.isArray(roles)) {
        authorized = roles.every(role => hasRequiredRole(userRole, role));
      } else {
        authorized = hasRequiredRole(userRole, roles);
      }

      if (!authorized && allowOwner && resourceType) {
        const resourceId = req.params[resourceIdParam] || req.body[resourceIdParam] || req.query[resourceIdParam];
        if (resourceId) {
          const resource = { id: resourceId, tenantId: req.user.tenantId };
          authorized = isResourceOwner(req.user, resource, resourceType);
        }
      }

      if (!authorized) {
        return res.status(403).json({ success: false, error: 'FORBIDDEN', message: errorMessage, required: roles, userRole });
      }
      next();
    } catch (error) {
      console.error('[AUTHORIZE] Error:', error);
      return res.status(500).json({ success: false, error: 'AUTHORIZATION_ERROR', message: 'An error occurred during authorization' });
    }
  };
};

export const authorizePermission = (permission, options = {}) => {
  const { allowOwner = false, resourceType = null, resourceIdParam = 'id', errorMessage = 'Insufficient permissions' } = options;

  return async (req, res, next) => {
    try {
      if (!req.user) {
        return res.status(401).json({ success: false, error: 'UNAUTHORIZED', message: 'Authentication required' });
      }
      const userRole = req.user.role;
      if (userRole === 'superadmin') return next();

      let authorized = hasPermission(userRole, permission);
      if (!authorized && allowOwner && resourceType) {
        const resourceId = req.params[resourceIdParam] || req.body[resourceIdParam] || req.query[resourceIdParam];
        if (resourceId) {
          const resource = { id: resourceId, tenantId: req.user.tenantId };
          authorized = isResourceOwner(req.user, resource, resourceType);
        }
      }

      if (!authorized) {
        return res.status(403).json({ success: false, error: 'FORBIDDEN', message: errorMessage, required: permission, userRole });
      }
      next();
    } catch (error) {
      console.error('[AUTHORIZE] Error:', error);
      return res.status(500).json({ success: false, error: 'AUTHORIZATION_ERROR', message: 'An error occurred during authorization' });
    }
  };
};

export const authorizeOwner = (resourceType, options = {}) => {
  const { resourceIdParam = 'id', errorMessage = 'You do not own this resource', allowAdmins = true } = options;

  return async (req, res, next) => {
    try {
      if (!req.user) return res.status(401).json({ success: false, error: 'UNAUTHORIZED', message: 'Authentication required' });
      const userRole = req.user.role;
      if (userRole === 'superadmin') return next();
      if (allowAdmins && (userRole === 'admin' || userRole === 'tenant_admin')) return next();

      const resourceId = req.params[resourceIdParam] || req.body[resourceIdParam] || req.query[resourceIdParam];
      if (!resourceId) {
        return res.status(400).json({ success: false, error: 'RESOURCE_ID_REQUIRED', message: 'Resource ID is required' });
      }

      const resource = { id: resourceId, tenantId: req.user.tenantId };
      const isOwner = isResourceOwner(req.user, resource, resourceType);
      if (!isOwner) {
        return res.status(403).json({ success: false, error: 'FORBIDDEN', message: errorMessage });
      }
      next();
    } catch (error) {
      console.error('[AUTHORIZE] Error:', error);
      return res.status(500).json({ success: false, error: 'AUTHORIZATION_ERROR', message: 'An error occurred during authorization' });
    }
  };
};

export const authorizeTenant = (options = {}) => {
  const { errorMessage = 'Access to this tenant is forbidden', allowSuperadmin = true } = options;

  return async (req, res, next) => {
    try {
      if (!req.user) return res.status(401).json({ success: false, error: 'UNAUTHORIZED', message: 'Authentication required' });
      if (allowSuperadmin && req.user.role === 'superadmin') return next();

      const requestedTenantId = req.params.tenantId || req.body.tenantId || req.query.tenantId || req.headers['x-tenant-id'];
      if (!requestedTenantId) return next();

      if (req.user.tenantId?.toString() !== requestedTenantId.toString()) {
        return res.status(403).json({ success: false, error: 'FORBIDDEN', message: errorMessage });
      }
      next();
    } catch (error) {
      console.error('[AUTHORIZE] Error:', error);
      return res.status(500).json({ success: false, error: 'AUTHORIZATION_ERROR', message: 'An error occurred during authorization' });
    }
  };
};

export const authorizeAll = (permissions, options = {}) => {
  const { requireAll = true, errorMessage = 'Insufficient permissions' } = options;

  return async (req, res, next) => {
    try {
      if (!req.user) return res.status(401).json({ success: false, error: 'UNAUTHORIZED', message: 'Authentication required' });
      const userRole = req.user.role;
      if (userRole === 'superadmin') return next();

      let authorized;
      if (requireAll) {
        authorized = permissions.every(perm => hasPermission(userRole, perm));
      } else {
        authorized = permissions.some(perm => hasPermission(userRole, perm));
      }

      if (!authorized) {
        return res.status(403).json({ success: false, error: 'FORBIDDEN', message: errorMessage, required: permissions, userRole });
      }
      next();
    } catch (error) {
      console.error('[AUTHORIZE] Error:', error);
      return res.status(500).json({ success: false, error: 'AUTHORIZATION_ERROR', message: 'An error occurred during authorization' });
    }
  };
};

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

export const getUserPermissions = (user) => {
  if (!user || !user.role) return [];
  const permissions = [];
  for (const [permission, allowedRoles] of Object.entries(AUTHORIZATION_CONFIG.permissions)) {
    if (allowedRoles.includes(user.role) || allowedRoles.includes('*')) {
      permissions.push(permission);
    }
  }
  return permissions;
};

export const hasAnyRole = (user, roles) => {
  if (!user || !user.role) return false;
  return roles.includes(user.role);
};

export const hasAllRoles = (user, roles) => {
  if (!user || !user.role) return false;
  return roles.every(role => role === user.role);
};

export const getRoleLevel = (role) => AUTHORIZATION_CONFIG.roleHierarchy.indexOf(role);

export const isRoleHigherOrEqual = (role1, role2) => {
  const level1 = getRoleLevel(role1);
  const level2 = getRoleLevel(role2);
  return level1 !== -1 && level2 !== -1 && level1 >= level2;
};

export default {
  authorize,
  authorizePermission,
  authorizeOwner,
  authorizeTenant,
  authorizeAll,
  getUserPermissions,
  hasAnyRole,
  hasAllRoles,
  getRoleLevel,
  isRoleHigherOrEqual,
  AUTHORIZATION_CONFIG
};
