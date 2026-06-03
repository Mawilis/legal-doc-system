/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN ACCESS CONTROL HOOK [V2.0.0-ZERO-TRUST-EXECUTIVE]                                                               ║
 * ║ [ROLE NORMALISATION | TENANT ISOLATION | NO FALLBACK OMEGA | DYNAMIC PERMISSIONS | EXECUTIVE GATES]                                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 2.0.0-ZERO-TRUST-EXECUTIVE | PRODUCTION READY | TENANT-SAFE ACCESS ADJUDICATION                                             ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/hooks/useSovereignAccess.js                                          ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO/Lead Architect) - Mandated that only the real founder/Omega identity can cross tenant boundaries.      ║
 * ║ • AI Engineering (Codex) - RECTIFIED: Removed unsafe super-admin fallback and added permission-aware tenant role normalisation.       ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import { useEffect, useMemo, useState } from 'react';
import { useAuth } from '../contexts/authContext';

const ROLE_LEVELS = Object.freeze({
  super_admin: 100,
  founder: 100,
  omega: 100,
  executive: 90,
  admin: 80,
  tenant_owner: 70,
  tenant_manager: 60,
  finance: 58,
  operations_manager: 56,
  sales_representative: 50,
  user: 10,
  unauthenticated: 0
});

const ROLE_ALIASES = Object.freeze({
  SUPER_ADMIN: 'super_admin',
  FOUNDER: 'super_admin',
  OMEGA: 'super_admin',
  CEO: 'executive',
  DIRECTOR: 'executive',
  EXECUTIVE: 'executive',
  TENANT_OWNER: 'tenant_owner',
  OWNER: 'tenant_owner',
  TENANT_ADMIN: 'tenant_owner',
  ADMIN: 'admin',
  TENANT_MANAGER: 'tenant_manager',
  OPERATIONS_MANAGER: 'operations_manager',
  SALES: 'sales_representative',
  SALES_REP: 'sales_representative',
  SALES_REPRESENTATIVE: 'sales_representative',
  FINANCE: 'finance',
  USER: 'user'
});

const ROLE_PERMISSIONS = Object.freeze({
  super_admin: [
    'executive_dashboard',
    'view_all_analytics',
    'view_all_tenants',
    'manage_users',
    'manage_tenants',
    'view_revenue',
    'view_forecasts',
    'view_risk',
    'export_reports',
    'view_investor_kpis',
    'view_quantum_forecasts',
    'view_user_activity',
    'view_tenant_performance',
    'generate_investor_report',
    'audit_logs',
    'wilsy_ai_license'
  ],
  executive: [
    'executive_dashboard',
    'view_all_tenants',
    'view_revenue',
    'view_forecasts',
    'view_risk',
    'export_reports',
    'view_investor_kpis',
    'view_quantum_forecasts',
    'view_tenant_performance',
    'generate_investor_report',
    'wilsy_ai_license'
  ],
  admin: [
    'view_system_health',
    'view_performance',
    'view_audit_logs',
    'manage_users',
    'view_revenue',
    'view_risk'
  ],
  tenant_owner: [
    'executive_dashboard',
    'view_tenant_revenue',
    'view_tenant_forecasts',
    'view_tenant_risk',
    'export_reports',
    'view_tenant_performance',
    'view_user_activity',
    'wilsy_ai_license'
  ],
  tenant_manager: [
    'view_tenant_revenue',
    'view_tenant_forecasts',
    'view_tenant_risk',
    'view_tenant_performance',
    'view_user_activity'
  ],
  finance: [
    'view_tenant_revenue',
    'view_revenue',
    'export_reports'
  ],
  operations_manager: [
    'view_tenant_performance',
    'view_user_activity'
  ],
  sales_representative: [
    'view_revenue',
    'view_forecasts',
    'view_tenant_dashboard',
    'view_user_activity'
  ],
  user: [
    'view_personal_activity'
  ],
  unauthenticated: []
});

/**
 * @function normalizeSovereignRole
 * @description Converts backend and local-storage role aliases into a canonical access role.
 * @param {string} role - Raw role value.
 * @returns {string} Canonical role.
 * @collaboration Keeps founder/Omega authority explicit while allowing tenant business roles to route to the right modules.
 */
export const normalizeSovereignRole = (role = 'unauthenticated') => {
  const raw = String(role || 'unauthenticated').trim();
  const upper = raw.toUpperCase();
  return ROLE_ALIASES[upper] || raw.toLowerCase() || 'unauthenticated';
};

/**
 * @function readStoredAccessUser
 * @description Reads authenticated user identity from Wilsy OS storage keys without inventing a privileged fallback.
 * @returns {Object|null} Stored user packet or null.
 * @collaboration Missing identity must never become founder access; this is the client-side zero-trust guardrail.
 */
export const readStoredAccessUser = () => {
  const candidateKeys = ['wilsy_user', 'userData', 'user'];
  for (const key of candidateKeys) {
    const raw = localStorage.getItem(key);
    if (!raw || raw === 'undefined' || raw === 'null') continue;
    try {
      const parsed = JSON.parse(raw);
      if (parsed && typeof parsed === 'object') return parsed;
    } catch {
      continue;
    }
  }
  return null;
};

/**
 * @function resolvePermissionSet
 * @description Combines role permissions with explicit user permissions.
 * @param {Object} user - User identity packet.
 * @param {string} userRole - Canonical user role.
 * @returns {Array<string>} Unique permission list.
 * @collaboration Tenant owners can receive dynamic feature permissions without creating a new dashboard component.
 */
export const resolvePermissionSet = (user = {}, userRole = 'unauthenticated') => {
  const rolePermissions = ROLE_PERMISSIONS[userRole] || [];
  const explicitPermissions = [
    ...(Array.isArray(user.permissions) ? user.permissions : []),
    ...(Array.isArray(user.enabledPermissions) ? user.enabledPermissions : [])
  ].map(permission => String(permission || '').trim()).filter(Boolean);
  return [...new Set([...rolePermissions, ...explicitPermissions])];
};

/**
 * @function hasPermission
 * @description Checks whether a canonical role or explicit permission list includes a requested permission.
 * @param {string|Array<string>} roleOrPermissions - Canonical role or permission array.
 * @param {string} requiredPermission - Permission key.
 * @returns {boolean} True when access is allowed.
 * @collaboration Route gates and dashboards must agree on permission semantics.
 */
export const hasPermission = (roleOrPermissions, requiredPermission) => {
  const permissions = Array.isArray(roleOrPermissions)
    ? roleOrPermissions
    : (ROLE_PERMISSIONS[normalizeSovereignRole(roleOrPermissions)] || []);
  return permissions.includes(requiredPermission) || permissions.includes('view_all_analytics');
};

/**
 * @function hasRoleLevel
 * @description Checks whether a user role meets a minimum access level.
 * @param {string} userRole - Candidate role.
 * @param {string|number} requiredLevel - Required role key or numeric level.
 * @returns {boolean} True when the user level is sufficient.
 * @collaboration Gives tenant modules a consistent hierarchy without leaking tenant data across roles.
 */
export const hasRoleLevel = (userRole, requiredLevel) => {
  const normalizedRole = normalizeSovereignRole(userRole);
  const userLevel = ROLE_LEVELS[normalizedRole] || 0;
  const minLevel = typeof requiredLevel === 'number'
    ? requiredLevel
    : ROLE_LEVELS[normalizeSovereignRole(requiredLevel)] || 0;
  return userLevel >= minLevel;
};

/**
 * @function useSovereignAccess
 * @description Provides role, tenant and permission flags for tenant-isolated dashboard routing.
 * @returns {Object} Access context.
 * @collaboration The executive suite depends on this hook to deny sales reps and cross-tenant administrators before any source hydration.
 */
export const useSovereignAccess = () => {
  const { user: authUser, isAuthenticated } = useAuth() || {};
  const [identity, setIdentity] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const storedUser = readStoredAccessUser();
    setIdentity(authUser || storedUser || null);
    setIsLoading(false);
  }, [authUser]);

  const accessPacket = useMemo(() => {
    const user = identity || {};
    const authenticated = Boolean(isAuthenticated || localStorage.getItem('wilsy_auth_token') || localStorage.getItem('token'));
    const userRole = authenticated ? normalizeSovereignRole(user.role || user.userRole || 'user') : 'unauthenticated';
    const permissions = resolvePermissionSet(user, userRole);
    const tenantId = user.tenantId || user.activeTenantId || user.tenant || 'UNRESOLVED_TENANT';
    const userEmail = user.email || user.userEmail || null;
    const roleLevel = ROLE_LEVELS[userRole] || 0;

    return {
      userRole,
      userEmail,
      tenantId,
      permissions,
      roleLevel,
      isLoading,
      isAuthenticated: authenticated,
      isFounder: userRole === 'super_admin',
      isExecutive: ['super_admin', 'executive'].includes(userRole),
      isAdmin: ['super_admin', 'executive', 'admin'].includes(userRole),
      isTenantOwner: ['super_admin', 'executive', 'tenant_owner'].includes(userRole),
      isSalesRep: userRole === 'sales_representative',
      canViewRevenue: hasPermission(permissions, 'view_revenue') || hasPermission(permissions, 'view_tenant_revenue'),
      canViewForecasts: hasPermission(permissions, 'view_forecasts') || hasPermission(permissions, 'view_tenant_forecasts'),
      canViewRisk: hasPermission(permissions, 'view_risk') || hasPermission(permissions, 'view_tenant_risk'),
      canExport: hasPermission(permissions, 'export_reports'),
      canViewInvestorKPIs: hasPermission(permissions, 'view_investor_kpis'),
      canViewQuantumForecasts: hasPermission(permissions, 'view_quantum_forecasts'),
      canViewUserActivity: hasPermission(permissions, 'view_user_activity') || hasPermission(permissions, 'view_tenant_user_activity'),
      canViewTenantPerformance: hasPermission(permissions, 'view_tenant_performance') || hasPermission(permissions, 'view_all_tenants'),
      canGenerateInvestorReport: hasPermission(permissions, 'generate_investor_report'),
      canViewAllTenants: hasPermission(permissions, 'view_all_tenants'),
      hasPermission: (permission) => hasPermission(permissions, permission),
      hasRoleLevel: (level) => hasRoleLevel(userRole, level)
    };
  }, [identity, isAuthenticated, isLoading]);

  return accessPacket;
};

export default useSovereignAccess;
