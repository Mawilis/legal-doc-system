/**
 * TITLE: WILSY OS Sovereign Tenant Context
 * VERSION: v6.3.0-AUTHENTICATED-WORKSPACE-PROJECTION-HANDOFF
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
 *                  exposed. Cross-tenant mismatch fails closed without a tenant
 *                  profile or directory request.
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
import tenantApi from '../services/api/tenantApi'; // ✅ Corrected path
import sovereignClient from '../utils/sovereignClient';

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
  accessPosture: { state: 'ACTIVE', source: 'UNRESOLVED', updatedAt: null },
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
  const [accessPosture, setAccessPosture] = useState({ state: 'ACTIVE', source: 'UNRESOLVED', updatedAt: null });

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
   * @description Loads the authoritative Kennel dunning posture used to restrict mutating tenant actions.
   * @param {Object|null} tenant - Tenant whose platform subscription posture must be evaluated.
   * @returns {Promise<Object>} Resolved posture, retaining a non-blocking unknown state on transport failure.
   * @collaboration Makes read-only suspension explicit in the UI without fabricating a financial enforcement result.
   */
  const refreshAccessPosture = useCallback(async (tenant = activeTenant) => {
    const tenantId = tenantIdentifier(tenant);
    if (!tenantId) {
      const unresolved = { state: 'ACTIVE', source: 'UNRESOLVED', updatedAt: null };
      setAccessPosture(unresolved);
      return unresolved;
    }
    try {
      const response = await sovereignClient.get('/billing/dunning/state', {
        headers: { 'X-Tenant-ID': tenantId },
      });
      const payload = response?.data?.data || response?.data || {};
      const states = Array.isArray(payload.states) ? payload.states : [];
      const newest = states[0] || {};
      const resolved = {
        state: String(newest.state || 'ACTIVE').toUpperCase(),
        source: states.length ? 'KENNEL_DUNNING_LEDGER' : 'KENNEL_NO_DUNNING_CASE',
        updatedAt: newest.updated_at || newest.evaluated_at || null,
        invoiceId: newest.invoice_id || null,
        subscriptionId: newest.subscription_id || null,
      };
      setAccessPosture(resolved);
      return resolved;
    } catch (requestError) {
      const unavailable = { state: 'ACTIVE', source: 'SOURCE_UNAVAILABLE', updatedAt: null, error: requestError.message };
      setAccessPosture(unavailable);
      return unavailable;
    }
  }, [activeTenant, tenantIdentifier]);

  // ─── Project the server-certified authenticated workspace tenant exactly ───
  useEffect(() => {
    let cancelled = false;
    const expectedId = String(authenticatedTenantId || '').trim();

    let persisted = null;
    if (!expectedId) {
      try {
        const saved = localStorage.getItem('wilsy_active_tenant');
        persisted = saved ? JSON.parse(saved) : null;
      } catch {
        persisted = null;
      }
    }

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

    const candidate = initialTenant || persisted;
    const candidateId = tenantIdentifier(candidate);
    if (candidate) {
      setActiveTenant((previous) => (
        tenantIdentifier(previous) === candidateId ? previous : candidate
      ));
      setAuthorityMismatch(false);
      setError(null);
    }
    finish();
    return () => { cancelled = true; };
  }, [authenticatedTenantId, initialTenant, tenantIdentifier]);

  // ─── Refresh tenant list from Kennel ──────────────────────────────────────
  const refreshTenants = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await tenantApi.getTenants();
      const tenantList = Array.isArray(response?.data) ? response.data : [];
      setTenants(tenantList);
      if (tenantList.length && activeTenant && !tenantList.some(t => tenantIdentifier(t) === tenantIdentifier(activeTenant))) {
        setActiveTenant(null);
        localStorage.removeItem('wilsy_active_tenant');
      }
    } catch (err) {
      const message = err.response?.data?.message || err.message || 'Failed to load tenants.';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [activeTenant, tenantIdentifier]);

  useEffect(() => {
    refreshAccessPosture(activeTenant);
  }, [activeTenant, refreshAccessPosture]);

  // ─── Resolve tenant by alias ──────────────────────────────────────────────
  const resolveTenant = useCallback(async (alias) => {
    if (!alias) return null;
    const clean = alias.trim().toLowerCase();
    const found = tenants.find(t =>
      t.tenant_id?.toLowerCase() === clean ||
      t.name?.toLowerCase() === clean ||
      t.alias?.toLowerCase() === clean
    );
    if (found) return found;

    try {
      const response = await tenantApi.getTenant(clean);
      const tenant = response?.data;
      if (tenant) {
        setTenants(prev => {
          if (prev.some(t => t.tenant_id === tenant.tenant_id)) return prev;
          return [...prev, tenant];
        });
        return tenant;
      }
    } catch {
      // ignore
    }
    return null;
  }, [tenants]);

  // ─── Switch active tenant ─────────────────────────────────────────────────
  const switchTenant = useCallback(async (tenantId) => {
    const requestedId = String(tenantId || '').trim();
    if (!requestedId) throw new Error('A canonical tenant identifier is required.');
    if (tenantIdentifier(activeTenant).toLowerCase() === requestedId.toLowerCase()) return activeTenant;
    setLoading(true);
    setError(null);
    try {
      let tenant = tenants.find(t => tenantIdentifier(t).toLowerCase() === requestedId.toLowerCase());
      if (!tenant) {
        const response = await tenantApi.getTenant(requestedId);
        tenant = response?.data;
        if (!tenant) throw new Error('Tenant not found.');
        setTenants((prev) => prev.some((item) => tenantIdentifier(item) === tenantIdentifier(tenant)) ? prev : [...prev, tenant]);
      }
      const resolvedId = tenantIdentifier(tenant);
      if (authenticatedTenantId && resolvedId !== String(authenticatedTenantId).trim()) {
        setAuthorityMismatch(true);
        throw new Error('AUTHENTICATED_WORKSPACE_AUTHORITY_MISMATCH');
      }
      if (tenantIdentifier(activeTenant) !== resolvedId) setActiveTenant(tenant);
      localStorage.setItem('wilsy_active_tenant', JSON.stringify(tenant));
      setAuthorityMismatch(false);
      return tenant;
    } catch (err) {
      const message = err.response?.data?.message || err.message || 'Failed to switch tenant.';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [activeTenant, authenticatedTenantId, tenantIdentifier, tenants]);

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
 * VERSION: v6.3.0-AUTHENTICATED-WORKSPACE-PROJECTION-HANDOFF
 * AUTHORITY BOUNDARY: browser tenant projection only; Python EOS workspace-bootstrap remains authoritative
 * TENANT POSTURE: authenticated initialTenant must exactly match authenticatedTenantId; persisted browser state cannot establish authenticated scope
 * FAIL-CLOSED POSTURE: missing or mismatched authenticated projection exposes no active tenant and performs no compensating privileged tenant-profile request
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
