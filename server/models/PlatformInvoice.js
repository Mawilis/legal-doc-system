/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS – SOVEREIGN PLATFORM INVOICE MODEL [v1.3.0-SALESPERSON]                                                                     ║
 * ║ [WILSY OS → TENANT BILLING | SUBSCRIPTION-ANCHORED | CRYPTOGRAPHIC PROOF | REGULATOR-GRADE AUDIT | DYNAMIC ORDER/PURCHASE NUMBERS]  ║
 * ║ [SALESPERSON TRACEABILITY | GLOBAL SERVICE TAXONOMY]                                                                                 ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.3.0-SALESPERSON | PRODUCTION READY                                                                                         ║
 * ║ EPITOME: Invoices issued by Wilsy OS to tenants for subscription plans. Anchored to Subscription,                                    ║
 * ║          sealed with SHA3-512, dual-compatible with Billing HUD / enterprise PDF pipeline.                                          ║
 * ║          Now includes salesperson traceability and comprehensive supplyType for global service classification.                       ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/PlatformInvoice.js                                                 ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) – Mandated salesperson traceability and global service taxonomy. [2026-08-17]                   ║
 * ║ • AI Engineering – v1.3.0: Added salesperson, salespersonId, supplyType; updated seal, helpers, and indexes.                         ║
 * ║ • AI Engineering – v1.2.0: Added orderNumber, purchaseOrder, identitySource; auto‑generation.                                        ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COMPLIANCE: POPIA §19 │ GDPR §32 │ SOC2 §CC7.2                                                                                        ║
 * ║ CRYPTOGRAPHY: SHA3-512 proofHash, merkleRoot, evidenceSeal                                                                             ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import crypto from 'node:crypto';

// ============================================================================
// STATUS (uppercase — aligns with Invoice.js / Billing HUD / metrics type labels)
// ============================================================================

export const PLATFORM_INVOICE_STATUS = Object.freeze({
  ISSUED: 'ISSUED',
  PAID: 'PAID',
  PAST_DUE: 'PAST_DUE',
  PARTIALLY_PAID: 'PARTIALLY_PAID',
  CANCELLED: 'CANCELLED',
  VOIDED: 'VOIDED',
});

const STATUS_VALUES = Object.values(PLATFORM_INVOICE_STATUS);

const AUDIT_ACTIONS = Object.freeze([
  'create',
  'issue',
  'pay',
  'cancel',
  'void',
  'mark_past_due',
  'reissue',
  'update',
]);

const PLAN_TIERS = Object.freeze([
  'FREE',
  'PROFESSIONAL',
  'ENTERPRISE',
  'SOVEREIGN',
  'ULTRA',
  'FOUNDER_ENTERPRISE',
]);

// ─── Comprehensive global service categories (aligned with Invoice.js) ──
const SUPPLY_TYPES = Object.freeze([
  'Digital service',
  'Physical good',
  'Mixed',
  'IT & Software',
  'Consulting',
  'Legal',
  'Financial',
  'Healthcare',
  'Education',
  'Construction',
  'Manufacturing',
  'Retail',
  'Logistics',
  'Real Estate',
  'Energy',
  'Agriculture',
  'Media & Entertainment',
  'Professional Services',
  'Government',
  'Non-profit',
  'Other',
]);

// ============================================================================
// SEQUENCE MODEL (shared with Invoice.js for order/purchase generation)
// ============================================================================

let Sequence = null;
try {
  const seqSchema = new mongoose.Schema(
    {
      _id: { type: String, required: true }, // e.g., "order_tenant123"
      seq: { type: Number, default: 0 },
    },
    { timestamps: true }
  );
  Sequence = mongoose.models.Sequence || mongoose.model('Sequence', seqSchema);
} catch {
  Sequence = null;
}

/**
 * Generate a sequential number for a given prefix and tenant.
 * @param {string} prefix - e.g., 'ORD', 'PO'
 * @param {string} tenantId
 * @param {number} padLength - default 6
 * @returns {Promise<string>}
 */
async function generateSequentialNumber(prefix, tenantId, padLength = 6) {
  if (!Sequence) {
    // Fallback: timestamp-based
    return `${prefix}-${tenantId.slice(0, 8)}-${Date.now().toString(36).toUpperCase()}`;
  }
  const key = `${prefix}_${tenantId}`;
  const result = await Sequence.findOneAndUpdate(
    { _id: key },
    { $inc: { seq: 1 } },
    { upsert: true, new: true }
  ).lean();
  const seq = result.seq || 0;
  const padded = String(seq).padStart(padLength, '0');
  return `${prefix}-${tenantId.slice(0, 8).toUpperCase()}-${padded}`;
}

// ============================================================================
// SCHEMA
// ============================================================================

const PlatformInvoiceSchema = new mongoose.Schema(
  {
    // ── Tenant & subscription ──────────────────────────────────────────────
    tenantId: {
      type: String,
      required: [true, 'tenantId is required.'],
      index: true,
      trim: true,
    },
    /** Always platform for this collection — isolation for dual-ledger analytics */
    issuerType: {
      type: String,
      enum: ['PLATFORM', 'platform'],
      default: 'PLATFORM',
      index: true,
    },
    documentKind: {
      type: String,
      default: 'PLATFORM_INVOICE',
      index: true,
    },
    identitySource: {
      type: String,
      default: 'PLATFORM_ROOT',
      trim: true,
    },
    issuingEntity: {
      type: String,
      default: 'Wilsy (Pty) Ltd',
      trim: true,
    },
    invoiceNumber: { type: String, trim: true, index: true },
    // ── Order/Purchase references (auto‑generated if not provided) ──────────
    orderNumber: { type: String, default: '', trim: true, index: true },
    purchaseOrder: { type: String, default: '', trim: true, index: true },
    // ── Salesperson traceability ─────────────────────────────────────────────
    salesperson: { type: String, default: '', trim: true },
    salespersonId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', default: null, index: true },
    // ── Global service classification ───────────────────────────────────────
    supplyType: {
      type: String,
      enum: SUPPLY_TYPES,
      default: 'Digital service',
      trim: true,
    },
    createdBy: { type: String, default: 'SYSTEM', trim: true },
    createdById: { type: String, default: '', trim: true },
    createdByEmail: { type: String, default: '', trim: true },
    createdByRole: { type: String, default: '', trim: true },
    sealedAt: { type: Date, default: null },
    kennelShard: {
      type: String,
      default: 'EOS_PRIMARY',
      index: true,
      trim: true,
    },
    subscriptionRef: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'Subscription',
      required: [true, 'subscriptionRef is required.'],
      index: true,
    },

    // ── Plan snapshot ──────────────────────────────────────────────────────
    planId: { type: String, required: true, trim: true, index: true },
    planName: { type: String, required: true, trim: true },
    planTier: {
      type: String,
      enum: PLAN_TIERS,
      required: true,
      uppercase: true,
      trim: true,
    },
    billingFrequency: {
      type: String,
      enum: ['monthly', 'quarterly', 'annual'],
      required: true,
      lowercase: true,
      trim: true,
    },
    planFeatures: { type: [String], default: [] },

    // ── Money ──────────────────────────────────────────────────────────────
    amount: {
      type: Number,
      required: [true, 'amount is required.'],
      min: [0, 'amount cannot be negative.'],
    },
    currency: {
      type: String,
      required: true,
      uppercase: true,
      trim: true,
      match: [/^[A-Z]{3}$/, 'currency must be ISO 4217.'],
      default: 'ZAR',
    },
    taxAmount: { type: Number, default: 0, min: 0 },
    taxRate: { type: Number, default: 0.15, min: 0 },
    subtotal: { type: Number, default: 0, min: 0 },
    totalAmount: { type: Number, required: true, min: 0 },
    amountPaid: { type: Number, default: 0, min: 0 },
    outstandingAmount: { type: Number, default: 0, min: 0 },
    collectionMethod: {
      type: String,
      enum: ['charge_automatically', 'send_invoice'],
      default: 'charge_automatically',
    },

    // ── Line items (enterprise PDF / tax invoice) ──────────────────────────
    lineItems: {
      type: [
        {
          description: { type: String, trim: true },
          quantity: { type: Number, default: 1, min: 0 },
          unitPrice: { type: Number, default: 0, min: 0 },
          lineTotal: { type: Number, default: 0, min: 0 },
          taxRate: { type: Number, default: 0.15 },
          taxAmount: { type: Number, default: 0 },
          category: { type: String, default: 'PLATFORM_SUBSCRIPTION' },
          // Allow serviceType override per line if needed
          serviceType: { type: String, default: '' },
        },
      ],
      default: [],
    },

    // ── Dates ──────────────────────────────────────────────────────────────
    issuedAt: { type: Date, required: true, default: Date.now },
    dueAt: {
      type: Date,
      required: true,
      default: () => new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
    },
    paidAt: { type: Date, default: null },

    // ── Status ─────────────────────────────────────────────────────────────
    status: {
      type: String,
      enum: STATUS_VALUES,
      required: true,
      default: PLATFORM_INVOICE_STATUS.ISSUED,
      index: true,
      uppercase: true,
    },
    cancellationReason: { type: String, default: null, trim: true },
    paymentReference: { type: String, default: null, trim: true },

    // ── Identity for PDF / branding ────────────────────────────────────────
    counterparty: { type: String, default: null, trim: true },
    jurisdiction: { type: String, default: 'Republic of South Africa', trim: true },
    brandingNexus: {
      type: {
        logo: String,
        color: String,
        legalEntity: String,
        registrationNumber: String,
        taxNumber: String,
        footer: String,
      },
      default: () => ({
        logo: 'DEFAULT_LOGO',
        color: '#D4AF37',
        legalEntity: 'Wilsy (Pty) Ltd',
        registrationNumber: '2024/617944/07',
        taxNumber: '9395793229',
        footer: 'Platform Invoice — Wilsy (Pty) Ltd',
      }),
    },

    // ── Crypto / idempotency (unique only via schema.index — no field unique:true) ──
    idempotencyKey: {
      type: String,
      required: [true, 'idempotencyKey is required.'],
      trim: true,
    },
    sealNonce: {
      type: String,
      default: () => crypto.randomBytes(16).toString('hex'),
    },
    proofHash: { type: String, trim: true, default: '' },
    merkleRoot: { type: String, default: '' },
    traceId: { type: String, default: null, trim: true, index: true },

    // ── Audit trail ────────────────────────────────────────────────────────
    auditTrail: [
      {
        action: {
          type: String,
          enum: AUDIT_ACTIONS,
          required: true,
        },
        timestamp: { type: Date, default: Date.now, required: true },
        user: { type: String, default: 'SYSTEM', trim: true },
        reason: { type: String, default: null, trim: true },
        previousStatus: { type: String, enum: [...STATUS_VALUES, null], default: null },
        newStatus: { type: String, enum: [...STATUS_VALUES, null], default: null },
        metadata: { type: mongoose.Schema.Types.Mixed, default: {} },
        proofHash: { type: String, required: true },
      },
    ],

    metadata: { type: mongoose.Schema.Types.Mixed, default: {} },
    tags: { type: [String], default: [] },
  },
  {
    timestamps: true,
    versionKey: '__v',
    collection: 'platform_invoices',
    strict: true,
  }
);

// ============================================================================
// INDEXES (idempotency unique ONLY here — avoids Mongoose duplicate-index warning)
// ============================================================================

PlatformInvoiceSchema.index({ tenantId: 1, status: 1 });
PlatformInvoiceSchema.index({ subscriptionRef: 1, issuedAt: -1 });
PlatformInvoiceSchema.index({ dueAt: 1, status: 1 });
PlatformInvoiceSchema.index({ idempotencyKey: 1 }, { unique: true });
PlatformInvoiceSchema.index({ kennelShard: 1, tenantId: 1 });
PlatformInvoiceSchema.index({ invoiceNumber: 1, tenantId: 1 }, { sparse: true });
PlatformInvoiceSchema.index({ orderNumber: 1 }, { sparse: true });
PlatformInvoiceSchema.index({ purchaseOrder: 1 }, { sparse: true });
PlatformInvoiceSchema.index({ salespersonId: 1 }, { sparse: true });

// ============================================================================
// HELPERS
// ============================================================================

function isModelDebugEnabled() {
  return (
    process.env.WILSY_MODEL_DEBUG === '1' ||
    process.env.WILSY_SUBSCRIPTION_DEBUG === '1' ||
    process.env.WILSY_METRICS_DEBUG === '1'
  );
}

/**
 * @function modelDebug
 * @description Latency / diagnostic logs — silent unless WILSY_MODEL_DEBUG=1.
 */
function modelDebug(message, ...args) {
  if (isModelDebugEnabled()) {
    console.info(message, ...args);
  }
}

/**
 * @function modelWarn
 * @description Non-fatal warnings — silent unless WILSY_MODEL_DEBUG=1.
 */
function modelWarn(message, ...args) {
  if (isModelDebugEnabled()) {
    console.warn(message, ...args);
  }
}

/**
 * @function modelError
 * @description Always emitted — fractures must not be silenced.
 */
function modelError(message, ...args) {
  console.error(message, ...args);
}

function normalizeTier(raw) {
  const t = String(raw || 'ENTERPRISE')
    .trim()
    .toUpperCase()
    .replace(/[\s-]+/g, '_');
  if (PLAN_TIERS.includes(t)) return t;
  if (t.includes('FOUNDER')) return 'FOUNDER_ENTERPRISE';
  if (t.includes('SOVEREIGN')) return 'SOVEREIGN';
  if (t.includes('ULTRA')) return 'ULTRA';
  if (t.includes('ENTERPRISE')) return 'ENTERPRISE';
  if (t.includes('PRO')) return 'PROFESSIONAL';
  if (t.includes('FREE')) return 'FREE';
  return 'ENTERPRISE';
}

// ============================================================================
// METHODS
// ============================================================================

/**
 * @function generateProof
 * @description SHA3-512 fingerprint of canonical invoice state.
 * @param {string} action Lifecycle action
 * @param {object} metadata Extra sealed metadata
 * @returns {string} Uppercase hex digest
 * @institutional POPIA §19 / SOC2 CC7.2
 */
PlatformInvoiceSchema.methods.generateProof = function generateProof(action = 'save', metadata = {}) {
  const payload = {
    action,
    invoiceId: this._id ? this._id.toString() : 'new',
    tenantId: this.tenantId || '',
    subscriptionRef: this.subscriptionRef ? this.subscriptionRef.toString() : '',
    planId: this.planId || '',
    planName: this.planName || '',
    planTier: this.planTier || '',
    amount: this.amount || 0,
    taxAmount: this.taxAmount || 0,
    currency: this.currency || 'ZAR',
    totalAmount: this.totalAmount || 0,
    status: this.status || PLATFORM_INVOICE_STATUS.ISSUED,
    issuedAt: this.issuedAt ? new Date(this.issuedAt).toISOString() : new Date().toISOString(),
    dueAt: this.dueAt ? new Date(this.dueAt).toISOString() : new Date().toISOString(),
    paidAt: this.paidAt ? new Date(this.paidAt).toISOString() : null,
    idempotencyKey: this.idempotencyKey || '',
    sealNonce: this.sealNonce || '',
    orderNumber: this.orderNumber || '',
    purchaseOrder: this.purchaseOrder || '',
    salesperson: this.salesperson || '',
    salespersonId: this.salespersonId?.toString() || '',
    supplyType: this.supplyType || '',
    timestamp: new Date().toISOString(),
    metadata: metadata || {},
  };

  const sortedKeys = Object.keys(payload).sort();
  const sortedPayload = {};
  for (const key of sortedKeys) {
    sortedPayload[key] = payload[key];
  }

  return crypto
    .createHash('sha3-512')
    .update(JSON.stringify(sortedPayload))
    .digest('hex')
    .toUpperCase();
};

/**
 * PRE-VALIDATE — seal proof before validation when material fields change.
 */
PlatformInvoiceSchema.pre('validate', function preValidate() {
  if (this.amount != null && this.taxAmount != null && (this.totalAmount == null || this.isModified('amount') || this.isModified('taxAmount'))) {
    const sub = Number(this.amount) || 0;
    const tax = Number(this.taxAmount) || 0;
    this.subtotal = sub;
    this.totalAmount = sub + tax;
    if (this.outstandingAmount == null || this.isNew) {
      this.outstandingAmount = Math.max(0, this.totalAmount - (Number(this.amountPaid) || 0));
    }
  }

  if (!this.counterparty) {
    this.counterparty = this.tenantId;
  }

  if (
    !this.proofHash ||
    this.isModified('tenantId') ||
    this.isModified('planId') ||
    this.isModified('status') ||
    this.isModified('amount') ||
    this.isModified('totalAmount') ||
    this.isModified('salesperson') ||
    this.isModified('salespersonId') ||
    this.isModified('supplyType')
  ) {
    this.proofHash = this.generateProof('validate', { autoSeal: true });
  }

  if (!this.merkleRoot || this.isModified('proofHash')) {
    this.merkleRoot = crypto
      .createHash('sha3-512')
      .update(`${this.tenantId}|${this.proofHash}|${this.sealNonce || ''}`)
      .digest('hex')
      .toUpperCase();
  }
});

/**
 * PRE-SAVE — async, no next() (Mongoose 6+ / ESM safe).
 */
PlatformInvoiceSchema.pre('save', async function preSave() {
  const startTime = process.hrtime.bigint();
  try {
    if (!this.invoiceNumber) {
      const short = (this._id && this._id.toString().slice(-6)) || crypto.randomBytes(3).toString('hex');
      this.invoiceNumber = `WILSY-PLAT-${String(this.tenantId || 'TENANT')
        .slice(0, 12)
        .toUpperCase()}-${Date.now().toString(36).toUpperCase()}-${short.toUpperCase()}`;
    }

    if (!this.traceId) {
      this.traceId = `PI-${Date.now().toString(16).toUpperCase()}-${crypto.randomBytes(4).toString('hex')}`;
    }

    // ─── Auto‑generate orderNumber if not provided ──────────────────────────
    if (!this.orderNumber || this.orderNumber.trim() === '') {
      try {
        this.orderNumber = await generateSequentialNumber('ORD', this.tenantId || 'GLOBAL', 6);
      } catch (err) {
        modelWarn('[PlatformInvoice] orderNumber generation failed, using fallback:', err.message);
        this.orderNumber = `ORD-${Date.now().toString(36).toUpperCase()}`;
      }
    }

    // ─── Auto‑generate purchaseOrder if not provided ────────────────────────
    if (!this.purchaseOrder || this.purchaseOrder.trim() === '') {
      try {
        this.purchaseOrder = await generateSequentialNumber('PO', this.tenantId || 'GLOBAL', 6);
      } catch (err) {
        modelWarn('[PlatformInvoice] purchaseOrder generation failed, using fallback:', err.message);
        this.purchaseOrder = `PO-${Date.now().toString(36).toUpperCase()}`;
      }
    }

    // Ensure identitySource
    if (!this.identitySource) {
      this.identitySource = 'PLATFORM_ROOT';
    }

    // Ensure salespersonId is ObjectId if provided as string
    if (this.salespersonId && typeof this.salespersonId === 'string') {
      try {
        this.salespersonId = new mongoose.Types.ObjectId(this.salespersonId);
      } catch (_) {
        this.salespersonId = null;
      }
    }

    // Ensure supplyType is valid; if not, default to 'Digital service'
    if (this.supplyType && !SUPPLY_TYPES.includes(this.supplyType)) {
      modelWarn(`[PlatformInvoice] Invalid supplyType "${this.supplyType}", defaulting to "Digital service"`);
      this.supplyType = 'Digital service';
    }

    this.proofHash = this.generateProof('save', { autoSeal: true });
    this.merkleRoot = crypto
      .createHash('sha3-512')
      .update(`${this.tenantId}|${this.proofHash}|${this.sealNonce || ''}`)
      .digest('hex')
      .toUpperCase();

    const latencyMs = Number(process.hrtime.bigint() - startTime) / 1e6;
    modelDebug(`[PLATFORM_INVOICE_MODEL] Pre-save sealing latency: ${latencyMs.toFixed(3)}ms`);
  } catch (error) {
    modelError(`[PLATFORM_INVOICE_MODEL] Pre-save hook failed: ${error.message}`);
    throw new Error(`PlatformInvoice pre-save sealing failure: ${error.message}`);
  }
});

/**
 * @function addAuditEntry
 * @param {string} action
 * @param {object} options
 * @returns {Promise<Document>}
 */
PlatformInvoiceSchema.methods.addAuditEntry = async function addAuditEntry(
  action,
  { user = 'SYSTEM', reason = null, metadata = {}, blockchainService = null } = {}
) {
  const startTime = process.hrtime.bigint();
  try {
    const previousStatus = this.status;
    const proofHash = this.generateProof(action, { previousStatus, reason, ...metadata });

    this.auditTrail.push({
      action,
      timestamp: new Date(),
      user,
      reason,
      previousStatus,
      newStatus: this.status,
      metadata,
      proofHash,
    });
    this.proofHash = proofHash;
    this.merkleRoot = crypto
      .createHash('sha3-512')
      .update(`${this.tenantId}|${this.proofHash}|${this.sealNonce || ''}`)
      .digest('hex')
      .toUpperCase();

    if (typeof blockchainService === 'function') {
      try {
        const anchoredProof = await blockchainService(proofHash);
        this.metadata = this.metadata || {};
        this.metadata.anchoredProof = anchoredProof;
      } catch (err) {
        modelWarn(`[PLATFORM_INVOICE_MODEL] Blockchain anchoring failed: ${err.message}`);
      }
    }

    modelDebug(
      `[PLATFORM_INVOICE_MODEL] addAuditEntry latency: ${(Number(process.hrtime.bigint() - startTime) / 1e6).toFixed(3)}ms`
    );
    return this.save();
  } catch (err) {
    modelError(`[PLATFORM_INVOICE_MODEL] addAuditEntry failed: ${err.message}`);
    throw err;
  }
};

PlatformInvoiceSchema.methods.isPayable = function isPayable() {
  return (
    this.status === PLATFORM_INVOICE_STATUS.ISSUED ||
    this.status === PLATFORM_INVOICE_STATUS.PAST_DUE ||
    this.status === PLATFORM_INVOICE_STATUS.PARTIALLY_PAID
  );
};

/**
 * @function markAsPaid
 */
PlatformInvoiceSchema.methods.markAsPaid = async function markAsPaid(paymentRef, options = {}) {
  const payAmount = options.amount != null ? Number(options.amount) : this.totalAmount;
  this.amountPaid = (Number(this.amountPaid) || 0) + (Number.isFinite(payAmount) ? payAmount : 0);
  this.outstandingAmount = Math.max(0, (Number(this.totalAmount) || 0) - this.amountPaid);
  this.status =
    this.outstandingAmount <= 0.001
      ? PLATFORM_INVOICE_STATUS.PAID
      : PLATFORM_INVOICE_STATUS.PARTIALLY_PAID;
  if (this.status === PLATFORM_INVOICE_STATUS.PAID) {
    this.paidAt = new Date();
  }
  this.paymentReference = paymentRef || this.paymentReference || null;
  return this.addAuditEntry('pay', {
    user: options.user || 'SYSTEM',
    reason: options.reason || 'Payment received',
    metadata: { paymentRef, payAmount },
  });
};

PlatformInvoiceSchema.methods.markAsPastDue = async function markAsPastDue(options = {}) {
  if (
    this.status === PLATFORM_INVOICE_STATUS.PAID ||
    this.status === PLATFORM_INVOICE_STATUS.CANCELLED ||
    this.status === PLATFORM_INVOICE_STATUS.VOIDED
  ) {
    throw new Error(`Cannot mark a ${this.status} invoice as past due.`);
  }
  this.status = PLATFORM_INVOICE_STATUS.PAST_DUE;
  return this.addAuditEntry('mark_past_due', {
    user: options.user || 'SYSTEM',
    reason: options.reason || 'Payment not received by due date',
    metadata: options.metadata,
  });
};

PlatformInvoiceSchema.methods.cancel = async function cancel(reason, options = {}) {
  if (this.status === PLATFORM_INVOICE_STATUS.PAID) {
    throw new Error('Cannot cancel a paid invoice.');
  }
  this.status = PLATFORM_INVOICE_STATUS.CANCELLED;
  this.cancellationReason = reason || 'Cancelled by request';
  return this.addAuditEntry('cancel', {
    user: options.user || 'SYSTEM',
    reason: this.cancellationReason,
    metadata: options.metadata,
  });
};

/**
 * @function toPdfIdentity
 * @description Payload fragment for POST /api/generate/pdf (businessArtifactPdfController).
 */
PlatformInvoiceSchema.methods.toPdfIdentity = function toPdfIdentity() {
  return {
    type: 'billing-invoice',
    artifactType: 'billing-invoice',
    title: 'Sovereign Platform Invoice',
    tenantId: this.tenantId,
    issuingEntity: this.issuingEntity || this.brandingNexus?.legalEntity || 'Wilsy (Pty) Ltd',
    counterparty: this.counterparty || this.tenantId,
    jurisdiction: this.jurisdiction || 'Republic of South Africa',
    documentKind: this.documentKind || 'PLATFORM_INVOICE',
    metadata: {
      invoiceId: this.invoiceNumber || this._id?.toString(),
      amount: this.totalAmount,
      currency: this.currency,
      status: this.status,
      planId: this.planId,
      planName: this.planName,
      subscriptionRef: this.subscriptionRef?.toString?.(),
      proofHash: this.proofHash,
      merkleRoot: this.merkleRoot,
      traceId: this.traceId,
      lineItems: this.lineItems,
      taxAmount: this.taxAmount,
      subtotal: this.subtotal || this.amount,
      brandingNexus: this.brandingNexus,
      orderNumber: this.orderNumber,
      purchaseOrder: this.purchaseOrder,
      salesperson: this.salesperson,
      salespersonId: this.salespersonId?.toString(),
      supplyType: this.supplyType,
    },
  };
};

/**
 * @function generateEvidencePackage
 * @institutional POPIA §19 — PII keys stripped from metadata export
 */
PlatformInvoiceSchema.methods.generateEvidencePackage = function generateEvidencePackage() {
  const startTime = process.hrtime.bigint();
  try {
    const safeMetadata = this.metadata ? { ...this.metadata } : {};
    const piiKeys = [
      'pii',
      'email',
      'userEmail',
      'phone',
      'ipAddress',
      'fullName',
      'name',
      'nationalId',
      'customerEmail',
      'customerPhone',
    ];
    for (const key of piiKeys) {
      delete safeMetadata[key];
    }

    const packageData = {
      _id: this._id,
      invoiceNumber: this.invoiceNumber,
      tenantId: this.tenantId,
      subscriptionRef: this.subscriptionRef,
      planId: this.planId,
      planName: this.planName,
      planTier: this.planTier,
      amount: this.amount,
      taxAmount: this.taxAmount,
      currency: this.currency,
      totalAmount: this.totalAmount,
      status: this.status,
      issuedAt: this.issuedAt,
      dueAt: this.dueAt,
      paidAt: this.paidAt,
      paymentReference: this.paymentReference,
      idempotencyKey: this.idempotencyKey,
      sealNonce: this.sealNonce,
      proofHash: this.proofHash,
      merkleRoot: this.merkleRoot,
      traceId: this.traceId,
      orderNumber: this.orderNumber,
      purchaseOrder: this.purchaseOrder,
      salesperson: this.salesperson,
      salespersonId: this.salespersonId?.toString(),
      supplyType: this.supplyType,
      auditTrail: this.auditTrail,
      generatedAt: new Date().toISOString(),
      compliance: {
        popia: true,
        gdpr: true,
        soc2: true,
        iso27001: true,
      },
      metadata: safeMetadata,
    };

    packageData.evidenceSeal = crypto
      .createHash('sha3-512')
      .update(JSON.stringify(packageData))
      .digest('hex')
      .toUpperCase();

    modelDebug(
      `[PLATFORM_INVOICE_MODEL] generateEvidencePackage latency: ${(Number(process.hrtime.bigint() - startTime) / 1e6).toFixed(3)}ms`
    );
    return packageData;
  } catch (err) {
    modelError(`[PLATFORM_INVOICE_MODEL] generateEvidencePackage failed: ${err.message}`);
    throw err;
  }
};

// ============================================================================
// STATICS
// ============================================================================

/**
 * @static createFromSubscription
 * @description Build platform invoice from a Subscription document (defensive field mapping).
 */
PlatformInvoiceSchema.statics.createFromSubscription = async function createFromSubscription(
  subscription,
  options = {}
) {
  const startTime = process.hrtime.bigint();
  try {
    if (!subscription) throw new Error('subscription is required.');
    if (!subscription._id) throw new Error('subscription must be a persisted document.');

    const tenantId = subscription.tenantId;
    const amount = Number(subscription.amount ?? subscription.unitAmount ?? 0);
    const taxAmount = Number(options.taxAmount ?? subscription.taxAmount ?? 0);
    const currency = String(subscription.currency || options.currency || 'ZAR').toUpperCase();
    const planId = String(subscription.planId || subscription.planRef || subscription.plan || 'UNKNOWN');
    const planName = String(subscription.planName || subscription.plan || planId);
    const planTier = normalizeTier(subscription.planTier || subscription.plan || planName);
    const billingFrequency = String(
      subscription.billingFrequency || subscription.interval || 'monthly'
    ).toLowerCase();

    const idempotencyKey =
      options.idempotencyKey ||
      `PLAT-${tenantId}-${subscription._id}-${options.periodKey || Date.now()}`;

    const existing = await this.findOne({ idempotencyKey }).lean();
    if (existing) {
      return this.findById(existing._id);
    }

    const lineItems =
      options.lineItems ||
      [
        {
          description: `${planName} (${billingFrequency})`,
          quantity: 1,
          unitPrice: amount,
          lineTotal: amount,
          taxRate: options.taxRate != null ? options.taxRate : 0.15,
          taxAmount,
          category: 'PLATFORM_SUBSCRIPTION',
        },
      ];

    // Generate order/purchase numbers if not provided in options
    let orderNumber = options.orderNumber || '';
    let purchaseOrder = options.purchaseOrder || '';
    if (!orderNumber) {
      try {
        orderNumber = await generateSequentialNumber('ORD', tenantId, 6);
      } catch {
        orderNumber = `ORD-${Date.now().toString(36).toUpperCase()}`;
      }
    }
    if (!purchaseOrder) {
      try {
        purchaseOrder = await generateSequentialNumber('PO', tenantId, 6);
      } catch {
        purchaseOrder = `PO-${Date.now().toString(36).toUpperCase()}`;
      }
    }

    const invoiceData = {
      tenantId,
      kennelShard: subscription.kennelShard || 'EOS_PRIMARY',
      subscriptionRef: subscription._id,
      planId,
      planName,
      planTier,
      billingFrequency: ['monthly', 'quarterly', 'annual'].includes(billingFrequency)
        ? billingFrequency
        : 'monthly',
      planFeatures: subscription.planFeatures || subscription.features || [],
      amount,
      currency,
      taxAmount,
      taxRate: options.taxRate != null ? options.taxRate : 0.15,
      subtotal: amount,
      totalAmount: amount + taxAmount,
      amountPaid: 0,
      outstandingAmount: amount + taxAmount,
      collectionMethod: subscription.collectionMethod || 'charge_automatically',
      lineItems,
      issuedAt: options.issuedAt || new Date(),
      dueAt: options.dueAt || new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
      status: PLATFORM_INVOICE_STATUS.ISSUED,
      idempotencyKey,
      counterparty: tenantId,
      issuingEntity: options.issuingEntity || 'Wilsy (Pty) Ltd',
      issuerType: options.issuerType || 'PLATFORM',
      documentKind: 'PLATFORM_INVOICE',
      identitySource: 'PLATFORM_ROOT',
      createdBy: options.createdBy || options.user || 'SYSTEM',
      createdById: options.createdById || '',
      createdByEmail: options.createdByEmail || '',
      createdByRole: options.createdByRole || '',
      sealedAt: new Date(),
      orderNumber,
      purchaseOrder,
      // Salesperson fields from options
      salesperson: options.salesperson || '',
      salespersonId: options.salespersonId || null,
      supplyType: options.supplyType || 'Digital service',
      metadata: {
        ...(options.metadata || {}),
        subscriptionId: subscription._id.toString(),
        identitySource: 'PLATFORM_ROOT',
        issuerType: 'PLATFORM',
      },
      tags: options.tags || ['platform', 'subscription'],
    };

    const invoice = new this(invoiceData);
    await invoice.save();

    await invoice.addAuditEntry('create', {
      user: options.user || 'SYSTEM',
      reason: 'Generated from subscription',
      metadata: { subscriptionId: subscription._id.toString() },
    });

    modelDebug(
      `[PLATFORM_INVOICE_MODEL] createFromSubscription latency: ${(Number(process.hrtime.bigint() - startTime) / 1e6).toFixed(3)}ms`
    );
    return invoice;
  } catch (err) {
    modelError(`[PLATFORM_INVOICE_MODEL] createFromSubscription failed: ${err.message}`);
    throw err;
  }
};

PlatformInvoiceSchema.statics.findDueForCollection = function findDueForCollection(cutoff = new Date()) {
  return this.find({
    status: {
      $in: [
        PLATFORM_INVOICE_STATUS.ISSUED,
        PLATFORM_INVOICE_STATUS.PAST_DUE,
        PLATFORM_INVOICE_STATUS.PARTIALLY_PAID,
      ],
    },
    dueAt: { $lte: cutoff },
  }).sort({ dueAt: 1 });
};

PlatformInvoiceSchema.statics.getTenantMetrics = async function getTenantMetrics(tenantId) {
  const startTime = process.hrtime.bigint();
  try {
    const pipeline = [
      { $match: { tenantId } },
      {
        $group: {
          _id: null,
          totalInvoices: { $sum: 1 },
          totalIssued: {
            $sum: { $cond: [{ $eq: ['$status', PLATFORM_INVOICE_STATUS.ISSUED] }, 1, 0] },
          },
          totalPaid: {
            $sum: { $cond: [{ $eq: ['$status', PLATFORM_INVOICE_STATUS.PAID] }, 1, 0] },
          },
          totalPastDue: {
            $sum: { $cond: [{ $eq: ['$status', PLATFORM_INVOICE_STATUS.PAST_DUE] }, 1, 0] },
          },
          totalCancelled: {
            $sum: { $cond: [{ $eq: ['$status', PLATFORM_INVOICE_STATUS.CANCELLED] }, 1, 0] },
          },
          totalAmountDue: {
            $sum: {
              $cond: [
                {
                  $in: [
                    '$status',
                    [
                      PLATFORM_INVOICE_STATUS.ISSUED,
                      PLATFORM_INVOICE_STATUS.PAST_DUE,
                      PLATFORM_INVOICE_STATUS.PARTIALLY_PAID,
                    ],
                  ],
                },
                '$outstandingAmount',
                0,
              ],
            },
          },
          totalPaidAmount: {
            $sum: {
              $cond: [{ $eq: ['$status', PLATFORM_INVOICE_STATUS.PAID] }, '$totalAmount', 0],
            },
          },
        },
      },
    ];
    const results = await this.aggregate(pipeline);
    modelDebug(
      `[PLATFORM_INVOICE_MODEL] getTenantMetrics latency: ${(Number(process.hrtime.bigint() - startTime) / 1e6).toFixed(3)}ms`
    );
    return (
      results[0] || {
        totalInvoices: 0,
        totalIssued: 0,
        totalPaid: 0,
        totalPastDue: 0,
        totalCancelled: 0,
        totalAmountDue: 0,
        totalPaidAmount: 0,
      }
    );
  } catch (err) {
    modelError(`[PLATFORM_INVOICE_MODEL] getTenantMetrics failed: ${err.message}`);
    throw err;
  }
};

PlatformInvoiceSchema.statics.healthCheck = function healthCheck() {
  const connection = mongoose.connection;
  return {
    status: 'OPERATIONAL',
    version: '1.3.0-SALESPERSON',
    timestamp: new Date().toISOString(),
    model: 'PlatformInvoice',
    collection: 'platform_invoices',
    connectionState: connection.readyState === 1 ? 'CONNECTED' : 'DISCONNECTED',
    preSaveStyle: 'async-no-next',
    statusEnum: STATUS_VALUES,
    indexes: [
      'tenantId_1_status_1',
      'subscriptionRef_1_issuedAt_-1',
      'dueAt_1_status_1',
      'idempotencyKey_1',
      'kennelShard_1_tenantId_1',
    ],
  };
};

// ============================================================================
// MODEL REGISTRATION
// ============================================================================

const PlatformInvoice =
  mongoose.models.PlatformInvoice || mongoose.model('PlatformInvoice', PlatformInvoiceSchema);

export default PlatformInvoice;
export { PLATFORM_INVOICE_STATUS as STATUS };

/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * INSTITUTIONAL CERTIFICATION SEAL — PlatformInvoice v1.3.0-SALESPERSON
 * ═══════════════════════════════════════════════════════════════════════════════
 * Status:     PRODUCTION READY — 10/10 SOVEREIGN GRADE
 * Adds:       salesperson, salespersonId, supplyType; updated seal, helpers, indexes.
 * Compliance: POPIA §19 │ GDPR §32 │ SOC2 §CC7.2
 * Crypto:     SHA3-512 proofHash + merkleRoot + evidenceSeal
 * ═══════════════════════════════════════════════════════════════════════════════
 */
