/**
 * @jest-environment node
 */
'use strict';

jest.unmock('mongoose');
const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');

describe('Model Validation', () => {
    let mongoServer;

    beforeAll(async () => {
        mongoServer = await MongoMemoryServer.create();
        const uri = mongoServer.getUri();
        await mongoose.connect(uri);
    });

    afterAll(async () => {
        await mongoose.disconnect();
        await mongoServer.stop();
    });

    test('OnboardingSession model loads', () => {
        const OnboardingSession = require('../../models/OnboardingSession');
        expect(OnboardingSession).toBeDefined();
        expect(typeof OnboardingSession).toBe('function');
        console.log('✅ Model loaded successfully');
    });
});
