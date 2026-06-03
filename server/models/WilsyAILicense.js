/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - WILSY AI LICENSE MODEL [V1.0.0-CROSS-TENANT-ENTITLEMENT]                                                                  ║
 * ║ [TENANT-SCOPED AI ENTITLEMENTS | SHA3 LICENSE SEALS | MODULE ACTIVATION RECEIPTS | MONETISABLE ADD-ON GOVERNANCE]                    ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-CROSS-TENANT-ENTITLEMENT | PRODUCTION READY | WILSY AI LICENSING STATE                                                 ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/WilsyAILicense.js                                                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Mandated Wilsy AI as a licensable tenant add-on service, not a prototype widget.                    ║
 * ║ • AI Engineering (Codex) - ARCHITECTED: Persisted tenant-scoped Wilsy AI entitlements with cryptographic seals and audit receipts.     ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import crypto from 'node:crypto';

const { Schema } = mongoose;

/**
 * @function stableWilsyAIStringify
 * @description Serializes license proof payloads with deterministic object key ordering.
 * @param {unknown} value - Candidate payload.
 * @returns {string} Stable JSON string.
 * @collaboration License seals must replay to the same hash across tenants, requests and investor diligence exports.
 */
const stableWilsyAIStringify = (value) => {
  if (typeof value === 'undefined') return 'null';
  if (value instanceof Date) return JSON.stringify(value.toISOString());
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(item => stableWilsyAIStringify(item)).join(',')}]`;
  return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${stableWilsyAIStringify(value[key])}`).join(',')}}`;
};

/**
 * @function createWilsyAILicenseHash
 * @description Creates a SHA3-512 proof hash for a Wilsy AI license payload.
 * @param {Object} payload - License payload.
 * @returns {string} Uppercase SHA3-512 digest.
 * @collaboration Every Wilsy AI activation becomes a tamper-evident monetisation receipt.
 */
export const createWilsyAILicenseHash = (payload = {}) => (
  crypto.createHash('sha3-512').update(stableWilsyAIStringify(payload)).digest('hex').toUpperCase()
);

/**
 * @constant {mongoose.Schema}
 * @description Tenant-scoped Wilsy AI license state.
 * @collaboration Supports licensing Wilsy AI across bakeries, importers, construction firms and enterprise tenants without new code files.
 */
const wilsyAILicenseSchema = new Schema({
  licenseId: {
    type: String,
    required: true,
    unique: true,
    index: true
  },
  tenantId: {
    type: String,
    required: true,
    index: true,
    uppercase: true,
    trim: true
  },
  moduleId: {
    type: String,
    required: true,
    index: true,
    trim: true
  },
  moduleName: {
    type: String,
    required: true,
    trim: true
  },
  tier: {
    type: String,
    enum: ['WILSY_AI_STARTER', 'WILSY_AI_GROWTH', 'WILSY_AI_INSTITUTIONAL'],
    required: true,
    index: true
  },
  status: {
    type: String,
    enum: ['PENDING_SOURCE', 'ACTIVE', 'SUSPENDED', 'REVOKED'],
    default: 'PENDING_SOURCE',
    index: true
  },
  businessProfile: {
    industryKey: String,
    industryLabel: String,
    sourceStatus: String,
    sourceEvidence: String
  },
  dailyDutyKey: String,
  lane: String,
  commercials: {
    currency: { type: String, default: 'ZAR' },
    monthlyPrice: { type: Number, default: 0 },
    setupPrice: { type: Number, default: 0 },
    overagePricePerRequest: { type: Number, default: 0 },
    vatRate: { type: Number, default: 0.15 },
    billingModel: { type: String, default: 'MONTHLY_ADD_ON' },
    valuePromise: String
  },
  requestPolicy: {
    dailyRequestLimit: { type: Number, default: 0 },
    monthlyAutomationLimit: { type: Number, default: 0 },
    analystSeats: { type: Number, default: 1 },
    maxAutonomousActionsPerDay: { type: Number, default: 0 },
    approvalRequiredAboveValue: { type: Number, default: 0 },
    currency: { type: String, default: 'ZAR' }
  },
  usageSnapshot: {
    dailyRequestsUsed: { type: Number, default: 0 },
    monthlyRequestsUsed: { type: Number, default: 0 },
    estimatedMinutesSaved: { type: Number, default: 0 },
    estimatedValueZar: { type: Number, default: 0 },
    roiMultiple: { type: Number, default: 0 },
    sourceStatus: { type: String, default: 'USAGE_LEDGER_NOT_SYNCED' },
    lastSync: Date
  },
  sourceRequirements: [{ type: String }],
  entitlements: [{ type: String }],
  activation: {
    mode: { type: String, default: 'EXECUTIVE_COMMAND' },
    activatedBy: String,
    activatedAt: Date,
    revokedBy: String,
    revokedAt: Date,
    reason: String
  },
  proof: {
    algorithm: { type: String, default: 'SHA3-512' },
    canonicalization: { type: String, default: 'STABLE_JSON_KEY_SORT' },
    hash: { type: String, index: true },
    canonicalPayload: String
  },
  receipts: [{
    eventType: String,
    status: String,
    actor: String,
    traceId: String,
    timestamp: { type: Date, default: Date.now },
    proofHash: String
  }]
}, {
  timestamps: true
});

wilsyAILicenseSchema.index({ tenantId: 1, moduleId: 1 }, { unique: true });
wilsyAILicenseSchema.index({ tenantId: 1, status: 1, tier: 1 });

/**
 * @method sealLicense
 * @description Rebuilds the cryptographic proof for the current license document.
 * @returns {void}
 * @collaboration Keeps license state tamper-evident after activation, suspension or revocation.
 */
wilsyAILicenseSchema.methods.sealLicense = function sealLicense() {
  const payload = {
    licenseId: this.licenseId,
    tenantId: this.tenantId,
    moduleId: this.moduleId,
    moduleName: this.moduleName,
    tier: this.tier,
    status: this.status,
    businessProfile: this.businessProfile,
    dailyDutyKey: this.dailyDutyKey,
    lane: this.lane,
    commercials: this.commercials,
    requestPolicy: this.requestPolicy,
    usageSnapshot: this.usageSnapshot,
    sourceRequirements: this.sourceRequirements,
    entitlements: this.entitlements,
    activation: this.activation
  };
  this.proof = {
    algorithm: 'SHA3-512',
    canonicalization: 'STABLE_JSON_KEY_SORT',
    hash: createWilsyAILicenseHash(payload),
    canonicalPayload: stableWilsyAIStringify(payload)
  };
};

/**
 * @hook preValidate
 * @description Assigns missing license IDs and proof hashes before persistence.
 * @returns {void}
 * @collaboration License creation must be deterministic enough for audit and flexible enough for any tenant type.
 */
wilsyAILicenseSchema.pre('validate', function preValidateWilsyAILicense(next) {
  if (!this.licenseId) {
    const suffix = crypto.randomBytes(5).toString('hex').toUpperCase();
    this.licenseId = `WILSY-AI-${String(this.tenantId || 'TENANT').toUpperCase()}-${suffix}`;
  }
  this.sealLicense();
  next();
});

const WilsyAILicense = mongoose.models.WilsyAILicense || mongoose.model('WilsyAILicense', wilsyAILicenseSchema);

export default WilsyAILicense;
