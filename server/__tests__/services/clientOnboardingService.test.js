'use strict';
const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');
const { registerModels } = require('../helpers/registerModels');

// Mock tenantContext properly
jest.mock('../../middleware/tenantContext', () => ({
    getCurrentTenant: jest.fn().mockReturnValue('tenant-test-123'),
    getCurrentUser: jest.fn().mockReturnValue('test-user-456')
}));

// Mock logger to suppress output during tests
jest.mock('../../utils/logger', () => ({
    info: jest.fn(),
    error: jest.fn(),
    warn: jest.fn(),
    debug: jest.fn()
}));

// Mock metrics to prevent interval issues
jest.mock('../../utils/metrics', () => ({
    increment: jest.fn(),
    recordTiming: jest.fn(),
    setGauge: jest.fn(),
    shutdown: jest.fn()
}));

// Mock worker to prevent interval issues
jest.mock('../../workers/documentVerificationWorker', () => ({
    queueForScanning: jest.fn().mockResolvedValue(true),
    queueForOCR: jest.fn().mockResolvedValue(true),
    shutdown: jest.fn()
}));

describe('Client Onboarding Service', () => {
    let mongoServer;
    let clientOnboardingService;
    let OnboardingSession;

    beforeAll(async () => {
        // Set test environment
        process.env.NODE_ENV = 'test';
        
        mongoServer = await MongoMemoryServer.create();
        const uri = mongoServer.getUri();
        
        await mongoose.connect(uri);
        
        // Register models explicitly
        await registerModels();
        
        // Get the model reference
        OnboardingSession = mongoose.model('OnboardingSession');
        
        // NOW import service (after models are registered)
        clientOnboardingService = require('../../services/clientOnboardingService');
        
        console.log('✅ Test setup complete');
    });

    afterAll(async () => {
        // Shutdown service
        if (clientOnboardingService && typeof clientOnboardingService.shutdown === 'function') {
            await clientOnboardingService.shutdown();
        }
        
        // Close mongoose connection
        await mongoose.disconnect();
        await mongoServer.stop();
    });

    beforeEach(async () => {
        // Clear database
        if (OnboardingSession) {
            await OnboardingSession.deleteMany({});
        }
        jest.clearAllMocks();
    });

    test('should be defined', () => {
        expect(clientOnboardingService).toBeDefined();
    });

    test('should create session', async () => {
        const session = await clientOnboardingService.createSession(
            'test-001',
            'tenant-1',
            'INDIVIDUAL',
            { 
                firstName: 'John', 
                lastName: 'Doe', 
                idNumber: '9001011234567', 
                dateOfBirth: '1990-01-01', 
                nationality: 'South African', 
                popiaConsent: true 
            }
        );
        
        expect(session).toBeDefined();
        expect(session.sessionId).toBe('test-001');
        expect(session.tenantId).toBe('tenant-1');
        expect(session.clientType).toBe('INDIVIDUAL');
        expect(session.status).toBe('PENDING');
    });
});
