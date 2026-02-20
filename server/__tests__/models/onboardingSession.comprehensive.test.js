/**
 * @jest-environment node
 */
'use strict';

const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');
const OnboardingSession = require('../../models/OnboardingSession');

describe('🏛️ OnboardingSession Model - Legal Grade Validation', () => {
    let mongoServer;
    let connection;

    beforeAll(async () => {
        mongoServer = await MongoMemoryServer.create();
        const uri = mongoServer.getUri();
        await mongoose.connect(uri);
        connection = mongoose.connection;
        console.log('✅ Test database connected');
    });

    afterAll(async () => {
        await mongoose.disconnect();
        await mongoServer.stop();
        console.log('✅ Test database disconnected');
    });

    afterEach(async () => {
        await OnboardingSession.deleteMany({});
    });

    describe('1. Model Integrity', () => {
        test('Model should be a constructor function', () => {
            expect(typeof OnboardingSession).toBe('function');
            expect(OnboardingSession.prototype).toBeDefined();
        });

        test('Schema should have required legal fields', () => {
            const schema = OnboardingSession.schema;
            
            // Core legal fields
            expect(schema.paths.sessionId).toBeDefined();
            expect(schema.paths.tenantId).toBeDefined();
            expect(schema.paths.clientType).toBeDefined();
            expect(schema.paths.status).toBeDefined();
            expect(schema.paths.currentStage).toBeDefined();
            expect(schema.paths.legalCompliance).toBeDefined();
            expect(schema.paths.fica).toBeDefined();
            expect(schema.paths.risk).toBeDefined();
            expect(schema.paths.compliance).toBeDefined();
            expect(schema.paths.expiresAt).toBeDefined();
        });

        test('CLIENT_TYPES should contain all legal entity types', () => {
            const OnboardingSessionWithConst = require('../../models/OnboardingSession');
            // Test through schema validation
            const validTypes = ['INDIVIDUAL', 'COMPANY', 'TRUST', 'NPO', 'PARTNERSHIP'];
            validTypes.forEach(type => {
                expect(() => {
                    new OnboardingSession({
                        sessionId: `ONB_${type.substring(0,3)}_20250217120000_TEST_tenant`,
                        tenantId: 'tenant-1',
                        clientType: type,
                        clientData: { firstName: 'Test' },
                        metadata: { createdBy: 'test' }
                    });
                }).not.toThrow();
            });
        });
    });

    describe('2. Session Creation & Validation', () => {
        const validSessionData = {
            sessionId: 'ONB_IND_20250217120000_A1B2C3D4_tenant-1',
            tenantId: 'tenant-1',
            clientType: 'INDIVIDUAL',
            clientData: {
                firstName: 'John',
                lastName: 'Doe',
                idNumber: '8001015009081',
                dateOfBirth: '1980-01-01',
                nationality: 'South African'
            },
            metadata: {
                createdBy: 'test-user'
            }
        };

        test('Should create valid session with minimal data', async () => {
            const session = new OnboardingSession(validSessionData);
            const saved = await session.save();
            
            expect(saved.sessionId).toBe(validSessionData.sessionId);
            expect(saved.tenantId).toBe('tenant-1');
            expect(saved.clientType).toBe('INDIVIDUAL');
            expect(saved.status).toBe('PENDING');
            expect(saved.currentStage).toBe('INITIATED');
            expect(saved.stages).toHaveLength(1);
            expect(saved.stages[0].stage).toBe('INITIATED');
            expect(saved.stages[0].hash).toBeDefined();
            expect(saved.metadata.createdBy).toBe('test-user');
            expect(saved.expiresAt).toBeDefined();
        });

        test('Should generate session ID via static method', () => {
            const sessionId = OnboardingSession.generateSessionId('INDIVIDUAL', 'tenant-1');
            expect(sessionId).toMatch(/^ONB_IND_\d{14}_[A-F0-9]{8}_[a-zA-Z0-9-]{4,12}$/);
        });

        test('Should create session via static createSession', async () => {
            const session = await OnboardingSession.createSession('tenant-1', {
                clientType: 'INDIVIDUAL',
                clientData: {
                    firstName: 'Jane',
                    lastName: 'Smith',
                    idNumber: '8001015009081',
                    dateOfBirth: '1980-01-01',
                    nationality: 'South African'
                },
                metadata: { createdBy: 'test-user' }
            }, { createdBy: 'test-user' });
            
            expect(session.sessionId).toBeDefined();
            expect(session.tenantId).toBe('tenant-1');
            expect(session.stages).toHaveLength(1);
            expect(session.legalCompliance.lastComplianceCheck).toBeDefined();
            expect(session.legalCompliance.nextComplianceCheck).toBeDefined();
        });

        test('Should validate required fields', async () => {
            const invalidSession = new OnboardingSession({
                tenantId: 'tenant-1',
                clientType: 'INDIVIDUAL'
                // Missing clientData
            });
            
            await expect(invalidSession.save()).rejects.toThrow();
        });

        test('Should enforce unique sessionId', async () => {
            const session1 = new OnboardingSession(validSessionData);
            await session1.save();
            
            const session2 = new OnboardingSession(validSessionData);
            await expect(session2.save()).rejects.toThrow(/duplicate key/);
        });

        test('Should validate client data based on client type', async () => {
            // COMPANY requires businessName and registrationNumber
            const invalidCompanySession = new OnboardingSession({
                sessionId: 'ONB_BUS_20250217120000_TEST_tenant-1',
                tenantId: 'tenant-1',
                clientType: 'COMPANY',
                clientData: { firstName: 'Wrong' }, // Should be businessName
                metadata: { createdBy: 'test' }
            });
            
            await expect(invalidCompanySession.save()).rejects.toThrow(/required fields/);
        });
    });

    describe('3. Instance Methods', () => {
        let session;

        beforeEach(async () => {
            session = new OnboardingSession({
                sessionId: 'ONB_IND_20250217120000_TEST_tenant-1',
                tenantId: 'tenant-1',
                clientType: 'INDIVIDUAL',
                clientData: {
                    firstName: 'Test',
                    lastName: 'User',
                    idNumber: '8001015009081',
                    dateOfBirth: '1980-01-01',
                    nationality: 'South African'
                },
                metadata: { createdBy: 'test-user' }
            });
            await session.save();
        });

        test('advanceStage should add new stage with audit trail', async () => {
            await session.advanceStage('CLIENT_INFO', { completed: true }, 'test-user', {
                ipAddress: '127.0.0.1',
                userAgent: 'test-agent'
            });
            
            expect(session.stages).toHaveLength(2);
            expect(session.currentStage).toBe('CLIENT_INFO');
            expect(session.stages[1].stage).toBe('CLIENT_INFO');
            expect(session.stages[1].performedBy).toBe('test-user');
            expect(session.stages[1].hash).toBeDefined();
            expect(session.stages[1].previousHash).toBe(session.stages[0].hash);
            expect(session.metadata.version).toBe(2);
        });

        test('addDocument should add document with chain of custody', async () => {
            const documentData = {
                documentId: 'doc_123',
                documentType: 'ID_COPY',
                fileHash: crypto.createHash('sha256').update('test').digest('hex'),
                fileName: 'id.pdf',
                fileSize: 1024
            };
            
            await session.addDocument(documentData, {
                uploadedBy: 'test-user',
                ipAddress: '127.0.0.1'
            });
            
            expect(session.documents).toHaveLength(1);
            expect(session.documents[0].documentId).toBe('doc_123');
            expect(session.documents[0].chainOfCustody).toHaveLength(1);
            expect(session.documents[0].chainOfCustody[0].action).toBe('UPLOADED');
        });

        test('verifyDocument should update document verification status', async () => {
            const documentData = {
                documentId: 'doc_123',
                documentType: 'ID_COPY',
                fileHash: crypto.createHash('sha256').update('test').digest('hex')
            };
            
            await session.addDocument(documentData);
            await session.verifyDocument('doc_123', {
                method: 'MANUAL',
                notes: 'Verified manually'
            }, 'verifier-user');
            
            expect(session.documents[0].verified).toBe(true);
            expect(session.documents[0].verifiedBy).toBe('verifier-user');
            expect(session.documents[0].chainOfCustody).toHaveLength(2);
            expect(session.documents[0].chainOfCustody[1].action).toBe('VERIFIED');
        });

        test('updateFICAStatus should track FICA compliance', async () => {
            await session.updateFICAStatus('APPROVED', {
                reference: 'FICA-123',
                riskScore: 25,
                riskLevel: 'LOW',
                notes: 'All checks passed'
            }, 'fico-user');
            
            expect(session.fica.status).toBe('APPROVED');
            expect(session.fica.reference).toBeDefined();
            expect(session.fica.screeningHistory).toHaveLength(1);
            expect(session.legalCompliance.ficaCompliant).toBe(true);
            expect(session.legalCompliance.ficaCompliantAt).toBeDefined();
        });

        test('updateRiskAssessment should calculate risk level', async () => {
            await session.updateRiskAssessment({
                score: 85,
                factors: [
                    { factor: 'PEP', score: 40, description: 'Politically exposed person' },
                    { factor: 'FOREIGN', score: 45, description: 'Foreign national' }
                ]
            }, 'risk-user');
            
            expect(session.risk.score).toBe(85);
            expect(session.risk.level).toBe('HIGH');
            expect(session.risk.assessmentHistory).toHaveLength(1);
            expect(session.risk.nextReviewDate).toBeDefined();
        });

        test('placeOnLegalHold should activate legal hold', async () => {
            await session.placeOnLegalHold('Court order #12345', 'legal-officer', {
                caseNumber: 'CASE-2024-001',
                expiresAt: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000)
            });
            
            expect(session.compliance.legalHold.active).toBe(true);
            expect(session.compliance.legalHold.reason).toBe('Court order #12345');
            expect(session.compliance.legalHold.caseNumber).toBe('CASE-2024-001');
        });

        test('releaseLegalHold should deactivate legal hold', async () => {
            await session.placeOnLegalHold('Court order', 'legal-officer');
            await session.releaseLegalHold('legal-officer', 'Case resolved');
            
            expect(session.compliance.legalHold.active).toBe(false);
            expect(session.compliance.legalHold.releasedBy).toBe('legal-officer');
            expect(session.compliance.legalHold.releaseReason).toBe('Case resolved');
        });

        test('getLegalSummary should return comprehensive legal summary', () => {
            const summary = session.getLegalSummary();
            
            expect(summary.sessionId).toBe(session.sessionId);
            expect(summary.tenantId).toBe('tenant-1');
            expect(summary.clientType).toBe('INDIVIDUAL');
            expect(summary.fica).toBeDefined();
            expect(summary.risk).toBeDefined();
            expect(summary.compliance).toBeDefined();
            expect(summary.timeline).toBeDefined();
            expect(summary.documents).toBeDefined();
        });

        test('getAuditTrail should return complete trail with integrity check', async () => {
            await session.advanceStage('CLIENT_INFO', {}, 'test-user');
            
            const trail = session.getAuditTrail();
            
            expect(trail.stages).toHaveLength(2);
            expect(trail.integrity.valid).toBe(true);
            expect(trail.integrity.stages).toBe(2);
        });

        test('verifyAuditTrail should validate blockchain integrity', () => {
            const verification = session.verifyAuditTrail();
            expect(verification.valid).toBe(true);
        });

        test('exportForDiscovery should redact sensitive data', () => {
            const exported = session.exportForDiscovery();
            
            expect(exported.sessionId).toBeDefined();
            expect(exported.security?.encryption).toBeUndefined();
            expect(exported.exportMetadata).toBeDefined();
            expect(exported.exportMetadata.integrityHash).toBeDefined();
            expect(exported.exportMetadata.verifiedBy.valid).toBe(true);
        });

        test('getSummary should return dashboard summary', () => {
            const summary = session.getSummary();
            
            expect(summary.sessionId).toBe(session.sessionId);
            expect(summary.clientIdentifier).toBeDefined();
            expect(summary.stageProgress).toBeDefined();
            expect(summary.requiresAttention).toBeDefined();
        });
    });

    describe('4. Static Methods', () => {
        beforeEach(async () => {
            // Create test sessions
            const sessions = [
                {
                    sessionId: 'ONB_IND_001_tenant-1',
                    tenantId: 'tenant-1',
                    clientType: 'INDIVIDUAL',
                    clientData: { firstName: 'User1', lastName: 'Test' },
                    status: 'PENDING',
                    metadata: { createdBy: 'test' }
                },
                {
                    sessionId: 'ONB_IND_002_tenant-1',
                    tenantId: 'tenant-1',
                    clientType: 'INDIVIDUAL',
                    clientData: { firstName: 'User2', lastName: 'Test' },
                    status: 'COMPLETED',
                    metadata: { createdBy: 'test' }
                },
                {
                    sessionId: 'ONB_BUS_003_tenant-2',
                    tenantId: 'tenant-2',
                    clientType: 'COMPANY',
                    clientData: { businessName: 'Biz1' },
                    status: 'PENDING',
                    risk: { level: 'HIGH' },
                    metadata: { createdBy: 'test' }
                },
                {
                    sessionId: 'ONB_TRU_004_tenant-1',
                    tenantId: 'tenant-1',
                    clientType: 'TRUST',
                    clientData: { trustName: 'Trust1' },
                    status: 'IN_PROGRESS',
                    fica: { status: 'PENDING' },
                    metadata: { createdBy: 'test' }
                }
            ];

            for (const data of sessions) {
                const session = new OnboardingSession(data);
                await session.save();
            }
        });

        test('findByTenant should filter by tenant', async () => {
            const results = await OnboardingSession.findByTenant('tenant-1');
            expect(results).toHaveLength(3);
        });

        test('findByTenant with status filter', async () => {
            const results = await OnboardingSession.findByTenant('tenant-1', { status: 'PENDING' });
            expect(results).toHaveLength(1);
            expect(results[0].status).toBe('PENDING');
        });

        test('findByTenant with clientType filter', async () => {
            const results = await OnboardingSession.findByTenant('tenant-1', { clientType: 'TRUST' });
            expect(results).toHaveLength(1);
            expect(results[0].clientType).toBe('TRUST');
        });

        test('findByTenant with search text', async () => {
            const results = await OnboardingSession.findByTenant('tenant-1', { searchText: 'User1' });
            expect(results.length).toBeGreaterThan(0);
        });

        test('getLegalStatistics should return comprehensive stats', async () => {
            const stats = await OnboardingSession.getLegalStatistics('tenant-1');
            
            expect(stats.statusBreakdown).toBeDefined();
            expect(stats.clientTypeBreakdown).toBeDefined();
            expect(stats.ficaStatusBreakdown).toBeDefined();
            expect(stats.riskLevelBreakdown).toBeDefined();
            expect(stats.compliance).toBeDefined();
            expect(stats.requiresAttention).toBeDefined();
            expect(stats.averages).toBeDefined();
        });

        test('findOnLegalHold should return sessions on hold', async () => {
            // Place a session on hold
            const session = await OnboardingSession.findOne({ sessionId: 'ONB_IND_001_tenant-1' });
            await session.placeOnLegalHold('Test hold', 'test-user');
            
            const results = await OnboardingSession.findOnLegalHold('tenant-1');
            expect(results).toHaveLength(1);
            expect(results[0].sessionId).toBe('ONB_IND_001_tenant-1');
        });

        test('findExpiringSoon should return sessions near expiry', async () => {
            // Set a session to expire soon
            const session = await OnboardingSession.findOne({ sessionId: 'ONB_IND_001_tenant-1' });
            session.expiresAt = new Date(Date.now() + 15 * 24 * 60 * 60 * 1000); // 15 days
            await session.save();
            
            const results = await OnboardingSession.findExpiringSoon('tenant-1', 30);
            expect(results.length).toBeGreaterThan(0);
        });

        test('getDashboardMetrics should return operational metrics', async () => {
            const metrics = await OnboardingSession.getDashboardMetrics('tenant-1');
            
            expect(metrics.totalSessions).toBe(3);
            expect(metrics.activeSessions).toBeDefined();
            expect(metrics.pendingFICA).toBeDefined();
            expect(metrics.highRisk).toBeDefined();
            expect(metrics.legalHoldCount).toBe(0);
            expect(metrics.expiringSoon).toBeDefined();
            expect(metrics.recentSessions).toBeDefined();
            expect(metrics.completionRate).toBeDefined();
        });

        test('calculateCompletionRate should return percentage', async () => {
            const rate = await OnboardingSession.calculateCompletionRate('tenant-1', new Date(Date.now() - 30 * 24 * 60 * 60 * 1000));
            expect(rate).toBeGreaterThanOrEqual(0);
            expect(rate).toBeLessThanOrEqual(100);
        });
    });

    describe('5. Indexes and Performance', () => {
        test('indexes should be created', async () => {
            const indexes = await OnboardingSession.collection.indexes();
            
            const hasTenantStatusIndex = indexes.some(i => 
                i.key && i.key.tenantId === 1 && i.key.status === 1 && i.key.createdAt === -1
            );
            expect(hasTenantStatusIndex).toBe(true);
            
            const hasFicaStatusIndex = indexes.some(i => 
                i.key && i.key['fica.status'] === 1 && i.key.createdAt === -1
            );
            expect(hasFicaStatusIndex).toBe(true);
            
            const hasRiskLevelIndex = indexes.some(i => 
                i.key && i.key['risk.level'] === 1 && i.key.status === 1
            );
            expect(hasRiskLevelIndex).toBe(true);
        });

        test('text search index should exist', async () => {
            const indexes = await OnboardingSession.collection.indexes();
            const hasTextIndex = indexes.some(i => i.name === 'client_search_index');
            expect(hasTextIndex).toBe(true);
        });
    });

    describe('6. Virtual Properties', () => {
        let session;

        beforeEach(async () => {
            session = new OnboardingSession({
                sessionId: 'ONB_IND_TEST_tenant-1',
                tenantId: 'tenant-1',
                clientType: 'INDIVIDUAL',
                clientData: { firstName: 'Test' },
                metadata: { createdBy: 'test' },
                expiresAt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)
            });
            await session.save();
        });

        test('isExpired should return correct status', () => {
            expect(session.isExpired).toBe(false);
            
            session.expiresAt = new Date(Date.now() - 1000);
            expect(session.isExpired).toBe(true);
        });

        test('stageCount should return correct count', () => {
            expect(session.stageCount).toBe(1);
        });

        test('documentCount should return correct count', () => {
            expect(session.documentCount).toBe(0);
        });

        test('processingProgress should return correct percentage', () => {
            const progress = session.processingProgress;
            expect(progress.completed).toBe(1);
            expect(progress.total).toBeGreaterThan(1);
            expect(progress.percentage).toBe((1 / progress.total) * 100);
        });

        test('ageInDays should return correct age', () => {
            expect(session.ageInDays).toBe(0);
        });

        test('legalSummary should return summary', () => {
            const summary = session.legalSummary;
            expect(summary.sessionId).toBe(session.sessionId);
            expect(summary.dataRetention).toBeDefined();
            expect(summary.dataRetention.daysRemaining).toBeGreaterThan(0);
        });
    });

    describe('7. Edge Cases and Error Handling', () => {
        test('Should handle invalid stage transitions', async () => {
            const session = new OnboardingSession({
                sessionId: 'ONB_IND_TEST_tenant-1',
                tenantId: 'tenant-1',
                clientType: 'INDIVIDUAL',
                clientData: { firstName: 'Test' },
                metadata: { createdBy: 'test' }
            });
            await session.save();
            
            await expect(session.advanceStage('INVALID_STAGE', {}, 'test-user')).rejects.toThrow();
        });

        test('Should handle invalid FICA status transitions', async () => {
            const session = new OnboardingSession({
                sessionId: 'ONB_IND_TEST_tenant-1',
                tenantId: 'tenant-1',
                clientType: 'INDIVIDUAL',
                clientData: { firstName: 'Test' },
                metadata: { createdBy: 'test' }
            });
            await session.save();
            
            await session.updateFICAStatus('APPROVED', {}, 'test-user');
            await expect(session.updateFICAStatus('PENDING', {}, 'test-user')).rejects.toThrow();
        });

        test('Should handle missing documents in verifyDocument', async () => {
            const session = new OnboardingSession({
                sessionId: 'ONB_IND_TEST_tenant-1',
                tenantId: 'tenant-1',
                clientType: 'INDIVIDUAL',
                clientData: { firstName: 'Test' },
                metadata: { createdBy: 'test' }
            });
            await session.save();
            
            await expect(session.verifyDocument('non-existent', {}, 'test-user')).rejects.toThrow();
        });

        test('Should handle releasing non-existent legal hold', async () => {
            const session = new OnboardingSession({
                sessionId: 'ONB_IND_TEST_tenant-1',
                tenantId: 'tenant-1',
                clientType: 'INDIVIDUAL',
                clientData: { firstName: 'Test' },
                metadata: { createdBy: 'test' }
            });
            await session.save();
            
            await expect(session.releaseLegalHold('test-user', 'No hold')).rejects.toThrow();
        });
    });
});
