/**
 * @jest-environment node
 */
'use strict';

// Force Jest to give us the raw module
jest.deepUnmock('mongoose');
jest.deepUnmock('../../models/OnboardingSession');

const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');
const OnboardingSession = require('../../models/OnboardingSession');

describe('🏛️ SOVEREIGN SHIELD - Model Validation', () => {
    let mongoServer;

    beforeAll(async () => {
        mongoServer = await MongoMemoryServer.create();
        const uri = mongoServer.getUri();
        await mongoose.connect(uri);
        console.log('✅ Test database connected');
    });

    afterAll(async () => {
        await mongoose.disconnect();
        await mongoServer.stop();
        console.log('✅ Test database disconnected');
    });

    test('Model is constructor function', () => {
        console.log('Model type:', typeof OnboardingSession);
        expect(typeof OnboardingSession).toBe('function');
        expect(OnboardingSession.prototype).toBeDefined();
    });

    test('Can create session', async () => {
        const session = new OnboardingSession({
            sessionId: 'ONB_IND_20250218120000_TEST_tenant-1',
            tenantId: 'tenant-1',
            clientType: 'INDIVIDUAL',
            clientData: { firstName: 'Test', lastName: 'User' },
            metadata: { createdBy: 'test' }
        });

        const saved = await session.save();
        expect(saved.sessionId).toBeDefined();
        expect(saved.tenantId).toBe('tenant-1');
        console.log('✅ Session created successfully');
    });
});
