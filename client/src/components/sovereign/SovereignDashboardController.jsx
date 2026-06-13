/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN DASHBOARD CONTROLLER [V17.2.0-DYNAMIC-RETURN]                                                                    ║
 * ║ [ROLE AUTO-DETECTION | FOUNDER RETURN DOCK | STANDALONE EXECUTIVE SHARDS | MOUNT TELEMETRY | TENANT CONTEXT ROUTING]                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 17.2.0-DYNAMIC-RETURN | PRODUCTION READY | BIBLICAL WORTH BILLIONS                                                           ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/sovereign/SovereignDashboardController.jsx               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated login-time dashboard auto-detection with founder-grade return navigation.           ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Injected ErrorBoundary wrappers around dashboard shards for institutional resilience.            ║
 * ║ • AI Engineering (Codex) - RESTORED: Removed root Founder bypass and rebuilt polymorphic dashboard routing with standalone shards.      ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import React, { Suspense, useEffect, useMemo, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { ArrowLeft, Crown, Loader2 } from 'lucide-react';
import { useTenants } from '../../contexts/tenantContext.jsx';
import { broadcastTelemetry } from '../../utils/telemetryHelper.js';
import ErrorBoundary from '../ErrorBoundary';

/**
 * 🏛️ COMMAND CENTER SHARDS
 * High-fidelity dashboards are lazily loaded to ensure code splitting aligns with institutional security.
 */
const FounderDashboard = React.lazy(() => import('./FounderDashboard'));
const GeneralDashboard = React.lazy(() => import('./GeneralDashboard'));
const ExecutiveDashboard = React.lazy(() => import('../executive/ExecutiveDashboard'));
const COODashboard = React.lazy(() => import('../coo/COODashboard'));
const CRMDashboard = React.lazy(() => import('../crm/CRMDashboard'));
const SalesDashboard = React.lazy(() => import('../sales/SalesDashboard'));
const FinanceDashboard = React.lazy(() => import('../finance/FinanceDashboard'));
const HRDashboard = React.lazy(() => import('../hr/HrDashboard'));
const ITDashboard = React.lazy(() => import('../it/ITDashboard'));

export const DASHBOARD_KEYS = Object.freeze({
  FOUNDER: 'FOUNDER_DASHBOARD',
  GENERAL: 'GENERAL_DASHBOARD',
  EXECUTIVE: 'EXECUTIVE_DASHBOARD',
  COO: 'COO_DASHBOARD',
  CRM: 'CRM_DASHBOARD',
  SALES: 'SALES_DASHBOARD',
  FINANCE: 'FINANCE_DASHBOARD',
  HR: 'HR_DASHBOARD',
  IT: 'IT_DASHBOARD'
});

const DASHBOARD_LABELS = Object.freeze({
  [DASHBOARD_KEYS.FOUNDER]: 'Founder Dashboard',
  [DASHBOARD_KEYS.GENERAL]: 'Tenant Command Center',
  [DASHBOARD_KEYS.EXECUTIVE]: 'Executive Dashboard',
  [DASHBOARD_KEYS.COO]: 'COO Operations Dashboard',
  [DASHBOARD_KEYS.CRM]: 'CRM Command Center',
  [DASHBOARD_KEYS.SALES]: 'Sales Dashboard',
  [DASHBOARD_KEYS.FINANCE]: 'Finance Dashboard',
  [DASHBOARD_KEYS.HR]: 'HR Dashboard',
  [DASHBOARD_KEYS.IT]: 'IT Dashboard'
});

const DASHBOARD_ALIASES = Object.freeze({
  BOARDROOM_HUD: DASHBOARD_KEYS.EXECUTIVE,
  CEO_DASHBOARD: DASHBOARD_KEYS.EXECUTIVE,
  EXECUTIVE: DASHBOARD_KEYS.EXECUTIVE,
  EXECUTIVE_DASHBOARD: DASHBOARD_KEYS.EXECUTIVE,
  EXECUTIVE_OVERSIGHT: DASHBOARD_KEYS.EXECUTIVE,
  FOUNDER: DASHBOARD_KEYS.FOUNDER,
  FOUNDER_DASHBOARD: DASHBOARD_KEYS.FOUNDER,
  HOME: DASHBOARD_KEYS.FOUNDER,
  OMEGA: DASHBOARD_KEYS.FOUNDER,
  SINGULARITY_MATRIX: DASHBOARD_KEYS.FOUNDER,
  SOVEREIGN: DASHBOARD_KEYS.FOUNDER,
  SUPER_ADMIN: DASHBOARD_KEYS.FOUNDER,
  GENERAL: DASHBOARD_KEYS.GENERAL,
  GENERAL_DASHBOARD: DASHBOARD_KEYS.GENERAL,
  TENANT: DASHBOARD_KEYS.GENERAL,
  TENANT_COMMAND_CENTER: DASHBOARD_KEYS.GENERAL,
  COO: DASHBOARD_KEYS.COO,
  COO_DASHBOARD: DASHBOARD_KEYS.COO,
  OPERATIONS: DASHBOARD_KEYS.COO,
  CRM: DASHBOARD_KEYS.CRM,
  CRM_DASHBOARD: DASHBOARD_KEYS.CRM,
  CLIENTS: DASHBOARD_KEYS.CRM,
  CUSTOMER_SUCCESS: DASHBOARD_KEYS.CRM,
  SALES: DASHBOARD_KEYS.SALES,
  SALES_DASHBOARD: DASHBOARD_KEYS.SALES,
  SALES_REPRESENTATIVE_DASHBOARD: DASHBOARD_KEYS.SALES,
  REVENUE: DASHBOARD_KEYS.SALES,
  FINANCE: DASHBOARD_KEYS.FINANCE,
  FINANCE_DASHBOARD: DASHBOARD_KEYS.FINANCE,
  BILLING: DASHBOARD_KEYS.FINANCE,
  CFO_DASHBOARD: DASHBOARD_KEYS.FINANCE,
  REVENUE_LEDGER: DASHBOARD_KEYS.FINANCE,
  HR: DASHBOARD_KEYS.HR,
  HR_DASHBOARD: DASHBOARD_KEYS.HR,
  PEOPLE: DASHBOARD_KEYS.HR,
  IT: DASHBOARD_KEYS.IT,
  IT_DASHBOARD: DASHBOARD_KEYS.IT,
  SECURITY: DASHBOARD_KEYS.IT,
  TECHNOLOGY: DASHBOARD_KEYS.IT
});

const ROLE_DASHBOARD_MAP = Object.freeze({
  ACCOUNT_EXECUTIVE: DASHBOARD_KEYS.SALES,
  ACCOUNTANT: DASHBOARD_KEYS.FINANCE,
  ADMIN: DASHBOARD_KEYS.GENERAL,
  BOARD_MEMBER: DASHBOARD_KEYS.EXECUTIVE,
  BUSINESS_DEVELOPMENT: DASHBOARD_KEYS.SALES,
  CEO: DASHBOARD_KEYS.EXECUTIVE,
  CFO: DASHBOARD_KEYS.FINANCE,
  COO: DASHBOARD_KEYS.COO,
  CRM: DASHBOARD_KEYS.CRM,
  CUSTOMER_SUCCESS: DASHBOARD_KEYS.CRM,
  EXECUTIVE: DASHBOARD_KEYS.EXECUTIVE,
  FINANCE: DASHBOARD_KEYS.FINANCE,
  FINANCE_MANAGER: DASHBOARD_KEYS.FINANCE,
  HR: DASHBOARD_KEYS.HR,
  HR_MANAGER: DASHBOARD_KEYS.HR,
  IT: DASHBOARD_KEYS.IT,
  IT_ADMIN: DASHBOARD_KEYS.IT,
  MANAGER: DASHBOARD_KEYS.GENERAL,
  OWNER: DASHBOARD_KEYS.EXECUTIVE,
  SALES: DASHBOARD_KEYS.SALES,
  SALES_MANAGER: DASHBOARD_KEYS.SALES,
  SALES_REP: DASHBOARD_KEYS.SALES,
  SALES_REPRESENTATIVE: DASHBOARD_KEYS.SALES,
  TENANT_ADMIN: DASHBOARD_KEYS.GENERAL,
  TENANT_OWNER: DASHBOARD_KEYS.EXECUTIVE,
  USER: DASHBOARD_KEYS.GENERAL
});

const FOUNDER_AUTHORITY_TOKENS = Object.freeze([
  'FOUNDER',
  'GLOBAL_ROOT',
  'OMEGA',
  'ROOT',
  'SOVEREIGN',
  'SOVEREIGN_ACCESS',
  'SUPERADMIN',
  'SUPER_ADMIN'
]);

/**
 * @function normalizeDashboardToken
 * @description Converts role, permission and dashboard strings into comparable uppercase keys.
 * @param {unknown} value - Raw identity, role or dashboard token.
 * @returns {string} Normalized dashboard token.
 * @collaboration Keeps legacy login shards, tenant profile settings and current role strings speaking one resolver language.
 */
export const normalizeDashboardToken = (value = '') => (
  String(value || '')
    .trim()
    .replace(/([a-z])([A-Z])/g, '$1_$2')
    .replace(/[\s./:-]+/g, '_')
    .replace(/_+/g, '_')
    .toUpperCase()
);

/**
 * @function mapDashboardAlias
 * @description Resolves historical module names and dashboard slugs into canonical dashboard keys.
 * @param {unknown} value - Candidate dashboard slug.
 * @returns {string} Canonical dashboard key or an empty string.
 * @collaboration Preserves Wilson's older Founder module names while enabling standalone dashboard routing again.
 */
export const mapDashboardAlias = (value = '') => {
  const token = normalizeDashboardToken(value);
  if (!token) return '';
  if (Object.values(DASHBOARD_KEYS).includes(token)) return token;
  return DASHBOARD_ALIASES[token] || '';
};

/**
 * @function isValidDashboardUser
 * @description Verifies that a login identity has enough shape to make a dashboard routing decision.
 * @param {unknown} obj - Candidate identity object.
 * @returns {boolean} True when the identity can be routed.
 * @collaboration Allows backend identity envelopes without forcing every shard to contain an email field.
 */
export const isValidDashboardUser = (obj = null) => (
  Boolean(
    obj
    && typeof obj === 'object'
    && typeof obj.role === 'string'
    && obj.role.trim().length > 0
    && (obj.email || obj.id || obj._id || obj.userId)
  )
);

/**
 * @function collectDashboardSignals
 * @description Gathers explicit dashboard preferences from user, tenant and login metadata.
 * @param {Object} params - Resolver context.
 * @param {Object} params.user - Authenticated user envelope.
 * @param {Object|string} params.activeTenant - Active tenant shard.
 * @param {string} params.dashboardIntent - Session-level dashboard override from local storage.
 * @returns {Array<unknown>} Ordered dashboard signals.
 * @collaboration Makes the login resolver honor saved dashboard intent before falling back to role defaults.
 */
export const collectDashboardSignals = ({ user = {}, activeTenant = {}, dashboardIntent = '' } = {}) => [
  dashboardIntent,
  user.dashboardKey,
  user.dashboard,
  user.defaultDashboard,
  user.preferredDashboard,
  user.landingDashboard,
  user.startDashboard,
  user.module,
  user.defaultModule,
  user.profile?.dashboardKey,
  user.profile?.dashboard,
  user.profile?.defaultDashboard,
  user.preferences?.dashboardKey,
  user.preferences?.dashboard,
  user.preferences?.defaultDashboard,
  user.sovereignProfile?.dashboardKey,
  user.sovereignProfile?.dashboard,
  user.sovereignProfile?.defaultDashboard,
  user.founderProfile?.dashboardKey,
  user.founderProfile?.dashboard,
  user.founderProfile?.defaultDashboard,
  activeTenant?.dashboardKey,
  activeTenant?.dashboard,
  activeTenant?.defaultDashboard,
  activeTenant?.preferredDashboard,
  activeTenant?.profile?.dashboardKey,
  activeTenant?.profile?.dashboard,
  activeTenant?.profile?.defaultDashboard,
  activeTenant?.executive?.dashboardKey,
  activeTenant?.executive?.dashboard
].filter(Boolean);

/**
 * @function hasFounderReturnAuthority
 * @description Determines whether the active identity may return from a standalone shard to the Founder Dashboard.
 * @param {Object} params - Authority context.
 * @param {Object} params.user - Authenticated user envelope.
 * @param {string} params.role - Optional normalized role override.
 * @returns {boolean} True when founder return controls should render.
 * @collaboration Keeps Wilson's founder login powerful without forcing every view to be wrapped inside FounderDashboard chrome.
 */
export const hasFounderReturnAuthority = ({ user = {}, role = '' } = {}) => {
  const roleToken = normalizeDashboardToken(role || user.role || user.accountRole || user.tenantRole);
  const permissionTokens = [
    roleToken,
    user.accessLevel,
    user.authority,
    user.rank,
    user.sovereignAccess ? 'SOVEREIGN_ACCESS' : '',
    user.isFounder ? 'FOUNDER' : '',
    user.isOmega ? 'OMEGA' : '',
    user.omegaAccess ? 'OMEGA' : '',
    ...(Array.isArray(user.roles) ? user.roles : []),
    ...(Array.isArray(user.permissions) ? user.permissions : []),
    ...(Array.isArray(user.scopes) ? user.scopes : [])
  ].map(normalizeDashboardToken).filter(Boolean);

  return permissionTokens.some(token => FOUNDER_AUTHORITY_TOKENS.includes(token));
};

/**
 * @function resolveDashboardKey
 * @description Resolves the canonical dashboard key from manual override, saved intent, user role and tenant context.
 * @param {Object} params - Dashboard resolver context.
 * @param {Object} params.user - Authenticated user envelope.
 * @param {Object|string} params.activeTenant - Current tenant shard.
 * @param {string} params.manualDashboardKey - In-session dashboard override.
 * @param {string} params.dashboardIntent - Persisted login dashboard intent.
 * @returns {string} Canonical dashboard key.
 * @collaboration Restores the dynamic login behavior where the user's identity decides the mounted dashboard.
 */
export const resolveDashboardKey = ({
  user = {},
  activeTenant = {},
  manualDashboardKey = '',
  dashboardIntent = ''
} = {}) => {
  const manualTarget = mapDashboardAlias(manualDashboardKey);
  if (manualTarget) return manualTarget;

  const explicitTarget = collectDashboardSignals({ user, activeTenant, dashboardIntent })
    .map(mapDashboardAlias)
    .find(Boolean);
  if (explicitTarget) return explicitTarget;

  const roleToken = normalizeDashboardToken(user.role || user.accountRole || user.tenantRole);
  if (hasFounderReturnAuthority({ user, role: roleToken })) return DASHBOARD_KEYS.FOUNDER;

  return ROLE_DASHBOARD_MAP[roleToken] || DASHBOARD_KEYS.GENERAL;
};

/**
 * @function getDashboardDisplayName
 * @description Provides a compact operator label for a resolved dashboard key.
 * @param {string} dashboardKey - Canonical dashboard key.
 * @returns {string} Human readable dashboard label.
 * @collaboration Names standalone shards clearly when the founder return dock is visible.
 */
export const getDashboardDisplayName = (dashboardKey = DASHBOARD_KEYS.GENERAL) => (
  DASHBOARD_LABELS[dashboardKey] || DASHBOARD_LABELS[DASHBOARD_KEYS.GENERAL]
);

/**
 * @function getExecutiveRoleLabel
 * @description Chooses the role label passed into the standalone ExecutiveDashboard.
 * @param {Object} user - Authenticated user envelope.
 * @returns {string} Executive-facing role label.
 * @collaboration Preserves CEO/Executive semantics when the same executive surface serves multiple login roles.
 */
export const getExecutiveRoleLabel = (user = {}) => {
  const roleToken = normalizeDashboardToken(user.role || user.accountRole || user.tenantRole);
  if (['CEO', 'FOUNDER', 'OMEGA', 'SUPER_ADMIN', 'SUPERADMIN'].includes(roleToken)) return 'CEO';
  if (roleToken === 'TENANT_OWNER' || roleToken === 'OWNER') return 'OWNER';
  return roleToken || 'EXECUTIVE';
};

/**
 * @function FounderReturnFrame
 * @description Wraps standalone dashboards with a compact return control for founder-authorized identities.
 * @param {Object} props - Frame properties.
 * @param {string} props.dashboardLabel - Active dashboard label.
 * @param {Function} props.onReturn - Return handler.
 * @param {React.ReactNode} props.children - Mounted dashboard shard.
 * @returns {React.ReactElement} Standalone dashboard frame.
 * @collaboration Lets Wilson inspect specialist dashboards independently and return to the Founder Dashboard without losing context.
 */
const FounderReturnFrame = ({ dashboardLabel, onReturn, children }) => (
  <div style={{ minHeight: '100vh', background: '#050505', color: '#f8fafc', display: 'flex', flexDirection: 'column' }}>
    <div
      style={{
        minHeight: 52,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: 16,
        padding: '10px 16px',
        borderBottom: '1px solid rgba(212,175,55,0.28)',
        background: 'rgba(5,5,5,0.96)',
        position: 'sticky',
        top: 0,
        zIndex: 50
      }}
    >
      <button
        type="button"
        onClick={onReturn}
        aria-label="Return to Founder Dashboard"
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 8,
          minHeight: 34,
          padding: '8px 12px',
          borderRadius: 8,
          border: '1px solid rgba(212,175,55,0.5)',
          background: 'rgba(212,175,55,0.12)',
          color: '#f8fafc',
          fontFamily: 'JetBrains Mono, monospace',
          fontSize: 11,
          fontWeight: 800,
          letterSpacing: 0,
          textTransform: 'uppercase',
          cursor: 'pointer'
        }}
      >
        <ArrowLeft size={14} />
        Return To Founder Dashboard
      </button>
      <span
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 8,
          color: '#d4af37',
          fontFamily: 'JetBrains Mono, monospace',
          fontSize: 11,
          fontWeight: 800,
          letterSpacing: 0,
          textTransform: 'uppercase',
          whiteSpace: 'nowrap'
        }}
      >
        <Crown size={14} />
        {dashboardLabel}
      </span>
    </div>
    <div style={{ flex: 1, minHeight: 0 }}>
      {children}
    </div>
  </div>
);

/**
 * @function SovereignDashboardController
 * @description Evaluates the user's forensic role and mounts the corresponding Command Center shard.
 * @param {Object} props - Controller properties.
 * @param {Object} props.user - Authenticated user envelope supplied by AuthProvider.
 * @returns {React.ReactElement} Resolved dashboard shard.
 * @collaboration Centralizes dashboard auto-detection so login, founder handoff and specialist shards stay dynamically connected.
 */
const SovereignDashboardController = ({ user: propUser }) => {
  const { activeTenant } = useTenants();
  const [manualDashboardKey, setManualDashboardKey] = useState('');

  const user = useMemo(() => {
    if (isValidDashboardUser(propUser)) return propUser;

    const vaultData = localStorage.getItem('wilsy_user') || localStorage.getItem('user');
    if (vaultData) {
      try {
        const parsed = JSON.parse(vaultData);
        if (isValidDashboardUser(parsed)) return parsed;
        console.error('[SOVEREIGN-CONTROLLER] Vault schema validation failed.');
      } catch (error) {
        console.error('[SOVEREIGN-CONTROLLER] Vault data corruption detected.', error);
      }
    }
    return null;
  }, [propUser]);

  const dashboardIntent = useMemo(() => (
    localStorage.getItem('wilsy_dashboard_intent')
    || localStorage.getItem('wilsy_default_dashboard')
    || localStorage.getItem('wilsy_last_dashboard')
    || ''
  ), [user?.email, user?.id, user?._id]);
  const role = normalizeDashboardToken(user?.role || user?.accountRole || user?.tenantRole);
  const traceId = localStorage.getItem('traceId') || 'SYSTEM_CORE_INIT';
  const dashboardKey = useMemo(() => (
    user
      ? resolveDashboardKey({ user, activeTenant, manualDashboardKey, dashboardIntent })
      : ''
  ), [activeTenant, dashboardIntent, manualDashboardKey, user]);
  const dashboardLabel = getDashboardDisplayName(dashboardKey);
  const canReturnToFounder = Boolean(
    user
    && dashboardKey
    && dashboardKey !== DASHBOARD_KEYS.FOUNDER
    && hasFounderReturnAuthority({ user, role })
  );

  /**
   * 🛰️ MOUNT TELEMETRY
   * Broadcasts successful entry into the Command Center for the forensic audit trail.
   */
  useEffect(() => {
    if (user && role && dashboardKey) {
      broadcastTelemetry(user.tenantAlias || user.tenantId || 'GLOBAL_ROOT', 'DASHBOARD_EVENT', 'DASHBOARD_MOUNT_SUCCESS', user.email || user.id, {
        role,
        dashboardKey,
        dashboardLabel,
        traceId,
        version: '17.2.0'
      });
      console.log(`[SOVEREIGN-CONTROLLER] Shard Mounted: ${dashboardKey} | Role: ${role} | Trace: ${traceId}`);
    }
  }, [dashboardKey, dashboardLabel, role, traceId, user]);

  if (!user) {
    console.warn('[SOVEREIGN-CONTROLLER] No identity shard discovered. Reverting to Gateway.', { traceId });
    return <Navigate to="/login" replace />;
  }

  let dashboardShard = null;
  if (dashboardKey === DASHBOARD_KEYS.FOUNDER) {
    dashboardShard = <FounderDashboard user={user} />;
  } else if (dashboardKey === DASHBOARD_KEYS.EXECUTIVE) {
    dashboardShard = <ExecutiveDashboard role={getExecutiveRoleLabel(user)} user={user} />;
  } else if (dashboardKey === DASHBOARD_KEYS.COO) {
    dashboardShard = <COODashboard user={user} />;
  } else if (dashboardKey === DASHBOARD_KEYS.CRM) {
    dashboardShard = <CRMDashboard user={user} />;
  } else if (dashboardKey === DASHBOARD_KEYS.SALES) {
    dashboardShard = <SalesDashboard user={user} />;
  } else if (dashboardKey === DASHBOARD_KEYS.FINANCE) {
    dashboardShard = <FinanceDashboard user={user} />;
  } else if (dashboardKey === DASHBOARD_KEYS.HR) {
    dashboardShard = <HRDashboard user={user} />;
  } else if (dashboardKey === DASHBOARD_KEYS.IT) {
    dashboardShard = <ITDashboard user={user} />;
  } else if (dashboardKey === DASHBOARD_KEYS.GENERAL) {
    dashboardShard = <GeneralDashboard user={user} />;
  } else {
    console.error('[SOVEREIGN-CONTROLLER] Identity fragment unrecognized.', {
      role,
      dashboardKey,
      traceId,
      timestamp: new Date().toISOString()
    });
    return <Navigate to="/unauthorized" replace />;
  }

  const guardedShard = (
    <ErrorBoundary>
      {dashboardShard}
    </ErrorBoundary>
  );

  return (
    <Suspense
      fallback={
        <div className="h-screen bg-black flex flex-col items-center justify-center">
          <Loader2 className="w-12 h-12 text-[#D4AF37] animate-spin mb-6" />
          <p className="text-[#D4AF37] font-mono text-xs tracking-[0.3em] uppercase animate-pulse">
            Hydrating Sovereign Command Center...
          </p>
        </div>
      }
    >
      {canReturnToFounder ? (
        <FounderReturnFrame
          dashboardLabel={dashboardLabel}
          onReturn={() => setManualDashboardKey(DASHBOARD_KEYS.FOUNDER)}
        >
          {guardedShard}
        </FounderReturnFrame>
      ) : guardedShard}
    </Suspense>
  );
};

export default SovereignDashboardController;
