#!/bin/bash
TEST_PATH="/Users/wilsonkhanyezi/legal-doc-system/server/tests/models/Case.test.js"

cat << 'INNER_EOF' > "$TEST_PATH"
const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');

describe('Case Model Comprehensive Tests', () => {
    let mongoServer;
    let Case;

    // Helper to generate IDs safely across Mongoose versions
    const generateId = () => new mongoose.Types.ObjectId();

    beforeAll(async () => {
        mongoServer = await MongoMemoryServer.create();
        const uri = mongoServer.getUri();
        await mongoose.connect(uri);
        Case = require('../../models/Case');
    });

    afterAll(async () => {
        await mongoose.disconnect();
        await mongoServer.stop();
    });

    afterEach(async () => {
        if (Case) await Case.deleteMany({});
    });

    test('Schema Validation: should validate a valid case document', async () => {
        const validCase = new Case({
            tenantId: 'tenant_12345678',
            caseNumber: 'AB-2023-0001',
            title: 'Test Case',
            client: { name: 'Test Client' },
            audit: { createdBy: generateId() }
        });
        const saved = await validCase.save();
        expect(saved._id).toBeDefined();
    });

    test('Static Methods: should add PAIA request', async () => {
        const caseDoc = await new Case({
            tenantId: 'tenant_12345678',
            caseNumber: 'AB-2023-0002',
            title: 'Test Case',
            client: { name: 'Test Client' },
            audit: { createdBy: generateId() }
        }).save();

        const paiaData = {
            statutoryDeadline: new Date(Date.now() + 1000000),
            audit: { createdBy: generateId() }
        };

        const result = await Case.addPaiaRequest(caseDoc._id, paiaData);
        expect(result.success).toBe(true);
        expect(result.requestId).toBeDefined();
    });
});
INNER_EOF

echo "✅ Case.test.js updated with safe ID generation."
