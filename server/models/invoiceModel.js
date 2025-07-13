// server/models/invoiceModel.js

const mongoose = require('mongoose');

// This sub-schema defines the structure for individual line items on the invoice.
const lineItemSchema = new mongoose.Schema({
    description: {
        type: String,
        required: [true, 'Each line item must have a description.'],
        trim: true,
    },
    quantity: {
        type: Number,
        required: [true, 'Quantity is required.'],
        default: 1,
    },
    unitPrice: {
        type: Number,
        required: [true, 'Unit price is required.'],
    },
});


const invoiceSchema = new mongoose.Schema(
    {
        // --- Core Invoice Details ---
        invoiceNumber: {
            type: String,
            required: true,
            unique: true,
            trim: true,
        },
        issueDate: {
            type: Date,
            required: true,
            default: Date.now,
        },
        dueDate: {
            type: Date,
            required: true,
        },

        // --- Relationships ---
        client: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'Client',
            required: true,
        },
        document: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'Document',
            required: true,
        },

        // --- Financials ---
        lineItems: [lineItemSchema], // An array of line items based on the sub-schema
        subtotal: {
            type: Number,
            required: true,
        },
        tax: {
            type: Number,
            required: true,
            default: 0,
        },
        total: {
            type: Number,
            required: true,
        },

        // --- Status ---
        status: {
            type: String,
            enum: ['Draft', 'Sent', 'Paid', 'Overdue', 'Cancelled'],
            default: 'Draft',
        },
        notes: {
            type: String,
            trim: true,
        },
    },
    {
        timestamps: true, // Adds createdAt and updatedAt
    }
);

const Invoice = mongoose.model('Invoice', invoiceSchema);

module.exports = Invoice;
