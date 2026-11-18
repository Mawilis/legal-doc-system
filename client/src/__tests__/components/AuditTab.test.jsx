/**
 * TITLE: WILSY OS Billing Audit Tenant Boundary Client Certificate
 * VERSION: v1.0.1-DUPLICATE-MISMATCH-ASSERTION
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Certifies persisted audit and integrity posture render only from the
 *          authenticated current-tenant Python EOS read interface.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/AuditTab.test.jsx
 * COLLABORATION / OWNERSHIP: Covers AuditTab, TenantContext, sovereignClient,
 *                            and billing audit/integrity Python EOS endpoints.
 * CERTIFICATION / UPDATE DATE: 2026-11-10
 * CHANGELOG: v1.0.1-DUPLICATE-MISMATCH-ASSERTION accepts the same fail-closed
 *            tenant mismatch in its accessible summary and empty-state row.
 *            v1.0.0-AUTHENTICATED-READONLY-CLIENT-CONTRACT certifies current
 *            tenant scoping, source-backed read-only visibility, and mismatch denial.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic event and tenant data; no live identity or transport.
 * TENANT BOUNDARY: Authenticated TenantContext is the only request scope.
 * AUTHORITY BOUNDARY: Read-only display cannot authorize control mutation or revocation.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution and settlement.
 */
import React from 'react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { cleanup, render, screen, waitFor, within } from '@testing-library/react';

const { apiGet, useTenants } = vi.hoisted(() => ({
  apiGet: vi.fn(),
  useTenants: vi.fn(),
}));

vi.mock('../../contexts/tenantContext', () => ({ useTenants }));
vi.mock('../../utils/sovereignClient', () => ({ default: { get: apiGet } }));

import { AuditTab } from '../../components/audit/AuditTab.jsx';

const TENANT = 'TENANT-AUDIT-SYNTHETIC';
const foreignTenant = 'TENANT-AUDIT-FOREIGN';
const event = {
  event_id: 'AUDIT-EVENT-SYNTHETIC-1',
  tenant_id: TENANT,
  event_type: 'BILLING_PROOF_REFERENCE_CHECKED',
  created_at: '2026-11-10T08:00:00.000Z',
  invoice_id: 'INV-SYNTHETIC-1',
  proof_hash: 'A'.repeat(128),
};
const integrity = {
  auto_renew: true,
  encrypted_backup: false,
  neural_sync: true,
  source: 'PERSISTED_TENANT_CONTROL_STATE',
};

describe('AuditTab authenticated tenant-scoped read-only contract', () => {
  beforeEach(() => {
    useTenants.mockReturnValue({
      activeTenant: { tenant_id: TENANT },
      bootstrapReady: true,
      authorityMismatch: false,
    });
    apiGet.mockReset();
    apiGet.mockImplementation((path) => Promise.resolve({
      data: path.endsWith('/events') ? [event] : integrity,
    }));
  });

  afterEach(() => cleanup());

  it('loads persisted audit and integrity data using the authenticated tenant context', async () => {
    render(<AuditTab />);

    expect(await screen.findByText('BILLING_PROOF_REFERENCE_CHECKED')).toBeInTheDocument();
    expect(screen.getByTestId('integrity-auto_renew')).toHaveTextContent('Enabled');
    expect(screen.getByTestId('integrity-encrypted_backup')).toHaveTextContent('Disabled');
    expect(screen.getByTestId('audit-integrity-source')).toHaveTextContent(
      'PERSISTED_TENANT_CONTROL_STATE',
    );
    expect(apiGet).toHaveBeenCalledWith('/billing/audit/events', expect.objectContaining({
      headers: { 'X-Tenant-ID': TENANT },
      params: { limit: 100 },
      signal: expect.any(AbortSignal),
    }));
    expect(apiGet).toHaveBeenCalledWith('/billing/audit/integrity', expect.objectContaining({
      headers: { 'X-Tenant-ID': TENANT },
      signal: expect.any(AbortSignal),
    }));

    const posture = screen.getByRole('complementary', { name: 'Read-only audit posture' });
    const integrityPanel = within(posture).getByRole('heading', { name: 'System integrity posture' }).closest('section');
    expect(within(integrityPanel).queryByRole('button')).not.toBeInTheDocument();
    expect(within(posture).getByTestId('audit-anomaly-posture')).toHaveTextContent(
      'No authenticated Python EOS anomaly feed is mounted',
    );
  });

  it('fails closed before transport when a display tenant conflicts with authenticated context', async () => {
    render(<AuditTab externalTenantId={foreignTenant} />);

    await waitFor(() => {
      expect(screen.getByTestId('audit-source-state')).toHaveTextContent(
        'AUTHENTICATED_TENANT_CONTEXT_MISMATCH',
      );
    });
    expect(screen.getAllByText('The supplied display tenant does not match the authenticated workspace.'))
      .toHaveLength(2);
    expect(apiGet).not.toHaveBeenCalled();
  });

  it('does not infer tenant scope from an external identifier when authenticated context is absent', async () => {
    useTenants.mockReturnValue({
      activeTenant: null,
      bootstrapReady: true,
      authorityMismatch: false,
    });
    render(<AuditTab externalTenantId={TENANT} />);

    await waitFor(() => {
      expect(screen.getByTestId('audit-source-state')).toHaveTextContent(
        'AUTHENTICATED_TENANT_UNAVAILABLE',
      );
    });
    expect(apiGet).not.toHaveBeenCalled();
  });
});

/**
 * ARTIFACT: WILSY OS Billing Audit Tenant Boundary Client Certificate
 * VERSION: v1.0.1-DUPLICATE-MISMATCH-ASSERTION
 * AUTHORITY BOUNDARY: Authenticated tenant read projection only.
 * TENANT POSTURE: Missing or conflicting authenticated context makes no request.
 * FAIL-CLOSED POSTURE: No client control mutation or unverified live claim.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
