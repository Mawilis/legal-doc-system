/**
 * @jest-environment node
 */
'use strict';

const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');
const modelLoader = require('../helpers/modelLoader');

describe('🔧 MINIMAL WORKING TEST - Model Loading Verification', () => {
    let mongoServer;
    let OnboardingSession;

    beforeAll(async () => {
        // Setup database
        mongoServer = await MongoMemoryServer.create();
        const uri = mongoServer.getUri();
        await mongoose.connect(uri);
        
        // Load model using helper
        OnboardingSession = await modelLoader.loadModel(
            'OnboardingSession', 
            'models/OnboardingSession.js'
        );
        
        console.log('✅ Model loaded, type:', typeof OnboardingSession);
    });

    afterAll(async () => {
        await mongoose.disconnect();
        await mongoServer.stop();
        modelLoader.reset();
    });

    test('Model should be a constructor function', () => {
        expect(typeof OnboardingSession).toBe('function');
        expect(OnboardingSession.prototype).toBeDefined();
    });

    test('Should be able to create instance with new', () => {
        const session = new OnboardingSession({
            sessionId: 'ONB_IND_20250218120000_TEST_tenant-1',
            tenantId: 'tenant-1',
            clientType: 'INDIVIDUAL',
            clientData: { firstName: 'Test' },
            metadata: { createdBy: 'test' }
        });
        
        expect(session).toBeDefined();
        expect(session.sessionId).toBe('ONB_IND_20250218120000_TEST_tenant-1');
    });

    test('Static method createSession should exist', () => {
        expect(typeof OnboardingSession.createSession).toBe('function');
    });
});
