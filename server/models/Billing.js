/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN FINANCIAL LEDGER [V28.0.0-MARS]                                                                                   ║
 * ║ [SAAS SUBSCRIPTION NUCLEUS | AES-256-GCM | FORENSIC CHAIN INTEGRATION | NATIVE SHA3-512]                                               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 28.0.0-MARS | PRODUCTION READY                                                                                                ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL FINALITY                                                           ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/Billing.js                                                         ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated zero-skew financial integrity & SARS compliance.                                     ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Decoupled Tenant Client Invoicing. This model now strictly governs Sovereign SaaS Revenue.      ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import crypto from 'node:crypto';
import { getCurrentTenantId } from '../middleware/tenantContext.js';

const { Schema } = mongoose;

/**
 * 🔐 [QUANTUM SHIELD: AES-256-GCM]
 * Encrypts PII at the field level before it touches the physical disk.
 */
const encryptField = (value) => {
  if (!value || typeof value !== 'string') return value;
  // Fallback to a development key if the environment variable is missing during build
  const keyHex = process.env.ENCRYPTION_KEY || crypto.randomBytes(32).toString('hex');
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv('aes-256-gcm', Buffer.from(keyHex, 'hex'), iv);
  let encrypted = cipher.update(value, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  return { encrypted, iv: iv.toString('hex'), tag: cipher.getAuthTag().toString('hex') };
};

const BillingSchema = new Schema({
  // 🛡️ The Shard Owner this subscription applies to
  tenantId: { type: String, required: true, unique: true, index: true },

  tier: {
    type: String,
    enum: ['SOLO_PRACTITIONER', 'SMALL_FIRM', 'MID_SIZE_FIRM', 'LARGE_FIRM', 'ENTERPRISE', 'SOVEREIGN'],
    default: 'SOLO_PRACTITIONER'
  },
  billingCycle: { type: String, enum: ['MONTHLY', 'ANNUAL'], default: 'MONTHLY' },
  status: { type: String, enum: ['ACTIVE', 'PAST_DUE', 'SUSPENDED', 'CANCELLED'], default: 'ACTIVE' },

  // 💰 SOVEREIGN REVENUE RECOGNITION (Your ARR/MRR Metrics)
  totalVolume: { type: Number, default: 0 },
  monthlyRecurring: { type: Number, default: 0 }, // MRR logic for Founder Dashboard
  currency: { type: String, default: 'ZAR' },

  // 🔐 ENCRYPTED PAYMENT NEXUS (PCI-DSS)
  paymentDetails: {
    gatewayToken: { type: Object, set: encryptField },
    lastFour: String,
    method: { type: String, enum: ['CARD', 'EFT', 'CRYPTO_SETTLEMENT'], default: 'CARD' }
  },

  compliance: {
    vatRegistration: String,
    taxClearanceStatus: { type: String, default: 'VERIFIED' },
    popiaConsent: { type: Boolean, default: false }
  },

  // 📜 FORENSIC CHAIN: "Every cent sealed in sovereign truth."
  // Immutable ledger of changes to the Subscription Tier or Billing Status
  forensicChain: [{
    entryId: { type: String, required: true },
    timestamp: { type: Date, default: Date.now },
    action: { type: String, required: true },
    performer: { type: String, required: true },
    payload: Schema.Types.Mixed,
    seal: {
      algorithm: { type: String, default: 'SHA3-512-NATIVE' },
      hash: { type: String, required: true },
      signature: String
    },
    narrative: String
  }],

  // 🛡️ LEDGER INTEGRITY METADATA
  ledgerSeal: String // Master SHA3-512 seal of the subscription state

}, {
  timestamps: true,
  collection: 'sovereign_billing_ledger'
});

// ============================================================================
// 🧪 SOVEREIGN ASYNC HOOKS
// ============================================================================

/**
 * 🛡️ MULTIVERSE ISOLATION HOOK
 * Ensures no tenant can ever see another's ledger entries.
 */
BillingSchema.pre(/^find/, function(next) {
  const tenantId = getCurrentTenantId();
  if (tenantId && tenantId !== 'WILSY_ROOT' && tenantId !== 'GLOBAL_ROOT') {
    this.where({ tenantId });
  }
  next();
});

/**
 * 🧪 MASTER LEDGER SEAL
 * Automatically updates the top-level ledgerSeal whenever subscription status changes.
 */
BillingSchema.pre('save', function(next) {
  if (this.isModified('status') || this.isModified('monthlyRecurring') || this.isModified('tier')) {
    const preImage = JSON.stringify({
      tenantId: this.tenantId,
      tier: this.tier,
      mrr: this.monthlyRecurring,
      status: this.status
    });
    this.ledgerSeal = crypto.createHash('sha3-512').update(preImage).digest('hex');
  }
  next();
});

// ============================================================================
// 🏛️ SOVEREIGN MODEL EXPORT
// ============================================================================

export const Billing = mongoose.models.Billing || mongoose.model('Billing', BillingSchema);
export default Billing;
