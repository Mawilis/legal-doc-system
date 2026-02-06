/* eslint-env jest */
/*
===============================================================================
FILENAME: ots.integration.test.js
===============================================================================
PATH: /server/test/ots.integration.test.js
PURPOSE: Integration tests for OpenTimestamps - Full lifecycle verification
ASCII FLOW:
[Real File] -> [SHA256] -> [OTS Stamp] -> [Verify Mock] -> [Success]
COMPLIANCE: ECT Act §15(4) Proof of Integrity
===============================================================================
*/

const ots = require('../lib/ots');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// INTEGRATION MOCKING STRATEGY:
// 1. Filesystem: REAL (We want to verify folders/files are actually created)
// 2. Network/Blockchain: MOCKED (We don't want to hit real Bitcoin servers during test)
jest.mock('open-timestamps', () => ({
  OTSClient: jest.fn().mockImplementation(() => ({
    stamp: jest.fn().mockResolvedValue(Buffer.from('MOCK_OTS_PROOF_DATA')),
    upgrade: jest.fn().mockResolvedValue(Buffer.from('MOCK_UPGRADED_PROOF')),
    verify: jest.fn().mockResolvedValue(new Date()) // Returns verification time
  }))
}));

describe('OTS Integration: Full Lifecycle', () => {
    const testTenantId = 'integration_tenant';
    const testDocId = 'contract_final_v1';
    const storageDir = path.join(process.cwd(), 'storage', 'timestamps', testTenantId);
    
    // Create a dummy contract file to hash
    const contractContent = 'This is a legally binding contract signed on 2026-02-01';
    const contractHash = crypto.createHash('sha256').update(contractContent).digest('hex');

    beforeAll(async () => {
        // Ensure clean slate before starting
        if (fs.existsSync(storageDir)) {
            fs.rmSync(storageDir, { recursive: true, force: true });
        }
    });

    afterAll(async () => {
        // Cleanup artifacts after tests
        if (fs.existsSync(storageDir)) {
            fs.rmSync(storageDir, { recursive: true, force: true });
        }
    });

    test('Step 1: Anchor Document to Blockchain (Simulation)', async () => {
        // 1. Stamp the document hash
        const result = await ots.stampDocument(contractHash, testDocId, testTenantId);

        // 2. Verify success response
        expect(result.success).toBe(true);
        expect(result.filePath).toContain(testDocId);

        // 3. CRITICAL: Verify physical file creation on disk
        const fileExists = fs.existsSync(result.filePath);
        expect(fileExists).toBe(true);
    });

    test('Step 2: Upgrade Timestamp (Calendar Server)', async () => {
        const timestampPath = path.join(storageDir, `${testDocId}.ots`);
        
        // 1. Request upgrade
        const result = await ots.upgradeTimestamp(timestampPath);

        // 2. Verify upgrade logic
        expect(result.success).toBe(true);
        expect(result.anchored).toBe(true);
        expect(result.upgraded).toBe(true);
    });

    test('Step 3: Verify Timestamp Integrity', async () => {
        const timestampPath = path.join(storageDir, `${testDocId}.ots`);

        // 1. Verify using the original hash
        const result = await ots.verifyTimestamp(timestampPath, contractHash);

        // 2. Assert verification success
        expect(result.verified).toBe(true);
        expect(result.blockchainAnchored).toBe(true);
        expect(result.confidence).toBe('high');
    });

    test('Step 4: Detect Tampering (Security Check)', async () => {
        const timestampPath = path.join(storageDir, `${testDocId}.ots`);
        
        // 1. Generate a different hash (simulating modified document)
        const tamperedContent = 'This contract was altered by a hacker.';
        const tamperedHash = crypto.createHash('sha256').update(tamperedContent).digest('hex');

        // 2. Mock a verification failure just for this test
        const { OTSClient } = require('open-timestamps');
        const mockClient = new OTSClient();
        mockClient.verify.mockRejectedValueOnce(new Error('Hash mismatch'));

        // 3. Attempt verification
        const result = await ots.verifyTimestamp(timestampPath, tamperedHash);

        // 4. Expect failure (which is a SUCCESS for security)
        expect(result.verified).toBe(false);
        expect(result.error).toBeDefined();
    });
});
