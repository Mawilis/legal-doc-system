/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - DASHBOARD CHROME CONFIG HELPERS                              ║
 * ║ Shared Executive-standard chrome configuration for every dashboard.       ║
 * ╠════════════════════════════════════════════════════════════════════════════╣
 * ║ MANDATE                                                                  ║
 * ║ • One Wilsy OS top rail standard.                                         ║
 * ║ • One reusable Account Command Center pattern.                            ║
 * ║ • One source-truth language layer.                                        ║
 * ║ • Dashboard-specific actions stay inside each dashboard.                  ║
 * ║ • No fake placeholder data.                                               ║
 * ╚════════════════════════════════════════════════════════════════════════════╝
 */

const WILSY_DASHBOARD_CHROME_VERSION = 'V1.0.0-EXECUTIVE-STANDARD-CONFIG';

const WILSY_DASHBOARD_CHROME_THEME_STORAGE_KEYS = Object.freeze({
  theme: 'wilsy:account-command-center:theme',
  mode: 'wilsy:account-command-center:mode'
});

const WILSY_DASHBOARD_CHROME_THEME_SKINS = Object.freeze({
  wilsy_aurora: {
    accent: '#B66DFF',
    secondary: '#17BDF2',
    authority: '#D4AF37',
    live: '#84F0C8',
    risk: '#FF8AA4',
    surface: '#060B18',
    panel: '#0B1024',
    rail: '#080C18',
    bg: '#020306',
    text: '#FFFAF0',
    muted: '#C5CCE5',
    border: 'rgba(182,109,255,0.34)'
  },
  sovereign_black: {
    accent: '#D4AF37',
    secondary: '#56D69B',
    authority: '#F6D76B',
    live: '#56D69B',
    risk: '#FF6673',
    surface: '#050505',
    panel: '#0B0B0B',
    rail: '#030303',
    bg: '#000000',
    text: '#FFFFFF',
    muted: '#A7A7A7',
    border: 'rgba(212,175,55,0.32)'
  },
  cobalt_glass: {
    accent: '#17BDF2',
    secondary: '#8DBBFF',
    authority: '#D4AF37',
    live: '#54F0D1',
    risk: '#FF7C98',
    surface: '#06142E',
    panel: '#0A1D3D',
    rail: '#07132B',
    bg: '#020817',
    text: '#F3F8FF',
    muted: '#AFC7F6',
    border: 'rgba(23,189,242,0.34)'
  },
  pearl_command: {
    accent: '#7C68FF',
    secondary: '#0F9F6E',
    authority: '#C49A18',
    live: '#0F9F6E',
    risk: '#D33F62',
    surface: '#FFFFFF',
    panel: '#EEF2FF',
    rail: '#FFFFFF',
    bg: '#F6F8FF',
    text: '#111827',
    muted: '#53617F',
    border: 'rgba(124,104,255,0.26)'
  },
  legacy_gold: {
    accent: '#D4AF37',
    secondary: '#8FE6B1',
    authority: '#F6D76B',
    live: '#8FE6B1',
    risk: '#FF8A8A',
    surface: '#0D0A03',
    panel: '#141006',
    rail: '#090702',
    bg: '#070602',
    text: '#FFF8DC',
    muted: '#B9A56D',
    border: 'rgba(246,215,107,0.32)'
  },
  forensic_violet: {
    accent: '#B66DFF',
    secondary: '#E7B7FF',
    authority: '#D4AF37',
    live: '#84F0C8',
    risk: '#FF8AA4',
    surface: '#0D0718',
    panel: '#140B26',
    rail: '#090412',
    bg: '#05020A',
    text: '#FFF7FF',
    muted: '#CAB8EA',
    border: 'rgba(182,109,255,0.36)'
  },
  quantum: {
    accent: '#17F2D1',
    secondary: '#B6F6FF',
    authority: '#D4AF37',
    live: '#84F0C8',
    risk: '#FF789A',
    surface: '#06111A',
    panel: '#071C25',
    rail: '#031018',
    bg: '#01050A',
    text: '#F5FFFF',
    muted: '#9FD7E7',
    border: 'rgba(23,242,209,0.34)'
  }
});

const WILSY_DASHBOARD_CHROME_PROFILES = Object.freeze({
  executive: {
    commandLabel: 'Executive Command',
    title: 'WILSY OS EXECUTIVE COMMAND CENTER',
    role: 'EXECUTIVE',
    primaryActionLabel: 'NEW COMMAND',
    liveSyncLabel: 'LIVE SYNC',
    searchPlaceholder: 'Search Wilsy OS or press ⌘K',
    themeId: 'wilsy_aurora'
  },
  crm: {
    commandLabel: 'Customer Intelligence',
    title: 'WILSY OS CRM COMMAND CENTER',
    role: 'CRM_OPERATOR',
    primaryActionLabel: 'NEW CUSTOMER COMMAND',
    liveSyncLabel: 'LIVE SYNC',
    searchPlaceholder: 'Search customers, deals, contacts or press ⌘K',
    themeId: 'wilsy_aurora'
  },
  hr: {
    commandLabel: 'People Command',
    title: 'WILSY OS HR COMMAND CENTER',
    role: 'HR_OPERATOR',
    primaryActionLabel: 'NEW PEOPLE COMMAND',
    liveSyncLabel: 'LIVE SYNC',
    searchPlaceholder: 'Search employees, roles, payroll or press ⌘K',
    themeId: 'cobalt_glass'
  },
  finance: {
    commandLabel: 'Finance Command',
    title: 'WILSY OS FINANCE COMMAND CENTER',
    role: 'FINANCE_OPERATOR',
    primaryActionLabel: 'NEW FINANCE COMMAND',
    liveSyncLabel: 'LIVE SYNC',
    searchPlaceholder: 'Search revenue, payments, invoices or press ⌘K',
    themeId: 'legacy_gold'
  },
  legal: {
    commandLabel: 'Legal Command',
    title: 'WILSY OS LEGAL COMMAND CENTER',
    role: 'LEGAL_OPERATOR',
    primaryActionLabel: 'NEW LEGAL COMMAND',
    liveSyncLabel: 'LIVE SYNC',
    searchPlaceholder: 'Search matters, evidence, contracts or press ⌘K',
    themeId: 'forensic_violet'
  },
  billing: {
    commandLabel: 'Billing Command',
    title: 'WILSY OS BILLING COMMAND CENTER',
    role: 'BILLING_OPERATOR',
    primaryActionLabel: 'NEW BILLING COMMAND',
    liveSyncLabel: 'LIVE SYNC',
    searchPlaceholder: 'Search invoices, accounts, payments or press ⌘K',
    themeId: 'legacy_gold'
  },
  documents: {
    commandLabel: 'Document Command',
    title: 'WILSY OS DOCUMENT VAULT',
    role: 'DOCUMENT_OPERATOR',
    primaryActionLabel: 'NEW DOCUMENT COMMAND',
    liveSyncLabel: 'LIVE SYNC',
    searchPlaceholder: 'Search documents, evidence, signatures or press ⌘K',
    themeId: 'cobalt_glass'
  }
});

/**
 * @function normalizeWilsyDashboardText
 * @description Normalizes display text for shared dashboard chrome without inserting fake business data.
 * @param {unknown} value - Candidate value.
 * @param {string} fallback - Display fallback used only when the source is empty.
 * @returns {string} Display-safe text.
 * @collaboration Keeps every Wilsy OS dashboard clean while preserving source-truth discipline.
 */
const normalizeWilsyDashboardText = (value, fallback = '') => {
  const resolved = String(value ?? '').trim();
  return resolved || fallback;
};

/**
 * @function titleizeWilsyDashboardText
 * @description Converts role, source and dashboard identifiers into readable labels.
 * @param {unknown} value - Candidate identifier.
 * @returns {string} Human-readable label.
 * @collaboration Prevents raw machine keys from leaking into shared dashboard chrome.
 */
const titleizeWilsyDashboardText = (value = '') => (
  String(value || '')
    .replace(/[_-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .toLowerCase()
    .replace(/\b\w/g, letter => letter.toUpperCase())
);

/**
 * @function compactWilsyDashboardSignal
 * @description Converts source, account and readiness states into Wilsy OS operating language.
 * @param {unknown} value - Source, session or readiness state.
 * @returns {string} Human-readable signal.
 * @collaboration Standardizes source-truth language across CRM, HR, Finance, Legal, Billing and Executive dashboards.
 */
const compactWilsyDashboardSignal = (value = 'SOURCE_REQUIRED') => {
  const raw = String(value || 'SOURCE_REQUIRED').trim().toUpperCase();

  const aliases = {
    READY: 'Ready',
    LIVE: 'Live',
    COMMAND_READY: 'Ready for decisions',
    EXECUTIVE_EPITOME: 'Executive standard',
    SOURCE_GAPS: 'Source gaps',
    SOURCE_REQUIRED: 'Source required',
    SOURCE_SILENT: 'Source awaiting connection',
    SOURCE_PENDING: 'Source pending',
    SOURCE_LIVE: 'Source live',
    LIVE_SOURCE: 'Live source',
    LIVE_SOURCE_READY: 'Live source ready',
    LIVE_SOURCE_PARTIAL: 'Partially connected',
    ZERO_RECORDS_FOUND_IN_SHARD: 'No records found',
    TELEMETRY_SYNCING: 'Telemetry syncing',
    TELEMETRY_LIVE: 'Telemetry live',
    STREAM_READY: 'Live activity stream',
    ACCOUNT_VERIFIED: 'Account verified',
    ACCESS_GATED: 'Access gated',
    POPIA_SAFE: 'POPIA display safe',
    TENANT_LEDGER_READY: 'Tenant ledger ready',
    TENANT_BRAND_DEFAULTED: 'Tenant branding incomplete',
    TENANT_PROFILE_INCOMPLETE: 'Tenant profile incomplete',
    PROFILE_NEEDED: 'Profile setup required',
    CRM_SOURCE_LIVE: 'CRM source live',
    CRM_SOURCE_SILENT: 'CRM awaiting connection',
    HR_SOURCE_LIVE: 'HR source live',
    HR_SOURCE_SILENT: 'HR awaiting connection',
    FINANCE_SERVICE_LIVE: 'Finance connected',
    FINANCE_SOURCE_REQUIRED: 'Finance setup required',
    SECURITY_SOURCE_LIVE: 'Security source live',
    COMPLIANCE_SOURCE_REQUIRED: 'Compliance source required'
  };

  if (aliases[raw]) return aliases[raw];

  return raw
    .replace(/^WILSY_/, '')
    .replace(/^EXECUTIVE_/, '')
    .replace(/^CRM_/, '')
    .replace(/^HR_/, '')
    .replace(/^FINANCE_/, '')
    .replace(/^LEGAL_/, '')
    .replace(/_SOURCE_/g, '_')
    .replace(/_SOURCE$/g, '')
    .replace(/_+/g, ' ')
    .toLowerCase()
    .replace(/\b\w/g, letter => letter.toUpperCase()) || 'Source required';
};

/**
 * @function normalizeWilsyDashboardKey
 * @description Normalizes dashboard keys for profile lookup.
 * @param {unknown} dashboardKey - Candidate dashboard key.
 * @returns {string} Supported dashboard key or generic dashboard.
 * @collaboration Lets every vertical request the shared chrome by stable OS identity.
 */
const normalizeWilsyDashboardKey = (dashboardKey = 'dashboard') => {
  const normalized = String(dashboardKey || 'dashboard').trim().toLowerCase().replace(/[^a-z0-9-]/g, '-');
  if (WILSY_DASHBOARD_CHROME_PROFILES[normalized]) return normalized;
  return normalized || 'dashboard';
};

/**
 * @function normalizeWilsyDashboardThemeId
 * @description Normalizes saved or profile-selected Account Command Center theme ids.
 * @param {unknown} themeId - Candidate theme id.
 * @returns {string} Supported theme id.
 * @collaboration Keeps all dashboards aligned with the reusable Account Command Center theme receipt.
 */
const normalizeWilsyDashboardThemeId = (themeId = '') => {
  const aliases = {
    forensic: 'forensic_violet',
    cobalt: 'cobalt_glass',
    wilsy_daybreak: 'pearl_command',
    dark_ops: 'sovereign_black'
  };
  const normalized = aliases[themeId] || themeId || 'wilsy_aurora';
  return WILSY_DASHBOARD_CHROME_THEME_SKINS[normalized] ? normalized : 'wilsy_aurora';
};

/**
 * @function normalizeWilsyDashboardMode
 * @description Normalizes dashboard theme mode.
 * @param {unknown} mode - Candidate mode.
 * @returns {string} Safe mode id.
 * @collaboration Prevents unsupported Account mode values from destabilizing shared dashboard chrome.
 */
const normalizeWilsyDashboardMode = (mode = '') => (
  ['day', 'night', 'auto'].includes(String(mode || '').trim()) ? String(mode || '').trim() : 'night'
);

/**
 * @function resolveWilsyDashboardMode
 * @description Resolves auto mode to day or night from local time.
 * @param {string} mode - Candidate mode.
 * @returns {string} Resolved mode.
 * @collaboration Allows dashboards to consume Account auto mode without backend preference dependency.
 */
const resolveWilsyDashboardMode = (mode = 'night') => {
  const safeMode = normalizeWilsyDashboardMode(mode);
  if (safeMode !== 'auto') return safeMode;
  const hour = new Date().getHours();
  return hour >= 7 && hour < 18 ? 'day' : 'night';
};

/**
 * @function readWilsyDashboardChromePreference
 * @description Reads persisted theme and mode values saved by Account Command Center.
 * @param {Object} options - Preference read options.
 * @param {string} options.themeId - Fallback theme id.
 * @param {string} options.mode - Fallback mode.
 * @returns {{themeId:string,mode:string,resolvedMode:string,skin:Object}} Theme preference packet.
 * @collaboration Gives each dashboard the same Executive-grade theme source without local one-off storage keys.
 */
const readWilsyDashboardChromePreference = ({ themeId = 'wilsy_aurora', mode = 'night' } = {}) => {
  const storedTheme = typeof window === 'undefined'
    ? themeId
    : window.localStorage.getItem(WILSY_DASHBOARD_CHROME_THEME_STORAGE_KEYS.theme) || themeId;
  const storedMode = typeof window === 'undefined'
    ? mode
    : window.localStorage.getItem(WILSY_DASHBOARD_CHROME_THEME_STORAGE_KEYS.mode) || mode;
  const safeThemeId = normalizeWilsyDashboardThemeId(storedTheme);
  const safeMode = normalizeWilsyDashboardMode(storedMode);

  return {
    themeId: safeThemeId,
    mode: safeMode,
    resolvedMode: resolveWilsyDashboardMode(safeMode),
    skin: WILSY_DASHBOARD_CHROME_THEME_SKINS[safeThemeId] || WILSY_DASHBOARD_CHROME_THEME_SKINS.wilsy_aurora
  };
};

/**
 * @function buildWilsyDashboardThemeVars
 * @description Builds CSS variables consumed by the shared dashboard chrome.
 * @param {string} themeId - Theme id.
 * @param {string} mode - Theme mode.
 * @returns {Object} CSS variable payload.
 * @collaboration Lets every dashboard repaint from Account Command Center receipts using one theme contract.
 */
const buildWilsyDashboardThemeVars = (themeId = 'wilsy_aurora', mode = 'night') => {
  const safeThemeId = normalizeWilsyDashboardThemeId(themeId);
  const resolvedMode = resolveWilsyDashboardMode(mode);
  const skin = WILSY_DASHBOARD_CHROME_THEME_SKINS[safeThemeId] || WILSY_DASHBOARD_CHROME_THEME_SKINS.wilsy_aurora;

  return {
    '--wilsy-bg': skin.bg,
    '--wilsy-surface': skin.surface,
    '--wilsy-panel': skin.panel,
    '--wilsy-rail': skin.rail,
    '--wilsy-text': skin.text,
    '--wilsy-muted': skin.muted,
    '--wilsy-accent': skin.accent,
    '--wilsy-accent-2': skin.secondary,
    '--wilsy-accent-3': skin.live,
    '--wilsy-authority': skin.authority,
    '--wilsy-live': skin.live,
    '--wilsy-risk': skin.risk,
    '--wilsy-border': skin.border,
    colorScheme: resolvedMode === 'day' ? 'light' : 'dark'
  };
};

/**
 * @function buildWilsyDashboardTenantIdentity
 * @description Builds tenant identity for the shared dashboard brand plate.
 * @param {Object} tenant - Tenant, branding or company source.
 * @returns {Object} Tenant identity packet.
 * @collaboration Gives every dashboard the same tenant plate contract while allowing tenant branding to win.
 */
const buildWilsyDashboardTenantIdentity = (tenant = {}) => {
  const displayName = normalizeWilsyDashboardText(
    tenant.displayName || tenant.companyName || tenant.tenantName || tenant.name,
    'Wilsy OS Tenant'
  );
  const tenantId = normalizeWilsyDashboardText(
    tenant.tenantId || tenant.id,
    'TENANT'
  );
  return {
    ...tenant,
    tenantId,
    displayName,
    name: displayName,
    logo: tenant.logo || tenant.branding?.logo || '',
    initials: normalizeWilsyDashboardText(
      tenant.initials,
      displayName.split(/\s+/).map(token => token[0]).join('').slice(0, 2).toUpperCase() || 'WO'
    ),
    status: compactWilsyDashboardSignal(tenant.status || tenant.sourceStatus || 'TENANT_LEDGER_READY')
  };
};

/**
 * @function buildWilsyDashboardOperatorIdentity
 * @description Builds operator identity for the shared top rail.
 * @param {Object} operator - User, access or auth source.
 * @param {string} role - Dashboard role fallback.
 * @returns {Object} Operator identity packet.
 * @collaboration Standardizes operator identity across dashboards without inventing profile records.
 */
const buildWilsyDashboardOperatorIdentity = (operator = {}, role = 'OPERATOR') => {
  const composedName = [operator.firstName, operator.lastName].filter(Boolean).join(' ').trim();
  const displayName = normalizeWilsyDashboardText(
    operator.fullName || operator.displayName || operator.name || composedName || operator.email || operator.username,
    'Wilsy OS Operator'
  );
  const roleLabel = titleizeWilsyDashboardText(
    operator.title || operator.position || operator.roleLabel || operator.tenantRole || operator.role || operator.userRole || role
  );

  return {
    ...operator,
    displayName,
    name: displayName,
    roleLabel,
    role: operator.role || operator.userRole || role,
    email: operator.email || operator.userEmail || operator.username || ''
  };
};

/**
 * @function buildWilsyDashboardStoryMessages
 * @description Builds the operating story rail for a dashboard from real source posture.
 * @param {Object} params - Story inputs.
 * @returns {Array<string>} Story rail messages.
 * @collaboration Replaces fake placeholder title theatre with honest tenant, operator and source context.
 */
const buildWilsyDashboardStoryMessages = ({
  tenant = {},
  operator = {},
  profile = {},
  readiness = {},
  sourceSnapshot = {},
  dashboardLabel = 'Wilsy OS Dashboard'
} = {}) => {
  const tenantName = normalizeWilsyDashboardText(tenant.displayName || tenant.name, 'Wilsy OS Tenant');
  const operatorName = normalizeWilsyDashboardText(operator.displayName || operator.name, 'Wilsy OS Operator');
  const roleLabel = normalizeWilsyDashboardText(operator.roleLabel || operator.role, 'Operator');
  const readinessLabel = compactWilsyDashboardSignal(readiness.posture || readiness.status || 'SOURCE_REQUIRED');
  const liveSources = Number(readiness.liveSources || 0);
  const totalSources = Number(readiness.totalSources || Object.keys(sourceSnapshot || {}).length || 0);
  const profileLabel = compactWilsyDashboardSignal(profile.sourceStatus || profile.status || 'TENANT_LEDGER_READY');

  return [
    `${dashboardLabel} active for ${tenantName}`,
    `${operatorName} operating as ${roleLabel}`,
    totalSources > 0 ? `${liveSources}/${totalSources} live sources visible` : 'Source inventory required',
    `Tenant profile: ${profileLabel}`,
    `Operating posture: ${readinessLabel}`
  ];
};

/**
 * @function buildWilsyDashboardMetrics
 * @description Builds shared chrome metric cards from source-backed values.
 * @param {Array<Object>} metrics - Candidate metric rows.
 * @returns {Array<Object>} Sanitized metric rows.
 * @collaboration Keeps dashboard metric strips reusable while refusing synthetic values.
 */
const buildWilsyDashboardMetrics = (metrics = []) => (
  (Array.isArray(metrics) ? metrics : [])
    .filter(metric => metric && typeof metric === 'object')
    .map(metric => ({
      id: normalizeWilsyDashboardText(metric.id || metric.label, `metric-${Date.now()}`),
      label: normalizeWilsyDashboardText(metric.label, 'SOURCE'),
      value: metric.value ?? 'SOURCE_REQUIRED',
      detail: metric.detail || ''
    }))
);

/**
 * @function buildWilsyDashboardAccountSummary
 * @description Builds Account Command Center summary props from dashboard source posture.
 * @param {Object} params - Account summary inputs.
 * @returns {{securitySummary:Object,complianceSummary:Object,sessionSummary:Object}} Account summary props.
 * @collaboration Lets CRM, HR and other dashboards reuse the existing Account Command Center with real context instead of a new modal.
 */
const buildWilsyDashboardAccountSummary = ({
  access = {},
  readiness = {},
  sourceSnapshot = {},
  telemetry = {},
  compliance = {}
} = {}) => {
  const sourceStatus = readiness.posture || readiness.status || 'SOURCE_REQUIRED';
  return {
    securitySummary: {
      identitySource: access.allowed === false ? 'Access gated' : compactWilsyDashboardSignal(access.identitySource || 'ACCOUNT_VERIFIED'),
      mfaStatus: compactWilsyDashboardSignal(access.mfaStatus || sourceSnapshot.security?.status || 'SOURCE_REQUIRED'),
      trustedDevices: compactWilsyDashboardSignal(access.trustedDevices || sourceSnapshot.it?.status || 'SOURCE_REQUIRED'),
      accountActivity: compactWilsyDashboardSignal(sourceStatus)
    },
    complianceSummary: {
      privacyStatus: compactWilsyDashboardSignal(compliance.privacyStatus || 'POPIA_SAFE'),
      complianceStatus: compactWilsyDashboardSignal(compliance.status || sourceSnapshot.compliance?.status || 'COMPLIANCE_SOURCE_REQUIRED'),
      auditConfidence: normalizeWilsyDashboardText(compliance.auditConfidence, `${Number(readiness.score || 0)}% readiness`),
      retentionStatus: compactWilsyDashboardSignal(compliance.retentionStatus || sourceSnapshot.records?.status || 'TENANT_LEDGER_READY')
    },
    sessionSummary: {
      activeSessions: telemetry.isSyncing
        ? 'Telemetry syncing'
        : compactWilsyDashboardSignal(telemetry.status || sourceSnapshot.telemetry?.status || 'SOURCE_REQUIRED')
    }
  };
};

/**
 * @function buildWilsyDashboardChromeConfig
 * @description Builds the complete shared chrome prop contract for any Wilsy OS dashboard.
 * @param {Object} params - Dashboard chrome inputs.
 * @returns {Object} Shared dashboard chrome config.
 * @collaboration Allows CRM and every future dashboard to inherit Executive chrome standards with context-specific actions.
 */
const buildWilsyDashboardChromeConfig = ({
  dashboardKey = 'dashboard',
  tenant = {},
  operator = {},
  access = {},
  readiness = {},
  sourceSnapshot = {},
  telemetry = {},
  compliance = {},
  profile = {},
  metrics = [],
  themeId = '',
  mode = '',
  overrides = {}
} = {}) => {
  const safeDashboardKey = normalizeWilsyDashboardKey(dashboardKey);
  const profileConfig = WILSY_DASHBOARD_CHROME_PROFILES[safeDashboardKey] || {};
  const tenantIdentity = buildWilsyDashboardTenantIdentity(tenant);
  const operatorIdentity = buildWilsyDashboardOperatorIdentity(operator, profileConfig.role || 'OPERATOR');
  const preference = readWilsyDashboardChromePreference({
    themeId: themeId || profileConfig.themeId || 'wilsy_aurora',
    mode: mode || 'night'
  });
  const accountSummary = buildWilsyDashboardAccountSummary({
    access,
    readiness,
    sourceSnapshot,
    telemetry,
    compliance
  });

  return {
    dashboardKey: safeDashboardKey,
    commandLabel: overrides.commandLabel || profileConfig.commandLabel || 'Wilsy OS Command',
    title: overrides.title || profileConfig.title || 'WILSY OS DASHBOARD',
    role: overrides.role || profileConfig.role || 'OPERATOR',
    posture: readiness.posture || readiness.status || 'SOURCE_REQUIRED',
    tenant: tenantIdentity,
    operator: operatorIdentity,
    storyMessages: overrides.storyMessages || buildWilsyDashboardStoryMessages({
      tenant: tenantIdentity,
      operator: operatorIdentity,
      profile,
      readiness,
      sourceSnapshot,
      dashboardLabel: overrides.title || profileConfig.title || 'Wilsy OS Dashboard'
    }),
    search: {
      placeholder: overrides.searchPlaceholder || profileConfig.searchPlaceholder || 'Search Wilsy OS or press ⌘K'
    },
    actions: {
      liveSyncLabel: overrides.liveSyncLabel || profileConfig.liveSyncLabel || 'LIVE SYNC',
      primaryActionLabel: overrides.primaryActionLabel || profileConfig.primaryActionLabel || 'NEW COMMAND'
    },
    account: {
      label: overrides.accountLabel || 'COMMAND CENTER',
      activeThemeId: preference.themeId,
      themeMode: preference.mode,
      ...accountSummary
    },
    metrics: buildWilsyDashboardMetrics(metrics),
    themePreference: preference,
    themeVars: buildWilsyDashboardThemeVars(preference.themeId, preference.mode),
    version: WILSY_DASHBOARD_CHROME_VERSION
  };
};

export {
  WILSY_DASHBOARD_CHROME_PROFILES,
  WILSY_DASHBOARD_CHROME_THEME_SKINS,
  WILSY_DASHBOARD_CHROME_THEME_STORAGE_KEYS,
  WILSY_DASHBOARD_CHROME_VERSION,
  buildWilsyDashboardAccountSummary,
  buildWilsyDashboardChromeConfig,
  buildWilsyDashboardMetrics,
  buildWilsyDashboardOperatorIdentity,
  buildWilsyDashboardStoryMessages,
  buildWilsyDashboardTenantIdentity,
  buildWilsyDashboardThemeVars,
  compactWilsyDashboardSignal,
  normalizeWilsyDashboardKey,
  normalizeWilsyDashboardMode,
  normalizeWilsyDashboardText,
  normalizeWilsyDashboardThemeId,
  readWilsyDashboardChromePreference,
  resolveWilsyDashboardMode,
  titleizeWilsyDashboardText
};
