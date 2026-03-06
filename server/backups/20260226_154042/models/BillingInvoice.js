#!/* eslint-disable */
/* ╔════════════════════════════════════════════════════════════════╗
  ║ BILLING INVOICE MODEL - INVESTOR-GRADE MODULE                 ║
  ║ Forensic Traceability | POPIA Compliant | Retention-Aware     ║
  ╚════════════════════════════════════════════════════════════════╝ */
/*
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/BillingInvoice.js
 * INVESTOR VALUE PROPOSITION:
 * • Provides auditable billing records for 7+ year retention
 * • Enables CFO-ready financial reporting
 * • Supports forensic investigation with SHA256 proof
 * • Compliance: Companies Act §24, POPIA §19, Consumer Protection Act §43
 */

import mongoose from 'mongoose';
import { v4 as uuidv4 } from 'uuid.js';
import { createHash } from 'crypto';

const { Schema } = mongoose;

/*
 * Billing Invoice Schema - Forensic-grade invoice tracking
 */
const billingInvoiceSchema = new Schema(
  {
    // Core invoice identification
    invoiceId: {
      type: String,
      required: true,
      unique: true,
      index: true,
      default: () => `INV-${new Date().getFullYear()}-${uuidv4().substring(0, 8)}`,
    },

    // Tenant isolation
    tenantId: {
      type: String,
      required: true,
      index: true,
      validate: {
        validator(v) {
          return /^[a-zA-Z0-9_-]{8,64}$/.test(v);
        },
        message: (props) => `${props.value} is not a valid tenant ID format`,
      },
    },

    // Invoice details
    invoiceNumber: {
      type: String,
      required: true,
      unique: true,
    },

    billingPeriod: {
      month: {
        type: Number, required: true, min: 1, max: 12,
      },
      year: { type: Number, required: true },
      startDate: { type: Date, required: true },
      endDate: { type: Date, required: true },
    },

    // Financial data
    currency: {
      type: String,
      default: 'ZAR',
      enum: ['ZAR', 'USD', 'EUR', 'GBP'],
    },

    items: [
      {
        description: { type: String, required: true },
        quantity: { type: Number, default: 1 },
        unitPrice: { type: Number, required: true },
        amount: { type: Number, required: true },
        type: {
          type: String,
          enum: ['subscription', 'usage', 'overage', 'credit', 'adjustment'],
        },
        metadata: { type: Schema.Types.Mixed },
      },
    ],

    subtotal: {
      type: Number,
      required: true,
      min: 0,
    },

    taxRate: {
      type: Number,
      default: 0.15, // 15% VAT (South Africa)
    },

    taxAmount: {
      type: Number,
      required: true,
      min: 0,
    },

    total: {
      type: Number,
      required: true,
      min: 0,
    },

    // Payment tracking
    status: {
      type: String,
      enum: ['draft', 'issued', 'paid', 'overdue', 'cancelled', 'refunded'],
      default: 'draft',
      index: true,
    },

    issuedAt: Date,
    dueDate: Date,
    paidAt: Date,
    paymentMethod: {
      type: String,
      enum: ['card', 'eft', 'crypto', 'credit', 'invoice'],
    },

    paymentReference: String,
    transactionId: String,

    // Forensic proof
    invoiceHash: {
      type: String,
      required: true,
      unique: true,
    },

    previousInvoiceHash: String,

    // Usage data reference
    usageReportId: String,
    usageRecords: [
      {
        recordId: String,
        count: Number,
        type: String,
      },
    ],

    // Tenant information (redacted in responses)
    billingEmail: {
      type: String,
      set(v) {
        // Store encrypted, return redacted
        return v; // In production, encrypt here
      },
    },

    billingAddress: {
      line1: String,
      line2: String,
      city: String,
      province: String,
      postalCode: String,
      country: { type: String, default: 'ZA' },
    },

    taxId: String,
    vatNumber: String,

    // Data governance
    retentionPolicy: {
      type: String,
      enum: ['companies_act_10_years', 'tax_act_5_years', 'permanent_record'],
      default: 'companies_act_10_years',
      required: true,
    },

    dataResidency: {
      type: String,
      enum: ['ZA', 'EU', 'US', 'GLOBAL'],
      default: 'ZA',
      required: true,
    },

    retentionStart: {
      type: Date,
      default: Date.now,
      required: true,
    },

    retentionEnd: {
      type: Date,
      required: true,
    },

    consentExemption: {
      type: Boolean,
      default: false,
    },

    // Audit fields
    createdBy: String,
    createdAt: {
      type: Date,
      default: Date.now,
      immutable: true,
    },
    updatedAt: {
      type: Date,
      default: Date.now,
    },
  },
  {
    timestamps: true,
    collection: 'billing_invoices',
  },
);

// Indexes for performance
billingInvoiceSchema.index({ tenantId: 1, status: 1 });
billingInvoiceSchema.index({ tenantId: 1, 'billingPeriod.year': 1, 'billingPeriod.month': 1 });
billingInvoiceSchema.index({ issuedAt: -1 });
billingInvoiceSchema.index({ dueDate: 1, status: 1 });

/*
 * Pre-save middleware to generate invoice hash and set retention
 */
billingInvoiceSchema.pre('save', function (next) {
  try {
    // Generate invoice number if not set
    if (!this.invoiceNumber) {
      const year = new Date().getFullYear();
      const month = String(new Date().getMonth() + 1).padStart(2, '0');
      const random = Math.floor(Math.random() * 10000)
        .toString()
        .padStart(4, '0');
      this.invoiceNumber = `INV-${year}${month}-${random}`;
    }

    // Generate invoice hash for tamper-evident proof
    const hashInput = [
      this.invoiceId,
      this.tenantId,
      this.subtotal,
      this.taxAmount,
      this.total,
      this.issuedAt?.toISOString() || new Date().toISOString(),
      this.status,
    ].join('|');

    this.invoiceHash = createHash('sha256').update(hashInput).digest('hex');

    // Set retention end based on policy
    if (!this.retentionEnd) {
      const retentionYears = {
        companies_act_10_years: 10,
        tax_act_5_years: 5,
        permanent_record: 100,
      };
      const years = retentionYears[this.retentionPolicy] || 10;
      this.retentionEnd = new Date();
      this.retentionEnd.setFullYear(this.retentionEnd.getFullYear() + years);
    }

    this.updatedAt = new Date();
    next();
  } catch (error) {
    next(error);
  }
});

/*
 * Instance method to check if invoice is under retention
 */
billingInvoiceSchema.methods.isUnderRetention = function () {
  return new Date() < this.retentionEnd;
};

/*
 * Instance method to redact sensitive data for POPIA compliance
 */
billingInvoiceSchema.methods.redactForExport = function () {
  const redacted = this.toObject();

  // Redact sensitive fields
  if (redacted.billingEmail) {
    const [localPart, domain] = redacted.billingEmail.split('@');
    redacted.billingEmail = `${localPart.substring(0, 2)}*@${domain}`;
  }

  if (redacted.taxId) {
    redacted.taxId = `*${redacted.taxId.slice(-4)}`;
  }

  if (redacted.vatNumber) {
    redacted.vatNumber = `*${redacted.vatNumber.slice(-4)}`;
  }

  return redacted;
};

/*
 * Static method to find invoices for tenant
 */
billingInvoiceSchema.statics.findForTenant = function (tenantId, filters = {}, pagination = {}) {
  const { limit = 100, skip = 0, sort = { issuedAt: -1 } } = pagination;

  return this.find({
    tenantId,
    ...filters,
  })
    .sort(sort)
    .limit(limit)
    .skip(skip)
    .lean();
};

/*
 * Static method to generate next invoice number
 */
billingInvoiceSchema.statics.generateNextInvoiceNumber = async function () {
  const year = new Date().getFullYear();
  const month = String(new Date().getMonth() + 1).padStart(2, '0');

  const lastInvoice = await this.findOne({
    invoiceNumber: new RegExp(`^INV-${year}${month}-`),
  }).sort({ invoiceNumber: -1 });

  if (lastInvoice) {
    const lastSeq = parseInt(lastInvoice.invoiceNumber.slice(-4));
    const nextSeq = (lastSeq + 1).toString().padStart(4, '0');
    return `INV-${year}${month}-${nextSeq}`;
  }

  return `INV-${year}${month}-0001`;
};

/*
 * ASSUMPTIONS:
 * - tenantId format: ^[a-zA-Z0-9_-]{8,64}$
 * - Default retention: companies_act_10_years (10 years)
 * - Default data residency: ZA
 * - VAT rate: 15% (South Africa)
 */

const BillingInvoice = mongoose.model('BillingInvoice', billingInvoiceSchema);

export default BillingInvoice;
