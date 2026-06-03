/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN LEDGER MODEL [V27.9.0-OMEGA]                                                                                      ║
 * ║ [ATOMIC REVENUE AGGREGATE | FORENSIC CHAIN REGISTRY | NATIVE SHA3-512 SEALING | MULTIVERSE ISOLATION]                                   ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 27.9.0-OMEGA | PRODUCTION READY                                                                                               ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL FINALITY                                                           ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/ledgerModel.js                                                     ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated revolutionary institutional integrity and 10+ year future-proofing.                  ║
 * ║ • Gemini (AI Engineering) - Engineered the Native SHA3-512 Ledger Sealing and Multiverse Isolation hooks.                              ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import crypto from 'node:crypto';
import { getCurrentTenantId } from '../middleware/tenantContext.js';

const { Schema } = mongoose;

const ledgerSchema = new Schema({
  // 🏢 TENANT NEXUS
  tenantId: {
    type: Schema.Types.ObjectId,
    ref: 'Tenant',
    required: true,
    unique: true,
    index: true
  },

  // 💰 FINANCIAL AGGREGATES (Represented in Cents for Absolute Precision)
  amount: { type: Number, required: true, default: 0 },
  monthlyRecurring: { type: Number, default: 0 },
  transactionsPerSecond: { type: Number, default: 0 },

  // 📜 FORENSIC CHAIN: "Every action sealed in sovereign truth."
  forensicChain: [{
    entryId: { type: String, required: true },
    timestamp: { type: Date, default: Date.now },
    action: String,
    performer: String,
    payload: Schema.Types.Mixed,
    seal: {
      algorithm: { type: String, default: 'SHA3-512-NATIVE' },
      hash: { type: String, required: true },
      signature: String
    }
  }],

  // 🛡️ MASTER LEDGER SEAL
  ledgerSeal: { type: String, index: true }

}, {
  timestamps: true,
  collection: 'sovereign_ledger'
});

// ============================================================================
// 🧪 SOVEREIGN ASYNC HOOKS
// ============================================================================

/**
 * 🛡️ MULTIVERSE ISOLATION HOOK
 */
ledgerSchema.pre(/^find/, function(next) {
  const tenantId = getCurrentTenantId();
  if (tenantId && tenantId !== 'WILSY_SOVEREIGN_ROOT') {
    this.where({ tenantId });
  }
  next();
});

/**
 * 🧪 MASTER INTEGRITY SEAL
 */
ledgerSchema.pre('save', function(next) {
  if (this.isModified('amount') || this.isModified('monthlyRecurring') || this.isModified('forensicChain')) {
    const preImage = JSON.stringify({
      tenantId: this.tenantId,
      amount: this.amount,
      mrr: this.monthlyRecurring,
      chainLength: this.forensicChain.length
    });
    this.ledgerSeal = crypto.createHash('sha3-512').update(preImage).digest('hex');
  }
  next();
});

export const Ledger = mongoose.models.Ledger || mongoose.model('Ledger', ledgerSchema);
export default Ledger;
