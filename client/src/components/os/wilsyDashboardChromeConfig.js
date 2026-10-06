/* eslint-disable */
/**
 * TITLE: WILSY OS Shared Dashboard Chrome Identity + Branding Resolver
 * VERSION: v2.0.0-D21B9-AUTHENTICATED-BRANDING-PRESENTATION
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Resolve descriptive tenant/operator chrome identity while accepting
 *          tenant branding only from the authenticated D21B8 tenant projection.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/os/wilsyDashboardChromeConfig.js
 * COLLABORATION / OWNERSHIP: D21B8 AuthContext owns browser admission of the
 *                            D21B7 workspace branding projection; shared chrome
 *                            owns presentation only. Individual dashboards may
 *                            provide descriptive tenant/operator labels but may
 *                            not introduce branding authority.
 * CERTIFICATION / UPDATE DATE: 2026-09-25
 * CHANGELOG: v2.0.0-D21B9-AUTHENTICATED-BRANDING-PRESENTATION removes legacy
 *            logo/logoUrl path authority from shared chrome and projects only
 *            the already-bounded authenticatedTenant.branding object. Approved
 *            colours and labels may style presentation; logo/favicon remain
 *            opaque descriptors until a separately certified authenticated
 *            asset-serving route exists. WILSY OS remains the permanent trust
 *            mark and no tenant branding can replace it.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: No raw URL/path/base64/bytes are accepted as
 *                             tenant branding. Browser-local/discovery/legacy
 *                             branding fields are ignored.
 * TENANT BOUNDARY: Authenticated branding tenantId must equal the authenticated
 *                  tenant identity. Foreign/malformed branding is suppressed.
 * AUTHORITY BOUNDARY: Presentation only; no authentication, membership, IAM,
 *                     legal-command, billing, upload or asset-resolution truth.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns execution.
 */

const VERSION = 'v2.0.0-D21B9-AUTHENTICATED-BRANDING-PRESENTATION';

function firstNonEmpty(...candidates) {
  for (const candidate of candidates) {
    if (candidate == null) continue;
    const value = String(candidate).trim();
    if (value) return value;
  }
  return '';
}

function exactOptionalColor(value) {
  if (value == null) return null;
  return typeof value === 'string' && /^#[0-9A-F]{6}$/.test(value)
    ? value
    : null;
}

function boundedAuthenticatedBranding(authenticatedTenant) {
  if (!authenticatedTenant || typeof authenticatedTenant !== 'object') return null;
  const tenantId = firstNonEmpty(authenticatedTenant.tenantId);
  const branding = authenticatedTenant.branding;
  if (!tenantId || branding == null) return null;
  if (!branding || typeof branding !== 'object' || Array.isArray(branding)) return null;
  if (
    branding.tenantId !== tenantId
    || branding.platformTrustMarkRequired !== true
    || typeof branding.profileId !== 'string'
    || !branding.profileId
    || typeof branding.profileLabel !== 'string'
    || !branding.profileLabel
    || typeof branding.brandingTier !== 'string'
    || !branding.brandingTier
  ) {
    return null;
  }

  const logo = branding.logo && typeof branding.logo === 'object'
    ? {
        reference: branding.logo.reference,
        contentFingerprint: branding.logo.contentFingerprint,
        mediaType: branding.logo.mediaType,
        kind: branding.logo.kind,
      }
    : null;
  const favicon = branding.favicon && typeof branding.favicon === 'object'
    ? {
        reference: branding.favicon.reference,
        contentFingerprint: branding.favicon.contentFingerprint,
        mediaType: branding.favicon.mediaType,
        kind: branding.favicon.kind,
      }
    : null;

  return {
    tenantId,
    profileId: branding.profileId,
    profileLabel: branding.profileLabel,
    brandingTier: branding.brandingTier,
    primaryColor: exactOptionalColor(branding.primaryColor),
    secondaryColor: exactOptionalColor(branding.secondaryColor),
    accentColor: exactOptionalColor(branding.accentColor),
    emailDisplayName:
      typeof branding.emailDisplayName === 'string' && branding.emailDisplayName
        ? branding.emailDisplayName
        : null,
    platformTrustMarkRequired: true,
    logo,
    favicon,
  };
}

/**
 * Resolve descriptive tenant/operator identity plus authenticated branding.
 *
 * Explicit tenant/operator props may control descriptive labels only. Branding
 * is consumed solely from authenticatedTenant.branding, which D21B8 admitted
 * from the READY Python EOS workspace-bootstrap response.
 */
export function resolveWilsyChromeIdentitySources({
  tenant = {},
  operator = {},
  authUser = {},
  activeTenant = {},
  authenticatedTenant = {},
  dashboard = {},
  storyMessages = []
} = {}) {
  const explicitTenant = tenant && typeof tenant === 'object' ? tenant : {};
  const contextTenant = activeTenant && typeof activeTenant === 'object' ? activeTenant : {};
  const authTenant = authenticatedTenant && typeof authenticatedTenant === 'object'
    ? authenticatedTenant
    : {};

  const displayName = firstNonEmpty(
    explicitTenant.name,
    explicitTenant.displayName,
    explicitTenant.companyName,
    explicitTenant.tenantName,
    explicitTenant.legalName,
    explicitTenant.code,
    explicitTenant.tenantId,
    explicitTenant.id,
    authTenant.name,
    authTenant.displayName,
    authTenant.companyName,
    authTenant.tenantName,
    authTenant.legalName,
    authTenant.code,
    authTenant.tenantId,
    authTenant.id,
    contextTenant.name,
    contextTenant.displayName,
    contextTenant.companyName,
    contextTenant.tenantName,
    contextTenant.legalName,
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
      .map((word) => word[0]?.toUpperCase() || '')
      .join('') || 'WR';

  const explicitOp = operator && typeof operator === 'object' ? operator : {};
  const contextOp = authUser && typeof authUser === 'object' ? authUser : {};
  const operatorName = firstNonEmpty(
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
  const roleLabel = firstNonEmpty(
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
      authTenant.tenantId,
      authTenant.id,
      authTenant.code,
      contextTenant.tenantId,
      contextTenant.id,
      contextTenant.code
    ) || null;

  const authenticatedBranding = boundedAuthenticatedBranding(authTenant);
  const branding =
    authenticatedBranding && authenticatedBranding.tenantId === authTenant.tenantId
      ? authenticatedBranding
      : null;

  const status = firstNonEmpty(
    explicitTenant.billingStatus,
    explicitTenant.status,
    authTenant.billingStatus,
    authTenant.status,
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
      tenantId,
      status,
      branding,
      // D21B9 deliberately exposes no renderable tenant logo URL.
      logo: null,
      brandingProfileLabel: branding?.profileLabel || null,
      primaryColor: branding?.primaryColor || null,
      secondaryColor: branding?.secondaryColor || null,
      accentColor: branding?.accentColor || null,
      platformTrustMarkRequired: branding?.platformTrustMarkRequired === true,
    },
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

export { VERSION };

export default { resolveWilsyChromeIdentitySources };


// ARTIFACT: wilsyDashboardChromeConfig.js
// VERSION: v2.0.0-D21B9-AUTHENTICATED-BRANDING-PRESENTATION
// AUTHORITY BOUNDARY: presentation only; branding accepted solely from D21B8 authenticatedTenant.branding
// TENANT POSTURE: branding tenant must exactly match authenticated tenant; legacy/raw logo paths are ignored
// FAIL-CLOSED POSTURE: malformed/foreign branding suppresses tenant branding rather than inventing fallback authority
// FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
