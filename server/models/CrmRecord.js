/* eslint-disable */
/**
 * WILSY OS — SOVEREIGN CRM RECORD LEDGER
 * VERSION: 2.0.0-EPITOME-EVIDENCE-SPINE
 *
 * Mandate:
 * This model is not a clone of Zoho, HubSpot, or Salesforce.
 * It is the commercial truth layer of Wilsy OS.
 *
 * Story:
 * - Lead is origin-of-obligation.
 * - Contact is authority and communication evidence.
 * - Account is counterparty legal identity.
 * - Deal is contract intent plus commercial risk.
 * - Task is audit activity.
 * - Meeting is negotiation evidence.
 * - Document is a legal artifact linked to source truth.
 *
 * Truth policy:
 * Empty collections are valid live state.
 * No synthetic records.
 * No fake VERIFIED status.
 */

import mongoose from 'mongoose';

const { Schema } = mongoose;

export const WILSY_OS_CRM_EPITOME_VERSION = '2.0.0-EPITOME-EVIDENCE-SPINE';
export const WILSY_OS_CRM_TRUTH_POLICY = 'NO_FAKE_VERIFIED';

export const CRM_RECORD_TYPES = [
  'lead',
  'contact',
  'account',
  'deal',
  'task',
  'meeting',
  'call',
  'campaign',
  'document',
  'visit',
  'project',
  'quote',
  'invoice',
  'case',
  'ticket',
  'contract',
  'authority',
  'risk',
  'opportunity',
  'supplier',
  'partner',
];

export const CRM_SOURCE_POSTURES = [
  'NOT_EVALUATED',
  'PENDING',
  'MISSING',
  'ERROR',
  'BLOCKED',
  'READY_FOR_ANCHOR',
  'VERIFIED',
];

export const CRM_AUTHORITY_STATES = [
  'UNKNOWN',
  'PENDING',
  'MISSING',
  'VALIDATED',
  'VERIFIED',
  'EXPIRED',
  'REVOKED',
  'BLOCKED',
];

export const CRM_CONTRACT_STATES = [
  'NONE',
  'INTENT',
  'DRAFTING',
  'IN_REVIEW',
  'NEGOTIATION',
  'APPROVED',
  'SIGNED',
  'ACTIVE',
  'EXPIRED',
  'TERMINATED',
  'DISPUTED',
  'BLOCKED',
];

export const CRM_BOARD_READINESS_STATES = [
  'NOT_READY',
  'NEEDS_EVIDENCE',
  'NEEDS_AUTHORITY',
  'NEEDS_CONTRACT',
  'NEEDS_COMPLIANCE',
  'READY_FOR_REVIEW',
  'READY_FOR_BOARDROOM',
  'SEALED',
];

export const CRM_RISK_LEVELS = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];

const EvidenceSourceSchema = new Schema(
  {
    sourceSystem: { type: String, trim: true, default: 'WILSY_OS', index: true },
    sourceRecordId: { type: String, trim: true, default: '', index: true },
    sourceRecordUrl: { type: String, trim: true, default: '' },
    sourceModule: { type: String, trim: true, default: '' },
    sourcePayloadHash: { type: String, trim: true, default: '' },
    evidenceHash: { type: String, trim: true, default: '' },
    retrievedAt: { type: Date, default: null },
    verifiedAt: { type: Date, default: null },
    verifiedBy: { type: String, trim: true, default: '' },
    confidence: { type: Number, min: 0, max: 100, default: 0 },
    status: { type: String, enum: CRM_SOURCE_POSTURES, default: 'NOT_EVALUATED' },
    message: { type: String, trim: true, default: '' },
  },
  { _id: false }
);

const RepairSignalSchema = new Schema(
  {
    code: { type: String, trim: true, default: '' },
    status: { type: String, enum: CRM_SOURCE_POSTURES, default: 'MISSING' },
    connector: { type: String, trim: true, default: 'CRM / Contract Ledger' },
    field: { type: String, trim: true, default: '' },
    message: { type: String, trim: true, default: '' },
    operatorAction: { type: String, trim: true, default: '' },
    severity: { type: String, enum: CRM_RISK_LEVELS, default: 'MEDIUM' },
    createdAt: { type: Date, default: Date.now },
  },
  { _id: false }
);

const LegalIdentitySchema = new Schema(
  {
    legalName: { type: String, trim: true, default: '', index: true },
    tradingName: { type: String, trim: true, default: '' },
    registrationNumber: { type: String, trim: true, default: '', index: true },
    taxNumber: { type: String, trim: true, default: '' },
    vatNumber: { type: String, trim: true, default: '' },
    jurisdiction: { type: String, trim: true, default: '' },
    entityType: { type: String, trim: true, default: '' },
    beneficialOwner: { type: String, trim: true, default: '' },
    websiteDomain: { type: String, trim: true, lowercase: true, default: '', index: true },
    evidence: { type: EvidenceSourceSchema, default: () => ({}) },
  },
  { _id: false }
);

const AuthoritySchema = new Schema(
  {
    status: { type: String, enum: CRM_AUTHORITY_STATES, default: 'UNKNOWN', index: true },
    authorizedSignatoryName: { type: String, trim: true, default: '' },
    authorizedSignatoryTitle: { type: String, trim: true, default: '' },
    authorityEvidenceType: { type: String, trim: true, default: '' },
    authorityReference: { type: String, trim: true, default: '' },
    boardResolutionId: { type: String, trim: true, default: '' },
    delegationOfAuthorityId: { type: String, trim: true, default: '' },
    powerOfAttorneyId: { type: String, trim: true, default: '' },
    expiresAt: { type: Date, default: null },
    evidence: { type: EvidenceSourceSchema, default: () => ({}) },
  },
  { _id: false }
);

const ContractLedgerSchema = new Schema(
  {
    status: { type: String, enum: CRM_CONTRACT_STATES, default: 'NONE', index: true },
    agreementId: { type: String, trim: true, default: '', index: true },
    contractId: { type: String, trim: true, default: '', index: true },
    artifactId: { type: String, trim: true, default: '', index: true },
    artifactType: { type: String, trim: true, default: '' },
    governingDocumentName: { type: String, trim: true, default: '' },
    signatureStatus: { type: String, trim: true, default: '' },
    counterpartyLegalName: { type: String, trim: true, default: '', index: true },
    contractValue: { type: Number, default: 0 },
    currency: { type: String, trim: true, default: 'ZAR' },
    effectiveDate: { type: Date, default: null },
    expiryDate: { type: Date, default: null },
    renewalDate: { type: Date, default: null },
    sourceRegistryArtifactId: { type: String, trim: true, default: '' },
    evidence: { type: EvidenceSourceSchema, default: () => ({}) },
  },
  { _id: false }
);

const CommercialTruthSchema = new Schema(
  {
    pipeline: { type: String, trim: true, default: 'default' },
    stage: { type: String, trim: true, default: '' },
    forecastCategory: { type: String, trim: true, default: '' },
    nextBestAction: { type: String, trim: true, default: '' },
    objection: { type: String, trim: true, default: '' },
    closePlan: { type: String, trim: true, default: '' },
    decisionProcess: { type: String, trim: true, default: '' },
    economicBuyer: { type: String, trim: true, default: '' },
    champion: { type: String, trim: true, default: '' },
    competitors: [{ type: String, trim: true }],
    winThemes: [{ type: String, trim: true }],
    lossRisks: [{ type: String, trim: true }],
  },
  { _id: false }
);

const BoardReadinessSchema = new Schema(
  {
    status: { type: String, enum: CRM_BOARD_READINESS_STATES, default: 'NOT_READY', index: true },
    readinessScore: { type: Number, min: 0, max: 100, default: 0 },
    riskLevel: { type: String, enum: CRM_RISK_LEVELS, default: 'MEDIUM', index: true },
    sourcePosture: { type: String, enum: CRM_SOURCE_POSTURES, default: 'NOT_EVALUATED' },
    authorityPosture: { type: String, enum: CRM_AUTHORITY_STATES, default: 'UNKNOWN' },
    contractPosture: { type: String, enum: CRM_CONTRACT_STATES, default: 'NONE' },
    compliancePosture: { type: String, enum: CRM_SOURCE_POSTURES, default: 'NOT_EVALUATED' },
    financePosture: { type: String, enum: CRM_SOURCE_POSTURES, default: 'NOT_EVALUATED' },
    repairSignalCount: { type: Number, min: 0, default: 0 },
    boardroomNarrative: { type: String, trim: true, default: '' },
    lastAssessedAt: { type: Date, default: null },
  },
  { _id: false }
);

const AuditTrailSchema = new Schema(
  {
    action: { type: String, trim: true, default: '' },
    actor: { type: String, trim: true, default: '' },
    source: { type: String, trim: true, default: 'WILSY_OS' },
    message: { type: String, trim: true, default: '' },
    evidenceHash: { type: String, trim: true, default: '' },
    createdAt: { type: Date, default: Date.now },
  },
  { _id: false }
);

const CrmRecordSchema = new Schema(
  {
    tenantId: { type: String, required: true, trim: true, index: true },
    type: { type: String, required: true, enum: CRM_RECORD_TYPES, index: true },

    externalId: { type: String, trim: true, default: '', index: true },
    sourceRecordId: { type: String, trim: true, default: '', index: true },
    sourceSystem: { type: String, trim: true, default: 'WILSY_OS', index: true },
    sourceModule: { type: String, trim: true, default: '' },
    sourcePosture: {
      type: String,
      enum: CRM_SOURCE_POSTURES,
      default: 'NOT_EVALUATED',
      index: true,
    },
    sourceEvidence: { type: EvidenceSourceSchema, default: () => ({}) },
    repairSignals: { type: [RepairSignalSchema], default: [] },

    recordOwner: { type: String, trim: true, default: '' },
    ownerId: { type: String, trim: true, default: '' },
    ownerName: { type: String, trim: true, default: '' },

    name: { type: String, trim: true, default: '' },
    displayName: { type: String, trim: true, default: '', index: true },
    salutation: { type: String, trim: true, default: '' },
    firstName: { type: String, trim: true, default: '' },
    lastName: { type: String, trim: true, default: '' },
    title: { type: String, trim: true, default: '' },
    department: { type: String, trim: true, default: '' },
    email: { type: String, trim: true, lowercase: true, default: '', index: true },
    secondaryEmail: { type: String, trim: true, lowercase: true, default: '' },
    phone: { type: String, trim: true, default: '' },
    mobile: { type: String, trim: true, default: '' },
    homePhone: { type: String, trim: true, default: '' },
    otherPhone: { type: String, trim: true, default: '' },
    fax: { type: String, trim: true, default: '' },
    status: { type: String, trim: true, default: 'NEW', index: true },
    score: { type: Number, min: 0, max: 100, default: null },
    leadSource: { type: String, trim: true, default: '' },
    lifecycleStage: { type: String, trim: true, default: '' },
    rating: { type: String, trim: true, default: '' },

    accountName: { type: String, trim: true, default: '', index: true },
    company: { type: String, trim: true, default: '', index: true },
    contactName: { type: String, trim: true, default: '' },
    accountSite: { type: String, trim: true, default: '' },
    accountNumber: { type: String, trim: true, default: '' },
    accountType: { type: String, trim: true, default: '' },
    parentAccount: { type: String, trim: true, default: '' },
    industry: { type: String, trim: true, default: '' },
    website: { type: String, trim: true, default: '' },
    companyDomainName: { type: String, trim: true, lowercase: true, default: '', index: true },
    tickerSymbol: { type: String, trim: true, default: '' },
    ownership: { type: String, trim: true, default: '' },
    employees: { type: Number, default: null },
    annualRevenue: { type: Number, default: null },

    legalIdentity: { type: LegalIdentitySchema, default: () => ({}) },
    authority: { type: AuthoritySchema, default: () => ({}) },
    contractLedger: { type: ContractLedgerSchema, default: () => ({}) },
    commercialTruth: { type: CommercialTruthSchema, default: () => ({}) },
    boardReadiness: { type: BoardReadinessSchema, default: () => ({}) },

    street: { type: String, trim: true, default: '' },
    city: { type: String, trim: true, default: '' },
    state: { type: String, trim: true, default: '' },
    province: { type: String, trim: true, default: '' },
    postalCode: { type: String, trim: true, default: '' },
    country: { type: String, trim: true, default: '' },

    stage: { type: String, trim: true, default: '' },
    pipeline: { type: String, trim: true, default: 'default' },
    typeLabel: { type: String, trim: true, default: '' },
    nextStep: { type: String, trim: true, default: '' },
    value: { type: Number, default: 0 },
    amount: { type: Number, default: 0 },
    expectedRevenue: { type: Number, default: 0 },
    probability: { type: Number, min: 0, max: 100, default: 0 },
    currency: { type: String, trim: true, default: 'ZAR' },
    closingDate: { type: Date, default: null },
    campaignSource: { type: String, trim: true, default: '' },

    dueDate: { type: Date, default: null },
    startsAt: { type: Date, default: null },
    endsAt: { type: Date, default: null },
    completedAt: { type: Date, default: null },
    priority: { type: String, trim: true, default: '' },
    subject: { type: String, trim: true, default: '' },
    description: { type: String, trim: true, default: '' },
    reminder: { type: Boolean, default: false },
    repeat: { type: Boolean, default: false },

    callType: { type: String, trim: true, default: '' },
    callPurpose: { type: String, trim: true, default: '' },
    callResult: { type: String, trim: true, default: '' },
    durationSeconds: { type: Number, default: 0 },

    fileName: { type: String, trim: true, default: '' },
    fileType: { type: String, trim: true, default: '' },
    fileUrl: { type: String, trim: true, default: '' },
    folder: { type: String, trim: true, default: 'Document Library' },
    fileSize: { type: Number, default: 0 },

    visitType: { type: String, trim: true, default: '' },
    location: { type: String, trim: true, default: '' },
    projectPhase: { type: String, trim: true, default: '' },
    percentComplete: { type: Number, min: 0, max: 100, default: 0 },

    associations: [
      {
        type: { type: String, trim: true },
        id: { type: String, trim: true },
        name: { type: String, trim: true },
        role: { type: String, trim: true },
        evidenceRole: { type: String, trim: true, default: '' },
      },
    ],
    tags: [{ type: String, trim: true }],

    sourceRegistryArtifactIds: [{ type: String, trim: true }],
    linkedArtifactIds: [{ type: String, trim: true }],
    linkedInvoiceIds: [{ type: String, trim: true }],
    linkedProjectIds: [{ type: String, trim: true }],
    linkedComplianceIds: [{ type: String, trim: true }],

    aiNarrative: {
      executiveSummary: { type: String, trim: true, default: '' },
      relationshipStory: { type: String, trim: true, default: '' },
      legalRiskStory: { type: String, trim: true, default: '' },
      nextBestAction: { type: String, trim: true, default: '' },
      lastGeneratedAt: { type: Date, default: null },
    },

    dataQuality: {
      completenessScore: { type: Number, min: 0, max: 100, default: 0 },
      duplicateRisk: { type: Number, min: 0, max: 100, default: 0 },
      staleRisk: { type: Number, min: 0, max: 100, default: 0 },
      lastTouchedAt: { type: Date, default: null },
      missingFields: [{ type: String, trim: true }],
    },

    auditTrail: { type: [AuditTrailSchema], default: [] },
    metadata: { type: Schema.Types.Mixed, default: {} },
    createdBy: { type: String, trim: true, default: '' },
    updatedBy: { type: String, trim: true, default: '' },
  },
  {
    timestamps: true,
    strict: false,
    minimize: false,
  }
);

/**
 * @function crmDisplayName
 * @description Returns the strongest human-readable CRM display name.
 * @returns {string} Display name.
 * @collaboration Lets every CRM record tell a board-readable story without inventing data.
 */
function crmDisplayName() {
  return (
    this.displayName ||
    this.name ||
    this.accountName ||
    this.company ||
    this.contactName ||
    this.email ||
    this.subject ||
    this.fileName ||
    this.externalId ||
    String(this._id || '')
  );
}

/**
 * @function crmLegalName
 * @description Returns the strongest legal/counterparty name for evidence linkage.
 * @returns {string} Legal or counterparty name.
 * @collaboration Turns CRM records into legal identity evidence candidates.
 */
function crmLegalName() {
  return (
    this.legalIdentity?.legalName ||
    this.contractLedger?.counterpartyLegalName ||
    this.accountName ||
    this.company ||
    this.name ||
    this.displayName ||
    ''
  );
}

/**
 * @function crmHasAuditableSource
 * @description Checks whether the record has minimum source identity metadata.
 * @returns {boolean} Whether source evidence can be audited.
 * @collaboration Prevents fake VERIFIED status by requiring source identity and retrieval metadata.
 */
function crmHasAuditableSource() {
  return Boolean(
    this.sourceEvidence?.sourceSystem &&
    this.sourceEvidence?.sourceRecordId &&
    this.sourceEvidence?.retrievedAt &&
    this.sourceEvidence?.evidenceHash
  );
}

/**
 * @function crmReadinessScore
 * @description Computes evidence readiness from source, authority, contract and quality signals.
 * @returns {number} Readiness score from 0 to 100.
 * @collaboration Makes CRM state board-readable while keeping VERIFIED strictly evidence-backed.
 */
function crmReadinessScore() {
  let score = 0;

  if (this.sourcePosture === 'VERIFIED' && this.hasAuditableSource()) score += 30;
  if (this.authority?.status === 'VERIFIED') score += 20;
  if (['SIGNED', 'ACTIVE', 'APPROVED'].includes(this.contractLedger?.status)) score += 20;
  if (this.legalIdentity?.legalName || this.company || this.accountName) score += 10;
  if (this.email || this.phone || this.website || this.companyDomainName) score += 10;
  if (!this.repairSignals?.length) score += 10;

  return Math.max(0, Math.min(100, score));
}

/**
 * @function crmAppendRepairSignal
 * @description Adds a repair signal if it is not already present.
 * @param {object} signal - Repair signal.
 * @returns {object} Current CRM record.
 * @collaboration Converts CRM gaps into executable repair work instead of silent data rot.
 */
function crmAppendRepairSignal(signal = {}) {
  const code = signal.code || 'CRM_EVIDENCE_GAP';
  const exists = (this.repairSignals || []).some(
    (item) => item.code === code && item.field === signal.field
  );

  if (!exists) {
    this.repairSignals.push({
      code,
      status: signal.status || 'MISSING',
      field: signal.field || '',
      message: signal.message || 'CRM evidence requires repair.',
      operatorAction: signal.operatorAction || 'Connect live CRM evidence before board reliance.',
      severity: signal.severity || 'MEDIUM',
    });
  }

  return this;
}

/**
 * @function crmToSourceRegistryEvidence
 * @description Projects a CRM record into Source Registry connector evidence.
 * @returns {object} Source Registry evidence projection.
 * @collaboration Links Wilsy CRM directly into Legal Artifact Studio, Source Registry and Boardroom Proof.
 */
function crmToSourceRegistryEvidence() {
  const sourceStatus = this.sourcePosture || 'NOT_EVALUATED';
  const legalName = this.legalName;
  const readinessScore = this.computeCrmReadinessScore();

  return {
    connector: 'CRM / Contract Ledger',
    recordId: String(this._id || ''),
    tenantId: this.tenantId,
    type: this.type,
    title: this.displayLabel,
    legalName,
    sourcePosture: sourceStatus,
    sourceSystem: this.sourceEvidence?.sourceSystem || this.sourceSystem || 'WILSY_OS',
    sourceRecordId:
      this.sourceEvidence?.sourceRecordId || this.sourceRecordId || this.externalId || '',
    retrievedAt: this.sourceEvidence?.retrievedAt || null,
    evidenceHash: this.sourceEvidence?.evidenceHash || '',
    authorityStatus: this.authority?.status || 'UNKNOWN',
    contractStatus: this.contractLedger?.status || 'NONE',
    agreementId: this.contractLedger?.agreementId || '',
    boardReadiness: this.boardReadiness?.status || 'NOT_READY',
    readinessScore,
    repairSignals: this.repairSignals || [],
    truthPolicy: WILSY_OS_CRM_TRUTH_POLICY,
  };
}

/**
 * @function crmPreValidateEvidencePosture
 * @description Normalizes CRM evidence posture before validation without fabricating verification.
 * @returns {void}
 * @collaboration Ensures every CRM record carries a live evidence posture before persistence.
 */
function crmPreValidateEvidencePosture() {
  this.displayName =
    this.displayName ||
    this.name ||
    this.accountName ||
    this.company ||
    this.contactName ||
    this.subject ||
    this.fileName ||
    '';
  this.sourceRecordId =
    this.sourceRecordId || this.externalId || this.sourceEvidence?.sourceRecordId || '';
  this.sourceEvidence = this.sourceEvidence || {};
  this.sourceEvidence.sourceSystem =
    this.sourceEvidence.sourceSystem || this.sourceSystem || 'WILSY_OS';
  this.sourceEvidence.sourceRecordId =
    this.sourceEvidence.sourceRecordId || this.sourceRecordId || '';

  this.legalIdentity = this.legalIdentity || {};
  this.legalIdentity.legalName =
    this.legalIdentity.legalName ||
    this.contractLedger?.counterpartyLegalName ||
    this.accountName ||
    this.company ||
    this.name ||
    '';

  this.contractLedger = this.contractLedger || {};
  this.contractLedger.counterpartyLegalName =
    this.contractLedger.counterpartyLegalName ||
    this.legalIdentity.legalName ||
    this.accountName ||
    this.company ||
    '';

  this.boardReadiness = this.boardReadiness || {};
  this.repairSignals = this.repairSignals || [];

  if (this.sourcePosture === 'VERIFIED' && !this.hasAuditableSource()) {
    this.sourcePosture = 'MISSING';
    this.appendRepairSignal({
      code: 'CRM_VERIFIED_WITHOUT_AUDITABLE_SOURCE',
      field: 'sourceEvidence',
      message:
        'CRM record attempted VERIFIED without sourceRecordId, retrievedAt and evidenceHash.',
      operatorAction: 'Attach auditable source evidence before VERIFIED posture is allowed.',
      severity: 'HIGH',
    });
  }

  if (!this.sourcePosture) {
    this.sourcePosture = 'NOT_EVALUATED';
  }

  this.boardReadiness.readinessScore = this.computeCrmReadinessScore();
  this.boardReadiness.sourcePosture = this.sourcePosture;
  this.boardReadiness.authorityPosture = this.authority?.status || 'UNKNOWN';
  this.boardReadiness.contractPosture = this.contractLedger?.status || 'NONE';
  this.boardReadiness.repairSignalCount = this.repairSignals.length;
  this.boardReadiness.lastAssessedAt = new Date();

  if (!this.boardReadiness.boardroomNarrative) {
    this.boardReadiness.boardroomNarrative =
      'CRM record is part of the Wilsy OS commercial truth layer. Board reliance requires source, authority, contract and compliance evidence.';
  }

  return undefined;
}

/**
 * @function crmFindForSourceRegistry
 * @description Finds CRM records that can support Source Registry verification.
 * @param {object} options - Lookup options.
 * @returns {Promise<Array<object>>} CRM records.
 * @collaboration Lets Source Registry resolve evidence from the Wilsy CRM spine.
 */
async function crmFindForSourceRegistry(options = {}) {
  const query = {
    tenantId: options.tenantId || 'MASTER',
  };

  const or = [];

  if (options.type) query.type = options.type;
  if (options.sourcePosture) query.sourcePosture = options.sourcePosture;
  if (options.agreementId) or.push({ 'contractLedger.agreementId': options.agreementId });
  if (options.artifactId) or.push({ 'contractLedger.artifactId': options.artifactId });
  if (options.counterpartyLegalName) {
    const safe = String(options.counterpartyLegalName).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    or.push({ 'contractLedger.counterpartyLegalName': new RegExp(safe, 'i') });
    or.push({ 'legalIdentity.legalName': new RegExp(safe, 'i') });
    or.push({ company: new RegExp(safe, 'i') });
    or.push({ accountName: new RegExp(safe, 'i') });
  }

  if (or.length) query.$or = or;

  return this.find(query)
    .sort({ updatedAt: -1, createdAt: -1 })
    .limit(options.limit || 50)
    .lean();
}

CrmRecordSchema.virtual('displayLabel').get(crmDisplayName);
CrmRecordSchema.virtual('legalName').get(crmLegalName);

CrmRecordSchema.methods.hasAuditableSource = crmHasAuditableSource;
CrmRecordSchema.methods.computeCrmReadinessScore = crmReadinessScore;
CrmRecordSchema.methods.appendRepairSignal = crmAppendRepairSignal;
CrmRecordSchema.methods.toSourceRegistryEvidence = crmToSourceRegistryEvidence;

CrmRecordSchema.statics.findForSourceRegistry = crmFindForSourceRegistry;

CrmRecordSchema.pre('validate', crmPreValidateEvidencePosture);

CrmRecordSchema.index({ tenantId: 1, type: 1, createdAt: -1 });
CrmRecordSchema.index({ tenantId: 1, type: 1, stage: 1 });
CrmRecordSchema.index({ tenantId: 1, type: 1, status: 1 });
CrmRecordSchema.index({ tenantId: 1, type: 1, email: 1 });
CrmRecordSchema.index({ tenantId: 1, type: 1, companyDomainName: 1 });
CrmRecordSchema.index({ tenantId: 1, type: 1, externalId: 1 });
CrmRecordSchema.index({ tenantId: 1, type: 1, sourcePosture: 1 });
CrmRecordSchema.index({ tenantId: 1, type: 1, 'authority.status': 1 });
CrmRecordSchema.index({ tenantId: 1, type: 1, 'contractLedger.status': 1 });
CrmRecordSchema.index({ tenantId: 1, 'contractLedger.agreementId': 1 });
CrmRecordSchema.index({ tenantId: 1, 'contractLedger.artifactId': 1 });
CrmRecordSchema.index({ tenantId: 1, 'legalIdentity.legalName': 1 });
CrmRecordSchema.index({ tenantId: 1, 'boardReadiness.status': 1 });
CrmRecordSchema.index({ tenantId: 1, 'boardReadiness.riskLevel': 1 });
CrmRecordSchema.index({ tenantId: 1, sourceSystem: 1, sourceRecordId: 1 });
CrmRecordSchema.index({
  name: 'text',
  displayName: 'text',
  email: 'text',
  phone: 'text',
  accountName: 'text',
  company: 'text',
  status: 'text',
  stage: 'text',
  industry: 'text',
  companyDomainName: 'text',
  title: 'text',
  subject: 'text',
  description: 'text',
  fileName: 'text',
  folder: 'text',
  'legalIdentity.legalName': 'text',
  'contractLedger.counterpartyLegalName': 'text',
  'contractLedger.agreementId': 'text',
  'authority.authorizedSignatoryName': 'text',
  'aiNarrative.executiveSummary': 'text',
  'aiNarrative.relationshipStory': 'text',
});

export default mongoose.models.CrmRecord || mongoose.model('CrmRecord', CrmRecordSchema);
