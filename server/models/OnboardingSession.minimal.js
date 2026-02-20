'use strict';

const mongoose = require('mongoose');

const onboardingSessionSchema = new mongoose.Schema({
    sessionId: { type: String, required: true, unique: true },
    tenantId: { type: String, required: true },
    clientType: { type: String, required: true },
    clientData: { type: 'Mixed', required: true },
    metadata: {
        createdBy: { type: String, required: true },
        createdAt: { type: Date, default: Date.now }
    }
});

// Force export as constructor
const Model = mongoose.model('OnboardingSessionMinimal', onboardingSessionSchema);
module.exports = Model;
