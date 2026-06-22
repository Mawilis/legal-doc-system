/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS — SOVEREIGN CRM ROUTES                                                                                                      ║
 * ║ VERSION: 2.0.0-EPITOME-COMMAND-SPINE                                                                                                 ║
 * ║ ABSOLUTE ROLE: CRM API for commercial truth, legal identity, authority, contract ledger, board readiness and Source Registry evidence.║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & MANDATE                                                                                                               ║
 * ║ • Wilson Khanyezi — Founder/Lead Architect: Mandated CRM not as a clone of Zoho/HubSpot, but as Wilsy OS commercial truth spine.     ║
 * ║ • AI Engineering — Epitomised routes: Added boardroom readiness, source posture, authority and contract-ledger command endpoints.     ║
 * ║ • Source Registry — Integrated projection surface so CRM records can support legal artifact verification without fake VERIFIED data.  ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * @fileoverview Sovereign CRM route layer.
 * Empty collections are valid live state.
 * The route layer must never fabricate customers, deals, authority, contracts or VERIFIED evidence.
 */

import express from 'express';
import mongoose from 'mongoose';
import crypto from 'crypto';
import CrmRecord from '../models/CrmRecord.js';

const router = express.Router();

const CRM_ROUTE_VERSION = '2.0.0-EPITOME-COMMAND-SPINE';
const CRM_TRUTH_POLICY = 'NO_FAKE_VERIFIED';

const SOURCE_POSTURES = [
  'NOT_EVALUATED',
  'PENDING',
  'MISSING',
  'ERROR',
  'BLOCKED',
  'READY_FOR_ANCHOR',
  'VERIFIED',
];

const RESOURCE_TYPES = Object.freeze({
  leads: 'lead',
  contacts: 'contact',
  accounts: 'account',
  deals: 'deal',
  tasks: 'task',
  meetings: 'meeting',
  calls: 'call',
  campaigns: 'campaign',
  documents: 'document',
  visits: 'visit',
  projects: 'project',
  quotes: 'quote',
  invoices: 'invoice',
  cases: 'case',
  tickets: 'ticket',
  contracts: 'contract',
  authorities: 'authority',
  risks: 'risk',
  opportunities: 'opportunity',
  suppliers: 'supplier',
  partners: 'partner',
});

const DEFAULTS_BY_TYPE = Object.freeze({
  lead: {
    status: 'NEW',
    score: null,
    leadSource: 'Direct',
    lifecycleStage: 'lead',
    sourcePosture: 'NOT_EVALUATED',
  },
  contact: { status: 'ACTIVE', lifecycleStage: 'customer', sourcePosture: 'NOT_EVALUATED' },
  account: { status: 'ACTIVE', accountType: 'Customer', sourcePosture: 'NOT_EVALUATED' },
  deal: {
    status: 'OPEN',
    stage: 'qualification',
    pipeline: 'default',
    probability: 10,
    value: 0,
    amount: 0,
    expectedRevenue: 0,
    currency: 'ZAR',
    sourcePosture: 'NOT_EVALUATED',
  },
  task: { status: 'Not Started', priority: 'High', sourcePosture: 'NOT_EVALUATED' },
  meeting: { status: 'SCHEDULED', sourcePosture: 'NOT_EVALUATED' },
  call: { status: 'PLANNED', callType: 'Outbound', sourcePosture: 'NOT_EVALUATED' },
  campaign: { status: 'DRAFT', sourcePosture: 'NOT_EVALUATED' },
  document: { status: 'DRAFT', folder: 'Document Library', sourcePosture: 'NOT_EVALUATED' },
  visit: { status: 'PLANNED', sourcePosture: 'NOT_EVALUATED' },
  project: {
    status: 'OPEN',
    projectPhase: 'Discovery',
    percentComplete: 0,
    sourcePosture: 'NOT_EVALUATED',
  },
  quote: { status: 'DRAFT', sourcePosture: 'NOT_EVALUATED' },
  invoice: { status: 'DRAFT', sourcePosture: 'NOT_EVALUATED' },
  case: { status: 'OPEN', priority: 'High', sourcePosture: 'NOT_EVALUATED' },
  ticket: { status: 'OPEN', priority: 'High', sourcePosture: 'NOT_EVALUATED' },
  contract: { status: 'DRAFT', sourcePosture: 'NOT_EVALUATED' },
  authority: { status: 'PENDING', sourcePosture: 'NOT_EVALUATED' },
  risk: { status: 'OPEN', sourcePosture: 'NOT_EVALUATED' },
  opportunity: {
    status: 'OPEN',
    stage: 'qualification',
    probability: 10,
    sourcePosture: 'NOT_EVALUATED',
  },
  supplier: { status: 'ACTIVE', accountType: 'Supplier', sourcePosture: 'NOT_EVALUATED' },
  partner: { status: 'ACTIVE', accountType: 'Partner', sourcePosture: 'NOT_EVALUATED' },
});

const CRM_FIELD_BLUEPRINTS = Object.freeze({
  lead: [
    'ownerName',
    'name',
    'firstName',
    'lastName',
    'accountName',
    'title',
    'email',
    'phone',
    'mobile',
    'leadSource',
    'status',
    'score',
    'industry',
    'annualRevenue',
    'city',
    'country',
    'sourcePosture',
    'boardReadiness',
  ],
  contact: [
    'ownerName',
    'salutation',
    'firstName',
    'lastName',
    'accountName',
    'title',
    'department',
    'email',
    'phone',
    'mobile',
    'homePhone',
    'otherPhone',
    'fax',
    'leadSource',
    'authority',
    'sourcePosture',
  ],
  account: [
    'ownerName',
    'accountName',
    'legalIdentity',
    'accountSite',
    'parentAccount',
    'accountNumber',
    'accountType',
    'industry',
    'website',
    'phone',
    'fax',
    'tickerSymbol',
    'ownership',
    'employees',
    'annualRevenue',
    'rating',
    'sourcePosture',
  ],
  deal: [
    'ownerName',
    'name',
    'accountName',
    'contactName',
    'stage',
    'pipeline',
    'typeLabel',
    'value',
    'amount',
    'probability',
    'expectedRevenue',
    'closingDate',
    'nextStep',
    'leadSource',
    'campaignSource',
    'contractLedger',
    'authority',
    'boardReadiness',
  ],
  task: [
    'ownerName',
    'subject',
    'dueDate',
    'contactName',
    'accountName',
    'status',
    'priority',
    'reminder',
    'repeat',
    'description',
    'auditTrail',
  ],
  meeting: [
    'ownerName',
    'name',
    'startsAt',
    'endsAt',
    'accountName',
    'location',
    'description',
    'auditTrail',
  ],
  call: [
    'ownerName',
    'subject',
    'phone',
    'callType',
    'callPurpose',
    'callResult',
    'startsAt',
    'durationSeconds',
    'contactName',
    'accountName',
    'description',
  ],
  campaign: [
    'ownerName',
    'name',
    'status',
    'startsAt',
    'endsAt',
    'value',
    'expectedRevenue',
    'description',
  ],
  document: [
    'ownerName',
    'fileName',
    'fileType',
    'fileUrl',
    'folder',
    'fileSize',
    'accountName',
    'contactName',
    'status',
    'sourceRegistryArtifactIds',
  ],
  visit: [
    'ownerName',
    'name',
    'visitType',
    'startsAt',
    'accountName',
    'contactName',
    'location',
    'status',
    'description',
  ],
  project: [
    'ownerName',
    'name',
    'accountName',
    'projectPhase',
    'status',
    'priority',
    'dueDate',
    'percentComplete',
    'value',
    'description',
  ],
  quote: [
    'ownerName',
    'name',
    'accountName',
    'contactName',
    'value',
    'currency',
    'status',
    'contractLedger',
  ],
  invoice: [
    'ownerName',
    'name',
    'accountName',
    'contactName',
    'value',
    'currency',
    'status',
    'linkedInvoiceIds',
  ],
  case: ['ownerName', 'subject', 'accountName', 'contactName', 'status', 'priority', 'description'],
  ticket: [
    'ownerName',
    'subject',
    'accountName',
    'contactName',
    'status',
    'priority',
    'description',
  ],
  contract: [
    'ownerName',
    'name',
    'accountName',
    'contactName',
    'contractLedger',
    'authority',
    'sourceRegistryArtifactIds',
  ],
  authority: ['ownerName', 'name', 'accountName', 'contactName', 'authority', 'legalIdentity'],
  risk: ['ownerName', 'name', 'accountName', 'status', 'priority', 'boardReadiness', 'description'],
  opportunity: [
    'ownerName',
    'name',
    'accountName',
    'contactName',
    'stage',
    'pipeline',
    'value',
    'probability',
    'expectedRevenue',
  ],
  supplier: [
    'ownerName',
    'accountName',
    'legalIdentity',
    'authority',
    'contractLedger',
    'sourcePosture',
  ],
  partner: [
    'ownerName',
    'accountName',
    'legalIdentity',
    'authority',
    'contractLedger',
    'sourcePosture',
  ],
});

/**
 * @function stableStringify
 * @description Serializes values with deterministic key ordering for route seals.
 * @param {*} value - Value to serialize.
 * @returns {string} Deterministic JSON string.
 * @collaboration Ensures CRM command responses can be fingerprinted for audit and boardroom replay.
 */
function stableStringify(value) {
  if (value === null || typeof value !== 'object') return JSON.stringify(value);

  if (Array.isArray(value)) {
    return `[${value.map(stableStringify).join(',')}]`;
  }

  return `{${Object.keys(value)
    .sort()
    .map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`)
    .join(',')}}`;
}

/**
 * @function createRouteSeal
 * @description Creates a SHA3-512 route fingerprint for CRM response proof.
 * @param {object} payload - Payload to seal.
 * @returns {string} SHA3-512 hex digest.
 * @collaboration Turns CRM API output into boardroom-auditable operating evidence.
 */
function createRouteSeal(payload = {}) {
  return crypto.createHash('sha3-512').update(stableStringify(payload)).digest('hex');
}

/**
 * @function getTenantId
 * @description Resolves tenant identity from query, headers or request context.
 * @param {object} req - Express request.
 * @returns {string} Tenant id.
 * @collaboration Keeps CRM records tenant-aware without inventing tenant context.
 */
function getTenantId(req) {
  return (
    req.query.tenantId ||
    req.headers['x-tenant-id'] ||
    req.tenantId ||
    req.user?.tenantId ||
    req.user?.tenant ||
    'WILSY_GLOBAL_ROOT'
  ).toString();
}

/**
 * @function getActor
 * @description Resolves the current actor for CRM audit fields.
 * @param {object} req - Express request.
 * @returns {string} Actor identity.
 * @collaboration Links CRM changes to operator responsibility and audit review.
 */
function getActor(req) {
  return (
    req.user?.id ||
    req.user?._id ||
    req.user?.email ||
    req.headers['x-user-id'] ||
    'system'
  ).toString();
}

/**
 * @function getResourceType
 * @description Maps public CRM resource names to internal record types.
 * @param {string} resource - Public resource name.
 * @returns {string|undefined} Internal CRM type.
 * @collaboration Preserves clean API URLs while the model keeps sovereign CRM semantics.
 */
function getResourceType(resource) {
  return RESOURCE_TYPES[resource];
}

/**
 * @function requireResourceType
 * @description Validates and resolves a CRM resource type.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @returns {string|null} Internal type or null after response.
 * @collaboration Prevents unknown modules from entering the CRM command spine.
 */
function requireResourceType(req, res) {
  const type = getResourceType(req.params.resource);

  if (!type) {
    res.status(404).json({
      success: false,
      message: 'CRM resource is not registered',
      truthPolicy: CRM_TRUTH_POLICY,
    });
    return null;
  }

  return type;
}

/**
 * @function normalizeRecord
 * @description Converts Mongoose documents or plain records into API-safe records.
 * @param {object} record - CRM record.
 * @returns {object|null} Normalized record.
 * @collaboration Gives frontend CRM, Source Registry and Executive Dashboard one predictable shape.
 */
function normalizeRecord(record) {
  const doc = record?.toObject ? record.toObject({ virtuals: true }) : record;

  if (!doc) return null;

  return {
    ...doc,
    id: doc._id?.toString?.() || doc.id,
    _id: doc._id?.toString?.() || doc._id,
    displayLabel:
      doc.displayLabel ||
      doc.displayName ||
      doc.name ||
      doc.accountName ||
      doc.company ||
      doc.subject ||
      doc.fileName ||
      '',
    legalName:
      doc.legalName ||
      doc.legalIdentity?.legalName ||
      doc.contractLedger?.counterpartyLegalName ||
      doc.accountName ||
      doc.company ||
      '',
    truthPolicy: CRM_TRUTH_POLICY,
  };
}

/**
 * @function asyncRoute
 * @description Wraps async route handlers and forwards failures to Express error middleware.
 * @param {Function} handler - Async route handler.
 * @returns {Function} Express middleware.
 * @collaboration Keeps CRM API failures controlled instead of collapsing the operating surface.
 */
function asyncRoute(handler) {
  return (req, res, next) => {
    Promise.resolve(handler(req, res, next)).catch(next);
  };
}

/**
 * @function escapeRegex
 * @description Escapes user search text before building a regular expression.
 * @param {string} value - Raw search value.
 * @returns {string} Regex-safe value.
 * @collaboration Keeps CRM search flexible without allowing regex injection.
 */
function escapeRegex(value = '') {
  return String(value).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * @function buildListQuery
 * @description Builds a tenant-bound CRM list query from resource filters.
 * @param {object} req - Express request.
 * @param {string} type - CRM record type.
 * @returns {object} MongoDB query.
 * @collaboration Lets the CRM cockpit filter live data without bypassing tenant boundaries.
 */
function buildListQuery(req, type) {
  const tenantId = getTenantId(req);
  const query = { tenantId, type };
  const search = (req.query.search || '').toString().trim();
  const stage = (req.query.stage || '').toString().trim();
  const status = (req.query.status || '').toString().trim();
  const ownerName = (req.query.ownerName || '').toString().trim();
  const accountName = (req.query.accountName || '').toString().trim();
  const sourcePosture = (req.query.sourcePosture || '').toString().trim();
  const boardStatus = (req.query.boardStatus || '').toString().trim();
  const authorityStatus = (req.query.authorityStatus || '').toString().trim();
  const contractStatus = (req.query.contractStatus || '').toString().trim();

  if (type === 'deal' && stage && stage.toUpperCase() !== 'ALL') query.stage = stage;
  if (status && status.toUpperCase() !== 'ALL') query.status = status;
  if (ownerName && ownerName.toUpperCase() !== 'ALL') query.ownerName = ownerName;
  if (accountName && accountName.toUpperCase() !== 'ALL') query.accountName = accountName;
  if (sourcePosture && sourcePosture.toUpperCase() !== 'ALL') query.sourcePosture = sourcePosture;
  if (boardStatus && boardStatus.toUpperCase() !== 'ALL')
    query['boardReadiness.status'] = boardStatus;
  if (authorityStatus && authorityStatus.toUpperCase() !== 'ALL')
    query['authority.status'] = authorityStatus;
  if (contractStatus && contractStatus.toUpperCase() !== 'ALL')
    query['contractLedger.status'] = contractStatus;

  if (search) {
    const pattern = new RegExp(escapeRegex(search), 'i');
    query.$or = [
      { name: pattern },
      { displayName: pattern },
      { email: pattern },
      { phone: pattern },
      { accountName: pattern },
      { company: pattern },
      { status: pattern },
      { stage: pattern },
      { industry: pattern },
      { companyDomainName: pattern },
      { subject: pattern },
      { description: pattern },
      { fileName: pattern },
      { folder: pattern },
      { title: pattern },
      { city: pattern },
      { country: pattern },
      { 'legalIdentity.legalName': pattern },
      { 'contractLedger.counterpartyLegalName': pattern },
      { 'contractLedger.agreementId': pattern },
      { 'authority.authorizedSignatoryName': pattern },
    ];
  }

  return query;
}

/**
 * @function sanitizeLimit
 * @description Converts requested limit into a safe pagination limit.
 * @param {*} value - Raw limit.
 * @returns {number} Safe limit.
 * @collaboration Protects the CRM route from unbounded list queries.
 */
function sanitizeLimit(value) {
  const limit = Number(value);

  if (!Number.isFinite(limit)) return 50;

  return Math.min(Math.max(Math.floor(limit), 1), 500);
}

/**
 * @function sanitizeOffset
 * @description Converts requested offset into a safe pagination offset.
 * @param {*} value - Raw offset.
 * @returns {number} Safe offset.
 * @collaboration Keeps CRM pagination deterministic for frontend cockpit tables.
 */
function sanitizeOffset(value) {
  const offset = Number(value);

  if (!Number.isFinite(offset)) return 0;

  return Math.max(Math.floor(offset), 0);
}

/**
 * @function hasAuditableSourcePayload
 * @description Checks whether a payload has enough source metadata to request VERIFIED posture.
 * @param {object} payload - CRM payload.
 * @returns {boolean} Whether auditable source metadata exists.
 * @collaboration Stops route-level fake VERIFIED attempts before the model guard runs.
 */
function hasAuditableSourcePayload(payload = {}) {
  return Boolean(
    payload.sourceEvidence?.sourceSystem &&
    payload.sourceEvidence?.sourceRecordId &&
    payload.sourceEvidence?.retrievedAt &&
    payload.sourceEvidence?.evidenceHash
  );
}

/**
 * @function buildRepairSignal
 * @description Builds a standardized CRM repair signal.
 * @param {object} signal - Signal input.
 * @returns {object} Repair signal.
 * @collaboration Converts CRM data gaps into executable work for operators.
 */
function buildRepairSignal(signal = {}) {
  return {
    code: signal.code || 'CRM_EVIDENCE_REQUIRED',
    status: signal.status || 'MISSING',
    connector: signal.connector || 'CRM / Contract Ledger',
    field: signal.field || '',
    message: signal.message || 'CRM evidence requires repair before board reliance.',
    operatorAction:
      signal.operatorAction || 'Attach auditable source evidence, authority and contract linkage.',
    severity: signal.severity || 'MEDIUM',
    createdAt: new Date(),
  };
}

/**
 * @function mergeRepairSignal
 * @description Adds a repair signal without duplicating the same field/code pair.
 * @param {Array<object>} signals - Existing signals.
 * @param {object} signal - Signal to add.
 * @returns {Array<object>} Merged repair signals.
 * @collaboration Keeps repair queues useful instead of noisy.
 */
function mergeRepairSignal(signals = [], signal = {}) {
  const next = Array.isArray(signals) ? [...signals] : [];
  const prepared = buildRepairSignal(signal);
  const exists = next.some((item) => item.code === prepared.code && item.field === prepared.field);

  if (!exists) next.push(prepared);

  return next;
}

/**
 * @function normalizeImportRecord
 * @description Normalizes incoming import records with tenant, actor and source metadata.
 * @param {object} record - Imported record.
 * @param {string} type - CRM record type.
 * @param {string} tenantId - Tenant id.
 * @param {string} actor - Actor id.
 * @param {string} importId - Import id.
 * @returns {object} Normalized import payload.
 * @collaboration Makes bulk import a governed evidence intake instead of a raw spreadsheet dump.
 */
function normalizeImportRecord(record, type, tenantId, actor, importId) {
  const sourceRecordId =
    record.sourceRecordId || record.externalId || record.metadata?.sourceRecordId || '';

  return {
    ...DEFAULTS_BY_TYPE[type],
    ...record,
    tenantId,
    type,
    sourceRecordId,
    sourceSystem: record.sourceSystem || record.metadata?.source || 'WILSY_CRM_IMPORT',
    createdBy: record.createdBy || actor,
    updatedBy: actor,
    metadata: {
      ...(record.metadata || {}),
      importId,
      importedAt: new Date().toISOString(),
      source: record.sourceSystem || record.metadata?.source || 'WILSY_CRM_IMPORT',
      sourceRecordId,
    },
  };
}

/**
 * @function computeDerivedFields
 * @description Computes identity, commercial, contract and evidence posture fields.
 * @param {object} payload - Raw CRM payload.
 * @returns {object} Derived payload.
 * @collaboration Turns CRUD input into Wilsy OS commercial truth without creating synthetic records.
 */
function computeDerivedFields(payload) {
  const next = { ...payload };

  if (!next.name) {
    next.name =
      [next.firstName, next.lastName].filter(Boolean).join(' ') ||
      next.accountName ||
      next.company ||
      next.subject ||
      next.fileName ||
      '';
  }

  next.displayName =
    next.displayName ||
    next.name ||
    next.accountName ||
    next.company ||
    next.contactName ||
    next.subject ||
    next.fileName ||
    '';
  if (!next.accountName && next.company) next.accountName = next.company;

  if (!next.companyDomainName && next.website) {
    next.companyDomainName = next.website
      .replace(/^https?:\/\//, '')
      .replace(/^www\./, '')
      .split('/')[0];
  }

  next.sourceRecordId =
    next.sourceRecordId || next.externalId || next.sourceEvidence?.sourceRecordId || '';

  next.legalIdentity = {
    ...(next.legalIdentity || {}),
    legalName:
      next.legalIdentity?.legalName ||
      next.contractLedger?.counterpartyLegalName ||
      next.accountName ||
      next.company ||
      next.name ||
      '',
  };

  next.contractLedger = {
    ...(next.contractLedger || {}),
    counterpartyLegalName:
      next.contractLedger?.counterpartyLegalName ||
      next.legalIdentity?.legalName ||
      next.accountName ||
      next.company ||
      '',
    agreementId: next.contractLedger?.agreementId || next.agreementId || next.contractId || '',
  };

  if (next.amount && !next.value) next.value = next.amount;
  if (next.value && !next.amount) next.amount = next.value;

  if (next.type === 'deal' || next.type === 'opportunity') {
    const value = Number(next.value || next.amount || 0);
    const probability = Number(next.probability || 0) / 100;
    next.expectedRevenue = Number.isFinite(value * probability)
      ? Math.round(value * probability)
      : 0;
  }

  if (next.sourcePosture === 'VERIFIED' && !hasAuditableSourcePayload(next)) {
    next.sourcePosture = 'MISSING';
    next.repairSignals = mergeRepairSignal(next.repairSignals, {
      code: 'CRM_VERIFIED_WITHOUT_AUDITABLE_SOURCE',
      field: 'sourceEvidence',
      message: 'CRM route rejected VERIFIED posture because source evidence is incomplete.',
      operatorAction:
        'Attach sourceSystem, sourceRecordId, retrievedAt and evidenceHash before VERIFIED is allowed.',
      severity: 'HIGH',
    });
  }

  next.boardReadiness = {
    ...(next.boardReadiness || {}),
    sourcePosture: next.sourcePosture || 'NOT_EVALUATED',
    authorityPosture: next.authority?.status || next.boardReadiness?.authorityPosture || 'UNKNOWN',
    contractPosture: next.contractLedger?.status || next.boardReadiness?.contractPosture || 'NONE',
    repairSignalCount: Array.isArray(next.repairSignals) ? next.repairSignals.length : 0,
    lastAssessedAt: new Date(),
  };

  return next;
}

/**
 * @function buildSourceRegistryProjection
 * @description Projects CRM records into Source Registry evidence form.
 * @param {object} record - CRM record or document.
 * @returns {object} Source Registry projection.
 * @collaboration Connects CRM directly to legal artifact verification and boardroom proof readiness.
 */
function buildSourceRegistryProjection(record = {}) {
  if (typeof record.toSourceRegistryEvidence === 'function') {
    return record.toSourceRegistryEvidence();
  }

  const normalized = normalizeRecord(record) || {};
  const sourceEvidence = normalized.sourceEvidence || {};

  return {
    connector: 'CRM / Contract Ledger',
    recordId: normalized.id || normalized._id || '',
    tenantId: normalized.tenantId,
    type: normalized.type,
    title: normalized.displayLabel || normalized.displayName || normalized.name,
    legalName:
      normalized.legalName ||
      normalized.legalIdentity?.legalName ||
      normalized.contractLedger?.counterpartyLegalName ||
      '',
    sourcePosture: normalized.sourcePosture || 'NOT_EVALUATED',
    sourceSystem: sourceEvidence.sourceSystem || normalized.sourceSystem || 'WILSY_OS',
    sourceRecordId:
      sourceEvidence.sourceRecordId || normalized.sourceRecordId || normalized.externalId || '',
    retrievedAt: sourceEvidence.retrievedAt || null,
    evidenceHash: sourceEvidence.evidenceHash || '',
    authorityStatus: normalized.authority?.status || 'UNKNOWN',
    contractStatus: normalized.contractLedger?.status || 'NONE',
    agreementId: normalized.contractLedger?.agreementId || '',
    boardReadiness: normalized.boardReadiness?.status || 'NOT_READY',
    readinessScore: normalized.boardReadiness?.readinessScore || 0,
    repairSignals: normalized.repairSignals || [],
    truthPolicy: CRM_TRUTH_POLICY,
  };
}

/**
 * @function buildCommandNarrative
 * @description Builds a boardroom-readable CRM command narrative from summary values.
 * @param {object} stats - CRM summary stats.
 * @returns {string} Command narrative.
 * @collaboration Makes CRM metrics tell an operating-system story instead of showing raw counters.
 */
function buildCommandNarrative(stats = {}) {
  if (!stats.total) {
    return 'CRM command spine is live. Empty collection is valid state; import or create real records before evidence reliance.';
  }

  return `CRM command spine is live with ${stats.total} records, ${stats.openDealValue || 0} total open pipeline value and ${stats.repairSignalCount || 0} evidence repair signals.`;
}

/**
 * @function buildCommandEnvelope
 * @description Wraps route payloads with version, truth policy and seal.
 * @param {object} payload - Payload.
 * @returns {object} Command envelope.
 * @collaboration Standardizes CRM route responses for the Executive Dashboard and audit replay.
 */
function buildCommandEnvelope(payload = {}) {
  const envelope = {
    ...payload,
    routeVersion: CRM_ROUTE_VERSION,
    truthPolicy: CRM_TRUTH_POLICY,
    timestamp: new Date().toISOString(),
  };

  return {
    ...envelope,
    routeSeal: createRouteSeal(envelope),
  };
}

/**
 * @function handleCrmHealth
 * @description Returns CRM route health and available command resources.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @returns {object} JSON response.
 * @collaboration Gives operators a live proof that the CRM route layer is mounted.
 */
function handleCrmHealth(req, res) {
  return res.json(
    buildCommandEnvelope({
      success: true,
      status: 'CRM_COMMAND_SPINE_MOUNTED',
      resources: Object.keys(RESOURCE_TYPES),
      commandSurfaces: [
        'records',
        'imports',
        'source-registry-evidence',
        'board-readiness',
        'authority',
        'contract-ledger',
        'repair-signals',
      ],
    })
  );
}

/**
 * @function handleCrmSchema
 * @description Returns CRM schema blueprints and route capabilities.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @returns {object} JSON response.
 * @collaboration Lets the frontend render CRM forms without hardcoded prototype assumptions.
 */
function handleCrmSchema(req, res) {
  return res.json(
    buildCommandEnvelope({
      success: true,
      resources: Object.keys(RESOURCE_TYPES),
      fields: CRM_FIELD_BLUEPRINTS,
      defaults: DEFAULTS_BY_TYPE,
      sourcePostures: SOURCE_POSTURES,
      story:
        'Wilsy OS CRM is the commercial truth spine: records become legal identity, authority, contract and boardroom evidence.',
    })
  );
}

/**
 * @function handleCrmSummary
 * @description Returns tenant CRM summary grouped by type and revenue.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @returns {Promise<object>} JSON response.
 * @collaboration Feeds CRM cockpit cards with live tenant-bound data.
 */
async function handleCrmSummary(req, res) {
  const tenantId = getTenantId(req);
  const rows = await CrmRecord.aggregate([
    { $match: { tenantId } },
    {
      $group: {
        _id: '$type',
        total: { $sum: 1 },
        value: { $sum: '$value' },
        expectedRevenue: { $sum: '$expectedRevenue' },
        repairSignals: { $sum: { $size: { $ifNull: ['$repairSignals', []] } } },
      },
    },
  ]);

  const summary = rows.reduce((acc, row) => {
    acc[row._id] = {
      total: row.total,
      value: row.value,
      expectedRevenue: row.expectedRevenue,
      repairSignals: row.repairSignals,
    };
    return acc;
  }, {});

  return res.json(
    buildCommandEnvelope({
      success: true,
      tenantId,
      summary,
    })
  );
}

/**
 * @function handleCommandCenter
 * @description Returns an executive CRM command-center snapshot.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @returns {Promise<object>} JSON response.
 * @collaboration Elevates CRM above records by exposing pipeline, evidence posture and board readiness.
 */
async function handleCommandCenter(req, res) {
  const tenantId = getTenantId(req);

  const [byType, bySourcePosture, byBoardReadiness, pipelineRows, repairRows, total] =
    await Promise.all([
      CrmRecord.aggregate([
        { $match: { tenantId } },
        { $group: { _id: '$type', total: { $sum: 1 } } },
      ]),
      CrmRecord.aggregate([
        { $match: { tenantId } },
        { $group: { _id: '$sourcePosture', total: { $sum: 1 } } },
      ]),
      CrmRecord.aggregate([
        { $match: { tenantId } },
        { $group: { _id: '$boardReadiness.status', total: { $sum: 1 } } },
      ]),
      CrmRecord.aggregate([
        { $match: { tenantId, type: { $in: ['deal', 'opportunity'] } } },
        {
          $group: {
            _id: '$stage',
            total: { $sum: 1 },
            value: { $sum: '$value' },
            expectedRevenue: { $sum: '$expectedRevenue' },
          },
        },
      ]),
      CrmRecord.aggregate([
        { $match: { tenantId } },
        { $project: { repairCount: { $size: { $ifNull: ['$repairSignals', []] } } } },
        { $group: { _id: null, total: { $sum: '$repairCount' } } },
      ]),
      CrmRecord.countDocuments({ tenantId }),
    ]);

  const openDealValue = pipelineRows.reduce((sum, row) => sum + Number(row.value || 0), 0);
  const repairSignalCount = repairRows[0]?.total || 0;

  return res.json(
    buildCommandEnvelope({
      success: true,
      tenantId,
      total,
      narrative: buildCommandNarrative({ total, openDealValue, repairSignalCount }),
      byType,
      bySourcePosture,
      byBoardReadiness,
      pipeline: pipelineRows,
      repairSignalCount,
    })
  );
}

/**
 * @function handleSourceRegistryEvidence
 * @description Returns CRM records projected as Source Registry evidence.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @returns {Promise<object>} JSON response.
 * @collaboration Lets Legal Artifact Studio verify counterparty, contract and authority evidence from CRM.
 */
async function handleSourceRegistryEvidence(req, res) {
  const tenantId = getTenantId(req);
  const limit = sanitizeLimit(req.query.limit);
  const options = {
    tenantId,
    limit,
    type: req.query.type,
    agreementId: req.query.agreementId,
    artifactId: req.query.artifactId,
    counterpartyLegalName: req.query.counterpartyLegalName,
    sourcePosture: req.query.sourcePosture,
  };

  const records =
    typeof CrmRecord.findForSourceRegistry === 'function'
      ? await CrmRecord.findForSourceRegistry(options)
      : await CrmRecord.find({ tenantId })
          .sort({ updatedAt: -1, createdAt: -1 })
          .limit(limit)
          .lean();

  return res.json(
    buildCommandEnvelope({
      success: true,
      tenantId,
      total: records.length,
      evidence: records.map(buildSourceRegistryProjection),
    })
  );
}

/**
 * @function handleListResource
 * @description Lists CRM records for one resource.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @returns {Promise<object>} JSON response.
 * @collaboration Powers Zoho-class list screens while adding Wilsy evidence posture.
 */
async function handleListResource(req, res) {
  const type = requireResourceType(req, res);
  if (!type) return null;

  const limit = sanitizeLimit(req.query.limit);
  const offset = sanitizeOffset(req.query.offset);
  const query = buildListQuery(req, type);

  const [items, total] = await Promise.all([
    CrmRecord.find(query).sort({ updatedAt: -1, createdAt: -1 }).skip(offset).limit(limit),
    CrmRecord.countDocuments(query),
  ]);

  return res.json(
    buildCommandEnvelope({
      success: true,
      items: items.map(normalizeRecord),
      total,
      limit,
      offset,
      hasMore: offset + limit < total,
      tenantId: getTenantId(req),
      resource: req.params.resource,
      type,
    })
  );
}

/**
 * @function handleGetRecord
 * @description Returns one CRM record with Source Registry projection.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @returns {Promise<object>} JSON response.
 * @collaboration Turns a CRM detail page into an evidence dossier.
 */
async function handleGetRecord(req, res) {
  const type = requireResourceType(req, res);
  if (!type) return null;

  if (!mongoose.Types.ObjectId.isValid(req.params.id)) {
    return res
      .status(400)
      .json({ success: false, message: 'Invalid CRM record id', truthPolicy: CRM_TRUTH_POLICY });
  }

  const record = await CrmRecord.findOne({ _id: req.params.id, tenantId: getTenantId(req), type });

  if (!record) {
    return res
      .status(404)
      .json({ success: false, message: 'CRM record not found', truthPolicy: CRM_TRUTH_POLICY });
  }

  return res.json(
    buildCommandEnvelope({
      success: true,
      record: normalizeRecord(record),
      sourceRegistryEvidence: buildSourceRegistryProjection(record),
    })
  );
}

/**
 * @function handleCreateRecord
 * @description Creates one CRM record with evidence posture controls.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @returns {Promise<object>} JSON response.
 * @collaboration Makes record creation a governed intake into Wilsy OS commercial truth.
 */
async function handleCreateRecord(req, res) {
  const type = requireResourceType(req, res);
  if (!type) return null;

  const tenantId = getTenantId(req);
  const actor = getActor(req);
  const payload = {
    ...DEFAULTS_BY_TYPE[type],
    ...req.body,
    tenantId,
    type,
    createdBy: actor,
    updatedBy: actor,
  };
  const finalPayload = computeDerivedFields(payload);

  if (
    !finalPayload.name &&
    !finalPayload.email &&
    !finalPayload.phone &&
    !finalPayload.accountName &&
    ['lead', 'contact', 'account', 'deal', 'opportunity', 'supplier', 'partner'].includes(type)
  ) {
    return res.status(400).json({
      success: false,
      message: 'Name, email, phone or account is required for this CRM record',
      truthPolicy: CRM_TRUTH_POLICY,
    });
  }

  const created = await CrmRecord.create(finalPayload);

  return res.status(201).json(
    buildCommandEnvelope({
      success: true,
      record: normalizeRecord(created),
      sourceRegistryEvidence: buildSourceRegistryProjection(created),
    })
  );
}

/**
 * @function handlePreviewImport
 * @description Previews a CRM import batch before persistence.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @returns {Promise<object>} JSON response.
 * @collaboration Makes imports explain duplicate risk, identity coverage and evidence posture before data enters CRM.
 */
async function handlePreviewImport(req, res) {
  const type = requireResourceType(req, res);
  if (!type) return null;

  const records = Array.isArray(req.body?.records) ? req.body.records : [];
  if (!records.length) {
    return res
      .status(400)
      .json({
        success: false,
        message: 'Preview payload must include records',
        truthPolicy: CRM_TRUTH_POLICY,
      });
  }

  const tenantId = getTenantId(req);
  const dedupeKey = req.body?.dedupeKey || (['lead', 'contact'].includes(type) ? 'email' : 'name');
  const blueprint = CRM_FIELD_BLUEPRINTS[type] || [];
  const normalized = records.map((record) =>
    computeDerivedFields({ ...DEFAULTS_BY_TYPE[type], ...record, tenantId, type })
  );
  const mappedFieldSet = new Set();
  let missingIdentity = 0;
  let attemptedFakeVerified = 0;

  normalized.forEach((record) => {
    blueprint.forEach((field) => {
      if (record[field] !== undefined && record[field] !== null && record[field] !== '')
        mappedFieldSet.add(field);
    });
    if (!record.name && !record.email && !record.phone && !record.accountName) missingIdentity += 1;
    if (record.sourcePosture === 'MISSING' && req.body?.sourcePosture === 'VERIFIED')
      attemptedFakeVerified += 1;
  });

  const dedupeValues = [...new Set(normalized.map((record) => record[dedupeKey]).filter(Boolean))];
  const duplicateCandidates = dedupeValues.length
    ? await CrmRecord.countDocuments({ tenantId, type, [dedupeKey]: { $in: dedupeValues } })
    : 0;
  const fieldCoverage = blueprint.length
    ? Math.round((mappedFieldSet.size / blueprint.length) * 100)
    : 0;

  return res.json(
    buildCommandEnvelope({
      success: true,
      resource: req.params.resource,
      sourceSystem: req.body?.sourceSystem || 'UNKNOWN',
      received: records.length,
      ready: Math.max(records.length - missingIdentity, 0),
      needsReview: missingIdentity,
      duplicateCandidates,
      dedupeKey,
      fieldCoverage,
      mappedFields: [...mappedFieldSet],
      missingIdentity,
      attemptedFakeVerified,
    })
  );
}

/**
 * @function handleImportRecords
 * @description Imports CRM records with dedupe and evidence posture controls.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @returns {Promise<object>} JSON response.
 * @collaboration Moves CRM import beyond spreadsheet upload into governed operating intake.
 */
async function handleImportRecords(req, res) {
  const type = requireResourceType(req, res);
  if (!type) return null;

  const records = Array.isArray(req.body?.records) ? req.body.records : [];
  if (!records.length) {
    return res
      .status(400)
      .json({
        success: false,
        message: 'Import payload must include records',
        truthPolicy: CRM_TRUTH_POLICY,
      });
  }
  if (records.length > 10000) {
    return res
      .status(413)
      .json({
        success: false,
        message: 'Import batch exceeds 10000 records',
        truthPolicy: CRM_TRUTH_POLICY,
      });
  }

  const tenantId = getTenantId(req);
  const actor = getActor(req);
  const mode = ['insert', 'upsert'].includes(req.body?.mode) ? req.body.mode : 'upsert';
  const dedupeKey = req.body?.dedupeKey || (['lead', 'contact'].includes(type) ? 'email' : 'name');
  const sourceSystem = req.body?.sourceSystem || 'WILSY_CRM_IMPORT';
  const importId = `CRM-IMPORT-${Date.now()}-${Math.random().toString(16).slice(2, 8).toUpperCase()}`;

  const report = {
    success: true,
    importId,
    resource: req.params.resource,
    type,
    mode,
    dedupeKey,
    received: records.length,
    inserted: 0,
    updated: 0,
    skipped: 0,
    errors: [],
    truthPolicy: CRM_TRUTH_POLICY,
  };

  for (const [index, rawRecord] of records.entries()) {
    const payload = computeDerivedFields(
      normalizeImportRecord({ ...rawRecord, sourceSystem }, type, tenantId, actor, importId)
    );
    const hasIdentity = payload.name || payload.email || payload.phone || payload.accountName;

    if (!hasIdentity) {
      report.skipped += 1;
      report.errors.push({ row: index + 1, message: 'Missing name, email, phone or account' });
      continue;
    }

    try {
      const dedupeValue = payload[dedupeKey];

      if (mode === 'upsert' && dedupeValue) {
        const existing = await CrmRecord.findOne({ tenantId, type, [dedupeKey]: dedupeValue });
        if (existing) {
          await CrmRecord.updateOne(
            { _id: existing._id },
            { $set: payload },
            { runValidators: true }
          );
          report.updated += 1;
          continue;
        }
      }

      await CrmRecord.create(payload);
      report.inserted += 1;
    } catch (error) {
      report.skipped += 1;
      report.errors.push({ row: index + 1, message: error.message });
    }
  }

  return res.status(201).json(buildCommandEnvelope(report));
}

/**
 * @function handleUpdateRecord
 * @description Updates one CRM record with route-level evidence posture controls.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @returns {Promise<object>} JSON response.
 * @collaboration Keeps CRM edits aligned to the model evidence guard.
 */
async function handleUpdateRecord(req, res) {
  const type = requireResourceType(req, res);
  if (!type) return null;

  if (!mongoose.Types.ObjectId.isValid(req.params.id)) {
    return res
      .status(400)
      .json({ success: false, message: 'Invalid CRM record id', truthPolicy: CRM_TRUTH_POLICY });
  }

  const updated = await CrmRecord.findOneAndUpdate(
    { _id: req.params.id, tenantId: getTenantId(req), type },
    computeDerivedFields({ ...req.body, type, updatedBy: getActor(req) }),
    { new: true, runValidators: true }
  );

  if (!updated) {
    return res
      .status(404)
      .json({ success: false, message: 'CRM record not found', truthPolicy: CRM_TRUTH_POLICY });
  }

  return res.json(
    buildCommandEnvelope({
      success: true,
      record: normalizeRecord(updated),
      sourceRegistryEvidence: buildSourceRegistryProjection(updated),
    })
  );
}

/**
 * @function handleAttachRepairSignal
 * @description Adds an operator repair signal to one CRM record.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @returns {Promise<object>} JSON response.
 * @collaboration Lets Wilsy OS convert CRM evidence gaps into tracked repair work.
 */
async function handleAttachRepairSignal(req, res) {
  const type = requireResourceType(req, res);
  if (!type) return null;

  if (!mongoose.Types.ObjectId.isValid(req.params.id)) {
    return res
      .status(400)
      .json({ success: false, message: 'Invalid CRM record id', truthPolicy: CRM_TRUTH_POLICY });
  }

  const record = await CrmRecord.findOne({ _id: req.params.id, tenantId: getTenantId(req), type });

  if (!record) {
    return res
      .status(404)
      .json({ success: false, message: 'CRM record not found', truthPolicy: CRM_TRUTH_POLICY });
  }

  if (typeof record.appendRepairSignal === 'function') {
    record.appendRepairSignal(req.body || {});
  } else {
    record.repairSignals = mergeRepairSignal(record.repairSignals, req.body || {});
  }

  record.updatedBy = getActor(req);
  await record.save();

  return res.json(
    buildCommandEnvelope({
      success: true,
      record: normalizeRecord(record),
      sourceRegistryEvidence: buildSourceRegistryProjection(record),
    })
  );
}

/**
 * @function handlePatchAuthority
 * @description Updates the authority posture for a CRM record.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @returns {Promise<object>} JSON response.
 * @collaboration Makes contacts, accounts and deals authority-aware before boardroom reliance.
 */
async function handlePatchAuthority(req, res) {
  const type = requireResourceType(req, res);
  if (!type) return null;

  if (!mongoose.Types.ObjectId.isValid(req.params.id)) {
    return res
      .status(400)
      .json({ success: false, message: 'Invalid CRM record id', truthPolicy: CRM_TRUTH_POLICY });
  }

  const updated = await CrmRecord.findOneAndUpdate(
    { _id: req.params.id, tenantId: getTenantId(req), type },
    computeDerivedFields({
      authority: req.body || {},
      updatedBy: getActor(req),
    }),
    { new: true, runValidators: true }
  );

  if (!updated) {
    return res
      .status(404)
      .json({ success: false, message: 'CRM record not found', truthPolicy: CRM_TRUTH_POLICY });
  }

  return res.json(
    buildCommandEnvelope({
      success: true,
      record: normalizeRecord(updated),
      sourceRegistryEvidence: buildSourceRegistryProjection(updated),
    })
  );
}

/**
 * @function handlePatchContractLedger
 * @description Updates contract-ledger posture for a CRM record.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @returns {Promise<object>} JSON response.
 * @collaboration Links CRM pipeline and accounts to legal artifacts and Source Registry verification.
 */
async function handlePatchContractLedger(req, res) {
  const type = requireResourceType(req, res);
  if (!type) return null;

  if (!mongoose.Types.ObjectId.isValid(req.params.id)) {
    return res
      .status(400)
      .json({ success: false, message: 'Invalid CRM record id', truthPolicy: CRM_TRUTH_POLICY });
  }

  const updated = await CrmRecord.findOneAndUpdate(
    { _id: req.params.id, tenantId: getTenantId(req), type },
    computeDerivedFields({
      contractLedger: req.body || {},
      updatedBy: getActor(req),
    }),
    { new: true, runValidators: true }
  );

  if (!updated) {
    return res
      .status(404)
      .json({ success: false, message: 'CRM record not found', truthPolicy: CRM_TRUTH_POLICY });
  }

  return res.json(
    buildCommandEnvelope({
      success: true,
      record: normalizeRecord(updated),
      sourceRegistryEvidence: buildSourceRegistryProjection(updated),
    })
  );
}

/**
 * @function handleDeleteRecord
 * @description Deletes one CRM record inside tenant boundary.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @returns {Promise<object>} JSON response.
 * @collaboration Keeps destructive CRM operations explicit and tenant-bound.
 */
async function handleDeleteRecord(req, res) {
  const type = requireResourceType(req, res);
  if (!type) return null;

  if (!mongoose.Types.ObjectId.isValid(req.params.id)) {
    return res
      .status(400)
      .json({ success: false, message: 'Invalid CRM record id', truthPolicy: CRM_TRUTH_POLICY });
  }

  const deleted = await CrmRecord.findOneAndDelete({
    _id: req.params.id,
    tenantId: getTenantId(req),
    type,
  });

  if (!deleted) {
    return res
      .status(404)
      .json({ success: false, message: 'CRM record not found', truthPolicy: CRM_TRUTH_POLICY });
  }

  return res.json(
    buildCommandEnvelope({
      success: true,
      id: req.params.id,
      resource: req.params.resource,
    })
  );
}

/**
 * @function handleCrmRouteError
 * @description Converts CRM route errors into safe API responses.
 * @param {Error} err - Error object.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @param {Function} next - Express next callback.
 * @returns {object|void} Error response or next delegation.
 * @collaboration Keeps route failures operationally visible without exposing internals.
 */
function handleCrmRouteError(err, req, res, next) {
  if (err?.name === 'ValidationError') {
    return res
      .status(400)
      .json({ success: false, message: err.message, truthPolicy: CRM_TRUTH_POLICY });
  }

  if (err?.name === 'CastError') {
    return res
      .status(400)
      .json({ success: false, message: 'Invalid CRM record id', truthPolicy: CRM_TRUTH_POLICY });
  }

  return next(err);
}

router.get('/health', handleCrmHealth);
router.get('/schema', handleCrmSchema);
router.get('/summary', asyncRoute(handleCrmSummary));
router.get('/command-center', asyncRoute(handleCommandCenter));
router.get('/source-registry-evidence', asyncRoute(handleSourceRegistryEvidence));

router.get('/:resource', asyncRoute(handleListResource));
router.get('/:resource/:id', asyncRoute(handleGetRecord));
router.post('/:resource', asyncRoute(handleCreateRecord));
router.post('/:resource/import', asyncRoute(handleImportRecords));
router.post('/:resource/preview-import', asyncRoute(handlePreviewImport));
router.post('/:resource/:id/repair-signal', asyncRoute(handleAttachRepairSignal));
router.patch('/:resource/:id/authority', asyncRoute(handlePatchAuthority));
router.patch('/:resource/:id/contract-ledger', asyncRoute(handlePatchContractLedger));
router.put('/:resource/:id', asyncRoute(handleUpdateRecord));
router.delete('/:resource/:id', asyncRoute(handleDeleteRecord));

router.use(handleCrmRouteError);

export default router;
