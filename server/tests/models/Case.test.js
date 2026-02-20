jest.unmock('mongoose');
const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');
const Case = require('../../models/Case');

describe('Case Model Comprehensive Tests', () => {
    let mongoServer;

    beforeAll(async () => {
        mongoServer = await MongoMemoryServer.create();
        await mongoose.connect(mongoServer.getUri());
    });

    afterAll(async () => {
        await mongoose.disconnect();
        await mongoServer.stop();
    });

    afterEach(async () => {
        await Case.deleteMany({});
    });

    test('Forensic Integrity: Model should be a function', () => {
        expect(typeof Case).toBe('function');
    });

    test('Production Scenario: Create and Add PAIA', async () => {
        const doc = await Case.create({
            tenantId: 'tenant_12345678',
            caseNumber: 'VALID-' + Date.now(),
            title: 'Audit Case',
            client: { name: 'Test Client' },
            audit: { createdBy: new mongoose.mongo.ObjectId() }
        });

        const result = await Case.addPaiaRequest(doc._id, {
            statutoryDeadline: new Date(Date.now() + 1000000)
        });
        expect(result.success).toBe(true);
    });
});
