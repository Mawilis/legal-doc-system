/**
 * TITLE: Post-MFA Tenant Bootstrap Authority Certificate
 * VERSION: v1.0.0-POST-MFA-BOOTSTRAP-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Proves authenticated tenant bootstrap is exact, bounded, idempotent,
 *          and fail-closed without a directory fetch or cross-tenant projection.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/contexts/tenantContext.postMfa.test.jsx
 * COLLABORATION / OWNERSHIP: TenantProvider, AuthProvider, Kennel tenantApi.
 * CERTIFICATION / UPDATE DATE: 2026-09-17
 * CHANGELOG: v1.0.0-POST-MFA-BOOTSTRAP-CERT — Initial focused certificate.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
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

const authenticatedTenant = { tenantId: 'TENANT-A', alias: 'tenant-a', name: 'Tenant A' };

function Harness() {
  const { activeTenant, bootstrapReady, authorityMismatch, error, switchTenant, refreshTenants } = useTenants();
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

describe('post-MFA tenant bootstrap authority', () => {
  beforeEach(() => {
    const values = new Map();
    const storage = {
      getItem: (key) => values.get(key) || null,
      setItem: (key, value) => values.set(key, String(value)),
      removeItem: (key) => values.delete(key),
      clear: () => values.clear(),
    };
    Object.defineProperty(globalThis, 'localStorage', { configurable: true, value: storage });
    tenantApi.getTenant.mockReset();
    tenantApi.getTenant.mockResolvedValue({ data: authenticatedTenant });
    tenantApi.getTenants.mockReset();
    sovereignClient.get.mockClear();
  });

  it('hydrates the authenticated tenant through one exact canonical lookup without downloading the directory', async () => {
    renderProvider({ initialTenant: authenticatedTenant, authenticatedTenantId: 'TENANT-A' });
    await waitFor(() => expect(screen.getByTestId('ready')).toHaveTextContent('true'));
    expect(screen.getByTestId('tenant')).toHaveTextContent('TENANT-A');
    expect(tenantApi.getTenant).toHaveBeenCalledTimes(1);
    expect(tenantApi.getTenant).toHaveBeenCalledWith('TENANT-A');
    expect(tenantApi.getTenants).not.toHaveBeenCalled();
  });

  it('re-hydrates a same-id local tenant from canonical server authority', async () => {
    const staleLocalTenant = { tenantId: 'TENANT-A', alias: 'tenant-a', name: 'Stale Local Tenant' };
    const canonicalTenant = { tenantId: 'TENANT-A', alias: 'tenant-a', name: 'Canonical Server Tenant' };
    tenantApi.getTenant.mockResolvedValue({ data: canonicalTenant });

    renderProvider({ initialTenant: staleLocalTenant, authenticatedTenantId: 'TENANT-A' });

    await waitFor(() => expect(screen.getByTestId('ready')).toHaveTextContent('true'));
    expect(tenantApi.getTenant).toHaveBeenCalledWith('TENANT-A');
    expect(screen.getByTestId('tenant')).toHaveTextContent('TENANT-A');
    expect(screen.getByTestId('tenant-name')).toHaveTextContent('Canonical Server Tenant');
    expect(tenantApi.getTenants).not.toHaveBeenCalled();
  });

  it('fails closed when the discovered tenant does not match authenticated authority', async () => {
    renderProvider({ initialTenant: { tenantId: 'TENANT-B', name: 'Tenant B' }, authenticatedTenantId: 'TENANT-A' });
    await waitFor(() => expect(screen.getByTestId('mismatch')).toHaveTextContent('true'));
    expect(screen.getByTestId('tenant')).toHaveTextContent('');
    expect(screen.getByTestId('error')).toHaveTextContent('AUTHENTICATED_WORKSPACE_AUTHORITY_MISMATCH');
    expect(tenantApi.getTenants).not.toHaveBeenCalled();
  });

  it('keeps same-tenant switching idempotent and reserves directory refresh for explicit action', async () => {
    renderProvider({ initialTenant: authenticatedTenant, authenticatedTenantId: 'TENANT-A' });
    await waitFor(() => expect(screen.getByTestId('ready')).toHaveTextContent('true'));
    fireEvent.click(screen.getByRole('button', { name: 'same' }));
    expect(tenantApi.getTenant).toHaveBeenCalledTimes(1);
    expect(tenantApi.getTenant).toHaveBeenCalledWith('TENANT-A');
    expect(tenantApi.getTenants).not.toHaveBeenCalled();
    tenantApi.getTenants.mockResolvedValue({ data: [authenticatedTenant] });
    fireEvent.click(screen.getByRole('button', { name: 'refresh' }));
    await waitFor(() => expect(tenantApi.getTenants).toHaveBeenCalledTimes(1));
  });
});

/**
 * ARTIFACT: client/tests/contexts/tenantContext.postMfa.test.jsx
 * VERSION: v1.0.0-POST-MFA-BOOTSTRAP-CERT
 * AUTHORITY BOUNDARY: browser tenant projection only
 * TENANT POSTURE: exact authenticated tenant; mismatch is fail-closed
 * FAIL-CLOSED POSTURE: no active tenant is exposed on authority mismatch
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
