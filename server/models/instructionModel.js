// server/models/instructionModel.js

const mongoose = require('mongoose');
const Document = require('./documentModel'); // We might need this for middleware later
const logger = require('../utils/logger');

const instructionSchema = new mongoose.Schema(
    {
        // --- Core Relationships ---
        // This instruction must be linked to a specific document.
        document: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'Document',
            required: [true, 'An instruction must be linked to a document.'],
        },
        // The attorney or user who created this instruction.
        createdBy: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'User',
            required: [true, 'An instruction must have a creator.'],
        },
        // The deputy (who is also a user) assigned to carry out the instruction.
        assignedTo: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'User',
            required: [true, 'An instruction must be assigned to a deputy.'],
        },

        // --- Instruction Details ---
        serviceType: {
            type: String,
            required: true,
            enum: ['Normal', 'Urgent'],
            default: 'Normal',
        },
        specialInstructions: {
            type: String,
            trim: true,
            default: '',
        },

        // --- Status & Workflow ---
        status: {
            type: String,
            enum: ['Pending', 'Acknowledged', 'In Progress', 'Completed', 'Cancelled'],
            default: 'Pending',
        },

        // --- Financials ---
        // A field to store a quotation if one was requested before service.
        quotationAmount: {
            type: Number,
            default: null,
        },
    },
    {
        // Automatically add `createdAt` and `updatedAt` timestamps.
        timestamps: true,
    }
);

// --- Mongoose Middleware to update the corresponding Document ---
// This hook runs automatically *after* an instruction is successfully saved.
instructionSchema.post('save', async function (doc, next) {
    // `doc` is the instruction that was just saved.
    // We want to automatically update the related document to link back to this instruction
    // and set its status to "Assigned". This keeps our data in sync.
    try {
        await Document.findByIdAndUpdate(doc.document, {
            status: 'Assigned',
            assignedTo: doc.assignedTo,
            // You could also add a history entry here if needed.
        });
        logger.info(`Associated document ${doc.document} updated successfully after instruction creation.`);
    } catch (error) {
        logger.error(`Failed to update associated document for instruction ${doc._id}: ${error.message}`);
        // In a production app, you might want to handle this error more gracefully,
        // perhaps by queuing a retry or sending an alert.
    }
    next();
});


const Instruction = mongoose.model('Instruction', instructionSchema);

module.exports = Instruction;
