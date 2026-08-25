/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN ACCESS GATEWAY [v34.2.0-HASH-ALIGNED]                                                                          ║
 * ║ REVENUE-LINKED · SHA3-512 ONE-WAY HASH · KEY PREFIX · TRACE-ANCHORED · NO PLAINTEXT AT REST                                         ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 34.2.0-HASH-ALIGNED | PRODUCTION READY                                                                                     ║
 * ║ EPITOME: API keys stored as SHA3-512 hashes only. Raw secret returned once at provision (OnboardingService).                         ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/api/ApiKey.js                                                    ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ ALIGNMENT: OnboardingService v34.1 hashApiKey() uses sha3-512 — verifyKey MUST use the same algorithm.                              ║
 * ║ COMPLIANCE: POPIA §19 · GDPR §32 · SOC2 §CC6/CC7 · ISO 27001                                                                        ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */
import mongoose from 'mongoose';
import crypto from 'node:crypto';

const { Schema } = mongoose;

let broadcastTelemetry = async () => { };
try {
  const tel = await import('../../utils/telemetryHelper.js');
  if (typeof tel.broadcastTelemetry === 'function') {
    broadcastTelemetry = tel.broadcastTelemetry;
  }
} catch {
  /* optional */
}

/**
 * Canonical API key hash — MUST match OnboardingService.hashApiKey
 * @param {string} rawKey
 * @returns {string} hex sha3-512
 */
export function hashApiKeySecret(rawKey) {
  return crypto.createHash('sha3-512').update(String(rawKey || '')).digest('hex');
}

const API_KEY_TIERS = Object.freeze([
  'BASIC',
  'STANDARD',
  'PROFESSIONAL',
  'ENTERPRISE',
  'SOVEREIGN',
]);

const ApiKeySchema = new Schema(
  {
    keyId: {
      type: String,
      required: true,
      unique: true,
      index: true,
      default: () => `WOS-KEY-${crypto.randomBytes(4).toString('hex').toUpperCase()}`,
    },

    /** SHA3-512 of raw key — never store plaintext */
    keyHash: {
      type: String,
      required: true,
      unique: true,
      index: true,
      select: false,
    },

    /** First 12 chars of raw key for UI / Merkle leaves (not secret alone) */
    keyPrefix: {
      type: String,
      required: false,
      index: true,
      trim: true,
    },

    hint: {
      type: String,
      required: false,
      default: function hintDefault() {
        return this.keyPrefix
          ? `${this.keyPrefix.slice(0, 4)}...${this.keyPrefix.slice(-4)}`
          : 'WOS****';
      },
    },

    createdTraceId: {
      type: String,
      required: false,
      index: true,
      trim: true,
    },

    tenantId: {
      type: Schema.Types.ObjectId,
      ref: 'Tenant',
      required: true,
      index: true,
    },

    name: {
      type: String,
      required: true,
      default: 'Master Revenue Key',
      trim: true,
    },

    tier: {
      type: String,
      required: true,
      enum: API_KEY_TIERS,
      default: 'BASIC',
      index: true,
      uppercase: true,
      trim: true,
    },

    scopes: {
      type: [String],
      enum: ['CORE_READ', 'CORE_WRITE', 'FORENSIC_ADMIN', 'REVENUE_AUDIT', 'BILLING_WRITE'],
      default: ['CORE_READ'],
    },

    isActive: {
      type: Boolean,
      default: true,
      index: true,
    },

    lastUsed: Date,
    expiresAt: Date,

    forensicChain: [
      {
        traceId: { type: String, index: true },
        timestamp: { type: Date, default: Date.now },
        action: { type: String, required: true },
        performer: { type: String, default: 'SYSTEM_GENESIS' },
        seal: { type: String },
      },
    ],
  },
  {
    timestamps: true,
    collection: 'api_keys',
  }
);

ApiKeySchema.index({ tenantId: 1, isActive: 1 });
ApiKeySchema.index({ keyHash: 1, isActive: 1 });

/**
 * Strip any accidental plaintext `key` field before persist.
 * Async pre-save — no next().
 */
ApiKeySchema.pre('save', async function apiKeyPreSave() {
  if (Object.prototype.hasOwnProperty.call(this, 'key')) {
    this.set('key', undefined);
  }
  if (this.isNew) {
    if (!this.hint && this.keyPrefix) {
      this.hint = `${this.keyPrefix.slice(0, 4)}...${this.keyPrefix.slice(-4)}`;
    }
    if (!this.hint) {
      this.hint = `WOS-${crypto.randomBytes(3).toString('hex').toUpperCase()}`;
    }
    try {
      await broadcastTelemetry(
        this.tenantId?.toString?.() || 'UNKNOWN',
        'API_KEY_PROVISIONED',
        'SYSTEM',
        'GENESIS',
        {
          keyId: this.keyId,
          tier: this.tier,
          keyPrefix: this.keyPrefix || null,
          traceId: this.createdTraceId || 'SYSTEM_GENESIS',
        }
      );
    } catch {
      /* non-blocking */
    }
  }
});

/**
 * Validate raw key against SHA3-512 hash (aligned with OnboardingService).
 * @param {string} rawKey
 * @returns {Promise<import('mongoose').Document|null>}
 */
ApiKeySchema.statics.verifyKey = async function verifyKey(rawKey) {
  if (!rawKey || typeof rawKey !== 'string') return null;
  const hash = hashApiKeySecret(rawKey);
  const keyDoc = await this.findOne({ keyHash: hash, isActive: true }).select('+keyHash');
  if (!keyDoc) return null;
  keyDoc.lastUsed = new Date();
  await keyDoc.save();
  return keyDoc;
};

/**
 * @param {string} traceId
 * @param {string} performer
 * @returns {Promise<import('mongoose').Document>}
 */
ApiKeySchema.methods.revokeKey = async function revokeKey(traceId, performer) {
  this.isActive = false;
  this.forensicChain.push({
    traceId,
    action: 'KEY_REVOKED',
    performer,
    timestamp: new Date(),
  });
  try {
    await broadcastTelemetry(
      this.tenantId?.toString?.() || 'UNKNOWN',
      'API_KEY_REVOKED',
      performer,
      'SECURITY_ACTION',
      { traceId, keyId: this.keyId }
    );
  } catch {
    /* non-blocking */
  }
  return this.save();
};

export const ApiKey = mongoose.models.ApiKey || mongoose.model('ApiKey', ApiKeySchema);
export default ApiKey;
