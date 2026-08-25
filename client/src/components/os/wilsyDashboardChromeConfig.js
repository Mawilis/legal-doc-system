/* eslint-disable */
/**
 * =============================================================================
 * Wilsy OS — Dashboard Chrome Identity Resolver
 * =============================================================================
 * File:           client/src/components/os/wilsyDashboardChromeConfig.js
 * Version:        v1.2.0-EXPLICIT-TENANT-PRIORITY
 * Authority:      Wilsy OS Core Governance
 * Epitome:        Explicit tenant/operator props win over context fallbacks so
 *                 chrome tests and live dashboards show the correct brand.
 * Classification: Production Artifact
 *
 * Change Log:
 *   2026-08-05 v1.2.0-EXPLICIT-TENANT-PRIORITY — Prefer `tenant` / `operator`
 *     props over activeTenant / authUser when resolving display names.
 * =============================================================================
 */

/**
 * @function firstNonEmpty
 * @description First non-empty string among candidates.
 */
function firstNonEmpty(...candidates) {
  for (const c of candidates) {
    if (c == null) continue;
    const s = String(c).trim();
    if (s) return s;
  }
  return '';
}

/**
 * @function resolveWilsyChromeIdentitySources
 * @description Resolves tenant + operator identity for shared OS chrome.
 *              Explicit `tenant` / `operator` props always beat context values.
 * @param {object} params
 * @returns {{ tenant: object, operator: object, storyMessages: string[], tenantName: string }}
 * @collaboration BillingHUD, HR, CRM, Founder chrome, WilsyOSDashboardChrome tests.
 */
export function resolveWilsyChromeIdentitySources({
  tenant = {},
  operator = {},
  authUser = {},
  activeTenant = {},
  dashboard = {},
  storyMessages = []
} = {}) {
  const explicitTenant = tenant && typeof tenant === 'object' ? tenant : {};
  const contextTenant = activeTenant && typeof activeTenant === 'object' ? activeTenant : {};

  // Explicit prop fields first (test: Acme Legal over Wilsy Tenant from context)
  const displayName =
    firstNonEmpty(
      explicitTenant.name,
      explicitTenant.displayName,
      explicitTenant.companyName,
      explicitTenant.tenantName,
      explicitTenant.legalName,
      explicitTenant.brandName,
      explicitTenant.code,
      explicitTenant.tenantId,
      explicitTenant.id,
      contextTenant.name,
      contextTenant.displayName,
      contextTenant.companyName,
      contextTenant.tenantName,
      contextTenant.legalName,
      contextTenant.brandName,
      contextTenant.code,
      contextTenant.tenantId,
      contextTenant.id,
      'Wilsy OS Root'
    );

  const initials =
    String(displayName)
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((w) => w[0]?.toUpperCase() || '')
      .join('') || 'WR';

  const explicitOp = operator && typeof operator === 'object' ? operator : {};
  const contextOp = authUser && typeof authUser === 'object' ? authUser : {};

  const operatorName =
    firstNonEmpty(
      explicitOp.displayName,
      explicitOp.name,
      [explicitOp.firstName, explicitOp.lastName].filter(Boolean).join(' '),
      explicitOp.email,
      contextOp.displayName,
      contextOp.name,
      [contextOp.firstName, contextOp.lastName].filter(Boolean).join(' '),
      contextOp.email,
      'Operator'
    );

  const roleLabel =
    firstNonEmpty(
      explicitOp.roleLabel,
      explicitOp.role,
      contextOp.roleLabel,
      contextOp.role,
      dashboard.role,
      'OPERATOR'
    );

  const tenantId =
    firstNonEmpty(
      explicitTenant.tenantId,
      explicitTenant.id,
      explicitTenant.code,
      contextTenant.tenantId,
      contextTenant.id,
      contextTenant.code
    ) || null;

  const logo =
    explicitTenant.logoUrl ||
    explicitTenant.logo ||
    contextTenant.logoUrl ||
    contextTenant.logo ||
    null;

  const status =
    firstNonEmpty(
      explicitTenant.billingStatus,
      explicitTenant.status,
      contextTenant.billingStatus,
      contextTenant.status,
      'OPERATING BRAND VERIFIED'
    );

  const defaultStory = [
    `Dashboard ${dashboard.dashboardKey || 'command'}`,
    `Posture ${dashboard.posture || 'SOURCE_REQUIRED'}`,
    `Tenant ${displayName}`
  ];

  return {
    tenant: {
      displayName,
      tenantName: displayName,
      name: displayName,
      initials,
      logo,
      status,
      tenantId
    },
    // Flat aliases used by some chrome consumers / tests
    tenantName: displayName,
    tenantDisplayName: displayName,
    operator: {
      displayName: operatorName,
      roleLabel: String(roleLabel).replace(/_/g, ' '),
      email: firstNonEmpty(explicitOp.email, contextOp.email)
    },
    storyMessages:
      Array.isArray(storyMessages) && storyMessages.length ? storyMessages : defaultStory
  };
}

export default { resolveWilsyChromeIdentitySources };
