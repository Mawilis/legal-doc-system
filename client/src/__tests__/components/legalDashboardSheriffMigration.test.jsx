/**
 * WILSY OS — ROLE-SCOPED LEGAL COCKPIT MIGRATION CERTIFICATE
 * VERSION: v3.0.0-L8-6I-DEPUTY-FIELD-COMMAND-COCKPIT-CERT
 * AUTHORITY: Client presentation/wiring certification only.
 * EPITOME: Proves LegalDashboard preserves the certified SHERIFF cockpit while
 *          correlating L8-6C deputy work with L8-6D command capability, exposing
 *          touch-friendly governed L8-6G field controls, requiring canonical
 *          post-command refresh before success, performing no cross-role fallback,
 *          and creating no browser P5M sequence/provenance/legal/financial truth.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/legalDashboardSheriffMigration.test.jsx
 * CERTIFICATION / UPDATE DATE: 2026-09-23
 * CHANGELOG: 2026-09-23 v3.0.0-L8-6I-DEPUTY-FIELD-COMMAND-COCKPIT-CERT certifies exact work/capability parity, browser
 *            field-device provenance-only identity, begin/completed/not-completed
 *            controls, observation capture, command pending/error/success states,
 *            mandatory canonical refresh, terminal disappearance confirmation,
 *            and no sequence/fingerprint/GPS/financial authority in the cockpit.
 *            2026-09-23 v2.0.1-L8-6C-ROLE-SCOPED-LEGAL-COCKPIT-CERT rebinds the role-scoped cockpit certificate
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
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const {
  getDeputyFieldCapabilities,
  getDeputyPersonalActiveWork,
  getSheriffOperationalQueues,
  recordDeputyFieldOutcome,
  transitionDeputyFieldAttempt,
} = vi.hoisted(() => ({
  getDeputyFieldCapabilities: vi.fn(),
  getDeputyPersonalActiveWork: vi.fn(),
  getSheriffOperationalQueues: vi.fn(),
  recordDeputyFieldOutcome: vi.fn(),
  transitionDeputyFieldAttempt: vi.fn(),
}));

vi.mock('../../services/legalOperationsService.js', () => ({
  LEGAL_OPERATIONS_CLIENT_VERSION: 'v1.2.0-L8-6H-DEPUTY-FIELD-COMMAND-CLIENT',
  getDeputyFieldCapabilities,
  getDeputyPersonalActiveWork,
  getSheriffOperationalQueues,
  recordDeputyFieldOutcome,
  transitionDeputyFieldAttempt,
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

const CURRENT_EVIDENCE = 'a'.repeat(128);

const liveDeputyWork = (state = 'ATTEMPTED') => ({
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
      state,
      allocated_at: '2026-09-23T10:20:00+00:00',
    },
  ],
});

const emptyDeputyWork = () => ({
  tenantId: 'tenant-deputy',
  visibility: 'DEPUTY_PERSONAL_ACTIVE_WORK',
  deputyId: 'deputy-bound',
  activeAttempts: [],
});

const liveDeputyCapabilities = (state = 'ATTEMPTED') => ({
  tenantId: 'tenant-deputy',
  visibility: 'DEPUTY_FIELD_COMMAND_CAPABILITIES',
  deputyId: 'deputy-bound',
  capabilities: [
    {
      tenantId: 'tenant-deputy',
      attemptId: 'attempt-mine',
      instructionId: 'instruction-mine',
      documentId: 'document-mine',
      deputyId: 'deputy-bound',
      currentState: state,
      currentEvidenceIdentity: CURRENT_EVIDENCE,
      nextCommandKinds:
        state === 'ALLOCATED'
          ? ['TRANSITION_TO_ATTEMPTED']
          : [
            'RECORD_COMPLETED_OUTCOME',
            'RECORD_NOT_COMPLETED_OUTCOME',
          ],
    },
  ],
});

const emptyDeputyCapabilities = () => ({
  tenantId: 'tenant-deputy',
  visibility: 'DEPUTY_FIELD_COMMAND_CAPABILITIES',
  deputyId: 'deputy-bound',
  capabilities: [],
});

describe('L8-6I governed deputy Legal Operations cockpit', () => {
  beforeEach(() => {
    getDeputyFieldCapabilities.mockReset();
    getDeputyPersonalActiveWork.mockReset();
    getSheriffOperationalQueues.mockReset();
    recordDeputyFieldOutcome.mockReset();
    transitionDeputyFieldAttempt.mockReset();
    window.localStorage.clear();
    window.localStorage.setItem(
      'wilsy.legal-operations.field-device.v1',
      'browser-device:test-device',
    );
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

  it('renders only correlated bound-deputy work and state-valid terminal controls', async () => {
    getDeputyPersonalActiveWork.mockResolvedValueOnce(liveDeputyWork());
    getDeputyFieldCapabilities.mockResolvedValueOnce(
      liveDeputyCapabilities(),
    );

    render(<LegalDashboard roleView="DEPUTY" />);

    await waitFor(() => {
      expect(getDeputyPersonalActiveWork).toHaveBeenCalledTimes(1);
      expect(getDeputyFieldCapabilities).toHaveBeenCalledTimes(1);
    });
    expect(getSheriffOperationalQueues).not.toHaveBeenCalled();

    expect(await screen.findByText('attempt-mine')).toBeInTheDocument();
    expect(screen.getAllByText('deputy-bound').length).toBeGreaterThan(0);
    expect(screen.getByText(/My active service work/i)).toBeInTheDocument();
    expect(screen.getByText(/Tenant: tenant-deputy/i)).toBeInTheDocument();
    expect(screen.getByRole('button', {
      name: 'Record completed outcome',
    })).toBeInTheDocument();
    expect(screen.getByRole('button', {
      name: 'Record not completed',
    })).toBeInTheDocument();
    expect(screen.queryByRole('button', {
      name: 'Begin attempt',
    })).not.toBeInTheDocument();
    expect(screen.getByText(/Sequence lineage: server-owned/i)).toBeInTheDocument();
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
    getDeputyFieldCapabilities.mockResolvedValueOnce(
      liveDeputyCapabilities(),
    );

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
    expect(getDeputyFieldCapabilities).not.toHaveBeenCalled();
    expect(getSheriffOperationalQueues).not.toHaveBeenCalled();
  });

  it('fails closed when deputy work and capability projections drift', async () => {
    getDeputyPersonalActiveWork.mockResolvedValueOnce(liveDeputyWork());
    const drift = liveDeputyCapabilities();
    drift.capabilities[0].attemptId = 'attempt-other';
    getDeputyFieldCapabilities.mockResolvedValueOnce(drift);

    render(<LegalDashboard roleView="DEPUTY" />);

    expect(
      await screen.findByText('QUEUE_READ_FAILED'),
    ).toBeInTheDocument();
    expect(
      screen.getByText('LEGAL_OPERATIONS_DEPUTY_CAPABILITY_PARITY_INVALID'),
    ).toBeInTheDocument();
    expect(screen.queryByRole('button', {
      name: 'Record completed outcome',
    })).not.toBeInTheDocument();
    expect(transitionDeputyFieldAttempt).not.toHaveBeenCalled();
    expect(recordDeputyFieldOutcome).not.toHaveBeenCalled();
  });

  it('begins an allocated attempt and shows success only after canonical refresh', async () => {
    getDeputyPersonalActiveWork
      .mockResolvedValueOnce(liveDeputyWork('ALLOCATED'))
      .mockResolvedValueOnce(liveDeputyWork('ATTEMPTED'));
    getDeputyFieldCapabilities
      .mockResolvedValueOnce(liveDeputyCapabilities('ALLOCATED'))
      .mockResolvedValueOnce(liveDeputyCapabilities('ATTEMPTED'));
    transitionDeputyFieldAttempt.mockResolvedValueOnce({
      data: { state: 'ATTEMPTED' },
      fieldEvidence: { event_id: 'server-validated' },
    });

    render(<LegalDashboard roleView="DEPUTY" />);

    const evidenceInput = await screen.findByLabelText(
      'Observation evidence reference for attempt-mine',
    );
    fireEvent.change(evidenceInput, {
      target: { value: 'photo:door-attempt-mine' },
    });

    const begin = screen.getByRole('button', { name: 'Begin attempt' });
    await waitFor(() => expect(begin).toBeEnabled());
    fireEvent.click(begin);

    await waitFor(() => {
      expect(transitionDeputyFieldAttempt).toHaveBeenCalledTimes(1);
    });
    expect(transitionDeputyFieldAttempt).toHaveBeenCalledWith(
      expect.objectContaining({
        attemptId: 'attempt-mine',
        currentEvidenceIdentity: CURRENT_EVIDENCE,
        deviceId: 'browser-device:test-device',
        eventId: expect.stringMatching(/^browser-event:/),
        observationReference: 'photo:door-attempt-mine',
      }),
    );
    const submitted = transitionDeputyFieldAttempt.mock.calls[0][0];
    expect(submitted).not.toHaveProperty('sequenceNumber');
    expect(submitted).not.toHaveProperty('previousEventFingerprint');
    expect(submitted).not.toHaveProperty('evidenceFingerprint');

    expect(
      await screen.findByText(
        'Canonical refresh confirms this attempt is now ATTEMPTED.',
      ),
    ).toBeInTheDocument();
    expect(getDeputyPersonalActiveWork).toHaveBeenCalledTimes(2);
    expect(getDeputyFieldCapabilities).toHaveBeenCalledTimes(2);
    expect(screen.getByRole('button', {
      name: 'Record completed outcome',
    })).toBeInTheDocument();
  });

  it('records a terminal outcome and confirms disappearance from canonical active work', async () => {
    getDeputyPersonalActiveWork
      .mockResolvedValueOnce(liveDeputyWork('ATTEMPTED'))
      .mockResolvedValueOnce(emptyDeputyWork());
    getDeputyFieldCapabilities
      .mockResolvedValueOnce(liveDeputyCapabilities('ATTEMPTED'))
      .mockResolvedValueOnce(emptyDeputyCapabilities());
    recordDeputyFieldOutcome.mockResolvedValueOnce({
      data: { outcome: 'COMPLETED' },
      fieldEvidence: { event_id: 'server-validated-terminal' },
    });

    render(<LegalDashboard roleView="DEPUTY" />);

    const evidenceInput = await screen.findByLabelText(
      'Observation evidence reference for attempt-mine',
    );
    fireEvent.change(evidenceInput, {
      target: { value: 'photo:served-attempt-mine' },
    });

    const complete = screen.getByRole('button', {
      name: 'Record completed outcome',
    });
    await waitFor(() => expect(complete).toBeEnabled());
    fireEvent.click(complete);

    await waitFor(() => {
      expect(recordDeputyFieldOutcome).toHaveBeenCalledTimes(1);
    });
    expect(recordDeputyFieldOutcome).toHaveBeenCalledWith(
      expect.objectContaining({
        attemptId: 'attempt-mine',
        deviceId: 'browser-device:test-device',
        eventId: expect.stringMatching(/^browser-event:/),
        observationReference: 'photo:served-attempt-mine',
        outcome: 'COMPLETED',
      }),
    );

    expect(
      await screen.findByText(
        'Canonical refresh confirms the terminal attempt left active work.',
      ),
    ).toBeInTheDocument();
    expect(screen.queryByText('attempt-mine')).not.toBeInTheDocument();
    expect(
      screen.getByText(/No active service attempts are assigned/i),
    ).toBeInTheDocument();
  });

  it('does not claim command success when the governed mutation fails', async () => {
    getDeputyPersonalActiveWork.mockResolvedValueOnce(
      liveDeputyWork('ATTEMPTED'),
    );
    getDeputyFieldCapabilities.mockResolvedValueOnce(
      liveDeputyCapabilities('ATTEMPTED'),
    );
    recordDeputyFieldOutcome.mockRejectedValueOnce({
      response: {
        status: 409,
        data: { detail: 'LEGAL_OPERATIONS_FIELD_EVIDENCE_CONFLICT' },
      },
    });

    render(<LegalDashboard roleView="DEPUTY" />);

    fireEvent.change(
      await screen.findByLabelText(
        'Observation evidence reference for attempt-mine',
      ),
      { target: { value: 'photo:conflicting-event' } },
    );
    fireEvent.click(screen.getByRole('button', {
      name: 'Record completed outcome',
    }));

    expect(
      await screen.findByText('Field command not confirmed'),
    ).toBeInTheDocument();
    expect(
      screen.getByText('LEGAL_OPERATIONS_FIELD_EVIDENCE_CONFLICT'),
    ).toBeInTheDocument();
    expect(screen.queryByText('Canonical refresh confirmed')).not.toBeInTheDocument();
    expect(getDeputyPersonalActiveWork).toHaveBeenCalledTimes(1);
    expect(getDeputyFieldCapabilities).toHaveBeenCalledTimes(1);
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
      "getDeputyFieldCapabilities",
    );
    expect(source).toContain(
      "transitionDeputyFieldAttempt",
    );
    expect(source).toContain(
      "recordDeputyFieldOutcome",
    );
    expect(source).toContain(
      "v7.0.0-L8-6I-DEPUTY-FIELD-COMMAND-COCKPIT",
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
      'sequenceNumber',
      'previousEventFingerprint',
      'evidenceFingerprint',
    ]) {
      expect(source).not.toContain(forbidden);
    }
  });
});

/**
 * ARTIFACT: legalDashboardSheriffMigration.test.jsx
 * VERSION: v3.0.0-L8-6I-DEPUTY-FIELD-COMMAND-COCKPIT-CERT
 * AUTHORITY BOUNDARY: deterministic role-scoped presentation and governed deputy observation-command wiring evidence only
 * TENANT POSTURE: exact server-authorized deputy work/capability parity is required before command controls render
 * FAIL-CLOSED POSTURE: unresolved/denied/drifted reads, command errors and failed canonical refresh never cross-fallback or claim success
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
