/**
 * WILSY OS — ROLE-SCOPED LEGAL OPERATIONS CLIENT CERTIFICATE
 * VERSION: v2.3.0-L8-8N-CONFLICT-SCREENING-READ-CLIENT-CERT
 * AUTHORITY: Client transport-adapter contract certification only.
 * EPITOME: Certifies the canonical Legal Operations browser adapter across
 *          sheriff/deputy/client reads, D11 law-firm workspace, exact finance
 *          evidence lookup, governed initial intake, ReturnOfService generation
 *          and bound-Deputy field commands without browser-owned authority.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/services/legalOperationsService.test.js
 * CERTIFICATION / UPDATE DATE: 2026-09-25
 * CHANGELOG: 2026-09-25 v2.3.0-L8-8N-CONFLICT-SCREENING-READ-CLIENT-CERT binds the authenticated screening review-queue read adapter to the canonical /api/legal-operations/conflict-screenings path, proves exact data-minimized rows, server-owned tenant/order/status and privileged-field rejection.
 *            2026-09-25 v2.2.0-L8-8L-CONFLICT-REVIEW-COMMAND-CLIENT-CERT binds the authenticated four-field conflict-review adapter to the canonical /api/legal-operations/conflict-reviews path, proves server-owned authority exclusion, bounded receipt validation and unchanged 401/403/404/409/transport failures.
 *            2026-09-24 v2.1.0-L8-7D15-MATTER-WORKSPACE-COMPATIBILITY-CERT binds production v1.6.0-L8-7D15-MATTER-WORKSPACE-COMPATIBILITY and proves V1 remains unchanged while V2 requires exact first-class CaseMatter rows, matter counts, deterministic order, valid states and SHA3-512 evidence locators; mixed or malformed contracts reject fail-closed.
 *            2026-09-24 v2.0.1-L8-7D14-WORKSPACE-SUMMARY-VALIDATION-CERT binds production v1.5.1-L8-7D14-WORKSPACE-SUMMARY-VALIDATION and proves
 *            every D11 workspace state/outcome summary counter is recomputed
 *            from validated rows; total-preserving breakdown drift rejects.
 *            2026-09-23 v2.0.0-L8-7D13-LEGAL-OPERATIONS-ADAPTER-CERT binds production v1.5.0-L8-7D13-LEGAL-INTAKE-CLIENT and certifies
 *            D11 workspace schema/count/order/evidence integrity, exact finance
 *            lookup with no caller tenant scope, L8-2 intake request/response
 *            lineage, ReturnOfService command binding, immutability and
 *            fail-closed malformed evidence handling.
 *            2026-09-23 v1.3.0-L8-7D7-CLIENT-MATTER-READ-CLIENT-CERT certifies exact
 *            /legal-operations/client/matters GET transport, D5 schema/version/
 *            visibility binding, exact four-field matter cards, deterministic
 *            order/uniqueness, malformed/extra-field rejection, deep freezing,
 *            zero browser request authority, and production v1.3.0-L8-7D7-CLIENT-MATTER-READ-CLIENT alignment.
 *            2026-09-23 v1.2.0-L8-6H-DEPUTY-FIELD-COMMAND-CLIENT-CERT certifies exact field-capability GET transport,
 *            transition/outcome POST whitelists, rejection of sequence/provenance
 *            authority fields before transport, response attempt/device/event
 *            binding, terminal outcome binding, immutability, and production
 *            v1.2.0 version alignment.
 *            2026-09-23 v1.1.0-L8-6C-ROLE-SCOPED-LEGAL-OPERATIONS-CLIENT-CERT adds exact deputy personal-work endpoint,
 *            bound-deputy/tenant/state rejection, immutability, and production
 *            v1.1.0 binding while preserving sheriff queue assertions.
 *            2026-09-23 v1.0.1-L8-6A-SHERIFF-QUEUE-CLIENT-CERT certifies immutable queue-row objects and
 *            rebinds the adapter certificate to production v1.0.1.
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

const { mockGet, mockPost, mockConflictReviewPost } = vi.hoisted(() => ({
  mockGet: vi.fn(),
  mockPost: vi.fn(),
  mockConflictReviewPost: vi.fn(),
}));

vi.mock('../../services/api.js', () => ({
  default: {
    get: mockGet,
    post: mockPost,
  },
}));

vi.mock('../../utils/sovereignClient.js', () => ({
  default: {
    post: mockConflictReviewPost,
  },
}));

import {
  LEGAL_OPERATIONS_CLIENT_VERSION,
  __legalOperationsServiceInternals,
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
} from '../../services/legalOperationsService.js';

const payload = () => ({
  tenant_id: 'tenant-sheriff',
  visibility: 'SHERIFF_OPERATIONAL_QUEUE',
  office_receipt: [
    {
      tenant_id: 'tenant-sheriff',
      document_id: 'document-1',
      state: 'REGISTERED',
    },
  ],
  deputy_assignment: [
    {
      tenant_id: 'tenant-sheriff',
      document_id: 'document-2',
      state: 'RECEIVED',
    },
  ],
  active_attempts: [
    {
      tenant_id: 'tenant-sheriff',
      attempt_id: 'attempt-1',
      deputy_id: 'deputy-1',
      state: 'ALLOCATED',
    },
  ],
});

const clientMatterPayload = () => ({
  schema: 'WILSY-LEGAL-CLIENT-MATTER-PROJECTION/V1',
  version: 'v1.0.0-L8-7D5-CLIENT-MATTER-PROJECTION',
  tenant_id: 'tenant-client',
  visibility: 'LEGAL_CLIENT_EXPLICIT_MATTERS',
  matters: [
    {
      case_matter_id: 'matter-a',
      matter_reference: 'CLIENT-001',
      opened_at: '2026-09-23T18:00:00+00:00',
      state: 'OPEN',
    },
    {
      case_matter_id: 'matter-b',
      matter_reference: 'CLIENT-002',
      opened_at: '2026-09-23T18:05:00+00:00',
      state: 'CLOSED',
    },
  ],
});


const workspacePayload = () => ({
  schema: 'WILSY-LEGAL-OPERATIONS-PRACTICE-WORKSPACE/V1',
  version: 'v1.7.0-L8-7D11-LEGAL-PRACTICE-WORKSPACE-API',
  tenant_id: 'tenant-law',
  visibility: 'LEGAL_PRACTICE_WORKSPACE',
  summary: {
    instructions_total: 2,
    instructions_registered: 1,
    instructions_accepted: 1,
    instructions_closed: 0,
    instructions_cancelled: 0,
    documents_total: 2,
    documents_registered: 0,
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
    returns_total: 0,
  },
  instructions: [
    {
      instruction_id: 'instruction-1',
      case_matter_id: 'matter-1',
      document_id: 'document-1',
      registered_at: '2026-09-23T14:00:00+00:00',
      state: 'REGISTERED',
      evidence_identity: 'a'.repeat(128),
    },
    {
      instruction_id: 'instruction-2',
      case_matter_id: 'matter-2',
      document_id: 'document-2',
      registered_at: '2026-09-23T14:05:00+00:00',
      state: 'ACCEPTED',
      evidence_identity: 'b'.repeat(128),
    },
  ],
  documents: [
    {
      document_id: 'document-1',
      case_matter_id: 'matter-1',
      document_type: 'summons',
      registered_at: '2026-09-23T14:01:00+00:00',
      state: 'RECEIVED',
      evidence_identity: 'c'.repeat(128),
    },
    {
      document_id: 'document-2',
      case_matter_id: 'matter-2',
      document_type: 'notice',
      registered_at: '2026-09-23T14:06:00+00:00',
      state: 'ALLOCATED_TO_DEPUTY',
      evidence_identity: 'd'.repeat(128),
    },
  ],
  attempts: [
    {
      attempt_id: 'attempt-1',
      instruction_id: 'instruction-2',
      document_id: 'document-2',
      deputy_id: 'deputy-1',
      allocated_at: '2026-09-23T14:10:00+00:00',
      state: 'ATTEMPTED',
      evidence_identity: 'e'.repeat(128),
    },
  ],
  executions: [
    {
      service_execution_id: 'execution-1',
      attempt_id: 'attempt-1',
      instruction_id: 'instruction-2',
      document_id: 'document-2',
      outcome: 'COMPLETED',
      executed_at: '2026-09-23T14:20:00+00:00',
      evidence_identity: 'f'.repeat(128),
    },
  ],
  returns: [],
});

const workspaceV2Payload = () => {
  const base = workspacePayload();
  return {
    ...base,
    schema: 'WILSY-LEGAL-OPERATIONS-PRACTICE-WORKSPACE/V2',
    version: 'v1.8.0-L8-7D15-FIRST-CLASS-MATTER-WORKSPACE-API',
    summary: {
      matters_total: 2,
      matters_open: 1,
      matters_closed: 1,
      ...base.summary,
    },
    matters: [
      {
        case_matter_id: 'matter-1',
        matter_reference: 'CASE-2026-0001',
        opened_at: '2026-09-23T13:50:00+00:00',
        state: 'OPEN',
        evidence_identity: '1'.repeat(128),
      },
      {
        case_matter_id: 'matter-2',
        matter_reference: 'CASE-2026-0002',
        opened_at: '2026-09-23T13:55:00+00:00',
        state: 'CLOSED',
        evidence_identity: '2'.repeat(128),
      },
    ],
  };
};


const intakeInput = () => ({
  caseMatterId: 'matter-intake-1',
  matterReference: 'CASE-2026-0100',
  caseOpenedAt: '2026-09-23T15:00:00+00:00',
  matterEvidenceReference: 'matter-evidence-1',
  instructionId: 'instruction-intake-1',
  instructionRegisteredAt: '2026-09-23T15:00:00+00:00',
  instructionEvidenceReference: 'instruction-evidence-1',
  documentId: 'document-intake-1',
  documentType: 'summons',
  documentRegisteredAt: '2026-09-23T15:00:00+00:00',
  documentRegistrationEvidenceReference: 'document-evidence-1',
  registrationCustodyEventId: 'custody-intake-1',
});

const intakeResponse = () => {
  const input = intakeInput();
  const base = {
    schema: 'WILSY-LEGAL-OPERATIONS-LIFECYCLE/V1',
    version: 'v1.0.0-LEGAL-OPERATIONS-LIFECYCLE',
    tenant_id: 'tenant-law',
  };
  return {
    disposition: 'CREATED',
    case_matter: {
      ...base,
      entity_type: 'CaseMatter',
      case_matter_id: input.caseMatterId,
      matter_reference: input.matterReference,
      opened_at: input.caseOpenedAt,
      evidence_reference: input.matterEvidenceReference,
      state: 'OPEN',
      transition_history: [],
    },
    instruction: {
      ...base,
      entity_type: 'LegalInstruction',
      instruction_id: input.instructionId,
      case_matter_id: input.caseMatterId,
      document_id: input.documentId,
      registered_at: input.instructionRegisteredAt,
      evidence_reference: input.instructionEvidenceReference,
      state: 'REGISTERED',
      transition_history: [],
    },
    document: {
      ...base,
      entity_type: 'ProcessDocument',
      document_id: input.documentId,
      case_matter_id: input.caseMatterId,
      document_type: input.documentType,
      registered_at: input.documentRegisteredAt,
      registration_evidence_reference: input.documentRegistrationEvidenceReference,
      state: 'REGISTERED',
      transition_history: [],
    },
    custody_event: {
      ...base,
      entity_type: 'DocumentCustodyEvent',
      custody_event_id: input.registrationCustodyEventId,
      document_id: input.documentId,
      event_type: 'REGISTERED',
      occurred_at: input.documentRegisteredAt,
      sequence_number: 1,
      evidence_reference: input.documentRegistrationEvidenceReference,
      from_holder_reference: null,
      to_holder_reference: null,
    },
  };
};

const returnInput = () => ({
  executionId: 'execution-1',
  executionEvidenceIdentity: 'f'.repeat(128),
  returnId: 'return-1',
  generatedAt: '2026-09-23T15:30:00+00:00',
});

const returnResponse = () => ({
  data: {
    schema: 'WILSY-LEGAL-OPERATIONS-LIFECYCLE/V1',
    version: 'v1.0.0-LEGAL-OPERATIONS-LIFECYCLE',
    entity_type: 'ReturnOfService',
    tenant_id: 'tenant-law',
    return_id: 'return-1',
    instruction_id: 'instruction-2',
    document_id: 'document-2',
    attempt_id: 'attempt-1',
    service_execution_id: 'execution-1',
    service_outcome: 'COMPLETED',
    service_evidence_reference: 'service-evidence',
    service_evidence_fingerprint: '9'.repeat(128),
    generated_at: '2026-09-23T15:30:00+00:00',
    state: 'GENERATED',
  },
});

const financeResponse = () => ({
  tenant_id: 'tenant-law',
  entity_type: 'ClientInvoice',
  entity_identity: 'invoice-1',
  visibility: 'FINANCE_VISIBLE',
  data: {
    invoice_id: 'invoice-1',
    status: 'ISSUED',
  },
});


const deputyPayload = () => ({
  tenant_id: 'tenant-deputy',
  visibility: 'DEPUTY_PERSONAL_ACTIVE_WORK',
  deputy_id: 'deputy-bound',
  active_attempts: [
    {
      tenant_id: 'tenant-deputy',
      attempt_id: 'attempt-bound',
      instruction_id: 'instruction-bound',
      document_id: 'document-bound',
      deputy_id: 'deputy-bound',
      state: 'ATTEMPTED',
    },
  ],
});


const SHA3_A = 'a'.repeat(128);
const SHA3_B = 'b'.repeat(128);
const SHA3_C = 'c'.repeat(128);
const OCCURRED_AT = '2026-09-23T16:00:00+00:00';
const ACCEPTED_AT = '2026-09-23T16:00:01+00:00';

const capabilityPayload = (state = 'ALLOCATED') => ({
  tenant_id: 'tenant-deputy',
  visibility: 'DEPUTY_FIELD_COMMAND_CAPABILITIES',
  deputy_id: 'deputy-bound',
  capabilities: [
    {
      tenant_id: 'tenant-deputy',
      attempt_id: 'attempt-bound',
      instruction_id: 'instruction-bound',
      document_id: 'document-bound',
      deputy_id: 'deputy-bound',
      current_state: state,
      current_evidence_identity: SHA3_A,
      next_command_kinds:
        state === 'ALLOCATED'
          ? ['TRANSITION_TO_ATTEMPTED']
          : [
            'RECORD_COMPLETED_OUTCOME',
            'RECORD_NOT_COMPLETED_OUTCOME',
          ],
    },
  ],
});

const fieldReceipt = ({
  eventId = 'event-mobile-1',
  sequenceNumber = 1,
  evidenceFingerprint = SHA3_B,
} = {}) => ({
  tenant_id: 'tenant-deputy',
  receipt_id: 'receipt-mobile-1',
  event_id: eventId,
  device_id: 'device-mobile-1',
  sequence_number: sequenceNumber,
  attempt_id: 'attempt-bound',
  instruction_id: 'instruction-bound',
  document_id: 'document-bound',
  deputy_id: 'deputy-bound',
  district_id: 'district-1',
  sheriff_office_id: 'office-1',
  evidence_reference: 'photo:attempt-bound',
  evidence_fingerprint: evidenceFingerprint,
  command_fingerprint: SHA3_C,
  accepted_at: ACCEPTED_AT,
  evidence_identity: SHA3_A,
});

const attemptedResponse = () => ({
  data: {
    schema: 'WILSY-LEGAL-OPERATIONS-LIFECYCLE',
    version: 'v1',
    entity_type: 'ServiceAttempt',
    tenant_id: 'tenant-deputy',
    attempt_id: 'attempt-bound',
    instruction_id: 'instruction-bound',
    document_id: 'document-bound',
    deputy_id: 'deputy-bound',
    allocated_at: '2026-09-23T15:00:00+00:00',
    allocation_evidence_reference: 'allocation-proof',
    state: 'ATTEMPTED',
    transition_history: [
      {
        prior_state: 'ALLOCATED',
        resulting_state: 'ATTEMPTED',
        occurred_at: OCCURRED_AT,
        evidence_reference: 'photo:attempt-bound',
        evidence_fingerprint: null,
      },
    ],
  },
  field_evidence: fieldReceipt(),
});

const executionResponse = () => ({
  data: {
    schema: 'WILSY-LEGAL-OPERATIONS-LIFECYCLE',
    version: 'v1',
    entity_type: 'ServiceExecution',
    tenant_id: 'tenant-deputy',
    service_execution_id: SHA3_C,
    attempt_id: 'attempt-bound',
    instruction_id: 'instruction-bound',
    document_id: 'document-bound',
    outcome: 'COMPLETED',
    executed_at: OCCURRED_AT,
    evidence_reference: 'photo:attempt-bound',
    evidence_fingerprint: SHA3_B,
  },
  field_evidence: fieldReceipt({
    eventId: 'event-mobile-2',
    sequenceNumber: 2,
  }),
});

const transitionInput = () => ({
  attemptId: 'attempt-bound',
  currentEvidenceIdentity: SHA3_A,
  deviceId: 'device-mobile-1',
  eventId: 'event-mobile-1',
  occurredAt: OCCURRED_AT,
  observationReference: 'photo:attempt-bound',
});

const outcomeInput = () => ({
  ...transitionInput(),
  eventId: 'event-mobile-2',
  outcome: 'COMPLETED',
});

const conflictReviewInput = () => ({
  screeningId: 'screening-1',
  reviewId: 'review-1',
  outcome: 'CONFLICT_IDENTIFIED',
  reviewReasonReference: 'review-reason:operator-observed',
});

const conflictReviewResponse = () => ({
  data: {
    review_id: 'review-1',
    screening_id: 'screening-1',
    outcome: 'CONFLICT_IDENTIFIED',
    reviewed_at: '2026-09-25T04:00:00.123456+00:00',
    fingerprint: SHA3_A,
  },
});

describe('L8-7D7 role-scoped Legal Operations client adapter', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('reads the exact authenticated conflict-screening review queue without tenant input', async () => {
    const screeningPayload = {
      schema: 'WILSY-LEGAL-CONFLICT-SCREENING-PRESENTATION/V1',
      version: 'v1.9.0-L8-8N-CONFLICT-SCREENING-READ-API',
      tenant_id: 'tenant-law',
      visibility: 'LEGAL_CONFLICT_SCREENING_REVIEW_QUEUE',
      screenings: [
        {
          screening_id: 'screening-new',
          source_case_matter_id: 'matter-new',
          status: 'REVIEW_REQUIRED',
          screened_at: '2026-09-25T04:00:00+00:00',
        },
      ],
    };
    mockGet.mockResolvedValueOnce({ data: screeningPayload });

    const result = await getLegalConflictScreenings();

    expect(mockGet).toHaveBeenCalledWith('/legal-operations/conflict-screenings');
    expect(result.screenings).toEqual([
      {
        screeningId: 'screening-new',
        sourceCaseMatterId: 'matter-new',
        status: 'REVIEW_REQUIRED',
        screenedAt: '2026-09-25T04:00:00+00:00',
      },
    ]);
    expect(Object.isFrozen(result)).toBe(true);
    expect(Object.isFrozen(result.screenings)).toBe(true);
    expect(Object.isFrozen(result.screenings[0])).toBe(true);
  });

  it('rejects screening presentation privilege, tenant, status and order drift', async () => {
    const validate = __legalOperationsServiceInternals.assertCanonicalConflictScreeningPayload;
    const base = {
      schema: 'WILSY-LEGAL-CONFLICT-SCREENING-PRESENTATION/V1',
      version: 'v1.9.0-L8-8N-CONFLICT-SCREENING-READ-API',
      tenant_id: 'tenant-law',
      visibility: 'LEGAL_CONFLICT_SCREENING_REVIEW_QUEUE',
      screenings: [
        {
          screening_id: 'screening-new',
          source_case_matter_id: 'matter-new',
          status: 'REVIEW_REQUIRED',
          screened_at: '2026-09-25T04:00:00+00:00',
        },
      ],
    };
    expect(() => validate({ ...base, authorization_evidence: 'forbidden' }))
      .toThrow('LEGAL_OPERATIONS_CONFLICT_SCREENING_RESPONSE_INVALID');
    expect(() => validate({ ...base, screenings: [{ ...base.screenings[0], status: 'NO_MATCH_FOUND' }] }))
      .toThrow('LEGAL_OPERATIONS_CONFLICT_SCREENING_SCOPE_INVALID');
    expect(() => validate({ ...base, tenant_id: 'tenant-forged' })).not.toThrow();
    const unsorted = {
      ...base,
      screenings: [
        base.screenings[0],
        { ...base.screenings[0], screening_id: 'screening-old', screened_at: '2026-09-26T04:00:00+00:00' },
      ],
    };
    expect(() => validate(unsorted)).toThrow('LEGAL_OPERATIONS_CONFLICT_SCREENING_ORDER_INVALID');
  });

  it.each([
    [401, 'AUTHENTICATION_REJECTED'],
    [403, 'LEGAL_CONFLICT_SCREENING_AUTHORIZATION_REQUIRED'],
    [503, 'LEGAL_CONFLICT_SCREENING_EVIDENCE_UNAVAILABLE'],
  ])('preserves screening read failure %s without local fallback', async (status, code) => {
    const error = { response: { status, data: { detail: code } } };
    mockGet.mockRejectedValueOnce(error);
    await expect(getLegalConflictScreenings()).rejects.toBe(error);
  });

  it('issues conflict review through the canonical route with exactly four fields', async () => {
    mockConflictReviewPost.mockResolvedValueOnce({ data: conflictReviewResponse() });

    const result = await issueLegalConflictReview(conflictReviewInput());

    expect(mockConflictReviewPost).toHaveBeenCalledTimes(1);
    expect(mockConflictReviewPost).toHaveBeenCalledWith(
      '/legal-operations/conflict-reviews',
      {
        screening_id: 'screening-1',
        review_id: 'review-1',
        outcome: 'CONFLICT_IDENTIFIED',
        review_reason_reference: 'review-reason:operator-observed',
      },
    );
    expect(Object.keys(mockConflictReviewPost.mock.calls[0][1]).sort()).toEqual([
      'outcome',
      'review_id',
      'review_reason_reference',
      'screening_id',
    ]);
    expect(result).toEqual({
      reviewId: 'review-1',
      screeningId: 'screening-1',
      outcome: 'CONFLICT_IDENTIFIED',
      reviewedAt: '2026-09-25T04:00:00.123456+00:00',
      fingerprint: SHA3_A,
    });
    expect(Object.isFrozen(result)).toBe(true);
    expect(mockPost).not.toHaveBeenCalled();
  });

  it('rejects browser-owned tenant, reviewer, chronology, screening, and authority fields', async () => {
    const forbidden = {
      tenant_id: 'tenant-forged',
      reviewer_principal_id: 'principal-forged',
      reviewed_at: '2026-09-25T04:00:00+00:00',
      screening_fingerprint: SHA3_A,
      screening_payload: { party: 'forbidden' },
      authorization_evidence_reference: 'auth-forged',
      authorization_evidence_fingerprint: SHA3_A,
      source_evidence_reference: 'source-forged',
      waiver: true,
      client_acceptance: true,
      financial_authority: true,
    };

    for (const [field, value] of Object.entries(forbidden)) {
      await expect(issueLegalConflictReview({
        ...conflictReviewInput(),
        [field]: value,
      })).rejects.toThrow('LEGAL_OPERATIONS_CONFLICT_REVIEW_INPUT_INVALID');
    }
    expect(mockConflictReviewPost).not.toHaveBeenCalled();
  });

  it('rejects malformed or privileged server receipts without local fallback', async () => {
    mockConflictReviewPost.mockResolvedValueOnce({
      data: {
        ...conflictReviewResponse(),
        authorization_evidence_reference: 'must-not-cross-boundary',
      },
    });

    await expect(issueLegalConflictReview(conflictReviewInput())).rejects.toThrow(
      'LEGAL_OPERATIONS_CONFLICT_REVIEW_RESPONSE_INVALID',
    );
  });

  it.each([
    [401, 'AUTHENTICATION_REJECTED'],
    [403, 'LEGAL_CONFLICT_REVIEW_AUTHORIZATION_REQUIRED'],
    [404, 'LEGAL_OPERATION_NOT_FOUND'],
    [409, 'LEGAL_CONFLICT_REVIEW_CONFLICT'],
  ])('preserves server semantic failure %s without overwrite or retry', async (status, code) => {
    const error = { response: { status, data: { detail: code } } };
    mockConflictReviewPost.mockRejectedValueOnce(error);

    await expect(issueLegalConflictReview(conflictReviewInput())).rejects.toBe(error);
  });

  it('preserves transport failure rather than manufacturing success', async () => {
    const error = new Error('NETWORK_UNAVAILABLE');
    mockConflictReviewPost.mockRejectedValueOnce(error);

    await expect(issueLegalConflictReview(conflictReviewInput())).rejects.toBe(error);
  });

  it('uses the governed queue endpoint and adapts only the certified queues', async () => {
    mockGet.mockResolvedValueOnce({ data: payload() });

    const result = await getSheriffOperationalQueues();

    expect(mockGet).toHaveBeenCalledTimes(1);
    expect(mockGet).toHaveBeenCalledWith(
      '/legal-operations/operational-queues',
    );
    expect(result).toEqual({
      tenantId: 'tenant-sheriff',
      visibility: 'SHERIFF_OPERATIONAL_QUEUE',
      officeReceipt: payload().office_receipt,
      deputyAssignment: payload().deputy_assignment,
      activeAttempts: payload().active_attempts,
    });
    expect(Object.isFrozen(result)).toBe(true);
    expect(Object.isFrozen(result.officeReceipt)).toBe(true);
    expect(Object.isFrozen(result.deputyAssignment)).toBe(true);
    expect(Object.isFrozen(result.activeAttempts)).toBe(true);
    expect(Object.isFrozen(result.officeReceipt[0])).toBe(true);
    expect(Object.isFrozen(result.deputyAssignment[0])).toBe(true);
    expect(Object.isFrozen(result.activeAttempts[0])).toBe(true);
  });

  it('rejects missing, extra, or malformed response fields without fallback', () => {
    const validate =
      __legalOperationsServiceInternals.assertCanonicalQueuePayload;

    const missing = payload();
    delete missing.active_attempts;
    expect(() => validate(missing)).toThrow(
      'LEGAL_OPERATIONS_QUEUE_RESPONSE_INVALID',
    );

    const extra = { ...payload(), monthlyRevenue: 999999 };
    expect(() => validate(extra)).toThrow(
      'LEGAL_OPERATIONS_QUEUE_RESPONSE_INVALID',
    );

    const malformed = { ...payload(), office_receipt: {} };
    expect(() => validate(malformed)).toThrow(
      'LEGAL_OPERATIONS_QUEUE_RESPONSE_INVALID',
    );
  });

  it('rejects cross-tenant queue rows rather than presenting leaked work', () => {
    const validate =
      __legalOperationsServiceInternals.assertCanonicalQueuePayload;
    const crossTenant = payload();
    crossTenant.active_attempts = [
      {
        tenant_id: 'tenant-foreign',
        attempt_id: 'attempt-foreign',
        state: 'ALLOCATED',
      },
    ];

    expect(() => validate(crossTenant)).toThrow(
      'LEGAL_OPERATIONS_QUEUE_TENANT_MISMATCH',
    );
  });

  it('does not manufacture unsupported dashboard truth', () => {
    const result = __legalOperationsServiceInternals.assertCanonicalQueuePayload(
      payload(),
    );
    expect(Object.keys(result).sort()).toEqual([
      'activeAttempts',
      'deputyAssignment',
      'officeReceipt',
      'tenantId',
      'visibility',
    ]);
    const serialized = JSON.stringify(result).toLowerCase();
    for (const forbidden of [
      'urgent',
      'distance',
      'billing',
      'invoice',
      'payment',
      'settlement',
      'revenue',
      'client_name',
      'ai_score',
    ]) {
      expect(serialized).not.toContain(forbidden);
    }
  });

  it('reads exact D6 client matters with no browser-owned request scope', async () => {
    mockGet.mockResolvedValueOnce({ data: clientMatterPayload() });

    const result = await getLegalClientMatters();

    expect(mockGet).toHaveBeenCalledTimes(1);
    expect(mockGet).toHaveBeenCalledWith(
      '/legal-operations/client/matters',
    );
    expect(result).toEqual({
      schema: 'WILSY-LEGAL-CLIENT-MATTER-PROJECTION/V1',
      version: 'v1.0.0-L8-7D5-CLIENT-MATTER-PROJECTION',
      tenantId: 'tenant-client',
      visibility: 'LEGAL_CLIENT_EXPLICIT_MATTERS',
      matters: [
        {
          caseMatterId: 'matter-a',
          matterReference: 'CLIENT-001',
          openedAt: '2026-09-23T18:00:00+00:00',
          state: 'OPEN',
        },
        {
          caseMatterId: 'matter-b',
          matterReference: 'CLIENT-002',
          openedAt: '2026-09-23T18:05:00+00:00',
          state: 'CLOSED',
        },
      ],
    });
    expect(Object.isFrozen(result)).toBe(true);
    expect(Object.isFrozen(result.matters)).toBe(true);
    expect(Object.isFrozen(result.matters[0])).toBe(true);
    expect(Object.isFrozen(result.matters[1])).toBe(true);
  });

  it('rejects client schema, version, visibility, state, timestamp, and extra-field drift', () => {
    const validate =
      __legalOperationsServiceInternals.assertCanonicalClientMatterPayload;

    for (const invalid of [
      { ...clientMatterPayload(), schema: 'WILSY-LEGAL-CLIENT-MATTER-PROJECTION/V2' },
      { ...clientMatterPayload(), version: 'vNext' },
      { ...clientMatterPayload(), visibility: 'AUDIT_VISIBLE' },
      {
        ...clientMatterPayload(),
        matters: [
          {
            ...clientMatterPayload().matters[0],
            state: 'ATTEMPTED',
          },
        ],
      },
      {
        ...clientMatterPayload(),
        matters: [
          {
            ...clientMatterPayload().matters[0],
            opened_at: 'not-a-timestamp',
          },
        ],
      },
      { ...clientMatterPayload(), instruction_id: 'instruction-leak' },
    ]) {
      expect(() => validate(invalid)).toThrow(
        'LEGAL_OPERATIONS_CLIENT_MATTER',
      );
    }
  });

  it('rejects duplicate or unsorted client matters rather than normalizing server drift', () => {
    const validate =
      __legalOperationsServiceInternals.assertCanonicalClientMatterPayload;

    const duplicate = clientMatterPayload();
    duplicate.matters[1].case_matter_id = 'matter-a';
    expect(() => validate(duplicate)).toThrow(
      'LEGAL_OPERATIONS_CLIENT_MATTER_SCOPE_INVALID',
    );

    const unsorted = clientMatterPayload();
    unsorted.matters = [...unsorted.matters].reverse();
    expect(() => validate(unsorted)).toThrow(
      'LEGAL_OPERATIONS_CLIENT_MATTER_SCOPE_INVALID',
    );
  });

  it('projects only the D5 client-safe field set and no internal or financial truth', () => {
    const result =
      __legalOperationsServiceInternals.assertCanonicalClientMatterPayload(
        clientMatterPayload(),
      );

    expect(Object.keys(result).sort()).toEqual([
      'matters',
      'schema',
      'tenantId',
      'version',
      'visibility',
    ]);
    expect(Object.keys(result.matters[0]).sort()).toEqual([
      'caseMatterId',
      'matterReference',
      'openedAt',
      'state',
    ]);

    const serialized = JSON.stringify(result).toLowerCase();
    for (const forbidden of [
      'principal',
      'client_principal',
      'instruction',
      'document',
      'deputy',
      'attempt',
      'evidence',
      'fingerprint',
      'return',
      'invoice',
      'billing',
      'payment',
      'settlement',
      'revenue',
      'ai_',
      'authorized',
      'role',
    ]) {
      expect(serialized).not.toContain(forbidden);
    }
  });

  it('uses the bound-deputy endpoint and adapts only personal active work', async () => {
    mockGet.mockResolvedValueOnce({ data: deputyPayload() });

    const result = await getDeputyPersonalActiveWork();

    expect(mockGet).toHaveBeenCalledTimes(1);
    expect(mockGet).toHaveBeenCalledWith(
      '/legal-operations/deputy/active-work',
    );
    expect(result).toEqual({
      tenantId: 'tenant-deputy',
      visibility: 'DEPUTY_PERSONAL_ACTIVE_WORK',
      deputyId: 'deputy-bound',
      activeAttempts: deputyPayload().active_attempts,
    });
    expect(Object.isFrozen(result)).toBe(true);
    expect(Object.isFrozen(result.activeAttempts)).toBe(true);
    expect(Object.isFrozen(result.activeAttempts[0])).toBe(true);
  });

  it('rejects deputy tenant, deputy identity, terminal state, and extra-field drift', () => {
    const validate =
      __legalOperationsServiceInternals.assertCanonicalDeputyActiveWorkPayload;

    const crossTenant = deputyPayload();
    crossTenant.active_attempts[0].tenant_id = 'tenant-foreign';
    expect(() => validate(crossTenant)).toThrow(
      'LEGAL_OPERATIONS_DEPUTY_WORK_SCOPE_INVALID',
    );

    const crossDeputy = deputyPayload();
    crossDeputy.active_attempts[0].deputy_id = 'deputy-other';
    expect(() => validate(crossDeputy)).toThrow(
      'LEGAL_OPERATIONS_DEPUTY_WORK_SCOPE_INVALID',
    );

    const terminal = deputyPayload();
    terminal.active_attempts[0].state = 'COMPLETED';
    expect(() => validate(terminal)).toThrow(
      'LEGAL_OPERATIONS_DEPUTY_WORK_SCOPE_INVALID',
    );

    const extra = { ...deputyPayload(), office_receipt: [] };
    expect(() => validate(extra)).toThrow(
      'LEGAL_OPERATIONS_DEPUTY_WORK_RESPONSE_INVALID',
    );
  });

  it('reads exact deputy field capabilities and preserves state-command mapping', async () => {
    mockGet.mockResolvedValueOnce({ data: capabilityPayload('ALLOCATED') });

    const result = await getDeputyFieldCapabilities();

    expect(mockGet).toHaveBeenCalledTimes(1);
    expect(mockGet).toHaveBeenCalledWith(
      '/legal-operations/deputy/field-capabilities',
    );
    expect(result).toEqual({
      tenantId: 'tenant-deputy',
      visibility: 'DEPUTY_FIELD_COMMAND_CAPABILITIES',
      deputyId: 'deputy-bound',
      capabilities: [
        {
          tenantId: 'tenant-deputy',
          attemptId: 'attempt-bound',
          instructionId: 'instruction-bound',
          documentId: 'document-bound',
          deputyId: 'deputy-bound',
          currentState: 'ALLOCATED',
          currentEvidenceIdentity: SHA3_A,
          nextCommandKinds: ['TRANSITION_TO_ATTEMPTED'],
        },
      ],
    });
    expect(Object.isFrozen(result)).toBe(true);
    expect(Object.isFrozen(result.capabilities)).toBe(true);
    expect(Object.isFrozen(result.capabilities[0])).toBe(true);
    expect(Object.isFrozen(result.capabilities[0].nextCommandKinds)).toBe(true);
  });

  it('rejects capability scope, locator, and state-command drift', () => {
    const validate =
      __legalOperationsServiceInternals
        .assertCanonicalDeputyFieldCapabilitiesPayload;

    const crossDeputy = capabilityPayload();
    crossDeputy.capabilities[0].deputy_id = 'deputy-other';
    expect(() => validate(crossDeputy)).toThrow(
      'LEGAL_OPERATIONS_DEPUTY_CAPABILITY_SCOPE_INVALID',
    );

    const badLocator = capabilityPayload();
    badLocator.capabilities[0].current_evidence_identity = 'not-a-sha3';
    expect(() => validate(badLocator)).toThrow(
      'LEGAL_OPERATIONS_DEPUTY_CAPABILITY_SCOPE_INVALID',
    );

    const wrongCommand = capabilityPayload('ALLOCATED');
    wrongCommand.capabilities[0].next_command_kinds = [
      'RECORD_COMPLETED_OUTCOME',
    ];
    expect(() => validate(wrongCommand)).toThrow(
      'LEGAL_OPERATIONS_DEPUTY_CAPABILITY_SCOPE_INVALID',
    );
  });

  it('posts begin-attempt observation without browser authority or sequence lineage', async () => {
    mockPost.mockResolvedValueOnce({ data: attemptedResponse() });

    const result = await transitionDeputyFieldAttempt(transitionInput());

    expect(mockPost).toHaveBeenCalledTimes(1);
    expect(mockPost).toHaveBeenCalledWith(
      '/legal-operations/deputy/attempts/attempt-bound/transition',
      {
        current_evidence_identity: SHA3_A,
        device_id: 'device-mobile-1',
        event_id: 'event-mobile-1',
        occurred_at: OCCURRED_AT,
        observation_reference: 'photo:attempt-bound',
      },
    );
    expect(mockPost.mock.calls[0][1]).not.toHaveProperty('tenant_id');
    expect(mockPost.mock.calls[0][1]).not.toHaveProperty('deputy_id');
    expect(mockPost.mock.calls[0][1]).not.toHaveProperty('sequence_number');
    expect(mockPost.mock.calls[0][1]).not.toHaveProperty(
      'previous_event_fingerprint',
    );
    expect(mockPost.mock.calls[0][1]).not.toHaveProperty(
      'evidence_fingerprint',
    );
    expect(result.data.state).toBe('ATTEMPTED');
    expect(result.fieldEvidence.sequence_number).toBe(1);
    expect(Object.isFrozen(result)).toBe(true);
    expect(Object.isFrozen(result.data)).toBe(true);
    expect(Object.isFrozen(result.fieldEvidence)).toBe(true);
  });

  it('posts terminal observation and validates canonical execution evidence', async () => {
    mockPost.mockResolvedValueOnce({ data: executionResponse() });

    const result = await recordDeputyFieldOutcome(outcomeInput());

    expect(mockPost).toHaveBeenCalledTimes(1);
    expect(mockPost).toHaveBeenCalledWith(
      '/legal-operations/deputy/attempts/attempt-bound/outcome',
      {
        current_evidence_identity: SHA3_A,
        device_id: 'device-mobile-1',
        event_id: 'event-mobile-2',
        occurred_at: OCCURRED_AT,
        observation_reference: 'photo:attempt-bound',
        outcome: 'COMPLETED',
      },
    );
    expect(mockPost.mock.calls[0][1]).not.toHaveProperty(
      'service_execution_id',
    );
    expect(mockPost.mock.calls[0][1]).not.toHaveProperty('executed_at');
    expect(result.data.entity_type).toBe('ServiceExecution');
    expect(result.data.outcome).toBe('COMPLETED');
    expect(result.data.evidence_fingerprint).toBe(
      result.fieldEvidence.evidence_fingerprint,
    );
  });

  it('rejects browser lineage/authority fields before command transport', async () => {
    for (const forbidden of [
      { sequenceNumber: 1 },
      { previousEventFingerprint: SHA3_A },
      { evidenceFingerprint: SHA3_A },
      { receiptId: 'receipt-browser' },
      { tenantId: 'tenant-browser' },
      { deputyId: 'deputy-browser' },
      { serviceExecutionId: 'execution-browser' },
    ]) {
      await expect(
        transitionDeputyFieldAttempt({
          ...transitionInput(),
          ...forbidden,
        }),
      ).rejects.toThrow('LEGAL_OPERATIONS_FIELD_COMMAND_INPUT_INVALID');
    }
    expect(mockPost).not.toHaveBeenCalled();
  });

  it('rejects mismatched command response scope instead of presenting success', async () => {
    const response = attemptedResponse();
    response.field_evidence.event_id = 'event-other';
    mockPost.mockResolvedValueOnce({ data: response });

    await expect(
      transitionDeputyFieldAttempt(transitionInput()),
    ).rejects.toThrow('LEGAL_OPERATIONS_FIELD_COMMAND_RESPONSE_INVALID');
  });

  it('reads and freezes the exact D11 legal-practice workspace', async () => {
    mockGet.mockResolvedValueOnce({ data: workspacePayload() });

    const result = await getLegalPracticeWorkspace();

    expect(mockGet).toHaveBeenCalledWith('/legal-operations/workspace');
    expect(result.tenantId).toBe('tenant-law');
    expect(result.visibility).toBe('LEGAL_PRACTICE_WORKSPACE');
    expect(result.summary.instructions_total).toBe(2);
    expect(result.instructions[1].state).toBe('ACCEPTED');
    expect(result.executions[0].outcome).toBe('COMPLETED');
    expect(Object.isFrozen(result)).toBe(true);
    expect(Object.isFrozen(result.summary)).toBe(true);
    expect(Object.isFrozen(result.instructions)).toBe(true);
    expect(Object.isFrozen(result.instructions[0])).toBe(true);
  });

  it('rejects workspace summary, order, locator, and extra-field drift', () => {
    const validate =
      __legalOperationsServiceInternals.assertCanonicalLegalWorkspacePayload;

    const summaryDrift = workspacePayload();
    summaryDrift.summary.instructions_total = 99;
    expect(() => validate(summaryDrift)).toThrow(
      'LEGAL_OPERATIONS_WORKSPACE_SUMMARY_MISMATCH',
    );

    const breakdownDrift = workspacePayload();
    breakdownDrift.summary.attempts_attempted = 0;
    breakdownDrift.summary.attempts_allocated = 1;
    expect(() => validate(breakdownDrift)).toThrow(
      'LEGAL_OPERATIONS_WORKSPACE_SUMMARY_MISMATCH',
    );

    const unsorted = workspacePayload();
    unsorted.instructions.reverse();
    expect(() => validate(unsorted)).toThrow(
      'LEGAL_OPERATIONS_WORKSPACE_RESPONSE_INVALID',
    );

    const badLocator = workspacePayload();
    badLocator.attempts[0].evidence_identity = 'not-a-sha3';
    expect(() => validate(badLocator)).toThrow(
      'LEGAL_OPERATIONS_WORKSPACE_RESPONSE_INVALID',
    );

    expect(() => validate({
      ...workspacePayload(),
      client_name: 'forbidden',
    })).toThrow('LEGAL_OPERATIONS_WORKSPACE_RESPONSE_INVALID');
  });

  it('performs exact finance evidence lookup with no browser tenant authority', async () => {
    mockGet.mockResolvedValueOnce({ data: financeResponse() });

    const result = await getLegalFinanceEvidence('INVOICE', 'invoice-1');

    expect(mockGet).toHaveBeenCalledWith(
      '/legal-operations/invoices/invoice-1',
    );
    expect(result).toEqual({
      tenantId: 'tenant-law',
      entityType: 'ClientInvoice',
      entityIdentity: 'invoice-1',
      visibility: 'FINANCE_VISIBLE',
      data: financeResponse().data,
    });
    expect(Object.isFrozen(result)).toBe(true);
    expect(Object.isFrozen(result.data)).toBe(true);
  });

  it('accepts D15 V2 first-class matters while preserving exact canonical matter truth', async () => {
    mockGet.mockResolvedValueOnce({ data: workspaceV2Payload() });

    const result = await getLegalPracticeWorkspace();

    expect(mockGet).toHaveBeenCalledWith('/legal-operations/workspace');
    expect(result.schema).toBe('WILSY-LEGAL-OPERATIONS-PRACTICE-WORKSPACE/V2');
    expect(result.version).toBe('v1.8.0-L8-7D15-FIRST-CLASS-MATTER-WORKSPACE-API');
    expect(result.summary).toEqual(expect.objectContaining({
      matters_total: 2,
      matters_open: 1,
      matters_closed: 1,
    }));
    expect(result.matters).toEqual([
      expect.objectContaining({
        case_matter_id: 'matter-1',
        matter_reference: 'CASE-2026-0001',
        state: 'OPEN',
      }),
      expect.objectContaining({
        case_matter_id: 'matter-2',
        matter_reference: 'CASE-2026-0002',
        state: 'CLOSED',
      }),
    ]);
    expect(Object.isFrozen(result)).toBe(true);
    expect(Object.isFrozen(result.matters)).toBe(true);
    expect(Object.isFrozen(result.matters[0])).toBe(true);
  });

  it.each([
    ['unsorted matter rows', (value) => value.matters.reverse()],
    ['extra matter field', (value) => { value.matters[0].client_name = 'forbidden'; }],
    ['invalid matter state', (value) => { value.matters[0].state = 'ARCHIVED'; }],
    ['invalid matter evidence', (value) => { value.matters[0].evidence_identity = 'bad'; }],
    ['matter summary drift', (value) => { value.summary.matters_open = 2; }],
    ['mixed V2 shape with V1 identity', (value) => {
      value.schema = 'WILSY-LEGAL-OPERATIONS-PRACTICE-WORKSPACE/V1';
      value.version = 'v1.7.0-L8-7D11-LEGAL-PRACTICE-WORKSPACE-API';
    }],
  ])('rejects D15 V2 %s fail-closed', async (_label, mutate) => {
    const value = workspaceV2Payload();
    mutate(value);
    mockGet.mockResolvedValueOnce({ data: value });

    await expect(getLegalPracticeWorkspace()).rejects.toThrow(
      /LEGAL_OPERATIONS_WORKSPACE_(?:RESPONSE_INVALID|SUMMARY_MISMATCH)/,
    );
  });

  it('posts exact initial-intake facts and rejects browser authority fields', async () => {
    mockPost.mockResolvedValueOnce({ data: intakeResponse() });

    const input = intakeInput();
    const result = await registerLegalIntake(input);

    expect(mockPost).toHaveBeenCalledWith(
      '/legal-operations/intake/registrations',
      {
        case_matter_id: input.caseMatterId,
        matter_reference: input.matterReference,
        case_opened_at: input.caseOpenedAt,
        matter_evidence_reference: input.matterEvidenceReference,
        instruction_id: input.instructionId,
        instruction_registered_at: input.instructionRegisteredAt,
        instruction_evidence_reference: input.instructionEvidenceReference,
        document_id: input.documentId,
        document_type: input.documentType,
        document_registered_at: input.documentRegisteredAt,
        document_registration_evidence_reference:
          input.documentRegistrationEvidenceReference,
        registration_custody_event_id: input.registrationCustodyEventId,
      },
    );
    expect(mockPost.mock.calls[0][1]).not.toHaveProperty('tenant_id');
    expect(mockPost.mock.calls[0][1]).not.toHaveProperty('principal_id');
    expect(mockPost.mock.calls[0][1]).not.toHaveProperty('role');
    expect(result.disposition).toBe('CREATED');
    expect(result.tenantId).toBe('tenant-law');
    expect(Object.isFrozen(result.caseMatter)).toBe(true);
  });

  it('rejects malformed intake chronology before network transport', async () => {
    const input = intakeInput();
    input.caseOpenedAt = '2026-09-23T16:00:00+00:00';
    input.instructionRegisteredAt = '2026-09-23T15:00:00+00:00';

    await expect(registerLegalIntake(input)).rejects.toThrow(
      'LEGAL_OPERATIONS_INTAKE_INPUT_INVALID',
    );
    expect(mockPost).not.toHaveBeenCalled();
  });

  it('generates ReturnOfService from exact server-issued execution evidence only', async () => {
    mockPost.mockResolvedValueOnce({ data: returnResponse() });

    const input = returnInput();
    const result = await generateLegalReturnOfService(input);

    expect(mockPost).toHaveBeenCalledWith(
      '/legal-operations/executions/execution-1/return',
      {
        execution_evidence_identity: input.executionEvidenceIdentity,
        return_id: input.returnId,
        generated_at: input.generatedAt,
      },
    );
    expect(mockPost.mock.calls[0][1]).not.toHaveProperty('tenant_id');
    expect(mockPost.mock.calls[0][1]).not.toHaveProperty('service_outcome');
    expect(result.returnId).toBe('return-1');
    expect(result.serviceOutcome).toBe('COMPLETED');
    expect(Object.isFrozen(result)).toBe(true);
  });

  it('keeps sheriff and deputy adapters distinct and non-financial', () => {
    const sheriff =
      __legalOperationsServiceInternals.assertCanonicalQueuePayload(payload());
    const deputy =
      __legalOperationsServiceInternals.assertCanonicalDeputyActiveWorkPayload(
        deputyPayload(),
      );

    expect(Object.keys(deputy).sort()).toEqual([
      'activeAttempts',
      'deputyId',
      'tenantId',
      'visibility',
    ]);
    expect(deputy).not.toHaveProperty('officeReceipt');
    expect(deputy).not.toHaveProperty('deputyAssignment');
    expect(sheriff).not.toHaveProperty('deputyId');

    const serialized = JSON.stringify({ sheriff, deputy }).toLowerCase();
    for (const forbidden of [
      'urgent',
      'distance',
      'gps',
      'billing',
      'invoice',
      'payment',
      'settlement',
      'revenue',
      'client_name',
      'ai_score',
    ]) {
      expect(serialized).not.toContain(forbidden);
    }

    expect(LEGAL_OPERATIONS_CLIENT_VERSION).toBe(
      'v1.8.0-L8-8N-CONFLICT-SCREENING-READ-CLIENT',
    );
  });
});

/**
 * ARTIFACT: legalOperationsService.test.js
 * VERSION: v2.3.0-L8-8N-CONFLICT-SCREENING-READ-CLIENT-CERT
 * AUTHORITY BOUNDARY: Legal Operations read/intake/return/deputy-command/conflict-review browser adapter certificate only
 * TENANT POSTURE: server tenant/principal/role/client/deputy scope remains authoritative; browser cannot create authorization scope
 * FAIL-CLOSED POSTURE: malformed/extra/missing/schema/version/order/scope/state/command-response drift rejects before presentation or transport success
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
