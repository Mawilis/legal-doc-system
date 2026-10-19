/**
 * WILSY OS — PW-P11C LEGAL DASHBOARD PRODUCTIVE-WORK CERTIFICATE
 * VERSION: v1.1.0-P8-LEGAL-DASHBOARD-WORK-COMPLETION-CERT
 * AUTHORITY: Presentation/wiring only.
 * EPITOME: Prove compact daily-work search, server-owned category projection,
 * selected completion intent, EOS readback, and fail-closed presentation.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/legalDashboardProductiveWork.test.jsx
 * COLLABORATION / OWNERSHIP: LegalDashboard presents Python EOS truth; this
 * certificate owns component-level rendering and interaction evidence only.
 * CERTIFICATION / UPDATE DATE: 2026-10-19
 * CHANGELOG: v1.1.0 adds P8 compact queue, filtering, completion submission,
 * denial, authoritative readback, and duplicate-submit prevention evidence.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 controls.
 * SECURITY / PRIVACY POSTURE: Synthetic fixtures only; no credentials or
 * production legal payloads are present.
 * TENANT BOUNDARY: Productive-work transport accepts no tenant/principal input.
 * AUTHORITY BOUNDARY: Presentation evidence only; no IAM, assignment,
 * completion, workflow, legal-event, billing, payment, or settlement truth.
 * FINANCIAL AUTHORITY BOUNDARY: None.
 * FAIL-CLOSED POSTURE: Denial, transport failure, retained active work, and
 * malformed projection never produce a completion-success claim.
 */

import React from 'react';
import '@testing-library/jest-dom/vitest';
import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from '@testing-library/react';
import {
  afterEach,
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from 'vitest';

const mocks = vi.hoisted(() => ({
  getLegalPracticeWorkspace: vi.fn(),
  getLegalConflictScreenings: vi.fn(),
  getLegalProductiveWork: vi.fn(),
  completeLegalWorkItem: vi.fn(),
  getLegalSpecialistWorkflow: vi.fn(),
}));

vi.mock('../../services/legalMatterDeadlineService.js', () => ({
  createLegalMatterDeadline: vi.fn(),
  getLegalMatterDeadlines: vi.fn(),
}));

vi.mock('../../services/legalOperationsService.js', () => ({
  LEGAL_OPERATIONS_CLIENT_VERSION:
    'v2.0.0-LEGAL-EVIDENCE-UPLOAD-BROWSER-TRANSPORT',
  generateLegalReturnOfService: vi.fn(),
  getDeputyFieldCapabilities: vi.fn(),
  getDeputyPersonalActiveWork: vi.fn(),
  getLegalClientMatters: vi.fn(),
  getLegalClientAcceptanceInstruments: vi.fn(),
  createLegalClientAcceptanceContext: vi.fn(),
  getLegalClientAcceptanceContent: vi.fn(),
  confirmLegalClientAcceptance: vi.fn(),
  getLegalConflictScreenings: mocks.getLegalConflictScreenings,
  getLegalFinanceEvidence: vi.fn(),
  getLegalPracticeWorkspace: mocks.getLegalPracticeWorkspace,
  getLegalProductiveWork: mocks.getLegalProductiveWork,
  completeLegalWorkItem: mocks.completeLegalWorkItem,
  getLegalSpecialistWorkflow: mocks.getLegalSpecialistWorkflow,
  getSheriffOperationalQueues: vi.fn(),
  issueLegalConflictReview: vi.fn(),
  recordDeputyFieldOutcome: vi.fn(),
  registerLegalIntake: vi.fn(),
  transitionDeputyFieldAttempt: vi.fn(),
  uploadLegalEvidence: vi.fn(),
}));

vi.mock('../../contexts/authContext', () => ({
  useAuth: () => ({
    user: {
      id: 'principal-law',
      email: 'operator@example.test',
      role: 'tenant_legal_partner',
      tenantId: 'tenant-law',
      permissions: [
        'legal_operations:productive_work:read',
      ],
      legalPermissionsAuthoritative: true,
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
    matters_total: 0,
    matters_open: 0,
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
  matters: [],
  instructions: [],
  documents: [],
  attempts: [],
  executions: [],
  returns: [],
});

const productiveWork = () => ({
  tenantId: 'tenant-law',
  principalId: 'principal-law',
  asOf: '2026-10-16T01:00:00+00:00',
  operatingContexts: [
    {
      operatingRoleId: 'role-corporate',
      operatingRoleRevision: 2,
      displayName: 'Corporate Attorney',
      capabilityIds: ['PRACTICE_CORPORATE'],
      officeReferences: ['office:jhb'],
      practiceReferences: ['practice:corporate'],
      businessUnitReferences: [],
      jurisdictionReferences: ['jurisdiction:ZA'],
    },
  ],
  capabilityIds: ['PRACTICE_CORPORATE'],
  assignedWorkItems: [
    {
      workItemId: 'work-1',
      caseMatterId: 'matter-1',
      title: 'Prepare governed filing',
      sourceKind: 'LEGAL_WORKFLOW_STAGE',
      sourceReference: 'stage:filing',
      status: 'OPEN',
      createdAt: '2026-10-16T00:00:00+00:00',
      dueAt: '2026-10-16T08:00:00+00:00',
    },
  ],
  supervisedWorkItems: [],
  overdueWorkItems: [],
  dueSoonWorkItems: [],
});

describe('PW-P11C canonical Legal dashboard productive work', () => {
  afterEach(() => {
    cleanup();
  });

  beforeEach(() => {
    vi.clearAllMocks();

    mocks.getLegalPracticeWorkspace.mockResolvedValue(
      workspace(),
    );

    mocks.getLegalConflictScreenings.mockResolvedValue({
      schema: 'WILSY-LEGAL-CONFLICT-SCREENING-PRESENTATION/V1',
      version: 'v1.9.0-L8-8N-CONFLICT-SCREENING-READ-API',
      tenantId: 'tenant-law',
      visibility: 'LEGAL_CONFLICT_SCREENING_REVIEW_QUEUE',
      screenings: [],
    });

    mocks.getLegalProductiveWork.mockResolvedValue(
      productiveWork(),
    );
    mocks.getLegalSpecialistWorkflow.mockResolvedValue({
      tenantId: 'tenant-law',
      principalId: 'principal-law',
      asOf: '2026-10-18T10:00:00+00:00',
      rows: [{
        workItemId: 'work-1',
        caseMatterId: 'matter-1',
        workflowInstanceId: 'workflow-1',
        workflowDefinitionId: 'definition-1',
        stageDefinitionId: 'stage-review',
        readiness: 'BLOCKED_DEPENDENCY_AND_GATE',
        blockingDependencyWorkItemIds: ['work-0'],
        unsatisfiedGateReferences: ['PARTNER_REVIEW'],
        materializationTransitionId: 'transition-1',
        materializationReceiptId: 'receipt-1',
      }],
    });
  });


  const openCompactWork = async () => {
    render(<LegalDashboard roleView="LEGAL_PARTNER" />);
    fireEvent.click(await screen.findByRole('button', { name: 'My Work' }));
    await screen.findByText('Prepare governed filing');
    expect(screen.getByRole('region', {
      name: 'Compact legal work queue',
    })).toBeInTheDocument();
  };

  const submitEvidence = async () => {
    fireEvent.click(
      screen.getByRole('button', {
        name: 'Open completion for work-1',
      }),
    );
    expect(screen.getByRole('region', {
      name: 'Selected work completion inspector',
    })).toBeInTheDocument();
    fireEvent.change(
      screen.getByRole('combobox', { name: 'Assigned work to complete' }),
      { target: { value: 'work-1' } },
    );
    fireEvent.change(
      screen.getByRole('textbox', { name: 'Completion evidence reference' }),
      { target: { value: 'evidence:filing-record' } },
    );
    fireEvent.change(
      screen.getByRole('textbox', { name: 'Completion evidence fingerprint' }),
      { target: { value: 'a'.repeat(128) } },
    );
    fireEvent.click(
      screen.getByRole('button', {
        name: 'Confirm legal work completion',
      }),
    );
  };

  it('searches the compact queue without changing authoritative work', async () => {
    await openCompactWork();
    const search = screen.getByRole('searchbox', {
      name: 'Search legal work',
    });
    fireEvent.change(search, { target: { value: 'absent-matter' } });
    expect(screen.getByText('No matching work in this category.'))
      .toBeInTheDocument();
    fireEvent.change(search, { target: { value: 'matter-1' } });
    expect(screen.getByText('Prepare governed filing'))
      .toBeInTheDocument();
    expect(mocks.getLegalProductiveWork).toHaveBeenCalledTimes(1);
  });

  it('switches workload categories without manufacturing assignments', async () => {
    await openCompactWork();
    const category = screen.getByRole('combobox', {
      name: 'Work queue category',
    });
    fireEvent.change(category, { target: { value: 'overdue' } });
    expect(screen.getByText(
      'No server-classified overdue work is currently projected.',
    )).toBeInTheDocument();
    expect(screen.queryByText('Prepare governed filing'))
      .not.toBeInTheDocument();
    fireEvent.change(category, { target: { value: 'assigned' } });
    expect(screen.getByText('Prepare governed filing'))
      .toBeInTheDocument();
    expect(mocks.getLegalProductiveWork).toHaveBeenCalledTimes(1);
  });

  it('confirms completion only after successful EOS readback', async () => {
    mocks.completeLegalWorkItem.mockResolvedValue({
      work_item_id: 'work-1',
    });
    mocks.getLegalProductiveWork
      .mockResolvedValueOnce(productiveWork())
      .mockResolvedValueOnce({
        ...productiveWork(),
        assignedWorkItems: [],
        dueSoonWorkItems: [],
      });

    await openCompactWork();
    await submitEvidence();

    await waitFor(() => {
      expect(mocks.completeLegalWorkItem).toHaveBeenCalledWith({
        workItemId: 'work-1',
        completionEvidenceReference: 'evidence:filing-record',
        completionEvidenceFingerprint: 'a'.repeat(128),
      });
    });

    expect(await screen.findByText(
      'Completion confirmed by EOS and active work refreshed.',
    )).toBeInTheDocument();
    expect(mocks.getLegalProductiveWork).toHaveBeenCalledTimes(2);
    expect(screen.queryByText('Prepare governed filing'))
      .not.toBeInTheDocument();
  });

  it('preserves 403 denial without a false completion claim', async () => {
    mocks.completeLegalWorkItem.mockRejectedValue({
      response: { status: 403 },
    });
    await openCompactWork();
    await submitEvidence();

    expect(await screen.findByText(
      'Current tenant authority does not permit this completion.',
    )).toBeInTheDocument();
    expect(mocks.getLegalProductiveWork).toHaveBeenCalledTimes(1);
    expect(screen.getByText('Prepare governed filing'))
      .toBeInTheDocument();
  });

  it('fails closed when authoritative readback retains the work', async () => {
    mocks.completeLegalWorkItem.mockResolvedValue({
      work_item_id: 'work-1',
    });
    await openCompactWork();
    await submitEvidence();

    expect(await screen.findByText(
      'Completion or authoritative readback could not be confirmed.',
    )).toBeInTheDocument();
    expect(mocks.getLegalProductiveWork).toHaveBeenCalledTimes(2);
    expect(screen.getByText('Prepare governed filing'))
      .toBeInTheDocument();
    expect(screen.queryByText(
      'Completion confirmed by EOS and active work refreshed.',
    )).not.toBeInTheDocument();
  });

  it('prevents a second submission while EOS completion is pending', async () => {
    let release;
    mocks.completeLegalWorkItem.mockImplementation(() => new Promise(
      (resolve) => { release = resolve; },
    ));
    await openCompactWork();
    await submitEvidence();

    await waitFor(() => {
      expect(mocks.completeLegalWorkItem).toHaveBeenCalledTimes(1);
    });
    expect(screen.getByRole('button', {
      name: 'Confirming with EOS…',
    })).toBeDisabled();

    release({ work_item_id: 'work-1' });
    expect(await screen.findByText(
      'Completion or authoritative readback could not be confirmed.',
    )).toBeInTheDocument();
    expect(mocks.completeLegalWorkItem).toHaveBeenCalledTimes(1);
  });


  it('keeps productive-work transport closed until My Work is opened', async () => {
    render(
      <LegalDashboard roleView="LEGAL_PARTNER" />,
    );

    const button = await screen.findByRole(
      'button',
      {
        name: 'My Work',
      },
    );

    expect(
      mocks.getLegalProductiveWork,
    ).not.toHaveBeenCalled();

    fireEvent.click(button);

    await waitFor(() => {
      expect(
        mocks.getLegalProductiveWork,
      ).toHaveBeenCalledTimes(1);
    });

    expect(
      await screen.findByRole(
        'heading',
        {
          name: 'My productive work',
        },
      ),
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        'Prepare governed filing',
      ),
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        'Corporate Attorney',
      ),
    ).toBeInTheDocument();
  });

  it('renders responsive non-overflow layout primitives for daily work', async () => {
    render(
      <LegalDashboard roleView="LEGAL_PARTNER" />,
    );

    fireEvent.click(
      await screen.findByRole(
        'button',
        {
          name: 'My Work',
        },
      ),
    );

    const surface = await screen.findByRole(
      'heading',
      {
        name: 'My productive work',
      },
    );

    const container = surface.closest(
      '[data-legal-productive-work="true"]',
    );

    expect(container).not.toBeNull();

    expect(
      container.querySelector(
        '[data-legal-workstation="compact"]',
      ),
    ).not.toBeNull();

    expect(
      container.querySelector(
        '.min-w-0',
      ),
    ).not.toBeNull();
  });

  it('enriches only an already-visible productive-work row', async () => {
    render(<LegalDashboard roleView="LEGAL_PARTNER" />);
    fireEvent.click(await screen.findByRole('button', { name: 'My Work' }));

    expect(await screen.findByText('Workflow: stage-review')).toBeInTheDocument();
    expect(screen.getByText('Blocked by dependency and gate')).toBeInTheDocument();
    expect(screen.getByText(/Dependencies: work-0/)).toBeInTheDocument();
    expect(screen.getByText(/Unsatisfied gates: PARTNER_REVIEW/)).toBeInTheDocument();
    expect(screen.getByText(/explanatory readiness/i)).toBeInTheDocument();
  });

  it('does not manufacture a row from unmatched specialist evidence', async () => {
    mocks.getLegalSpecialistWorkflow.mockResolvedValueOnce({
      tenantId: 'tenant-law',
      principalId: 'principal-law',
      asOf: '2026-10-18T10:00:00+00:00',
      rows: [{
        workItemId: 'invisible-work',
        caseMatterId: 'matter-hidden',
        readiness: 'ACTIONABLE',
        blockingDependencyWorkItemIds: [],
        unsatisfiedGateReferences: [],
      }],
    });

    render(<LegalDashboard roleView="LEGAL_PARTNER" />);
    fireEvent.click(await screen.findByRole('button', { name: 'My Work' }));

    expect(await screen.findByText('Prepare governed filing')).toBeInTheDocument();
    expect(screen.queryByText('invisible-work')).not.toBeInTheDocument();
    expect(screen.queryByText('matter-hidden')).not.toBeInTheDocument();
  });

  it('keeps productive work visible when specialist enrichment is unavailable', async () => {
    mocks.getLegalSpecialistWorkflow.mockRejectedValueOnce(new Error('offline'));

    render(<LegalDashboard roleView="LEGAL_PARTNER" />);
    fireEvent.click(await screen.findByRole('button', { name: 'My Work' }));

    expect(await screen.findByText('Prepare governed filing')).toBeInTheDocument();
    expect(screen.getByRole('status', { name: 'Workflow enrichment unavailable' }))
      .toHaveTextContent('Productive work remains available');
  });

  it('does not expose My Work when authoritative permissions omit productive-work read', async () => {
    const auth = await import(
      '../../contexts/authContext'
    );

    expect(auth).toBeDefined();

    render(
      <LegalDashboard
        roleView="LEGAL_SECRETARY"
        user={{
          id: 'principal-secretary',
          role: 'LEGAL_SECRETARY',
          permissions: [],
          legalPermissionsAuthoritative: true,
        }}
      />,
    );

    await screen.findByText(
      'Legal Operations Command Center',
    );

    expect(
      screen.queryByRole(
        'button',
        {
          name: 'My Work',
        },
      ),
    ).not.toBeInTheDocument();

    expect(
      mocks.getLegalProductiveWork,
    ).not.toHaveBeenCalled();
  });
});

/**
 * ARTIFACT: legalDashboardProductiveWork.test.jsx
 * VERSION: v1.1.0-P8-LEGAL-DASHBOARD-WORK-COMPLETION-CERT
 * AUTHORITY BOUNDARY: presentation only; Python EOS remains sovereign
 * MOBILE POSTURE: adaptive grid/min-width certificate only; live browser follows
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
