/**
 * WILSY OS — CRM EXECUTIVE DNA SERVICE
 * VERSION: 1.0.1-STANDALONE-OS-SHARD
 *
 * @fileoverview Executive Dashboard DNA helpers for standalone CRM OS shard.
 */

export const CRM_EXECUTIVE_DNA_VERSION = '1.0.1-STANDALONE-OS-SHARD';
export const CRM_EXECUTIVE_TRUTH_POLICY = 'NO_FAKE_VERIFIED';

export const CRM_ALL_EXECUTIVE_MODULES = Object.freeze([
  'leads',
  'contacts',
  'accounts',
  'deals',
  'tasks',
  'meetings',
  'calls',
  'campaigns',
  'documents',
  'visits',
  'projects',
  'quotes',
  'invoices',
  'cases',
  'tickets',
  'contracts',
  'authorities',
  'risks',
  'opportunities',
  'suppliers',
  'partners'
]);

const ROLE_MATRIX = Object.freeze({
  FOUNDER: {
    label: 'Founder CRM Command',
    allowedModules: CRM_ALL_EXECUTIVE_MODULES,
    canCreate: true,
    canEdit: true,
    canDelete: true,
    canImport: true,
    canExport: true,
    canFounderReturn: true
  },
  SUPER_ADMIN: {
    label: 'Super Admin CRM Command',
    allowedModules: CRM_ALL_EXECUTIVE_MODULES,
    canCreate: true,
    canEdit: true,
    canDelete: true,
    canImport: true,
    canExport: true,
    canFounderReturn: true
  },
  TENANT_OWNER: {
    label: 'Tenant Owner CRM Command',
    allowedModules: CRM_ALL_EXECUTIVE_MODULES,
    canCreate: true,
    canEdit: true,
    canDelete: true,
    canImport: true,
    canExport: true,
    canFounderReturn: false
  },
  TENANT_ADMIN: {
    label: 'Tenant Admin CRM Command',
    allowedModules: CRM_ALL_EXECUTIVE_MODULES,
    canCreate: true,
    canEdit: true,
    canDelete: true,
    canImport: true,
    canExport: true,
    canFounderReturn: false
  },
  TENANT_DISCOVERY: {
    label: 'Tenant Discovery CRM',
    allowedModules: ['leads', 'contacts', 'accounts', 'visits', 'meetings', 'calls', 'documents'],
    canCreate: true,
    canEdit: true,
    canDelete: false,
    canImport: true,
    canExport: true,
    canFounderReturn: false
  },
  SDR: {
    label: 'SDR Prospecting Command',
    allowedModules: ['leads', 'contacts', 'tasks', 'meetings', 'calls', 'campaigns'],
    canCreate: true,
    canEdit: true,
    canDelete: false,
    canImport: true,
    canExport: true,
    canFounderReturn: false
  },
  SALES_CONSULTANT: {
    label: 'Sales Consultant Command',
    allowedModules: [
      'leads',
      'contacts',
      'accounts',
      'deals',
      'tasks',
      'meetings',
      'calls',
      'campaigns',
      'documents',
      'visits',
      'projects',
      'quotes',
      'contracts',
      'opportunities'
    ],
    canCreate: true,
    canEdit: true,
    canDelete: false,
    canImport: true,
    canExport: true,
    canFounderReturn: false
  },
  SALES_MANAGER: {
    label: 'Sales Manager Command',
    allowedModules: [
      'leads',
      'contacts',
      'accounts',
      'deals',
      'tasks',
      'meetings',
      'calls',
      'campaigns',
      'documents',
      'visits',
      'projects',
      'quotes',
      'contracts',
      'opportunities',
      'risks'
    ],
    canCreate: true,
    canEdit: true,
    canDelete: true,
    canImport: true,
    canExport: true,
    canFounderReturn: false
  },
  CUSTOMER_SUCCESS_MANAGER: {
    label: 'Customer Success Command',
    allowedModules: [
      'contacts',
      'accounts',
      'tasks',
      'meetings',
      'calls',
      'documents',
      'visits',
      'projects',
      'cases',
      'tickets',
      'contracts',
      'risks'
    ],
    canCreate: true,
    canEdit: true,
    canDelete: false,
    canImport: true,
    canExport: true,
    canFounderReturn: false
  },
  CUSTOMER_SUCCESS: {
    label: 'Customer Success Command',
    allowedModules: [
      'contacts',
      'accounts',
      'tasks',
      'meetings',
      'calls',
      'documents',
      'visits',
      'projects',
      'cases',
      'tickets'
    ],
    canCreate: true,
    canEdit: true,
    canDelete: false,
    canImport: false,
    canExport: true,
    canFounderReturn: false
  },
  FINANCE: {
    label: 'Finance CRM Command',
    allowedModules: ['accounts', 'deals', 'quotes', 'invoices', 'contracts', 'documents'],
    canCreate: true,
    canEdit: true,
    canDelete: false,
    canImport: true,
    canExport: true,
    canFounderReturn: false
  },
  GENERAL: {
    label: 'CRM Operator',
    allowedModules: ['leads', 'contacts', 'accounts', 'tasks', 'meetings', 'calls', 'documents'],
    canCreate: true,
    canEdit: true,
    canDelete: false,
    canImport: false,
    canExport: true,
    canFounderReturn: false
  }
});

/**
 * @function safeText
 * @description Returns the first non-empty text value.
 * @param {...*} values - Candidate values.
 * @returns {string} First usable text.
 * @collaboration Keeps CRM executive identity stable across tenant/profile shapes.
 */
export function safeText(...values) {
  const value = values.find((candidate) => candidate !== undefined && candidate !== null && String(candidate).trim() !== '');
  return value === undefined ? '' : String(value).trim();
}

/**
 * @function normalizeCrmExecutiveToken
 * @description Normalizes role and dashboard tokens.
 * @param {*} value - Raw token.
 * @returns {string} Normalized token.
 * @collaboration Mirrors Executive Dashboard role resolver behavior for CRM.
 */
export function normalizeCrmExecutiveToken(value = '') {
  return String(value || '')
    .trim()
    .replace(/([a-z])([A-Z])/g, '$1_$2')
    .replace(/[\s./:-]+/g, '_')
    .replace(/_+/g, '_')
    .toUpperCase();
}

/**
 * @function collectCrmExecutiveSignals
 * @description Collects CRM role signals from user and active tenant metadata.
 * @param {object} params - Resolver params.
 * @returns {Array<string>} Ordered role tokens.
 * @collaboration Lets Tenant Discovery, SDR, Sales Consultant and CSM roles resolve CRM access.
 */
export function collectCrmExecutiveSignals({ user = {}, activeTenant = {} } = {}) {
  return [
    user.role,
    user.accountRole,
    user.tenantRole,
    user.crmRole,
    user.salesRole,
    user.dashboardRole,
    user.roleView,
    user.profile?.role,
    user.profile?.crmRole,
    user.profile?.salesRole,
    user.preferences?.crmRole,
    user.sovereignProfile?.crmRole,
    activeTenant?.role,
    activeTenant?.tenantRole,
    activeTenant?.crmRole,
    activeTenant?.salesRole,
    activeTenant?.dashboardRole,
    activeTenant?.profile?.crmRole,
    activeTenant?.profile?.salesRole,
    activeTenant?.profile?.dashboardRole,
    activeTenant?.discovery?.role,
    activeTenant?.sales?.role,
    activeTenant?.customerSuccess?.role,
    ...(Array.isArray(user.roles) ? user.roles : []),
    ...(Array.isArray(user.permissions) ? user.permissions : []),
    ...(Array.isArray(user.scopes) ? user.scopes : [])
  ].map(normalizeCrmExecutiveToken).filter(Boolean);
}

/**
 * @function resolveCrmExecutiveAccess
 * @description Resolves CRM module/action access from user and tenant role signals.
 * @param {object} params - Resolver params.
 * @returns {object} CRM executive access contract.
 * @collaboration Gives CRM the same role-first access principle as Executive Dashboard.
 */
export function resolveCrmExecutiveAccess({ user = {}, activeTenant = {} } = {}) {
  const signals = collectCrmExecutiveSignals({ user, activeTenant });

  let roleToken = signals.find((token) => ['FOUNDER', 'CEO', 'ROOT', 'SOVEREIGN', 'GLOBAL_ROOT'].includes(token)) ? 'FOUNDER' : '';
  roleToken = roleToken || signals.find((token) => ROLE_MATRIX[token]) || '';

  if (!roleToken && signals.some((token) => ['SUPERADMIN', 'SUPER_ADMIN'].includes(token))) roleToken = 'SUPER_ADMIN';
  if (!roleToken && signals.some((token) => ['TENANTOWNER', 'TENANT_OWNER', 'OWNER'].includes(token))) roleToken = 'TENANT_OWNER';
  if (!roleToken && signals.some((token) => ['TENANTADMIN', 'TENANT_ADMIN', 'ADMIN'].includes(token))) roleToken = 'TENANT_ADMIN';
  if (!roleToken && signals.some((token) => ['CUSTOMER_SUCCESS', 'CSM'].includes(token))) roleToken = 'CUSTOMER_SUCCESS_MANAGER';
  if (!roleToken && signals.some((token) => ['SALES', 'SALES_REP', 'SALES_REPRESENTATIVE'].includes(token))) roleToken = 'SALES_CONSULTANT';
  if (!roleToken && signals.some((token) => ['DISCOVERY', 'TENANT_DISCOVERY_REP'].includes(token))) roleToken = 'TENANT_DISCOVERY';

  roleToken = roleToken || 'GENERAL';

  const matrix = ROLE_MATRIX[roleToken] || ROLE_MATRIX.GENERAL;

  return {
    roleToken,
    roleLabel: matrix.label,
    allowedModules: matrix.allowedModules,
    canCreate: matrix.canCreate,
    canEdit: matrix.canEdit,
    canDelete: matrix.canDelete,
    canImport: matrix.canImport,
    canExport: matrix.canExport,
    canFounderReturn: matrix.canFounderReturn,
    truthPolicy: CRM_EXECUTIVE_TRUTH_POLICY
  };
}

/**
 * @function filterCrmExecutiveTabs
 * @description Filters CRM tab definitions by resolved access.
 * @param {Array<object>} tabs - CRM tabs.
 * @param {Array<string>} allowedModules - Allowed module ids.
 * @returns {Array<object>} Visible tabs.
 * @collaboration Prevents tenant roles from seeing CRM modules outside their remit.
 */
export function filterCrmExecutiveTabs(tabs = [], allowedModules = []) {
  return tabs.filter((tab) => allowedModules.includes(tab.id));
}

/**
 * @function resolveCrmExecutiveTheme
 * @description Builds CRM theme runtime variables from tenant branding.
 * @param {object} params - Theme params.
 * @returns {object} Theme runtime.
 * @collaboration Gives CRM the same tenant-brand DNA as Executive Dashboard.
 */
export function resolveCrmExecutiveTheme({ activeTenant = {}, user = {} } = {}) {
  const branding = activeTenant?.branding || activeTenant?.theme || {};
  const primary = safeText(branding.primaryColor, branding.primary, activeTenant?.primaryColor, '#D4AF37');
  const secondary = safeText(branding.secondaryColor, branding.secondary, activeTenant?.secondaryColor, '#0EA5E9');
  const accent = safeText(branding.accentColor, branding.accent, activeTenant?.accentColor, '#93C5FD');

  return {
    companyName: safeText(branding.companyName, activeTenant?.companyName, activeTenant?.name, activeTenant?.legalName, user?.tenantName, 'Wilsy OS Root'),
    primary,
    secondary,
    accent,
    cssVars: {
      '--wilsy-crm-primary': primary,
      '--wilsy-crm-secondary': secondary,
      '--wilsy-crm-accent': accent,
      '--wilsy-crm-primary-glow': `${primary}44`,
      '--wilsy-crm-secondary-glow': `${secondary}33`
    }
  };
}

/**
 * @function buildCrmExecutiveIdentity
 * @description Builds tenant/operator identity data for the standalone CRM header.
 * @param {object} params - Identity params.
 * @returns {object} Tenant identity.
 * @collaboration Recreates Executive Dashboard tenant identity pattern for CRM.
 */
export function buildCrmExecutiveIdentity({ activeTenant = {}, user = {}, tenantId = '' } = {}) {
  const companyName = safeText(activeTenant?.branding?.companyName, activeTenant?.companyName, activeTenant?.name, activeTenant?.legalName, 'Wilsy OS Root');
  const initials = companyName.split(/\s+/).filter(Boolean).slice(0, 2).map((part) => part[0]).join('').toUpperCase() || 'WO';

  return {
    tenantId,
    initials,
    companyName,
    operatorName: safeText(user?.name, user?.fullName, user?.email, 'Wilson Khanyezi'),
    operatorRole: safeText(user?.role, user?.accountRole, user?.tenantRole, 'Super Admin'),
    sector: safeText(activeTenant?.industry, activeTenant?.sector, activeTenant?.profile?.industry, 'Technology, SaaS and Digital Command'),
    brandStatus: 'OPERATING BRAND VERIFIED',
    truthPolicy: CRM_EXECUTIVE_TRUTH_POLICY
  };
}

/**
 * @function buildCrmFloatingExecutiveActions
 * @description Builds Executive-style floating actions for CRM.
 * @param {object} params - Action params.
 * @returns {Array<object>} Floating actions.
 * @collaboration Transfers Executive Dashboard floating command principles into CRM.
 */
export function buildCrmFloatingExecutiveActions({
  canFounderReturn = false,
  canCreate = false,
  canImport = false,
  canExport = false,
  activeTab = 'leads'
} = {}) {
  const actions = [
    { id: 'sync', label: 'Live Sync', intent: 'SYNC', enabled: true },
    { id: 'create', label: `New ${activeTab.replace(/s$/, '')}`, intent: 'CREATE', enabled: canCreate },
    { id: 'import', label: 'Import', intent: 'IMPORT', enabled: canImport },
    { id: 'export', label: 'Export', intent: 'EXPORT', enabled: canExport }
  ];

  if (canFounderReturn) actions.unshift({ id: 'founder', label: 'Founder', intent: 'FOUNDER_RETURN', enabled: true });

  return actions.filter((action) => action.enabled);
}
