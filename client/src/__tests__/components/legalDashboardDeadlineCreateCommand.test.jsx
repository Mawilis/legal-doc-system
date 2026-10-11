/**
 * WILSY OS — LEGAL MATTER DEADLINE CREATE COMMAND CERTIFICATE
 * VERSION: v1.0.0-D4C-MATTER-DEADLINE-CREATE-COMMAND-CERT
 * AUTHORITY: Browser presentation/command wiring evidence only.
 * EPITOME: Certifies write-gated evidenced deadline creation for Partner,
 *          Attorney and Paralegal while Secretary remains read-only.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/legalDashboardDeadlineCreateCommand.test.jsx
 * CERTIFICATION / UPDATE DATE: 2026-10-11
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * TENANT BOUNDARY: Tenant authority remains server-derived.
 * AUTHORITY BOUNDARY: Browser captures explicit deadline evidence only; Python
 *                     EOS owns authorization, deadline semantics and persistence.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const {
  createLegalMatterDeadline,
  getLegalMatterDeadlines,
  generateLegalReturnOfService,
  getDeputyFieldCapabilities,
  getDeputyPersonalActiveWork,
  getLegalClientMatters,
  getLegalConflictScreenings,
  getLegalFinanceEvidence,
  getLegalPracticeWorkspace,
  getSheriffOperationalQueues,
  issueLegalConflictReview,
  recordDeputyFieldOutcome,
  registerLegalIntake,
  transitionDeputyFieldAttempt,
} = vi.hoisted(() => ({
  createLegalMatterDeadline: vi.fn(),
  getLegalMatterDeadlines: vi.fn(),
  generateLegalReturnOfService: vi.fn(),
  getDeputyFieldCapabilities: vi.fn(),
  getDeputyPersonalActiveWork: vi.fn(),
  getLegalClientMatters: vi.fn(),
  getLegalConflictScreenings: vi.fn(),
  getLegalFinanceEvidence: vi.fn(),
  getLegalPracticeWorkspace: vi.fn(),
  getSheriffOperationalQueues: vi.fn(),
  issueLegalConflictReview: vi.fn(),
  recordDeputyFieldOutcome: vi.fn(),
  registerLegalIntake: vi.fn(),
  transitionDeputyFieldAttempt: vi.fn(),
}));

vi.mock('../../services/legalMatterDeadlineService.js', () => ({
  createLegalMatterDeadline,
  getLegalMatterDeadlines,
}));

vi.mock('../../services/legalOperationsService.js', () => ({
  LEGAL_OPERATIONS_CLIENT_VERSION: 'v1.8.0-L8-8N-CONFLICT-SCREENING-READ-CLIENT',
  generateLegalReturnOfService,
  getDeputyFieldCapabilities,
  getDeputyPersonalActiveWork,
  getLegalClientMatters,
  getLegalConflictScreenings,
  getLegalFinanceEvidence,
  getLegalPracticeWorkspace,
  getSheriffOperationalQueues,
  issueLegalConflictReview,
  recordDeputyFieldOutcome,
  registerLegalIntake,
  transitionDeputyFieldAttempt,
}));

vi.mock('../../contexts/authContext', () => ({
  useAuth: () => ({
    user: {
      id: 'principal-law',
      email: 'operator@example.test',
      role: 'tenant_legal_partner',
      tenantId: 'tenant-law',
    },
    tenant: {
      tenantId: 'tenant-law',
      displayName: 'WILSY Legal Practice',
      status: 'ACTIVE',
    },
  }),
}));

vi.mock('../../contexts/tenantContext', () => ({
  useTenants: () => ({
    activeTenant: {
      tenantId: 'tenant-law',
      displayName: 'WILSY Legal Practice',
      status: 'ACTIVE',
    },
    tenants: [],
  }),
}));

import LegalDashboard from '../../components/industry/LegalDashboard.jsx';

const workspace = () => ({
  schema: 'WILSY-LEGAL-OPERATIONS-PRACTICE-WORKSPACE/V2',
  version: 'v1.8.0-L8-7D15-FIRST-CLASS-MATTER-WORKSPACE-API',
  tenantId: 'tenant-law',
  visibility: 'LEGAL_PRACTICE_WORKSPACE',
  summary: {
    matters_total: 1,
    matters_open: 1,
    matters_closed: 0,
    instructions_total: 0,
    instructions_registered: 0,
    instructions_accepted: 0,
    instructions_closed: 0,
    instructions_cancelled: 0,
    documents_total: 0,
    documents_registered: 0,
    documents_received: 0,
    documents_allocated: 0,
    documents_returned: 0,
    attempts_total: 0,
    attempts_allocated: 0,
    attempts_attempted: 0,
    attempts_completed: 0,
    attempts_not_completed: 0,
    attempts_cancelled: 0,
    executions_total: 0,
    executions_completed: 0,
    executions_not_completed: 0,
    returns_total: 0,
  },
  matters: [{
    case_matter_id: 'matter-001',
    matter_reference: 'CASE-2026-0001',
    opened_at: '2026-10-01T08:00:00+00:00',
    state: 'OPEN',
    evidence_identity: 'a'.repeat(128),
  }],
  instructions: [],
  documents: [],
  attempts: [],
  executions: [],
  returns: [],
});

const screeningQueue = () => ({
  schema: 'WILSY-LEGAL-CONFLICT-SCREENING-PRESENTATION/V1',
  version: 'v1.9.0-L8-8N-CONFLICT-SCREENING-READ-API',
  tenantId: 'tenant-law',
  visibility: 'LEGAL_CONFLICT_SCREENING_REVIEW_QUEUE',
  screenings: [],
});

const createdDeadline = Object.freeze({
  deadlineId: 'deadline-created',
  caseMatterId: 'matter-001',
  deadlineKind: 'FILING',
  title: 'File replying affidavit',
  dueAt: '2026-10-25T08:30:00.000Z',
  sourceType: 'COURT_ORDER',
  jurisdictionReference: 'court:gp-hc',
  createdAt: '2026-10-11T13:00:00.000Z',
  supersedesDeadlineId: null,
  status: 'ACTIVE',
});

describe('D4C Legal matter deadline create command', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getLegalPracticeWorkspace.mockResolvedValue(workspace());
    getLegalConflictScreenings.mockResolvedValue(screeningQueue());
    getLegalMatterDeadlines
      .mockResolvedValueOnce([])
      .mockResolvedValue([createdDeadline]);
    createLegalMatterDeadline.mockResolvedValue(createdDeadline);
  });

  it('lets Partner dispatch the strict evidenced create contract and requires canonical refresh', async () => {
    render(<LegalDashboard roleView="LEGAL_PARTNER" />);
    fireEvent.click(await screen.findByRole('button', { name: 'Deadlines' }));

    expect(await screen.findByLabelText('Create matter deadline')).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText('Deadline title'), {
      target: { value: 'File replying affidavit' },
    });
    fireEvent.change(screen.getByLabelText('Deadline due at'), {
      target: { value: '2026-10-25T10:30' },
    });
    fireEvent.change(screen.getByLabelText('Deadline source reference'), {
      target: { value: 'court-order:2026-10-11' },
    });
    fireEvent.change(screen.getByLabelText('Deadline source evidence fingerprint'), {
      target: { value: 'c'.repeat(128) },
    });
    fireEvent.change(screen.getByLabelText('Deadline jurisdiction reference'), {
      target: { value: 'court:gp-hc' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Record deadline' }));

    await waitFor(() => expect(createLegalMatterDeadline).toHaveBeenCalledTimes(1));
    const command = createLegalMatterDeadline.mock.calls[0][0];

    expect(Object.keys(command).sort()).toEqual([
      'caseMatterId',
      'createdAt',
      'deadlineId',
      'deadlineKind',
      'dueAt',
      'jurisdictionReference',
      'sourceEvidenceFingerprint',
      'sourceReference',
      'sourceType',
      'supersedesDeadlineId',
      'title',
    ].sort());
    expect(command.caseMatterId).toBe('matter-001');
    expect(command.deadlineKind).toBe('FILING');
    expect(command.title).toBe('File replying affidavit');
    expect(command.sourceType).toBe('COURT_ORDER');
    expect(command.sourceReference).toBe('court-order:2026-10-11');
    expect(command.sourceEvidenceFingerprint).toBe('c'.repeat(128));
    expect(command.jurisdictionReference).toBe('court:gp-hc');
    expect(command.supersedesDeadlineId).toBeNull();
    expect(command.deadlineId).toMatch(/^deadline-/);
    expect(command.dueAt).toBe(new Date('2026-10-25T10:30').toISOString());
    expect(Number.isNaN(Date.parse(command.createdAt))).toBe(false);
    expect(command).not.toHaveProperty('tenantId');
    expect(command).not.toHaveProperty('principalId');
    expect(command).not.toHaveProperty('status');
    expect(command).not.toHaveProperty('overdue');
    expect(command).not.toHaveProperty('paymentState');

    await waitFor(() => expect(getLegalMatterDeadlines).toHaveBeenCalledTimes(2));
    expect(
      await screen.findByText(/canonical refresh confirmed/i),
    ).toBeInTheDocument();
  });

  it('keeps Secretary read-only while preserving deadline visibility', async () => {
    render(<LegalDashboard roleView="LEGAL_SECRETARY" />);
    fireEvent.click(await screen.findByRole('button', { name: 'Deadlines' }));

    await screen.findByRole('heading', { name: 'Matter deadlines' });
    expect(screen.queryByLabelText('Create matter deadline')).not.toBeInTheDocument();
    expect(createLegalMatterDeadline).not.toHaveBeenCalled();
  });

  it('lets authoritative permission projection narrow Partner to read-only deadline access', async () => {
    render(
      <LegalDashboard
        roleView="LEGAL_PARTNER"
        user={{
          id: 'principal-partner-readonly',
          permissions: ['legal_operations:matter_deadline:read'],
          legalPermissionsAuthoritative: true,
        }}
      />,
    );
    fireEvent.click(await screen.findByRole('button', { name: 'Deadlines' }));

    await screen.findByRole('heading', { name: 'Matter deadlines' });
    expect(screen.queryByLabelText('Create matter deadline')).not.toBeInTheDocument();
    expect(createLegalMatterDeadline).not.toHaveBeenCalled();
  });

  it('surfaces create failure without fabricating success or refresh', async () => {
    createLegalMatterDeadline.mockRejectedValueOnce({
      response: {
        status: 409,
        data: { detail: 'LEGAL_MATTER_DEADLINE_REPLAY_DIVERGENCE' },
      },
    });

    render(<LegalDashboard roleView="LEGAL_ATTORNEY" />);
    fireEvent.click(await screen.findByRole('button', { name: 'Deadlines' }));

    await screen.findByLabelText('Create matter deadline');
    fireEvent.change(screen.getByLabelText('Deadline title'), {
      target: { value: 'File replying affidavit' },
    });
    fireEvent.change(screen.getByLabelText('Deadline due at'), {
      target: { value: '2026-10-25T10:30' },
    });
    fireEvent.change(screen.getByLabelText('Deadline source reference'), {
      target: { value: 'court-order:2026-10-11' },
    });
    fireEvent.change(screen.getByLabelText('Deadline source evidence fingerprint'), {
      target: { value: 'c'.repeat(128) },
    });
    fireEvent.change(screen.getByLabelText('Deadline jurisdiction reference'), {
      target: { value: 'court:gp-hc' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Record deadline' }));

    expect(await screen.findByRole('alert')).toBeInTheDocument();
    expect(screen.queryByText(/canonical refresh confirmed/i)).not.toBeInTheDocument();
    expect(getLegalMatterDeadlines).toHaveBeenCalledTimes(1);
  });
});

/**
 * ARTIFACT: legalDashboardDeadlineCreateCommand.test.jsx
 * VERSION: v1.0.0-D4C-MATTER-DEADLINE-CREATE-COMMAND-CERT
 * AUTHORITY BOUNDARY: write-gated deadline command presentation certificate only
 * TENANT POSTURE: tenant authority remains server-derived
 * FAIL-CLOSED POSTURE: denied, malformed or failed create never fabricates success
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
