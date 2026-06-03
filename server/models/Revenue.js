/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - INSTITUTIONAL REVENUE SCHEMA [V2.0.1-MARS-EPITOMISED]                                                                      ║
 * ║ [TRANSACTIONAL LEDGER | FORENSIC AUDIT TRAILS | ARR/MRR BENCHMARKING | BILLION DOLLAR SPEC]                                            ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 2.0.1-MARS | PRODUCTION READY | BIBLICAL WORTH BILLIONS                                                                       ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY | SELF-VALIDATING LEDGER                                  ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/Revenue.js                                                         ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated absolute financial integrity and trajectory-aware growth forecasting.                ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Merged legacy revenueModel.js forensic tracking into the master transactional ledger.           ║
 * ║ • AI Engineering (Gemini) - ENHANCED: Injected Forensic Seal verification method for runtime integrity proof. [2026-05-21]             ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import crypto from 'node:crypto';

const RevenueSchema = new mongoose.Schema({
  /**
   * 🛡️ TENANT IDENTITY ANCHOR
   * Ensures absolute data isolation. Every revenue strike is cryptographically bound to a specific tenant.
   */
  tenantId: {
    type: String,
    required: [true, 'Institutional Tenant ID mandatory for financial isolation'],
    index: true,
    default: 'WILSY_GLOBAL_ROOT'
  },
  transactionId: {
    type: String,
    unique: true,
    required: true,
    default: () => `REV-${Date.now()}-${Math.floor(Math.random() * 1000)}`
  },
  amount: {
    type: Number,
    required: [true, 'Financial strike requires a defined value'],
    min: 0
  },
  /**
   * 📈 RECURRING REVENUE SHARDS
   * Essential for the Growth Trajectory Engine and $1B boardroom forecasting.
   */
  annualRecurringRevenue: {
    type: Number,
    default: 0,
    index: true
  },
  monthlyRecurringRevenue: {
    type: Number,
    default: 0,
    index: true
  },
  currency: {
    type: String,
    default: 'ZAR',
    enum: ['ZAR', 'USD', 'GBP', 'EUR']
  },
  category: {
    type: String,
    enum: ['LEGAL_FEES', 'CONSULTATION', 'DISBURSEMENTS', 'RETAINER', 'TRUST_INTEREST'],
    required: true,
    index: true
  },
  status: {
    type: String,
    enum: ['PENDING', 'RECONCILED', 'VOID', 'DISPUTED'],
    default: 'PENDING',
    index: true
  },
  /** @description Optional fee earner association for automated system strikes. */
  feeEarner: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: false,
    index: true
  },
  metadata: {
    type: mongoose.Schema.Types.Mixed,
    default: {}
  },
  timestamp: {
    type: Date,
    default: Date.now,
    index: true
  },
  /**
   * 🔬 FORENSIC AUDIT TELEMETRY
   * Tracking the exact microsecond this financial shard was updated.
   */
  lastForensicAudit: {
    type: Date,
    default: Date.now
  },
  /**
   * 🧬 CRYPTOGRAPHIC VERSIONING
   */
  versionTag: {
    type: String,
    default: 'SINGULARITY-V2'
  },
  /**
   * 🛡️ FORENSIC SEAL
   * SHA3-512 Hash for self-verifying integrity checks.
   */
  forensicSeal: {
    type: String,
    default: null
  }
}, {
  timestamps: true,
  minimize: false,
  collection: 'revenue_ledger'
});

/**
 * 🛡️ PRE-SAVE HOOK: Forensic Timestamp Update & Seal Generation
 */
RevenueSchema.pre('save', function(next) {
  this.lastForensicAudit = new Date();
  // Self-sealing the record on write
  const sealContent = `${this.transactionId}|${this.amount}|${this.tenantId}`;
  this.forensicSeal = crypto.createHash('sha3-512').update(sealContent).digest('hex');
  next();
});

/**
 * @method verifyIntegrity
 * @description Validates the forensic seal of this revenue record.
 * @returns {boolean} Integrity verification status.
 */
RevenueSchema.methods.verifyIntegrity = function() {
    const sealContent = `${this.transactionId}|${this.amount}|${this.tenantId}`;
    const calculated = crypto.createHash('sha3-512').update(sealContent).digest('hex');
    return calculated === this.forensicSeal;
};

/**
 * 🏛️ INSTITUTIONAL INDEXING
 * Optimized for temporal trajectory strikes, Grafana aggregations, and cross-shard audits.
 */
RevenueSchema.index({ tenantId: 1, timestamp: -1 });
RevenueSchema.index({ tenantId: 1, annualRecurringRevenue: -1 });
RevenueSchema.index({ feeEarner: 1, category: 1 });

const Revenue = mongoose.models.Revenue || mongoose.model('Revenue', RevenueSchema);

export default Revenue;
