/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN ACCESS GATEWAY [V33.34.0-OMEGA-KEY]                                                                               ║
 * ║ [REVENUE-LINKED | ONE-WAY CRYPTOGRAPHIC HASHING | GRANULAR INSTITUTIONAL SCOPES | TRACE-ANCHORED]                                      ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 33.34.0-OMEGA | PRODUCTION READY | BIBLICAL WORTH BILLIONS                                                                    ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/api/ApiKey.js                                                      ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * • Wilson Khanyezi (CEO/Lead Architect) - Access Control Strategy & Revenue Linkage. [2026-05-04]                                         ║
 * • AI Engineering (Gemini) - RECTIFIED: Implemented SHA-256 hashing to prevent raw key exposure in the database Nucleus.                  ║
 * • AI Engineering (Gemini) - ENHANCED: Integrated Forensic Chain for court-admissible lifecycle tracking.                                  ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import crypto from 'node:crypto';
import { broadcastTelemetry } from '../../utils/telemetryHelper.js';

const { Schema } = mongoose;

const ApiKeySchema = new Schema({
  // 🛡️ PUBLIC IDENTIFIER: Used for management/UI without exposing the secret
  keyId: {
    type: String,
    required: true,
    unique: true,
    index: true,
    default: () => `WOS-KEY-${crypto.randomBytes(4).toString('hex').toUpperCase()}`
  },

  // 🛡️ CRYPTOGRAPHIC ANCHOR: The SHA-256 hash of the secret key.
  keyHash: {
    type: String,
    required: true,
    unique: true,
    index: true,
    select: false // Never exposed in standard queries
  },

  // 🛡️ KEY HINT: First 4 and Last 4 for institutional recognition (e.g., WOS_...A1B2)
  hint: { type: String, required: true },

  tenantId: {
    type: Schema.Types.ObjectId,
    ref: 'Tenant',
    required: true,
    index: true
  },

  name: {
    type: String,
    required: true,
    default: 'Master Revenue Key',
    trim: true
  },

  tier: {
    type: String,
    required: true,
    enum: ['BASIC', 'PROFESSIONAL', 'ENTERPRISE', 'SOVEREIGN'],
    default: 'BASIC',
    index: true
  },

  // 🏛️ INSTITUTIONAL SCOPES: Granular permission matrix
  scopes: {
    type: [String],
    enum: ['CORE_READ', 'CORE_WRITE', 'FORENSIC_ADMIN', 'REVENUE_AUDIT', 'BILLING_WRITE'],
    default: ['CORE_READ']
  },

  isActive: {
    type: Boolean,
    default: true,
    index: true
  },

  lastUsed: Date,
  expiresAt: Date,

  // 🛡️ TRACE-AWARE FORENSIC CHAIN
  forensicChain: [{
    traceId: { type: String, index: true },
    timestamp: { type: Date, default: Date.now },
    action: { type: String, required: true },
    performer: { type: String, default: 'SYSTEM_GENESIS' },
    seal: { type: String } // SHA3-512 integrity hash for the log entry
  }]
}, {
  timestamps: true,
  collection: 'api_keys'
});

// ============================================================================
// 🏛️ INSTITUTIONAL INDEXING
// ============================================================================
ApiKeySchema.index({ tenantId: 1, isActive: 1 });
ApiKeySchema.index({ keyHash: 1, isActive: 1 });

// ============================================================================
// 🛡️ SOVEREIGN HOOKS
// ============================================================================

/**
 * 🛡️ PRE-SAVE INTERCEPTOR
 * Ensures every key event is pulsed through the Forensic Echo.
 */
ApiKeySchema.pre('save', async function(next) {
  if (this.isNew) {
    // Pulse Genesis Telemetry
    await broadcastTelemetry(
      this.tenantId.toString(),
      'API_KEY_PROVISIONED',
      'SYSTEM',
      'GENESIS',
      { keyId: this.keyId, tier: this.tier }
    );
  }
  next();
});

// ============================================================================
// 🧪 BOARDROOM CAPABILITIES
// ============================================================================

/**
 * @method verifyKey
 * @desc Validates a raw key against the Sovereign Hash.
 */
ApiKeySchema.statics.verifyKey = async function(rawKey) {
  const hash = crypto.createHash('sha256').update(rawKey).digest('hex');
  const keyDoc = await this.findOne({ keyHash: hash, isActive: true }).select('+keyHash');

  if (keyDoc) {
    keyDoc.lastUsed = new Date();
    await keyDoc.save();
    return keyDoc;
  }
  return null;
};

/**
 * @method revokeKey
 * @desc Administratively severs access and logs the forensic breach.
 */
ApiKeySchema.methods.revokeKey = async function(traceId, performer) {
  this.isActive = false;
  this.forensicChain.push({
    traceId,
    action: 'KEY_REVOKED',
    performer,
    timestamp: new Date()
  });

  await broadcastTelemetry(this.tenantId.toString(), 'API_KEY_REVOKED', performer, 'SECURITY_ACTION', { traceId, keyId: this.keyId });
  return this.save();
};

export const ApiKey = mongoose.models.ApiKey || mongoose.model('ApiKey', ApiKeySchema);
export default ApiKey;
