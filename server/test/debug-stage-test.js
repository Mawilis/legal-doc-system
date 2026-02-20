/* eslint-env mocha, node */
const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');
const assert = require('assert');

describe('🔍 Stage Advancement Debug', function() {
    let mongoServer;
    let OnboardingSession;

    before(async function() {
        mongoServer = await MongoMemoryServer.create();
        const uri = mongoServer.getUri();
        await mongoose.connect(uri);
        OnboardingSession = require('../models/OnboardingSession');
    });

    after(async function() {
        await mongoose.disconnect();
        await mongoServer.stop();
    });

    it('should show what happens during stage advancement', async function() {
        const sessionId = OnboardingSession.generateSessionId('INDIVIDUAL', 'tenant-1');
        
        const session = new OnboardingSession({
            sessionId: sessionId,
            tenantId: 'tenant-1',
            clientType: 'INDIVIDUAL',
            identityType: 'SA_ID',
            idNumber: '8001015009081',
            clientData: {
                firstName: 'Debug',
                lastName: 'Test',
                dateOfBirth: '1980-01-01',
                nationality: 'South African'
            },
            metadata: { createdBy: 'test' }
        });

        console.log('1. Initial stages:', session.stages ? session.stages.length : 0);
        await session.save();
        console.log('2. After save stages:', session.stages.length);
        
        await session.advanceStage('CLIENT_INFO', { test: 'data' }, 'tester');
        console.log('3. After advanceStage stages:', session.stages.length);
        console.log('4. Current stage:', session.currentStage);
        
        assert.strictEqual(session.stages.length, 2);
    });
});
