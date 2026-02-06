/* eslint-disable no-undef */
/*
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    AUDIT TRAIL TEST SUITE                                    ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  FILE: __tests__/models/AuditTrail.test.js                                  ║
║                                                                              ║
║  PURPOSE: Comprehensive tests for AuditTrail model with document access     ║
║                                                                              ║
║  CHIEF ARCHITECT: Wilson Khanyezi                                           ║
║  EMAIL: wilsy.wk@gmail.com | CELL: +27 69 046 5710                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
*/

const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');
const AuditTrail = require('../../models/AuditTrail');

// Test constants
const TEST_TENANT_ID = 'tenant_test_12345';
const TEST_USER_ID = new mongoose.Types.ObjectId();
const TEST_DOCUMENT_ID = new mongoose.Types.ObjectId();

// MongoDB Memory Server
let mongoServer;
let mongoUri;

describe('AuditTrail Model Tests', () => {
    beforeAll(async () => {
        mongoServer = await MongoMemoryServer.create();
        mongoUri = mongoServer.getUri();
        await mongoose.connect(mongoUri);
    });

    beforeEach(async () => {
        await AuditTrail.deleteMany({});
    });

    afterAll(async () => {
        await mongoose.disconnect();
        await mongoServer.stop();
    });

    describe('Document Access Logging', () => {
        test('should log document access event', async () => {
            const result = await AuditTrail.logDocumentAccess({
                tenantId: TEST_TENANT_ID,
                userId: TEST_USER_ID,
                userRole: 'LEGAL_COUNSEL',
                documentId: TEST_DOCUMENT_ID,
                documentVersion: 1,
                accessType: 'VIEW',
                documentMetadata: {
                    title: 'Test Legal Document',
                    classification: 'CONFIDENTIAL',
                    fileSize: 1024
                },
                ipAddress: '192.168.1.100',
                userAgent: 'Mozilla/5.0',
                success: true,
                statusCode: 200,
                responseTimeMs: 150
            });

            expect(result.eventId).toMatch(/^AUDIT-\d{13}-[a-f0-9]{12}$/);
            expect(result.actor.tenantId).toBe(TEST_TENANT_ID);
            expect(result.action.category).toBe('DOCUMENT_ACCESS');
            expect(result.action.documentAccess.accessType).toBe('VIEW');
            expect(result.outcome.success).toBe(true);
        });
    });

    describe('Validation Tests', () => {
        test('should require tenant ID', async () => {
            const audit = new AuditTrail({
                eventId: 'AUDIT-1234567890123-abcdef123456',
                actor: {
                    userId: TEST_USER_ID,
                    userRole: 'LEGAL_COUNSEL'
                },
                action: {
                    category: 'DOCUMENT_ACCESS',
                    method: 'GET',
                    resourceType: 'DOCUMENT',
                    endpoint: '/test',
                    description: 'Test'
                },
                outcome: {
                    statusCode: 200,
                    success: true,
                    responseTimeMs: 100
                },
                compliance: {
                    legalBasis: 'POPIA_2013',
                    jurisdiction: 'ZA'
                }
            });

            await expect(audit.save()).rejects.toThrow(/Tenant ID is required/);
        });
    });
});