/**
 * @jest-environment node
 */
'use strict';

const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');

describe('🏛️ WORKING MODEL TEST', () => {
    let mongoServer;
    let OnboardingSession;

    beforeAll(async () => {
        mongoServer = await MongoMemoryServer.create();
        const uri = mongoServer.getUri();
        await mongoose.connect(uri);
        
        // Load model with fallback to mongoose.models
        try {
            OnboardingSession = require('../../models/OnboardingSession');
            if (typeof OnboardingSession !== 'function' && mongoose.models.OnboardingSession) {
                OnboardingSession = mongoose.models.OnboardingSession;
            }
        } catch (error) {
            OnboardingSession = mongoose.models.OnboardingSession;
        }
        
        console.log('✅ Database connected');
        console.log('📊 Final model type:', typeof OnboardingSession);
    });

    afterAll(async () => {
        await mongoose.disconnect();
        await mongoServer.stop();
    });

    afterEach(async () => {
        if (OnboardingSession && typeof OnboardingSession.deleteMany === 'function') {
            await OnboardingSession.deleteMany({});
        }
    });

    test('Model should be a constructor', () => {
        expect(typeof OnboardingSession).toBe('function');
    });

    test('Should create session with minimal data', async () => {
        const session = new OnboardingSession({
            sessionId: 'ONB_IND_20250218120000_TEST_tenant-1',
            tenantId: 'tenant-1',
            clientType: 'INDIVIDUAL',
            clientData: { firstName: 'Test' },
            metadata: { createdBy: 'test' }
        });

        const saved = await session.save();
        expect(saved.sessionId).toBeDefined();
        console.log('✅ Session created');
    });
});
