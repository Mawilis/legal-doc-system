/**
 * WILSY OS — ROLE-SCOPED LEGAL OPERATIONS CLIENT ADAPTER
 * VERSION: v1.5.0-L8-7D13-LEGAL-INTAKE-CLIENT
 * AUTHORITY: Browser transport validation and presentation adaptation only.
 * EPITOME: Authenticated browser adapter for certified Legal Operations reads,
 *          practice-workspace projection, exact finance evidence lookups,
 *          initial-intake registration, ReturnOfService generation and bound
 *          Deputy field commands. Browser input never establishes tenant,
 *          principal, role, lifecycle, service, money or settlement authority.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/services/legalOperationsService.js
 * COLLABORATION / OWNERSHIP: Python EOS IAM owns access authority; L8-5C owns
 *                            sheriff queues; L8-6B owns immutable binding; L8-6C
 *                            owns deputy work; L8-6D owns state capability; L8-6G
 *                            owns bound field-command composition and P5M lineage;
 *                            D5 owns the sanitized client-matter projection and
 *                            D6 owns authenticated snapshot transport. This adapter
 *                            owns exact browser response validation and immutable
 *                            presentation adaptation only.
 * CERTIFICATION / UPDATE DATE: 2026-09-23
 * CHANGELOG: 2026-09-23 v1.5.0-L8-7D13-LEGAL-INTAKE-CLIENT adds strict initial-intake registration
 *            transport for the existing L8-2 command. The request accepts only
 *            explicit opaque case/instruction/document/custody identities,
 *            timestamps, document type, matter reference and evidence
 *            references; tenant/principal/role remain server-derived. Response
 *            validation requires exact registration-only P1 facts and CREATED
 *            or REPLAYED disposition before presentation success.
 *            2026-09-23 v1.4.0-L8-7D12-LEGAL-PRACTICE-WORKSPACE-CLIENT adds exact GET /legal-operations/workspace
 *            validation/adaptation for the D11 legal-practice workspace,
 *            exact tariff-assessment/billing-eligibility/invoice read adapters,
 *            and the existing ReturnOfService generation command. Browser input
 *            never supplies tenant/principal/role, money, service outcome,
 *            payment or settlement truth.
 *            2026-09-23 v1.3.0-L8-7D7-CLIENT-MATTER-READ-CLIENT adds GET /legal-operations/client/matters,
 *            validates the exact D5 schema/version/visibility and exact four-field
 *            matter-card contract, rejects malformed/extra/missing/duplicate/
 *            unsorted matter evidence, maps only case ID/reference/opened time/
 *            OPEN-or-CLOSED state to immutable camelCase presentation data, and
 *            admits no browser-owned tenant/client/matter/role/visibility input.
 *            2026-09-23 v1.2.0-L8-6H-DEPUTY-FIELD-COMMAND-CLIENT adds exact deputy field-capability reads plus
 *            bound transition/outcome POST adapters. Request whitelists exclude
 *            tenant/principal/deputy authority, P5M sequence lineage, evidence
 *            fingerprints, receipt identity, execution identity/time, billing,
 *            AI, payment, and settlement truth. Command responses are validated
 *            against exact attempt/device/event scope and frozen before return.
 *            2026-09-23 v1.1.0-L8-6C-ROLE-SCOPED-LEGAL-OPERATIONS-CLIENT adds exact
 *            /legal-operations/deputy/active-work transport and fail-closed
 *            validation for tenant_id, DEPUTY_PERSONAL_ACTIVE_WORK visibility,
 *            canonical deputy_id, bound-deputy active attempts and
 *            ALLOCATED/ATTEMPTED states. Sheriff transport is unchanged.
 *            2026-09-23 v1.0.1-L8-6A-SHERIFF-QUEUE-CLIENT freezes each validated queue row as well as
 *            the aggregate and queue arrays; transport semantics are unchanged.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: No client-supplied tenant, principal, client,
 *                             matter, role, visibility, deputy, sequence lineage,
 *                             sovereign fingerprint, execution, billing, payment,
 *                             settlement, geospatial or AI truth is admitted.
 * TENANT BOUNDARY: Server response tenant remains authoritative; client-matter
 *                  rows carry no browser-selected tenant/client identity, while
 *                  deputy rows still match the server-bound canonical deputy_id.
 * AUTHORITY BOUNDARY: Read/command transport validation only. Browser role,
 *                     capability, visibility, observation or display state never
 *                     grants sheriff/deputy/client authority or creates legal,
 *                     service, billing or financial truth.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import api from './api.js';

export const LEGAL_OPERATIONS_CLIENT_VERSION =
  'v1.5.0-L8-7D13-LEGAL-INTAKE-CLIENT';

const QUEUE_KEYS = Object.freeze([
  'office_receipt',
  'deputy_assignment',
  'active_attempts',
]);

const RESPONSE_KEYS = Object.freeze([
  'tenant_id',
  'visibility',
  ...QUEUE_KEYS,
]);

const DEPUTY_RESPONSE_KEYS = Object.freeze([
  'tenant_id',
  'visibility',
  'deputy_id',
  'active_attempts',
]);

const ACTIVE_ATTEMPT_STATES = Object.freeze([
  'ALLOCATED',
  'ATTEMPTED',
]);

const CLIENT_MATTER_SCHEMA =
  'WILSY-LEGAL-CLIENT-MATTER-PROJECTION/V1';
const CLIENT_MATTER_VERSION =
  'v1.0.0-L8-7D5-CLIENT-MATTER-PROJECTION';
const CLIENT_MATTER_VISIBILITY =
  'LEGAL_CLIENT_EXPLICIT_MATTERS';
const CLIENT_MATTER_RESPONSE_KEYS = Object.freeze([
  'schema',
  'version',
  'tenant_id',
  'visibility',
  'matters',
]);
const CLIENT_MATTER_KEYS = Object.freeze([
  'case_matter_id',
  'matter_reference',
  'opened_at',
  'state',
]);
const CLIENT_MATTER_STATES = Object.freeze([
  'OPEN',
  'CLOSED',
]);

const LEGAL_WORKSPACE_SCHEMA =
  'WILSY-LEGAL-OPERATIONS-PRACTICE-WORKSPACE/V1';
const LEGAL_WORKSPACE_VERSION =
  'v1.7.0-L8-7D11-LEGAL-PRACTICE-WORKSPACE-API';
const LEGAL_WORKSPACE_VISIBILITY =
  'LEGAL_PRACTICE_WORKSPACE';

const LEGAL_WORKSPACE_RESPONSE_KEYS = Object.freeze([
  'schema',
  'version',
  'tenant_id',
  'visibility',
  'summary',
  'instructions',
  'documents',
  'attempts',
  'executions',
  'returns',
]);

const LEGAL_WORKSPACE_SUMMARY_KEYS = Object.freeze([
  'instructions_total',
  'instructions_registered',
  'instructions_accepted',
  'instructions_closed',
  'instructions_cancelled',
  'documents_total',
  'documents_registered',
  'documents_received',
  'documents_allocated',
  'documents_returned',
  'attempts_total',
  'attempts_allocated',
  'attempts_attempted',
  'attempts_completed',
  'attempts_not_completed',
  'attempts_cancelled',
  'executions_total',
  'executions_completed',
  'executions_not_completed',
  'returns_total',
]);

const LEGAL_WORKSPACE_ROW_KEYS = Object.freeze({
  instructions: Object.freeze([
    'instruction_id',
    'case_matter_id',
    'document_id',
    'registered_at',
    'state',
    'evidence_identity',
  ]),
  documents: Object.freeze([
    'document_id',
    'case_matter_id',
    'document_type',
    'registered_at',
    'state',
    'evidence_identity',
  ]),
  attempts: Object.freeze([
    'attempt_id',
    'instruction_id',
    'document_id',
    'deputy_id',
    'allocated_at',
    'state',
    'evidence_identity',
  ]),
  executions: Object.freeze([
    'service_execution_id',
    'attempt_id',
    'instruction_id',
    'document_id',
    'outcome',
    'executed_at',
    'evidence_identity',
  ]),
  returns: Object.freeze([
    'return_id',
    'instruction_id',
    'document_id',
    'attempt_id',
    'service_execution_id',
    'service_outcome',
    'generated_at',
    'state',
    'evidence_identity',
  ]),
});

const LEGAL_WORKSPACE_STATES = Object.freeze({
  instructions: Object.freeze(['REGISTERED', 'ACCEPTED', 'CLOSED', 'CANCELLED']),
  documents: Object.freeze([
    'REGISTERED',
    'RECEIVED',
    'ALLOCATED_TO_DEPUTY',
    'RETURNED_TO_CLIENT',
  ]),
  attempts: Object.freeze([
    'ALLOCATED',
    'ATTEMPTED',
    'COMPLETED',
    'NOT_COMPLETED',
    'CANCELLED',
  ]),
  executions: Object.freeze(['COMPLETED', 'NOT_COMPLETED']),
  returns: Object.freeze(['GENERATED']),
});

const LEGAL_FINANCE_KINDS = Object.freeze({
  TARIFF_ASSESSMENT: Object.freeze({
    route: 'tariff-assessments',
    entityType: 'TariffAssessment',
  }),
  BILLING_ELIGIBILITY: Object.freeze({
    route: 'billing-eligibilities',
    entityType: 'ProcessServiceBillingEligibility',
  }),
  INVOICE: Object.freeze({
    route: 'invoices',
    entityType: 'ClientInvoice',
  }),
});

const LEGAL_INTAKE_INPUT_KEYS = Object.freeze([
  'caseMatterId',
  'matterReference',
  'caseOpenedAt',
  'matterEvidenceReference',
  'instructionId',
  'instructionRegisteredAt',
  'instructionEvidenceReference',
  'documentId',
  'documentType',
  'documentRegisteredAt',
  'documentRegistrationEvidenceReference',
  'registrationCustodyEventId',
]);

const P1_BASE_KEYS = Object.freeze(['schema', 'version', 'entity_type', 'tenant_id']);
const LEGAL_INTAKE_RESPONSE_KEYS = Object.freeze([
  'disposition',
  'case_matter',
  'instruction',
  'document',
  'custody_event',
]);


const DEPUTY_CAPABILITY_RESPONSE_KEYS = Object.freeze([
  'tenant_id',
  'visibility',
  'deputy_id',
  'capabilities',
]);

const DEPUTY_CAPABILITY_KEYS = Object.freeze([
  'tenant_id',
  'attempt_id',
  'instruction_id',
  'document_id',
  'deputy_id',
  'current_state',
  'current_evidence_identity',
  'next_command_kinds',
]);

const FIELD_COMMAND_KINDS = Object.freeze({
  TRANSITION_TO_ATTEMPTED: 'TRANSITION_TO_ATTEMPTED',
  RECORD_COMPLETED_OUTCOME: 'RECORD_COMPLETED_OUTCOME',
  RECORD_NOT_COMPLETED_OUTCOME: 'RECORD_NOT_COMPLETED_OUTCOME',
});

const COMMANDS_BY_STATE = Object.freeze({
  ALLOCATED: Object.freeze([
    FIELD_COMMAND_KINDS.TRANSITION_TO_ATTEMPTED,
  ]),
  ATTEMPTED: Object.freeze([
    FIELD_COMMAND_KINDS.RECORD_COMPLETED_OUTCOME,
    FIELD_COMMAND_KINDS.RECORD_NOT_COMPLETED_OUTCOME,
  ]),
});

const FIELD_OBSERVATION_KEYS = Object.freeze([
  'attemptId',
  'currentEvidenceIdentity',
  'deviceId',
  'eventId',
  'occurredAt',
  'observationReference',
]);

const FIELD_OUTCOME_KEYS = Object.freeze([
  ...FIELD_OBSERVATION_KEYS,
  'outcome',
]);

const FIELD_RECEIPT_KEYS = Object.freeze([
  'tenant_id',
  'receipt_id',
  'event_id',
  'device_id',
  'sequence_number',
  'attempt_id',
  'instruction_id',
  'document_id',
  'deputy_id',
  'district_id',
  'sheriff_office_id',
  'evidence_reference',
  'evidence_fingerprint',
  'command_fingerprint',
  'accepted_at',
  'evidence_identity',
]);

const SERVICE_ATTEMPT_KEYS = Object.freeze([
  'schema',
  'version',
  'entity_type',
  'tenant_id',
  'attempt_id',
  'instruction_id',
  'document_id',
  'deputy_id',
  'allocated_at',
  'allocation_evidence_reference',
  'state',
  'transition_history',
]);

const SERVICE_EXECUTION_KEYS = Object.freeze([
  'schema',
  'version',
  'entity_type',
  'tenant_id',
  'service_execution_id',
  'attempt_id',
  'instruction_id',
  'document_id',
  'outcome',
  'executed_at',
  'evidence_reference',
  'evidence_fingerprint',
]);

const SHA3_512_PATTERN = /^[0-9a-f]{128}$/;
const TERMINAL_OUTCOMES = Object.freeze(['COMPLETED', 'NOT_COMPLETED']);

function isPlainObject(value) {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}


function assertExactKeys(value, expectedKeys, errorCode) {
  if (!isPlainObject(value)) {
    throw new Error(errorCode);
  }
  const keys = Object.keys(value).sort();
  const expected = [...expectedKeys].sort();
  if (
    keys.length !== expected.length
    || keys.some((key, index) => key !== expected[index])
  ) {
    throw new Error(errorCode);
  }
}

function isCanonicalText(value) {
  return typeof value === 'string' && value.trim() === value && Boolean(value);
}

function isCanonicalTimestamp(value) {
  if (!isCanonicalText(value)) return false;
  if (!/(?:Z|[+-]\d{2}:\d{2})$/.test(value)) return false;
  return Number.isFinite(Date.parse(value));
}

function freezeValue(value) {
  if (Array.isArray(value)) {
    return Object.freeze(value.map((item) => freezeValue(item)));
  }
  if (isPlainObject(value)) {
    const frozen = Object.fromEntries(
      Object.entries(value).map(([key, item]) => [key, freezeValue(item)]),
    );
    return Object.freeze(frozen);
  }
  return value;
}

function assertCanonicalQueuePayload(value) {
  if (!isPlainObject(value)) {
    throw new Error('LEGAL_OPERATIONS_QUEUE_RESPONSE_INVALID');
  }

  const keys = Object.keys(value).sort();
  const expectedKeys = [...RESPONSE_KEYS].sort();
  if (
    keys.length !== expectedKeys.length
    || keys.some((key, index) => key !== expectedKeys[index])
  ) {
    throw new Error('LEGAL_OPERATIONS_QUEUE_RESPONSE_INVALID');
  }

  if (
    typeof value.tenant_id !== 'string'
    || !value.tenant_id.trim()
    || value.visibility !== 'SHERIFF_OPERATIONAL_QUEUE'
  ) {
    throw new Error('LEGAL_OPERATIONS_QUEUE_RESPONSE_INVALID');
  }

  for (const key of QUEUE_KEYS) {
    if (!Array.isArray(value[key])) {
      throw new Error('LEGAL_OPERATIONS_QUEUE_RESPONSE_INVALID');
    }
    for (const item of value[key]) {
      if (!isPlainObject(item) || typeof item.tenant_id !== 'string') {
        throw new Error('LEGAL_OPERATIONS_QUEUE_RESPONSE_INVALID');
      }
      if (item.tenant_id !== value.tenant_id) {
        throw new Error('LEGAL_OPERATIONS_QUEUE_TENANT_MISMATCH');
      }
    }
  }

  const immutableRows = (rows) => Object.freeze(
    rows.map((item) => Object.freeze({ ...item })),
  );

  return Object.freeze({
    tenantId: value.tenant_id,
    visibility: value.visibility,
    officeReceipt: immutableRows(value.office_receipt),
    deputyAssignment: immutableRows(value.deputy_assignment),
    activeAttempts: immutableRows(value.active_attempts),
  });
}

function assertCanonicalDeputyActiveWorkPayload(value) {
  if (!isPlainObject(value)) {
    throw new Error('LEGAL_OPERATIONS_DEPUTY_WORK_RESPONSE_INVALID');
  }

  const keys = Object.keys(value).sort();
  const expectedKeys = [...DEPUTY_RESPONSE_KEYS].sort();
  if (
    keys.length !== expectedKeys.length
    || keys.some((key, index) => key !== expectedKeys[index])
  ) {
    throw new Error('LEGAL_OPERATIONS_DEPUTY_WORK_RESPONSE_INVALID');
  }

  if (
    typeof value.tenant_id !== 'string'
    || !value.tenant_id.trim()
    || value.visibility !== 'DEPUTY_PERSONAL_ACTIVE_WORK'
    || typeof value.deputy_id !== 'string'
    || !value.deputy_id.trim()
    || !Array.isArray(value.active_attempts)
  ) {
    throw new Error('LEGAL_OPERATIONS_DEPUTY_WORK_RESPONSE_INVALID');
  }

  for (const item of value.active_attempts) {
    if (
      !isPlainObject(item)
      || item.tenant_id !== value.tenant_id
      || item.deputy_id !== value.deputy_id
      || !ACTIVE_ATTEMPT_STATES.includes(item.state)
    ) {
      throw new Error('LEGAL_OPERATIONS_DEPUTY_WORK_SCOPE_INVALID');
    }
  }

  return Object.freeze({
    tenantId: value.tenant_id,
    visibility: value.visibility,
    deputyId: value.deputy_id,
    activeAttempts: Object.freeze(
      value.active_attempts.map((item) => Object.freeze({ ...item })),
    ),
  });
}


function assertCanonicalClientMatterPayload(value) {
  assertExactKeys(
    value,
    CLIENT_MATTER_RESPONSE_KEYS,
    'LEGAL_OPERATIONS_CLIENT_MATTER_RESPONSE_INVALID',
  );
  if (
    value.schema !== CLIENT_MATTER_SCHEMA
    || value.version !== CLIENT_MATTER_VERSION
    || !isCanonicalText(value.tenant_id)
    || value.visibility !== CLIENT_MATTER_VISIBILITY
    || !Array.isArray(value.matters)
  ) {
    throw new Error('LEGAL_OPERATIONS_CLIENT_MATTER_RESPONSE_INVALID');
  }

  const seen = new Set();
  let priorKey = null;
  const matters = value.matters.map((entry) => {
    assertExactKeys(
      entry,
      CLIENT_MATTER_KEYS,
      'LEGAL_OPERATIONS_CLIENT_MATTER_RESPONSE_INVALID',
    );
    if (
      !isCanonicalText(entry.case_matter_id)
      || !isCanonicalText(entry.matter_reference)
      || !isCanonicalTimestamp(entry.opened_at)
      || !CLIENT_MATTER_STATES.includes(entry.state)
      || seen.has(entry.case_matter_id)
    ) {
      throw new Error('LEGAL_OPERATIONS_CLIENT_MATTER_SCOPE_INVALID');
    }
    const currentKey = `${entry.case_matter_id}\u0000${entry.matter_reference}`;
    if (priorKey !== null && currentKey < priorKey) {
      throw new Error('LEGAL_OPERATIONS_CLIENT_MATTER_SCOPE_INVALID');
    }
    priorKey = currentKey;
    seen.add(entry.case_matter_id);
    return Object.freeze({
      caseMatterId: entry.case_matter_id,
      matterReference: entry.matter_reference,
      openedAt: entry.opened_at,
      state: entry.state,
    });
  });

  return Object.freeze({
    schema: value.schema,
    version: value.version,
    tenantId: value.tenant_id,
    visibility: value.visibility,
    matters: Object.freeze(matters),
  });
}


function assertSha3(value, errorCode) {
  if (!SHA3_512_PATTERN.test(value)) {
    throw new Error(errorCode);
  }
  return value;
}

function assertSortedRows(rows, identityKey, errorCode) {
  let prior = null;
  for (const row of rows) {
    const current = row[identityKey];
    if (!isCanonicalText(current) || (prior !== null && current < prior)) {
      throw new Error(errorCode);
    }
    prior = current;
  }
}

function assertCanonicalLegalWorkspacePayload(value) {
  const errorCode = 'LEGAL_OPERATIONS_WORKSPACE_RESPONSE_INVALID';
  assertExactKeys(value, LEGAL_WORKSPACE_RESPONSE_KEYS, errorCode);
  if (
    value.schema !== LEGAL_WORKSPACE_SCHEMA
    || value.version !== LEGAL_WORKSPACE_VERSION
    || !isCanonicalText(value.tenant_id)
    || value.visibility !== LEGAL_WORKSPACE_VISIBILITY
    || !isPlainObject(value.summary)
  ) {
    throw new Error(errorCode);
  }

  assertExactKeys(value.summary, LEGAL_WORKSPACE_SUMMARY_KEYS, errorCode);
  for (const key of LEGAL_WORKSPACE_SUMMARY_KEYS) {
    if (
      !Number.isInteger(value.summary[key])
      || value.summary[key] < 0
    ) {
      throw new Error(errorCode);
    }
  }

  const identityKeys = {
    instructions: 'instruction_id',
    documents: 'document_id',
    attempts: 'attempt_id',
    executions: 'service_execution_id',
    returns: 'return_id',
  };

  const timestampKeys = {
    instructions: 'registered_at',
    documents: 'registered_at',
    attempts: 'allocated_at',
    executions: 'executed_at',
    returns: 'generated_at',
  };

  const stateKeys = {
    instructions: 'state',
    documents: 'state',
    attempts: 'state',
    executions: 'outcome',
    returns: 'state',
  };

  const arrays = {};
  for (const [name, expectedKeys] of Object.entries(LEGAL_WORKSPACE_ROW_KEYS)) {
    const rows = value[name];
    if (!Array.isArray(rows)) throw new Error(errorCode);
    assertSortedRows(rows, identityKeys[name], errorCode);

    arrays[name] = Object.freeze(rows.map((row) => {
      assertExactKeys(row, expectedKeys, errorCode);
      for (const [key, item] of Object.entries(row)) {
        if (key === 'evidence_identity') {
          assertSha3(item, errorCode);
        } else if (key === timestampKeys[name]) {
          if (!isCanonicalTimestamp(item)) throw new Error(errorCode);
        } else if (key === stateKeys[name]) {
          if (!LEGAL_WORKSPACE_STATES[name].includes(item)) {
            throw new Error(errorCode);
          }
        } else if (!isCanonicalText(item)) {
          throw new Error(errorCode);
        }
      }
      return Object.freeze({ ...row });
    }));
  }

  if (
    value.summary.instructions_total !== arrays.instructions.length
    || value.summary.documents_total !== arrays.documents.length
    || value.summary.attempts_total !== arrays.attempts.length
    || value.summary.executions_total !== arrays.executions.length
    || value.summary.returns_total !== arrays.returns.length
  ) {
    throw new Error('LEGAL_OPERATIONS_WORKSPACE_SUMMARY_MISMATCH');
  }

  return Object.freeze({
    schema: value.schema,
    version: value.version,
    tenantId: value.tenant_id,
    visibility: value.visibility,
    summary: Object.freeze({ ...value.summary }),
    instructions: arrays.instructions,
    documents: arrays.documents,
    attempts: arrays.attempts,
    executions: arrays.executions,
    returns: arrays.returns,
  });
}

function assertCanonicalFinanceEvidence(value, expectedEntityType) {
  const errorCode = 'LEGAL_OPERATIONS_FINANCE_RESPONSE_INVALID';
  assertExactKeys(
    value,
    ['tenant_id', 'entity_type', 'entity_identity', 'visibility', 'data'],
    errorCode,
  );
  if (
    !isCanonicalText(value.tenant_id)
    || value.entity_type !== expectedEntityType
    || !isCanonicalText(value.entity_identity)
    || value.visibility !== 'FINANCE_VISIBLE'
    || !isPlainObject(value.data)
  ) {
    throw new Error(errorCode);
  }
  return Object.freeze({
    tenantId: value.tenant_id,
    entityType: value.entity_type,
    entityIdentity: value.entity_identity,
    visibility: value.visibility,
    data: freezeValue(value.data),
  });
}

function assertReturnCommandInput(value) {
  const errorCode = 'LEGAL_OPERATIONS_RETURN_COMMAND_INPUT_INVALID';
  assertExactKeys(
    value,
    ['executionId', 'executionEvidenceIdentity', 'returnId', 'generatedAt'],
    errorCode,
  );
  if (
    !isCanonicalText(value.executionId)
    || !SHA3_512_PATTERN.test(value.executionEvidenceIdentity)
    || !isCanonicalText(value.returnId)
    || !isCanonicalTimestamp(value.generatedAt)
  ) {
    throw new Error(errorCode);
  }
  return Object.freeze({ ...value });
}

function assertCanonicalReturnCommandResponse(value, input) {
  const errorCode = 'LEGAL_OPERATIONS_RETURN_COMMAND_RESPONSE_INVALID';
  assertExactKeys(value, ['data'], errorCode);
  const data = value.data;
  if (!isPlainObject(data)) throw new Error(errorCode);
  const required = [
    'schema',
    'version',
    'entity_type',
    'tenant_id',
    'return_id',
    'instruction_id',
    'document_id',
    'attempt_id',
    'service_execution_id',
    'service_outcome',
    'service_evidence_reference',
    'service_evidence_fingerprint',
    'generated_at',
    'state',
  ];
  assertExactKeys(data, required, errorCode);
  if (
    data.entity_type !== 'ReturnOfService'
    || data.return_id !== input.returnId
    || data.service_execution_id !== input.executionId
    || !isCanonicalText(data.tenant_id)
    || !isCanonicalText(data.instruction_id)
    || !isCanonicalText(data.document_id)
    || !isCanonicalText(data.attempt_id)
    || !['COMPLETED', 'NOT_COMPLETED'].includes(data.service_outcome)
    || !isCanonicalTimestamp(data.generated_at)
    || data.state !== 'GENERATED'
    || !SHA3_512_PATTERN.test(data.service_evidence_fingerprint)
  ) {
    throw new Error(errorCode);
  }
  return Object.freeze({
    tenantId: data.tenant_id,
    returnId: data.return_id,
    instructionId: data.instruction_id,
    documentId: data.document_id,
    attemptId: data.attempt_id,
    serviceExecutionId: data.service_execution_id,
    serviceOutcome: data.service_outcome,
    generatedAt: data.generated_at,
    state: data.state,
  });
}


function assertRegistrationSnapshot(
  value,
  {
    entityType,
    expectedKeys,
    stateKey = null,
    stateValue = null,
    expectedIdentity = null,
    identityKey = null,
  },
) {
  const errorCode = 'LEGAL_OPERATIONS_INTAKE_RESPONSE_INVALID';
  assertExactKeys(value, [...P1_BASE_KEYS, ...expectedKeys], errorCode);
  if (
    value.schema !== 'WILSY-LEGAL-OPERATIONS-LIFECYCLE/V1'
    || value.version !== 'v1.0.0-LEGAL-OPERATIONS-LIFECYCLE'
    || value.entity_type !== entityType
    || !isCanonicalText(value.tenant_id)
  ) {
    throw new Error(errorCode);
  }
  if (
    identityKey
    && (
      !isCanonicalText(value[identityKey])
      || (expectedIdentity && value[identityKey] !== expectedIdentity)
    )
  ) {
    throw new Error(errorCode);
  }
  if (stateKey && value[stateKey] !== stateValue) {
    throw new Error(errorCode);
  }
  if ('transition_history' in value && (
    !Array.isArray(value.transition_history)
    || value.transition_history.length !== 0
  )) {
    throw new Error(errorCode);
  }
  return value;
}

function assertLegalIntakeInput(value) {
  const errorCode = 'LEGAL_OPERATIONS_INTAKE_INPUT_INVALID';
  assertExactKeys(value, LEGAL_INTAKE_INPUT_KEYS, errorCode);
  for (const key of [
    'caseMatterId',
    'matterReference',
    'matterEvidenceReference',
    'instructionId',
    'instructionEvidenceReference',
    'documentId',
    'documentType',
    'documentRegistrationEvidenceReference',
    'registrationCustodyEventId',
  ]) {
    if (!isCanonicalText(value[key])) throw new Error(errorCode);
  }
  for (const key of [
    'caseOpenedAt',
    'instructionRegisteredAt',
    'documentRegisteredAt',
  ]) {
    if (!isCanonicalTimestamp(value[key])) throw new Error(errorCode);
  }
  if (
    Date.parse(value.caseOpenedAt) > Date.parse(value.instructionRegisteredAt)
    || Date.parse(value.instructionRegisteredAt) > Date.parse(value.documentRegisteredAt)
  ) {
    throw new Error(errorCode);
  }
  return Object.freeze({ ...value });
}

function assertCanonicalLegalIntakeResponse(value, input) {
  const errorCode = 'LEGAL_OPERATIONS_INTAKE_RESPONSE_INVALID';
  assertExactKeys(value, LEGAL_INTAKE_RESPONSE_KEYS, errorCode);
  if (!['CREATED', 'REPLAYED'].includes(value.disposition)) {
    throw new Error(errorCode);
  }

  const matter = assertRegistrationSnapshot(value.case_matter, {
    entityType: 'CaseMatter',
    identityKey: 'case_matter_id',
    expectedIdentity: input.caseMatterId,
    stateKey: 'state',
    stateValue: 'OPEN',
    expectedKeys: [
      'case_matter_id',
      'matter_reference',
      'opened_at',
      'evidence_reference',
      'state',
      'transition_history',
    ],
  });
  const instruction = assertRegistrationSnapshot(value.instruction, {
    entityType: 'LegalInstruction',
    identityKey: 'instruction_id',
    expectedIdentity: input.instructionId,
    stateKey: 'state',
    stateValue: 'REGISTERED',
    expectedKeys: [
      'instruction_id',
      'case_matter_id',
      'document_id',
      'registered_at',
      'evidence_reference',
      'state',
      'transition_history',
    ],
  });
  const document = assertRegistrationSnapshot(value.document, {
    entityType: 'ProcessDocument',
    identityKey: 'document_id',
    expectedIdentity: input.documentId,
    stateKey: 'state',
    stateValue: 'REGISTERED',
    expectedKeys: [
      'document_id',
      'case_matter_id',
      'document_type',
      'registered_at',
      'registration_evidence_reference',
      'state',
      'transition_history',
    ],
  });
  const custody = assertRegistrationSnapshot(value.custody_event, {
    entityType: 'DocumentCustodyEvent',
    identityKey: 'custody_event_id',
    expectedIdentity: input.registrationCustodyEventId,
    expectedKeys: [
      'custody_event_id',
      'document_id',
      'event_type',
      'occurred_at',
      'sequence_number',
      'evidence_reference',
      'from_holder_reference',
      'to_holder_reference',
    ],
  });

  if (
    matter.matter_reference !== input.matterReference
    || matter.opened_at !== input.caseOpenedAt
    || matter.evidence_reference !== input.matterEvidenceReference
    || instruction.case_matter_id !== input.caseMatterId
    || instruction.document_id !== input.documentId
    || instruction.registered_at !== input.instructionRegisteredAt
    || instruction.evidence_reference !== input.instructionEvidenceReference
    || document.case_matter_id !== input.caseMatterId
    || document.document_type !== input.documentType
    || document.registered_at !== input.documentRegisteredAt
    || document.registration_evidence_reference
      !== input.documentRegistrationEvidenceReference
    || custody.document_id !== input.documentId
    || custody.event_type !== 'REGISTERED'
    || custody.occurred_at !== input.documentRegisteredAt
    || custody.sequence_number !== 1
    || custody.evidence_reference !== input.documentRegistrationEvidenceReference
    || custody.from_holder_reference !== null
    || custody.to_holder_reference !== null
    || new Set([
      matter.tenant_id,
      instruction.tenant_id,
      document.tenant_id,
      custody.tenant_id,
    ]).size !== 1
  ) {
    throw new Error(errorCode);
  }

  return Object.freeze({
    disposition: value.disposition,
    tenantId: matter.tenant_id,
    caseMatter: freezeValue(matter),
    instruction: freezeValue(instruction),
    document: freezeValue(document),
    custodyEvent: freezeValue(custody),
  });
}


function assertCanonicalDeputyFieldCapabilitiesPayload(value) {
  assertExactKeys(
    value,
    DEPUTY_CAPABILITY_RESPONSE_KEYS,
    'LEGAL_OPERATIONS_DEPUTY_CAPABILITY_RESPONSE_INVALID',
  );
  if (
    !isCanonicalText(value.tenant_id)
    || value.visibility !== 'DEPUTY_FIELD_COMMAND_CAPABILITIES'
    || !isCanonicalText(value.deputy_id)
    || !Array.isArray(value.capabilities)
  ) {
    throw new Error('LEGAL_OPERATIONS_DEPUTY_CAPABILITY_RESPONSE_INVALID');
  }

  const capabilities = value.capabilities.map((entry) => {
    assertExactKeys(
      entry,
      DEPUTY_CAPABILITY_KEYS,
      'LEGAL_OPERATIONS_DEPUTY_CAPABILITY_RESPONSE_INVALID',
    );
    const expectedKinds = COMMANDS_BY_STATE[entry.current_state];
    if (
      entry.tenant_id !== value.tenant_id
      || entry.deputy_id !== value.deputy_id
      || !isCanonicalText(entry.attempt_id)
      || !isCanonicalText(entry.instruction_id)
      || !isCanonicalText(entry.document_id)
      || !expectedKinds
      || !SHA3_512_PATTERN.test(entry.current_evidence_identity)
      || !Array.isArray(entry.next_command_kinds)
      || entry.next_command_kinds.length !== expectedKinds.length
      || entry.next_command_kinds.some(
        (kind, index) => kind !== expectedKinds[index],
      )
    ) {
      throw new Error('LEGAL_OPERATIONS_DEPUTY_CAPABILITY_SCOPE_INVALID');
    }
    return Object.freeze({
      tenantId: entry.tenant_id,
      attemptId: entry.attempt_id,
      instructionId: entry.instruction_id,
      documentId: entry.document_id,
      deputyId: entry.deputy_id,
      currentState: entry.current_state,
      currentEvidenceIdentity: entry.current_evidence_identity,
      nextCommandKinds: Object.freeze([...entry.next_command_kinds]),
    });
  });

  return Object.freeze({
    tenantId: value.tenant_id,
    visibility: value.visibility,
    deputyId: value.deputy_id,
    capabilities: Object.freeze(capabilities),
  });
}

function assertFieldObservationInput(value, { terminal = false } = {}) {
  const keys = terminal ? FIELD_OUTCOME_KEYS : FIELD_OBSERVATION_KEYS;
  assertExactKeys(
    value,
    keys,
    'LEGAL_OPERATIONS_FIELD_COMMAND_INPUT_INVALID',
  );
  if (
    !isCanonicalText(value.attemptId)
    || !SHA3_512_PATTERN.test(value.currentEvidenceIdentity)
    || !isCanonicalText(value.deviceId)
    || !isCanonicalText(value.eventId)
    || !isCanonicalTimestamp(value.occurredAt)
    || !isCanonicalText(value.observationReference)
    || (
      terminal
      && !TERMINAL_OUTCOMES.includes(value.outcome)
    )
  ) {
    throw new Error('LEGAL_OPERATIONS_FIELD_COMMAND_INPUT_INVALID');
  }
  return Object.freeze({ ...value });
}

function assertCanonicalFieldReceipt(value, input) {
  assertExactKeys(
    value,
    FIELD_RECEIPT_KEYS,
    'LEGAL_OPERATIONS_FIELD_COMMAND_RESPONSE_INVALID',
  );
  if (
    !isCanonicalText(value.tenant_id)
    || value.attempt_id !== input.attemptId
    || value.device_id !== input.deviceId
    || value.event_id !== input.eventId
    || !Number.isInteger(value.sequence_number)
    || value.sequence_number < 1
    || !SHA3_512_PATTERN.test(value.evidence_fingerprint)
    || !SHA3_512_PATTERN.test(value.command_fingerprint)
    || !SHA3_512_PATTERN.test(value.evidence_identity)
    || !isCanonicalTimestamp(value.accepted_at)
  ) {
    throw new Error('LEGAL_OPERATIONS_FIELD_COMMAND_RESPONSE_INVALID');
  }
  return freezeValue(value);
}

function assertCanonicalFieldCommandResponse(value, input, { terminal = false } = {}) {
  assertExactKeys(
    value,
    ['data', 'field_evidence'],
    'LEGAL_OPERATIONS_FIELD_COMMAND_RESPONSE_INVALID',
  );
  const receipt = assertCanonicalFieldReceipt(value.field_evidence, input);
  const data = value.data;
  const expectedKeys = terminal ? SERVICE_EXECUTION_KEYS : SERVICE_ATTEMPT_KEYS;
  assertExactKeys(
    data,
    expectedKeys,
    'LEGAL_OPERATIONS_FIELD_COMMAND_RESPONSE_INVALID',
  );

  if (
    data.tenant_id !== receipt.tenant_id
    || data.attempt_id !== input.attemptId
    || (
      terminal
        ? (
          data.entity_type !== 'ServiceExecution'
          || data.outcome !== input.outcome
          || !SHA3_512_PATTERN.test(data.evidence_fingerprint)
          || data.evidence_fingerprint !== receipt.evidence_fingerprint
        )
        : (
          data.entity_type !== 'ServiceAttempt'
          || data.state !== 'ATTEMPTED'
        )
    )
  ) {
    throw new Error('LEGAL_OPERATIONS_FIELD_COMMAND_RESPONSE_INVALID');
  }

  return Object.freeze({
    data: freezeValue(data),
    fieldEvidence: receipt,
  });
}

function toFieldCommandBody(input, { terminal = false } = {}) {
  const body = {
    current_evidence_identity: input.currentEvidenceIdentity,
    device_id: input.deviceId,
    event_id: input.eventId,
    occurred_at: input.occurredAt,
    observation_reference: input.observationReference,
  };
  if (terminal) body.outcome = input.outcome;
  return Object.freeze(body);
}

export async function registerLegalIntake(value) {
  const input = assertLegalIntakeInput(value);
  const response = await api.post('/legal-operations/intake/registrations', {
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
  });
  return assertCanonicalLegalIntakeResponse(response?.data, input);
}


export async function getLegalPracticeWorkspace() {
  const response = await api.get('/legal-operations/workspace');
  return assertCanonicalLegalWorkspacePayload(response?.data);
}

export async function getLegalFinanceEvidence(kind, identity) {
  const contract = LEGAL_FINANCE_KINDS[kind];
  if (!contract || !isCanonicalText(identity)) {
    throw new Error('LEGAL_OPERATIONS_FINANCE_LOOKUP_INPUT_INVALID');
  }
  const response = await api.get(
    `/legal-operations/${contract.route}/${encodeURIComponent(identity)}`,
  );
  return assertCanonicalFinanceEvidence(
    response?.data,
    contract.entityType,
  );
}

export async function generateLegalReturnOfService(value) {
  const input = assertReturnCommandInput(value);
  const response = await api.post(
    `/legal-operations/executions/${encodeURIComponent(input.executionId)}/return`,
    {
      execution_evidence_identity: input.executionEvidenceIdentity,
      return_id: input.returnId,
      generated_at: input.generatedAt,
    },
  );
  return assertCanonicalReturnCommandResponse(response?.data, input);
}


export async function getSheriffOperationalQueues() {
  const response = await api.get('/legal-operations/operational-queues');
  return assertCanonicalQueuePayload(response?.data);
}

export async function getDeputyPersonalActiveWork() {
  const response = await api.get('/legal-operations/deputy/active-work');
  return assertCanonicalDeputyActiveWorkPayload(response?.data);
}


export async function getDeputyFieldCapabilities() {
  const response = await api.get('/legal-operations/deputy/field-capabilities');
  return assertCanonicalDeputyFieldCapabilitiesPayload(response?.data);
}

export async function getLegalClientMatters() {
  const response = await api.get('/legal-operations/client/matters');
  return assertCanonicalClientMatterPayload(response?.data);
}

export async function transitionDeputyFieldAttempt(value) {
  const input = assertFieldObservationInput(value);
  const response = await api.post(
    `/legal-operations/deputy/attempts/${encodeURIComponent(input.attemptId)}/transition`,
    toFieldCommandBody(input),
  );
  return assertCanonicalFieldCommandResponse(response?.data, input);
}

export async function recordDeputyFieldOutcome(value) {
  const input = assertFieldObservationInput(value, { terminal: true });
  const response = await api.post(
    `/legal-operations/deputy/attempts/${encodeURIComponent(input.attemptId)}/outcome`,
    toFieldCommandBody(input, { terminal: true }),
  );
  return assertCanonicalFieldCommandResponse(
    response?.data,
    input,
    { terminal: true },
  );
}

export const __legalOperationsServiceInternals = Object.freeze({
  assertCanonicalQueuePayload,
  assertCanonicalDeputyActiveWorkPayload,
  assertCanonicalDeputyFieldCapabilitiesPayload,
  assertCanonicalClientMatterPayload,
  assertFieldObservationInput,
  assertCanonicalFieldCommandResponse,
  toFieldCommandBody,
  QUEUE_KEYS,
  RESPONSE_KEYS,
  DEPUTY_RESPONSE_KEYS,
  ACTIVE_ATTEMPT_STATES,
  CLIENT_MATTER_SCHEMA,
  CLIENT_MATTER_VERSION,
  CLIENT_MATTER_VISIBILITY,
  CLIENT_MATTER_RESPONSE_KEYS,
  CLIENT_MATTER_KEYS,
  CLIENT_MATTER_STATES,
  assertLegalIntakeInput,
  assertCanonicalLegalIntakeResponse,
  LEGAL_INTAKE_INPUT_KEYS,
  LEGAL_INTAKE_RESPONSE_KEYS,
  assertCanonicalLegalWorkspacePayload,
  assertCanonicalFinanceEvidence,
  assertReturnCommandInput,
  assertCanonicalReturnCommandResponse,
  LEGAL_WORKSPACE_SCHEMA,
  LEGAL_WORKSPACE_VERSION,
  LEGAL_WORKSPACE_VISIBILITY,
  LEGAL_WORKSPACE_RESPONSE_KEYS,
  LEGAL_WORKSPACE_SUMMARY_KEYS,
  LEGAL_WORKSPACE_ROW_KEYS,
  LEGAL_WORKSPACE_STATES,
  LEGAL_FINANCE_KINDS,
  DEPUTY_CAPABILITY_RESPONSE_KEYS,
  DEPUTY_CAPABILITY_KEYS,
  FIELD_COMMAND_KINDS,
  COMMANDS_BY_STATE,
  FIELD_OBSERVATION_KEYS,
  FIELD_OUTCOME_KEYS,
  FIELD_RECEIPT_KEYS,
});

/**
 * ARTIFACT: legalOperationsService.js
 * VERSION: v1.5.0-L8-7D13-LEGAL-INTAKE-CLIENT
 * AUTHORITY BOUNDARY: role-scoped Legal Operations read/intake/return/deputy-command browser transport validation only
 * TENANT POSTURE: server tenant/client/deputy scope remains authoritative; browser cannot establish tenant, client or matter authority
 * FAIL-CLOSED POSTURE: malformed/extra/missing/scope/state/schema/version/order/command-response drift rejects without fallback
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
