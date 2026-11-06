/**
 * TITLE: WILSY OS tenant module manifest contract
 * VERSION: v1.0.0-EOS-TENANT-MODULE-MANIFEST-CLIENT
 * AUTHORITY: Browser validation of the authenticated server-issued module projection.
 * PURPOSE: Bind module identity, product identity, workspace route and entitlement
 *          evidence to one exact tenant without creating any client authorization.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/utils/tenantModuleManifest.js
 * COLLABORATION / OWNERSHIP: EOS auth module manifest owns the response; client consumes presentation metadata only.
 * CERTIFICATION / UPDATE DATE: 2026-11-06
 * CHANGELOG: v1.0.0 establishes strict tenant-bound response validation and a closed module-to-product mapping.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: No local entitlement inference, browser-supplied role, route grant or permission expansion.
 * TENANT BOUNDARY: Exact authenticated tenant match is mandatory.
 * FINANCIAL AUTHORITY BOUNDARY: No pricing, payment, execution or settlement authority.
 */

export const MODULE_MANIFEST_VERSION = 'v1.0.0-EOS-TENANT-MODULE-MANIFEST';

export const MODULE_PRESENTATION = Object.freeze({
  LEGAL_OS: Object.freeze({
    productId: 'LEGAL_OPERATIONS',
    label: 'Legal OS',
    workspaceKey: 'LEGAL_DASHBOARD',
    navigationGroup: 'PROFESSIONAL_SERVICES',
    iconKey: 'scale',
  }),
  BILLING: Object.freeze({
    productId: 'BILLING',
    label: 'Billing',
    workspaceKey: 'BILLING_HUB',
    navigationGroup: 'BUSINESS_OPERATIONS',
    iconKey: 'receipt',
  }),
  CRM: Object.freeze({
    productId: 'CRM',
    label: 'CRM',
    workspaceKey: 'CRM_DASHBOARD',
    navigationGroup: 'CUSTOMER_OPERATIONS',
    iconKey: 'users',
  }),
  PEOPLE: Object.freeze({
    productId: 'HR',
    label: 'People',
    workspaceKey: 'HR_DASHBOARD',
    navigationGroup: 'PEOPLE_OPERATIONS',
    iconKey: 'users-round',
  }),
});

/**
 * Admit only the exact READY server-issued module projection for the active tenant.
 * This validates presentation metadata only; destinations and APIs independently authorize.
 */
export const validateWilsyModuleManifest = (payload, expectedTenantId) => {
  const workspace = payload?.workspace;
  if (
    payload?.status !== 'READY'
    || typeof expectedTenantId !== 'string'
    || !expectedTenantId
    || workspace?.tenantId !== expectedTenantId
    || workspace?.moduleManifestVersion !== MODULE_MANIFEST_VERSION
    || !Array.isArray(workspace.modules)
    || workspace.modules.length > Object.keys(MODULE_PRESENTATION).length
  ) {
    throw new Error('MODULE_MANIFEST_RESPONSE_INVALID');
  }

  const seen = new Set();
  return workspace.modules.map((module) => {
    const canonical = MODULE_PRESENTATION[module?.moduleId];
    const fields = [
      'moduleId',
      'productId',
      'label',
      'workspaceKey',
      'navigationGroup',
      'iconKey',
      'entitlementId',
      'entitlementRevision',
      'entitlementFingerprint',
    ];
    if (
      !canonical
      || seen.has(module.moduleId)
      || fields.some((field) => !Object.prototype.hasOwnProperty.call(module, field))
      || fields.length !== Object.keys(module).length
      || module.productId !== canonical.productId
      || module.label !== canonical.label
      || module.workspaceKey !== canonical.workspaceKey
      || module.navigationGroup !== canonical.navigationGroup
      || module.iconKey !== canonical.iconKey
      || typeof module.entitlementId !== 'string'
      || !module.entitlementId
      || !Number.isInteger(module.entitlementRevision)
      || module.entitlementRevision < 0
      || typeof module.entitlementFingerprint !== 'string'
      || !/^[0-9a-f]{128}$/.test(module.entitlementFingerprint)
    ) {
      throw new Error('MODULE_MANIFEST_ENTRY_INVALID');
    }
    seen.add(module.moduleId);
    return Object.freeze({ ...module });
  });
};

// ARTIFACT: tenantModuleManifest.js
// VERSION: v1.0.0-EOS-TENANT-MODULE-MANIFEST-CLIENT
// AUTHORITY BOUNDARY: presentation validation only; no IAM or route admission
// TENANT POSTURE: exact authenticated tenant match required
// FAIL-CLOSED POSTURE: unknown, duplicate, malformed, foreign or forged entries reject
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
// END OF WILSY OS SOVEREIGN ARTIFACT
