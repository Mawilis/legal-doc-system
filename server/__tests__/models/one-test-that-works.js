/**
 * @jest-environment node
 */
'use strict';

const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');

describe('✅ ONE TEST THAT WILL WORK', () => {
    let mongoServer;
    let OnboardingSession;

    beforeAll(async () => {
        mongoServer = await MongoMemoryServer.create();
        const uri = mongoServer.getUri();
        await mongoose.connect(uri);
        
        // Load the main model directly
        OnboardingSession = require('../../models/OnboardingSession');
        
        console.log('✅ Database connected');
        console.log('📊 Model type from require:', typeof OnboardingSession);
    });

    afterAll(async () => {
        await mongoose.disconnect();
        await mongoServer.stop();
    });

    test('Model is a function', () => {
        console.log('✅ Test running, model type:', typeof OnboardingSession);
        expect(typeof OnboardingSession).toBe('function');
    });

    test('Can create instance', () => {
        const session = new OnboardingSession({
            sessionId: 'ONB_IND_20250218120000_TEST_tenant-1',
            tenantId: 'tenant-1',
            clientType: 'INDIVIDUAL',
            clientData: { firstName: 'Test' },
            metadata: { createdBy: 'test' }
        });
        
        expect(session).toBeDefined();
        console.log('✅ Instance created');
    });

    test('Can save to database', async () => {
        const session = new OnboardingSession({
            sessionId: 'ONB_IND_20250218120000_TEST_tenant-1',
            tenantId: 'tenant-1',
            clientType: 'INDIVIDUAL',
            clientData: { firstName: 'Test' },
            metadata: { createdBy: 'test' }
        });

        const saved = await session.save();
        expect(saved._id).toBeDefined();
        console.log('✅ Saved to database');
    });
});
