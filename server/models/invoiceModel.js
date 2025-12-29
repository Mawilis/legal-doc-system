/**
 * ~/server/models/invoiceModel.js
 *
 * Enterprise Invoice Model (Billion-Dollar Legal Tech)
 * ----------------------------------------------------
 * Collaboration-ready, production-grade Mongoose schema for invoices.
 * - Reusable line item sub-schema (matches PDF line structure).
 * - Auto-calculates subtotal, tax, total, and balance on save.
 * - Clear identity fields (invoiceNumber, referenceNumber).
 * - Relations to Document, Client, and User (createdBy).
 * - Banking details for payment instructions.
 * - Status lifecycle with index for reporting and performance.
 * - Audit history array with action, actor, and timestamp.
 * - Helpful instance/static methods for payments and status transitions.
 * - Timestamps enabled (createdAt, updatedAt).
 */

'use strict';

const mongoose = require('mongoose');

// ------------------------------------------
// Helpers
// ------------------------------------------
/**
 * Round a number to 2 decimal places, avoiding floating point drift.
 */
const round2 = (num) => Number((Math.round((num + Number.EPSILON) * 100) / 100).toFixed(2));

/**
 * Validate positive amounts where required.
 */
const isNonNegative = (val) => typeof val === 'number' && val >= 0;

/**
 * Valid invoice statuses for lifecycle control.
 */
const INVOICE_STATUSES = ['Draft', 'Sent', 'Paid', 'Partially Paid', 'Overdue', 'Cancelled'];

// ------------------------------------------
// Line Item Sub-Schema (No _id for compact docs)
// ------------------------------------------
const InvoiceItemSchema = new mongoose.Schema(
    {
        /** Human-readable description of the item (e.g., "Service of Process (Rule 41)") */
        description: { type: String, required: true, trim: true },

        /** Optional business reference (e.g., case number fragment "1245/2025") */
        reference: { type: String, trim: true },

        /** Quantity of the item */
        quantity: { type: Number, default: 1, min: 0 },

        /** Unit price (excl. tax) */
        unitPrice: { type: Number, required: true, validate: [isNonNegative, 'unitPrice must be non-negative'] },

        /** Tax rate applied to the line (e.g., 0.15 for 15% VAT) */
        taxRate: { type: Number, default: 0.15, min: 0 },

        /** Final calculated amount for the line (incl. tax); computed in pre-save */
        amount: { type: Number, required: true, validate: [isNonNegative, 'amount must be non-negative'] }
    },
    { _id: false }
);

// ------------------------------------------
// Invoice Schema
// ------------------------------------------
const invoiceSchema = new mongoose.Schema(
    {
        // 1) Identity
        /** Firm-unique invoice number (e.g., "INV-2025-001") */
        invoiceNumber: { type: String, required: true, unique: true, index: true, trim: true },

        /** Business reference (links to case number or internal tracking; e.g., "1245/2025") */
        referenceNumber: { type: String, required: true, trim: true },

        // 2) Relations
        /** Optional link to the originating document */
        document: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' },

        /** Optional link to client record */
        client: { type: mongoose.Schema.Types.ObjectId, ref: 'Client' },

        /** Snapshot of the billing details at issuance time */
        billedTo: {
            name: { type: String, trim: true },
            address: { type: String, trim: true },
            email: { type: String, trim: true }
        },

        // 3) Financials
        /** Array of invoice line items (amount computed from quantity, unitPrice, taxRate) */
        items: { type: [InvoiceItemSchema], default: [] },

        /** Subtotal (sum of line totals excl. tax) */
        subtotal: { type: Number, default: 0, validate: [isNonNegative, 'subtotal must be non-negative'] },

        /** Tax total (sum of line tax amounts) */
        taxTotal: { type: Number, default: 0, validate: [isNonNegative, 'taxTotal must be non-negative'] },

        /** Discount applied to the invoice (absolute amount, not percentage) */
        discount: { type: Number, default: 0, min: 0 },

        /** Grand total (subtotal + taxTotal - discount) */
        total: { type: Number, required: true, validate: [isNonNegative, 'total must be non-negative'] },

        /** Outstanding amount (initially equals total; decreases as payments are recorded) */
        balance: { type: Number, required: true, validate: [isNonNegative, 'balance must be non-negative'] },

        // 4) Metadata
        /** Date the invoice was issued */
        dateIssued: { type: Date, default: Date.now },

        /** Due date for payment */
        dateDue: { type: Date, required: true },

        /** Status lifecycle with index for faster filtering */
        status: {
            type: String,
            enum: INVOICE_STATUSES,
            default: 'Draft',
            index: true
        },

        // 5) Payment Instructions (banking snapshot; can be overridden per invoice)
        bankingDetails: {
            bankName: { type: String, default: 'FNB', trim: true },
            accountNumber: { type: String, default: '123456789', trim: true },
            branchCode: { type: String, default: '250655', trim: true },
            reference: { type: String, trim: true } // Typically the invoiceNumber
        },

        // 6) Audit
        /** User that created the invoice */
        createdBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },

        /** History of actions taken on the invoice (e.g., status changes, edits) */
        history: {
            type: [
                {
                    action: { type: String, required: true, trim: true },
                    by: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
                    date: { type: Date, default: Date.now },
                    reason: { type: String, trim: true } // Optional reason/context
                }
            ],
            default: []
        }
    },
    { timestamps: true }
);

// ------------------------------------------
// Indexes for reporting and performance
// ------------------------------------------
invoiceSchema.index({ status: 1, dateDue: 1 });
invoiceSchema.index({ client: 1, dateIssued: -1 });

// ------------------------------------------
// Pre-Validation: Ensure items are present for non-zero totals
// ------------------------------------------
invoiceSchema.pre('validate', function (next) {
    // If no items, then totals and balance must be zero
    if (!this.items || this.items.length === 0) {
        this.subtotal = 0;
        this.taxTotal = 0;
        this.total = round2(0 - (this.discount || 0));
        if (this.total < 0) this.total = 0;
        // If new, ensure balance mirrors total
        if (this.isNew) {
            this.balance = this.total;
        }
    }
    next();
});

// ------------------------------------------
// Pre-Save: Auto-Calculate Line Item amounts and Invoice totals
// ------------------------------------------
invoiceSchema.pre('save', function (next) {
    let sub = 0;
    let tax = 0;

    if (Array.isArray(this.items) && this.items.length > 0) {
        this.items.forEach((item) => {
            const lineTotal = round2((item.quantity || 0) * (item.unitPrice || 0));
            const lineTax = round2(lineTotal * (item.taxRate || 0));
            sub += lineTotal;
            tax += lineTax;
            item.amount = round2(lineTotal + lineTax); // Line item total incl. tax
        });
    }

    this.subtotal = round2(sub);
    this.taxTotal = round2(tax);
    const discount = round2(this.discount || 0);
    this.total = round2(this.subtotal + this.taxTotal - discount);

    // If new, balance = total; otherwise preserve existing balance unless negative
    if (this.isNew) {
        this.balance = this.total;
    } else {
        this.balance = round2(Math.max(this.balance, 0));
    }

    next();
});

// ------------------------------------------
// Instance Methods
// ------------------------------------------
/**
 * Apply a payment to the invoice and update status accordingly.
 * @param {number} amount - Payment amount (must be > 0)
 * @param {Object} options - Optional metadata { by, reason }
 */
invoiceSchema.methods.applyPayment = async function (amount, options = {}) {
    const pay = round2(amount || 0);
    if (pay <= 0) throw new Error('Payment amount must be greater than 0');
    if (pay > this.balance) throw new Error('Payment exceeds outstanding balance');

    this.balance = round2(this.balance - pay);

    // Update status based on remaining balance
    if (this.balance === 0) {
        this.status = 'Paid';
    } else {
        this.status = 'Partially Paid';
    }

    // Push to audit history
    this.history.push({
        action: 'PAYMENT_APPLIED',
        by: options.by || undefined,
        reason: options.reason || `Payment of ${pay} applied`
    });

    return this.save();
};

/**
 * Transition status with audit history.
 * @param {string} nextStatus - Target status (must be in INVOICE_STATUSES)
 * @param {Object} options - { by, reason }
 */
invoiceSchema.methods.transitionStatus = async function (nextStatus, options = {}) {
    if (!INVOICE_STATUSES.includes(nextStatus)) {
        throw new Error(`Invalid status transition: ${nextStatus}`);
    }

    // Basic rules to prevent illogical transitions
    const current = this.status;
    if (current === 'Cancelled') throw new Error('Cannot transition a cancelled invoice');
    if (current === 'Paid' && nextStatus !== 'Cancelled') {
        throw new Error('Paid invoices can only be cancelled (with justification) or left as is');
    }

    this.status = nextStatus;
    this.history.push({
        action: 'STATUS_CHANGED',
        by: options.by || undefined,
        reason: options.reason || `Status changed from '${current}' to '${nextStatus}'`
    });

    return this.save();
};

// ------------------------------------------
// Static Methods
// ------------------------------------------
/**
 * Find overdue invoices (past due date with positive balance).
 */
invoiceSchema.statics.findOverdue = function () {
    const now = new Date();
    return this.find({ dateDue: { $lt: now }, balance: { $gt: 0 }, status: { $ne: 'Cancelled' } });
};

// ------------------------------------------
// Model Export
// ------------------------------------------
module.exports = mongoose.model('Invoice', invoiceSchema);


