'use strict';
const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');

describe('Debug Model Registration', () => {
    let mongoServer;

    beforeAll(async () => {
        mongoServer = await MongoMemoryServer.create();
        const uri = mongoServer.getUri();
        await mongoose.connect(uri);
        console.log('✅ MongoDB connected');
    });

    afterAll(async () => {
        await mongoose.disconnect();
        await mongoServer.stop();
    });

    test('models should register', () => {
        console.log('Before require - models:', Object.keys(mongoose.models));
        
        const Session = require('../../models/OnboardingSession');
        console.log('After Session require - models:', Object.keys(mongoose.models));
        console.log('Session model type:', typeof Session);
        console.log('Session model name:', Session?.modelName);
        
        const Document = require('../../models/OnboardingDocument');
        console.log('After Document require - models:', Object.keys(mongoose.models));
        console.log('Document model type:', typeof Document);
        console.log('Document model name:', Document?.modelName);
        
        expect(Object.keys(mongoose.models).length).toBeGreaterThan(0);
    });
});
