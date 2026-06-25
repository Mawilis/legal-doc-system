/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - CRM INTELLIGENCE MODELS                                                                                     ║
 * ║ TELEMETRY | COMPLIANCE RECEIPTS | GOVERNANCE CUSTODY | REVENUE LEDGER | PREDICTIVE SCORES                              ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * @fileoverview Sovereign CRM intelligence Mongoose models.
 */

import {
  Schema,
  buildCrmAuditTrailSchema,
  buildCrmEvidenceSchema,
  buildCrmSchemaOptions,
  buildCrmTenantFields,
  getOrCreateModel,
} from './wilsyCrmBaseSchemas.js';

/**
 * @function buildComplianceReceiptSchema
 * @description Builds clause-bound CRM compliance receipt schema.
 * @returns {Schema} Mongoose schema.
 * @collaboration Binds POPIA, GDPR, SOC2 and governance clauses directly to CRM records.
 */
function buildComplianceReceiptSchema() {
  const schema = new Schema(
    {
      ...buildCrmTenantFields(),
      recordType: { type: String, trim: true, index: true, required: true },
      recordId: { type: String, trim: true, index: true, required: true },
      clause: { type: String, trim: true, index: true, required: true },
      jurisdiction: { type: String, trim: true, index: true, default: 'ZA' },
      controlId: { type: String, trim: true, index: true, default: null },
      hash: { type: String, trim: true, index: true, required: true },
      rootHash: { type: String, trim: true, index: true, default: null },
      sealed: { type: Boolean, index: true, default: false },
      sealedAt: { type: Date, default: null },
      evidence: [buildCrmEvidenceSchema()],
      payloadSnapshot: { type: Schema.Types.Mixed, default: {} },
      auditTrail: [buildCrmAuditTrailSchema()],
    },
    buildCrmSchemaOptions('crm_compliance_receipts')
  );

  schema.index({ tenantId: 1, recordType: 1, recordId: 1, clause: 1 });
  schema.index({ tenantId: 1, sealed: 1, updatedAt: -1 });

  return schema;
}

/**
 * @function buildTelemetryEventSchema
 * @description Builds real-time CRM telemetry event schema.
 * @returns {Schema} Mongoose schema.
 * @collaboration Captures live CRM operating events without faking sales records.
 */
function buildTelemetryEventSchema() {
  const schema = new Schema(
    {
      ...buildCrmTenantFields(),
      type: { type: String, trim: true, index: true, required: true },
      severity: { type: String, trim: true, index: true, default: 'INFO' },
      entityType: { type: String, trim: true, index: true, default: null },
      entityId: { type: String, trim: true, index: true, default: null },
      route: { type: String, trim: true, default: null },
      payload: { type: Schema.Types.Mixed, default: {} },
      receiptHash: { type: String, trim: true, index: true, default: null },
      rootHash: { type: String, trim: true, index: true, default: null },
      emittedAt: { type: Date, index: true, default: Date.now },
      auditTrail: [buildCrmAuditTrailSchema()],
    },
    buildCrmSchemaOptions('crm_telemetry_events')
  );

  schema.index({ tenantId: 1, type: 1, emittedAt: -1 });
  schema.index({ tenantId: 1, entityType: 1, entityId: 1 });

  return schema;
}

/**
 * @function buildGovernanceEventSchema
 * @description Builds CRM chain-of-custody governance event schema.
 * @returns {Schema} Mongoose schema.
 * @collaboration Tracks record movement, proof movement and contract custody with hash continuity.
 */
function buildGovernanceEventSchema() {
  const schema = new Schema(
    {
      ...buildCrmTenantFields(),
      chainId: { type: String, trim: true, index: true, required: true },
      sequence: { type: Number, min: 0, index: true, default: 0 },
      custodyType: { type: String, trim: true, index: true, required: true },
      entityType: { type: String, trim: true, index: true, required: true },
      entityId: { type: String, trim: true, index: true, required: true },
      fromActor: { type: String, trim: true, default: null },
      toActor: { type: String, trim: true, default: null },
      previousHash: { type: String, trim: true, index: true, default: null },
      eventHash: { type: String, trim: true, index: true, required: true },
      rootHash: { type: String, trim: true, index: true, default: null },
      payload: { type: Schema.Types.Mixed, default: {} },
      recordedAt: { type: Date, index: true, default: Date.now },
      auditTrail: [buildCrmAuditTrailSchema()],
    },
    buildCrmSchemaOptions('crm_governance_events')
  );

  schema.index({ tenantId: 1, chainId: 1, sequence: 1 });
  schema.index({ tenantId: 1, entityType: 1, entityId: 1 });

  return schema;
}

/**
 * @function buildRevenueLedgerSchema
 * @description Builds CRM revenue ledger schema for deal/account revenue intelligence.
 * @returns {Schema} Mongoose schema.
 * @collaboration Adds IFRS-aware ledger posture without inventing invoices or payments.
 */
function buildRevenueLedgerSchema() {
  const schema = new Schema(
    {
      ...buildCrmTenantFields(),
      dealId: { type: Schema.Types.ObjectId, ref: 'CRMDeal', index: true, default: null },
      accountId: { type: Schema.Types.ObjectId, ref: 'CRMAccount', index: true, default: null },
      ledgerType: { type: String, trim: true, index: true, default: 'PIPELINE' },
      amount: { type: Number, min: 0, default: 0 },
      currency: { type: String, trim: true, uppercase: true, default: 'ZAR' },
      status: { type: String, trim: true, index: true, default: 'PENDING' },
      ifrsCode: { type: String, trim: true, index: true, default: null },
      recognizedAt: { type: Date, index: true, default: null },
      receiptHash: { type: String, trim: true, index: true, default: null },
      rootHash: { type: String, trim: true, index: true, default: null },
      evidence: [buildCrmEvidenceSchema()],
      auditTrail: [buildCrmAuditTrailSchema()],
    },
    buildCrmSchemaOptions('crm_revenue_ledger')
  );

  schema.index({ tenantId: 1, status: 1, recognizedAt: -1 });
  schema.index({ tenantId: 1, ledgerType: 1 });

  return schema;
}

/**
 * @function buildPredictiveScoreSchema
 * @description Builds CRM predictive scoring schema.
 * @returns {Schema} Mongoose schema.
 * @collaboration Stores model outputs, confidence and input signals for auditability.
 */
function buildPredictiveScoreSchema() {
  const schema = new Schema(
    {
      ...buildCrmTenantFields(),
      entityType: { type: String, trim: true, index: true, required: true },
      entityId: { type: String, trim: true, index: true, required: true },
      modelKey: { type: String, trim: true, index: true, required: true },
      modelVersion: { type: String, trim: true, default: 'v1' },
      score: { type: Number, min: 0, max: 100, index: true, default: 0 },
      confidence: { type: Number, min: 0, max: 100, default: 0 },
      signals: { type: Schema.Types.Mixed, default: {} },
      explanation: { type: String, trim: true, default: null },
      receiptHash: { type: String, trim: true, index: true, default: null },
      scoredAt: { type: Date, index: true, default: Date.now },
      auditTrail: [buildCrmAuditTrailSchema()],
    },
    buildCrmSchemaOptions('crm_predictive_scores')
  );

  schema.index({ tenantId: 1, entityType: 1, entityId: 1, modelKey: 1 });
  schema.index({ tenantId: 1, score: -1 });

  return schema;
}

const CRMComplianceReceipt = getOrCreateModel(
  'CRMComplianceReceipt',
  buildComplianceReceiptSchema()
);
const CRMTelemetryEvent = getOrCreateModel('CRMTelemetryEvent', buildTelemetryEventSchema());
const CRMGovernanceEvent = getOrCreateModel('CRMGovernanceEvent', buildGovernanceEventSchema());
const CRMRevenueLedger = getOrCreateModel('CRMRevenueLedger', buildRevenueLedgerSchema());
const CRMPredictiveScore = getOrCreateModel('CRMPredictiveScore', buildPredictiveScoreSchema());

/**
 * @function registerWilsyCrmIntelligenceModels
 * @description Registers and returns all sovereign CRM intelligence models.
 * @returns {Object} Registered intelligence models.
 * @collaboration Makes telemetry, compliance, governance, revenue and scoring discoverable to services.
 */
function registerWilsyCrmIntelligenceModels() {
  return {
    CRMComplianceReceipt,
    CRMTelemetryEvent,
    CRMGovernanceEvent,
    CRMRevenueLedger,
    CRMPredictiveScore,
  };
}

export {
  CRMComplianceReceipt,
  CRMGovernanceEvent,
  CRMPredictiveScore,
  CRMRevenueLedger,
  CRMTelemetryEvent,
  buildComplianceReceiptSchema,
  buildGovernanceEventSchema,
  buildPredictiveScoreSchema,
  buildRevenueLedgerSchema,
  buildTelemetryEventSchema,
  registerWilsyCrmIntelligenceModels,
};

export default registerWilsyCrmIntelligenceModels;
