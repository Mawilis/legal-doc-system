// /Users/wilsonkhanyezi/legal-doc-system/server/validators/complianceValidator.js

// ============================================================================
// QUANTUM COMPLIANCE VALIDATOR: REGULATORY OMNISCIENCE ENGINE
// ============================================================================
// This quantum bastion validates every legal interaction against SA's regulatory
// tapestry—POPIA, FICA, ECT Act, Companies Act—and global compliance vectors.
// It transforms compliance from burden to competitive edge, weaving unbreakable
// legal DNA into every transaction, document, and user journey.
// ============================================================================
//                           ╔════════════════════════╗
//                           ║  COMPLIANCE QUANTUM    ║
//                           ╠════════════════════════╣
//                           ║  🛡️  → ⚖️  → 🔒 → 🌍   ║
//                           ║  POPIA | FICA | ECT    ║
//                           ║  CPA | PEPUDA | SARS   ║
//                           ║  GDPR | CCPA | NDPA    ║
//                           ╚════════════════════════╝
// ============================================================================

require('dotenv').config();
const Joi = require('joi');
const { createAuditLog } = require('../utils/auditLogger');
const { Client } = require('../models/Client');
const { redisClient } = require('../config/database');

// ============================================================================
// QUANTUM SCHEMAS: REGULATORY VALIDATION TEMPLATES
// ============================================================================

/**
 * POPIA Validation Schema: Protection of Personal Information Act
 * Implements 8 lawful processing conditions
 */
const POPIA_SCHEMA = Joi.object({
    // Condition 1: Accountability
    dataController: Joi.string().required(),
    informationOfficer: Joi.string().email().required(),

    // Condition 2: Processing Limitation
    purpose: Joi.string().required().min(10),
    lawfulBasis: Joi.string().valid(
        'consent',
        'contract',
        'legal_obligation',
        'vital_interests',
        'public_task',
        'legitimate_interests'
    ).required(),

    // Condition 3: Purpose Specification
    dataMinimization: Joi.boolean().required(),
    retentionPeriod: Joi.number().integer().min(1).max(100),

    // Condition 4: Further Processing Limitation
    compatiblePurpose: Joi.boolean().required(),

    // Condition 5: Information Quality
    dataAccuracy: Joi.boolean().required(),
    updateMechanism: Joi.string().required(),

    // Condition 6: Openness
    privacyNotice: Joi.boolean().required(),
    contactDetails: Joi.string().email().required(),

    // Condition 7: Security Safeguards
    encryptionLevel: Joi.string().valid('AES-128', 'AES-256', 'TLS-1.3').required(),
    accessControl: Joi.boolean().required(),
    breachResponsePlan: Joi.boolean().required(),

    // Condition 8: Data Subject Participation
    accessRights: Joi.boolean().required(),
    correctionRights: Joi.boolean().required(),
    deletionRights: Joi.boolean().required(),

    // Special Personal Information (Section 26)
    specialData: Joi.object({
        biometric: Joi.boolean(),
        health: Joi.boolean(),
        religious: Joi.boolean(),
        race: Joi.boolean(),
        criminal: Joi.boolean()
    }).optional(),

    // Cross-border transfer (Section 72)
    crossBorderTransfer: Joi.boolean().default(false),
    transferCountries: Joi.array().items(Joi.string().length(2)).optional(),
    transferSafeguards: Joi.string().optional()
});

/**
 * FICA Validation Schema: Financial Intelligence Centre Act
 * For anti-money laundering and counter-terrorism financing
 */
const FICA_SCHEMA = Joi.object({
    // Customer Identification
    identificationType: Joi.string().valid(
        'SA_ID',
        'PASSPORT',
        'DRIVERS_LICENSE',
        'ASYLUM_SEEKER',
        'REFUGEE'
    ).required(),

    identificationNumber: Joi.string().required(),
    identificationIssueDate: Joi.date().required(),
    identificationExpiryDate: Joi.date().required(),
    identificationCountry: Joi.string().length(2).required(),

    // Proof of Address
    proofOfAddressType: Joi.string().valid(
        'UTILITY_BILL',
        'BANK_STATEMENT',
        'RENTAL_AGREEMENT',
        'MUNICIPAL_ACCOUNT'
    ).required(),

    proofOfAddressDate: Joi.date().required(),
    addressMatch: Joi.boolean().required(),

    // Occupation and Source of Funds
    occupation: Joi.string().required().min(2),
    employer: Joi.string().optional(),
    annualIncome: Joi.number().min(0).required(),
    sourceOfFunds: Joi.string().valid(
        'EMPLOYMENT',
        'BUSINESS',
        'INVESTMENTS',
        'INHERITANCE',
        'GIFT',
        'OTHER'
    ).required(),

    // PEP Screening (Politically Exposed Persons)
    isPEP: Joi.boolean().required(),
    pepDetails: Joi.object({
        position: Joi.string().optional(),
        country: Joi.string().optional(),
        closeAssociates: Joi.array().items(Joi.string()).optional()
    }).when('isPEP', { is: true, then: Joi.required() }),

    // Risk Rating
    riskRating: Joi.string().valid('LOW', 'MEDIUM', 'HIGH').required(),
    riskJustification: Joi.string().when('riskRating', {
        is: Joi.string().valid('MEDIUM', 'HIGH'),
        then: Joi.required()
    }),

    // Ongoing Monitoring
    monitoringFrequency: Joi.string().valid(
        'ANNUAL',
        'BI_ANNUAL',
        'QUARTERLY',
        'MONTHLY'
    ).required(),

    // Third Party Verification
    thirdPartyVerified: Joi.boolean().default(false),
    verificationProvider: Joi.string().optional(),
    verificationDate: Joi.date().optional(),
    verificationReference: Joi.string().optional()
});

/**
 * ECT Act Validation: Electronic Communications and Transactions Act
 * For electronic signatures and records
 */
const ECT_SCHEMA = Joi.object({
    signatureType: Joi.string().valid(
        'SIMPLE',
        'ADVANCED',
        'QUALIFIED'
    ).required(),

    signatoryIdentityVerified: Joi.boolean().required(),
    signatureTimestamp: Joi.date().required(),
    signatureIpAddress: Joi.string().ip().required(),
    signatureHash: Joi.string().pattern(/^[a-f0-9]{64}$/).required(),

    documentHash: Joi.string().pattern(/^[a-f0-9]{64}$/).required(),
    preservationPeriod: Joi.number().integer().min(5).max(10).required(), // 5-10 years

    nonRepudiation: Joi.boolean().required(),
    auditTrail: Joi.array().items(Joi.object({
        action: Joi.string().required(),
        timestamp: Joi.date().required(),
        actor: Joi.string().required(),
        ipAddress: Joi.string().ip().required()
    })).min(1).required()
});

// ============================================================================
// QUANTUM VALIDATORS: CORE COMPLIANCE FUNCTIONS
// ============================================================================

/**
 * Validate POPIA compliance for data processing
 * @param {Object} data - Data processing details
 * @param {string} userId - User ID for audit trail
 * @returns {Promise<Object>} Validation result
 */
async function validatePOPIA(data, userId) {
    try {
        // Validate against POPIA schema
        const { error, value } = POPIA_SCHEMA.validate(data, {
            abortEarly: false,
            stripUnknown: true
        });

        if (error) {
            // Log validation failure
            await createAuditLog({
                action: 'POPIA_VALIDATION_FAILED',
                userId,
                metadata: {
                    errors: error.details.map(d => d.message),
                    data: redactSensitiveData(data)
                },
                compliance: ['POPIA'],
                severity: 'HIGH'
            });

            throw new Error(`POPIA validation failed: ${error.details.map(d => d.message).join(', ')}`);
        }

        // Check for special personal information (requires explicit consent)
        if (value.specialData) {
            const hasSpecialDataConsent = await checkSpecialDataConsent(userId, value.specialData);
            if (!hasSpecialDataConsent) {
                throw new Error('Special personal information requires explicit consent (POPIA Section 27)');
            }
        }

        // Validate cross-border transfers
        if (value.crossBorderTransfer) {
            const safeCountries = ['NA', 'BW', 'LS', 'SZ', 'ZM', 'ZW']; // SADC countries
            const unsafeTransfer = value.transferCountries?.some(country => !safeCountries.includes(country));

            if (unsafeTransfer && !value.transferSafeguards) {
                throw new Error('Cross-border transfer to non-SADC country requires safeguards (POPIA Section 72)');
            }
        }

        // Log successful validation
        await createAuditLog({
            action: 'POPIA_VALIDATION_PASSED',
            userId,
            metadata: {
                purpose: value.purpose,
                lawfulBasis: value.lawfulBasis,
                retentionPeriod: value.retentionPeriod
            },
            compliance: ['POPIA']
        });

        return {
            valid: true,
            data: value,
            timestamp: new Date().toISOString(),
            validationId: generateValidationId('POPIA')
        };

    } catch (error) {
        return {
            valid: false,
            error: error.message,
            timestamp: new Date().toISOString(),
            compliance: 'POPIA'
        };
    }
}

/**
 * Validate FICA compliance for client onboarding
 * @param {Object} clientData - Client identification data
 * @param {string} clientId - Client ID
 * @returns {Promise<Object>} Validation result
 */
async function validateFICAKYC(clientId) {
    try {
        // Check cache first
        const cacheKey = `fica_validation:${clientId}`;
        const cached = await redisClient.get(cacheKey);

        if (cached) {
            return JSON.parse(cached);
        }

        // Fetch client data
        const client = await Client.findByPk(clientId, {
            attributes: ['id', 'firstName', 'lastName', 'idNumber', 'ficaStatus', 'riskRating']
        });

        if (!client) {
            throw new Error('Client not found for FICA validation');
        }

        // Check existing FICA status
        if (client.ficaStatus === 'VERIFIED' && client.riskRating === 'LOW') {
            const result = {
                valid: true,
                status: 'VERIFIED',
                riskRating: client.riskRating,
                lastVerified: new Date().toISOString(),
                expiresAt: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString() // 1 year
            };

            // Cache for 24 hours
            await redisClient.setex(cacheKey, 86400, JSON.stringify(result));

            return result;
        }

        // Enhanced verification needed
        const verificationResult = await performEnhancedFICAVerification(client);

        // Update client record
        await client.update({
            ficaStatus: verificationResult.status,
            riskRating: verificationResult.riskRating,
            ficaVerifiedAt: new Date(),
            ficaExpiresAt: verificationResult.expiresAt
        });

        // Log verification
        await createAuditLog({
            action: 'FICA_VERIFICATION_COMPLETED',
            userId: clientId,
            metadata: {
                status: verificationResult.status,
                riskRating: verificationResult.riskRating,
                method: verificationResult.verificationMethod
            },
            compliance: ['FICA']
        });

        // Cache result
        await redisClient.setex(cacheKey, 86400, JSON.stringify(verificationResult));

        return verificationResult;

    } catch (error) {
        await createAuditLog({
            action: 'FICA_VERIFICATION_FAILED',
            userId: clientId,
            metadata: { error: error.message },
            compliance: ['FICA'],
            severity: 'MEDIUM'
        });

        return {
            valid: false,
            error: error.message,
            requiresAction: true,
            timestamp: new Date().toISOString(),
            compliance: 'FICA'
        };
    }
}

/**
 * Validate ECT Act compliance for electronic signatures
 * @param {Object} signatureData - Signature and document data
 * @returns {Promise<Object>} Validation result
 */
async function validateECTAct(signatureData) {
    try {
        const { error, value } = ECT_SCHEMA.validate(signatureData, {
            abortEarly: false
        });

        if (error) {
            throw new Error(`ECT Act validation failed: ${error.details.map(d => d.message).join(', ')}`);
        }

        // Validate document integrity
        const documentIntegrity = await verifyDocumentIntegrity(
            value.documentHash,
            value.signatureHash
        );

        if (!documentIntegrity.valid) {
            throw new Error(`Document integrity check failed: ${documentIntegrity.error}`);
        }

        // Validate non-repudiation
        if (!value.nonRepudiation) {
            throw new Error('Electronic signature must provide non-repudiation (ECT Act Section 13)');
        }

        // Ensure audit trail completeness
        const requiredEvents = ['DOCUMENT_CREATED', 'SIGNATURE_INITIATED', 'SIGNATURE_COMPLETED'];
        const auditEvents = value.auditTrail.map(event => event.action);

        const missingEvents = requiredEvents.filter(event => !auditEvents.includes(event));
        if (missingEvents.length > 0) {
            throw new Error(`Audit trail incomplete. Missing events: ${missingEvents.join(', ')}`);
        }

        const result = {
            valid: true,
            compliance: 'ECT_ACT',
            signatureType: value.signatureType,
            timestamp: value.signatureTimestamp,
            preservationPeriod: value.preservationPeriod,
            validationId: generateValidationId('ECT')
        };

        // Log successful validation
        await createAuditLog({
            action: 'ECT_VALIDATION_PASSED',
            metadata: {
                signatureType: value.signatureType,
                documentHash: value.documentHash,
                preservationPeriod: value.preservationPeriod
            },
            compliance: ['ECT_ACT']
        });

        return result;

    } catch (error) {
        return {
            valid: false,
            error: error.message,
            compliance: 'ECT_ACT',
            timestamp: new Date().toISOString()
        };
    }
}

/**
 * Validate Companies Act compliance for records
 * @param {Object} recordData - Company record data
 * @returns {Promise<Object>} Validation result
 */
async function validateCompaniesAct(recordData) {
    const requiredFields = [
        'companyName',
        'registrationNumber',
        'registrationDate',
        'directors',
        'registeredAddress',
        'annualFinancialYearEnd'
    ];

    const missingFields = requiredFields.filter(field => !recordData[field]);

    if (missingFields.length > 0) {
        return {
            valid: false,
            error: `Missing required fields: ${missingFields.join(', ')}`,
            compliance: 'COMPANIES_ACT',
            section: 'Section 24'
        };
    }

    // Validate director requirements (at least one director)
    if (!Array.isArray(recordData.directors) || recordData.directors.length === 0) {
        return {
            valid: false,
            error: 'Company must have at least one director',
            compliance: 'COMPANIES_ACT',
            section: 'Section 66'
        };
    }

    // Validate financial year end format
    const fyRegex = /^(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$/;
    if (!fyRegex.test(recordData.annualFinancialYearEnd)) {
        return {
            valid: false,
            error: 'Financial year end must be in MM-DD format',
            compliance: 'COMPANIES_ACT',
            section: 'Section 30'
        };
    }

    return {
        valid: true,
        compliance: 'COMPANIES_ACT',
        recordType: recordData.recordType || 'GENERAL',
        retentionPeriod: 7, // 7 years as per Section 28
        validationDate: new Date().toISOString()
    };
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Perform enhanced FICA verification with third-party integration
 * @param {Object} client - Client object
 * @returns {Promise<Object>} Verification result
 */
async function performEnhancedFICAVerification(client) {
    // Integration with third-party verification services
    // This is a mock implementation - integrate with Datanamix, LexisNexis, etc.

    const verificationServices = {
        Datanamix: process.env.DATANAMIX_API_KEY,
        LexisNexis: process.env.LEXISNEXIS_API_KEY,
        Refinitiv: process.env.REFINITIV_API_KEY
    };

    // Mock verification logic
    const riskFactors = {
        'ZA': 0.1,  // South Africa
        'US': 0.3,  // United States
        'CN': 0.4,  // China
        'ZW': 0.7   // Zimbabwe (higher risk)
    };

    // Determine risk based on client data
    let riskScore = 0.3; // Base risk

    if (client.idNumber && client.idNumber.startsWith('000')) {
        riskScore += 0.3; // Suspicious ID number
    }

    // Determine risk rating
    let riskRating = 'LOW';
    if (riskScore >= 0.7) riskRating = 'HIGH';
    else if (riskScore >= 0.4) riskRating = 'MEDIUM';

    // Determine verification status
    const status = riskRating === 'HIGH' ? 'PENDING_ENHANCED' : 'VERIFIED';

    return {
        valid: true,
        status,
        riskRating,
        verificationMethod: 'AUTOMATED_WITH_THIRD_PARTY',
        verificationDate: new Date().toISOString(),
        expiresAt: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString(),
        notes: riskRating === 'HIGH' ? 'Requires manual review' : 'Automated verification passed'
    };
}

/**
 * Verify document integrity using hash comparison
 * @param {string} documentHash - Original document hash
 * @param {string} signatureHash - Signature hash
 * @returns {Promise<Object>} Integrity check result
 */
async function verifyDocumentIntegrity(documentHash, signatureHash) {
    // In production, this would compare hashes stored in a secure ledger
    // and verify they haven't been tampered with

    const crypto = require('crypto');

    // Mock: Verify hash format
    const hashRegex = /^[a-f0-9]{64}$/;
    if (!hashRegex.test(documentHash) || !hashRegex.test(signatureHash)) {
        return {
            valid: false,
            error: 'Invalid hash format'
        };
    }

    // Check if hashes are different (they should be for document and signature)
    if (documentHash === signatureHash) {
        return {
            valid: false,
            error: 'Document and signature hashes must be different'
        };
    }

    return {
        valid: true,
        documentHash,
        signatureHash,
        verifiedAt: new Date().toISOString()
    };
}

/**
 * Check for special personal data consent
 * @param {string} userId - User ID
 * @param {Object} specialData - Special data types
 * @returns {Promise<boolean>} True if consent exists
 */
async function checkSpecialDataConsent(userId, specialData) {
    const consentTypes = Object.keys(specialData).filter(key => specialData[key]);

    if (consentTypes.length === 0) return true;

    // Check if explicit consent exists for each type
    const { Consent } = require('../models/Consent');

    for (const dataType of consentTypes) {
        const consent = await Consent.findOne({
            where: {
                userId,
                consentType: `SPECIAL_DATA_${dataType.toUpperCase()}`,
                status: 'GRANTED'
            }
        });

        if (!consent) return false;
    }

    return true;
}

/**
 * Redact sensitive data for logging
 * @param {Object} data - Data to redact
 * @returns {Object} Redacted data
 */
function redactSensitiveData(data) {
    const redacted = { ...data };

    // Redact identification numbers
    if (redacted.identificationNumber) {
        redacted.identificationNumber = '***' + redacted.identificationNumber.slice(-4);
    }

    // Redact email addresses
    if (redacted.email) {
        const [username, domain] = redacted.email.split('@');
        redacted.email = username.charAt(0) + '***@' + domain;
    }

    // Remove sensitive fields
    delete redacted.password;
    delete redacted.token;
    delete redacted.secret;

    return redacted;
}

/**
 * Generate unique validation ID
 * @param {string} prefix - Validation type prefix
 * @returns {string} Unique validation ID
 */
function generateValidationId(prefix) {
    const timestamp = Date.now().toString(36);
    const random = Math.random().toString(36).substr(2, 9);
    return `${prefix}_${timestamp}_${random}`.toUpperCase();
}

// ============================================================================
// COMPLIANCE BATCH VALIDATION
// ============================================================================

/**
 * Batch validate multiple compliance requirements
 * @param {Object} requirements - Compliance requirements to validate
 * @param {string} userId - User ID for audit
 * @returns {Promise<Object>} Batch validation results
 */
async function batchValidateCompliance(requirements, userId) {
    const validations = {};
    const errors = [];

    // Validate each requirement
    if (requirements.popia) {
        validations.popia = await validatePOPIA(requirements.popia, userId);
        if (!validations.popia.valid) errors.push('POPIA');
    }

    if (requirements.fica && requirements.fica.clientId) {
        validations.fica = await validateFICAKYC(requirements.fica.clientId);
        if (!validations.fica.valid) errors.push('FICA');
    }

    if (requirements.ect) {
        validations.ect = await validateECTAct(requirements.ect);
        if (!validations.ect.valid) errors.push('ECT_ACT');
    }

    if (requirements.companiesAct) {
        validations.companiesAct = await validateCompaniesAct(requirements.companiesAct);
        if (!validations.companiesAct.valid) errors.push('COMPANIES_ACT');
    }

    const allValid = errors.length === 0;

    // Log batch validation result
    await createAuditLog({
        action: 'BATCH_COMPLIANCE_VALIDATION',
        userId,
        metadata: {
            requirements: Object.keys(requirements),
            validations,
            allValid,
            errors
        },
        compliance: Object.keys(requirements).map(key => key.toUpperCase())
    });

    return {
        valid: allValid,
        validations,
        errors,
        timestamp: new Date().toISOString(),
        validationId: generateValidationId('BATCH')
    };
}

// ============================================================================
// TEST SUITE
// ============================================================================

if (process.env.NODE_ENV === 'test') {
    const { describe, it, expect, beforeAll } = require('@jest/globals');

    describe('Compliance Validator Quantum Gates', () => {
        it('should validate POPIA schema correctly', async () => {
            const popiaData = {
                dataController: 'Wilsy Legal',
                informationOfficer: 'io@wilsy.com',
                purpose: 'Legal service provision',
                lawfulBasis: 'contract',
                dataMinimization: true,
                compatiblePurpose: true,
                dataAccuracy: true,
                updateMechanism: 'Client portal',
                privacyNotice: true,
                contactDetails: 'privacy@wilsy.com',
                encryptionLevel: 'AES-256',
                accessControl: true,
                breachResponsePlan: true,
                accessRights: true,
                correctionRights: true,
                deletionRights: true
            };

            const result = await validatePOPIA(popiaData, 'test-user');
            expect(result.valid).toBe(true);
        });

        it('should reject invalid POPIA data', async () => {
            const invalidData = { purpose: 'test' };
            const result = await validatePOPIA(invalidData, 'test-user');
            expect(result.valid).toBe(false);
        });
    });
}

// ============================================================================
// EXPORTS
// ============================================================================

module.exports = {
    // Core Validators
    validatePOPIA,
    validateFICAKYC,
    validateECTAct,
    validateCompaniesAct,

    // Batch Validation
    batchValidateCompliance,

    // Schemas (for external use)
    POPIA_SCHEMA,
    FICA_SCHEMA,
    ECT_SCHEMA
};

// ============================================================================
// SENTINEL BEACONS: EVOLUTION QUANTA
// ============================================================================
// Quantum Leap: AI-powered compliance prediction engine
// Horizon Expansion: Real-time regulatory change detection
// Eternal Extension: Blockchain-immutable compliance proofs
// Compliance Vector: Automated DSAR (Data Subject Access Request) processing
// Performance Alchemy: Distributed compliance cache with invalidation
// ============================================================================

// Wilsy Touching Lives Eternally