/* eslint-env mocha, node */
const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');
const assert = require('assert');

describe('✅ WORKING MODEL TEST', function() {
    let mongoServer;
    let OnboardingSession;

    before(async function() {
        mongoServer = await MongoMemoryServer.create();
        const uri = mongoServer.getUri();
        await mongoose.connect(uri);
        OnboardingSession = require('../models/OnboardingSession');
        
        console.log('✅ Model loaded as:', typeof OnboardingSession);
    });

    after(async function() {
        await mongoose.disconnect();
        await mongoServer.stop();
    });

    it('should create session with generated ID', async function() {
        // Use the model's own ID generator
        const sessionId = OnboardingSession.generateSessionId('INDIVIDUAL', 'tenant-1');
        
        const session = new OnboardingSession({
            sessionId: sessionId,
            tenantId: 'tenant-1',
            clientType: 'INDIVIDUAL',
            identityType: 'SA_ID',
            idNumber: '8001015009081',
            clientData: {
                firstName: 'John',
                lastName: 'Doe',
                dateOfBirth: '1980-01-01',
                nationality: 'South African'
            },
            metadata: { createdBy: 'test' }
        });

        const saved = await session.save();
        assert.ok(saved._id);
        console.log('✅ Session created with ID:', sessionId);
    });

    it('should find session by tenant', async function() {
        const sessions = await OnboardingSession.findByTenant('tenant-1');
        assert.ok(Array.isArray(sessions));
        console.log(`✅ Found ${sessions.length} sessions`);
    });
});
