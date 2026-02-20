/* eslint-env mocha, node */
const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');
const assert = require('assert');

describe('Simple Test', function() {
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

    it('should load model as function', function() {
        assert.strictEqual(typeof OnboardingSession, 'function');
    });

    it('should create instance', function() {
        const session = new OnboardingSession({
            sessionId: 'ONB_IND_TEST_001',
            tenantId: 'tenant-1',
            clientType: 'INDIVIDUAL',
            identityType: 'SA_ID',
            idNumber: '8001015009081',
            clientData: {
                firstName: 'Test',
                lastName: 'User',
                dateOfBirth: '1980-01-01',
                nationality: 'South African'
            },
            metadata: { createdBy: 'test' }
        });
        assert.ok(session);
    });
});
