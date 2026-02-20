/**
 * @jest-environment node
 */
'use strict';

const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');

describe('🔧 DIRECT MODEL ACCESS TEST', () => {
    let mongoServer;
    let connection;
    let OnboardingSession;

    beforeAll(async () => {
        mongoServer = await MongoMemoryServer.create();
        const uri = mongoServer.getUri();
        await mongoose.connect(uri);
        connection = mongoose.connection;
        
        // Load model but also keep reference to mongoose.models
        OnboardingSession = require('../../models/OnboardingSession');
        
        console.log('✅ Database connected');
        console.log('📊 Direct import type:', typeof OnboardingSession);
        console.log('📊 Mongoose models:', Object.keys(mongoose.models));
        
        // If direct import is object but model exists in registry, use that
        if (typeof OnboardingSession !== 'function' && mongoose.models.OnboardingSession) {
            console.log('⚠️ Using model from mongoose.models instead');
            OnboardingSession = mongoose.models.OnboardingSession;
        }
    });

    afterAll(async () => {
        await mongoose.disconnect();
        await mongoServer.stop();
    });

    test('Model should be accessible', () => {
        expect(OnboardingSession).toBeDefined();
    });

    test('Should be able to create instance via mongoose.models', () => {
        // Try to get model from registry if needed
        const Model = typeof OnboardingSession === 'function' 
            ? OnboardingSession 
            : mongoose.models.OnboardingSession;
            
        expect(Model).toBeDefined();
        
        // In Mongoose 8, we need to use the model differently
        const doc = new Model({
            sessionId: 'test-123',
            tenantId: 'tenant-1',
            clientType: 'INDIVIDUAL',
            clientData: { test: true },
            metadata: { createdBy: 'test' }
        });
        
        expect(doc).toBeDefined();
        console.log('✅ Successfully created instance');
    });
});
