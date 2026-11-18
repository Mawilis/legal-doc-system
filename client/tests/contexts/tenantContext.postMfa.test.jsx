/**
 * TITLE: Authenticated Workspace Tenant Projection Handoff Certificate
 * VERSION: v1.3.0-GOVERNED-C2-TENANT-DIRECTORY-DENY
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Proves TenantProvider consumes only the exact AuthProvider
 *          server-certified workspace tenant during authenticated bootstrap,
 *          ignores persisted browser state as authority, performs no redundant
 *          tenant-profile read, fails closed on mismatch or missing projection,
 *          and limits refresh/alias resolution to the authenticated projection.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/contexts/tenantContext.postMfa.test.jsx
 * COLLABORATION / OWNERSHIP: TenantProvider and AuthProvider workspace-bootstrap
 *                            projection; transport mocks certify no directory call.
 * CERTIFICATION / UPDATE DATE: 2026-11-10
 * CHANGELOG:
 *   v1.3.0-GOVERNED-C2-TENANT-DIRECTORY-DENY — Proves refresh and alias resolution
 *     never issue global directory or arbitrary tenant-profile requests, and a
 *     persisted tenant is ignored when the authenticated workspace is absent.
 *   v1.2.0-NO-UNAUTHORIZED-DUNNING-BOOTSTRAP — Confirms no restricted dunning
 *     projection is fetched automatically during workspace hydration; posture
 *     remains UNKNOWN pending an actual SubscriptionRegistry lifecycle source.
 *   v1.1.0-AUTHENTICATED-WORKSPACE-PROJECTION-HANDOFF-CERT — Replaces the
 *     superseded expectation of a second GET /api/tenants/{tenant_id} after
 *     MFA with the v6.3.0 contract: authenticated initialTenant must exactly
 *     match authenticatedTenantId, persisted browser state cannot establish
 *     authenticated scope, and no tenant-profile read occurs during handoff.
 *   v1.0.0-POST-MFA-BOOTSTRAP-CERT — Initial focused post-MFA tenant bootstrap
 *     certificate.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: Synthetic tenant data only. Browser persistence
 *                             is explicitly tested as non-authoritative.
 * TENANT BOUNDARY: Exact authenticated tenant identity is required before an
 *                  active tenant is exposed; mismatch and missing projection
 *                  fail closed without tenant-profile or directory reads.
 * AUTHORITY BOUNDARY: Client projection only. Python EOS remains sovereign for
 *                     authentication, membership, business role, and canonical
 *                     tenant workspace truth.
 * FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains exclusive financial
 *                               execution and settlement authority.
 */

import React, { useState } from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const { tenantApi, sovereignClient } = vi.hoisted(() => ({
  tenantApi: { getTenant: vi.fn(), getTenants: vi.fn() },
  sovereignClient: { get: vi.fn().mockResolvedValue({ data: { states: [] } }) },
}));

vi.mock('../../src/services/api/tenantApi', () => ({ default: tenantApi }));
vi.mock('../../src/utils/sovereignClient', () => ({ default: sovereignClient }));

import { TenantProvider, useTenants } from '../../src/contexts/tenantContext.jsx';

const authenticatedTenant = {
  tenantId: 'TENANT-A',
  alias: 'tenant-a',
  name: 'Tenant A',
  status: 'ACTIVE',
};

function Harness() {
  const [switchError, setSwitchError] = useState('');
  const [resolvedTenant, setResolvedTenant] = useState('');
  const {
    activeTenant,
    bootstrapReady,
    authorityMismatch,
    error,
    switchTenant,
    resolveTenant,
    refreshTenants,
    accessPosture,
    refreshAccessPosture,
  } = useTenants();

  return (
    <div>
      <span data-testid="ready">{String(bootstrapReady)}</span>
      <span data-testid="tenant">{activeTenant?.tenantId || ''}</span>
      <span data-testid="tenant-name">{activeTenant?.name || ''}</span>
      <span data-testid="mismatch">{String(authorityMismatch)}</span>
      <span data-testid="error">{error || ''}</span>
      <span data-testid="posture">{accessPosture.state}</span>
      <span data-testid="posture-source">{accessPosture.source}</span>
      <button type="button" onClick={() => refreshAccessPosture()}>refresh posture</button>
      <span data-testid="switch-error">{switchError}</span>
      <span data-testid="resolved-tenant">{resolvedTenant}</span>
      <button type="button" onClick={() => switchTenant('TENANT-A')}>same</button>
      <button type="button" onClick={() => { void switchTenant('TENANT-B').catch((reason) => setSwitchError(reason.message)); }}>cross-tenant</button>
      <button type="button" onClick={() => refreshTenants()}>refresh</button>
      <button type="button" onClick={() => resolveTenant('TENANT-B').then((value) => setResolvedTenant(value?.tenantId || ''))}>resolve other</button>
    </div>
  );
}

const renderProvider = (props = {}) => render(
  <TenantProvider {...props}><Harness /></TenantProvider>,
);

describe('authenticated workspace tenant projection handoff', () => {
  beforeEach(() => {
    const values = new Map();
    const storage = {
      getItem: (key) => values.get(key) || null,
      setItem: (key, value) => values.set(key, String(value)),
      removeItem: (key) => values.delete(key),
      clear: () => values.clear(),
    };

    Object.defineProperty(globalThis, 'localStorage', {
      configurable: true,
      value: storage,
    });

    tenantApi.getTenant.mockReset();
    tenantApi.getTenants.mockReset();
    sovereignClient.get.mockClear();
  });

  it('adopts the exact authenticated server projection without a second tenant-profile read', async () => {
    renderProvider({
      initialTenant: authenticatedTenant,
      authenticatedTenantId: 'TENANT-A',
    });

    await waitFor(() => expect(screen.getByTestId('ready')).toHaveTextContent('true'));

    expect(screen.getByTestId('tenant')).toHaveTextContent('TENANT-A');
    expect(screen.getByTestId('tenant-name')).toHaveTextContent('Tenant A');
    expect(screen.getByTestId('mismatch')).toHaveTextContent('false');
    expect(screen.getByTestId('error')).toHaveTextContent('');
    expect(tenantApi.getTenant).not.toHaveBeenCalled();
    expect(tenantApi.getTenants).not.toHaveBeenCalled();
    expect(sovereignClient.get).not.toHaveBeenCalled();
  });

  it('does not use restricted dunning evidence as global subscription access authority', async () => {
    renderProvider({
      initialTenant: authenticatedTenant,
      authenticatedTenantId: 'TENANT-A',
    });
    await waitFor(() => expect(screen.getByTestId('ready')).toHaveTextContent('true'));
    expect(screen.getByTestId('posture')).toHaveTextContent('UNKNOWN');
    expect(screen.getByTestId('posture-source')).toHaveTextContent(
      'SUBSCRIPTION_REGISTRY_LIFECYCLE_NOT_PROJECTED',
    );
    expect(sovereignClient.get).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: 'refresh posture' }));
    expect(sovereignClient.get).not.toHaveBeenCalled();
    expect(screen.getByTestId('posture')).toHaveTextContent('UNKNOWN');
  });

  it('ignores persisted browser tenant state during authenticated bootstrap', async () => {
    localStorage.setItem('wilsy_active_tenant', JSON.stringify({
      tenantId: 'TENANT-B',
      alias: 'tenant-b',
      name: 'Persisted Browser Tenant',
    }));

    renderProvider({
      initialTenant: authenticatedTenant,
      authenticatedTenantId: 'TENANT-A',
    });

    await waitFor(() => expect(screen.getByTestId('ready')).toHaveTextContent('true'));

    expect(screen.getByTestId('tenant')).toHaveTextContent('TENANT-A');
    expect(screen.getByTestId('tenant-name')).toHaveTextContent('Tenant A');
    expect(screen.getByTestId('mismatch')).toHaveTextContent('false');
    expect(tenantApi.getTenant).not.toHaveBeenCalled();
    expect(tenantApi.getTenants).not.toHaveBeenCalled();

    expect(JSON.parse(localStorage.getItem('wilsy_active_tenant'))).toEqual(
      authenticatedTenant,
    );
  });

  it('fails closed when authenticated projection and authenticated tenant id disagree', async () => {
    renderProvider({
      initialTenant: { tenantId: 'TENANT-B', name: 'Tenant B' },
      authenticatedTenantId: 'TENANT-A',
    });

    await waitFor(() => expect(screen.getByTestId('mismatch')).toHaveTextContent('true'));

    expect(screen.getByTestId('tenant')).toHaveTextContent('');
    expect(screen.getByTestId('error')).toHaveTextContent(
      'AUTHENTICATED_WORKSPACE_AUTHORITY_MISMATCH',
    );
    expect(tenantApi.getTenant).not.toHaveBeenCalled();
    expect(tenantApi.getTenants).not.toHaveBeenCalled();
  });

  it('fails closed when authenticated scope exists but server projection is absent', async () => {
    localStorage.setItem('wilsy_active_tenant', JSON.stringify(authenticatedTenant));

    renderProvider({
      initialTenant: null,
      authenticatedTenantId: 'TENANT-A',
    });

    await waitFor(() => expect(screen.getByTestId('mismatch')).toHaveTextContent('true'));

    expect(screen.getByTestId('tenant')).toHaveTextContent('');
    expect(screen.getByTestId('error')).toHaveTextContent(
      'AUTHENTICATED_WORKSPACE_AUTHORITY_MISMATCH',
    );
    expect(tenantApi.getTenant).not.toHaveBeenCalled();
    expect(tenantApi.getTenants).not.toHaveBeenCalled();
  });

  it('does not resolve or fetch an arbitrary tenant outside the authenticated workspace', async () => {
    renderProvider({
      initialTenant: authenticatedTenant,
      authenticatedTenantId: 'TENANT-A',
    });

    await waitFor(() => expect(screen.getByTestId('ready')).toHaveTextContent('true'));
    fireEvent.click(screen.getByRole('button', { name: 'resolve other' }));

    await waitFor(() => expect(screen.getByTestId('resolved-tenant')).toHaveTextContent(''));
    expect(tenantApi.getTenant).not.toHaveBeenCalled();
    expect(tenantApi.getTenants).not.toHaveBeenCalled();
  });

  it('does not restore a persisted tenant when authenticated workspace scope is absent', async () => {
    localStorage.setItem('wilsy_active_tenant', JSON.stringify(authenticatedTenant));

    renderProvider();

    await waitFor(() => expect(screen.getByTestId('ready')).toHaveTextContent('true'));
    expect(screen.getByTestId('tenant')).toHaveTextContent('');
    expect(screen.getByTestId('mismatch')).toHaveTextContent('false');
    expect(tenantApi.getTenant).not.toHaveBeenCalled();
    expect(tenantApi.getTenants).not.toHaveBeenCalled();
  });

  it('requires a new EOS membership decision before cross-tenant switching', async () => {
    renderProvider({
      initialTenant: authenticatedTenant,
      authenticatedTenantId: 'TENANT-A',
    });

    await waitFor(() => expect(screen.getByTestId('ready')).toHaveTextContent('true'));
    fireEvent.click(screen.getByRole('button', { name: 'cross-tenant' }));

    await waitFor(() => {
      expect(screen.getByTestId('switch-error')).toHaveTextContent(
        'TENANT_SWITCH_REQUIRES_EOS_MEMBERSHIP_SELECTION',
      );
    });
    expect(screen.getByTestId('tenant')).toHaveTextContent('TENANT-A');
    expect(tenantApi.getTenant).not.toHaveBeenCalled();
    expect(tenantApi.getTenants).not.toHaveBeenCalled();
  });

  it('keeps same-tenant switching idempotent and refresh tenant-scoped without a directory request', async () => {
    renderProvider({
      initialTenant: authenticatedTenant,
      authenticatedTenantId: 'TENANT-A',
    });

    await waitFor(() => expect(screen.getByTestId('ready')).toHaveTextContent('true'));

    fireEvent.click(screen.getByRole('button', { name: 'same' }));

    expect(tenantApi.getTenant).not.toHaveBeenCalled();
    expect(tenantApi.getTenants).not.toHaveBeenCalled();

    fireEvent.click(screen.getByRole('button', { name: 'refresh' }));

    await waitFor(() => expect(screen.getByTestId('tenant')).toHaveTextContent('TENANT-A'));
    expect(tenantApi.getTenants).not.toHaveBeenCalled();
    expect(tenantApi.getTenant).not.toHaveBeenCalled();
  });
});

/**
 * ARTIFACT: client/tests/contexts/tenantContext.postMfa.test.jsx
 * VERSION: v1.3.0-GOVERNED-C2-TENANT-DIRECTORY-DENY
 * AUTHORITY BOUNDARY: browser tenant projection certificate only; Python EOS workspace-bootstrap remains authoritative
 * TENANT POSTURE: exact authenticated initialTenant/authenticatedTenantId match required; persisted state cannot establish authenticated scope
 * FAIL-CLOSED POSTURE: missing or mismatched authenticated projection exposes no active tenant; refresh and alias resolution cannot enumerate or fetch arbitrary tenants
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
