const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');
const assert = require('assert');

describe('Model Test with Mocha', function() {
    let mongoServer;
    
    before(async function() {
        mongoServer = await MongoMemoryServer.create();
        const uri = mongoServer.getUri();
        await mongoose.connect(uri);
    });
    
    after(async function() {
        await mongoose.disconnect();
        await mongoServer.stop();
    });
    
    it('should load model as function', function() {
        const OnboardingSession = require('../models/OnboardingSession');
        assert.strictEqual(typeof OnboardingSession, 'function');
    });
});
