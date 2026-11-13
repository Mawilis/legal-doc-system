/**
 * TITLE: Sovereign Identity Hub Client Boundary Tests
 * VERSION: v1.0.1-CURRENT-TENANT-PROJECTION
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Certifies the active identity hub renders against the canonical tenant projection and exposes no tenant-management shortcut without an authenticated principal.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/client/Sovereign_Identity_Hub.test.jsx
 * COLLABORATION / OWNERSHIP: Client identity surface and canonical TenantContext consumers.
 * CERTIFICATION / UPDATE DATE: 2026-11-10
 * CHANGELOG: v1.0.1-CURRENT-TENANT-PROJECTION mocks only the auth projection through its public hook, avoiding a network-starting provider in component tests.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Tests use synthetic in-memory projections only; no storage, network or identity authority is created.
 * TENANT BOUNDARY: The supplied context is an empty display projection and grants no tenant selection or mutation authority.
 * AUTHORITY BOUNDARY: Python EOS remains the identity and membership authority; this component test grants no access.
 * FINANCIAL AUTHORITY BOUNDARY: None.
 */

import React from 'react';
import { afterEach, describe, expect, test, vi } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { TenantContext } from '../../src/contexts/tenantContext.jsx';
import SovereignIdentityHub from '../../src/components/sovereign/Sovereign_Identity_Hub.jsx';

vi.mock('../../src/contexts/authContext', () => ({
  useAuth: () => ({ user: null, logout: vi.fn() }),
}));

const EMPTY_TENANT_PROJECTION = {
  activeTenant: null,
  tenants: [],
  loading: false,
  refreshTenants: async () => [],
  switchTenant: async () => null,
};

const renderIdentityHub = () => render(
  <MemoryRouter>
    <TenantContext.Provider value={EMPTY_TENANT_PROJECTION}>
      <SovereignIdentityHub />
    </TenantContext.Provider>
  </MemoryRouter>,
);

afterEach(() => cleanup());

describe('Sovereign Identity Hub current tenant boundary', () => {
  test('renders the identity hub with the canonical empty tenant projection', () => {
    renderIdentityHub();
    expect(screen.getByText(/SOVEREIGN IDENTITY HUB/i)).toBeInTheDocument();
    expect(screen.getByTestId('sovereign-identity-hub')).toBeInTheDocument();
  });

  test('does not expose tenant management when no authenticated principal is present', () => {
    renderIdentityHub();
    expect(screen.queryByRole('button', { name: /manage tenants/i })).not.toBeInTheDocument();
  });
});

/**
 * ARTIFACT: Sovereign Identity Hub Client Boundary Tests
 * VERSION: v1.0.1-CURRENT-TENANT-PROJECTION
 * AUTHORITY BOUNDARY: Presentation regression checks only; Python EOS owns identity, membership and workspace authority.
 * TENANT POSTURE: Empty synthetic projection; no tenant is selected or mutated.
 * FAIL-CLOSED POSTURE: Missing principal must not expose the tenant management action.
 * FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
