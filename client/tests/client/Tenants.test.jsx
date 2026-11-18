/**
 * TITLE: Active Tenant Management Workspace Tests
 * VERSION: v1.1.0-GOVERNED-C2-DENY-BOUNDARY
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Verifies /tms shows only the authenticated workspace and accurately
 *          disables cross-tenant lifecycle operations pending governed C2.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/client/Tenants.test.jsx
 * COLLABORATION / OWNERSHIP: App.jsx /tms route, Sovereign_TenantManager and TenantContext.
 * CERTIFICATION / UPDATE DATE: 2026-11-10
 * CHANGELOG: v1.1.0-GOVERNED-C2-DENY-BOUNDARY proves that global listing,
 *            provisioning and suspension are absent while the authenticated
 *            Python EOS workspace projection remains visible.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic in-memory projections only; no network or persistence.
 * TENANT BOUNDARY: A decoy directory entry is never rendered; only activeTenant is displayed.
 * AUTHORITY BOUNDARY: UI evidence does not grant backend authority; C2 lifecycle remains denied.
 * FINANCIAL AUTHORITY BOUNDARY: None.
 */

import React from 'react';
import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { TenantContext } from '../../src/contexts/tenantContext.jsx';
import SovereignTenantManager from '../../src/components/sovereign/Sovereign_TenantManager.jsx';

const renderTenantManager = (value = {}) => {
  const context = {
    activeTenant: null,
    tenants: [],
    loading: false,
    error: null,
    bootstrapReady: true,
    authorityMismatch: false,
    refreshTenants: async () => [],
    resolveTenant: async () => null,
    switchTenant: async () => null,
    ...value,
  };

  return render(
    <TenantContext.Provider value={context}>
      <SovereignTenantManager />
    </TenantContext.Provider>,
  );
};

describe('Active tenant management workspace', () => {
  it('renders only the authenticated current tenant projection', () => {
    renderTenantManager({
      activeTenant: {
        tenant_id: 'tenant-authenticated',
        name: 'Authenticated Practice',
        status: 'ACTIVE',
        region: 'ZA',
        industry: 'LEGAL',
      },
      tenants: [
        { tenant_id: 'tenant-foreign', name: 'Foreign Practice' },
      ],
    });

    expect(screen.getByRole('heading', { name: 'Tenant workspace' })).toBeInTheDocument();
    expect(screen.getByText('Authenticated Practice')).toBeInTheDocument();
    expect(screen.getByText('tenant-authenticated')).toBeInTheDocument();
    expect(screen.queryByText('Foreign Practice')).not.toBeInTheDocument();
    expect(screen.getByTestId('tms-workspace-state')).toHaveTextContent(
      'AUTHENTICATED_WORKSPACE_AVAILABLE',
    );
  });

  it('keeps global list, provisioning and suspension unavailable pending C2', () => {
    renderTenantManager({
      activeTenant: { tenant_id: 'tenant-authenticated', name: 'Authenticated Practice' },
    });

    expect(screen.getByTestId('tms-lifecycle-availability')).toHaveTextContent(
      'Global tenant listing, tenant creation, and tenant suspension remain disabled',
    );
    expect(screen.queryByRole('button', { name: /new shard|provision/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /suspend/i })).not.toBeInTheDocument();
  });

  it('keeps an absent authenticated projection unavailable without sample tenants', () => {
    renderTenantManager();

    expect(screen.getByTestId('tms-workspace-state')).toHaveTextContent(
      'AUTHENTICATED_WORKSPACE_UNAVAILABLE',
    );
    expect(screen.getByTestId('tms-empty-workspace')).toBeInTheDocument();
    expect(screen.queryByText(/ENSafrica|Dentons South Africa|Bowmans|Foreign Practice/i))
      .not.toBeInTheDocument();
  });
});

/**
 * ARTIFACT: Active Tenant Management Workspace Tests
 * VERSION: v1.1.0-GOVERNED-C2-DENY-BOUNDARY
 * AUTHORITY BOUNDARY: Repository regression evidence only; Python EOS owns authorization.
 * TENANT POSTURE: Only the active authenticated projection may be rendered.
 * FAIL-CLOSED POSTURE: No global tenant data or lifecycle action is fabricated.
 * FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
