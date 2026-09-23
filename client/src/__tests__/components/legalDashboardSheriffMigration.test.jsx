/**
 * WILSY OS — CERTIFIED SHERIFF COCKPIT MIGRATION CERTIFICATE
 * VERSION: v1.0.1-L8-6A-SHERIFF-COCKPIT-MIGRATION-CERT
 * AUTHORITY: Client presentation/wiring certification only.
 * EPITOME: Proves the registered LegalDashboard consumes the certified queue
 *          adapter, renders only backend-provided queue truth, fails closed on
 *          sheriff authorization denial, and contains no legacy mock sheriff
 *          metrics, clients, GPS, revenue, invoice, or deputy fixture truth.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/legalDashboardSheriffMigration.test.jsx
 * CERTIFICATION / UPDATE DATE: 2026-09-23
 * CHANGELOG: 2026-09-23 v1.0.1-L8-6A-SHERIFF-COCKPIT-MIGRATION-CERT rebinds the component certificate to the
 *            immutable-row client adapter and corrects duplicate-label
 *            assertions to match the intentional metric + queue-panel UI.
 */

import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const { getSheriffOperationalQueues } = vi.hoisted(() => ({
  getSheriffOperationalQueues: vi.fn(),
}));

vi.mock('../../services/legalOperationsService.js', () => ({
  LEGAL_OPERATIONS_CLIENT_VERSION: 'v1.0.1-L8-6A-SHERIFF-QUEUE-CLIENT',
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

describe('L8-6A certified sheriff cockpit migration', () => {
  beforeEach(() => {
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

  it('renders sheriff-authority denial without any browser fixture fallback', async () => {
    getSheriffOperationalQueues.mockRejectedValueOnce({
      response: { status: 403, data: { detail: 'Tenant authorization denied.' } },
    });

    render(<LegalDashboard roleView="DEPUTY" />);

    expect(
      await screen.findByText('SHERIFF_AUTHORITY_REQUIRED'),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Deputy personal queues remain blocked/i),
    ).toBeInTheDocument();
    expect(screen.queryByText('document-office')).not.toBeInTheDocument();
    expect(screen.queryByText('attempt-active')).not.toBeInTheDocument();
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
      await screen.findByText('Deputy personal queue'),
    ).toBeInTheDocument();
    expect(screen.getByText('Same-day / urgent prioritisation')).toBeInTheDocument();
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
      "v5.0.0-L8-6A-CERTIFIED-SHERIFF-COCKPIT",
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
 * VERSION: v1.0.1-L8-6A-SHERIFF-COCKPIT-MIGRATION-CERT
 * AUTHORITY BOUNDARY: deterministic client presentation/wiring evidence only
 * TENANT POSTURE: only server-authorized queue payloads reach presentation
 * FAIL-CLOSED POSTURE: authorization/evidence failures never create fixture truth
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
