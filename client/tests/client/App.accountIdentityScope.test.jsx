/**
 * TITLE: WILSY account identity scope transition certificate
 * VERSION: v1.1.0-FOCUSED-ACCOUNT-PROFILE-CERT
 * AUTHORITY: Client projection test only; Python EOS remains the authority.
 * EPITOME: Prove that the Top App Bar account menu follows a same-principal
 *          EOS tenant and selected-capacity transition without retaining the
 *          previous scope's organisation, email, or capacity.
 * ABSOLUTE CANONICAL PATH:
 *   /Users/wilsonkhanyezi/legal-doc-system/client/tests/client/App.accountIdentityScope.test.jsx
 * COLLABORATION / OWNERSHIP: App authenticated chrome and AuthProvider contract.
 * CERTIFICATION / UPDATE DATE: 2026-11-15
 * CHANGELOG: v1.1.0-FOCUSED-ACCOUNT-PROFILE-CERT verifies focused account navigation, explicit sign-in email provenance, and durable device menu density.
 * CHANGELOG: v1.0.1-ACCOUNT-IDENTITY-SCOPE-TRANSITIONS — Certifies the existing account identity scope and authenticated workspace boundaries.
 *            Previous: v1.0.1 adds inert authenticated-client mocks so this focused UI certificate cannot issue unrelated network requests.
 * CHANGELOG: v1.0.0 adds a focused same-principal tenant and capacity transition regression.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic projections only; no credential or API access.
 * TENANT BOUNDARY: Exact supplied AuthProvider tenant must match the rendered principal.
 * AUTHORITY BOUNDARY: Presentation regression only; this test creates no tenant,
 *                     membership, capacity, entitlement, or permission authority.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';

const { api, sovereignClient } = vi.hoisted(() => ({
  api: { get: vi.fn(), post: vi.fn(), defaults: { headers: { common: {} } } },
  sovereignClient: { get: vi.fn() },
}));

vi.mock('../../src/services/api', () => ({
  default: api,
  setActiveTenantTransportId: vi.fn(),
  getRecoveryContactStatus: vi.fn().mockResolvedValue({
    status: 200, data: { status: 'VERIFICATION_REQUIRED' },
  }),
  requestRecoveryContactVerification: vi.fn(),
}));
vi.mock('../../src/utils/sovereignClient', () => ({ default: sovereignClient }));
vi.mock('../../src/components/sovereign/SovereignDashboardController.jsx', () => ({
  default: () => <main><h1>WILSY Headquarters</h1></main>,
}));
vi.mock('../../src/components/intelligence/WilsyOSIntelligenceDockRuntime.jsx', () => ({
  default: () => null,
}));

import AuthContext from '../../src/contexts/authContext.jsx';
import { AuthenticatedGlobalChrome } from '../../src/App.jsx';

const WORKSPACE_CONTRACT = 'v1.0.0-WILSY-EOS-WORKSPACE-RESOLUTION';

const ownerProjection = {
  id: 'PRINCIPAL-SAME-ACCOUNT',
  firstName: 'Alex',
  lastName: 'Example',
  email: 'login-candidate@example.test',
  workspaceEmail: 'alex.tenant-a@example.test',
  tenantId: 'TENANT-ACCOUNT-A',
  role: 'tenant_owner',
  businessRole: 'tenant_owner',
  workspaceContractVersion: WORKSPACE_CONTRACT,
};

const authProjection = (user, tenant, sessionGeneration) => ({
  isAuthenticated: true,
  authStage: 'AUTHENTICATED',
  loading: false,
  sessionGeneration,
  user,
  tenant,
});

const renderAccount = (auth) => (
  <MemoryRouter>
    <AuthContext.Provider value={auth}>
      <AuthenticatedGlobalChrome
        user={auth.user}
        onLogout={vi.fn()}
        workspaceReleased={false}
      >
        <main>Authenticated workspace</main>
      </AuthenticatedGlobalChrome>
    </AuthContext.Provider>
  </MemoryRouter>
);

describe('Top App Bar account identity scope', () => {
  it('formats an EOS HR Director capacity and exposes recovery verification only after EOS readback', async () => {
    const hrUser = {
      ...ownerProjection,
      workspaceEmail: 'hr.director@example.test',
      role: 'tenant_hr_director',
      businessRole: 'tenant_hr_director',
    };
    const auth = authProjection(hrUser, { tenantId: hrUser.tenantId, legalName: 'Tenant A Organisation' }, 9);
    render(renderAccount(auth));
    expect(screen.getByRole('button', { name: 'Open account menu' })).toHaveTextContent('HR Director capacity');
    fireEvent.click(screen.getByRole('button', { name: 'Open account menu' }));
    fireEvent.click(screen.getByRole('menuitem', { name: /Security & sessions/ }));
    expect(await screen.findByRole('button', { name: 'Verify recovery email' })).toBeInTheDocument();
  });

  it('keeps profile detail in a focused view and saves only a device-local menu preference', () => {
    const candidate = { ...ownerProjection, workspaceEmail: null };
    const auth = authProjection(candidate, { tenantId: candidate.tenantId, legalName: 'Tenant A Organisation' }, 4);
    render(renderAccount(auth));
    fireEvent.click(screen.getByRole('button', { name: 'Open account menu' }));
    const menu = screen.getByRole('menu', { name: 'Account menu' });
    expect(menu).toHaveTextContent('Sign-in email · verification pending');
    fireEvent.click(screen.getByRole('menuitem', { name: /My profile/ }));
    expect(menu).toHaveTextContent('Sign-in email, not independently verified by EOS');
    expect(screen.getByRole('menuitem', { name: /Back to account/ })).toBeInTheDocument();
    expect(screen.queryByRole('menuitem', { name: /Personal settings/ })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('menuitem', { name: /Back to account/ }));
    fireEvent.click(screen.getByRole('menuitem', { name: /Personal settings/ }));
    fireEvent.click(screen.getByRole('menuitemradio', { name: /compact/i }));
    expect(window.localStorage.getItem('wilsy:chrome:profile-density')).toBe('compact');
    expect(screen.getByRole('menuitemradio', { name: /compact/i })).toHaveAttribute('aria-checked', 'true');
  });

  it('replaces tenant and capacity identity for the same principal without leaking the prior scope', () => {
    const first = authProjection(
      ownerProjection,
      { tenantId: ownerProjection.tenantId, legalName: 'Tenant A Organisation' },
      1,
    );
    const view = render(renderAccount(first));

    fireEvent.click(screen.getByRole('button', { name: 'Open account menu' }));
    let menu = screen.getByRole('menu', { name: 'Account menu' });
    expect(menu).toHaveTextContent('Alex Example');
    expect(menu).toHaveTextContent('alex.tenant-a@example.test');
    expect(menu).toHaveTextContent('Tenant A Organisation');
    expect(menu).toHaveTextContent('Operating as: Owner');
    expect(menu).not.toHaveTextContent('login-candidate@example.test');

    const samePrincipalInTenantB = {
      ...ownerProjection,
      workspaceEmail: 'alex.tenant-b@example.test',
      tenantId: 'TENANT-ACCOUNT-B',
      role: 'tenant_auditor',
      businessRole: 'tenant_auditor',
    };
    view.rerender(renderAccount(authProjection(
      samePrincipalInTenantB,
      { tenantId: samePrincipalInTenantB.tenantId, legalName: 'Tenant B Organisation' },
      2,
    )));

    expect(screen.queryByRole('menu', { name: 'Account menu' })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Open account menu' }));
    menu = screen.getByRole('menu', { name: 'Account menu' });
    expect(menu).toHaveTextContent('Alex Example');
    expect(menu).toHaveTextContent('alex.tenant-b@example.test');
    expect(menu).toHaveTextContent('Tenant B Organisation');
    expect(menu).toHaveTextContent('Operating as: Auditor');
    expect(menu).not.toHaveTextContent('alex.tenant-a@example.test');
    expect(menu).not.toHaveTextContent('Tenant A Organisation');
    expect(menu).not.toHaveTextContent('Operating as: Owner');

    const samePrincipalNewCapacity = {
      ...samePrincipalInTenantB,
      role: 'tenant_legal_partner',
      businessRole: 'tenant_legal_partner',
    };
    view.rerender(renderAccount(authProjection(
      samePrincipalNewCapacity,
      { tenantId: samePrincipalNewCapacity.tenantId, legalName: 'Tenant B Organisation' },
      3,
    )));

    expect(screen.queryByRole('menu', { name: 'Account menu' })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Open account menu' }));
    menu = screen.getByRole('menu', { name: 'Account menu' });
    expect(menu).toHaveTextContent('Tenant B Organisation');
    expect(menu).toHaveTextContent('Operating as: Legal Partner');
    expect(menu).not.toHaveTextContent('Operating as: Auditor');
    expect(menu).not.toHaveTextContent('Tenant A Organisation');
  });
});

// ARTIFACT: client/tests/client/App.accountIdentityScope.test.jsx
// VERSION: v1.1.0-FOCUSED-ACCOUNT-PROFILE-CERT
// AUTHORITY BOUNDARY: Client projection test only; EOS owns identity and access.
// TENANT POSTURE: Exact synthetic tenant projections; no persistence.
// FAIL-CLOSED POSTURE: Mismatched or stale rendered identity fails assertions.
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
// END OF WILSY OS SOVEREIGN ARTIFACT
