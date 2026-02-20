'use strict';

const mongoose = require('mongoose');

// Ultra-minimal schema
const onboardingSessionSchema = new mongoose.Schema({
    sessionId: { type: String, required: true, unique: true },
    tenantId: { type: String, required: true },
    clientType: { type: String, required: true, enum: ['INDIVIDUAL', 'COMPANY'] },
    clientData: { type: mongoose.Schema.Types.Mixed, required: true },
    metadata: {
        createdBy: { type: String, required: true },
        createdAt: { type: Date, default: Date.now }
    }
});

// Static method
onboardingSessionSchema.statics.createSession = async function(tenantId, data) {
    const session = new this({
        sessionId: `ONB_${Date.now()}`,
        tenantId,
        ...data
    });
    return await session.save();
};

// Create and export model
const OnboardingSession = mongoose.model('OnboardingSessionMinimal', onboardingSessionSchema);
module.exports = OnboardingSession;
