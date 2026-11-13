/**
 * TITLE: WILSY OS Sovereign Tenant Context
 * VERSION: v6.5.0-GOVERNED-C2-TENANT-DIRECTORY-DENY
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Projects the exact server-certified authenticated workspace tenant
 *          into browser context without demanding a second, independently
 *          privileged tenant-profile read after MFA.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/contexts/tenantContext.jsx
 * COLLABORATION / OWNERSHIP: Browser projection only. AuthProvider supplies the
 *                            Python EOS workspace-bootstrap projection; TenantProvider
 *                            owns bounded client hydration and same-tenant UI state.
 * CERTIFICATION / UPDATE DATE: 2026-09-24
 * CHANGELOG:
 *   v6.5.0-GOVERNED-C2-TENANT-DIRECTORY-DENY — Keeps only the exact authenticated
 *     workspace tenant in browser context; refresh and alias resolution cannot
 *     enumerate or fetch arbitrary tenants while global directory authority is
 *     outside governed Python EOS C2.
 *   v6.4.0-SUBSCRIPTION-LIFECYCLE-AUTHORITY-BOUNDARY — Stops loading restricted billing dunning
 *     projections in global post-MFA tenant hydration. Dunning evidence is
 *     not subscription lifecycle or entitlement truth. Until a separately
 *     authorised SubscriptionRegistry lifecycle projection exists, posture
 *     remains explicitly UNKNOWN; server-side command gates are unchanged.
 *   v6.3.0-AUTHENTICATED-WORKSPACE-PROJECTION-HANDOFF — Treats the current
 *     AuthProvider initialTenant as the only authenticated bootstrap candidate,
 *     requires its canonical identifier to equal authenticatedTenantId, and
 *     adopts that already server-revalidated projection without calling
 *     GET /api/tenants/{tenant_id}. Persisted browser state cannot establish an
 *     authenticated tenant. This closes the post-MFA LEGAL_PARTNER 403 caused
 *     by incorrectly requiring tenant:profile:read after workspace-bootstrap
 *     had already certified principal, membership, business role, and tenant.
 *   v6.2.0-POST-MFA-AUTHORITY-BOOTSTRAP — Hydrated only the authenticated
 *     tenant, removed bootstrap directory fetch, and failed closed on
 *     discovered/authenticated tenant mismatch; same-tenant switching remained
 *     idempotent.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: Browser storage and discovered tenant state never
 *                             become authenticated authority. An authenticated
 *                             tenant is accepted only from AuthProvider's
 *                             server-owned workspace-bootstrap projection.
 * TENANT BOUNDARY: authenticatedTenantId must exactly equal the initialTenant
 *                  canonical identifier before any authenticated tenant is
 *                  exposed. Refresh and alias resolution expose only that exact
 *                  projection; no global directory or arbitrary profile read occurs.
 * AUTHORITY BOUNDARY: Client projection only. Python EOS owns authentication,
 *                     ACTIVE principal/membership/business-role truth and
 *                     canonical tenant resolution. This context grants no
 *                     tenant-profile permission or authorization role.
 * FINANCIAL AUTHORITY BOUNDARY: None. Dunning state is read-only projection;
 *                               Kennel EOS remains exclusive financial execution
 *                               and settlement authority.
 */

import React, { createContext, useContext, useState, useEffect, useMemo, useCallback } from 'react';
import PropTypes from 'prop-types';
// Subscription lifecycle authority is not inferred from a dunning projection.

// ─── Context Definition ──────────────────────────────────────────────────────
export const TenantContext = createContext({
  activeTenant: null,
  tenants: [],
  loading: false,
  error: null,
  bootstrapReady: true,
  authorityMismatch: false,
  resolveTenant: async () => null,
  switchTenant: async () => {},
  refreshTenants: async () => {},
  accessPosture: { state: 'UNKNOWN', source: 'SUBSCRIPTION_LIFECYCLE_NOT_PROVIDED', updatedAt: null },
  isReadOnly: false,
  refreshAccessPosture: async () => {},
  setActiveTenant: () => {},
});

// ─── Provider Component ──────────────────────────────────────────────────────

export const TenantProvider = ({ children, initialTenant = null, authenticatedTenantId = '' }) => {
  const [tenants, setTenants] = useState([]);
  const [activeTenant, setActiveTenant] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [bootstrapReady, setBootstrapReady] = useState(false);
  const [authorityMismatch, setAuthorityMismatch] = useState(false);
  const [accessPosture, setAccessPosture] = useState({ state: 'UNKNOWN', source: 'SUBSCRIPTION_LIFECYCLE_NOT_PROVIDED', updatedAt: null });

  /**
   * @function tenantIdentifier
   * @description Resolves a tenant identifier without trusting a display name for access enforcement.
   * @param {Object|null} tenant - Active tenant record from the Kennel directory.
   * @returns {string} Canonical identifier or an empty string when the tenant has not resolved.
   * @collaboration Keeps the dunning access guard aligned with Kennel tenant header conventions.
   */
  const tenantIdentifier = useCallback((tenant) => String(
    tenant?.tenant_id || tenant?.tenantId || tenant?.id || tenant?._id || ''
  ).trim(), []);

  /**
   * @function refreshAccessPosture
   * @description Retain UNKNOWN until EOS supplies an independently authorised
   *              SubscriptionRegistry lifecycle projection. Billing dunning is
   *              collection evidence and must never be used as access authority.
   * @param {Object|null} tenant - Current authenticated tenant projection.
   * @returns {Promise<Object>} Explicitly unresolved, non-authoritative posture.
   * @collaboration EOS IAM retains all command permissions and EOS subscription
   *                lifecycle authority must furnish future access decisions.
   * @tenant Only a canonical authenticated tenant ID can scope a projection.
   * @mutation None: no billing or subscription state changes.
   * @financial No payment, entitlement, suspension or settlement authority.
   */
  const refreshAccessPosture = useCallback(async (tenant = activeTenant) => {
    const tenantId = tenantIdentifier(tenant);
    const unresolved = {
      state: 'UNKNOWN',
      source: tenantId
        ? 'SUBSCRIPTION_REGISTRY_LIFECYCLE_NOT_PROJECTED'
        : 'AUTHENTICATED_TENANT_NOT_VERIFIED',
      updatedAt: null,
    };
    setAccessPosture(unresolved);
    return unresolved;
  }, [activeTenant, tenantIdentifier]);

  // ─── Project the server-certified authenticated workspace tenant exactly ───
  useEffect(() => {
    let cancelled = false;
    const expectedId = String(authenticatedTenantId || '').trim();

    const finish = () => {
      if (!cancelled) setBootstrapReady(true);
    };

    if (expectedId) {
      const authenticatedCandidate = initialTenant;
      const candidateId = tenantIdentifier(authenticatedCandidate);

      if (!authenticatedCandidate || candidateId !== expectedId) {
        setActiveTenant(null);
        setAuthorityMismatch(true);
        setError('AUTHENTICATED_WORKSPACE_AUTHORITY_MISMATCH');
        finish();
        return () => { cancelled = true; };
      }

      setActiveTenant((previous) => (
        tenantIdentifier(previous) === candidateId ? previous : authenticatedCandidate
      ));
      setTenants((previous) => (
        previous.some((item) => tenantIdentifier(item) === candidateId)
          ? previous
          : [...previous, authenticatedCandidate]
      ));
      localStorage.setItem('wilsy_active_tenant', JSON.stringify(authenticatedCandidate));
      setAuthorityMismatch(false);
      setError(null);
      setLoading(false);
      finish();
      return () => { cancelled = true; };
    }

    // A missing authenticated workspace is not repaired from browser storage
    // or an unverified initial projection. Only EOS bootstrap can set scope.
    setActiveTenant(null);
    setTenants([]);
    setAuthorityMismatch(false);
    setError(null);
    setLoading(false);
    finish();
    return () => { cancelled = true; };
  }, [authenticatedTenantId, initialTenant, tenantIdentifier]);

  // ─── Refresh the authenticated tenant projection without global listing ────
  const refreshTenants = useCallback(async () => {
    const authenticatedId = String(authenticatedTenantId || '').trim();
    const activeId = tenantIdentifier(activeTenant);
    const authorizedProjection = Boolean(
      authenticatedId && activeTenant && activeId === authenticatedId && !authorityMismatch
    );
    const current = authorizedProjection ? [activeTenant] : [];
    setTenants(current);
    setLoading(false);
    setError(null);
    return current;
  }, [activeTenant, authenticatedTenantId, authorityMismatch, tenantIdentifier]);

  useEffect(() => {
    refreshAccessPosture(activeTenant);
  }, [activeTenant, refreshAccessPosture]);

  // ─── Resolve only the authenticated workspace projection ──────────────────
  const resolveTenant = useCallback(async (alias) => {
    const authenticatedId = String(authenticatedTenantId || '').trim();
    const activeId = tenantIdentifier(activeTenant);
    if (!alias || !authenticatedId || activeId !== authenticatedId || authorityMismatch) return null;
    const clean = String(alias).trim().toLowerCase();
    const identifiers = [
      activeTenant?.tenant_id,
      activeTenant?.tenantId,
      activeTenant?.id,
      activeTenant?._id,
      activeTenant?.name,
      activeTenant?.alias,
    ].filter((value) => typeof value === 'string').map((value) => value.trim().toLowerCase());
    return identifiers.includes(clean) ? activeTenant : null;
  }, [activeTenant, authenticatedTenantId, authorityMismatch, tenantIdentifier]);

  // ─── Switch active tenant ─────────────────────────────────────────────────
  const switchTenant = useCallback(async (tenantId) => {
    const requestedId = String(tenantId || '').trim();
    if (!requestedId) throw new Error('A canonical tenant identifier is required.');

    const authenticatedId = String(authenticatedTenantId || '').trim();
    if (!authenticatedId) {
      throw new Error('TENANT_SWITCH_REQUIRES_AUTHENTICATED_WORKSPACE');
    }
    if (requestedId !== authenticatedId) {
      // Cross-tenant changes require a fresh EOS membership decision and
      // session issuance. A client directory lookup cannot switch authority.
      throw new Error('TENANT_SWITCH_REQUIRES_EOS_MEMBERSHIP_SELECTION');
    }

    const activeId = tenantIdentifier(activeTenant);
    if (activeId !== authenticatedId) {
      throw new Error('AUTHENTICATED_WORKSPACE_AUTHORITY_MISMATCH');
    }
    return activeTenant;
  }, [activeTenant, authenticatedTenantId, tenantIdentifier]);

  // ─── Exposed context value ────────────────────────────────────────────────
  const contextValue = useMemo(() => ({
    activeTenant,
    tenants,
    loading,
    error,
    bootstrapReady,
    authorityMismatch,
    resolveTenant,
    switchTenant,
    refreshTenants,
    accessPosture,
    isReadOnly: ['SUSPENDED_READONLY', 'TERMINATED'].includes(accessPosture.state),
    refreshAccessPosture,
    setActiveTenant,
  }), [activeTenant, tenants, loading, error, bootstrapReady, authorityMismatch, resolveTenant, switchTenant, refreshTenants, accessPosture, refreshAccessPosture]);

  return (
    <TenantContext.Provider value={contextValue}>
      {children}
    </TenantContext.Provider>
  );
};

TenantProvider.propTypes = {
  children: PropTypes.node.isRequired,
  initialTenant: PropTypes.object,
  authenticatedTenantId: PropTypes.string,
};

export const useTenants = () => {
  const context = useContext(TenantContext);
  if (!context) {
    throw new Error('useTenants must be used within a TenantProvider');
  }
  return context;
};

export default TenantContext;

/**
 * ARTIFACT: client/src/contexts/tenantContext.jsx
 * VERSION: v6.5.0-GOVERNED-C2-TENANT-DIRECTORY-DENY
 * AUTHORITY BOUNDARY: browser tenant projection only; Python EOS workspace-bootstrap remains authoritative
 * TENANT POSTURE: authenticated initialTenant must exactly match authenticatedTenantId; persisted browser state cannot establish authenticated scope
 * FAIL-CLOSED POSTURE: missing or mismatched authenticated projection exposes no active tenant and performs no compensating privileged tenant-profile request
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
