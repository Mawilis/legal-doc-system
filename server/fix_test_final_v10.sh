#!/bin/bash
TEST_PATH="/Users/wilsonkhanyezi/legal-doc-system/server/tests/models/Case.test.js"

cat << 'INNER_EOF' > "$TEST_PATH"
const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');
// PRO-ENGINEER MOVE: Load at top level to ensure constructor visibility
const Case = require('../../models/Case');

describe('Case Model Comprehensive Tests', () => {
    let mongoServer;

    // Direct driver access for IDs
    const generateId = () => new mongoose.mongo.ObjectId();

    beforeAll(async () => {
        mongoServer = await MongoMemoryServer.create();
        const uri = mongoServer.getUri();
        if (mongoose.connection.readyState === 0) {
            await mongoose.connect(uri);
        }
    });

    afterAll(async () => {
        await mongoose.disconnect();
        await mongoServer.stop();
    });

    afterEach(async () => {
        await Case.deleteMany({});
    });

    test('Schema Validation: should validate a valid case document', async () => {
        // Validation: Verify Case is a constructor before proceeding
        expect(typeof Case).toBe('function');

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
        const caseDoc = await Case.create({
            tenantId: 'tenant_12345678',
            caseNumber: 'AB-2023-0002',
            title: 'Test Case',
            client: { name: 'Test Client' },
            audit: { createdBy: generateId() }
        });

        const paiaData = {
            statutoryDeadline: new Date(Date.now() + 1000000),
            audit: { createdBy: generateId() }
        };

        const result = await Case.addPaiaRequest(caseDoc._id, paiaData);
        expect(result.success).toBe(true);
    });
});
INNER_EOF

echo "✅ Case.test.js updated with Immutable Constructor logic."
