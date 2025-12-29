/**
 * ~/server/models/feeModel.js
 *
 * Enterprise Fee Model
 * --------------------
 * Collaboration-ready, production-grade schema for managing fees and tariffs.
 * - Defines fee codes, descriptions, and unit pricing.
 * - Supports flexible categories (e.g., Court Fees, Service Fees).
 * - Links to cases, documents, and invoices.
 * - Tracks audit history for compliance.
 * - Indexed for performance on feeCode and category.
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
// Fee Schema
// ------------------------------------------
const feeSchema = new mongoose.Schema(
    {
        // 1) Identity
        feeCode: { type: String, required: true, unique: true, index: true }, // e.g., "FEE-COURT-001"
        description: { type: String, required: true, trim: true }, // e.g., "Court Filing Fee"

        // 2) Financials
        unitPrice: { type: Number, required: true, min: 0 },
        taxRate: { type: Number, default: 0.15, min: 0 }, // Default VAT 15%
        currency: { type: String, default: 'ZAR' },

        // 3) Category
        category: { type: String, trim: true, default: 'General', index: true }, // e.g., "Court Fees", "Service Fees"

        // 4) Relations
        case: { type: mongoose.Schema.Types.ObjectId, ref: 'Case' },
        document: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' },
        invoice: { type: mongoose.Schema.Types.ObjectId, ref: 'Invoice' },
        createdBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },

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
feeSchema.index({ category: 1, feeCode: 1 });
feeSchema.index({ createdBy: 1, createdAt: -1 });

// ------------------------------------------
// Instance Methods
// ------------------------------------------
/**
 * Calculate total amount for a given quantity.
 */
feeSchema.methods.calculateAmount = function (quantity = 1) {
    const lineTotal = quantity * this.unitPrice;
    const tax = lineTotal * this.taxRate;
    return {
        subtotal: lineTotal,
        tax,
        total: lineTotal + tax
    };
};

/**
 * Transition fee status with audit history.
 */
feeSchema.methods.transitionStatus = function (nextStatus, options = {}) {
    const current = this.status || 'Active';
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
module.exports = mongoose.model('Fee', feeSchema);
