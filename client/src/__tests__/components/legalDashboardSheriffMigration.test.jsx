/**
 * WILSY OS — ROLE-SCOPED LEGAL COCKPIT MIGRATION CERTIFICATE
 * VERSION: v2.0.1-L8-6C-ROLE-SCOPED-LEGAL-COCKPIT-CERT
 * AUTHORITY: Client presentation/wiring certification only.
 * EPITOME: Proves LegalDashboard preserves the certified SHERIFF cockpit,
 *          exposes only L8-6C bound personal work for DEPUTY, performs no
 *          cross-role fallback, avoids privileged reads for unresolved roles,
 *          and contains no legacy mock/GPS/revenue/billing/deputy fixture truth.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/legalDashboardSheriffMigration.test.jsx
 * CERTIFICATION / UPDATE DATE: 2026-09-23
 * CHANGELOG: 2026-09-23 v2.0.1-L8-6C-ROLE-SCOPED-LEGAL-COCKPIT-CERT rebinds the role-scoped cockpit certificate
 *            to production v6.0.1 after the non-behavioral empty-state copy
 *            cleanup.
 *            2026-09-23 v2.0.0-L8-6C-ROLE-SCOPED-LEGAL-COCKPIT-CERT certifies role-scoped SHERIFF/DEPUTY
 *            endpoint selection, bound-deputy personal-work rendering,
 *            unresolved-role network silence, no cross-role fallback, and
 *            removal of obsolete deputy-queue blocked messaging.
 *            2026-09-23 v1.0.1-L8-6A-SHERIFF-COCKPIT-MIGRATION-CERT rebinds the component certificate to the
 *            immutable-row client adapter and corrects duplicate-label
 *            assertions to match the intentional metric + queue-panel UI.
 */

import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const { getDeputyPersonalActiveWork, getSheriffOperationalQueues } = vi.hoisted(() => ({
  getDeputyPersonalActiveWork: vi.fn(),
  getSheriffOperationalQueues: vi.fn(),
}));

vi.mock('../../services/legalOperationsService.js', () => ({
  LEGAL_OPERATIONS_CLIENT_VERSION: 'v1.1.0-L8-6C-ROLE-SCOPED-LEGAL-OPERATIONS-CLIENT',
  getDeputyPersonalActiveWork,
  getSheriffOperationalQueues,
}));

import LegalDashboard from '../../components/industry/LegalDashboard.jsx';

const DASHBOARD_SOURCE = resolve(
  process.cwd(),
  'src/components/industry/LegalDashboard.jsx',
);

const liveQueues = () => ({
  tenantId: 'tenant-sheriff',
  visibility: 'SHERIFF_OPERATIONAL_QUEUE',
  officeReceipt: [
    {
      tenant_id: 'tenant-sheriff',
      document_id: 'document-office',
      case_matter_id: 'matter-office',
      document_type: 'summons',
      state: 'REGISTERED',
      registered_at: '2026-09-23T10:00:00+00:00',
    },
  ],
  deputyAssignment: [
    {
      tenant_id: 'tenant-sheriff',
      document_id: 'document-received',
      case_matter_id: 'matter-received',
      document_type: 'notice',
      state: 'RECEIVED',
      received_at: '2026-09-23T10:10:00+00:00',
    },
  ],
  activeAttempts: [
    {
      tenant_id: 'tenant-sheriff',
      attempt_id: 'attempt-active',
      instruction_id: 'instruction-active',
      document_id: 'document-active',
      deputy_id: 'deputy-canonical',
      state: 'ALLOCATED',
      allocated_at: '2026-09-23T10:20:00+00:00',
    },
  ],
});

const liveDeputyWork = () => ({
  tenantId: 'tenant-deputy',
  visibility: 'DEPUTY_PERSONAL_ACTIVE_WORK',
  deputyId: 'deputy-bound',
  activeAttempts: [
    {
      tenant_id: 'tenant-deputy',
      attempt_id: 'attempt-mine',
      instruction_id: 'instruction-mine',
      document_id: 'document-mine',
      deputy_id: 'deputy-bound',
      state: 'ATTEMPTED',
      allocated_at: '2026-09-23T10:20:00+00:00',
    },
  ],
});

describe('L8-6C role-scoped Legal Operations cockpit migration', () => {
  beforeEach(() => {
    getDeputyPersonalActiveWork.mockReset();
    getSheriffOperationalQueues.mockReset();
  });

  it('renders only certified queue rows returned by the client adapter', async () => {
    getSheriffOperationalQueues.mockResolvedValueOnce(liveQueues());

    render(<LegalDashboard roleView="SHERIFF" />);

    await waitFor(() => {
      expect(getSheriffOperationalQueues).toHaveBeenCalledTimes(1);
    });

    expect(await screen.findByText('document-office')).toBeInTheDocument();
    expect(screen.getByText('document-received')).toBeInTheDocument();
    expect(screen.getByText('attempt-active')).toBeInTheDocument();
    expect(screen.getByText('deputy-canonical')).toBeInTheDocument();
    expect(screen.getByText(/Tenant: tenant-sheriff/i)).toBeInTheDocument();

    expect(screen.getAllByText('Office receipt').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Deputy assignment').length).toBeGreaterThan(0);
    expect(screen.getByText('Active service attempts')).toBeInTheDocument();
    expect(
      screen.getByText(/No mock legal truth/i),
    ).toBeInTheDocument();
  });

  it('renders only the authenticated deputy personal-work projection', async () => {
    getDeputyPersonalActiveWork.mockResolvedValueOnce(liveDeputyWork());

    render(<LegalDashboard roleView="DEPUTY" />);

    await waitFor(() => {
      expect(getDeputyPersonalActiveWork).toHaveBeenCalledTimes(1);
    });
    expect(getSheriffOperationalQueues).not.toHaveBeenCalled();

    expect(await screen.findByText('attempt-mine')).toBeInTheDocument();
    expect(screen.getAllByText('deputy-bound').length).toBeGreaterThan(0);
    expect(screen.getByText(/My active service work/i)).toBeInTheDocument();
    expect(screen.getByText(/Tenant: tenant-deputy/i)).toBeInTheDocument();
    expect(screen.queryByText('Office receipt')).not.toBeInTheDocument();
    expect(screen.queryByText('Deputy assignment')).not.toBeInTheDocument();
    expect(screen.queryByText('document-office')).not.toBeInTheDocument();
  });

  it('keeps deputy denial bounded and never falls back to sheriff queues', async () => {
    getDeputyPersonalActiveWork.mockRejectedValueOnce({
      response: {
        status: 403,
        data: { detail: 'DEPUTY_IDENTITY_BINDING_REQUIRED' },
      },
    });

    render(<LegalDashboard roleView="DEPUTY" />);

    expect(
      await screen.findByText('DEPUTY_IDENTITY_BINDING_REQUIRED'),
    ).toBeInTheDocument();
    expect(getSheriffOperationalQueues).not.toHaveBeenCalled();
    expect(screen.queryByText('document-office')).not.toBeInTheDocument();
    expect(screen.queryByText('attempt-active')).not.toBeInTheDocument();
  });

  it('does not probe privileged queue endpoints for unresolved legal role scope', async () => {
    render(<LegalDashboard roleView="LEGAL_VIEW" />);

    expect(
      await screen.findByText('LEGAL_ROLE_SCOPE_REQUIRED'),
    ).toBeInTheDocument();
    expect(getDeputyPersonalActiveWork).not.toHaveBeenCalled();
    expect(getSheriffOperationalQueues).not.toHaveBeenCalled();
  });

  it('keeps unsupported future capabilities explicit instead of synthetic', async () => {
    getSheriffOperationalQueues.mockResolvedValueOnce({
      ...liveQueues(),
      officeReceipt: [],
      deputyAssignment: [],
      activeAttempts: [],
    });

    render(<LegalDashboard roleView="SHERIFF" />);

    expect(
      await screen.findByText('Same-day / urgent prioritisation'),
    ).toBeInTheDocument();
    expect(screen.queryByText('Deputy personal queue')).not.toBeInTheDocument();
    expect(screen.getByText('Distance / GPS routing')).toBeInTheDocument();
    expect(screen.getByText('Billing readiness')).toBeInTheDocument();
    expect(screen.getByText('Return-generation queue')).toBeInTheDocument();
    expect(
      screen.getByText(/Observed fact ≠ derived signal ≠ AI inference/i),
    ).toBeInTheDocument();
  });

  it('contains no legacy hard-coded sheriff truth or direct fetch transport', () => {
    const source = readFileSync(DASHBOARD_SOURCE, 'utf8');

    expect(source).toContain(
      "getSheriffOperationalQueues",
    );
    expect(source).toContain(
      "getDeputyPersonalActiveWork",
    );
    expect(source).toContain(
      "v6.0.1-L8-6C-ROLE-SCOPED-LEGAL-COCKPIT",
    );
    expect(source).not.toContain('API_BASE_URL');
    expect(source).not.toContain('fetch(');

    for (const forbidden of [
      '12450',
      '284500',
      'Deputy Williams',
      'Deputy Peterson',
      'Smith & Associates',
      'Johnson Law Firm',
      'John Doe Construction',
      'serviceAddress',
      'monthlyRevenue',
      'successRate',
      'lat:',
      'lng:',
      'setInvoices(',
      'setClients(',
      'setDeputies(',
      'showRegisterModal',
    ]) {
      expect(source).not.toContain(forbidden);
    }
  });
});

/**
 * ARTIFACT: legalDashboardSheriffMigration.test.jsx
 * VERSION: v2.0.1-L8-6C-ROLE-SCOPED-LEGAL-COCKPIT-CERT
 * AUTHORITY BOUNDARY: deterministic role-scoped client presentation/wiring evidence only
 * TENANT POSTURE: only server-authorized sheriff or bound-deputy payloads reach presentation
 * FAIL-CLOSED POSTURE: unresolved/denied/unavailable roles never cross-fallback or create fixture truth
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
