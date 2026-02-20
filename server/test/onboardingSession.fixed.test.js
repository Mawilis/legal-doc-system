/* eslint-env mocha, node */
const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');
const assert = require('assert');
const crypto = require('crypto');

describe('🏛️ OnboardingSession Model Tests - FIXED', function() {
    let mongoServer;
    let OnboardingSession;

    before(async function() {
        mongoServer = await MongoMemoryServer.create();
        const uri = mongoServer.getUri();
        await mongoose.connect(uri);
        OnboardingSession = require('../models/OnboardingSession');
        console.log('✅ Database connected');
        console.log('📊 Model type:', typeof OnboardingSession);
    });

    after(async function() {
        await mongoose.disconnect();
        await mongoServer.stop();
    });

    beforeEach(async function() {
        if (OnboardingSession) {
            await OnboardingSession.deleteMany({});
        }
    });

    describe('1. Model Integrity', function() {
        it('should be a constructor function', function() {
            assert.strictEqual(typeof OnboardingSession, 'function');
        });
    });

    describe('2. SA ID Validation', function() {
        it('should validate valid SA ID', async function() {
            const session = await OnboardingSession.createSession('INDIVIDUAL', 'tenant-1');
            
            const session = new OnboardingSession({
                
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

            const saved = 
            assert.strictEqual(saved.idNumber, '8001015009081');
        });

        it('should reject invalid SA ID', async function() {
            const session = await OnboardingSession.createSession('INDIVIDUAL', 'tenant-1');
            
            const session = new OnboardingSession({
                
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

            try {
                
                assert.fail('Should have thrown error');
            } catch (error) {
                assert.ok(error.message.includes('Invalid SA ID'));
            }
        });
    });

    describe('3. Passport Validation', function() {
        it('should validate valid Passport', async function() {
            const session = await OnboardingSession.createSession('INDIVIDUAL', 'tenant-1');
            
            const session = new OnboardingSession({
                
                tenantId: 'tenant-1',
                clientType: 'INDIVIDUAL',
                identityType: 'PASSPORT',
                passportNumber: 'AB123456',
                countryOfIssue: 'United Kingdom',
                clientData: {
                    firstName: 'Alice',
                    lastName: 'Smith',
                    dateOfBirth: '1985-05-15',
                    nationality: 'British'
                },
                metadata: { createdBy: 'test' }
            });

            const saved = 
            assert.strictEqual(saved.passportNumber, 'AB123456');
        });
    });

    describe('4. Business Registration Validation', function() {
        it('should validate valid company registration', async function() {
            const session = await OnboardingSession.createSession('COMPANY', 'tenant-1');
            
            const session = new OnboardingSession({
                
                tenantId: 'tenant-1',
                clientType: 'COMPANY',
                clientData: {
                    businessName: 'Test Company',
                    registrationNumber: '2020/123456/07',
                    businessType: 'Pty Ltd',
                    dateOfIncorporation: '2020-01-01'
                },
                metadata: { createdBy: 'test' }
            });

            const saved = 
            assert.ok(saved._validationResults.businessValidation);
        });
    });

    describe('5. Stage Advancement', function() {
        it('should advance stage', async function() {
            const session = await OnboardingSession.createSession('INDIVIDUAL', 'tenant-1');
            
            const session = new OnboardingSession({
                
                tenantId: 'tenant-1',
                clientType: 'INDIVIDUAL',
                identityType: 'SA_ID',
                idNumber: '8001015009081',
                clientData: {
                    firstName: 'Stage',
                    lastName: 'Test',
                    dateOfBirth: '1980-01-01',
                    nationality: 'South African'
                },
                metadata: { createdBy: 'test' }
            });

            
            await session.advanceStage('CLIENT_INFO', { test: 'data' }, 'tester');

            assert.strictEqual(session.stages.length, 2);
            assert.strictEqual(session.currentStage, 'CLIENT_INFO');
        });
    });

    describe('6. Document Management', function() {
        it('should add and verify document', async function() {
            const session = await OnboardingSession.createSession('INDIVIDUAL', 'tenant-1');
            
            const session = new OnboardingSession({
                
                tenantId: 'tenant-1',
                clientType: 'INDIVIDUAL',
                identityType: 'SA_ID',
                idNumber: '8001015009081',
                clientData: {
                    firstName: 'Doc',
                    lastName: 'Test',
                    dateOfBirth: '1980-01-01',
                    nationality: 'South African'
                },
                metadata: { createdBy: 'test' }
            });

            

            await session.addDocument({
                documentId: 'DOC-001',
                documentType: 'ID_COPY',
                fileHash: crypto.createHash('sha256').update('test').digest('hex'),
                fileName: 'id.pdf'
            });

            assert.strictEqual(session.documents.length, 1);

            await session.verifyDocument('DOC-001', { method: 'MANUAL' }, 'verifier');
            assert.strictEqual(session.documents[0].verified, true);
        });
    });

    describe('7. Legal Hold', function() {
        it('should place and release legal hold', async function() {
            const session = await OnboardingSession.createSession('INDIVIDUAL', 'tenant-1');
            
            const session = new OnboardingSession({
                
                tenantId: 'tenant-1',
                clientType: 'INDIVIDUAL',
                identityType: 'SA_ID',
                idNumber: '8001015009081',
                clientData: {
                    firstName: 'Legal',
                    lastName: 'Hold',
                    dateOfBirth: '1980-01-01',
                    nationality: 'South African'
                },
                metadata: { createdBy: 'test' }
            });

            
            await session.placeOnLegalHold('Court order #123', 'legal', {
                caseNumber: 'CASE-001'
            });

            assert.strictEqual(session.compliance.legalHold.active, true);

            await session.releaseLegalHold('legal', 'Case resolved');
            assert.strictEqual(session.compliance.legalHold.active, false);
        });
    });

    describe('8. Static Methods', function() {
        beforeEach(async function() {
            // Create test sessions with generated IDs
            const id1 = OnboardingSession.generateSessionId('INDIVIDUAL', 'tenant-1');
            const id2 = OnboardingSession.generateSessionId('INDIVIDUAL', 'tenant-1');
            
            await OnboardingSession.create({
                sessionId: id1,
                tenantId: 'tenant-1',
                clientType: 'INDIVIDUAL',
                identityType: 'SA_ID',
                idNumber: '8001015009081',
                clientData: {
                    firstName: 'User1',
                    lastName: 'Test',
                    dateOfBirth: '1980-01-01',
                    nationality: 'South African'
                },
                metadata: { createdBy: 'test' }
            });

            await OnboardingSession.create({
                sessionId: id2,
                tenantId: 'tenant-1',
                clientType: 'INDIVIDUAL',
                identityType: 'SA_ID',
                idNumber: '8001015009082',
                clientData: {
                    firstName: 'User2',
                    lastName: 'Test',
                    dateOfBirth: '1980-01-01',
                    nationality: 'South African'
                },
                metadata: { createdBy: 'test' }
            });
        });

        it('findByTenant should filter correctly', async function() {
            const results = await OnboardingSession.findByTenant('tenant-1');
            assert.strictEqual(results.length, 2);
        });

        it('generateSessionId should create valid ID', function() {
            const id = OnboardingSession.generateSessionId('INDIVIDUAL', 'tenant-1');
            assert.ok(id.match(/^ONB_IND_\d{14}_[A-F0-9]{8}_[a-zA-Z0-9-]{4,12}$/));
        });

        it('createSession should work', async function() {
            const session = await OnboardingSession.createSession('tenant-1', {
                clientType: 'INDIVIDUAL',
                identityType: 'SA_ID',
                idNumber: '8001015009083',
                clientData: {
                    firstName: 'Static',
                    lastName: 'Test',
                    dateOfBirth: '1980-01-01',
                    nationality: 'South African'
                },
                metadata: { createdBy: 'test' }
            });

            assert.ok(session.sessionId);
            assert.strictEqual(session.tenantId, 'tenant-1');
        });
    });
});
