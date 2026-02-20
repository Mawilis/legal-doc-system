/* eslint-env jest */
/**
 * INTEGRATION TEST: Client Onboarding Service
 * INVESTOR-GRADE - WORKING SOLUTION
 * Version: 5.0.0
 */

const mongoose = require('mongoose');
const testSetup = require('../helpers/testSetup');
const auditLogger = require('../../utils/auditLogger');
const cryptoUtils = require('../../utils/cryptoUtils');

// Mock only external services
jest.mock('../../utils/auditLogger', () => ({
    audit: jest.fn().mockResolvedValue(true)
}));

jest.mock('../../utils/cryptoUtils', () => ({
    generateForensicHash: jest.fn().mockImplementation((data) => {
        return `hash_${Buffer.from(data).toString('hex').substring(0, 10)}`;
    }),
    redactSensitive: jest.fn().mockImplementation(data => data)
}));

jest.mock('../../utils/logger', () => ({
    info: jest.fn(),
    error: jest.fn(),
    warn: jest.fn(),
    debug: jest.fn()
}));

jest.mock('../../middleware/tenantContext', () => ({
    getCurrentTenant: jest.fn().mockReturnValue('tenant-test-12345678'),
    getCurrentUser: jest.fn().mockReturnValue('test-user-123')
}));

jest.mock('../../services/ficaScreeningService', () => ({
    screenClient: jest.fn().mockResolvedValue({ status: 'APPROVED', reference: 'FICA-123' }),
    healthCheck: jest.fn().mockResolvedValue({ status: 'healthy' })
}));

jest.mock('../../workers/documentVerificationWorker', () => ({
    queueForScanning: jest.fn().mockResolvedValue(true)
}));

describe('Client Onboarding Service - Integration Tests', () => {
    let clientOnboardingService;

    beforeAll(async () => {
        console.log('\n🚀 Starting test suite setup...');
        
        // Setup database
        await testSetup.setup();
        
        // Load models - they will self-register
        await testSetup.registerModels();
        
        console.log('📊 Available models:', Object.keys(mongoose.models));
        
        // Import the service
        clientOnboardingService = require('../../services/clientOnboardingService');
        
        console.log('✅ Test environment ready\n');
    });

    afterAll(async () => {
        console.log('\n🔄 Starting test suite teardown...');
        
        // Shutdown service
        if (clientOnboardingService && clientOnboardingService.shutdown) {
            await clientOnboardingService.shutdown();
            console.log('✅ Service shutdown complete');
        }
        
        // Teardown database
        await testSetup.teardown();
        console.log('✅ Test suite teardown complete\n');
    });

    beforeEach(async () => {
        // Clear database between tests
        await testSetup.clearDatabase();
        jest.clearAllMocks();
    });

    test('[TC-001] should create onboarding session', async () => {
        const sessionId = 'test-session-001';
        const tenantId = 'tenant-test-12345678';
        const clientType = 'INDIVIDUAL';
        const initialData = {
            firstName: 'John',
            lastName: 'Doe',
            idNumber: '9001011234567',
            dateOfBirth: '1990-01-01',
            nationality: 'South African',
            popiaConsent: true
        };

        const session = await clientOnboardingService.createSession(
            sessionId,
            tenantId,
            clientType,
            initialData
        );

        expect(session).toBeDefined();
        expect(session.sessionId).toBe(sessionId);
        expect(session.tenantId).toBe(tenantId);
        expect(session.clientType).toBe(clientType);
        expect(session.status).toBe('PENDING');
        expect(session.stages).toHaveLength(1);
        expect(session.stages[0].stage).toBe('INITIATED');
    });

    test('[TC-002] should get session', async () => {
        const sessionId = 'test-session-002';
        const tenantId = 'tenant-test-12345678';
        const clientType = 'INDIVIDUAL';
        const initialData = {
            firstName: 'Jane',
            lastName: 'Smith',
            idNumber: '9001011234567',
            dateOfBirth: '1990-01-01',
            nationality: 'South African',
            popiaConsent: true
        };

        await clientOnboardingService.createSession(
            sessionId,
            tenantId,
            clientType,
            initialData
        );

        const session = await clientOnboardingService.getSession(sessionId, tenantId);
        expect(session).toBeDefined();
        expect(session.sessionId).toBe(sessionId);
        expect(session.tenantId).toBe(tenantId);
    });

    test('[TC-003] should update session data', async () => {
        const sessionId = 'test-session-003';
        const tenantId = 'tenant-test-12345678';
        const clientType = 'INDIVIDUAL';
        
        await clientOnboardingService.createSession(
            sessionId,
            tenantId,
            clientType,
            {
                firstName: 'John',
                lastName: 'Doe',
                idNumber: '9001011234567',
                dateOfBirth: '1990-01-01',
                nationality: 'South African',
                popiaConsent: true
            }
        );

        const updated = await clientOnboardingService.updateSessionData(
            sessionId,
            tenantId,
            'CLIENT_INFO',
            { 
                firstName: 'John', 
                lastName: 'Doe', 
                idNumber: '9001011234567',
                dateOfBirth: '1990-01-01',
                nationality: 'South African'
            }
        );

        expect(updated).toBeDefined();
        expect(updated.stages).toHaveLength(2);
        expect(updated.currentStage).toBe('CLIENT_INFO');
    });

    test('[TC-004] should upload document', async () => {
        const sessionId = 'test-session-004';
        const tenantId = 'tenant-test-12345678';
        const clientType = 'INDIVIDUAL';
        
        await clientOnboardingService.createSession(
            sessionId,
            tenantId,
            clientType,
            {
                firstName: 'John',
                lastName: 'Doe',
                idNumber: '9001011234567',
                dateOfBirth: '1990-01-01',
                nationality: 'South African',
                popiaConsent: true
            }
        );

        const documentInfo = {
            documentType: 'ID_COPY',
            fileName: 'id-document.pdf',
            fileSize: 1024,
            mimeType: 'application/pdf'
        };
        
        const fileData = Buffer.from('mock file content');

        const document = await clientOnboardingService.uploadDocument(
            sessionId,
            tenantId,
            documentInfo,
            fileData
        );

        expect(document).toBeDefined();
        expect(document.documentType).toBe('ID_COPY');
        expect(document.sessionId).toBe(sessionId);
        expect(document.tenantId).toBe(tenantId);
    });

    test('[TC-005] should get documents', async () => {
        const sessionId = 'test-session-005';
        const tenantId = 'tenant-test-12345678';
        const clientType = 'INDIVIDUAL';
        
        await clientOnboardingService.createSession(
            sessionId,
            tenantId,
            clientType,
            {
                firstName: 'John',
                lastName: 'Doe',
                idNumber: '9001011234567',
                dateOfBirth: '1990-01-01',
                nationality: 'South African',
                popiaConsent: true
            }
        );

        await clientOnboardingService.uploadDocument(
            sessionId,
            tenantId,
            { 
                documentType: 'ID_COPY', 
                fileName: 'id.pdf', 
                fileSize: 1024, 
                mimeType: 'application/pdf' 
            },
            Buffer.from('id content')
        );

        await clientOnboardingService.uploadDocument(
            sessionId,
            tenantId,
            { 
                documentType: 'PROOF_OF_ADDRESS', 
                fileName: 'address.pdf', 
                fileSize: 2048, 
                mimeType: 'application/pdf' 
            },
            Buffer.from('address content')
        );

        const documents = await clientOnboardingService.getDocuments(sessionId, tenantId);
        expect(documents).toHaveLength(2);
        expect(documents[0].documentType).toBeDefined();
    });

    test('[TC-008] should get statistics', async () => {
        const tenantId = 'tenant-test-12345678';
        
        for (let i = 0; i < 5; i++) {
            await clientOnboardingService.createSession(
                `test-session-stat-${i}`,
                tenantId,
                'INDIVIDUAL',
                {
                    firstName: `User${i}`,
                    lastName: 'Test',
                    idNumber: `900101123456${i}`,
                    dateOfBirth: '1990-01-01',
                    nationality: 'South African',
                    popiaConsent: true
                }
            );
        }

        const stats = await clientOnboardingService.getStatistics(tenantId);
        expect(stats).toBeDefined();
        expect(stats.sessions.total).toBe(5);
    });

    test('[TC-009] should enforce tenant isolation', async () => {
        const sessionId1 = 'test-session-009-1';
        const tenantId1 = 'tenant-1';
        const clientType = 'INDIVIDUAL';
        
        await clientOnboardingService.createSession(
            sessionId1,
            tenantId1,
            clientType,
            { 
                firstName: 'Tenant1',
                lastName: 'User',
                idNumber: '9001011234567',
                dateOfBirth: '1990-01-01',
                nationality: 'South African',
                popiaConsent: true
            }
        );

        const sessionId2 = 'test-session-009-2';
        const tenantId2 = 'tenant-2';
        
        await clientOnboardingService.createSession(
            sessionId2,
            tenantId2,
            clientType,
            { 
                firstName: 'Tenant2',
                lastName: 'User',
                idNumber: '9001011234567',
                dateOfBirth: '1990-01-01',
                nationality: 'South African',
                popiaConsent: true
            }
        );

        const session = await clientOnboardingService.getSession(sessionId1, tenantId2);
        expect(session).toBeNull();

        const session1 = await clientOnboardingService.getSession(sessionId1, tenantId1);
        expect(session1).toBeDefined();
        expect(session1.tenantId).toBe(tenantId1);
    });
});
