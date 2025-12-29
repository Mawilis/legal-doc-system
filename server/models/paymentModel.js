/**
 * ~/server/models/paymentModel.js
 *
 * Enterprise Payment Model
 * ------------------------
 * Collaboration-ready, production-grade schema for managing payments.
 * - Links to invoices, cases, and clients.
 * - Tracks payment method, amount, and status.
 * - Includes audit history for compliance.
 * - Indexed for performance on status and invoice.
 */

'use strict';

const mongoose = require('mongoose');

// ------------------------------------------
// Audit History Sub-Schema
// ------------------------------------------
const historySchema = new mongoose.Schema(
    {
        action: { type: String, required: true, trim: true },
        by: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
        date: { type: Date, default: Date.now },
        reason: { type: String, trim: true }
    },
    { _id: false }
);

// ------------------------------------------
// Payment Schema
// ------------------------------------------
const paymentSchema = new mongoose.Schema(
    {
        // 1) Identity
        referenceNumber: { type: String, required: true, unique: true, index: true }, // e.g., PAY-2025-001

        // 2) Relations
        invoice: { type: mongoose.Schema.Types.ObjectId, ref: 'Invoice', required: true },
        case: { type: mongoose.Schema.Types.ObjectId, ref: 'Case' },
        client: { type: mongoose.Schema.Types.ObjectId, ref: 'Client' },
        createdBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },

        // 3) Financials
        amount: { type: Number, required: true, min: 0 },
        currency: { type: String, default: 'ZAR' },
        method: {
            type: String,
            enum: ['Cash', 'Card', 'EFT', 'Cheque', 'Mobile Money'],
            default: 'EFT'
        },
        transactionId: { type: String, trim: true }, // External reference (bank, gateway)

        // 4) Status
        status: {
            type: String,
            enum: ['Pending', 'Completed', 'Failed', 'Refunded'],
            default: 'Pending',
            index: true
        },

        // 5) Metadata
        meta: { type: Object, default: {} },

        // 6) Audit History
        history: { type: [historySchema], default: [] }
    },
    { timestamps: true }
);

// ------------------------------------------
// Indexes
// ------------------------------------------
paymentSchema.index({ status: 1, invoice: 1 });
paymentSchema.index({ client: 1, createdAt: -1 });

// ------------------------------------------
// Instance Methods
// ------------------------------------------
/**
 * Mark payment as completed and update invoice balance.
 */
paymentSchema.methods.completePayment = async function (options = {}) {
    this.status = 'Completed';
    this.history.push({
        action: 'PAYMENT_COMPLETED',
        by: options.by || undefined,
        reason: options.reason || `Payment of ${this.amount} marked as completed`
    });

    // Update linked invoice balance
    const Invoice = mongoose.model('Invoice');
    const invoice = await Invoice.findById(this.invoice);
    if (invoice) {
        await invoice.applyPayment(this.amount, { by: options.by, reason: 'Payment recorded' });
    }

    return this.save();
};

/**
 * Transition payment status with audit history.
 */
paymentSchema.methods.transitionStatus = function (nextStatus, options = {}) {
    const current = this.status;
    this.status = nextStatus;
    this.history.push({
        action: 'STATUS_CHANGED',
        by: options.by || undefined,
        reason: options.reason || `Status changed from '${current}' to '${nextStatus}'`
    });
    return this.save();
};

// ------------------------------------------
// Model Export
// ------------------------------------------
module.exports = mongoose.model('Payment', paymentSchema);
