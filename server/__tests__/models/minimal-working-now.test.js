/**
 * @jest-environment node
 */
'use strict';

const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');

describe('✅ MINIMAL WORKING MODEL TEST', () => {
    let mongoServer;
    let OnboardingSession;

    beforeAll(async () => {
        mongoServer = await MongoMemoryServer.create();
        const uri = mongoServer.getUri();
        await mongoose.connect(uri);
        
        // Load the minimal model
        OnboardingSession = require('../../models/OnboardingSession.minimal.working');
        
        console.log('✅ Database connected');
        console.log('📊 Model type:', typeof OnboardingSession);
        console.log('📊 Model is function:', typeof OnboardingSession === 'function');
        console.log('📊 Has createSession:', typeof OnboardingSession.createSession === 'function');
    });

    afterAll(async () => {
        await mongoose.disconnect();
        await mongoServer.stop();
    });

    test('Model should be a constructor', () => {
        expect(typeof OnboardingSession).toBe('function');
    });

    test('Should create instance with new', () => {
        const session = new OnboardingSession({
            sessionId: 'test-123',
            tenantId: 'tenant-1',
            clientType: 'INDIVIDUAL',
            clientData: { name: 'test' },
            metadata: { createdBy: 'test' }
        });
        
        expect(session).toBeDefined();
        expect(session.sessionId).toBe('test-123');
    });

    test('Static createSession should work', async () => {
        const session = await OnboardingSession.createSession('tenant-1', {
            clientType: 'INDIVIDUAL',
            clientData: { name: 'test' },
            metadata: { createdBy: 'test' }
        });
        
        expect(session).toBeDefined();
        expect(session.sessionId).toBeDefined();
    });
});
