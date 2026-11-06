/* eslint-disable */
/**
 * TITLE: WILSY OS Sovereign Dashboard Controller
 * VERSION: v18.7.0-AUTHENTICATED-ROLE-LANDING
 * AUTHORITY: Authenticated client dashboard routing and presentation composition.
 * EPITOME: Resolves the existing WILSY OS dashboard shard from authenticated
 *          identity and tenant context. L8-7D10 converges every published Legal
 *          business role on the single canonical WILSY Legal OS shard while
 *          leaving server IAM, tenant, lifecycle, service, billing and financial
 *          authority entirely outside browser routing.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/sovereign/SovereignDashboardController.jsx
 * COLLABORATION / OWNERSHIP: AuthProvider owns authenticated identity projection;
 *                            TenantContext owns selected tenant projection;
 *                            Python EOS owns authorization and Legal Operations
 *                            truth; dashboard components own presentation only.
 * CERTIFICATION / UPDATE DATE: 2026-09-23
 * CHANGELOG: 2026-09-23 v18.6.0-CANONICAL-KERNEL-HEALTH-TRANSPORT maps LEGAL_PARTNER, LEGAL_ATTORNEY,
 *            LEGAL_PARALEGAL, LEGAL_SECRETARY, LEGAL_FINANCE, LEGAL_CLIENT and
 *            their TENANT_* business-role aliases to the canonical Legal OS
 *            shard. Existing SHERIFF/DEPUTY mappings remain unchanged. Browser
 *            routing still grants no permission or business authority.
2026-09-23 v18.2.1-L8-6C-LEGAL-ROLE-ROUTING removes the superseded decorative pre-sovereign
 *            controller header after the L8-6C migration; runtime routing is
 *            unchanged.
 *            2026-09-23 v18.2.0-L8-6C-LEGAL-ROLE-ROUTING adds LEGAL_DASHBOARD as an existing-controller
 *            shard, maps normalized SHERIFF/TENANT_SHERIFF and
 *            DEPUTY/TENANT_DEPUTY roles to Legal OS, and forwards the
 *            authenticated normalized role only as roleView presentation input.
 *            2026-08-02 18.1.1-BOTTOM-BLEED-FIX preserved overflow for BillingHUD.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: Routing uses authenticated client projections;
 *                             roleView is non-authoritative and cannot grant API
 *                             access or manufacture tenant/deputy identity.
 * TENANT BOUNDARY: Active tenant remains selected by governed tenant context;
 *                  dashboard routing cannot widen server tenant scope.
 * AUTHORITY BOUNDARY: Client routing only. Python EOS independently authorizes
 *                     Legal Operations, IAM, lifecycle and binding reads.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 * FAIL-CLOSED DECLARATION: Unknown dashboard/role resolution does not create
 *                          Legal Operations authority or cross-role fallback.
 */


import React, { Suspense, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { ArrowLeft, Crown, Loader2, ShieldAlert } from 'lucide-react';
import { useTenants } from '../../contexts/tenantContext.jsx';
import { BusinessProvider } from '../../contexts/BusinessContext.jsx';
import { broadcastTelemetry } from '../../utils/telemetryHelper.js';
import api from '../../services/api.js';
import ErrorBoundary from '../ErrorBoundary';
import WilsyGlobalCommandSearch from './WilsyGlobalCommandSearch';

/**
 * 🏛️ COMMAND CENTER SHARDS
 * Lazily loaded to keep the founder path lean and align code-splitting with institutional security.
 */
const FounderDashboard = React.lazy(() => import('./FounderDashboard'));
const GeneralDashboard = React.lazy(() => import('./GeneralDashboard'));
const ExecutiveDashboard = React.lazy(() => import('../executive/ExecutiveDashboard'));
const COODashboard = React.lazy(() => import('../coo/COODashboard'));
const CRMDashboard = React.lazy(() => import('../crm/CRMDashboard'));
const SalesDashboard = React.lazy(() => import('../sales/SalesDashboard'));
// 🆕 REPLACED legacy FinanceDashboard with the new Sovereign BillingHUD
const BillingHUD = React.lazy(() => import('../billing/BillingHUD'));
const HRDashboard = React.lazy(() => import('../hr/HrDashboard'));
const OperationsDashboard = React.lazy(() => import('../operations/OperationsDashboard'));
const IntelligenceDashboard = React.lazy(() => import('../intelligence/IntelligenceDashboard'));
const ITDashboard = React.lazy(() => import('../it/ITDashboard'));
const LegalDashboard = React.lazy(() => import('../industry/LegalDashboard'));
const SystemServicesDashboard = React.lazy(() => import('../system-services/SystemServicesDashboard'));


export const DASHBOARD_KEYS = Object.freeze({
  FOUNDER: 'FOUNDER_DASHBOARD',
  GENERAL: 'GENERAL_DASHBOARD',
  EXECUTIVE: 'EXECUTIVE_DASHBOARD',
  COO: 'COO_DASHBOARD',
  CRM: 'CRM_DASHBOARD',
  SALES: 'SALES_DASHBOARD',
  FINANCE: 'FINANCE_DASHBOARD',   // ⬅️ Now resolves to BillingHUD
  HR: 'HR_DASHBOARD',
  OPERATIONS: 'OPERATIONS_DASHBOARD',
  INTELLIGENCE: 'INTELLIGENCE_DASHBOARD',
  IT: 'IT_DASHBOARD',
  LEGAL: 'LEGAL_DASHBOARD',
  SYSTEM_SERVICES: 'SYSTEM_SERVICES_DASHBOARD'
});

const DASHBOARD_LABELS = Object.freeze({
  [DASHBOARD_KEYS.FOUNDER]: 'Founder Dashboard',
  [DASHBOARD_KEYS.GENERAL]: 'Tenant Command Center',
  [DASHBOARD_KEYS.EXECUTIVE]: 'Executive Dashboard',
  [DASHBOARD_KEYS.COO]: 'COO Operations Dashboard',
  [DASHBOARD_KEYS.CRM]: 'CRM Command Center',
  [DASHBOARD_KEYS.SALES]: 'Sales Dashboard',
  [DASHBOARD_KEYS.FINANCE]: 'Billing Hub',  // ⬅️ Updated label
  [DASHBOARD_KEYS.HR]: 'HR Dashboard',
  [DASHBOARD_KEYS.OPERATIONS]: 'Operations OS',
  [DASHBOARD_KEYS.INTELLIGENCE]: 'Intelligence OS',
  [DASHBOARD_KEYS.IT]: 'IT Dashboard',
  [DASHBOARD_KEYS.LEGAL]: 'WILSY Legal OS',
  [DASHBOARD_KEYS.SYSTEM_SERVICES]: 'System Services'
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
  SUPERADMIN: DASHBOARD_KEYS.FOUNDER,
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
  BILLING: DASHBOARD_KEYS.FINANCE,        // ⬅️ 'BILLING' alias now maps to FINANCE -> BillingHUD
  BILLING_HUB: DASHBOARD_KEYS.FINANCE,
  CFO_DASHBOARD: DASHBOARD_KEYS.FINANCE,
  REVENUE_LEDGER: DASHBOARD_KEYS.FINANCE,
  HR: DASHBOARD_KEYS.HR,
  HR_DASHBOARD: DASHBOARD_KEYS.HR,
  OPERATIONS_DASHBOARD: DASHBOARD_KEYS.OPERATIONS,
  INTELLIGENCE_DASHBOARD: DASHBOARD_KEYS.INTELLIGENCE,
  PEOPLE: DASHBOARD_KEYS.HR,
  IT: DASHBOARD_KEYS.IT,
  IT_DASHBOARD: DASHBOARD_KEYS.IT,
  SECURITY: DASHBOARD_KEYS.IT,
  TECHNOLOGY: DASHBOARD_KEYS.IT,
  LEGAL: DASHBOARD_KEYS.LEGAL,
  LEGAL_DASHBOARD: DASHBOARD_KEYS.LEGAL,
  LEGAL_OS: DASHBOARD_KEYS.LEGAL,
  SYSTEM_SERVICES_DASHBOARD: DASHBOARD_KEYS.SYSTEM_SERVICES
});

const FOUNDER_AUTHORITY_TOKENS = Object.freeze([
  'FOUNDER',
  'FOUNDER_ARCHITECT',
  'GLOBAL_ROOT',
  'OMEGA',
  'ROOT',
  'SOVEREIGN',
  'SOVEREIGN_ACCESS',
  'SUPERADMIN',
  'SUPER_ADMIN'
]);

const WILSY_THEME_STORAGE_KEYS = Object.freeze({
  theme: 'wilsy:account-command-center:theme',
  mode: 'wilsy:account-command-center:mode'
});

const WILSY_OPERATING_SKINS = Object.freeze({
  wilsy_aurora: {
    id: 'wilsy_aurora', bg: '#020306', surface: '#070B18', panel: '#0B1024', rail: '#080C18',
    text: '#FFFAF0', muted: '#C5CCE5', accent: '#B66DFF', authority: '#D4AF37', live: '#84F0C8',
    risk: '#FF8AA4', border: 'rgba(182,109,255,0.34)'
  },
  sovereign_black: {
    id: 'sovereign_black', bg: '#000000', surface: '#050505', panel: '#0B0B0B', rail: '#030303',
    text: '#FFFFFF', muted: '#A7A7A7', accent: '#D4AF37', authority: '#F6D76B', live: '#56D69B',
    risk: '#FF6673', border: 'rgba(212,175,55,0.32)'
  },
  cobalt_glass: {
    id: 'cobalt_glass', bg: '#020817', surface: '#06142E', panel: '#0A1D3D', rail: '#07132B',
    text: '#F3F8FF', muted: '#AFC7F6', accent: '#17BDF2', authority: '#8DBBFF', live: '#54F0D1',
    risk: '#FF7C98', border: 'rgba(23,189,242,0.34)'
  },
  pearl_command: {
    id: 'pearl_command', bg: '#F6F8FF', surface: '#FFFFFF', panel: '#EEF2FF', rail: '#FFFFFF',
    text: '#111827', muted: '#53617F', accent: '#7C68FF', authority: '#C49A18', live: '#0F9F6E',
    risk: '#D33F62', border: 'rgba(124,104,255,0.26)'
  },
  legacy_gold: {
    id: 'legacy_gold', bg: '#070602', surface: '#0D0A03', panel: '#141006', rail: '#090702',
    text: '#FFF8DC', muted: '#B9A56D', accent: '#D4AF37', authority: '#F6D76B', live: '#8FE6B1',
    risk: '#FF8A8A', border: 'rgba(246,215,107,0.32)'
  },
  forensic_violet: {
    id: 'forensic_violet', bg: '#05020A', surface: '#0D0718', panel: '#140B26', rail: '#090412',
    text: '#FFF7FF', muted: '#CAB8EA', accent: '#B66DFF', authority: '#E7B7FF', live: '#84F0C8',
    risk: '#FF8AA4', border: 'rgba(182,109,255,0.36)'
  },
  quantum: {
    id: 'quantum', bg: '#01050A', surface: '#06111A', panel: '#071C25', rail: '#031018',
    text: '#F5FFFF', muted: '#9FD7E7', accent: '#17F2D1', authority: '#B6F6FF', live: '#84F0C8',
    risk: '#FF789A', border: 'rgba(23,242,209,0.34)'
  }
});

const KERNEL_PROBE_INTERVAL_MS = 60_000;
const CONTROLLER_VERSION = 'v18.7.0-AUTHENTICATED-ROLE-LANDING';

// ─── Theme helpers ───────────────────────────────────────────────────────────

const normalizeWilsyThemeId = (themeId = '') => {
  const aliases = {
    forensic: 'forensic_violet',
    cobalt: 'cobalt_glass',
    wilsy_daybreak: 'pearl_command',
    dark_ops: 'sovereign_black'
  };
  const normalized = aliases[themeId] || themeId || 'wilsy_aurora';
  return WILSY_OPERATING_SKINS[normalized] ? normalized : 'wilsy_aurora';
};

const normalizeWilsyThemeMode = (mode = '') => (
  ['day', 'night', 'auto'].includes(mode) ? mode : 'night'
);

const resolveWilsyThemeMode = (mode = 'night') => {
  const safeMode = normalizeWilsyThemeMode(mode);
  if (safeMode !== 'auto') return safeMode;
  const hour = new Date().getHours();
  return hour >= 7 && hour < 18 ? 'day' : 'night';
};

const readWilsyThemePreference = () => {
  const themeId = normalizeWilsyThemeId(
    typeof window === 'undefined' ? 'wilsy_aurora' : window.localStorage.getItem(WILSY_THEME_STORAGE_KEYS.theme)
  );
  const mode = normalizeWilsyThemeMode(
    typeof window === 'undefined' ? 'night' : window.localStorage.getItem(WILSY_THEME_STORAGE_KEYS.mode)
  );
  const resolvedMode = resolveWilsyThemeMode(mode);
  const skin = WILSY_OPERATING_SKINS[themeId] || WILSY_OPERATING_SKINS.wilsy_aurora;
  return { themeId, mode, resolvedMode, skin };
};

const installWilsyThemeRuntimeStyle = () => {
  if (typeof document === 'undefined') return;
  const styleId = 'wilsy-os-theme-runtime-style';
  if (document.getElementById(styleId)) return;

  const style = document.createElement('style');
  style.id = styleId;
  style.textContent = `
    :root { color-scheme: dark; }
    html[data-wilsy-resolved-mode="day"] { color-scheme: light; }
    body {
      background:
        radial-gradient(circle at 8% 0%, color-mix(in srgb, var(--wilsy-accent) 14%, transparent), transparent 30%),
        radial-gradient(circle at 88% 8%, color-mix(in srgb, var(--wilsy-live) 10%, transparent), transparent 32%),
        var(--wilsy-bg) !important;
      color: var(--wilsy-text) !important;
    }
    #root { min-height: 100vh; background: transparent !important; color: var(--wilsy-text) !important; }
    .wilsy-theme-bg { background: var(--wilsy-bg) !important; color: var(--wilsy-text) !important; }
    .wilsy-theme-surface { background: var(--wilsy-surface) !important; color: var(--wilsy-text) !important; border-color: var(--wilsy-border) !important; }
    .wilsy-theme-panel { background: var(--wilsy-panel) !important; color: var(--wilsy-text) !important; border-color: var(--wilsy-border) !important; }
    .wilsy-theme-accent { color: var(--wilsy-accent) !important; }
    .wilsy-theme-authority { color: var(--wilsy-authority) !important; }
  `;
  document.head.appendChild(style);
};

const applyWilsyThemeRuntime = () => {
  const preference = readWilsyThemePreference();
  if (typeof document === 'undefined') {
    return { themeId: preference.themeId, mode: preference.mode, resolvedMode: preference.resolvedMode };
  }

  installWilsyThemeRuntimeStyle();
  const root = document.documentElement;
  const body = document.body;
  const skin = preference.skin;
  const isDay = preference.resolvedMode === 'day';

  root.dataset.wilsyTheme = preference.themeId;
  root.dataset.wilsyMode = preference.mode;
  root.dataset.wilsyResolvedMode = preference.resolvedMode;
  body.dataset.wilsyTheme = preference.themeId;
  body.dataset.wilsyMode = preference.mode;
  body.dataset.wilsyResolvedMode = preference.resolvedMode;

  const values = {
    '--wilsy-bg': skin.bg,
    '--wilsy-surface': skin.surface,
    '--wilsy-panel': skin.panel,
    '--wilsy-rail': skin.rail,
    '--wilsy-text': skin.text,
    '--wilsy-muted': skin.muted,
    '--wilsy-accent': skin.accent,
    '--wilsy-authority': skin.authority,
    '--wilsy-live': skin.live,
    '--wilsy-risk': skin.risk,
    '--wilsy-border': skin.border,
    '--wilsy-shadow': isDay ? '0 24px 70px rgba(36,54,164,0.14)' : '0 24px 70px rgba(0,0,0,0.42)'
  };

  Object.entries(values).forEach(([key, value]) => {
    root.style.setProperty(key, value);
    body.style.setProperty(key, value);
  });

  return { themeId: preference.themeId, mode: preference.mode, resolvedMode: preference.resolvedMode };
};

// ─── Dashboard resolution ────────────────────────────────────────────────────

/**
 * @function normalizeDashboardToken
 * @description Converts role / permission / dashboard strings into comparable uppercase keys.
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
 * @description Resolves historical module names and slugs into canonical dashboard keys.
 */
export const mapDashboardAlias = (value = '') => {
  const token = normalizeDashboardToken(value);
  if (!token) return '';
  if (Object.values(DASHBOARD_KEYS).includes(token)) return token;
  return DASHBOARD_ALIASES[token] || '';
};

/**
 * @function isValidDashboardUser
 * @description Verifies identity has enough shape for a routing decision.
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
 */
export const collectDashboardSignals = ({ user = {}, activeTenant = {}, dashboardIntent = '' } = {}) => [
  dashboardIntent,
  user.dashboardKey, user.dashboard, user.defaultDashboard, user.preferredDashboard,
  user.landingDashboard, user.startDashboard, user.module, user.defaultModule,
  user.profile?.dashboardKey, user.profile?.dashboard, user.profile?.defaultDashboard,
  user.preferences?.dashboardKey, user.preferences?.dashboard, user.preferences?.defaultDashboard,
  user.sovereignProfile?.dashboardKey, user.sovereignProfile?.dashboard, user.sovereignProfile?.defaultDashboard,
  user.founderProfile?.dashboardKey, user.founderProfile?.dashboard, user.founderProfile?.defaultDashboard,
  activeTenant?.dashboardKey, activeTenant?.dashboard, activeTenant?.defaultDashboard,
  activeTenant?.preferredDashboard, activeTenant?.profile?.dashboardKey, activeTenant?.profile?.dashboard,
  activeTenant?.profile?.defaultDashboard, activeTenant?.executive?.dashboardKey, activeTenant?.executive?.dashboard
].filter(Boolean);

/**
 * @function hasFounderReturnAuthority
 * @description True when the identity may return from a standalone shard to the Founder Dashboard.
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

  return permissionTokens.some(
    (token) => FOUNDER_AUTHORITY_TOKENS.includes(token) || token.includes('FOUNDER')
  );
};

/**
 * @function resolveDashboardKey
 * @description Resolves canonical dashboard key from override, intent, role and tenant.
 */
const WORKSPACE_DASHBOARD_MAP = Object.freeze({
  EXECUTIVE_COMMAND_CENTRE: DASHBOARD_KEYS.EXECUTIVE,
  TENANT_ADMINISTRATION: DASHBOARD_KEYS.GENERAL,
  AUDIT_REPORTING: DASHBOARD_KEYS.GENERAL,
  TENANT_OPERATIONS: DASHBOARD_KEYS.GENERAL,
  LEGAL_PRACTICE: DASHBOARD_KEYS.LEGAL,
  LEGAL_FINANCE: DASHBOARD_KEYS.FINANCE,
  CLIENT_PORTAL: DASHBOARD_KEYS.LEGAL,
  PROCESS_SERVICE: DASHBOARD_KEYS.LEGAL,
  PEOPLE_OPERATIONS: DASHBOARD_KEYS.HR,
});

/**
 * Resolve the presentation shard from the versioned workspace contract
 * returned by EOS after current identity, membership and IAM verification.
 * The sole presentation exception is a durable Tenant Owner selecting the
 * Legal commercial-only shell; that branch never mounts practice authority and
 * the commercial endpoint independently revalidates subscription:read.
 */
export const resolveDashboardKey = ({ user = {}, manualDashboardKey = '' } = {}) => {
  const requestedDashboard = mapDashboardAlias(manualDashboardKey);
  const systemWorkspace = user.systemServicesWorkspace;
  // A fully verified EOS SYSTEM projection is itself the canonical workspace
  // selector. Requiring a second, client-originated dashboard request creates
  // a first-render race and can redirect a valid SYSTEM principal before the
  // post-mount effect has a chance to set manualDashboardKey.
  if (
    systemWorkspace?.status === 'READY'
    && systemWorkspace?.authority === 'EOS_SYSTEM_SERVICES'
    && systemWorkspace?.scope === 'SYSTEM'
    && typeof systemWorkspace?.principalId === 'string'
    && systemWorkspace.principalId === user.id
    && Array.isArray(systemWorkspace?.capabilities)
    && systemWorkspace.capabilities.includes('system_services:queue:read')
  ) {
    return DASHBOARD_KEYS.SYSTEM_SERVICES;
  }
  const roleToken = normalizeDashboardToken(
    user.role || user.accountRole || user.tenantRole,
  );
  // Tenant Owners may open the Legal presentation only as a commercial-read
  // surface. LegalDashboard resolves TENANT_OWNER before every practice role,
  // mounts no practice provider, and the commercial endpoint independently
  // revalidates subscription:read. This is a presentation route, not authority.
  if (
    ['TENANT_OWNER', 'OWNER'].includes(roleToken)
    && requestedDashboard === DASHBOARD_KEYS.LEGAL
  ) {
    return DASHBOARD_KEYS.LEGAL;
  }

  const workspaceDashboard = WORKSPACE_DASHBOARD_MAP[user.workspaceId] || '';
  if (!workspaceDashboard) return '';
  return requestedDashboard === workspaceDashboard
    ? requestedDashboard
    : workspaceDashboard;
};

/**
 * @function resolveDashboardRequestSignal
 * @description Extracts a canonical dashboard key from route events and payloads.
 */
export const resolveDashboardRequestSignal = (request = '') => {
  if (!request) return '';
  if (typeof request === 'string') return mapDashboardAlias(request);
  if (typeof request !== 'object') return '';

  const directSignals = [
    request.dashboardKey, request.dashboard, request.key, request.id,
    request.module, request.moduleKey, request.dashboardName, request.target, request.value
  ];
  const directTarget = directSignals.map(mapDashboardAlias).find(Boolean);
  if (directTarget) return directTarget;

  const routeSignal = String(request.route || request.path || request.href || '').replace(/^\/+/, '');
  return routeSignal ? mapDashboardAlias(routeSignal) : '';
};

/**
 * @function readRequestedDashboardFromStorage
 */
export const readRequestedDashboardFromStorage = () => {
  if (typeof window === 'undefined') return '';
  const raw = window.localStorage.getItem('wilsy:requested-dashboard');
  if (!raw) return '';
  try {
    return resolveDashboardRequestSignal(JSON.parse(raw));
  } catch {
    return resolveDashboardRequestSignal(raw);
  }
};

export const getDashboardDisplayName = (dashboardKey = DASHBOARD_KEYS.GENERAL) => (
  DASHBOARD_LABELS[dashboardKey] || DASHBOARD_LABELS[DASHBOARD_KEYS.GENERAL]
);

export const getExecutiveRoleLabel = (user = {}) => {
  const roleToken = normalizeDashboardToken(user.role || user.accountRole || user.tenantRole);
  if (['CEO', 'FOUNDER', 'OMEGA', 'SUPER_ADMIN', 'SUPERADMIN', 'FOUNDER_ARCHITECT'].includes(roleToken)) return 'CEO';
  if (roleToken === 'TENANT_OWNER' || roleToken === 'OWNER') return 'OWNER';
  return roleToken || 'EXECUTIVE';
};

// ─── Kennel bridge health probe ──────────────────────────────────────────────

/**
 * @function probeKernelBridge
 * @description Lightweight public probe of GET /api/kernel (Kennel Integration Contract).
 *              Never throws; returns structured health for telemetry panels.
 * @returns {Promise<{status:string, latencyMs:number, payload:object|null, error:string|null}>}
 */
export const probeKernelBridge = async () => {
  const started = performance.now();
  try {
    const response = await api.get('/kernel', {
      timeout: 8000,
      skipAuthRedirect: true,
    });
    const latencyMs = Math.round(performance.now() - started);
    const payload = response?.data && typeof response.data === 'object'
      ? response.data
      : null;
    return {
      status: String(payload?.status || 'OPERATIONAL').toUpperCase(),
      latencyMs,
      payload,
      error: null,
    };
  } catch (err) {
    const statusCode = err?.response?.status;
    return {
      status: statusCode ? `HTTP_${statusCode}` : 'UNREACHABLE',
      latencyMs: Math.round(performance.now() - started),
      payload: null,
      error: statusCode
        ? `HTTP ${statusCode}`
        : (err?.code === 'ECONNABORTED' ? 'TIMEOUT' : (err?.message || 'NETWORK')),
    };
  }
};

// ─── Founder return frame ────────────────────────────────────────────────────

const FounderReturnFrame = ({ dashboardLabel, onReturn, children }) => {
  const [founderDockOpen, setFounderDockOpen] = useState(false);

  useEffect(() => {
    const openFounderDock = () => setFounderDockOpen(true);
    window.addEventListener('wilsy:show-founder-return', openFounderDock);
    return () => window.removeEventListener('wilsy:show-founder-return', openFounderDock);
  }, []);

  return (
    <div style={{ minHeight: '100vh', background: 'var(--wilsy-bg, #050505)', color: 'var(--wilsy-text, #f8fafc)', position: 'relative' }}>
      {founderDockOpen && (
        <div
          role="region"
          aria-label="Founder return controls"
          style={{
            position: 'fixed', left: 22, top: 72, zIndex: 2500,
            display: 'inline-flex', alignItems: 'center', gap: 8, minHeight: 44,
            padding: '6px 8px', borderRadius: 999,
            border: '1px solid var(--wilsy-border, rgba(212,175,55,0.42))',
            background: 'color-mix(in srgb, var(--wilsy-panel, #05070d) 88%, transparent)',
            boxShadow: '0 18px 50px rgba(0,0,0,0.36)', backdropFilter: 'blur(16px)',
            fontFamily: 'JetBrains Mono, IBM Plex Mono, ui-monospace, monospace'
          }}
        >
          <button
            type="button"
            onClick={onReturn}
            aria-label="Return to Founder Dashboard"
            title={`Return to Founder Dashboard from ${dashboardLabel}`}
            style={{
              display: 'inline-flex', alignItems: 'center', gap: 9, minHeight: 34,
              padding: '0 12px', borderRadius: 999, border: 0, background: 'transparent',
              color: 'var(--wilsy-text, #fffaf0)', font: 'inherit', fontSize: 11, fontWeight: 900,
              letterSpacing: '0.08em', textTransform: 'uppercase', cursor: 'pointer'
            }}
          >
            <ArrowLeft size={14} />
            <span>Founder</span>
            <Crown size={14} color="var(--wilsy-authority, #d4af37)" />
          </button>
          <button
            type="button"
            onClick={() => setFounderDockOpen(false)}
            aria-label="Hide founder return controls"
            title="Hide founder return"
            style={{
              width: 30, height: 30, display: 'grid', placeItems: 'center', borderRadius: 999,
              border: '1px solid var(--wilsy-border, rgba(212,175,55,0.18))',
              background: 'rgba(0,0,0,0.22)', color: 'var(--wilsy-text, #fffaf0)', cursor: 'pointer'
            }}
          >
            ×
          </button>
        </div>
      )}

      <button
        type="button"
        onClick={() => setFounderDockOpen((value) => !value)}
        aria-label="Show founder return controls"
        title="Founder return"
        style={{
          position: 'fixed', left: 22, bottom: 22, zIndex: 2499, width: 44, height: 44,
          display: 'grid', placeItems: 'center', borderRadius: 999,
          border: '1px solid var(--wilsy-border, rgba(212,175,55,0.38))',
          background: 'color-mix(in srgb, var(--wilsy-panel, #05070d) 84%, transparent)',
          color: 'var(--wilsy-authority, #d4af37)', boxShadow: '0 14px 40px rgba(0,0,0,0.28)',
          backdropFilter: 'blur(14px)', cursor: 'pointer'
        }}
      >
        <Crown size={17} />
      </button>

      <div aria-label="Standalone dashboard shard" style={{ minHeight: '100vh', width: '100%' }}>
        {children}
      </div>
    </div>
  );
};

// ─── Controller ──────────────────────────────────────────────────────────────

/**
 * @function SovereignDashboardController
 * @description Evaluates forensic identity and mounts the correct Command Center shard.
 *              Probes Kennel bridge health on mount for institutional telemetry.
 * @param {Object} props
 * @param {Object} props.user - Authenticated user from AuthProvider
 * @param {Function} [props.onLogout] - AuthProvider-owned logout command.
 */
const SovereignDashboardController = ({ user: propUser, onLogout }) => {
  const { activeTenant } = useTenants();
  const [manualDashboardKey, setManualDashboardKey] = useState('');
  const [systemServicesWorkspace, setSystemServicesWorkspace] = useState(null);
  const [systemServicesIncidents, setSystemServicesIncidents] = useState([]);
  const [systemServicesAssignments, setSystemServicesAssignments] = useState([]);
  const [systemServicesAssignmentDetail, setSystemServicesAssignmentDetail] = useState(null);
  const [systemServicesActionState, setSystemServicesActionState] = useState('');
  const systemServicesRequestRef = useRef(0);
  const [isGlobalCommandSearchOpen, setIsGlobalCommandSearchOpen] = useState(false);
  const [kernelHealth, setKernelHealth] = useState({
    status: 'UNKNOWN',
    latencyMs: 0,
    payload: null,
    error: null
  });
  const probeRef = useRef(null);

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

    const role = normalizeDashboardToken(user?.role || user?.accountRole || user?.tenantRole);

  useEffect(() => {
    systemServicesRequestRef.current += 1;
    setSystemServicesWorkspace(
      user?.systemServicesWorkspace?.status === 'READY'
      && user.systemServicesWorkspace.authority === 'EOS_SYSTEM_SERVICES'
        ? user.systemServicesWorkspace
        : null,
    );
    setSystemServicesIncidents([]);
    setSystemServicesAssignments([]);
    setSystemServicesAssignmentDetail(null);
    setSystemServicesActionState('');
    if (
      user?.systemServicesWorkspace?.status === 'READY'
      && user.systemServicesWorkspace.authority === 'EOS_SYSTEM_SERVICES'
      && user.systemServicesWorkspace.scope === 'SYSTEM'
      && user.systemServicesWorkspace.principalId === user.id
      && Array.isArray(user.systemServicesWorkspace.capabilities)
      && user.systemServicesWorkspace.capabilities.includes('system_services:queue:read')
    ) {
      setManualDashboardKey(DASHBOARD_KEYS.SYSTEM_SERVICES);
    } else if (manualDashboardKey === DASHBOARD_KEYS.SYSTEM_SERVICES) {
      setManualDashboardKey('');
    }
  }, [user?.id, user?.email]);
  useEffect(() => {
    const projection = user?.systemServicesWorkspace;
    if (
      projection?.status !== 'READY'
      || projection?.authority !== 'EOS_SYSTEM_SERVICES'
      || projection?.scope !== 'SYSTEM'
      || projection?.principalId !== user?.id
      || !projection?.capabilities?.includes('system_services:queue:read')
    ) return undefined;

    let active = true;
    const incidentRead = api.get('/system-services/security-incidents', { timeout: 12000 })
      .then((result) => Array.isArray(result?.data) ? result.data : [])
      .catch(() => []);
    const assignmentRead = projection.capabilities.includes('system_services:incident:escalate')
      ? api.get('/system-services/security-incident-assignments/mine', { timeout: 12000 })
        .then((result) => Array.isArray(result?.data) ? result.data : [])
        .catch(() => [])
      : Promise.resolve([]);
    Promise.all([incidentRead, assignmentRead]).then(([incidents, assignments]) => {
      if (!active) return;
      setSystemServicesIncidents(incidents);
      setSystemServicesAssignments(assignments);
    });
    return () => { active = false; };
  }, [user?.id, user?.systemServicesWorkspace]);

  const traceId = localStorage.getItem('traceId') || 'SYSTEM_CORE_INIT';

  const dashboardUser = useMemo(() => (
    user && systemServicesWorkspace ? { ...user, systemServicesWorkspace } : user
  ), [systemServicesWorkspace, user]);

  const dashboardKey = useMemo(() => (
    dashboardUser ? resolveDashboardKey({ user: dashboardUser, manualDashboardKey }) : ''
  ), [dashboardUser, manualDashboardKey]);

  const dashboardLabel = getDashboardDisplayName(dashboardKey);
  const canReturnToFounder = Boolean(
    user && dashboardKey && dashboardKey !== DASHBOARD_KEYS.FOUNDER && hasFounderReturnAuthority({ user, role })
  );

  const handleManualDashboardSwitch = useCallback((request = '') => {
    const resolvedDashboardKey = resolveDashboardRequestSignal(request);
    if (!resolvedDashboardKey) {
      console.warn('[SOVEREIGN-CONTROLLER] Dashboard switch ignored — unrecognized request.', request);
      return;
    }
    setManualDashboardKey(resolvedDashboardKey);
    if (typeof window !== 'undefined') {
      window.localStorage.setItem('wilsy_last_dashboard', resolvedDashboardKey);
      window.localStorage.setItem('wilsy:requested-dashboard', JSON.stringify({
        dashboardKey: resolvedDashboardKey,
        requestedAt: new Date().toISOString(),
        source: 'SovereignDashboardController'
      }));
    }
  }, []);

  // Kennel bridge health probe (Contract v1.1.0 — public /api/kernel)
  useEffect(() => {
    let cancelled = false;

    const runProbe = async () => {
      const result = await probeKernelBridge();
      if (cancelled) return;
      setKernelHealth(result);
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('wilsy:kernel-health', { detail: result }));
        try {
          window.localStorage.setItem('wilsy:kernel-health', JSON.stringify({
            ...result,
            probedAt: new Date().toISOString()
          }));
        } catch { /* ignore quota */ }
      }
    };

    runProbe();
    probeRef.current = setInterval(runProbe, KERNEL_PROBE_INTERVAL_MS);

    return () => {
      cancelled = true;
      if (probeRef.current) clearInterval(probeRef.current);
    };
  }, []);

  useEffect(() => {
    const handleDashboardRouteRequest = (event = {}) => {
      if (event.type === 'storage' && event.key && event.key !== 'wilsy:requested-dashboard') return;
      const storageTarget = event.type === 'storage' ? readRequestedDashboardFromStorage() : '';
      const eventTarget = event.type === 'storage'
        ? storageTarget
        : resolveDashboardRequestSignal(event.detail || event);
      const targetDashboardKey = eventTarget || storageTarget;
      if (!targetDashboardKey) return;
      setManualDashboardKey(targetDashboardKey);
    };

    const initialRequestedDashboard = readRequestedDashboardFromStorage();
    if (initialRequestedDashboard) setManualDashboardKey(initialRequestedDashboard);

    window.addEventListener('wilsy:navigate-dashboard', handleDashboardRouteRequest);
    window.addEventListener('wilsy:switch-dashboard', handleDashboardRouteRequest);
    window.addEventListener('wilsy:open-dashboard', handleDashboardRouteRequest);
    window.addEventListener('wilsy:requested-dashboard', handleDashboardRouteRequest);
    window.addEventListener('storage', handleDashboardRouteRequest);

    return () => {
      window.removeEventListener('wilsy:navigate-dashboard', handleDashboardRouteRequest);
      window.removeEventListener('wilsy:switch-dashboard', handleDashboardRouteRequest);
      window.removeEventListener('wilsy:open-dashboard', handleDashboardRouteRequest);
      window.removeEventListener('wilsy:requested-dashboard', handleDashboardRouteRequest);
      window.removeEventListener('storage', handleDashboardRouteRequest);
    };
  }, []);

  useEffect(() => {
    applyWilsyThemeRuntime();
    const syncThemeRuntime = () => applyWilsyThemeRuntime();
    window.addEventListener('storage', syncThemeRuntime);
    window.addEventListener('wilsy:theme-change', syncThemeRuntime);
    return () => {
      window.removeEventListener('storage', syncThemeRuntime);
      window.removeEventListener('wilsy:theme-change', syncThemeRuntime);
    };
  }, []);

  useEffect(() => {
    const handleGlobalCommandSearchKeyDown = (event) => {
      const isKeyboardShortcut = event?.type === 'keydown'
        && String(event.key || '').toLowerCase() === 'k'
        && (event.metaKey || event.ctrlKey);
      const isCustomOpen = event?.type === 'wilsy:open-command-search';
      if (!isKeyboardShortcut && !isCustomOpen) return;
      event.preventDefault?.();
      setIsGlobalCommandSearchOpen(true);
    };

    window.addEventListener('keydown', handleGlobalCommandSearchKeyDown);
    window.addEventListener('wilsy:open-command-search', handleGlobalCommandSearchKeyDown);
    return () => {
      window.removeEventListener('keydown', handleGlobalCommandSearchKeyDown);
      window.removeEventListener('wilsy:open-command-search', handleGlobalCommandSearchKeyDown);
    };
  }, []);

  // Mount telemetry once per identity+dashboard (not on every kernel poll)
  const mountLoggedRef = useRef('');
  useEffect(() => {
    if (!user || !user.tenantId || !role || !dashboardKey) return;
    const mountKey = `${user.email || user.id || ''}|${dashboardKey}|${role}`;
    if (mountLoggedRef.current === mountKey) return;
    mountLoggedRef.current = mountKey;

    broadcastTelemetry(
      user.tenantId,
      'DASHBOARD_EVENT',
      'DASHBOARD_MOUNT_SUCCESS',
      user.email || user.id,
      {
        role,
        dashboardKey,
        dashboardLabel,
        traceId,
        version: CONTROLLER_VERSION,
        kernelStatus: kernelHealth.status,
        kernelLatencyMs: kernelHealth.latencyMs
      }
    );

    if (import.meta.env.DEV) {
      console.info(
        `[SOVEREIGN-CONTROLLER] Shard Mounted: ${dashboardKey} | Role: ${role} | Trace: ${traceId}`
      );
    }
  }, [dashboardKey, dashboardLabel, role, traceId, user]); // intentionally omit kernelHealth — polls must not re-log

  if (!user) {
    if (import.meta.env.DEV) {
      console.warn('[SOVEREIGN-CONTROLLER] No identity shard discovered. Reverting to Gateway.', { traceId });
    }
    return <Navigate to="/login" replace />;
  }

  let dashboardShard = null;
  if (dashboardKey === DASHBOARD_KEYS.SYSTEM_SERVICES) {
    dashboardShard = (
      <SystemServicesDashboard
        workspace={dashboardUser?.systemServicesWorkspace || null}
        incidents={systemServicesIncidents}
        assignments={systemServicesAssignments}
        assignmentDetail={systemServicesAssignmentDetail}
        actionState={systemServicesActionState}
        onOpenAssignment={handleOpenSystemServicesAssignment}
        onDecideAssignment={handleSystemServicesAssignmentDecision}
      />
    );
  } else   if (dashboardKey === DASHBOARD_KEYS.FOUNDER) {
    dashboardShard = <FounderDashboard user={user} onSwitchDashboard={handleManualDashboardSwitch} />;
  } else if (dashboardKey === DASHBOARD_KEYS.EXECUTIVE) {
    dashboardShard = (
      <ExecutiveDashboard
        role={getExecutiveRoleLabel(user)}
        user={user}
        onSwitchDashboard={handleManualDashboardSwitch}
      />
    );
  } else if (dashboardKey === DASHBOARD_KEYS.COO) {
    dashboardShard = <COODashboard user={user} />;
  } else if (dashboardKey === DASHBOARD_KEYS.CRM) {
    const crmTenantId = activeTenant?.tenantId || activeTenant?._id || user?.tenantId || '';
    dashboardShard = crmTenantId ? (
      <BusinessProvider tenantId={crmTenantId}>
        <CRMDashboard
          user={user}
          activeTenant={activeTenant}
          tenantId={crmTenantId}
          founderReturnEnabled={canReturnToFounder}
          onFounderReturn={() => handleManualDashboardSwitch(DASHBOARD_KEYS.FOUNDER)}
        />
      </BusinessProvider>
    ) : (
      <div role="alert">CRM tenant context unavailable.</div>
    );
  } else if (dashboardKey === DASHBOARD_KEYS.SALES) {
    dashboardShard = <SalesDashboard user={user} />;
  } else if (dashboardKey === DASHBOARD_KEYS.FINANCE) {
    // 🆕 Use the sovereign BillingHUD instead of the legacy FinanceDashboard
    dashboardShard = <BillingHUD user={user} />;
  } else if (dashboardKey === DASHBOARD_KEYS.HR) {
    dashboardShard = <HRDashboard user={user} />;
  } else if (dashboardKey === DASHBOARD_KEYS.OPERATIONS) {
    dashboardShard = <OperationsDashboard user={user} activeTenant={activeTenant} />;
  } else if (dashboardKey === DASHBOARD_KEYS.INTELLIGENCE) {
    dashboardShard = <IntelligenceDashboard user={user} activeTenant={activeTenant} />;
  } else if (dashboardKey === DASHBOARD_KEYS.IT) {
    dashboardShard = <ITDashboard user={user} />;
  } else if (dashboardKey === DASHBOARD_KEYS.LEGAL) {
    dashboardShard = (
      <LegalDashboard
        user={user}
        tenantConfig={activeTenant}
        roleView={role}
        onLogout={onLogout}
      />
    );
  } else if (dashboardKey === DASHBOARD_KEYS.GENERAL) {
    dashboardShard = <GeneralDashboard user={user} />;
  } else {
    console.error('[SOVEREIGN-CONTROLLER] Identity fragment unrecognized.', {
      role, dashboardKey, traceId, timestamp: new Date().toISOString()
    });
    return <Navigate to="/unauthorized" replace />;
  }

  const handleGlobalSearchNavigate = (result = {}) => {
    if (result.command === 'OPEN_SYSTEM_SERVICES') {
      const requestId = ++systemServicesRequestRef.current;
      setSystemServicesWorkspace(null);
      api.get('/system-services/workspace-bootstrap', { timeout: 12000 })
        .then(async (response) => {
          if (requestId !== systemServicesRequestRef.current) return;
          const projection = response?.data;
          if (
            projection?.status === 'READY'
            && projection?.authority === 'EOS_SYSTEM_SERVICES'
            && typeof projection?.principalId === 'string'
            && Array.isArray(projection?.capabilities)
            && projection.capabilities.includes('system_services:queue:read')
          ) {
            setSystemServicesWorkspace(projection);
            setManualDashboardKey(DASHBOARD_KEYS.SYSTEM_SERVICES);
            const incidentRead = api.get('/system-services/security-incidents', { timeout: 12000 })
              .then((result) => Array.isArray(result?.data) ? result.data : [])
              .catch(() => []);
            const assignmentRead = projection.capabilities.includes('system_services:incident:escalate')
              ? api.get('/system-services/security-incident-assignments/mine', { timeout: 12000 })
                .then((result) => Array.isArray(result?.data) ? result.data : [])
                .catch(() => [])
              : Promise.resolve([]);
            const [incidentRows, assignmentRows] = await Promise.all([incidentRead, assignmentRead]);
            if (requestId !== systemServicesRequestRef.current) return;
            setSystemServicesIncidents(incidentRows);
            setSystemServicesAssignments(assignmentRows);
          }
        })
        .catch(() => {
          if (requestId === systemServicesRequestRef.current) {
            setSystemServicesWorkspace(null);
            setSystemServicesIncidents([]);
            setSystemServicesAssignments([]);
            setSystemServicesAssignmentDetail(null);
            setManualDashboardKey('');
          }
        });
      return;
    }
    if (result.dashboardKey) handleManualDashboardSwitch(result.dashboardKey);
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('wilsy:global-search-activate', {
        detail: {
          ...result,
          tenantId: activeTenant?.tenantId || activeTenant?._id || user?.tenantId || 'MASTER'
        }
      }));
      window.localStorage.setItem('wilsy:last-global-search-result', JSON.stringify({
        ...result,
        activatedAt: new Date().toISOString()
      }));
    }
  };


  async function handleOpenSystemServicesAssignment(assignmentId) {
    setSystemServicesActionState('Loading authorized incident detail…');
    try {
      const response = await api.get(
        '/system-services/security-incident-assignments/' + encodeURIComponent(assignmentId),
        { timeout: 12000, forceNetworkRetry: true },
      );
      setSystemServicesAssignmentDetail(response?.data || null);
      setSystemServicesActionState('');
    } catch {
      setSystemServicesAssignmentDetail(null);
      setSystemServicesActionState('Incident detail is unavailable or this assignment is no longer authorized.');
    }
  }

  async function handleSystemServicesAssignmentDecision(assignmentId, decision) {
    const assignment = systemServicesAssignments.find((item) => item.assignmentId === assignmentId);
    if (!assignment || assignment.status !== 'PENDING_ACCEPTANCE' || !['accept', 'decline'].includes(decision)) return;
    setSystemServicesActionState('Submitting responder decision to EOS…');
    const nonce = window.crypto?.randomUUID?.()
      || ('ss-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2));
    try {
      await api.post(
        '/system-services/security-incident-assignments/' + encodeURIComponent(assignmentId) + '/' + decision,
        { expected_revision: assignment.revision },
        { headers: { 'Idempotency-Key': nonce }, timeout: 12000 },
      );
      const refreshed = await api.get('/system-services/security-incident-assignments/mine', {
        timeout: 12000, forceNetworkRetry: true,
      });
      setSystemServicesAssignments(Array.isArray(refreshed?.data) ? refreshed.data : []);
      if (systemServicesAssignmentDetail?.assignment?.assignmentId === assignmentId) {
        await handleOpenSystemServicesAssignment(assignmentId);
      }
      setSystemServicesActionState(decision === 'accept'
        ? 'EOS recorded responder acceptance. No containment or account action was performed.'
        : 'EOS recorded responder decline. No containment or account action was performed.');
    } catch {
      setSystemServicesActionState('EOS did not confirm this decision. Refresh the inbox before retrying.');
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // FIX: Wrap guardedShard in an overflow-enabled container to allow
  // BillingHUD's padding-bottom:208px to expand without clipping.
  // ═══════════════════════════════════════════════════════════════════════════
  const guardedShard = (
    <div style={{ overflowX: 'hidden', overflowY: 'auto', minHeight: '100vh', width: '100%' }}>
      <ErrorBoundary>
        {dashboardShard}
      </ErrorBoundary>
    </div>
  );

  const kernelDegraded = kernelHealth.status !== 'OPERATIONAL' && kernelHealth.status !== 'UNKNOWN';

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
      {kernelDegraded && (
        <div
          role="status"
          aria-live="polite"
          style={{
            position: 'fixed', top: 12, right: 12, zIndex: 3000,
            display: 'inline-flex', alignItems: 'center', gap: 8,
            padding: '8px 12px', borderRadius: 8,
            border: '1px solid rgba(255,138,164,0.45)',
            background: 'rgba(20,8,12,0.92)', color: '#FF8AA4',
            fontFamily: 'JetBrains Mono, ui-monospace, monospace',
            fontSize: 10, letterSpacing: '0.06em', textTransform: 'uppercase'
          }}
        >
          <ShieldAlert size={14} />
          <span>Kernel {kernelHealth.status}</span>
          {kernelHealth.latencyMs > 0 && <span>· {kernelHealth.latencyMs}ms</span>}
        </div>
      )}

      <WilsyGlobalCommandSearch
        isOpen={isGlobalCommandSearchOpen}
        onClose={() => setIsGlobalCommandSearchOpen(false)}
        onNavigate={handleGlobalSearchNavigate}
        user={user}
        activeTenant={activeTenant}
        currentDashboardKey={dashboardKey}
      />

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

/**
 * ARTIFACT: SovereignDashboardController.jsx
 * VERSION: v18.6.0-CANONICAL-KERNEL-HEALTH-TRANSPORT
 * AUTHORITY BOUNDARY: authenticated client dashboard routing and presentation composition only
 * TENANT POSTURE: active tenant projection is preserved; Legal OS role routing cannot widen server tenant scope
 * FAIL-CLOSED POSTURE: unknown roles/dashboards do not manufacture Legal Operations access or cross-role fallback
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
