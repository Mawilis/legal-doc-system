/**
 * WILSY OS — ROLE-SCOPED LEGAL OPERATIONS CLIENT CERTIFICATE
 * VERSION: v1.3.0-L8-7D7-CLIENT-MATTER-READ-CLIENT-CERT
 * AUTHORITY: Client transport-adapter contract certification only.
 * EPITOME: Certifies sheriff/deputy reads and deputy field commands plus the
 *          D7 LEGAL_CLIENT matter adapter, including exact D6 endpoint use,
 *          D5 schema/version/field validation, immutable safe-card adaptation,
 *          and exclusion of browser-owned scope, lifecycle, evidence, billing,
 *          AI, payment, execution or settlement truth.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/services/legalOperationsService.test.js
 * CERTIFICATION / UPDATE DATE: 2026-09-23
 * CHANGELOG: 2026-09-23 v1.3.0-L8-7D7-CLIENT-MATTER-READ-CLIENT-CERT certifies exact
 *            /legal-operations/client/matters GET transport, D5 schema/version/
 *            visibility binding, exact four-field matter cards, deterministic
 *            order/uniqueness, malformed/extra-field rejection, deep freezing,
 *            zero browser request authority, and production v1.3.0-L8-7D7-CLIENT-MATTER-READ-CLIENT alignment.
2026-09-23 v1.2.0-L8-6H-DEPUTY-FIELD-COMMAND-CLIENT-CERT certifies exact field-capability GET transport,
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

const { mockGet, mockPost } = vi.hoisted(() => ({
  mockGet: vi.fn(),
  mockPost: vi.fn(),
}));

vi.mock('../../services/api.js', () => ({
  default: {
    get: mockGet,
    post: mockPost,
  },
}));

import {
  LEGAL_OPERATIONS_CLIENT_VERSION,
  __legalOperationsServiceInternals,
  getDeputyFieldCapabilities,
  getDeputyPersonalActiveWork,
  getLegalClientMatters,
  getSheriffOperationalQueues,
  recordDeputyFieldOutcome,
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

describe('L8-7D7 role-scoped Legal Operations client adapter', () => {
  beforeEach(() => {
    vi.clearAllMocks();
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
      'v1.3.0-L8-7D7-CLIENT-MATTER-READ-CLIENT',
    );
  });
});

/**
 * ARTIFACT: legalOperationsService.test.js
 * VERSION: v1.3.0-L8-7D7-CLIENT-MATTER-READ-CLIENT-CERT
 * AUTHORITY BOUNDARY: sheriff/deputy/client read and bound deputy field-command browser adapter certificate only
 * TENANT POSTURE: server client/tenant/deputy scope is authoritative; browser cannot create client or matter scope
 * FAIL-CLOSED POSTURE: malformed/extra/missing/schema/version/order/scope/state/command-response drift rejects before presentation or transport success
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
