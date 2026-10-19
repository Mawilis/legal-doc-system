/**
 * WILSY OS — ROLE-SCOPED LEGAL OPERATIONS CLIENT ADAPTER
 * VERSION: v2.2.0-P8-LEGAL-WORK-COMPLETION-BROWSER-TRANSPORT
 * AUTHORITY: Browser transport validation and presentation adaptation only.
 * EPITOME: Authenticated browser adapter for certified Legal Operations reads,
 *          practice-workspace projection, exact finance evidence lookups,
 *          initial-intake registration, conflict-review issuance, ReturnOfService
 *          generation and bound Deputy field commands. Browser input never establishes tenant,
 *          principal, role, lifecycle, service, money or settlement authority.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/services/legalOperationsService.js
 * COLLABORATION / OWNERSHIP: Python EOS IAM owns access authority; L8-5C owns
 *                            sheriff queues; L8-6B/C/D/G own deputy binding/work/
 *                            capability/field-command lineage; D5/D6 own the
 *                            sanitized client-matter projection/transport; D11
 *                            owns the practice workspace projection; existing
 *                            finance-read and command routers own tariff/billing/
 *                            invoice evidence, intake and ReturnOfService HTTP
 *                            authority. This adapter owns strict browser transport
 *                            validation and immutable presentation adaptation only.
 * CERTIFICATION / UPDATE DATE: 2026-10-19
 * CHANGELOG: 2026-10-19 v2.2.0-P8-LEGAL-WORK-COMPLETION-BROWSER-TRANSPORT adds one authenticated authority-free work-completion browser command, strict three-field input whitelist, exact canonical server endpoint, opaque evidence only, and response work-item binding. Server retains tenant, principal, authorization, assignment, transaction, timestamp and durable completion truth.
 *            2026-10-16 v2.1.0-LEGAL-COMMERCIAL-CONTEXT-BROWSER-TRANSPORT adds one strict authenticated GET /legal-operations/commercial-context adapter. It validates the exact server-owned product/subscription/plan/commercial contract, preserves 401/403 as access denial, rejects malformed or extra commercial fields, accepts no tenant/plan/subscription/price selector, and creates no IAM, Legal, payment or settlement authority.
 *            2026-10-12 v2.0.0-LEGAL-EVIDENCE-UPLOAD-BROWSER-TRANSPORT adds one governed FormData upload command carrying only the selected file, document path identity, and idempotency header; it sets no multipart boundary and validates bounded canonical commit/reconciliation evidence.
 *            2026-09-25 v1.9.0-LEGAL-CLIENT-ACCEPTANCE-BROWSER-TRANSPORT adds the authenticated bounded conflict-screening review-queue read adapter. It accepts no tenant input, validates exact server-owned screening identity/status/matter/timestamp rows, preserves deterministic order and excludes screening evidence, party data, review/IAM and financial authority.
 *            2026-09-25 v1.7.0-L8-8L-CONFLICT-REVIEW-COMMAND-CLIENT adds the single authenticated conflict-review command adapter. It sends only the four human-choice fields through sovereignClient so the legacy api.js body-timestamp interceptor cannot mutate the strict command contract. Server-owned tenant, reviewer, chronology, screening, authorization, party and financial authority remain excluded.
 *            2026-09-24 v1.6.0-L8-7D15-MATTER-WORKSPACE-COMPATIBILITY adds a zero-break dual-contract bridge: the existing D11 V1 workspace remains exact and unchanged, while D15 V2 is admitted only when canonical CaseMatter rows and matter summary counts are present, sorted, exact-keyed, evidence-bound and internally consistent. No browser tenant, matter, lifecycle or financial authority is added.
 *            2026-09-24 v1.5.1-L8-7D14-WORKSPACE-SUMMARY-VALIDATION recomputes every D11 workspace state/outcome
 *            summary counter from the validated canonical rows before exposing
 *            dashboard metrics. Total-only consistency is no longer sufficient;
 *            any state-breakdown drift rejects fail-closed without fallback.
 *            Transport endpoints and authority semantics are unchanged.
 *            2026-09-23 v1.5.0-L8-7D13-LEGAL-INTAKE-CLIENT adds strict initial-intake registration
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
 * TENANT BOUNDARY: Server response tenant remains authoritative across practice,
 *                  finance, client and deputy projections. Browser requests never
 *                  select tenant/principal/role authority; deputy rows remain
 *                  bound to the server-authorized canonical deputy identity.
 * AUTHORITY BOUNDARY: Read/intake/return/deputy-command transport validation
 *                     only. Browser role, menu, capability, generated opaque IDs,
 *                     visibility, observation or display state never grants legal
 *                     practice, sheriff, deputy, finance or client authority and
 *                     never creates service, billing, payment or settlement truth.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import api from './api.js';
import sovereignClient from '../utils/sovereignClient.js';

export const LEGAL_OPERATIONS_CLIENT_VERSION =
  'v2.2.0-P8-LEGAL-WORK-COMPLETION-BROWSER-TRANSPORT';

const CONFLICT_REVIEW_INPUT_KEYS = Object.freeze([
  'screeningId',
  'reviewId',
  'outcome',
  'reviewReasonReference',
]);
const CONFLICT_REVIEW_RESPONSE_KEYS = Object.freeze([
  'review_id',
  'screening_id',
  'outcome',
  'reviewed_at',
  'fingerprint',
]);
const CONFLICT_REVIEW_OUTCOMES = Object.freeze([
  'CONFLICT_IDENTIFIED',
  'NO_CONFLICT_IDENTIFIED',
  'ESCALATION_REQUIRED',
]);

const LEGAL_COMMERCIAL_CONTEXT_SCHEMA =
  'WILSY-LEGAL-OPERATIONS-COMMERCIAL-CONTEXT/V1';
const LEGAL_COMMERCIAL_CONTEXT_VERSION =
  'v1.0.0-LEGAL-COMMERCIAL-CONTEXT-HTTP';
const LEGAL_COMMERCIAL_CONTEXT_VISIBILITY =
  'LEGAL_COMMERCIAL_CONTEXT_SUBSCRIPTION_READ';

const LEGAL_COMMERCIAL_CONTEXT_KEYS = Object.freeze([
  'schema',
  'version',
  'tenant_id',
  'visibility',
  'product',
  'subscription',
  'plan',
  'commercial',
]);

const LEGAL_COMMERCIAL_PRODUCT_KEYS = Object.freeze([
  'product_id',
  'workspace_key',
  'available',
  'entitlement_state',
]);

const LEGAL_COMMERCIAL_SUBSCRIPTION_KEYS = Object.freeze([
  'subscription_id',
  'status',
  'current_period_end',
]);

const LEGAL_COMMERCIAL_PLAN_KEYS = Object.freeze([
  'plan_id',
  'tier',
  'name',
  'features',
  'catalogue_version',
]);

const LEGAL_COMMERCIAL_VALUE_KEYS = Object.freeze([
  'amount',
  'currency',
  'billing_frequency',
  'monthly_equivalent_amount',
  'financial_execution_authority',
]);

const LEGAL_COMMERCIAL_ALLOWED_FREQUENCIES = Object.freeze([
  'monthly',
  'quarterly',
  'annual',
]);

const LEGAL_COMMERCIAL_ALLOWED_ENTITLEMENT_STATES = Object.freeze([
  'ACTIVE',
  'PENDING_SOURCE',
  'SUSPENDED',
  'REVOKED',
]);

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

const CLIENT_ACCEPTANCE_INSTRUMENT_SCHEMA =
  'WILSY-LEGAL-CLIENT-ACCEPTANCE-INSTRUMENT-PROJECTION/V1';
const CLIENT_ACCEPTANCE_INSTRUMENT_VERSION =
  'v1.0.0-L9A4-P2E-CLIENT-ACCEPTANCE-INSTRUMENT-PROJECTION';
const CLIENT_ACCEPTANCE_INSTRUMENT_VISIBILITY =
  'LEGAL_CLIENT_ACTIONABLE_ACCEPTANCE_INSTRUMENTS';
const CLIENT_ACCEPTANCE_INSTRUMENT_RESPONSE_KEYS = Object.freeze([
  'schema',
  'version',
  'tenant_id',
  'case_matter_id',
  'visibility',
  'instruments',
]);
const CLIENT_ACCEPTANCE_INSTRUMENT_KEYS = Object.freeze([
  'instrument_id',
  'version',
  'instrument_kind',
  'title',
  'review_scope',
  'effective_from',
  'instrument_fingerprint',
  'content_fingerprint',
]);
const CLIENT_ACCEPTANCE_CONTEXT_SCHEMA =
  'WILSY-LEGAL-CLIENT-ACCEPTANCE-CONTEXT/V1';
const CLIENT_ACCEPTANCE_CONTEXT_VERSION =
  'v1.0.0-L9A4-P2C1-CLIENT-ACCEPTANCE-CONTEXT';
const CLIENT_ACCEPTANCE_CONTEXT_KEYS = Object.freeze([
  'schema', 'context_version', 'acceptance_context_id', 'tenant_id',
  'actor_principal_id', 'case_matter_id', 'matter_reference',
  'matter_fingerprint', 'party_id', 'subject_reference',
  'subject_identity_fingerprint', 'capacity_id', 'capacity_type',
  'capacity_fingerprint', 'capacity_effective_from',
  'capacity_effective_until', 'instrument_id', 'instrument_version',
  'instrument_fingerprint', 'content_fingerprint', 'content_reference',
  'title', 'review_scope', 'instrument_effective_from',
  'lifecycle_status', 'lifecycle_fingerprint',
  'lifecycle_evidence_fingerprint', 'approval_id', 'approval_decision',
  'approval_fingerprint', 'approval_effective_from',
  'issuer_evidence_reference', 'issuer_evidence_fingerprint',
  'issued_at', 'expires_at', 'replay_key', 'fingerprint',
]);
const CLIENT_ACCEPTANCE_SCHEMA = 'WILSY-LEGAL-CLIENT-ACCEPTANCE/V1';
const CLIENT_ACCEPTANCE_VERSION = 'v1.0.0-L9A-CLIENT-ACCEPTANCE';
const CLIENT_ACCEPTANCE_KEYS = Object.freeze([
  'schema', 'acceptance_version', 'tenant_id', 'case_matter_id',
  'matter_fingerprint', 'acceptance_id', 'party_id', 'subject_reference',
  'subject_identity_fingerprint', 'acceptance_scope', 'actor_principal_id',
  'accepted_at', 'source_evidence_reference', 'source_evidence_fingerprint',
  'fingerprint',
]);

const LEGAL_WORKSPACE_SCHEMA =
  'WILSY-LEGAL-OPERATIONS-PRACTICE-WORKSPACE/V1';
const LEGAL_WORKSPACE_VERSION =
  'v1.7.0-L8-7D11-LEGAL-PRACTICE-WORKSPACE-API';
const LEGAL_WORKSPACE_V2_SCHEMA =
  'WILSY-LEGAL-OPERATIONS-PRACTICE-WORKSPACE/V2';
const LEGAL_WORKSPACE_V2_VERSION =
  'v1.8.0-L8-7D15-FIRST-CLASS-MATTER-WORKSPACE-API';
const LEGAL_WORKSPACE_VISIBILITY =
  'LEGAL_PRACTICE_WORKSPACE';

const PRODUCTIVE_WORK_SCHEMA =
  'WILSY-LEGAL-PROFILE-PRODUCTIVE-WORK/V1';
const PRODUCTIVE_WORK_VERSION =
  'v1.0.1-PW-P2-PROFILE-PRODUCTIVE-WORK-COMPOSITION';
const PRODUCTIVE_WORK_HTTP_VERSION =
  'v1.0.0-PW-P11B-AUTHENTICATED-PRODUCTIVE-WORK-READ-API';

const PRODUCTIVE_WORK_RESPONSE_KEYS = Object.freeze([
  'schema',
  'version',
  'http_version',
  'tenant_id',
  'principal_id',
  'as_of',
  'operating_contexts',
  'capability_ids',
  'assigned_work_items',
  'supervised_work_items',
  'overdue_work_items',
  'due_soon_work_items',
]);

const PRODUCTIVE_WORK_CONTEXT_KEYS = Object.freeze([
  'operating_role_id',
  'operating_role_revision',
  'display_name',
  'capability_ids',
  'office_references',
  'practice_references',
  'business_unit_references',
  'jurisdiction_references',
]);

const PRODUCTIVE_WORK_ITEM_KEYS = Object.freeze([
  'schema',
  'work_item_version',
  'work_item_id',
  'tenant_id',
  'case_matter_id',
  'title',
  'source_kind',
  'source_reference',
  'source_evidence_fingerprint',
  'status',
  'created_at',
  'due_at',
  'completion_evidence_reference',
  'completion_evidence_fingerprint',
  'completed_at',
  'cancellation_reason_reference',
  'cancelled_at',
  'fingerprint',
]);

const PRODUCTIVE_WORK_OPEN_STATES = Object.freeze([
  'OPEN',
  'IN_PROGRESS',
  'BLOCKED',
]);


const SPECIALIST_WORKFLOW_SCHEMA =
  'WILSY-LEGAL-SPECIALIST-WORKFLOW-PROJECTION/V1';
const SPECIALIST_WORKFLOW_VERSION =
  'v1.0.0-P0-LEGAL-SPECIALIST-WORKFLOW-PROJECTION';
const SPECIALIST_WORKFLOW_HTTP_VERSION =
  'v1.0.0-P2-LEGAL-SPECIALIST-WORKFLOW-HTTP';

const SPECIALIST_WORKFLOW_RESPONSE_KEYS = Object.freeze([
  'schema',
  'version',
  'http_version',
  'tenant_id',
  'principal_id',
  'as_of',
  'rows',
]);

const SPECIALIST_WORKFLOW_ROW_KEYS = Object.freeze([
  'work_item_id',
  'case_matter_id',
  'workflow_instance_id',
  'workflow_definition_id',
  'stage_definition_id',
  'readiness',
  'blocking_dependency_work_item_ids',
  'unsatisfied_gate_references',
  'materialization_transition_id',
  'materialization_receipt_id',
]);

const SPECIALIST_WORKFLOW_READINESS = Object.freeze([
  'ACTIONABLE',
  'BLOCKED_DEPENDENCY',
  'BLOCKED_GATE',
  'BLOCKED_DEPENDENCY_AND_GATE',
]);

const CONFLICT_SCREENING_SCHEMA =
  'WILSY-LEGAL-CONFLICT-SCREENING-PRESENTATION/V1';
const CONFLICT_SCREENING_VERSION =
  'v1.9.0-L8-8N-CONFLICT-SCREENING-READ-API';
const CONFLICT_SCREENING_VISIBILITY =
  'LEGAL_CONFLICT_SCREENING_REVIEW_QUEUE';
const CONFLICT_SCREENING_RESPONSE_KEYS = Object.freeze([
  'schema',
  'version',
  'tenant_id',
  'visibility',
  'screenings',
]);
const CONFLICT_SCREENING_ROW_KEYS = Object.freeze([
  'screening_id',
  'source_case_matter_id',
  'status',
  'screened_at',
]);

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

const LEGAL_WORKSPACE_V2_RESPONSE_KEYS = Object.freeze([
  'schema',
  'version',
  'tenant_id',
  'visibility',
  'summary',
  'matters',
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

const LEGAL_WORKSPACE_V2_SUMMARY_KEYS = Object.freeze([
  'matters_total',
  'matters_open',
  'matters_closed',
  ...LEGAL_WORKSPACE_SUMMARY_KEYS,
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

const LEGAL_WORKSPACE_V2_ROW_KEYS = Object.freeze({
  matters: Object.freeze([
    'case_matter_id',
    'matter_reference',
    'opened_at',
    'state',
    'evidence_identity',
  ]),
  ...LEGAL_WORKSPACE_ROW_KEYS,
});

const LEGAL_WORKSPACE_STATES = Object.freeze({
  matters: Object.freeze(['OPEN', 'CLOSED']),
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


function assertCanonicalClientAcceptanceInstrumentPayload(value, expectedMatterId) {
  const errorCode = 'LEGAL_OPERATIONS_CLIENT_ACCEPTANCE_INSTRUMENT_RESPONSE_INVALID';
  assertExactKeys(value, CLIENT_ACCEPTANCE_INSTRUMENT_RESPONSE_KEYS, errorCode);
  if (
    value.schema !== CLIENT_ACCEPTANCE_INSTRUMENT_SCHEMA
    || value.version !== CLIENT_ACCEPTANCE_INSTRUMENT_VERSION
    || !isCanonicalText(value.tenant_id)
    || value.case_matter_id !== expectedMatterId
    || value.visibility !== CLIENT_ACCEPTANCE_INSTRUMENT_VISIBILITY
    || !Array.isArray(value.instruments)
  ) {
    throw new Error(errorCode);
  }

  let priorKey = null;
  const seen = new Set();
  const instruments = value.instruments.map((entry) => {
    assertExactKeys(entry, CLIENT_ACCEPTANCE_INSTRUMENT_KEYS, errorCode);
    if (
      !isCanonicalText(entry.instrument_id)
      || !isCanonicalText(entry.version)
      || !isCanonicalText(entry.instrument_kind)
      || !isCanonicalText(entry.title)
      || !isCanonicalText(entry.review_scope)
      || !isCanonicalTimestamp(entry.effective_from)
      || !SHA3_512_PATTERN.test(entry.instrument_fingerprint)
      || !SHA3_512_PATTERN.test(entry.content_fingerprint)
    ) {
      throw new Error(errorCode);
    }
    const identity = `${entry.instrument_id}\u0000${entry.version}`;
    if (seen.has(identity)) throw new Error(errorCode);
    const orderKey = `${entry.effective_from}\u0000${entry.instrument_id}\u0000${entry.version}`;
    if (priorKey !== null && orderKey > priorKey) throw new Error(errorCode);
    priorKey = orderKey;
    seen.add(identity);
    return Object.freeze({
      instrumentId: entry.instrument_id,
      version: entry.version,
      instrumentKind: entry.instrument_kind,
      title: entry.title,
      reviewScope: entry.review_scope,
      effectiveFrom: entry.effective_from,
      instrumentFingerprint: entry.instrument_fingerprint,
      contentFingerprint: entry.content_fingerprint,
    });
  });

  return Object.freeze({
    schema: value.schema,
    version: value.version,
    tenantId: value.tenant_id,
    caseMatterId: value.case_matter_id,
    visibility: value.visibility,
    instruments: Object.freeze(instruments),
  });
}

function assertCanonicalClientAcceptanceContext(value, expected) {
  const errorCode = 'LEGAL_OPERATIONS_CLIENT_ACCEPTANCE_CONTEXT_RESPONSE_INVALID';
  assertExactKeys(value, CLIENT_ACCEPTANCE_CONTEXT_KEYS, errorCode);
  if (
    value.schema !== CLIENT_ACCEPTANCE_CONTEXT_SCHEMA
    || value.context_version !== CLIENT_ACCEPTANCE_CONTEXT_VERSION
    || value.case_matter_id !== expected.caseMatterId
    || value.acceptance_context_id !== expected.acceptanceContextId
    || value.instrument_id !== expected.instrumentId
    || value.replay_key !== expected.replayKey
    || !isCanonicalText(value.tenant_id)
    || !isCanonicalText(value.actor_principal_id)
    || !isCanonicalText(value.title)
    || !isCanonicalText(value.review_scope)
    || !isCanonicalTimestamp(value.issued_at)
    || !isCanonicalTimestamp(value.expires_at)
    || !SHA3_512_PATTERN.test(value.matter_fingerprint)
    || !SHA3_512_PATTERN.test(value.instrument_fingerprint)
    || !SHA3_512_PATTERN.test(value.content_fingerprint)
    || !SHA3_512_PATTERN.test(value.fingerprint)
  ) {
    throw new Error(errorCode);
  }
  return Object.freeze({
    acceptanceContextId: value.acceptance_context_id,
    caseMatterId: value.case_matter_id,
    instrumentId: value.instrument_id,
    instrumentVersion: value.instrument_version,
    title: value.title,
    reviewScope: value.review_scope,
    issuedAt: value.issued_at,
    expiresAt: value.expires_at,
    contentFingerprint: value.content_fingerprint,
  });
}

function assertCanonicalClientAcceptance(value, expectedContextId) {
  const errorCode = 'LEGAL_OPERATIONS_CLIENT_ACCEPTANCE_RESPONSE_INVALID';
  assertExactKeys(value, CLIENT_ACCEPTANCE_KEYS, errorCode);
  if (
    value.schema !== CLIENT_ACCEPTANCE_SCHEMA
    || value.acceptance_version !== CLIENT_ACCEPTANCE_VERSION
    || !isCanonicalText(value.tenant_id)
    || !isCanonicalText(value.case_matter_id)
    || !isCanonicalText(value.acceptance_id)
    || !isCanonicalText(value.acceptance_scope)
    || !isCanonicalTimestamp(value.accepted_at)
    || !SHA3_512_PATTERN.test(value.matter_fingerprint)
    || !SHA3_512_PATTERN.test(value.source_evidence_fingerprint)
    || !SHA3_512_PATTERN.test(value.fingerprint)
    || !String(value.source_evidence_reference || '').includes(expectedContextId)
  ) {
    throw new Error(errorCode);
  }
  return Object.freeze({
    acceptanceId: value.acceptance_id,
    caseMatterId: value.case_matter_id,
    acceptanceScope: value.acceptance_scope,
    acceptedAt: value.accepted_at,
    fingerprint: value.fingerprint,
  });
}

function assertClientAcceptanceContextInput(value) {
  const errorCode = 'LEGAL_OPERATIONS_CLIENT_ACCEPTANCE_CONTEXT_INPUT_INVALID';
  assertExactKeys(
    value,
    ['caseMatterId', 'acceptanceContextId', 'replayKey', 'instrumentId'],
    errorCode,
  );
  for (const key of ['caseMatterId', 'acceptanceContextId', 'replayKey', 'instrumentId']) {
    if (!isCanonicalText(value[key])) throw new Error(errorCode);
  }
  return Object.freeze({ ...value });
}

function assertClientAcceptanceConfirmationInput(value) {
  const errorCode = 'LEGAL_OPERATIONS_CLIENT_ACCEPTANCE_CONFIRMATION_INPUT_INVALID';
  assertExactKeys(
    value,
    ['acceptanceContextId', 'idempotencyKey', 'confirmed'],
    errorCode,
  );
  if (
    !isCanonicalText(value.acceptanceContextId)
    || !isCanonicalText(value.idempotencyKey)
    || value.confirmed !== true
  ) {
    throw new Error(errorCode);
  }
  return Object.freeze({ ...value });
}


function assertCanonicalConflictScreeningPayload(value) {
  const errorCode = 'LEGAL_OPERATIONS_CONFLICT_SCREENING_RESPONSE_INVALID';
  assertExactKeys(value, CONFLICT_SCREENING_RESPONSE_KEYS, errorCode);
  if (
    value.schema !== CONFLICT_SCREENING_SCHEMA
    || value.version !== CONFLICT_SCREENING_VERSION
    || !isCanonicalText(value.tenant_id)
    || value.visibility !== CONFLICT_SCREENING_VISIBILITY
    || !Array.isArray(value.screenings)
  ) {
    throw new Error(errorCode);
  }

  const seen = new Set();
  let priorTimestamp = null;
  let priorId = null;
  const screenings = value.screenings.map((entry) => {
    assertExactKeys(entry, CONFLICT_SCREENING_ROW_KEYS, errorCode);
    if (
      !isCanonicalText(entry.screening_id)
      || !isCanonicalText(entry.source_case_matter_id)
      || entry.status !== 'REVIEW_REQUIRED'
      || !isCanonicalTimestamp(entry.screened_at)
      || seen.has(entry.screening_id)
    ) {
      throw new Error('LEGAL_OPERATIONS_CONFLICT_SCREENING_SCOPE_INVALID');
    }
    const timestamp = Date.parse(entry.screened_at);
    if (
      priorTimestamp !== null
      && (
        timestamp > priorTimestamp
        || (timestamp === priorTimestamp && entry.screening_id < priorId)
      )
    ) {
      throw new Error('LEGAL_OPERATIONS_CONFLICT_SCREENING_ORDER_INVALID');
    }
    priorTimestamp = timestamp;
    priorId = entry.screening_id;
    seen.add(entry.screening_id);
    return Object.freeze({
      screeningId: entry.screening_id,
      sourceCaseMatterId: entry.source_case_matter_id,
      status: entry.status,
      screenedAt: entry.screened_at,
    });
  });

  return Object.freeze({
    schema: value.schema,
    version: value.version,
    tenantId: value.tenant_id,
    visibility: value.visibility,
    screenings: Object.freeze(screenings),
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


function assertCanonicalSpecialistWorkflowPayload(value) {
  const errorCode =
    'LEGAL_OPERATIONS_SPECIALIST_WORKFLOW_RESPONSE_INVALID';

  assertExactKeys(
    value,
    SPECIALIST_WORKFLOW_RESPONSE_KEYS,
    errorCode,
  );

  if (
    value.schema !== SPECIALIST_WORKFLOW_SCHEMA
    || value.version !== SPECIALIST_WORKFLOW_VERSION
    || value.http_version !== SPECIALIST_WORKFLOW_HTTP_VERSION
    || !isCanonicalText(value.tenant_id)
    || !isCanonicalText(value.principal_id)
    || !isCanonicalTimestamp(value.as_of)
    || !Array.isArray(value.rows)
  ) {
    throw new Error(errorCode);
  }

  let previousWorkItemId = null;

  const rows = value.rows.map((entry) => {
    assertExactKeys(
      entry,
      SPECIALIST_WORKFLOW_ROW_KEYS,
      errorCode,
    );

    if (
      !isCanonicalText(entry.work_item_id)
      || !isCanonicalText(entry.case_matter_id)
      || !isCanonicalText(entry.workflow_instance_id)
      || !isCanonicalText(entry.workflow_definition_id)
      || !isCanonicalText(entry.stage_definition_id)
      || !SPECIALIST_WORKFLOW_READINESS.includes(
        entry.readiness,
      )
      || !Array.isArray(
        entry.blocking_dependency_work_item_ids,
      )
      || !Array.isArray(
        entry.unsatisfied_gate_references,
      )
      || (
        entry.materialization_transition_id !== null
        && !isCanonicalText(
          entry.materialization_transition_id,
        )
      )
      || (
        entry.materialization_receipt_id !== null
        && !isCanonicalText(
          entry.materialization_receipt_id,
        )
      )
    ) {
      throw new Error(errorCode);
    }

    if (
      previousWorkItemId !== null
      && entry.work_item_id <= previousWorkItemId
    ) {
      throw new Error(errorCode);
    }

    previousWorkItemId = entry.work_item_id;

    const validateTokens = (tokens) => {
      let previous = null;
      const observed = new Set();

      for (const token of tokens) {
        if (
          !isCanonicalText(token)
          || observed.has(token)
          || (
            previous !== null
            && token < previous
          )
        ) {
          throw new Error(errorCode);
        }

        observed.add(token);
        previous = token;
      }

      return Object.freeze([...tokens]);
    };

    const dependencies = validateTokens(
      entry.blocking_dependency_work_item_ids,
    );

    const gates = validateTokens(
      entry.unsatisfied_gate_references,
    );

    const semanticStateValid = (
      (
        entry.readiness === 'ACTIONABLE'
        && dependencies.length === 0
        && gates.length === 0
      )
      || (
        entry.readiness === 'BLOCKED_DEPENDENCY'
        && dependencies.length > 0
        && gates.length === 0
      )
      || (
        entry.readiness === 'BLOCKED_GATE'
        && dependencies.length === 0
        && gates.length > 0
      )
      || (
        entry.readiness
          === 'BLOCKED_DEPENDENCY_AND_GATE'
        && dependencies.length > 0
        && gates.length > 0
      )
    );

    if (!semanticStateValid) {
      throw new Error(errorCode);
    }

    return Object.freeze({
      workItemId: entry.work_item_id,
      caseMatterId: entry.case_matter_id,
      workflowInstanceId: entry.workflow_instance_id,
      workflowDefinitionId: entry.workflow_definition_id,
      stageDefinitionId: entry.stage_definition_id,
      readiness: entry.readiness,
      blockingDependencyWorkItemIds: dependencies,
      unsatisfiedGateReferences: gates,
      materializationTransitionId:
        entry.materialization_transition_id,
      materializationReceiptId:
        entry.materialization_receipt_id,
    });
  });

  return Object.freeze({
    schema: value.schema,
    version: value.version,
    httpVersion: value.http_version,
    tenantId: value.tenant_id,
    principalId: value.principal_id,
    asOf: value.as_of,
    rows: Object.freeze(rows),
  });
}


function assertCanonicalProductiveWorkPayload(value) {
  const errorCode = 'LEGAL_OPERATIONS_PRODUCTIVE_WORK_RESPONSE_INVALID';

  assertExactKeys(
    value,
    PRODUCTIVE_WORK_RESPONSE_KEYS,
    errorCode,
  );

  if (
    value.schema !== PRODUCTIVE_WORK_SCHEMA
    || value.version !== PRODUCTIVE_WORK_VERSION
    || value.http_version !== PRODUCTIVE_WORK_HTTP_VERSION
    || !isCanonicalText(value.tenant_id)
    || !isCanonicalText(value.principal_id)
    || !isCanonicalTimestamp(value.as_of)
    || !Array.isArray(value.operating_contexts)
    || !Array.isArray(value.capability_ids)
  ) {
    throw new Error(errorCode);
  }

  const contexts = value.operating_contexts.map((entry) => {
    assertExactKeys(
      entry,
      PRODUCTIVE_WORK_CONTEXT_KEYS,
      errorCode,
    );

    if (
      !isCanonicalText(entry.operating_role_id)
      || !Number.isInteger(entry.operating_role_revision)
      || entry.operating_role_revision < 1
      || !isCanonicalText(entry.display_name)
    ) {
      throw new Error(errorCode);
    }

    for (const key of [
      'capability_ids',
      'office_references',
      'practice_references',
      'business_unit_references',
      'jurisdiction_references',
    ]) {
      if (
        !Array.isArray(entry[key])
        || entry[key].some((token) => !isCanonicalText(token))
      ) {
        throw new Error(errorCode);
      }
    }

    return Object.freeze({
      operatingRoleId: entry.operating_role_id,
      operatingRoleRevision: entry.operating_role_revision,
      displayName: entry.display_name,
      capabilityIds: Object.freeze([...entry.capability_ids]),
      officeReferences: Object.freeze([...entry.office_references]),
      practiceReferences: Object.freeze([...entry.practice_references]),
      businessUnitReferences: Object.freeze([...entry.business_unit_references]),
      jurisdictionReferences: Object.freeze([...entry.jurisdiction_references]),
    });
  });

  const adaptItems = (rows) => {
    if (!Array.isArray(rows)) {
      throw new Error(errorCode);
    }

    return Object.freeze(rows.map((entry) => {
      assertExactKeys(
        entry,
        PRODUCTIVE_WORK_ITEM_KEYS,
        errorCode,
      );

      if (
        entry.schema !== 'WILSY-LEGAL-WORK-ITEM/V1'
        || entry.work_item_version !== 'v1.0.1-G7E-LEGAL-WORK-ITEM'
        || entry.tenant_id !== value.tenant_id
        || !isCanonicalText(entry.work_item_id)
        || !isCanonicalText(entry.case_matter_id)
        || !isCanonicalText(entry.title)
        || !isCanonicalText(entry.source_kind)
        || !isCanonicalText(entry.source_reference)
        || !SHA3_512_PATTERN.test(entry.source_evidence_fingerprint)
        || !PRODUCTIVE_WORK_OPEN_STATES.includes(entry.status)
        || !isCanonicalTimestamp(entry.created_at)
        || (
          entry.due_at !== null
          && !isCanonicalTimestamp(entry.due_at)
        )
        || !SHA3_512_PATTERN.test(entry.fingerprint)
      ) {
        throw new Error(errorCode);
      }

      return Object.freeze({
        workItemId: entry.work_item_id,
        caseMatterId: entry.case_matter_id,
        title: entry.title,
        sourceKind: entry.source_kind,
        sourceReference: entry.source_reference,
        status: entry.status,
        createdAt: entry.created_at,
        dueAt: entry.due_at,
      });
    }));
  };

  const capabilityIds = Object.freeze(
    value.capability_ids.map((token) => {
      if (!isCanonicalText(token)) {
        throw new Error(errorCode);
      }
      return token;
    }),
  );

  return Object.freeze({
    schema: value.schema,
    version: value.version,
    httpVersion: value.http_version,
    tenantId: value.tenant_id,
    principalId: value.principal_id,
    asOf: value.as_of,
    operatingContexts: Object.freeze(contexts),
    capabilityIds,
    assignedWorkItems: adaptItems(value.assigned_work_items),
    supervisedWorkItems: adaptItems(value.supervised_work_items),
    overdueWorkItems: adaptItems(value.overdue_work_items),
    dueSoonWorkItems: adaptItems(value.due_soon_work_items),
  });
}


function assertCanonicalLegalWorkspacePayload(value) {
  const errorCode = 'LEGAL_OPERATIONS_WORKSPACE_RESPONSE_INVALID';
  if (!isPlainObject(value)) throw new Error(errorCode);

  const isV1 = (
    value.schema === LEGAL_WORKSPACE_SCHEMA
    && value.version === LEGAL_WORKSPACE_VERSION
  );
  const isV2 = (
    value.schema === LEGAL_WORKSPACE_V2_SCHEMA
    && value.version === LEGAL_WORKSPACE_V2_VERSION
  );
  if (!isV1 && !isV2) throw new Error(errorCode);

  const responseKeys = isV2
    ? LEGAL_WORKSPACE_V2_RESPONSE_KEYS
    : LEGAL_WORKSPACE_RESPONSE_KEYS;
  const summaryKeys = isV2
    ? LEGAL_WORKSPACE_V2_SUMMARY_KEYS
    : LEGAL_WORKSPACE_SUMMARY_KEYS;
  const rowContracts = isV2
    ? LEGAL_WORKSPACE_V2_ROW_KEYS
    : LEGAL_WORKSPACE_ROW_KEYS;

  assertExactKeys(value, responseKeys, errorCode);
  if (
    !isCanonicalText(value.tenant_id)
    || value.visibility !== LEGAL_WORKSPACE_VISIBILITY
    || !isPlainObject(value.summary)
  ) {
    throw new Error(errorCode);
  }

  assertExactKeys(value.summary, summaryKeys, errorCode);
  for (const key of summaryKeys) {
    if (
      !Number.isInteger(value.summary[key])
      || value.summary[key] < 0
    ) {
      throw new Error(errorCode);
    }
  }

  const identityKeys = {
    matters: 'case_matter_id',
    instructions: 'instruction_id',
    documents: 'document_id',
    attempts: 'attempt_id',
    executions: 'service_execution_id',
    returns: 'return_id',
  };

  const timestampKeys = {
    matters: 'opened_at',
    instructions: 'registered_at',
    documents: 'registered_at',
    attempts: 'allocated_at',
    executions: 'executed_at',
    returns: 'generated_at',
  };

  const stateKeys = {
    matters: 'state',
    instructions: 'state',
    documents: 'state',
    attempts: 'state',
    executions: 'outcome',
    returns: 'state',
  };

  const arrays = {};
  for (const [name, expectedKeys] of Object.entries(rowContracts)) {
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

  const countState = (rows, key, state) => (
    rows.reduce((count, row) => count + (row[key] === state ? 1 : 0), 0)
  );

  const expectedSummary = {
    ...(isV2 ? {
      matters_total: arrays.matters.length,
      matters_open: countState(arrays.matters, 'state', 'OPEN'),
      matters_closed: countState(arrays.matters, 'state', 'CLOSED'),
    } : {}),
    instructions_total: arrays.instructions.length,
    instructions_registered: countState(arrays.instructions, 'state', 'REGISTERED'),
    instructions_accepted: countState(arrays.instructions, 'state', 'ACCEPTED'),
    instructions_closed: countState(arrays.instructions, 'state', 'CLOSED'),
    instructions_cancelled: countState(arrays.instructions, 'state', 'CANCELLED'),
    documents_total: arrays.documents.length,
    documents_registered: countState(arrays.documents, 'state', 'REGISTERED'),
    documents_received: countState(arrays.documents, 'state', 'RECEIVED'),
    documents_allocated: countState(arrays.documents, 'state', 'ALLOCATED_TO_DEPUTY'),
    documents_returned: countState(arrays.documents, 'state', 'RETURNED_TO_CLIENT'),
    attempts_total: arrays.attempts.length,
    attempts_allocated: countState(arrays.attempts, 'state', 'ALLOCATED'),
    attempts_attempted: countState(arrays.attempts, 'state', 'ATTEMPTED'),
    attempts_completed: countState(arrays.attempts, 'state', 'COMPLETED'),
    attempts_not_completed: countState(arrays.attempts, 'state', 'NOT_COMPLETED'),
    attempts_cancelled: countState(arrays.attempts, 'state', 'CANCELLED'),
    executions_total: arrays.executions.length,
    executions_completed: countState(arrays.executions, 'outcome', 'COMPLETED'),
    executions_not_completed: countState(arrays.executions, 'outcome', 'NOT_COMPLETED'),
    returns_total: arrays.returns.length,
  };

  if (
    Object.entries(expectedSummary).some(
      ([key, expected]) => value.summary[key] !== expected,
    )
  ) {
    throw new Error('LEGAL_OPERATIONS_WORKSPACE_SUMMARY_MISMATCH');
  }

  const adapted = {
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
  };
  if (isV2) adapted.matters = arrays.matters;
  return Object.freeze(adapted);
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

function assertConflictReviewInput(value) {
  const errorCode = 'LEGAL_OPERATIONS_CONFLICT_REVIEW_INPUT_INVALID';
  assertExactKeys(value, CONFLICT_REVIEW_INPUT_KEYS, errorCode);
  if (
    !isCanonicalText(value.screeningId)
    || !isCanonicalText(value.reviewId)
    || !CONFLICT_REVIEW_OUTCOMES.includes(value.outcome)
    || !isCanonicalText(value.reviewReasonReference)
    || value.reviewReasonReference.length > 512
  ) {
    throw new Error(errorCode);
  }
  return Object.freeze({ ...value });
}

function assertCanonicalConflictReviewResponse(value, input) {
  const errorCode = 'LEGAL_OPERATIONS_CONFLICT_REVIEW_RESPONSE_INVALID';
  assertExactKeys(value, ['data'], errorCode);
  const data = value.data;
  assertExactKeys(data, CONFLICT_REVIEW_RESPONSE_KEYS, errorCode);
  if (
    data.review_id !== input.reviewId
    || data.screening_id !== input.screeningId
    || !CONFLICT_REVIEW_OUTCOMES.includes(data.outcome)
    || !isCanonicalTimestamp(data.reviewed_at)
    || !SHA3_512_PATTERN.test(data.fingerprint)
  ) {
    throw new Error(errorCode);
  }
  return Object.freeze({
    reviewId: data.review_id,
    screeningId: data.screening_id,
    outcome: data.outcome,
    reviewedAt: data.reviewed_at,
    fingerprint: data.fingerprint,
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


const exactCommercialObject = (value, keys, label) => {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    throw new Error(`LEGAL_COMMERCIAL_CONTEXT_INVALID_${label}`);
  }

  const actual = Object.keys(value).sort();
  const expected = [...keys].sort();

  if (
    actual.length !== expected.length
    || actual.some((key, index) => key !== expected[index])
  ) {
    throw new Error(`LEGAL_COMMERCIAL_CONTEXT_INVALID_${label}_KEYS`);
  }

  return value;
};

const exactCommercialText = (value, label, { nullable = false } = {}) => {
  if (nullable && value === null) return null;

  if (
    typeof value !== 'string'
    || !value
    || value !== value.trim()
  ) {
    throw new Error(`LEGAL_COMMERCIAL_CONTEXT_INVALID_${label}`);
  }

  return value;
};

const exactCommercialNumber = (
  value,
  label,
  { nullable = false } = {},
) => {
  if (nullable && value === null) return null;

  if (
    typeof value !== 'number'
    || !Number.isFinite(value)
    || value < 0
  ) {
    throw new Error(`LEGAL_COMMERCIAL_CONTEXT_INVALID_${label}`);
  }

  return value;
};

const validateLegalCommercialContext = (payload) => {
  const root = exactCommercialObject(
    payload,
    LEGAL_COMMERCIAL_CONTEXT_KEYS,
    'ROOT',
  );

  if (
    root.schema !== LEGAL_COMMERCIAL_CONTEXT_SCHEMA
    || root.version !== LEGAL_COMMERCIAL_CONTEXT_VERSION
    || root.visibility !== LEGAL_COMMERCIAL_CONTEXT_VISIBILITY
  ) {
    throw new Error('LEGAL_COMMERCIAL_CONTEXT_INVALID_ENVELOPE');
  }

  const tenantId = exactCommercialText(
    root.tenant_id,
    'TENANT',
  );

  const product = exactCommercialObject(
    root.product,
    LEGAL_COMMERCIAL_PRODUCT_KEYS,
    'PRODUCT',
  );

  if (
    product.product_id !== 'LEGAL_OPERATIONS'
    || product.workspace_key !== 'LEGAL_DASHBOARD'
    || typeof product.available !== 'boolean'
  ) {
    throw new Error('LEGAL_COMMERCIAL_CONTEXT_INVALID_PRODUCT');
  }

  if (
    product.entitlement_state !== null
    && !LEGAL_COMMERCIAL_ALLOWED_ENTITLEMENT_STATES.includes(
      product.entitlement_state,
    )
  ) {
    throw new Error(
      'LEGAL_COMMERCIAL_CONTEXT_INVALID_ENTITLEMENT_STATE',
    );
  }

  const subscription = exactCommercialObject(
    root.subscription,
    LEGAL_COMMERCIAL_SUBSCRIPTION_KEYS,
    'SUBSCRIPTION',
  );

  const plan = exactCommercialObject(
    root.plan,
    LEGAL_COMMERCIAL_PLAN_KEYS,
    'PLAN',
  );

  const commercial = exactCommercialObject(
    root.commercial,
    LEGAL_COMMERCIAL_VALUE_KEYS,
    'COMMERCIAL',
  );

  if (commercial.financial_execution_authority !== false) {
    throw new Error(
      'LEGAL_COMMERCIAL_CONTEXT_FINANCIAL_AUTHORITY_INVALID',
    );
  }

  if (!Array.isArray(plan.features)) {
    throw new Error('LEGAL_COMMERCIAL_CONTEXT_INVALID_PLAN_FEATURES');
  }

  const features = plan.features.map((value) =>
    exactCommercialText(value, 'PLAN_FEATURE')
  );

  if (new Set(features).size !== features.length) {
    throw new Error(
      'LEGAL_COMMERCIAL_CONTEXT_DUPLICATE_PLAN_FEATURE',
    );
  }

  if (product.available === true) {
    exactCommercialText(
      product.entitlement_state,
      'ENTITLEMENT_STATE',
    );

    if (product.entitlement_state !== 'ACTIVE') {
      throw new Error(
        'LEGAL_COMMERCIAL_CONTEXT_ACTIVE_PRODUCT_STATE_MISMATCH',
      );
    }

    const subscriptionId = exactCommercialText(
      subscription.subscription_id,
      'SUBSCRIPTION_ID',
    );
    const status = exactCommercialText(
      subscription.status,
      'SUBSCRIPTION_STATUS',
    );
    const currentPeriodEnd = exactCommercialText(
      subscription.current_period_end,
      'CURRENT_PERIOD_END',
    );
    const planId = exactCommercialText(
      plan.plan_id,
      'PLAN_ID',
    );
    const tier = exactCommercialText(
      plan.tier,
      'PLAN_TIER',
    );
    const name = exactCommercialText(
      plan.name,
      'PLAN_NAME',
    );

    if (status !== 'active') {
      throw new Error(
        'LEGAL_COMMERCIAL_CONTEXT_SUBSCRIPTION_NOT_ACTIVE',
      );
    }

    if (!features.includes('legal.core')) {
      throw new Error(
        'LEGAL_COMMERCIAL_CONTEXT_LEGAL_FEATURE_REQUIRED',
      );
    }

    if (
      !Number.isInteger(plan.catalogue_version)
      || plan.catalogue_version < 0
    ) {
      throw new Error(
        'LEGAL_COMMERCIAL_CONTEXT_INVALID_CATALOGUE_VERSION',
      );
    }

    const amount = exactCommercialNumber(
      commercial.amount,
      'AMOUNT',
    );
    const currency = exactCommercialText(
      commercial.currency,
      'CURRENCY',
    );
    const billingFrequency = exactCommercialText(
      commercial.billing_frequency,
      'BILLING_FREQUENCY',
    );
    const monthlyEquivalentAmount = exactCommercialNumber(
      commercial.monthly_equivalent_amount,
      'MONTHLY_EQUIVALENT',
    );

    if (
      !LEGAL_COMMERCIAL_ALLOWED_FREQUENCIES.includes(
        billingFrequency,
      )
    ) {
      throw new Error(
        'LEGAL_COMMERCIAL_CONTEXT_INVALID_BILLING_FREQUENCY',
      );
    }

    return Object.freeze({
      tenantId,
      product: Object.freeze({
        productId: product.product_id,
        workspaceKey: product.workspace_key,
        available: true,
        entitlementState: product.entitlement_state,
      }),
      subscription: Object.freeze({
        subscriptionId,
        status,
        currentPeriodEnd,
      }),
      plan: Object.freeze({
        planId,
        tier,
        name,
        features: Object.freeze([...features]),
        catalogueVersion: plan.catalogue_version,
      }),
      commercial: Object.freeze({
        amount,
        currency,
        billingFrequency,
        monthlyEquivalentAmount,
        financialExecutionAuthority: false,
      }),
    });
  }

  const absenceFields = [
    subscription.subscription_id,
    subscription.status,
    subscription.current_period_end,
    plan.plan_id,
    plan.tier,
    plan.name,
    plan.catalogue_version,
    commercial.amount,
    commercial.currency,
    commercial.billing_frequency,
    commercial.monthly_equivalent_amount,
  ];

  if (
    product.entitlement_state !== null
    || features.length !== 0
    || absenceFields.some((value) => value !== null)
  ) {
    throw new Error(
      'LEGAL_COMMERCIAL_CONTEXT_INVALID_ABSENT_PRODUCT_CONTRACT',
    );
  }

  return Object.freeze({
    tenantId,
    product: Object.freeze({
      productId: product.product_id,
      workspaceKey: product.workspace_key,
      available: false,
      entitlementState: null,
    }),
    subscription: null,
    plan: null,
    commercial: null,
  });
};

export const getLegalCommercialContext = async () => {
  try {
    const response = await api.get(
      '/legal-operations/commercial-context',
    );

    return Object.freeze({
      access: 'AUTHORIZED',
      context: validateLegalCommercialContext(
        response?.data,
      ),
    });
  } catch (error) {
    const status = Number(
      error?.response?.status,
    );

    if (status === 401 || status === 403) {
      return Object.freeze({
        access: 'DENIED',
        context: null,
      });
    }

    throw error;
  }
};

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

/**
 * Issue one authenticated human conflict-review command through the canonical
 * L8-8K route. The browser owns only the four human-choice fields; tenant,
 * reviewer identity, screening truth, authorization evidence and chronology
 * are derived by Python EOS inside the API-owned transaction. sovereignClient
 * is used because api.js intentionally adds transport timestamps to ordinary
 * mutation bodies, while this strict server model rejects unknown fields.
 *
 * @param {{screeningId: string, reviewId: string, outcome: string, reviewReasonReference: string}} value
 *   The exact four caller-owned command fields.
 * @returns {Promise<{reviewId: string, screeningId: string, outcome: string, reviewedAt: string, fingerprint: string}>}
 *   The bounded server receipt; no authorization evidence is exposed.
 * @throws {Error} For malformed client input or a malformed server response.
 * Axios authentication, authorization, 404, 409 and transport failures are
 * deliberately propagated unchanged so server semantics remain distinguishable.
 */
export async function issueLegalConflictReview(value) {
  const input = assertConflictReviewInput(value);
  const response = await sovereignClient.post('/legal-operations/conflict-reviews', {
    screening_id: input.screeningId,
    review_id: input.reviewId,
    outcome: input.outcome,
    review_reason_reference: input.reviewReasonReference,
  });
  return assertCanonicalConflictReviewResponse(response?.data, input);
}


export async function getLegalPracticeWorkspace() {
  const response = await api.get('/legal-operations/workspace');
  return assertCanonicalLegalWorkspacePayload(response?.data);
}


const COMPLETION_INPUT_KEYS = Object.freeze([
  'workItemId',
  'completionEvidenceReference',
  'completionEvidenceFingerprint',
]);

/**
 * Submit one authority-free completion intent for an assigned work item.
 * Python EOS exclusively owns IAM, tenant, assignment, provenance, time,
 * transaction and completion persistence. No browser-owned identity or
 * authorization fields are accepted.
 */
export async function completeLegalWorkItem(value) {
  if (
    value === null
    || typeof value !== 'object'
    || Array.isArray(value)
    || Object.getPrototypeOf(value) !== Object.prototype
    || Object.keys(value).length !== COMPLETION_INPUT_KEYS.length
    || COMPLETION_INPUT_KEYS.some(
      (key) => !Object.prototype.hasOwnProperty.call(value, key),
    )
  ) {
    throw new Error('LEGAL_WORK_COMPLETION_INPUT_INVALID');
  }

  const {
    workItemId,
    completionEvidenceReference,
    completionEvidenceFingerprint,
  } = value;

  if (
    typeof workItemId !== 'string'
    || !/^[A-Za-z0-9][A-Za-z0-9._:-]*$/.test(workItemId)
    || typeof completionEvidenceReference !== 'string'
    || !completionEvidenceReference.trim()
    || completionEvidenceReference !== completionEvidenceReference.trim()
    || typeof completionEvidenceFingerprint !== 'string'
    || !/^[a-f0-9]{128}$/.test(completionEvidenceFingerprint)
  ) {
    throw new Error('LEGAL_WORK_COMPLETION_INPUT_INVALID');
  }

  // sovereignClient avoids the legacy api.js command-body timestamp
  // interceptor; it must not add fields to this exact server contract.
  const response = await sovereignClient.post(
    `/legal-operations/work-items/${encodeURIComponent(workItemId)}/completion`,
    {
      completion_evidence_reference: completionEvidenceReference,
      completion_evidence_fingerprint: completionEvidenceFingerprint,
    },
  );

  const receipt = response?.data?.data;
  if (
    receipt === null
    || typeof receipt !== 'object'
    || Array.isArray(receipt)
    || receipt.work_item_id !== workItemId
  ) {
    throw new Error('LEGAL_WORK_COMPLETION_RECEIPT_INVALID');
  }

  return Object.freeze({ ...receipt });
}

let legalProductiveWorkInFlight = null;

export async function getLegalProductiveWork() {
  if (legalProductiveWorkInFlight) {
    return legalProductiveWorkInFlight;
  }

  const request = api
    .get('/legal-operations/productive-work')
    .then((response) => (
      assertCanonicalProductiveWorkPayload(
        response?.data,
      )
    ));

  legalProductiveWorkInFlight = request;

  try {
    return await request;
  } finally {
    if (legalProductiveWorkInFlight === request) {
      legalProductiveWorkInFlight = null;
    }
  }
}

let legalSpecialistWorkflowInFlight = null;

export async function getLegalSpecialistWorkflow() {
  if (legalSpecialistWorkflowInFlight) {
    return legalSpecialistWorkflowInFlight;
  }

  const request = api
    .get('/legal-operations/specialist-workflow')
    .then((response) => (
      assertCanonicalSpecialistWorkflowPayload(
        response?.data,
      )
    ));

  legalSpecialistWorkflowInFlight = request;

  try {
    return await request;
  } finally {
    if (
      legalSpecialistWorkflowInFlight === request
    ) {
      legalSpecialistWorkflowInFlight = null;
    }
  }
}

/**
 * Read the authenticated tenant's bounded conflict-screening review queue.
 * The server derives tenant scope and canonical REVIEW_REQUIRED eligibility;
 * this adapter performs no browser-side screening/review join or authority
 * reconstruction and accepts no tenant selector.
 *
 * @returns {Promise<{schema: string, version: string, tenantId: string, visibility: string, screenings: Array}>}
 *   Frozen presentation rows preserving canonical screening identity.
 * @throws {Error} For malformed server evidence; transport/auth failures pass
 *   through unchanged.
 */
export async function getLegalConflictScreenings() {
  const response = await api.get('/legal-operations/conflict-screenings');
  return assertCanonicalConflictScreeningPayload(response?.data);
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


export async function getLegalClientAcceptanceInstruments(caseMatterId) {
  if (!isCanonicalText(caseMatterId)) {
    throw new Error('LEGAL_OPERATIONS_CLIENT_ACCEPTANCE_INSTRUMENT_INPUT_INVALID');
  }
  const response = await api.get(
    `/legal-operations/client/matters/${encodeURIComponent(caseMatterId)}/acceptance-instruments`,
  );
  return assertCanonicalClientAcceptanceInstrumentPayload(
    response?.data?.data ?? response?.data,
    caseMatterId,
  );
}

export async function createLegalClientAcceptanceContext(value) {
  const input = assertClientAcceptanceContextInput(value);
  const response = await sovereignClient.post(
    `/legal-operations/client/matters/${encodeURIComponent(input.caseMatterId)}/acceptance-contexts`,
    {
      acceptance_context_id: input.acceptanceContextId,
      replay_key: input.replayKey,
      instrument_id: input.instrumentId,
    },
  );
  return assertCanonicalClientAcceptanceContext(response?.data?.data, input);
}

export async function getLegalClientAcceptanceContent(acceptanceContextId) {
  if (!isCanonicalText(acceptanceContextId)) {
    throw new Error('LEGAL_OPERATIONS_CLIENT_ACCEPTANCE_CONTENT_INPUT_INVALID');
  }
  const response = await api.get(
    `/legal-operations/client/acceptance-contexts/${encodeURIComponent(acceptanceContextId)}/content`,
    { responseType: 'text', transformResponse: [(data) => data] },
  );
  const headers = response?.headers || {};
  const contextId = headers['x-wilsy-acceptance-context-id'];
  const instrumentId = headers['x-wilsy-instrument-id'];
  const instrumentVersion = headers['x-wilsy-instrument-version'];
  const contentFingerprint = headers['x-wilsy-content-fingerprint'];
  const mediaType = String(headers['content-type'] || '').split(';')[0];
  if (
    contextId !== acceptanceContextId
    || !isCanonicalText(instrumentId)
    || !isCanonicalText(instrumentVersion)
    || !SHA3_512_PATTERN.test(contentFingerprint)
    || !isCanonicalText(mediaType)
    || typeof response?.data !== 'string'
    || response.data.length === 0
  ) {
    throw new Error('LEGAL_OPERATIONS_CLIENT_ACCEPTANCE_CONTENT_RESPONSE_INVALID');
  }
  return Object.freeze({
    acceptanceContextId: contextId,
    instrumentId,
    instrumentVersion,
    contentFingerprint,
    mediaType,
    content: response.data,
  });
}

export async function confirmLegalClientAcceptance(value) {
  const input = assertClientAcceptanceConfirmationInput(value);
  const response = await sovereignClient.post(
    `/legal-operations/client/acceptance-contexts/${encodeURIComponent(input.acceptanceContextId)}/acceptances`,
    { confirmed: true },
    { headers: { 'Idempotency-Key': input.idempotencyKey } },
  );
  return assertCanonicalClientAcceptance(
    response?.data?.data,
    input.acceptanceContextId,
  );
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

/**
 * Upload one file for an already-visible canonical ProcessDocument.
 * The browser supplies no tenant, principal, matter, fingerprint, capacity,
 * provider or storage authority and leaves multipart boundary construction to
 * the browser transport.
 */
export async function uploadLegalEvidence({ documentId, file, idempotencyKey }) {
  const errorCode = 'LEGAL_EVIDENCE_UPLOAD_INPUT_INVALID';
  if (
    !isCanonicalText(documentId)
    || !(file instanceof File)
    || file.size < 1
    || !isCanonicalText(idempotencyKey)
  ) {
    throw new Error(errorCode);
  }
  const form = new FormData();
  form.append('file', file);
  const response = await api.post(
    `/legal-operations/evidence/documents/${encodeURIComponent(documentId)}`,
    form,
    { headers: { 'Idempotency-Key': idempotencyKey } },
  );
  const value = response?.data;
  const keys = [
    'schema', 'version', 'ingestion_reference', 'document_id',
    'case_matter_id', 'state', 'content_reference', 'content_fingerprint',
    'content_length', 'uncertainty_id',
  ];
  assertExactKeys(value, keys, 'LEGAL_EVIDENCE_UPLOAD_RESPONSE_INVALID');
  if (
    value.schema !== 'WILSY-LEGAL-EVIDENCE-UPLOAD-RESULT/V1'
    || value.version !== 'v1.0.0-L10A4-LEGAL-EVIDENCE-UPLOAD-HTTP'
    || value.document_id !== documentId
    || !isCanonicalText(value.ingestion_reference)
    || !isCanonicalText(value.case_matter_id)
    || !['COMMITTED', 'RECONCILIATION_REQUIRED'].includes(value.state)
    || !SHA3_512_PATTERN.test(value.content_fingerprint)
    || !Number.isSafeInteger(value.content_length)
    || value.content_length !== file.size
    || (value.state === 'COMMITTED' && (!isCanonicalText(value.content_reference) || value.uncertainty_id !== null))
    || (value.state === 'RECONCILIATION_REQUIRED' && (value.content_reference !== null || !isCanonicalText(value.uncertainty_id)))
  ) {
    throw new Error('LEGAL_EVIDENCE_UPLOAD_RESPONSE_INVALID');
  }
  return Object.freeze({
    ingestionReference: value.ingestion_reference,
    documentId: value.document_id,
    caseMatterId: value.case_matter_id,
    state: value.state,
    contentReference: value.content_reference,
    contentFingerprint: value.content_fingerprint,
    contentLength: value.content_length,
    uncertaintyId: value.uncertainty_id,
  });
}

export const __legalOperationsServiceInternals = Object.freeze({
  assertCanonicalQueuePayload,
  assertCanonicalDeputyActiveWorkPayload,
  assertCanonicalDeputyFieldCapabilitiesPayload,
  assertCanonicalClientMatterPayload,
  assertCanonicalClientAcceptanceInstrumentPayload,
  assertCanonicalClientAcceptanceContext,
  assertCanonicalClientAcceptance,
  assertClientAcceptanceContextInput,
  assertClientAcceptanceConfirmationInput,
  assertCanonicalConflictScreeningPayload,
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
  CLIENT_ACCEPTANCE_INSTRUMENT_SCHEMA,
  CLIENT_ACCEPTANCE_INSTRUMENT_VERSION,
  CLIENT_ACCEPTANCE_INSTRUMENT_VISIBILITY,
  CLIENT_ACCEPTANCE_INSTRUMENT_RESPONSE_KEYS,
  CLIENT_ACCEPTANCE_INSTRUMENT_KEYS,
  CLIENT_ACCEPTANCE_CONTEXT_SCHEMA,
  CLIENT_ACCEPTANCE_CONTEXT_VERSION,
  CLIENT_ACCEPTANCE_CONTEXT_KEYS,
  CLIENT_ACCEPTANCE_SCHEMA,
  CLIENT_ACCEPTANCE_VERSION,
  CLIENT_ACCEPTANCE_KEYS,
  assertLegalIntakeInput,
  assertCanonicalLegalIntakeResponse,
  assertConflictReviewInput,
  assertCanonicalConflictReviewResponse,
  CONFLICT_REVIEW_INPUT_KEYS,
  CONFLICT_REVIEW_RESPONSE_KEYS,
  CONFLICT_REVIEW_OUTCOMES,
  LEGAL_INTAKE_INPUT_KEYS,
  LEGAL_INTAKE_RESPONSE_KEYS,
  assertCanonicalLegalWorkspacePayload,
  assertCanonicalFinanceEvidence,
  assertReturnCommandInput,
  assertCanonicalReturnCommandResponse,
  LEGAL_WORKSPACE_SCHEMA,
  LEGAL_WORKSPACE_VERSION,
  LEGAL_WORKSPACE_V2_SCHEMA,
  LEGAL_WORKSPACE_V2_VERSION,
  LEGAL_WORKSPACE_VISIBILITY,
  CONFLICT_SCREENING_SCHEMA,
  CONFLICT_SCREENING_VERSION,
  CONFLICT_SCREENING_VISIBILITY,
  CONFLICT_SCREENING_RESPONSE_KEYS,
  CONFLICT_SCREENING_ROW_KEYS,
  LEGAL_WORKSPACE_RESPONSE_KEYS,
  LEGAL_WORKSPACE_V2_RESPONSE_KEYS,
  LEGAL_WORKSPACE_SUMMARY_KEYS,
  LEGAL_WORKSPACE_V2_SUMMARY_KEYS,
  LEGAL_WORKSPACE_ROW_KEYS,
  LEGAL_WORKSPACE_V2_ROW_KEYS,
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
 * VERSION: v2.2.0-P8-LEGAL-WORK-COMPLETION-BROWSER-TRANSPORT
 * AUTHORITY BOUNDARY: role-scoped Legal Operations read/intake/return/deputy-command/conflict-review browser transport validation only
 * TENANT POSTURE: server tenant/principal/role/client/deputy scope remains authoritative across practice, finance, client and field surfaces; browser cannot establish authorization scope
 * FAIL-CLOSED POSTURE: malformed/extra/missing/scope/state/schema/version/order/command-response drift rejects without fallback
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
