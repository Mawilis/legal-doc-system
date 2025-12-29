const mongoose = require('mongoose');

const DispatchInstructionSchema = new mongoose.Schema({
    title: { type: String, required: true },
    documentCode: { type: String, required: true },
    caseNumber: { type: String, required: true },
    court: { type: String, required: true },
    classification: { type: String, default: 'LITIGATION' },
    
    plaintiff: String,
    defendant: String,

    serviceType: { type: String, required: true },
    serviceAddress: { type: String, required: true },
    urgency: { type: String, required: true },
    distanceKm: Number,

    attemptPlan: {
        minAttempts: Number,
        window: String
    },
    
    pricingPreview: {
        base: Number,
        travel: Number,
        vat: Number,
        total: Number
    },

    // Dynamic Fields
    urgentReason: String,
    ruleReference: String,
    securityPlan: String,
    warehouseProvider: String,

    // Flags
    afterHours: Boolean,
    locksmith: Boolean,
    security: Boolean,
    transport: Boolean,

    status: { type: String, default: 'Pending Dispatch' }
}, { timestamps: true });

module.exports = mongoose.model('DispatchInstruction', DispatchInstructionSchema);
