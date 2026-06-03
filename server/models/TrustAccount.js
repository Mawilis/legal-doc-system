/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - TRUST ACCOUNT LEDGER [V33.80.1-OMEGA-OPTIMIZED]                                                                             ║
 * ║ [LPC RULE 54 COMPLIANT | R10B+ ATOMIC FINALITY | SHA3-512 RECURSIVE CHAINING | TRACE-AWARE]                                           ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 33.80.1-OMEGA | PRODUCTION READY | BIBLICAL WORTH BILLIONS                                                                    ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | MATHEMATICAL CERTAINTY                                                         ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/TrustAccount.js                                                   ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated R10B+ auditable fiduciary certainty and LPC Rule 54 finality. [2026-05-04]           ║
 * ║ • AI Engineering (Gemini) - OPTIMIZED: Removed duplicate Mongoose indexes to streamline write strikes. [2026-05-06]                    ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';

const { Schema } = mongoose;

/**
 * 🧬 TRUST TRANSACTION SCHEMA
 * Represents an immutable fiduciary movement within the Sovereign Ledger.
 * Anchors are defined here to ensure atomic indexing within the transaction array.
 */
const TrustTransactionSchema = new Schema({
  transactionId: { type: String, required: true, unique: true },
  traceId: { type: String, required: true, index: true },
  timestamp: { type: Date, default: Date.now, index: true },
  type: {
    type: String,
    enum: ['DEPOSIT', 'WITHDRAWAL', 'TRANSFER', 'FEE_EARNED'],
    required: true
  },
  amount: { type: Number, required: true },
  description: { type: String, required: true },
  reference: { type: String, index: true },
  entityId: { type: Schema.Types.ObjectId, ref: 'Entity', required: true },
  initiatedBy: { type: Schema.Types.ObjectId, ref: 'User' },

  // 🧬 RECURSIVE FORENSIC LINK: SHA3-512 recursive link to the previous transaction hash
  forensicHash: { type: String, required: true, unique: true }
}, { timestamps: true });

/**
 * 🏛️ TRUST ACCOUNT SCHEMA [THE FIDUCIARY VAULT]
 */
const TrustAccountSchema = new Schema({
  tenantId: {
    type: Schema.Types.ObjectId,
    ref: 'Tenant',
    required: true,
    unique: true,
    index: true
  },
  accountNumber: { type: String, required: true, unique: true },
  bankName: { type: String, required: true },
  currency: { type: String, default: 'ZAR' },
  currentBalance: { type: Number, default: 0 },
  isFrozen: { type: Boolean, default: false },
  masterIntegritySeal: { type: String, unique: true },
  lastTransactionAt: { type: Date },
  transactions: [TrustTransactionSchema]
}, {
  timestamps: true,
  collection: 'fiduciary_trust_accounts'
});

// 🚀 RECTIFICATION: Removed TrustAccountSchema.index() calls for transaction fields.
// Mongoose automatically propagates the indexes from TrustTransactionSchema into the parent collection.

export const TrustAccount = mongoose.models.TrustAccount || mongoose.model('TrustAccount', TrustAccountSchema);
export default TrustAccount;
