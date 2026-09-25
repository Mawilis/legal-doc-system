/**
 * WILSY OS — PRODUCTION LEGAL OPERATIONS WORKSPACE CERTIFICATE
 * VERSION: v1.5.0-L8-8M-R2-CONFLICT-REVIEW-COCKPIT-CERT
 * AUTHORITY: Browser presentation/wiring certificate only.
 * EPITOME: Proves law-firm and finance roles resolve to real WILSY Legal OS
 *          workspaces backed by the D15 V2 first-class matter contract, with
 *          functional lifecycle navigation, governed intake, ReturnOfService generation, exact
 *          finance lookup and no cross-role endpoint fallback.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/legalDashboardPracticeWorkspace.test.jsx
 * CERTIFICATION / UPDATE DATE: 2026-09-24
 * CHANGELOG: 2026-09-25 v1.5.0-L8-8M-R2-CONFLICT-REVIEW-COCKPIT-CERT certifies canonical conflict-screening queue loading, REVIEW_REQUIRED-only presentation, bounded four-field human review submission, stable browser review identity, in-flight duplicate blocking, canonical refresh and bounded HTTP failure preservation. No browser authority is widened.
 *            2026-09-24 v1.4.0-L8-7D18-LEGAL-AUTHORITY-POSTURE-CERT certifies the D18 visible authority-posture surface: server-authoritative projections, compatibility role baselines and legacy narrowing hints are labeled distinctly; effective lanes match the already-certified presentation gates; explanatory posture cannot widen commands or create Legal/financial authority.
 *            2026-09-24 v1.3.0-L8-7D17-SERVER-BOUND-LEGAL-PERMISSION-PRESENTATION-CERT certifies D17 server-bound permission provenance in the Legal Command Center: an authoritative empty Legal permission projection removes Partner intake/return/finance affordances while retaining read-only workspace visibility, and authoritative-empty LEGAL_FINANCE performs no finance evidence transport. Absent server provenance still preserves the D16 role baseline.
 *            2026-09-24 v1.2.0-L8-7D16-PERMISSION-AWARE-LEGAL-COMMAND-CENTER-CERT certifies permission-aware narrowing for Legal Practice/Finance presentation: explicit legal permission hints can remove intake, ReturnOfService and finance affordances but cannot widen the canonical role envelope; absent legal permission hints preserve the certified role baseline.
 *            2026-09-24 v1.1.0-L8-7D15-FIRST-CLASS-MATTER-OPERATING-ROOM-CERT binds the production dashboard to the D15 V2 workspace, proves canonical matter rendering/search/drilldown, linked lifecycle operating-room composition, and post-intake navigation to the refreshed persisted matter without adding browser authority.
 *            2026-09-24 v1.0.1-L8-7D14-PRODUCTION-LEGAL-OPERATIONS-WORKSPACE-CERT rebinds the D14 dashboard certificate to
 *            v1.5.1-L8-7D14-WORKSPACE-SUMMARY-VALIDATION; workspace behavior and authority are unchanged.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only.
 * TENANT BOUNDARY: Every rendered data packet is a pre-authorized adapter result;
 *                  tests prove no browser tenant/principal/role command fields.
 * AUTHORITY BOUNDARY: Presentation/command wiring only; Python EOS owns legal truth.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution/settlement.
 * FAIL-CLOSED DECLARATION: Denial, mutation failure or cross-role drift never
 *                          creates fallback data or synthetic success.
 */

import React from 'react';
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const {
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

vi.mock('../../services/legalOperationsService.js', () => ({
  LEGAL_OPERATIONS_CLIENT_VERSION: 'v1.6.0-L8-7D15-MATTER-WORKSPACE-COMPATIBILITY',
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

const EVIDENCE_A = 'a'.repeat(128);
const EVIDENCE_B = 'b'.repeat(128);
const EVIDENCE_C = 'c'.repeat(128);
const EVIDENCE_D = 'd'.repeat(128);
const EVIDENCE_E = 'e'.repeat(128);

const practiceWorkspace = ({ withReturn = false, withNewMatter = false } = {}) => ({
  schema: 'WILSY-LEGAL-OPERATIONS-PRACTICE-WORKSPACE/V2',
  version: 'v1.8.0-L8-7D15-FIRST-CLASS-MATTER-WORKSPACE-API',
  tenantId: 'tenant-law',
  visibility: 'LEGAL_PRACTICE_WORKSPACE',
  summary: {
    matters_total: withNewMatter ? 3 : 2,
    matters_open: withNewMatter ? 2 : 1,
    matters_closed: 1,
    instructions_total: withNewMatter ? 3 : 2,
    instructions_registered: withNewMatter ? 2 : 1,
    instructions_accepted: 1,
    instructions_closed: 0,
    instructions_cancelled: 0,
    documents_total: withNewMatter ? 3 : 2,
    documents_registered: withNewMatter ? 1 : 0,
    documents_received: 1,
    documents_allocated: 1,
    documents_returned: 0,
    attempts_total: 1,
    attempts_allocated: 0,
    attempts_attempted: 1,
    attempts_completed: 0,
    attempts_not_completed: 0,
    attempts_cancelled: 0,
    executions_total: 1,
    executions_completed: 1,
    executions_not_completed: 0,
    returns_total: withReturn ? 1 : 0,
  },
  matters: [
    {
      case_matter_id: 'matter-001',
      matter_reference: 'CASE-2026-0001',
      opened_at: '2026-09-23T16:55:00+00:00',
      state: 'OPEN',
      evidence_identity: EVIDENCE_A,
    },
    {
      case_matter_id: 'matter-002',
      matter_reference: 'CASE-2026-0002',
      opened_at: '2026-09-23T17:00:00+00:00',
      state: 'CLOSED',
      evidence_identity: EVIDENCE_B,
    },
    ...(withNewMatter ? [{
      case_matter_id: 'matter-created-9001',
      matter_reference: 'CASE-2026-9001',
      opened_at: '2026-09-24T05:00:00+00:00',
      state: 'OPEN',
      evidence_identity: EVIDENCE_C,
    }] : []),
  ],
  instructions: [
    {
      instruction_id: 'instruction-001',
      case_matter_id: 'matter-001',
      document_id: 'document-001',
      registered_at: '2026-09-23T17:00:00+00:00',
      state: 'REGISTERED',
      evidence_identity: EVIDENCE_A,
    },
    {
      instruction_id: 'instruction-002',
      case_matter_id: 'matter-002',
      document_id: 'document-002',
      registered_at: '2026-09-23T17:05:00+00:00',
      state: 'ACCEPTED',
      evidence_identity: EVIDENCE_B,
    },
    ...(withNewMatter ? [{
      instruction_id: 'instruction-created-9001',
      case_matter_id: 'matter-created-9001',
      document_id: 'document-created-9001',
      registered_at: '2026-09-24T05:01:00+00:00',
      state: 'REGISTERED',
      evidence_identity: EVIDENCE_D,
    }] : []),
  ],
  documents: [
    {
      document_id: 'document-001',
      case_matter_id: 'matter-001',
      document_type: 'summons',
      registered_at: '2026-09-23T17:01:00+00:00',
      state: 'RECEIVED',
      evidence_identity: EVIDENCE_B,
    },
    {
      document_id: 'document-002',
      case_matter_id: 'matter-002',
      document_type: 'notice',
      registered_at: '2026-09-23T17:06:00+00:00',
      state: 'ALLOCATED_TO_DEPUTY',
      evidence_identity: EVIDENCE_C,
    },
    ...(withNewMatter ? [{
      document_id: 'document-created-9001',
      case_matter_id: 'matter-created-9001',
      document_type: 'summons',
      registered_at: '2026-09-24T05:02:00+00:00',
      state: 'REGISTERED',
      evidence_identity: EVIDENCE_E,
    }] : []),
  ],
  attempts: [
    {
      attempt_id: 'attempt-001',
      instruction_id: 'instruction-002',
      document_id: 'document-002',
      deputy_id: 'deputy-001',
      allocated_at: '2026-09-23T17:10:00+00:00',
      state: 'ATTEMPTED',
      evidence_identity: EVIDENCE_D,
    },
  ],
  executions: [
    {
      service_execution_id: 'execution-001',
      attempt_id: 'attempt-001',
      instruction_id: 'instruction-002',
      document_id: 'document-002',
      outcome: 'COMPLETED',
      executed_at: '2026-09-23T17:20:00+00:00',
      evidence_identity: EVIDENCE_E,
    },
  ],
  returns: withReturn
    ? [
      {
        return_id: 'return-001',
        instruction_id: 'instruction-002',
        document_id: 'document-002',
        attempt_id: 'attempt-001',
        service_execution_id: 'execution-001',
        service_outcome: 'COMPLETED',
        generated_at: '2026-09-23T17:30:00+00:00',
        state: 'GENERATED',
        evidence_identity: EVIDENCE_A,
      },
    ]
    : [],
});

const conflictScreeningQueue = ({ status = 'REVIEW_REQUIRED' } = {}) => ({
  schema: 'WILSY-LEGAL-CONFLICT-SCREENING-PRESENTATION/V1',
  version: 'v1.9.0-L8-8N-CONFLICT-SCREENING-READ-API',
  tenantId: 'tenant-law',
  visibility: 'LEGAL_CONFLICT_SCREENING_REVIEW_QUEUE',
  screenings: status
    ? [{
      screeningId: 'screening-001',
      sourceCaseMatterId: 'CASE-2026-0001',
      status,
      screenedAt: '2026-09-25T08:30:00Z',
    }]
    : [],
});

const conflictReviewReceipt = (outcome = 'ESCALATION_REQUIRED') => ({
  reviewId: 'review-accepted',
  screeningId: 'screening-001',
  outcome,
  reviewedAt: '2026-09-25T08:31:00Z',
  fingerprint: EVIDENCE_A,
});

describe('D15 first-class Legal Matter Operating Room', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getLegalConflictScreenings.mockResolvedValue({
      schema: 'WILSY-LEGAL-CONFLICT-SCREENING-PRESENTATION/V1',
      version: 'v1.9.0-L8-8N-CONFLICT-SCREENING-READ-API',
      tenantId: 'tenant-law',
      visibility: 'LEGAL_CONFLICT_SCREENING_REVIEW_QUEUE',
      screenings: [],
    });
  });

  it('renders a full law-firm operating workspace instead of a matter list', async () => {
    getLegalPracticeWorkspace.mockResolvedValueOnce(practiceWorkspace());

    const { container } = render(
      <LegalDashboard
        roleView="LEGAL_PARTNER"
        user={{ id: 'principal-law', email: 'partner@example.test' }}
        tenantConfig={{ tenantId: 'tenant-law', displayName: 'WILSY Legal Practice' }}
      />,
    );

    await waitFor(() => {
      expect(getLegalPracticeWorkspace).toHaveBeenCalledTimes(1);
    });
    expect(getSheriffOperationalQueues).not.toHaveBeenCalled();
    expect(getDeputyPersonalActiveWork).not.toHaveBeenCalled();
    expect(getLegalClientMatters).not.toHaveBeenCalled();

    expect(
      container.querySelector('[data-wilsy-dashboard-key="legal-practice"]'),
    ).not.toBeNull();
    expect(screen.getByText('Legal Operations Command Center')).toBeInTheDocument();

    for (const menu of [
      'Command Center',
      'Matters',
      'Instructions',
      'Process Documents',
      'Service Operations',
      'Returns of Service',
      'Finance Evidence',
      'New Instruction',
    ]) {
      expect(screen.getByRole('button', { name: menu })).toBeInTheDocument();
    }

    expect(screen.getAllByText('CASE-2026-0001').length).toBeGreaterThan(0);
    expect(screen.getByText('matter-001')).toBeInTheDocument();
    expect(screen.getByText('attempt-001')).toBeInTheDocument();
    expect(screen.getAllByText('Active instructions').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Returns generated').length).toBeGreaterThan(0);
  });

  it('searches first-class matters and opens one canonical Matter Operating Room', async () => {
    getLegalPracticeWorkspace.mockResolvedValueOnce(practiceWorkspace());
    render(<LegalDashboard roleView="LEGAL_ATTORNEY" />);

    await screen.findByText('Legal Operations Command Center');
    const search = screen.getByPlaceholderText('Search matter reference, ID or linked legal work');
    fireEvent.change(search, { target: { value: 'CASE-2026-0001' } });

    expect(screen.getByRole('heading', { name: 'Matters' })).toBeInTheDocument();
    expect(screen.getByText('CASE-2026-0001')).toBeInTheDocument();
    expect(screen.queryByText('CASE-2026-0002')).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Open matter' }));

    expect(screen.getByLabelText('Matter Operating Room')).toBeInTheDocument();
    expect(screen.getByText('instruction-001')).toBeInTheDocument();
    expect(screen.getByText('document-001')).toBeInTheDocument();
    expect(screen.getAllByText(EVIDENCE_A).length).toBeGreaterThan(0);
    expect(getLegalPracticeWorkspace).toHaveBeenCalledTimes(1);
  });

  it('switches across real lifecycle modules without new network scope', async () => {
    getLegalPracticeWorkspace.mockResolvedValueOnce(practiceWorkspace());
    render(<LegalDashboard roleView="LEGAL_ATTORNEY" />);

    await screen.findByText('Legal Operations Command Center');

    fireEvent.click(screen.getByRole('button', { name: 'Instructions' }));
    expect(screen.getByText('Legal instructions')).toBeInTheDocument();
    expect(screen.getByText('instruction-001')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Process Documents' }));
    expect(screen.getByRole('heading', { name: 'Process documents' })).toBeInTheDocument();
    expect(screen.getByText('document-001')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Service Operations' }));
    expect(screen.getByText('Service attempts')).toBeInTheDocument();
    expect(screen.getByText('Certified service executions')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Returns of Service' }));
    expect(screen.getAllByText('Returns of Service').length).toBeGreaterThan(1);

    expect(getLegalPracticeWorkspace).toHaveBeenCalledTimes(1);
  });

  it('registers governed intake and refreshes canonical workspace before success', async () => {
    getLegalPracticeWorkspace.mockResolvedValueOnce(practiceWorkspace());
    registerLegalIntake.mockImplementationOnce(async (submitted) => {
      const refreshed = practiceWorkspace({ withNewMatter: true });
      refreshed.matters[2].case_matter_id = submitted.caseMatterId;
      refreshed.instructions[2].case_matter_id = submitted.caseMatterId;
      refreshed.documents[2].case_matter_id = submitted.caseMatterId;
      refreshed.instructions[2].instruction_id = submitted.instructionId;
      refreshed.instructions[2].document_id = submitted.documentId;
      refreshed.documents[2].document_id = submitted.documentId;
      getLegalPracticeWorkspace.mockResolvedValueOnce(refreshed);
      return {
        disposition: 'CREATED',
        tenantId: 'tenant-law',
      };
    });

    render(<LegalDashboard roleView="LEGAL_PARALEGAL" />);
    await screen.findByText('Legal Operations Command Center');

    fireEvent.click(screen.getByRole('button', { name: 'New Instruction' }));

    fireEvent.change(screen.getByLabelText('Matter reference'), {
      target: { value: 'CASE-2026-9001' },
    });
    fireEvent.change(screen.getByLabelText('Process document type'), {
      target: { value: 'summons' },
    });
    fireEvent.change(screen.getByLabelText('Matter evidence reference'), {
      target: { value: 'matter-proof-9001' },
    });
    fireEvent.change(screen.getByLabelText('Instruction evidence reference'), {
      target: { value: 'instruction-proof-9001' },
    });
    fireEvent.change(
      screen.getByLabelText('Document registration evidence reference'),
      { target: { value: 'document-proof-9001' } },
    );

    fireEvent.click(screen.getByRole('button', { name: 'Register instruction' }));

    await waitFor(() => {
      expect(registerLegalIntake).toHaveBeenCalledTimes(1);
      expect(getLegalPracticeWorkspace).toHaveBeenCalledTimes(2);
    });

    const submitted = registerLegalIntake.mock.calls[0][0];
    expect(submitted).toEqual(expect.objectContaining({
      matterReference: 'CASE-2026-9001',
      documentType: 'summons',
      matterEvidenceReference: 'matter-proof-9001',
      instructionEvidenceReference: 'instruction-proof-9001',
      documentRegistrationEvidenceReference: 'document-proof-9001',
      caseMatterId: expect.stringMatching(/^matter-/),
      instructionId: expect.stringMatching(/^instruction-/),
      documentId: expect.stringMatching(/^document-/),
      registrationCustodyEventId: expect.stringMatching(/^custody-/),
    }));
    expect(submitted).not.toHaveProperty('tenantId');
    expect(submitted).not.toHaveProperty('principalId');
    expect(submitted).not.toHaveProperty('role');

    expect(await screen.findByRole('heading', { name: 'Matters' })).toBeInTheDocument();
    const operatingRoom = screen.getByLabelText('Matter Operating Room');
    expect(operatingRoom).toBeInTheDocument();
    expect(within(operatingRoom).getByText('CASE-2026-9001')).toBeInTheDocument();
    expect(within(operatingRoom).getByText(submitted.caseMatterId)).toBeInTheDocument();
  });

  it('does not present intake success when canonical refresh cannot rediscover the new matter', async () => {
    getLegalPracticeWorkspace
      .mockResolvedValueOnce(practiceWorkspace())
      .mockResolvedValueOnce(practiceWorkspace());
    registerLegalIntake.mockResolvedValueOnce({
      disposition: 'CREATED',
      tenantId: 'tenant-law',
    });

    render(<LegalDashboard roleView="LEGAL_PARALEGAL" />);
    await screen.findByText('Legal Operations Command Center');
    fireEvent.click(screen.getByRole('button', { name: 'New Instruction' }));

    fireEvent.change(screen.getByLabelText('Matter reference'), {
      target: { value: 'CASE-2026-NOT-REDISCOVERED' },
    });
    fireEvent.change(screen.getByLabelText('Process document type'), {
      target: { value: 'summons' },
    });
    fireEvent.change(screen.getByLabelText('Matter evidence reference'), {
      target: { value: 'matter-proof-missing' },
    });
    fireEvent.change(screen.getByLabelText('Instruction evidence reference'), {
      target: { value: 'instruction-proof-missing' },
    });
    fireEvent.change(
      screen.getByLabelText('Document registration evidence reference'),
      { target: { value: 'document-proof-missing' } },
    );

    fireEvent.click(screen.getByRole('button', { name: 'Register instruction' }));

    expect(
      await screen.findByText('LEGAL_OPERATIONS_INTAKE_REFRESH_MATTER_NOT_FOUND'),
    ).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'New instruction / intake' })).toBeInTheDocument();
    expect(screen.queryByLabelText('Matter Operating Room')).not.toBeInTheDocument();
    expect(getLegalPracticeWorkspace).toHaveBeenCalledTimes(2);
  });

  it('keeps secretary intake read-only while retaining operational visibility', async () => {
    getLegalPracticeWorkspace.mockResolvedValueOnce(practiceWorkspace());

    render(<LegalDashboard roleView="LEGAL_SECRETARY" />);

    await screen.findByText('Legal Operations Command Center');
    expect(screen.queryByRole('button', { name: 'New Instruction' })).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Instructions' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Service Operations' })).toBeInTheDocument();
    expect(registerLegalIntake).not.toHaveBeenCalled();
  });

  it('generates ReturnOfService from the exact certified execution locator then refreshes', async () => {
    getLegalPracticeWorkspace
      .mockResolvedValueOnce(practiceWorkspace())
      .mockResolvedValueOnce(practiceWorkspace({ withReturn: true }));
    generateLegalReturnOfService.mockResolvedValueOnce({
      tenantId: 'tenant-law',
      returnId: 'return-generated',
      serviceExecutionId: 'execution-001',
      serviceOutcome: 'COMPLETED',
      state: 'GENERATED',
    });

    render(<LegalDashboard roleView="LEGAL_ATTORNEY" />);
    await screen.findByText('Legal Operations Command Center');

    fireEvent.click(screen.getByRole('button', { name: 'Service Operations' }));
    fireEvent.click(screen.getByRole('button', { name: 'Generate return' }));

    await waitFor(() => {
      expect(generateLegalReturnOfService).toHaveBeenCalledTimes(1);
      expect(getLegalPracticeWorkspace).toHaveBeenCalledTimes(2);
    });
    expect(generateLegalReturnOfService).toHaveBeenCalledWith(
      expect.objectContaining({
        executionId: 'execution-001',
        executionEvidenceIdentity: EVIDENCE_E,
        returnId: expect.stringMatching(/^return-/),
        generatedAt: expect.stringMatching(/Z$/),
      }),
    );
    expect(generateLegalReturnOfService.mock.calls[0][0]).not.toHaveProperty('tenantId');
  });

  it('shows compatibility role-baseline provenance when no explicit Legal permissions exist', async () => {
    getLegalPracticeWorkspace.mockResolvedValueOnce(practiceWorkspace());

    render(
      <LegalDashboard
        roleView="LEGAL_PARTNER"
        user={{ id: 'principal-partner-baseline' }}
      />,
    );

    await screen.findByText('Legal Operations Command Center');
    const posture = screen.getByLabelText('Legal presentation authority posture');
    expect(within(posture).getByText('Role baseline compatibility')).toBeInTheDocument();
    expect(within(posture).getByText('LEGAL_PARTNER')).toBeInTheDocument();
    expect(within(posture).getByText(
      'Intake · Return generation · Billing evidence · Invoice evidence',
    )).toBeInTheDocument();
    expect(within(posture).getByText(/Python EOS re-authorizes every Legal Operations request/i)).toBeInTheDocument();
  });

  it('shows legacy narrowing provenance without presenting it as server authority', async () => {
    getLegalPracticeWorkspace.mockResolvedValueOnce(practiceWorkspace());

    render(
      <LegalDashboard
        roleView="LEGAL_ATTORNEY"
        user={{
          id: 'principal-attorney-legacy-narrow',
          permissions: ['legal_operations:instruction:write'],
        }}
      />,
    );

    await screen.findByText('Legal Operations Command Center');
    const posture = screen.getByLabelText('Legal presentation authority posture');
    expect(within(posture).getByText('Legacy narrowing hints')).toBeInTheDocument();
    expect(within(posture).getByText('Intake')).toBeInTheDocument();
    expect(within(posture).queryByText(/Return generation/)).not.toBeInTheDocument();
    expect(within(posture).queryByText(/Billing evidence/)).not.toBeInTheDocument();
  });

  it('narrows a Partner to explicit invoice-read presentation without widening browser authority', async () => {
    getLegalPracticeWorkspace.mockResolvedValueOnce(practiceWorkspace());

    render(
      <LegalDashboard
        roleView="LEGAL_PARTNER"
        user={{
          id: 'principal-partner-narrow',
          permissions: ['legal_operations:invoice:read'],
        }}
      />,
    );

    await screen.findByText('Legal Operations Command Center');

    expect(screen.queryByRole('button', { name: 'New Instruction' })).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Finance Evidence' })).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Service Operations' }));
    expect(screen.queryByRole('button', { name: 'Generate return' })).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Finance Evidence' }));
    const evidenceType = screen.getByLabelText('Finance evidence type');
    expect(within(evidenceType).getByRole('option', { name: 'Client invoice' })).toBeInTheDocument();
    expect(within(evidenceType).queryByRole('option', { name: 'Tariff assessment' })).not.toBeInTheDocument();
    expect(within(evidenceType).queryByRole('option', { name: 'Billing eligibility' })).not.toBeInTheDocument();
  });

  it('allows explicit instruction-write to retain intake while removing unrelated practice affordances', async () => {
    getLegalPracticeWorkspace.mockResolvedValueOnce(practiceWorkspace());

    render(
      <LegalDashboard
        roleView="LEGAL_ATTORNEY"
        user={{
          id: 'principal-attorney-intake-only',
          permissions: ['legal_operations:instruction:write'],
        }}
      />,
    );

    await screen.findByText('Legal Operations Command Center');

    expect(screen.getByRole('button', { name: 'New Instruction' })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Finance Evidence' })).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Service Operations' }));
    expect(screen.queryByRole('button', { name: 'Generate return' })).not.toBeInTheDocument();
  });

  it('treats a server-authoritative empty Partner permission set as least-authority presentation', async () => {
    getLegalPracticeWorkspace.mockResolvedValueOnce(practiceWorkspace());

    render(
      <LegalDashboard
        roleView="LEGAL_PARTNER"
        user={{
          id: 'principal-partner-authoritative-empty',
          permissions: [],
          legalPermissionsAuthoritative: true,
        }}
      />,
    );

    await screen.findByText('Legal Operations Command Center');

    const posture = screen.getByLabelText('Legal presentation authority posture');
    expect(within(posture).getByText('Server permission projection')).toBeInTheDocument();
    expect(within(posture).getByText('LEGAL_PARTNER')).toBeInTheDocument();
    expect(within(posture).getByText('Read-only')).toBeInTheDocument();

    expect(screen.getByRole('button', { name: 'Matters' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Instructions' })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'New Instruction' })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Finance Evidence' })).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Service Operations' }));
    expect(screen.queryByRole('button', { name: 'Generate return' })).not.toBeInTheDocument();

    expect(registerLegalIntake).not.toHaveBeenCalled();
    expect(generateLegalReturnOfService).not.toHaveBeenCalled();
    expect(getLegalFinanceEvidence).not.toHaveBeenCalled();
  });

  it('keeps authoritative-empty LEGAL_FINANCE locked without finance evidence transport', async () => {
    render(
      <LegalDashboard
        roleView="LEGAL_FINANCE"
        user={{
          id: 'principal-finance-authoritative-empty',
          permissions: [],
          legalPermissionsAuthoritative: true,
        }}
        tenantConfig={{ tenantId: 'tenant-law' }}
      />,
    );

    expect(await screen.findByText('Legal Finance Evidence')).toBeInTheDocument();
    const posture = screen.getByLabelText('Legal presentation authority posture');
    expect(within(posture).getByText('Server permission projection')).toBeInTheDocument();
    expect(within(posture).getByText('LEGAL_FINANCE')).toBeInTheDocument();
    expect(within(posture).getByText('Read-only')).toBeInTheDocument();
    expect(
      screen.getByText('Finance evidence is read-only for this permission posture'),
    ).toBeInTheDocument();
    expect(screen.queryByLabelText('Finance evidence type')).not.toBeInTheDocument();
    expect(screen.queryByLabelText('Finance evidence identity')).not.toBeInTheDocument();
    expect(getLegalFinanceEvidence).not.toHaveBeenCalled();
    expect(getLegalPracticeWorkspace).not.toHaveBeenCalled();
    expect(getLegalClientMatters).not.toHaveBeenCalled();
    expect(getSheriffOperationalQueues).not.toHaveBeenCalled();
    expect(getDeputyPersonalActiveWork).not.toHaveBeenCalled();
  });

  it('never lets a Secretary self-elevate with browser permission claims outside the role envelope', async () => {
    getLegalPracticeWorkspace.mockResolvedValueOnce(practiceWorkspace());

    render(
      <LegalDashboard
        roleView="LEGAL_SECRETARY"
        user={{
          id: 'principal-secretary-no-escalation',
          permissions: [
            'legal_operations:instruction:write',
            'legal_operations:billing:read',
          ],
        }}
      />,
    );

    await screen.findByText('Legal Operations Command Center');

    expect(screen.queryByRole('button', { name: 'New Instruction' })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Finance Evidence' })).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Service Operations' }));
    expect(screen.queryByRole('button', { name: 'Generate return' })).not.toBeInTheDocument();
    expect(registerLegalIntake).not.toHaveBeenCalled();
    expect(getLegalFinanceEvidence).not.toHaveBeenCalled();
    expect(generateLegalReturnOfService).not.toHaveBeenCalled();
  });

  it('narrows LEGAL_FINANCE to invoice-only when explicit legal permissions say so', async () => {
    getLegalFinanceEvidence.mockResolvedValueOnce({
      tenantId: 'tenant-law',
      entityType: 'ClientInvoice',
      entityIdentity: 'invoice-002',
      visibility: 'FINANCE_VISIBLE',
      data: { invoice_id: 'invoice-002', state: 'ISSUED' },
    });

    render(
      <LegalDashboard
        roleView="LEGAL_FINANCE"
        user={{
          id: 'principal-finance-invoice-only',
          permissions: ['legal_operations:invoice:read'],
        }}
        tenantConfig={{ tenantId: 'tenant-law' }}
      />,
    );

    expect(await screen.findByText('Legal Finance Evidence')).toBeInTheDocument();

    const evidenceType = screen.getByLabelText('Finance evidence type');
    expect(within(evidenceType).getByRole('option', { name: 'Client invoice' })).toBeInTheDocument();
    expect(within(evidenceType).queryByRole('option', { name: 'Tariff assessment' })).not.toBeInTheDocument();
    expect(within(evidenceType).queryByRole('option', { name: 'Billing eligibility' })).not.toBeInTheDocument();

    fireEvent.change(screen.getByLabelText('Finance evidence identity'), {
      target: { value: 'invoice-002' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Verify evidence' }));

    await waitFor(() => {
      expect(getLegalFinanceEvidence).toHaveBeenCalledWith('INVOICE', 'invoice-002');
    });
  });

  it('gives LEGAL_FINANCE an exact finance console without practice/client/field reads', async () => {
    getLegalFinanceEvidence.mockResolvedValueOnce({
      tenantId: 'tenant-law',
      entityType: 'ClientInvoice',
      entityIdentity: 'invoice-001',
      visibility: 'FINANCE_VISIBLE',
      data: { invoice_id: 'invoice-001', state: 'ISSUED' },
    });

    render(
      <LegalDashboard
        roleView="LEGAL_FINANCE"
        tenantConfig={{ tenantId: 'tenant-law' }}
      />,
    );

    expect(await screen.findByText('Legal Finance Evidence')).toBeInTheDocument();
    expect(getLegalPracticeWorkspace).not.toHaveBeenCalled();
    expect(getLegalClientMatters).not.toHaveBeenCalled();
    expect(getSheriffOperationalQueues).not.toHaveBeenCalled();
    expect(getDeputyPersonalActiveWork).not.toHaveBeenCalled();

    fireEvent.change(screen.getByLabelText('Finance evidence identity'), {
      target: { value: 'invoice-001' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Verify evidence' }));

    await waitFor(() => {
      expect(getLegalFinanceEvidence).toHaveBeenCalledWith(
        'INVOICE',
        'invoice-001',
      );
    });
    expect(await screen.findByText('ClientInvoice')).toBeInTheDocument();
    expect(screen.getByText(/Kennel EOS owns settlement/i)).toBeInTheDocument();
  });

  it('keeps practice denial inside the Legal OS shell with no role fallback', async () => {
    getLegalPracticeWorkspace.mockRejectedValueOnce({
      response: {
        status: 403,
        data: { detail: 'LEGAL_OPERATIONS_WORKSPACE_DENIED' },
      },
    });

    render(<LegalDashboard roleView="LEGAL_PARTNER" />);

    expect(
      await screen.findByText('LEGAL_PRACTICE_WORKSPACE_DENIED'),
    ).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Command Center' })).toBeInTheDocument();
    expect(getSheriffOperationalQueues).not.toHaveBeenCalled();
    expect(getLegalClientMatters).not.toHaveBeenCalled();
    expect(getDeputyPersonalActiveWork).not.toHaveBeenCalled();
  });

  it('loads and presents the canonical conflict-review queue without exposing a NO_MATCH action', async () => {
    getLegalPracticeWorkspace.mockResolvedValue(practiceWorkspace());
    getLegalConflictScreenings.mockResolvedValue(conflictScreeningQueue());

    render(<LegalDashboard roleView="LEGAL_PARTNER" />);

    const queue = await screen.findByRole('heading', { name: 'Conflict review queue' });
    const queueSection = queue.closest('section');
    expect(getLegalConflictScreenings).toHaveBeenCalledTimes(1);
    expect(within(queueSection).getByText('CASE-2026-0001')).toBeInTheDocument();
    expect(within(queueSection).getByText('REVIEW_REQUIRED')).toBeInTheDocument();
    expect(within(queueSection).getByText('Review Conflict')).toBeInTheDocument();

    getLegalConflictScreenings.mockResolvedValue(conflictScreeningQueue({ status: 'NO_MATCH_FOUND' }));
    getLegalPracticeWorkspace.mockResolvedValue(practiceWorkspace());
    fireEvent.click(screen.getByRole('button', { name: 'Refresh truth' }));

    await waitFor(() => {
      expect(getLegalConflictScreenings).toHaveBeenCalledTimes(2);
    });
    expect(screen.queryByRole('button', { name: 'Review Conflict' })).not.toBeInTheDocument();
    expect(screen.getByText('No screenings currently require human review.')).toBeInTheDocument();
  });

  it('submits only the four human review fields and refreshes canonical screening state', async () => {
    getLegalPracticeWorkspace.mockResolvedValue(practiceWorkspace());
    getLegalConflictScreenings
      .mockResolvedValueOnce(conflictScreeningQueue())
      .mockResolvedValueOnce(conflictScreeningQueue({ status: null }));
    issueLegalConflictReview.mockResolvedValueOnce(
      conflictReviewReceipt('NO_CONFLICT_IDENTIFIED'),
    );

    render(<LegalDashboard roleView="LEGAL_PARTNER" />);
    await screen.findByRole('heading', { name: 'Conflict review queue' });
    fireEvent.click(screen.getByRole('button', { name: 'Review Conflict' }));

    const outcome = screen.getByRole('combobox', {
      name: 'Conflict review outcome for CASE-2026-0001',
    });
    expect(Array.from(outcome.options).map((option) => option.value)).toEqual([
      '',
      'CONFLICT_IDENTIFIED',
      'NO_CONFLICT_IDENTIFIED',
      'ESCALATION_REQUIRED',
    ]);
    fireEvent.change(outcome, { target: { value: 'NO_CONFLICT_IDENTIFIED' } });
    fireEvent.change(
      screen.getByRole('textbox', { name: 'Conflict review reason for CASE-2026-0001' }),
      { target: { value: 'review-ref:bounded-human-check' } },
    );
    fireEvent.click(screen.getByRole('button', { name: 'Submit review' }));

    await waitFor(() => {
      expect(issueLegalConflictReview).toHaveBeenCalledTimes(1);
      expect(getLegalConflictScreenings).toHaveBeenCalledTimes(2);
    });
    const submitted = issueLegalConflictReview.mock.calls[0][0];
    expect(Object.keys(submitted).sort()).toEqual([
      'outcome',
      'reviewId',
      'reviewReasonReference',
      'screeningId',
    ].sort());
    expect(submitted).toEqual({
      screeningId: 'screening-001',
      reviewId: expect.stringMatching(/^review-[0-9a-f-]{36}$/),
      outcome: 'NO_CONFLICT_IDENTIFIED',
      reviewReasonReference: 'review-ref:bounded-human-check',
    });
    for (const forbidden of [
      'tenantId',
      'reviewerPrincipalId',
      'reviewedAt',
      'fingerprint',
      'partyId',
      'authorizationEvidence',
    ]) {
      expect(submitted).not.toHaveProperty(forbidden);
    }
  });

  it('keeps one review identity and blocks duplicate dispatch while the command is pending', async () => {
    getLegalPracticeWorkspace.mockResolvedValue(practiceWorkspace());
    getLegalConflictScreenings.mockResolvedValue(conflictScreeningQueue());
    let resolveReview;
    issueLegalConflictReview.mockImplementationOnce(
      () => new Promise((resolve) => { resolveReview = resolve; }),
    );

    const view = render(<LegalDashboard roleView="LEGAL_PARTNER" />);
    await screen.findByRole('heading', { name: 'Conflict review queue' });
    fireEvent.click(screen.getByRole('button', { name: 'Review Conflict' }));
    fireEvent.change(screen.getByRole('combobox', {
      name: 'Conflict review outcome for CASE-2026-0001',
    }), { target: { value: 'ESCALATION_REQUIRED' } });
    fireEvent.change(screen.getByRole('textbox', {
      name: 'Conflict review reason for CASE-2026-0001',
    }), { target: { value: 'review-ref:pending-check' } });
    fireEvent.click(screen.getByRole('button', { name: 'Submit review' }));

    await waitFor(() => {
      expect(issueLegalConflictReview).toHaveBeenCalledTimes(1);
      expect(screen.getByRole('button', { name: 'Submit review' })).toBeDisabled();
    });
    const firstPayload = issueLegalConflictReview.mock.calls[0][0];
    expect(screen.getAllByText('CASE-2026-0001').length).toBeGreaterThan(0);
    expect(getLegalConflictScreenings).toHaveBeenCalledTimes(1);

    view.rerender(<LegalDashboard roleView="LEGAL_PARTNER" />);
    expect(screen.getByRole('button', { name: 'Submit review' })).toBeDisabled();
    resolveReview(conflictReviewReceipt('ESCALATION_REQUIRED'));
    await screen.findByText(/Conflict review recorded as ESCALATION_REQUIRED/);
    expect(issueLegalConflictReview.mock.calls[0][0].reviewId).toBe(firstPayload.reviewId);
  });

  it('retains the same command identity after a 409 and presents bounded server failure', async () => {
    getLegalPracticeWorkspace.mockResolvedValue(practiceWorkspace());
    getLegalConflictScreenings.mockResolvedValue(conflictScreeningQueue());
    issueLegalConflictReview
      .mockRejectedValueOnce({ response: { status: 409, data: { detail: 'LEGAL_CONFLICT_REVIEW_CONFLICT' } } })
      .mockResolvedValueOnce(conflictReviewReceipt('ESCALATION_REQUIRED'));

    render(<LegalDashboard roleView="LEGAL_PARTNER" />);
    await screen.findByRole('heading', { name: 'Conflict review queue' });
    fireEvent.click(screen.getByRole('button', { name: 'Review Conflict' }));
    fireEvent.change(screen.getByRole('combobox', {
      name: 'Conflict review outcome for CASE-2026-0001',
    }), { target: { value: 'ESCALATION_REQUIRED' } });
    fireEvent.change(screen.getByRole('textbox', {
      name: 'Conflict review reason for CASE-2026-0001',
    }), { target: { value: 'review-ref:replay-check' } });
    fireEvent.click(screen.getByRole('button', { name: 'Submit review' }));
    await screen.findByText(/LEGAL_CONFLICT_REVIEW_CONFLICT/);
    const firstPayload = issueLegalConflictReview.mock.calls[0][0];

    fireEvent.click(screen.getByRole('button', { name: 'Submit review' }));
    await waitFor(() => expect(issueLegalConflictReview).toHaveBeenCalledTimes(2));
    expect(issueLegalConflictReview.mock.calls[1][0]).toEqual(firstPayload);
  });

  it.each([
    [403, 'AUTHORIZATION_DENIED'],
    [404, 'SCREENING_NOT_FOUND'],
  ])('keeps HTTP %s review failure visible without fabricating success', async (status, detail) => {
    getLegalPracticeWorkspace.mockResolvedValue(practiceWorkspace());
    getLegalConflictScreenings.mockResolvedValue(conflictScreeningQueue());
    issueLegalConflictReview.mockRejectedValueOnce({
      response: { status, data: { detail } },
    });

    render(<LegalDashboard roleView="LEGAL_PARTNER" />);
    await screen.findByRole('heading', { name: 'Conflict review queue' });
    fireEvent.click(screen.getByRole('button', { name: 'Review Conflict' }));
    fireEvent.change(screen.getByRole('combobox', {
      name: 'Conflict review outcome for CASE-2026-0001',
    }), { target: { value: 'CONFLICT_IDENTIFIED' } });
    fireEvent.change(screen.getByRole('textbox', {
      name: 'Conflict review reason for CASE-2026-0001',
    }), { target: { value: 'review-ref:failure-check' } });
    fireEvent.click(screen.getByRole('button', { name: 'Submit review' }));

    expect(await screen.findByText(new RegExp(detail))).toBeInTheDocument();
    expect(screen.queryByText(/Conflict review recorded/)).not.toBeInTheDocument();
    expect(getLegalConflictScreenings).toHaveBeenCalledTimes(1);
  });
});

/**
 * ARTIFACT: legalDashboardPracticeWorkspace.test.jsx
 * VERSION: v1.5.0-L8-8M-R2-CONFLICT-REVIEW-COCKPIT-CERT
 * CHANGELOG: 2026-09-25 v1.5.0-L8-8M-R2-CONFLICT-REVIEW-COCKPIT-CERT certifies canonical conflict-screening queue loading, REVIEW_REQUIRED-only presentation, bounded four-field human review submission, stable browser review identity, in-flight duplicate blocking, canonical refresh and bounded HTTP failure preservation. No browser authority is widened.
 * AUTHORITY BOUNDARY: law-firm/finance presentation and governed command wiring certificate only; D18 posture text reports provenance/effective lanes but neither it nor D17/browser permission hints can widen the canonical role envelope or prove authorization
 * TENANT POSTURE: server-authorized adapter packets only; no browser authority scope
 * FAIL-CLOSED POSTURE: role denial, explicit/server-authoritative permission narrowing including an empty grant set, misleading authority provenance, command failure and cross-role drift never fallback, widen role scope, invent operating-model authority or invent success
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
