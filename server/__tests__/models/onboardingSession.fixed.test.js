/**
 * @jest-environment node
 */
'use strict';

const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');
const testAdapter = require('./onboardingSession.test.adapter');

// This will be populated by the adapter
let OnboardingSession;

describe('🏛️ OnboardingSession Model - STRING-LITERAL SHIELD Test Suite', () => {
    let mongoServer;

    beforeAll(async () => {
        // Setup database
        mongoServer = await MongoMemoryServer.create();
        const uri = mongoServer.getUri();
        await mongoose.connect(uri);
        
        // Load model using adapter (GUARANTEES constructor)
        OnboardingSession = await testAdapter.initializeModel();
        
        console.log('✅ Test database connected');
        console.log('✅ Model loaded as:', typeof OnboardingSession);
    });

    afterAll(async () => {
        await mongoose.disconnect();
        await mongoServer.stop();
        console.log('✅ Test database disconnected');
    });

    afterEach(async () => {
        if (OnboardingSession) {
            await OnboardingSession.deleteMany({});
        }
    });

    // ============= TEST 1: Model Integrity =============
    describe('1. Model Integrity - STRING-LITERAL SHIELD Verification', () => {
        test('Model should be a constructor function', () => {
            expect(typeof OnboardingSession).toBe('function');
            expect(OnboardingSession.prototype).toBeDefined();
        });

        test('All Mixed types should be string literals', () => {
            const schema = OnboardingSession.schema;
            
            const verifyMixedType = (path) => {
                if (path && path.options && path.options.type) {
                    expect(path.options.type).toBe('Mixed');
                }
            };
            
            // Check clientData
            if (schema && schema.paths) {
                verifyMixedType(schema.paths.clientData);
                
                if (schema.paths.stages) {
                    const stagesSchema = schema.paths.stages.schema;
                    if (stagesSchema && stagesSchema.paths.data) {
                        verifyMixedType(stagesSchema.paths.data);
                    }
                }
                
                verifyMixedType(schema.paths._validationResults);
                verifyMixedType(schema.paths._encryption);
                verifyMixedType(schema.paths._audit);
            }
            
            console.log('✅ Mixed type verification complete');
        });
    });

    // ============= TEST 2: SA ID Validation =============
    describe('2. SA ID Validation', () => {
        test('Should validate valid SA ID', async () => {
            const session = new OnboardingSession({
                sessionId: 'ONB_IND_20250218120000_TEST_tenant-1',
                tenantId: 'tenant-1',
                clientType: 'INDIVIDUAL',
                identityType: 'SA_ID',
                idNumber: '8001015009081',
                clientData: {
                    firstName: 'John',
                    lastName: 'Doe',
                    dateOfBirth: '1980-01-01',
                    nationality: 'South African'
                },
                metadata: { createdBy: 'test' }
            });

            const saved = await session.save();
            expect(saved.idNumber).toBe('8001015009081');
            console.log('✅ Valid SA ID accepted');
        });

        test('Should reject invalid SA ID', async () => {
            const session = new OnboardingSession({
                sessionId: 'ONB_IND_20250218120000_TEST2_tenant-1',
                tenantId: 'tenant-1',
                clientType: 'INDIVIDUAL',
                identityType: 'SA_ID',
                idNumber: '12345',
                clientData: {
                    firstName: 'Jane',
                    lastName: 'Doe',
                    dateOfBirth: '1980-01-01',
                    nationality: 'South African'
                },
                metadata: { createdBy: 'test' }
            });

            await expect(session.save()).rejects.toThrow();
            console.log('✅ Invalid SA ID rejected');
        });
    });

    // ============= TEST 3: CreateSession Static Method =============
    describe('3. CreateSession Static Method', () => {
        test('createSession should work and return constructor instance', async () => {
            const session = await OnboardingSession.createSession('tenant-1', {
                clientType: 'INDIVIDUAL',
                clientData: {
                    firstName: 'Static',
                    lastName: 'Test',
                    dateOfBirth: '1980-01-01',
                    nationality: 'South African'
                }
            });

            expect(session).toBeDefined();
            expect(session.constructor).toBe(OnboardingSession);
            expect(session.sessionId).toBeDefined();
            console.log('✅ createSession works');
        });
    });

    // ============= Add more tests as needed =============
    // You can add all your other tests here following the same pattern
});
