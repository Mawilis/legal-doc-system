
/**
 * @jest-environment node
 */
'use strict';

const crypto = require('crypto');
const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');
const OnboardingSession = require('../../models/OnboardingSession');

describe('🏛️ OnboardingSession Model - STRING-LITERAL SHIELD Test Suite', () => {
    let mongoServer;

    beforeAll(async () => {
        mongoServer = await MongoMemoryServer.create();
        const uri = mongoServer.getUri();
        await mongoose.connect(uri);
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

    describe('1. Model Integrity - STRING-LITERAL SHIELD Verification', () => {
        test('Model should be a constructor function', () => {
            expect(typeof OnboardingSession).toBe('function');
            expect(OnboardingSession.prototype).toBeDefined();
        });

        test('All Mixed types should be string literals', () => {
            const schema = OnboardingSession.schema;

            // Helper function to check if a path has Mixed type as string literal
            const verifyMixedType = (path) => {
                if (path && path.options && path.options.type) {
                    expect(path.options.type).toBe('Mixed');
                }
            };

            // Check clientData
            verifyMixedType(schema.paths.clientData);

            // Check stages data
            if (schema.paths.stages) {
                const stagesSchema = schema.paths.stages.schema;
                if (stagesSchema && stagesSchema.paths.data) {
                    verifyMixedType(stagesSchema.paths.data);
                }
            }

            // Check _validationResults
            verifyMixedType(schema.paths._validationResults);

            // Check _encryption
            verifyMixedType(schema.paths._encryption);

            // Check _audit
            verifyMixedType(schema.paths._audit);

            // Check legalCompliance.eddRequirements
            if (schema.paths.legalCompliance) {
                const legalComplianceSchema = schema.paths.legalCompliance.schema;
                if (legalComplianceSchema && legalComplianceSchema.paths.eddRequirements) {
                    verifyMixedType(legalComplianceSchema.paths.eddRequirements);
                }
            }

            // Check fica.screeningHistory details
            if (schema.paths.fica) {
                const ficaSchema = schema.paths.fica.schema;
                if (ficaSchema && ficaSchema.paths.screeningHistory) {
                    const screeningHistorySchema = ficaSchema.paths.screeningHistory.schema;
                    if (screeningHistorySchema && screeningHistorySchema.paths.details) {
                        verifyMixedType(screeningHistorySchema.paths.details);
                    }
                }
            }

            // Check risk.factors metadata
            if (schema.paths.risk) {
                const riskSchema = schema.paths.risk.schema;
                if (riskSchema && riskSchema.paths.factors) {
                    const factorsSchema = riskSchema.paths.factors.schema;
                    if (factorsSchema && factorsSchema.paths.metadata) {
                        verifyMixedType(factorsSchema.paths.metadata);
                    }
                }
            }

            // Check compliance.legalHold.courtOrder
            if (schema.paths.compliance) {
                const complianceSchema = schema.paths.compliance.schema;
                if (complianceSchema && complianceSchema.paths.legalHold) {
                    const legalHoldSchema = complianceSchema.paths.legalHold.schema;
                    if (legalHoldSchema && legalHoldSchema.paths.courtOrder) {
                        verifyMixedType(legalHoldSchema.paths.courtOrder);
                    }
                }
            }

            // Check metadata.additionalData
            if (schema.paths.metadata) {
                const metadataSchema = schema.paths.metadata.schema;
                if (metadataSchema && metadataSchema.paths.additionalData) {
                    verifyMixedType(metadataSchema.paths.additionalData);
                }
            }

            console.log('✅ All Mixed types are string literals');
        });
    });

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
            expect(saved._validationResults.saidValidation).toBeDefined();
            console.log('✅ Valid SA ID accepted');
        });

        test('Should reject invalid SA ID', async () => {
            const session = new OnboardingSession({
                sessionId: 'ONB_IND_20250218120000_TEST2_tenant-1',
                tenantId: 'tenant-1',
                clientType: 'INDIVIDUAL',
                identityType: 'SA_ID',
                idNumber: '12345', // Invalid ID
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

    describe('3. Passport Validation', () => {
        test('Should validate valid Passport', async () => {
            const session = new OnboardingSession({
                sessionId: 'ONB_IND_20250218120000_TEST3_tenant-1',
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

            const saved = await session.save();
            expect(saved.passportNumber).toBe('AB123456');
            expect(saved._validationResults.passportValidation).toBeDefined();
            console.log('✅ Valid Passport accepted');
        });

        test('Should reject invalid Passport', async () => {
            const session = new OnboardingSession({
                sessionId: 'ONB_IND_20250218120000_TEST4_tenant-1',
                tenantId: 'tenant-1',
                clientType: 'INDIVIDUAL',
                identityType: 'PASSPORT',
                passportNumber: 'A', // Too short
                countryOfIssue: 'USA',
                clientData: {
                    firstName: 'Bob',
                    lastName: 'Johnson',
                    dateOfBirth: '1975-03-20',
                    nationality: 'American'
                },
                metadata: { createdBy: 'test' }
            });

            await expect(session.save()).rejects.toThrow();
            console.log('✅ Invalid Passport rejected');
        });
    });

    describe('4. Business Registration Validation', () => {
        test('Should validate valid company registration', async () => {
            const session = new OnboardingSession({
                sessionId: 'ONB_BUS_20250218120000_TEST5_tenant-1',
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

            const saved = await session.save();
            expect(saved._validationResults.businessValidation).toBeDefined();
            console.log('✅ Valid company registration accepted');
        });

        test('Should reject invalid registration', async () => {
            const session = new OnboardingSession({
                sessionId: 'ONB_BUS_20250218120000_TEST6_tenant-1',
                tenantId: 'tenant-1',
                clientType: 'COMPANY',
                clientData: {
                    businessName: 'Test Company',
                    registrationNumber: '123', // Invalid
                    businessType: 'Pty Ltd',
                    dateOfIncorporation: '2020-01-01'
                },
                metadata: { createdBy: 'test' }
            });

            await expect(session.save()).rejects.toThrow();
            console.log('✅ Invalid registration rejected');
        });
    });

    describe('5. Tax Number Validation', () => {
        test('Should validate tax number', async () => {
            const session = new OnboardingSession({
                sessionId: 'ONB_IND_20250218120000_TEST7_tenant-1',
                tenantId: 'tenant-1',
                clientType: 'INDIVIDUAL',
                identityType: 'SA_ID',
                idNumber: '8001015009081',
                clientData: {
                    firstName: 'Tax',
                    lastName: 'Payer',
                    dateOfBirth: '1980-01-01',
                    nationality: 'South African',
                    taxNumber: '1234567890'
                },
                metadata: { createdBy: 'test' }
            });

            const saved = await session.save();
            expect(saved._validationResults.taxValidation).toBeDefined();

            // Test the tax validation method
            const taxResult = saved.validateTaxInformation();
            expect(taxResult.valid).toBe(true);

            console.log('✅ Tax number validation working');
        });
    });

    describe('6. Address Validation', () => {
        test('Should validate address', async () => {
            const session = new OnboardingSession({
                sessionId: 'ONB_IND_20250218120000_TEST8_tenant-1',
                tenantId: 'tenant-1',
                clientType: 'INDIVIDUAL',
                identityType: 'SA_ID',
                idNumber: '8001015009081',
                clientData: {
                    firstName: 'Address',
                    lastName: 'Test',
                    dateOfBirth: '1980-01-01',
                    nationality: 'South African',
                    address: {
                        street: '123 Main St',
                        city: 'Johannesburg',
                        postalCode: '2000',
                        country: 'South Africa'
                    }
                },
                metadata: { createdBy: 'test' }
            });

            const saved = await session.save();
            expect(saved._validationResults.addressValidation).toBeDefined();

            // Test the address validation method
            const addressResult = saved.validateAddress();
            expect(addressResult.valid).toBe(true);

            console.log('✅ Address validation working');
        });
    });

    describe('7. Full Validation Method', () => {
        test('runFullValidation should use all functions', async () => {
            const session = new OnboardingSession({
                sessionId: 'ONB_IND_20250218120000_TEST9_tenant-1',
                tenantId: 'tenant-1',
                clientType: 'INDIVIDUAL',
                identityType: 'SA_ID',
                idNumber: '8001015009081',
                clientData: {
                    firstName: 'Full',
                    lastName: 'Validation',
                    dateOfBirth: '1980-01-01',
                    nationality: 'South African',
                    taxNumber: '1234567890',
                    address: {
                        street: '123 Main St',
                        city: 'Johannesburg',
                        postalCode: '2000',
                        country: 'South Africa'
                    }
                },
                metadata: { createdBy: 'test' }
            });

            await session.save();

            // This method uses EVERY validator function
            const results = session.runFullValidation();

            expect(results.identity.identityValid).toBe(true);
            expect(results.tax.valid).toBe(true);
            expect(results.address.valid).toBe(true);
            expect(results.compliance).toBeDefined();
            expect(results.allFunctionsAvailable.validateSAIDNumber).toBe(true);

            console.log('✅ Full validation method uses all functions');
        });
    });

    describe('8. Stage Advancement', () => {
        test('advanceStage should work with string literal data', async () => {
            const session = await OnboardingSession.createSession('tenant-1', {
                clientType: 'INDIVIDUAL',
                clientData: {
                    firstName: 'Stage',
                    lastName: 'Test',
                    dateOfBirth: '1980-01-01',
                    nationality: 'South African'
                }
            }, { createdBy: 'test' });

            await session.advanceStage('CLIENT_INFO', { test: 'data' }, 'tester');

            expect(session.stages).toHaveLength(2);
            expect(session.stages[1].data).toEqual({ test: 'data' });
            expect(session.stages[1].hash).toBeDefined();

            console.log('✅ Stage advancement works with Mixed data');
        });
    });

    describe('9. Document Management', () => {
        test('addDocument and verifyDocument should work', async () => {
            const session = await OnboardingSession.createSession('tenant-1', {
                clientType: 'INDIVIDUAL',
                clientData: {
                    firstName: 'Doc',
                    lastName: 'Test',
                    dateOfBirth: '1980-01-01',
                    nationality: 'South African'
                }
            }, { createdBy: 'test' });

            await session.addDocument({
                documentId: 'DOC-001',
                documentType: 'ID_COPY',
                fileHash: crypto.createHash('sha256').update('test').digest('hex'),
                fileName: 'id.pdf'
            });

            expect(session.documents).toHaveLength(1);

            await session.verifyDocument('DOC-001', { method: 'MANUAL' }, 'verifier');

            expect(session.documents[0].verified).toBe(true);

            console.log('✅ Document management works');
        });
    });

    describe('10. FICA Status Update', () => {
        test('updateFICAStatus should generate references', async () => {
            const session = await OnboardingSession.createSession('tenant-1', {
                clientType: 'INDIVIDUAL',
                clientData: {
                    firstName: 'FICA',
                    lastName: 'Test',
                    dateOfBirth: '1980-01-01',
                    nationality: 'South African'
                }
            }, { createdBy: 'test' });

            await session.updateFICAStatus('APPROVED', {
                riskScore: 25,
                notes: 'All good'
            }, 'compliance');

            expect(session.fica.status).toBe('APPROVED');
            expect(session.fica.reference).toMatch(/^FICA-/);
            expect(session.legalCompliance.complianceReference).toMatch(/^FICA-/);

            console.log('✅ FICA status update generates references');
        });
    });

    describe('11. Risk Assessment', () => {
        test('updateRiskAssessment should calculate EDD requirements', async () => {
            const session = await OnboardingSession.createSession('tenant-1', {
                clientType: 'INDIVIDUAL',
                clientData: {
                    firstName: 'Risk',
                    lastName: 'Test',
                    dateOfBirth: '1980-01-01',
                    nationality: 'South African'
                }
            }, { createdBy: 'test' });

            await session.updateRiskAssessment({
                score: 85,
                factors: [{ factor: 'PEP', score: 40 }]
            }, 'analyst');

            expect(session.risk.score).toBe(85);
            expect(session.risk.level).toBe('HIGH');
            expect(session.legalCompliance.eddRequirements).toBeDefined();

            console.log('✅ Risk assessment calculates EDD requirements');
        });
    });

    describe('12. Compliance Check', () => {
        test('checkCompliance should use both FICA and POPIA checkers', async () => {
            const session = await OnboardingSession.createSession('tenant-1', {
                clientType: 'INDIVIDUAL',
                clientData: {
                    firstName: 'Compliance',
                    lastName: 'Test',
                    dateOfBirth: '1980-01-01',
                    nationality: 'South African'
                }
            }, { createdBy: 'test' });

            const compliance = session.checkCompliance();

            expect(compliance.fica).toBeDefined();
            expect(compliance.popia).toBeDefined();
            expect(compliance.overallCompliant).toBeDefined();

            console.log('✅ Compliance check uses all checkers');
        });
    });

    describe('13. Legal Hold', () => {
        test('placeOnLegalHold and releaseLegalHold should work', async () => {
            const session = await OnboardingSession.createSession('tenant-1', {
                clientType: 'INDIVIDUAL',
                clientData: {
                    firstName: 'Legal',
                    lastName: 'Hold',
                    dateOfBirth: '1980-01-01',
                    nationality: 'South African'
                }
            }, { createdBy: 'test' });

            await session.placeOnLegalHold('Court order #123', 'legal', {
                caseNumber: 'CASE-001'
            });

            expect(session.compliance.legalHold.active).toBe(true);

            await session.releaseLegalHold('legal', 'Case resolved');

            expect(session.compliance.legalHold.active).toBe(false);

            console.log('✅ Legal hold works');
        });
    });

    describe('14. Audit Trail', () => {
        test('verifyAuditTrail should validate integrity', async () => {
            const session = await OnboardingSession.createSession('tenant-1', {
                clientType: 'INDIVIDUAL',
                clientData: {
                    firstName: 'Audit',
                    lastName: 'Trail',
                    dateOfBirth: '1980-01-01',
                    nationality: 'South African'
                }
            }, { createdBy: 'test' });

            await session.advanceStage('CLIENT_INFO', {}, 'user1');
            await session.advanceStage('FICA_SCREENING', {}, 'user2');

            const verification = session.verifyAuditTrail();
            expect(verification.valid).toBe(true);

            console.log('✅ Audit trail verification works');
        });
    });

    describe('15. Export for Discovery', () => {
        test('exportForDiscovery should redact sensitive data', async () => {
            const session = await OnboardingSession.createSession('tenant-1', {
                clientType: 'INDIVIDUAL',
                identityType: 'SA_ID',
                idNumber: '8001015009081',
                clientData: {
                    firstName: 'Export',
                    lastName: 'Test',
                    dateOfBirth: '1980-01-01',
                    nationality: 'South African',
                    taxNumber: '1234567890'
                }
            }, { createdBy: 'test' });

            const exported = session.exportForDiscovery();

            expect(exported.data.idNumber).toBe('[REDACTED]');
            expect(exported.data.clientData.taxNumber).toBe('[REDACTED]');
            expect(exported.metadata.compliance).toBeDefined();

            console.log('✅ Export for discovery redacts sensitive data');
        });
    });

    describe('16. Static Methods', () => {
        beforeEach(async () => {
            await OnboardingSession.createSession('tenant-1', {
                clientType: 'INDIVIDUAL',
                clientData: { firstName: 'User1', lastName: 'Test', dateOfBirth: '1980-01-01', nationality: 'SA' }
            });
            await OnboardingSession.createSession('tenant-1', {
                clientType: 'INDIVIDUAL',
                clientData: { firstName: 'User2', lastName: 'Test', dateOfBirth: '1980-01-01', nationality: 'SA' }
            });
            await OnboardingSession.createSession('tenant-2', {
                clientType: 'COMPANY',
                clientData: {
                    businessName: 'Biz1',
                    registrationNumber: '2020/123456/07',
                    businessType: 'Pty Ltd',
                    dateOfIncorporation: '2020-01-01'
                }
            });
        });

        test('findByTenant should filter correctly', async () => {
            const results = await OnboardingSession.findByTenant('tenant-1');
            expect(results).toHaveLength(2);
        });

        test('getDashboardMetrics should return metrics', async () => {
            const metrics = await OnboardingSession.getDashboardMetrics('tenant-1');
            expect(metrics.totalSessions).toBe(2);
            expect(metrics.activeSessions).toBe(2);
        });

        test('getStatistics should include identity breakdown', async () => {
            const stats = await OnboardingSession.getStatistics('tenant-1');
            expect(stats[0].identityTypeBreakdown).toBeDefined();
        });
    });

    describe('17. STRING-LITERAL SHIELD - Edge Cases', () => {
        test('Should handle empty Mixed fields gracefully', async () => {
            const session = new OnboardingSession({
                sessionId: 'ONB_IND_20250218120000_TEST99_tenant-1',
                tenantId: 'tenant-1',
                clientType: 'INDIVIDUAL',
                identityType: 'SA_ID',
                idNumber: '8001015009081',
                clientData: {
                    firstName: 'Edge',
                    lastName: 'Case',
                    dateOfBirth: '1980-01-01',
                    nationality: 'South African'
                },
                metadata: { createdBy: 'test' },
                _validationResults: {}, // Empty Mixed field
                _encryption: {}, // Empty Mixed field
                _audit: {} // Empty Mixed field
            });

            const saved = await session.save();
            expect(saved._validationResults).toBeDefined();
            expect(saved._encryption).toBeDefined();
            expect(saved._audit).toBeDefined();

            console.log('✅ Empty Mixed fields handled gracefully');
        });
    });
});
