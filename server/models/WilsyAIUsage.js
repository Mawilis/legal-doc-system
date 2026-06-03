/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - WILSY AI USAGE LEDGER [V1.0.0-REQUEST-ECONOMICS]                                                                           ║
 * ║ [TENANT-SCOPED AI REQUESTS | DAILY QUOTAS | ROI ANALYTICS | ZAR BILLING VALUE | SHA3 USAGE RECEIPTS]                                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-REQUEST-ECONOMICS | PRODUCTION READY | WILSY AI MONETISATION ANALYTICS LEDGER                                         ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/WilsyAIUsage.js                                                    ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Required Wilsy AI to justify tenant add-on fees through daily request and value analytics.          ║
 * ║ • AI Engineering (Codex) - ARCHITECTED: Added a tenant-isolated AI usage ledger with quota, ZAR value and proof receipts.             ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import crypto from 'node:crypto';

const { Schema } = mongoose;

/**
 * @function stableWilsyAIUsageStringify
 * @description Serializes Wilsy AI usage receipts with deterministic object key ordering.
 * @param {unknown} value - Candidate value.
 * @returns {string} Stable JSON string.
 * @collaboration AI usage becomes billable evidence, so its proof hash must replay exactly.
 */
const stableWilsyAIUsageStringify = (value) => {
  if (typeof value === 'undefined') return 'null';
  if (value instanceof Date) return JSON.stringify(value.toISOString());
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(item => stableWilsyAIUsageStringify(item)).join(',')}]`;
  return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${stableWilsyAIUsageStringify(value[key])}`).join(',')}}`;
};

/**
 * @function createWilsyAIUsageHash
 * @description Creates a SHA3-512 digest for a usage ledger payload.
 * @param {Object} payload - Usage payload.
 * @returns {string} Uppercase digest.
 * @collaboration Tenant usage analytics must be tamper-evident before they become invoices or investor metrics.
 */
export const createWilsyAIUsageHash = (payload = {}) => crypto
  .createHash('sha3-512')
  .update(stableWilsyAIUsageStringify(payload))
  .digest('hex')
  .toUpperCase();

/**
 * @constant {mongoose.Schema}
 * @description Tenant-scoped Wilsy AI request usage ledger.
 * @collaboration This ledger answers why a tenant pays extra: requests, time saved, value generated and quota posture.
 */
const wilsyAIUsageSchema = new Schema({
  usageId: {
    type: String,
    required: true,
    unique: true,
    index: true
  },
  tenantId: {
    type: String,
    required: true,
    uppercase: true,
    trim: true,
    index: true
  },
  licenseId: {
    type: String,
    trim: true,
    index: true
  },
  moduleId: {
    type: String,
    required: true,
    trim: true,
    index: true
  },
  tier: {
    type: String,
    enum: ['WILSY_AI_STARTER', 'WILSY_AI_GROWTH', 'WILSY_AI_INSTITUTIONAL'],
    required: true,
    index: true
  },
  requestType: {
    type: String,
    enum: [
      'INBOX_TRIAGE',
      'CASH_GAP_ANALYSIS',
      'STOCK_SUPPLY_CHECK',
      'COMPLIANCE_SENTINEL',
      'INDUSTRY_COMMAND',
      'DOCUMENT_CAPTURE',
      'CUSTOM_EXECUTIVE_TASK'
    ],
    default: 'CUSTOM_EXECUTIVE_TASK',
    index: true
  },
  status: {
    type: String,
    enum: ['PLANNED', 'EXECUTED', 'BLOCKED_BY_SOURCE', 'BLOCKED_BY_QUOTA', 'FAILED'],
    default: 'PLANNED',
    index: true
  },
  actor: {
    userId: String,
    email: String,
    role: String
  },
  metering: {
    requestUnits: { type: Number, default: 1, min: 0 },
    inputTokens: { type: Number, default: 0, min: 0 },
    outputTokens: { type: Number, default: 0, min: 0 },
    automationActions: { type: Number, default: 0, min: 0 }
  },
  valueMetrics: {
    estimatedMinutesSaved: { type: Number, default: 0, min: 0 },
    estimatedValueZar: { type: Number, default: 0, min: 0 },
    avoidedRiskZar: { type: Number, default: 0, min: 0 },
    roiMultiple: { type: Number, default: 0, min: 0 }
  },
  billing: {
    currency: { type: String, default: 'ZAR' },
    includedInPlan: { type: Boolean, default: true },
    overageCharge: { type: Number, default: 0, min: 0 },
    invoiceId: String
  },
  source: {
    sourceStatus: { type: String, default: 'REQUEST_CONTEXT' },
    sourceEvidence: String,
    sourceSnapshotHash: String
  },
  proof: {
    algorithm: { type: String, default: 'SHA3-512' },
    canonicalization: { type: String, default: 'STABLE_JSON_KEY_SORT' },
    hash: { type: String, index: true },
    canonicalPayload: String
  }
}, {
  timestamps: true
});

wilsyAIUsageSchema.index({ tenantId: 1, createdAt: -1 });
wilsyAIUsageSchema.index({ tenantId: 1, moduleId: 1, createdAt: -1 });
wilsyAIUsageSchema.index({ tenantId: 1, tier: 1, status: 1 });

/**
 * @method sealUsage
 * @description Rebuilds the proof hash for the current usage row.
 * @returns {void}
 * @collaboration Keeps each AI request row evidence-ready for quota disputes and add-on billing.
 */
wilsyAIUsageSchema.methods.sealUsage = function sealUsage() {
  const payload = {
    usageId: this.usageId,
    tenantId: this.tenantId,
    licenseId: this.licenseId,
    moduleId: this.moduleId,
    tier: this.tier,
    requestType: this.requestType,
    status: this.status,
    actor: this.actor,
    metering: this.metering,
    valueMetrics: this.valueMetrics,
    billing: this.billing,
    source: this.source
  };
  this.proof = {
    algorithm: 'SHA3-512',
    canonicalization: 'STABLE_JSON_KEY_SORT',
    hash: createWilsyAIUsageHash(payload),
    canonicalPayload: stableWilsyAIUsageStringify(payload)
  };
};

/**
 * @hook preValidate
 * @description Assigns missing usage ids and seals every usage row before persistence.
 * @returns {void}
 * @collaboration Usage can be recorded by many tenant workflows, but every row must share one proof standard.
 */
wilsyAIUsageSchema.pre('validate', function preValidateWilsyAIUsage(next) {
  if (!this.usageId) {
    this.usageId = `WAI-USE-${String(this.tenantId || 'TENANT').toUpperCase()}-${crypto.randomBytes(5).toString('hex').toUpperCase()}`;
  }
  this.sealUsage();
  next();
});

const WilsyAIUsage = mongoose.models.WilsyAIUsage || mongoose.model('WilsyAIUsage', wilsyAIUsageSchema);

export default WilsyAIUsage;
