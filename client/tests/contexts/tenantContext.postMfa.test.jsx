/**
 * TITLE: Authenticated Workspace Tenant Projection Handoff Certificate
 * VERSION: v1.1.0-AUTHENTICATED-WORKSPACE-PROJECTION-HANDOFF-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Proves TenantProvider consumes only the exact AuthProvider
 *          server-certified workspace tenant during authenticated bootstrap,
 *          ignores persisted browser state as authority, performs no redundant
 *          tenant-profile read, fails closed on mismatch or missing projection,
 *          and keeps explicit directory refresh separate.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/contexts/tenantContext.postMfa.test.jsx
 * COLLABORATION / OWNERSHIP: TenantProvider, AuthProvider workspace-bootstrap
 *                            projection, Kennel tenantApi client.
 * CERTIFICATION / UPDATE DATE: 2026-09-24
 * CHANGELOG:
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

import React from 'react';
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
  const {
    activeTenant,
    bootstrapReady,
    authorityMismatch,
    error,
    switchTenant,
    refreshTenants,
  } = useTenants();

  return (
    <div>
      <span data-testid="ready">{String(bootstrapReady)}</span>
      <span data-testid="tenant">{activeTenant?.tenantId || ''}</span>
      <span data-testid="tenant-name">{activeTenant?.name || ''}</span>
      <span data-testid="mismatch">{String(authorityMismatch)}</span>
      <span data-testid="error">{error || ''}</span>
      <button type="button" onClick={() => switchTenant('TENANT-A')}>same</button>
      <button type="button" onClick={() => refreshTenants()}>refresh</button>
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

  it('keeps same-tenant switching idempotent and directory refresh explicit', async () => {
    renderProvider({
      initialTenant: authenticatedTenant,
      authenticatedTenantId: 'TENANT-A',
    });

    await waitFor(() => expect(screen.getByTestId('ready')).toHaveTextContent('true'));

    fireEvent.click(screen.getByRole('button', { name: 'same' }));

    expect(tenantApi.getTenant).not.toHaveBeenCalled();
    expect(tenantApi.getTenants).not.toHaveBeenCalled();

    tenantApi.getTenants.mockResolvedValue({ data: [authenticatedTenant] });
    fireEvent.click(screen.getByRole('button', { name: 'refresh' }));

    await waitFor(() => expect(tenantApi.getTenants).toHaveBeenCalledTimes(1));
    expect(tenantApi.getTenant).not.toHaveBeenCalled();
  });
});

/**
 * ARTIFACT: client/tests/contexts/tenantContext.postMfa.test.jsx
 * VERSION: v1.1.0-AUTHENTICATED-WORKSPACE-PROJECTION-HANDOFF-CERT
 * AUTHORITY BOUNDARY: browser tenant projection certificate only; Python EOS workspace-bootstrap remains authoritative
 * TENANT POSTURE: exact authenticated initialTenant/authenticatedTenantId match required; persisted state cannot establish authenticated scope
 * FAIL-CLOSED POSTURE: missing or mismatched authenticated projection exposes no active tenant and performs no compensating privileged tenant-profile read
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
