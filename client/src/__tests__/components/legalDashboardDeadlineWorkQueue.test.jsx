/**
 * WILSY OS — LEGAL MATTER DEADLINE WORK QUEUE CERTIFICATE
 * VERSION: v1.0.0-D4B-MATTER-DEADLINE-WORK-QUEUE-CERT
 * AUTHORITY: Browser presentation/wiring evidence only.
 * EPITOME: Certifies on-demand matter deadline reads in the Legal Practice
 *          workspace, exact matter correlation, frozen D4A rows, permission
 *          narrowing, and absence of browser legal-period/overdue inference.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/legalDashboardDeadlineWorkQueue.test.jsx
 * CERTIFICATION / UPDATE DATE: 2026-10-11
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * TENANT BOUNDARY: Deadline transport derives tenant authority on the server.
 * AUTHORITY BOUNDARY: UI presentation only; Python EOS remains sovereign.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import React from 'react';
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const {
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

const emptySummary = Object.freeze({
  matters_total: 2,
  matters_open: 1,
  matters_closed: 1,
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
});

const workspace = () => ({
  schema: 'WILSY-LEGAL-OPERATIONS-PRACTICE-WORKSPACE/V2',
  version: 'v1.8.0-L8-7D15-FIRST-CLASS-MATTER-WORKSPACE-API',
  tenantId: 'tenant-law',
  visibility: 'LEGAL_PRACTICE_WORKSPACE',
  summary: { ...emptySummary },
  matters: [
    {
      case_matter_id: 'matter-001',
      matter_reference: 'CASE-2026-0001',
      opened_at: '2026-10-01T08:00:00+00:00',
      state: 'OPEN',
      evidence_identity: 'a'.repeat(128),
    },
    {
      case_matter_id: 'matter-002',
      matter_reference: 'CASE-2026-0002',
      opened_at: '2026-09-01T08:00:00+00:00',
      state: 'CLOSED',
      evidence_identity: 'b'.repeat(128),
    },
  ],
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

const activeDeadline = Object.freeze({
  deadlineId: 'deadline-001',
  caseMatterId: 'matter-001',
  deadlineKind: 'FILING',
  title: 'File answering affidavit',
  dueAt: '2026-10-20T10:00:00+00:00',
  sourceType: 'COURT_ORDER',
  jurisdictionReference: 'court:gp-hc',
  createdAt: '2026-10-11T10:00:00+00:00',
  supersedesDeadlineId: null,
  status: 'ACTIVE',
});

const satisfiedDeadline = Object.freeze({
  deadlineId: 'deadline-002',
  caseMatterId: 'matter-002',
  deadlineKind: 'CONTRACTUAL',
  title: 'Deliver closing bundle',
  dueAt: '2026-10-05T12:00:00+00:00',
  sourceType: 'CONTRACTUAL',
  jurisdictionReference: 'contract:msa-1',
  createdAt: '2026-09-20T12:00:00+00:00',
  supersedesDeadlineId: null,
  status: 'SATISFIED',
});

describe('D4B Legal matter deadline work queue', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getLegalPracticeWorkspace.mockResolvedValue(workspace());
    getLegalConflictScreenings.mockResolvedValue(screeningQueue());
    getLegalMatterDeadlines.mockImplementation(async (matterId) => (
      matterId === 'matter-001' ? [activeDeadline] : [satisfiedDeadline]
    ));
  });

  it('loads deadline rows only when the governed Deadlines view is opened', async () => {
    render(<LegalDashboard roleView="LEGAL_PARTNER" />);

    expect(await screen.findByRole('button', { name: 'Deadlines' })).toBeInTheDocument();
    expect(getLegalMatterDeadlines).not.toHaveBeenCalled();

    fireEvent.click(screen.getByRole('button', { name: 'Deadlines' }));

    await waitFor(() => {
      expect(getLegalMatterDeadlines).toHaveBeenCalledTimes(2);
    });
    expect(getLegalMatterDeadlines).toHaveBeenNthCalledWith(1, 'matter-001');
    expect(getLegalMatterDeadlines).toHaveBeenNthCalledWith(2, 'matter-002');

    const queueHeading = screen.getByRole('heading', { name: 'Matter deadlines' });
    const queue = queueHeading.closest('section');
    expect(queue).not.toBeNull();
    expect(within(queue).getByText('File answering affidavit')).toBeInTheDocument();
    expect(within(queue).getByText('Deliver closing bundle')).toBeInTheDocument();
    expect(within(queue).getByText('CASE-2026-0001 · FILING')).toBeInTheDocument();
    expect(within(queue).getByText('CASE-2026-0002 · CONTRACTUAL')).toBeInTheDocument();
    expect(within(queue).getByText('ACTIVE')).toBeInTheDocument();
    expect(within(queue).getByText('SATISFIED')).toBeInTheDocument();
    expect(within(queue).queryByText(/OVERDUE/i)).not.toBeInTheDocument();
  });

  it('keeps deadline transport closed when an authoritative permission projection omits read authority', async () => {
    render(
      <LegalDashboard
        roleView="LEGAL_SECRETARY"
        user={{
          id: 'principal-secretary',
          permissions: [],
          legalPermissionsAuthoritative: true,
        }}
      />,
    );

    await screen.findByText('Legal Operations Command Center');
    expect(screen.queryByRole('button', { name: 'Deadlines' })).not.toBeInTheDocument();
    expect(getLegalMatterDeadlines).not.toHaveBeenCalled();
  });

  it('shows bounded deadline failure without fabricating queue success', async () => {
    getLegalMatterDeadlines.mockRejectedValueOnce({
      response: {
        status: 503,
        data: { detail: 'LEGAL_MATTER_DEADLINE_UNAVAILABLE' },
      },
    });

    render(<LegalDashboard roleView="LEGAL_PARTNER" />);
    fireEvent.click(await screen.findByRole('button', { name: 'Deadlines' }));

    expect(
      await screen.findByText(/Deadline evidence is unavailable/i),
    ).toBeInTheDocument();
    expect(screen.getByText(/LEGAL_MATTER_DEADLINE_UNAVAILABLE/)).toBeInTheDocument();
    expect(
      screen.getByText('No certified deadlines are recorded for the current matter workspace.'),
    ).toBeInTheDocument();
  });
});

/**
 * ARTIFACT: legalDashboardDeadlineWorkQueue.test.jsx
 * VERSION: v1.0.0-D4B-MATTER-DEADLINE-WORK-QUEUE-CERT
 * AUTHORITY BOUNDARY: on-demand deadline presentation certificate only
 * TENANT POSTURE: tenant authority remains server-derived
 * FAIL-CLOSED POSTURE: denied/unavailable deadline evidence never falls back or invents posture
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
