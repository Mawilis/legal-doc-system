/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║  👑 WILSY OS 2050 - ROLE HIERARCHY                                       ║
  ║  Supreme Multi-Tenant Role Architecture with Forensic Compliance          ║
  ║  Supreme Architect: Wilson Khanyezi - 10th Generation                     ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

/**
 * Roles define the authority levels across Wilsy OS.
 * Each role is mapped to a hierarchy score and explicit permissions.
 * This file is investor‑grade: immutable, auditable, and forensic‑ready.
 */

export const ROLES = Object.freeze({
  // 🔒 Global System Roles
  SUPER_ADMIN: 'super_admin',

  // 🏢 Tenant Level Roles
  TENANT_OWNER: 'tenant_owner',
  TENANT_ADMIN: 'tenant_admin',
  TENANT_MANAGER: 'tenant_manager',
  TENANT_AUDITOR: 'tenant_auditor',

  // 👥 Standard User Roles
  USER_ADMIN: 'user_admin',
  USER_MANAGER: 'user_manager',
  USER_EDITOR: 'user_editor',
  USER_VIEWER: 'user_viewer',

  // 🌍 External Roles
  CLIENT: 'client',
  GUEST: 'guest'
});

/**
 * Hierarchy scores define comparative authority.
 * Higher numbers = greater authority.
 */
export const ROLE_HIERARCHY = Object.freeze({
  [ROLES.SUPER_ADMIN]: 1000,
  [ROLES.TENANT_OWNER]: 900,
  [ROLES.TENANT_ADMIN]: 800,
  [ROLES.TENANT_MANAGER]: 700,
  [ROLES.TENANT_AUDITOR]: 600,
  [ROLES.USER_ADMIN]: 500,
  [ROLES.USER_MANAGER]: 400,
  [ROLES.USER_EDITOR]: 300,
  [ROLES.USER_VIEWER]: 200,
  [ROLES.CLIENT]: 100,
  [ROLES.GUEST]: 0
});

/**
 * Permissions define explicit capabilities.
 * Each role is mapped to a set of allowed actions.
 * Compliance tags can be attached for forensic audits.
 */
export const ROLE_PERMISSIONS = Object.freeze({
  [ROLES.SUPER_ADMIN]: [
    'system:configure','tenant:create','tenant:delete','tenant:manage_all',
    'user:manage_all','audit:view_all','billing:manage_all','compliance:override'
  ],

  [ROLES.TENANT_OWNER]: [
    'tenant:configure','tenant:delete','tenant:billing','tenant:upgrade','tenant:downgrade',
    'admin:manage','audit:view_tenant','user:manage_all_tenant','compliance:view_tenant'
  ],

  [ROLES.TENANT_ADMIN]: [
    'tenant:view_settings','tenant:edit_settings','user:create','user:read','user:update',
    'user:delete','user:assign_roles','user:suspend','audit:view_tenant','reports:generate'
  ],

  [ROLES.TENANT_MANAGER]: [
    'user:create','user:read','user:update','reports:generate','content:manage'
  ],

  [ROLES.TENANT_AUDITOR]: [
    'audit:view_tenant','reports:view','compliance:view'
  ],

  [ROLES.USER_ADMIN]: [
    'user:create','user:read','user:update','user:delete','roles:assign_basic'
  ],

  [ROLES.USER_MANAGER]: [
    'user:create','user:read','user:update'
  ],

  [ROLES.USER_EDITOR]: [
    'content:create','content:update','content:delete'
  ],

  [ROLES.USER_VIEWER]: [
    'content:read','reports:view_basic'
  ],

  [ROLES.CLIENT]: [
    'documents:view_own','profile:edit_own'
  ],

  [ROLES.GUEST]: [
    'public:view'
  ]
});

/**
 * Compare two roles by hierarchy.
 * Returns true if role1 outranks role2.
 */
export const isRoleHigher = (role1, role2) => {
  return (ROLE_HIERARCHY[role1] || 0) > (ROLE_HIERARCHY[role2] || 0);
};

/**
 * Check if a role has a specific permission.
 * Returns true if permission is explicitly granted.
 */
export const hasPermission = (role, permission) => {
  const permissions = ROLE_PERMISSIONS[role] || [];
  return permissions.includes(permission) || permissions.includes('*');
};

/**
 * Forensic wrapper: returns full role profile for audit logging.
 */
export const getRoleProfile = (role) => {
  return {
    role,
    hierarchy: ROLE_HIERARCHY[role] || 0,
    permissions: ROLE_PERMISSIONS[role] || [],
    complianceTags: ['ISO27001','SOC2','POPIA'] // default compliance tags
  };
};
