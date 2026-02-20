const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');

describe('Wilsy OS - OnboardingSession Integrity', () => {
    let mongoServer;
    let OnboardingSession;

    beforeAll(async () => {
        mongoServer = await MongoMemoryServer.create();
        await mongoose.connect(mongoServer.getUri());
        
        // Clear Mongoose internal cache to prevent zombie models
        delete mongoose.models.OnboardingSession;
        
        // Force fresh require
        const modelPath = '../../models/OnboardingSession';
        delete require.cache[require.resolve(modelPath)];
        OnboardingSession = require(modelPath);
    });

    afterAll(async () => {
        await mongoose.disconnect();
        await mongoServer.stop();
    });

    test('Should verify constructor and advance stage', async () => {
        expect(typeof OnboardingSession).toBe('function');

        const session = new OnboardingSession({
            tenantId: 'ten_abc',
            sessionId: 'ONB_' + Date.now()
        });

        const saved = await session.save();
        await saved.advanceStage('IDENTITY_VERIFIED');
        expect(saved.stages.length).toBe(1);
    });
});
