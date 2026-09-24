/**
 * WILSY OS — PRODUCTION LEGAL OPERATIONS WORKSPACE CERTIFICATE
 * VERSION: v1.2.0-L8-7D16-PERMISSION-AWARE-LEGAL-COMMAND-CENTER-CERT
 * AUTHORITY: Browser presentation/wiring certificate only.
 * EPITOME: Proves law-firm and finance roles resolve to real WILSY Legal OS
 *          workspaces backed by the D15 V2 first-class matter contract, with
 *          functional lifecycle navigation, governed intake, ReturnOfService generation, exact
 *          finance lookup and no cross-role endpoint fallback.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/legalDashboardPracticeWorkspace.test.jsx
 * CERTIFICATION / UPDATE DATE: 2026-09-24
 * CHANGELOG: 2026-09-24 v1.2.0-L8-7D16-PERMISSION-AWARE-LEGAL-COMMAND-CENTER-CERT certifies permission-aware narrowing for Legal Practice/Finance presentation: explicit legal permission hints can remove intake, ReturnOfService and finance affordances but cannot widen the canonical role envelope; absent legal permission hints preserve the certified role baseline.
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
  getLegalFinanceEvidence,
  getLegalPracticeWorkspace,
  getSheriffOperationalQueues,
  recordDeputyFieldOutcome,
  registerLegalIntake,
  transitionDeputyFieldAttempt,
} = vi.hoisted(() => ({
  generateLegalReturnOfService: vi.fn(),
  getDeputyFieldCapabilities: vi.fn(),
  getDeputyPersonalActiveWork: vi.fn(),
  getLegalClientMatters: vi.fn(),
  getLegalFinanceEvidence: vi.fn(),
  getLegalPracticeWorkspace: vi.fn(),
  getSheriffOperationalQueues: vi.fn(),
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
  getLegalFinanceEvidence,
  getLegalPracticeWorkspace,
  getSheriffOperationalQueues,
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

describe('D15 first-class Legal Matter Operating Room', () => {
  beforeEach(() => {
    vi.clearAllMocks();
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

    expect(screen.getByText('CASE-2026-0001')).toBeInTheDocument();
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
});

/**
 * ARTIFACT: legalDashboardPracticeWorkspace.test.jsx
 * VERSION: v1.2.0-L8-7D16-PERMISSION-AWARE-LEGAL-COMMAND-CENTER-CERT
 * AUTHORITY BOUNDARY: law-firm/finance presentation and governed command wiring certificate only; browser legal permission hints may only narrow the canonical role envelope and never prove authorization
 * TENANT POSTURE: server-authorized adapter packets only; no browser authority scope
 * FAIL-CLOSED POSTURE: role denial, explicit permission narrowing, command failure and cross-role drift never fallback, widen role scope or invent success
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
