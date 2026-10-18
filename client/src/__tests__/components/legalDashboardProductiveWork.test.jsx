/**
 * WILSY OS — PW-P11C LEGAL DASHBOARD PRODUCTIVE-WORK CERTIFICATE
 * VERSION: v1.0.0-PW-P11C-LEGAL-DASHBOARD-PRODUCTIVE-WORK-CERT
 * AUTHORITY: Presentation/wiring only.
 * TENANT BOUNDARY: Productive-work transport accepts no tenant/principal input.
 * FINANCIAL AUTHORITY BOUNDARY: None.
 */

import React from 'react';
import {
  fireEvent,
  render,
  screen,
  waitFor,
} from '@testing-library/react';
import {
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
        '.xl\\:grid-cols-2',
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
 * VERSION: v1.0.0-PW-P11C-LEGAL-DASHBOARD-PRODUCTIVE-WORK-CERT
 * AUTHORITY BOUNDARY: presentation only; Python EOS remains sovereign
 * MOBILE POSTURE: adaptive grid/min-width certificate only; live browser follows
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
