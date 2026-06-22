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

import React, { Suspense, useCallback, useEffect, useMemo, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { ArrowLeft, Crown, Loader2 } from 'lucide-react';
import { useTenants } from '../../contexts/tenantContext.jsx';
import { broadcastTelemetry } from '../../utils/telemetryHelper.js';
import ErrorBoundary from '../ErrorBoundary';
import WilsyGlobalCommandSearch from './WilsyGlobalCommandSearch';

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


const WILSY_THEME_STORAGE_KEYS = Object.freeze({
  theme: 'wilsy:account-command-center:theme',
  mode: 'wilsy:account-command-center:mode'
});

const WILSY_OPERATING_SKINS = Object.freeze({
  wilsy_aurora: {
    id: 'wilsy_aurora',
    bg: '#020306',
    surface: '#070B18',
    panel: '#0B1024',
    rail: '#080C18',
    text: '#FFFAF0',
    muted: '#C5CCE5',
    accent: '#B66DFF',
    authority: '#D4AF37',
    live: '#84F0C8',
    risk: '#FF8AA4',
    border: 'rgba(182,109,255,0.34)'
  },
  sovereign_black: {
    id: 'sovereign_black',
    bg: '#000000',
    surface: '#050505',
    panel: '#0B0B0B',
    rail: '#030303',
    text: '#FFFFFF',
    muted: '#A7A7A7',
    accent: '#D4AF37',
    authority: '#F6D76B',
    live: '#56D69B',
    risk: '#FF6673',
    border: 'rgba(212,175,55,0.32)'
  },
  cobalt_glass: {
    id: 'cobalt_glass',
    bg: '#020817',
    surface: '#06142E',
    panel: '#0A1D3D',
    rail: '#07132B',
    text: '#F3F8FF',
    muted: '#AFC7F6',
    accent: '#17BDF2',
    authority: '#8DBBFF',
    live: '#54F0D1',
    risk: '#FF7C98',
    border: 'rgba(23,189,242,0.34)'
  },
  pearl_command: {
    id: 'pearl_command',
    bg: '#F6F8FF',
    surface: '#FFFFFF',
    panel: '#EEF2FF',
    rail: '#FFFFFF',
    text: '#111827',
    muted: '#53617F',
    accent: '#7C68FF',
    authority: '#C49A18',
    live: '#0F9F6E',
    risk: '#D33F62',
    border: 'rgba(124,104,255,0.26)'
  },
  legacy_gold: {
    id: 'legacy_gold',
    bg: '#070602',
    surface: '#0D0A03',
    panel: '#141006',
    rail: '#090702',
    text: '#FFF8DC',
    muted: '#B9A56D',
    accent: '#D4AF37',
    authority: '#F6D76B',
    live: '#8FE6B1',
    risk: '#FF8A8A',
    border: 'rgba(246,215,107,0.32)'
  },
  forensic_violet: {
    id: 'forensic_violet',
    bg: '#05020A',
    surface: '#0D0718',
    panel: '#140B26',
    rail: '#090412',
    text: '#FFF7FF',
    muted: '#CAB8EA',
    accent: '#B66DFF',
    authority: '#E7B7FF',
    live: '#84F0C8',
    risk: '#FF8AA4',
    border: 'rgba(182,109,255,0.36)'
  },
  quantum: {
    id: 'quantum',
    bg: '#01050A',
    surface: '#06111A',
    panel: '#071C25',
    rail: '#031018',
    text: '#F5FFFF',
    muted: '#9FD7E7',
    accent: '#17F2D1',
    authority: '#B6F6FF',
    live: '#84F0C8',
    risk: '#FF789A',
    border: 'rgba(23,242,209,0.34)'
  }
});

/**
 * @function normalizeWilsyThemeId
 * @description Normalizes saved and legacy theme identifiers into supported Wilsy OS operating skins.
 * @param {string} themeId - Candidate theme id.
 * @returns {string} Supported operating skin id.
 * @collaboration Allows old saved preferences to keep working while the full OS moves into sovereign operating skins.
 */
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

/**
 * @function normalizeWilsyThemeMode
 * @description Normalizes saved theme mode into day, night or auto.
 * @param {string} mode - Candidate mode.
 * @returns {string} Safe mode id.
 * @collaboration Keeps every mounted dashboard reading the same operating mode vocabulary.
 */
const normalizeWilsyThemeMode = (mode = '') => (
  ['day', 'night', 'auto'].includes(mode) ? mode : 'night'
);

/**
 * @function resolveWilsyThemeMode
 * @description Resolves auto mode against local operator time.
 * @param {string} mode - Requested mode.
 * @returns {string} Resolved mode id.
 * @collaboration Gives Wilsy OS an adaptive cockpit without requiring an external preference service.
 */
const resolveWilsyThemeMode = (mode = 'night') => {
  const safeMode = normalizeWilsyThemeMode(mode);
  if (safeMode !== 'auto') return safeMode;
  const hour = new Date().getHours();
  return hour >= 7 && hour < 18 ? 'day' : 'night';
};

/**
 * @function readWilsyThemePreference
 * @description Reads saved Wilsy OS theme preference from localStorage.
 * @returns {{themeId:string,mode:string,resolvedMode:string,skin:Object}} Theme preference packet.
 * @collaboration Makes the controller the operating-system level bridge between Account Command Center and all dashboards.
 */
const readWilsyThemePreference = () => {
  const themeId = normalizeWilsyThemeId(
    typeof window === 'undefined'
      ? 'wilsy_aurora'
      : window.localStorage.getItem(WILSY_THEME_STORAGE_KEYS.theme)
  );
  const mode = normalizeWilsyThemeMode(
    typeof window === 'undefined'
      ? 'night'
      : window.localStorage.getItem(WILSY_THEME_STORAGE_KEYS.mode)
  );
  const resolvedMode = resolveWilsyThemeMode(mode);
  const skin = WILSY_OPERATING_SKINS[themeId] || WILSY_OPERATING_SKINS.wilsy_aurora;
  return { themeId, mode, resolvedMode, skin };
};

/**
 * @function installWilsyThemeRuntimeStyle
 * @description Installs global CSS variable bridges used by every Wilsy OS dashboard.
 * @returns {void}
 * @collaboration Converts account preferences from a local panel setting into a system-wide operating skin layer.
 */
const installWilsyThemeRuntimeStyle = () => {
  if (typeof document === 'undefined') return;

  const styleId = 'wilsy-os-theme-runtime-style';
  if (document.getElementById(styleId)) return;

  const style = document.createElement('style');
  style.id = styleId;
  style.textContent = `
    :root {
      color-scheme: dark;
    }

    html[data-wilsy-resolved-mode="day"] {
      color-scheme: light;
    }

    body {
      background:
        radial-gradient(circle at 8% 0%, color-mix(in srgb, var(--wilsy-accent) 14%, transparent), transparent 30%),
        radial-gradient(circle at 88% 8%, color-mix(in srgb, var(--wilsy-live) 10%, transparent), transparent 32%),
        var(--wilsy-bg) !important;
      color: var(--wilsy-text) !important;
    }

    #root {
      min-height: 100vh;
      background: transparent !important;
      color: var(--wilsy-text) !important;
    }

    .wilsy-theme-bg {
      background: var(--wilsy-bg) !important;
      color: var(--wilsy-text) !important;
    }

    .wilsy-theme-surface {
      background: var(--wilsy-surface) !important;
      color: var(--wilsy-text) !important;
      border-color: var(--wilsy-border) !important;
    }

    .wilsy-theme-panel {
      background: var(--wilsy-panel) !important;
      color: var(--wilsy-text) !important;
      border-color: var(--wilsy-border) !important;
    }

    .wilsy-theme-accent {
      color: var(--wilsy-accent) !important;
    }

    .wilsy-theme-authority {
      color: var(--wilsy-authority) !important;
    }
  `;
  document.head.appendChild(style);
};

/**
 * @function applyWilsyThemeRuntime
 * @description Applies the current Wilsy OS operating skin to document root and body CSS variables.
 * @returns {{themeId:string,mode:string,resolvedMode:string}} Applied theme identity.
 * @collaboration Propagates saved Account Command Center receipts into every dashboard mounted by SovereignDashboardController.
 */
const applyWilsyThemeRuntime = () => {
  const preference = readWilsyThemePreference();

  if (typeof document === 'undefined') {
    return {
      themeId: preference.themeId,
      mode: preference.mode,
      resolvedMode: preference.resolvedMode
    };
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
    '--wilsy-bg': isDay && preference.themeId === 'pearl_command' ? skin.bg : skin.bg,
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

  return {
    themeId: preference.themeId,
    mode: preference.mode,
    resolvedMode: preference.resolvedMode
  };
};

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
 * @function resolveDashboardRequestSignal
 * @description Extracts a canonical dashboard key from route events, object payloads, slugs and legacy module requests.
 * @param {unknown} request - Dashboard request from FounderDashboard, storage or custom event.
 * @returns {string} Canonical dashboard key or empty string.
 * @collaboration Forces specialist dashboards like CRM to leave FounderDashboard chrome and mount through SovereignDashboardController.
 */
export const resolveDashboardRequestSignal = (request = '') => {
  if (!request) return '';

  if (typeof request === 'string') {
    return mapDashboardAlias(request);
  }

  if (typeof request !== 'object') {
    return '';
  }

  const directSignals = [
    request.dashboardKey,
    request.dashboard,
    request.key,
    request.id,
    request.module,
    request.moduleKey,
    request.dashboardName,
    request.target,
    request.value
  ];

  const directTarget = directSignals.map(mapDashboardAlias).find(Boolean);
  if (directTarget) return directTarget;

  const routeSignal = String(request.route || request.path || request.href || '').replace(/^\/+/, '');
  if (routeSignal) {
    return mapDashboardAlias(routeSignal);
  }

  return '';
};

/**
 * @function readRequestedDashboardFromStorage
 * @description Reads the last requested dashboard packet from localStorage without throwing on malformed payloads.
 * @returns {string} Canonical dashboard key or empty string.
 * @collaboration Lets nested Founder cards and specialist shards request standalone routing through a shared storage receipt.
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
const FounderReturnFrame = ({ dashboardLabel, onReturn, children }) => {
  const [founderDockOpen, setFounderDockOpen] = useState(false);

  useEffect(() => {
    const openFounderDock = () => setFounderDockOpen(true);
    window.addEventListener('wilsy:show-founder-return', openFounderDock);
    return () => {
      window.removeEventListener('wilsy:show-founder-return', openFounderDock);
    };
  }, []);

  return (
    <div style={{ minHeight: "100vh", background: "var(--wilsy-bg, #050505)", color: "var(--wilsy-text, #f8fafc)", position: "relative" }}>
      {founderDockOpen && (
        <div
          role="region"
          aria-label="Founder return controls"
          style={{
            position: "fixed",
            left: 22,
            top: 72,
            zIndex: 2500,
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
            minHeight: 44,
            padding: "6px 8px",
            borderRadius: 999,
            border: "1px solid var(--wilsy-border, rgba(212,175,55,0.42))",
            background: "color-mix(in srgb, var(--wilsy-panel, #05070d) 88%, transparent)",
            boxShadow: "0 18px 50px rgba(0,0,0,0.36)",
            backdropFilter: "blur(16px)",
            fontFamily: "JetBrains Mono, IBM Plex Mono, ui-monospace, monospace"
          }}
        >
          <button
            type="button"
            onClick={onReturn}
            aria-label="Return to Founder Dashboard"
            title={"Return to Founder Dashboard from " + dashboardLabel}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 9,
              minHeight: 34,
              padding: "0 12px",
              borderRadius: 999,
              border: 0,
              background: "transparent",
              color: "var(--wilsy-text, #fffaf0)",
              font: "inherit",
              fontSize: 11,
              fontWeight: 900,
              letterSpacing: "0.08em",
              textTransform: "uppercase",
              cursor: "pointer"
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
              width: 30,
              height: 30,
              display: "grid",
              placeItems: "center",
              borderRadius: 999,
              border: "1px solid var(--wilsy-border, rgba(212,175,55,0.18))",
              background: "rgba(0,0,0,0.22)",
              color: "var(--wilsy-text, #fffaf0)",
              cursor: "pointer"
            }}
          >
            ×
          </button>
        </div>
      )}

      <button
        type="button"
        onClick={() => setFounderDockOpen(value => !value)}
        aria-label="Show founder return controls"
        title="Founder return"
        style={{
          position: "fixed",
          left: 22,
          bottom: 22,
          zIndex: 2499,
          width: 44,
          height: 44,
          display: "grid",
          placeItems: "center",
          borderRadius: 999,
          border: "1px solid var(--wilsy-border, rgba(212,175,55,0.38))",
          background: "color-mix(in srgb, var(--wilsy-panel, #05070d) 84%, transparent)",
          color: "var(--wilsy-authority, #d4af37)",
          boxShadow: "0 14px 40px rgba(0,0,0,0.28)",
          backdropFilter: "blur(14px)",
          cursor: "pointer"
        }}
      >
        <Crown size={17} />
      </button>

      <div aria-label="Standalone dashboard shard" style={{ minHeight: "100vh", width: "100%" }}>
        {children}
      </div>
    </div>
  );
};

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
  const [isGlobalCommandSearchOpen, setIsGlobalCommandSearchOpen] = useState(false);

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
   * @function handleManualDashboardSwitch
   * @description Normalizes dashboard switch requests before updating controller state.
   * @param {unknown} request - Requested dashboard key, slug, route or object payload.
   * @returns {void}
   * @collaboration Prevents CRM and other specialist dashboards from being rendered inside FounderDashboard when a standalone shard exists.
   */
  const handleManualDashboardSwitch = useCallback((request = '') => {
    const resolvedDashboardKey = resolveDashboardRequestSignal(request);
    if (!resolvedDashboardKey) {
      console.warn('[SOVEREIGN-CONTROLLER] Dashboard switch ignored because request was not recognized.', request);
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




  useEffect(() => {
    /**
     * @function handleDashboardRouteRequest
     * @description Routes Wilsy OS dashboard navigation events through the controller instead of nested dashboard chrome.
     * @param {CustomEvent|StorageEvent} event - Dashboard route event or storage mutation.
     * @returns {void}
     * @collaboration Makes CRM, Sales, Finance, HR and Executive open as standalone shards from FounderDashboard and Command K.
     */
    const handleDashboardRouteRequest = (event = {}) => {
      if (event.type === 'storage' && event.key && event.key !== 'wilsy:requested-dashboard') return;

      const storageTarget = event.type === 'storage'
        ? readRequestedDashboardFromStorage()
        : '';

      const eventTarget = event.type === 'storage'
        ? storageTarget
        : resolveDashboardRequestSignal(event.detail || event);

      const targetDashboardKey = eventTarget || storageTarget;
      if (!targetDashboardKey) return;

      setManualDashboardKey(targetDashboardKey);
    };

    const initialRequestedDashboard = readRequestedDashboardFromStorage();
    if (initialRequestedDashboard) {
      setManualDashboardKey(initialRequestedDashboard);
    }

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

    const syncThemeRuntime = () => {
      applyWilsyThemeRuntime();
    };

    window.addEventListener('storage', syncThemeRuntime);
    window.addEventListener('wilsy:theme-change', syncThemeRuntime);

    return () => {
      window.removeEventListener('storage', syncThemeRuntime);
      window.removeEventListener('wilsy:theme-change', syncThemeRuntime);
    };
  }, []);

  useEffect(() => {
    /**
     * @function handleGlobalCommandSearchKeyDown
     * @description Opens Wilsy OS global command search from keyboard or custom events.
     * @param {KeyboardEvent|CustomEvent} event - Keyboard or custom open event.
     * @returns {void}
     * @collaboration Makes Command K a system-level operating gesture across Founder, Executive, HR, CRM and Finance shards.
     */
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
    dashboardShard = <FounderDashboard user={user} onSwitchDashboard={handleManualDashboardSwitch} />;
  } else if (dashboardKey === DASHBOARD_KEYS.EXECUTIVE) {
    dashboardShard = <ExecutiveDashboard role={getExecutiveRoleLabel(user)} user={user} />;
  } else if (dashboardKey === DASHBOARD_KEYS.COO) {
    dashboardShard = <COODashboard user={user} />;
  } else if (dashboardKey === DASHBOARD_KEYS.CRM) {
    dashboardShard = (
      <CRMDashboard
        user={user}
        activeTenant={activeTenant}
        tenantId={activeTenant?.tenantId || activeTenant?._id || user?.tenantId || 'MASTER'}
        founderReturnEnabled={canReturnToFounder}
        onFounderReturn={() => handleManualDashboardSwitch(DASHBOARD_KEYS.FOUNDER)}
      />
    );
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

  /**
   * @function handleGlobalSearchNavigate
   * @description Routes global command search results into dashboards, routes or command events.
   * @param {Object} result - Activated global search result.
   * @returns {void}
   * @collaboration Turns Command K into a real OS switchboard instead of a decorative search placeholder.
   */
  const handleGlobalSearchNavigate = (result = {}) => {
    if (result.dashboardKey) {
      handleManualDashboardSwitch(result.dashboardKey);
    }

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
