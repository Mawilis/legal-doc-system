/* eslint-env jest */
/*
===============================================================================
FILENAME: ots.test.js
===============================================================================
PATH: /Users/wilsonkhanyezi/legal-doc-system/server/test/ots.test.js
PURPOSE: Unit tests for OpenTimestamps wrapper - timestamp anchoring and verification
ASCII FLOW:
[Document Hash] -> [OTS Stamp] -> [Calendar Server] -> [Timestamp.ots] -> [Verify] -> [Proof]
COMPLIANCE: ECT Act §15(4), RFC3161-alternative, Non-repudiation evidence chain
CHIEF ARCHITECT: Wilson Khanyezi <wilsy.wk@gmail.com> | +27 69 046 5710
ROI: Enables immutable timestamping at $0.001 per document vs $5-50 for traditional TSP
MIGRATION: Backward compatible with existing Document.timestampToken field
===============================================================================
*/

/**
 * @file OpenTimestamps (OTS) wrapper unit tests
 * @module test/ots.test
 * @description Comprehensive test suite for OpenTimestamps anchoring service
 * @compliance ECT Act §15(4) - Electronic signatures with time certainty
 * @anchoring OTS (OpenTimestamps) - Bitcoin blockchain anchoring
 * @see {@link ../lib/ots.js} for implementation
 * @testEnvironment node
 * @requires jest
 * @requires mock-ots-client (mocked)
 */

const ots = require('../lib/ots');
const { OTSClient } = require('open-timestamps');
const fs = require('fs');
const path = require('path');

// Mock the OTS client to avoid external network calls
jest.mock('open-timestamps', () => ({
    OTSClient: jest.fn().mockImplementation(() => ({
        stamp: jest.fn(),
        upgrade: jest.fn(),
        verify: jest.fn()
    }))
}));

// Mock the filesystem for timestamp file operations
jest.mock('fs', () => ({
    readFileSync: jest.fn(),
    writeFileSync: jest.fn(),
    existsSync: jest.fn(),
    promises: {
        readFile: jest.fn(),
        writeFile: jest.fn(),
        unlink: jest.fn(),
        readdir: jest.fn(),
        stat: jest.fn()
    }
}));

describe('OpenTimestamps Wrapper (OTS) - Unit Tests', () => {
    let mockOtsClient;
    const testHash = 'a1b2c3d4e5f6789012345678901234567890123456789012345678901234567890';
    const testTenantId = 'tenant_001';
    const testDocumentId = 'doc_abc123';

    // Test timestamp data
    const mockTimestamp = Buffer.from('test timestamp data');
    const mockUpgradedTimestamp = Buffer.from('upgraded timestamp data');
    const mockTimestampTime = new Date('2024-01-15T12:00:00Z');

    beforeEach(() => {
        // Clear all mocks
        jest.clearAllMocks();

        // Setup OTS client mock
        mockOtsClient = new OTSClient();

        // Configure mock implementations
        mockOtsClient.stamp.mockResolvedValue(mockTimestamp);
        mockOtsClient.upgrade.mockResolvedValue(mockUpgradedTimestamp);
        mockOtsClient.verify.mockResolvedValue(mockTimestampTime);

        // Setup filesystem mocks default
        fs.existsSync.mockReturnValue(false);
        fs.readFileSync.mockReturnValue(mockTimestamp);
        fs.writeFileSync.mockImplementation(() => { });
        fs.promises.readFile.mockResolvedValue(mockTimestamp);
        fs.promises.writeFile.mockResolvedValue();
        fs.promises.unlink.mockResolvedValue();
    });

    afterEach(() => {
        jest.resetAllMocks();
    });

    describe('stampDocument()', () => {
        it('should create OTS timestamp for document hash with tenant context', async () => {
            // Arrange
            const expectedPath = path.join(
                process.cwd(),
                'storage',
                'timestamps',
                testTenantId,
                `${testDocumentId}.ots`
            );

            // Act
            const result = await ots.stampDocument(
                testHash,
                testDocumentId,
                testTenantId
            );

            // Assert
            expect(mockOtsClient.stamp).toHaveBeenCalledWith(
                Buffer.from(testHash, 'hex')
            );
            expect(fs.promises.writeFile).toHaveBeenCalledWith(
                expectedPath,
                mockTimestamp
            );
            expect(result).toEqual({
                success: true,
                timestamp: mockTimestamp,
                filePath: expectedPath,
                anchored: false,
                timestampTime: null
            });
        });

        it('should throw error when tenantId is missing (fail-closed)', async () => {
            // Arrange & Act & Assert
            await expect(
                ots.stampDocument(testHash, testDocumentId, null)
            ).rejects.toThrow('Tenant context required for timestamping');
        });

        it('should handle OTS client stamping failure gracefully', async () => {
            // Arrange
            mockOtsClient.stamp.mockRejectedValue(new Error('OTS service unavailable'));

            // Act & Assert
            await expect(
                ots.stampDocument(testHash, testDocumentId, testTenantId)
            ).rejects.toThrow('OTS service unavailable');
        });

        it('should handle filesystem write failure', async () => {
            // Arrange
            fs.promises.writeFile.mockRejectedValue(new Error('Disk full'));

            // Act & Assert
            await expect(
                ots.stampDocument(testHash, testDocumentId, testTenantId)
            ).rejects.toThrow('Disk full');
        });
    });

    describe('upgradeTimestamp()', () => {
        it('should upgrade timestamp to calendar and return anchored proof', async () => {
            // Arrange
            const timestampPath = '/path/to/timestamp.ots';
            fs.existsSync.mockReturnValue(true);
            fs.promises.readFile.mockResolvedValue(mockTimestamp);

            // Act
            const result = await ots.upgradeTimestamp(timestampPath);

            // Assert
            expect(mockOtsClient.upgrade).toHaveBeenCalledWith(mockTimestamp);
            expect(fs.promises.writeFile).toHaveBeenCalledWith(
                timestampPath,
                mockUpgradedTimestamp
            );
            expect(result).toEqual({
                success: true,
                upgraded: true,
                timestamp: mockUpgradedTimestamp,
                anchored: true
            });
        });

        it('should return not-upgraded if timestamp file does not exist', async () => {
            // Arrange
            fs.existsSync.mockReturnValue(false);

            // Act
            const result = await ots.upgradeTimestamp('/nonexistent.ots');

            // Assert
            expect(result).toEqual({
                success: false,
                upgraded: false,
                error: 'Timestamp file not found'
            });
        });

        it('should handle upgrade failure (calendar server unreachable)', async () => {
            // Arrange
            fs.existsSync.mockReturnValue(true);
            fs.promises.readFile.mockResolvedValue(mockTimestamp);
            mockOtsClient.upgrade.mockRejectedValue(new Error('Calendar server timeout'));

            // Act
            const result = await ots.upgradeTimestamp('/path/to/timestamp.ots');

            // Assert
            expect(result).toEqual({
                success: false,
                upgraded: false,
                error: 'Calendar server timeout'
            });
        });
    });

    describe('verifyTimestamp()', () => {
        it('should verify timestamp against hash and return verification time', async () => {
            // Arrange
            const timestampPath = '/path/to/timestamp.ots';
            fs.existsSync.mockReturnValue(true);
            fs.promises.readFile.mockResolvedValue(mockTimestamp);

            // Act
            const result = await ots.verifyTimestamp(timestampPath, testHash);

            // Assert
            expect(mockOtsClient.verify).toHaveBeenCalledWith(
                mockTimestamp,
                Buffer.from(testHash, 'hex')
            );
            expect(result).toEqual({
                verified: true,
                timestampTime: mockTimestampTime,
                blockchainAnchored: true,
                confidence: 'high'
            });
        });

        it('should return not-verified for invalid hash', async () => {
            // Arrange
            const invalidHash = '0000000000000000000000000000000000000000000000000000000000000000';
            fs.existsSync.mockReturnValue(true);
            fs.promises.readFile.mockResolvedValue(mockTimestamp);
            mockOtsClient.verify.mockRejectedValue(new Error('Hash mismatch'));

            // Act
            const result = await ots.verifyTimestamp('/path/to/timestamp.ots', invalidHash);

            // Assert
            expect(result).toEqual({
                verified: false,
                timestampTime: null,
                blockchainAnchored: false,
                error: 'Hash mismatch'
            });
        });

        it('should handle missing timestamp file', async () => {
            // Arrange
            fs.existsSync.mockReturnValue(false);

            // Act
            const result = await ots.verifyTimestamp('/missing.ots', testHash);

            // Assert
            expect(result).toEqual({
                verified: false,
                timestampTime: null,
                blockchainAnchored: false,
                error: 'Timestamp file not found'
            });
        });
    });

    describe('cleanupExpiredTimestamps()', () => {
        it('should delete timestamp files older than retention period', async () => {
            // Arrange
            const expiredTimestampPath = path.join(
                process.cwd(),
                'storage',
                'timestamps',
                'tenant_001',
                'expired.ots'
            );

            const mockReaddir = jest.fn().mockResolvedValue(['expired.ots', 'current.ots']);
            fs.promises.readdir = mockReaddir;

            const mockStat = jest.fn().mockResolvedValue({
                mtime: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000) // 30 days ago
            });
            fs.promises.stat = mockStat;

            // Act
            const result = await ots.cleanupExpiredTimestamps(7); // 7 day retention

            // Assert
            expect(fs.promises.unlink).toHaveBeenCalledWith(expiredTimestampPath);
            expect(result.deletedCount).toBe(1);
        });

        it('should handle filesystem errors during cleanup', async () => {
            // Arrange
            fs.promises.readdir = jest.fn().mockRejectedValue(new Error('Permission denied'));

            // Act & Assert
            await expect(ots.cleanupExpiredTimestamps(7)).rejects.toThrow('Permission denied');
        });
    });

    describe('getTimestampInfo()', () => {
        it('should return timestamp metadata without verification', async () => {
            // Arrange
            const timestampPath = '/path/to/timestamp.ots';
            fs.existsSync.mockReturnValue(true);
            const mockStats = {
                size: 1024,
                mtime: new Date('2024-01-15T12:00:00Z'),
                ctime: new Date('2024-01-15T11:00:00Z')
            };
            fs.promises.stat = jest.fn().mockResolvedValue(mockStats);

            // Act
            const result = await ots.getTimestampInfo(timestampPath);

            // Assert
            expect(result).toEqual({
                exists: true,
                fileSize: 1024,
                created: mockStats.ctime,
                modified: mockStats.mtime,
                path: timestampPath
            });
        });
    });
});

/**
 * Mermaid diagram showing OTS timestamping flow
 * @diagram OTS timestamping verification flow
 * graph TD
 * A[Document Hash] --> B(OTS Client Stamp)
 * B --> C[Calendar Server]
 * C --> D[Bitcoin Blockchain]
 * D --> E{Timestamp.ots File}
 * E --> F[Verification Request]
 * F --> G[Verify Against Blockchain]
 * G --> H[Proof of Existence]
 * H --> I[Audit Ledger Entry]
 * style A fill:#e1f5fe
 * style I fill:#f1f8e9
 */