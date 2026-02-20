
/*╔══════════════════════════════════════════════════════════════════════════════╗
  ║ FICA VALIDATORS - INVESTOR-GRADE ● FORENSIC ● PRODUCTION                    ║
  ║ Financial Intelligence Centre Act 38 of 2001 Compliant                      ║
  ║ Version: 2.0.0 - PRODUCTION - ALL FUNCTIONS DECLARED AND EXPORTED           ║
  ╚══════════════════════════════════════════════════════════════════════════════╝*/

'use strict';

const crypto = require('crypto');

// =================================================================================================================
// PRIVATE HELPER FUNCTIONS
// =================================================================================================================

/**
 * Luhn algorithm implementation for ID validation (PRIVATE - not exported)
 */
function _validateLuhn(idNumber) {
    let sum = 0;
    let alternate = false;

    for (let i = idNumber.length - 1; i >= 0; i--) {
        let digit = parseInt(idNumber.charAt(i), 10);

        if (alternate) {
            digit *= 2;
            if (digit > 9) {
                digit = (digit % 10) + 1;
            }
        }

        sum += digit;
        alternate = !alternate;
    }

    return sum % 10 === 0;
}

/**
 * Validate date components (PRIVATE - not exported)
 */
function _validateDate(year, month, day) {
    if (month < 1 || month > 12) {
        throw new Error('Invalid birth month in ID number');
    }

    const daysInMonth = new Date(year, month, 0).getDate();
    if (day < 1 || day > daysInMonth) {
        throw new Error('Invalid birth day in ID number');
    }

    return true;
}

/**
 * Validate passport format (PRIVATE - not exported)
 */
function _validatePassportFormat(passportNumber) {
    if (!passportNumber || passportNumber.length < 6 || passportNumber.length > 20) {
        throw new Error('Passport number must be between 6-20 characters');
    }
    if (!/^[A-Z0-9]+$/.test(passportNumber.toUpperCase())) {
        throw new Error('Passport number must be alphanumeric');
    }
    return true;
}

// =================================================================================================================
// EXPORTED VALIDATION FUNCTIONS
// =================================================================================================================

/**
 * Validate South African ID number according to Home Affairs standards
 * Implements Luhn algorithm and SA ID format validation
 * @param {string} idNumber - The SA ID number to validate
 * @returns {Object} Validation result with birth date, gender, and citizenship
 * @throws {Error} If validation fails
 */
exports.validateSAIDNumber = (idNumber) => {
    if (!idNumber) {
        throw new Error('ID number is required');
    }

    // Remove any spaces or special characters
    const cleanId = idNumber.toString().replace(/\s+/g, '');

    // Check length (13 digits for SA ID)
    if (cleanId.length !== 13) {
        throw new Error(`Invalid ID number length: expected 13 digits, got ${cleanId.length}`);
    }

    // Check if all characters are digits
    if (!/^\d+$/.test(cleanId)) {
        throw new Error('ID number must contain only digits');
    }

    // Extract birth date (YYMMDD)
    const year = parseInt(cleanId.substring(0, 2), 10);
    const month = parseInt(cleanId.substring(2, 4), 10);
    const day = parseInt(cleanId.substring(4, 6), 10);

    // Validate date using private helper
    _validateDate(year, month, day);

    // Validate citizenship (0 = SA citizen, 1 = permanent resident)
    const citizenship = parseInt(cleanId.substring(10, 11), 10);
    if (![0, 1].includes(citizenship)) {
        throw new Error('Invalid citizenship digit in ID number');
    }

    // Validate gender digit (should be between 0-9)
    const genderDigit = parseInt(cleanId.substring(6, 10), 10);
    if (isNaN(genderDigit)) {
        throw new Error('Invalid gender sequence in ID number');
    }

    // Luhn algorithm check
    if (!_validateLuhn(cleanId)) {
        throw new Error('ID number failed checksum validation');
    }

    const fullYear = year < 20 ? 2000 + year : 1900 + year;

    return {
        isValid: true,
        birthDate: new Date(fullYear, month - 1, day),
        birthDateString: `${fullYear}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`,
        gender: genderDigit >= 5000 ? 'MALE' : 'FEMALE',
        citizenship: citizenship === 0 ? 'CITIZEN' : 'PERMANENT_RESIDENT',
        age: new Date().getFullYear() - fullYear
    };
};

/**
 * Validate business registration number (CIPC format)
 * @param {string} regNumber - The registration number to validate
 * @returns {Object} Validation result with registration year and format
 * @throws {Error} If validation fails
 */
exports.validateBusinessRegistration = (regNumber) => {
    if (!regNumber) {
        throw new Error('Registration number is required');
    }

    const cleanReg = regNumber.toString().replace(/\s+/g, '').toUpperCase();

    // Check formats: YYYY/XXXXXX/XX or YYYY/XXXXXX
    const formats = [
        /^\d{4}\/\d{6}\/\d{2}$/,  // Companies Act format
        /^\d{4}\/\d{6}$/           // Close corporation format
    ];

    if (!formats.some(format => format.test(cleanReg))) {
        throw new Error('Invalid registration number format. Expected YYYY/XXXXXX/XX or YYYY/XXXXXX');
    }

    // Extract year
    const year = parseInt(cleanReg.substring(0, 4), 10);
    const currentYear = new Date().getFullYear();

    if (year < 1900 || year > currentYear) {
        throw new Error(`Invalid registration year: ${year}`);
    }

    // Extract sequence number
    const sequence = cleanReg.includes('/') ? cleanReg.split('/')[1] : '';

    return {
        isValid: true,
        registrationYear: year,
        sequenceNumber: sequence,
        format: cleanReg.includes('/') ?
            (cleanReg.split('/').length === 3 ? 'COMPANIES_ACT' : 'CLOSE_CORPORATION') :
            'UNKNOWN',
        age: currentYear - year
    };
};

/**
 * Validate tax number (SARS format)
 * @param {string} taxNumber - The tax number to validate
 * @returns {Object} Validation result
 * @throws {Error} If validation fails
 */
exports.validateTaxNumber = (taxNumber) => {
    if (!taxNumber) {
        throw new Error('Tax number is required');
    }

    const cleanTax = taxNumber.toString().replace(/\s+/g, '');

    // SARS tax numbers are typically 10 digits
    if (cleanTax.length !== 10) {
        throw new Error(`Invalid tax number length: expected 10 digits, got ${cleanTax.length}`);
    }

    if (!/^\d+$/.test(cleanTax)) {
        throw new Error('Tax number must contain only digits');
    }

    // SARS tax numbers usually start with a specific prefix
    const firstDigit = parseInt(cleanTax.charAt(0), 10);
    if (firstDigit < 0 || firstDigit > 9) {
        throw new Error('Invalid tax number format');
    }

    return {
        isValid: true,
        taxNumber: cleanTax,
        maskedNumber: `******${cleanTax.slice(-4)}`,
        format: 'SARS_10_DIGIT'
    };
};

/**
 * Validate proof of address (POPIA compliance)
 * @param {Object} address - The address object to validate
 * @returns {boolean} True if valid
 * @throws {Error} If validation fails
 */
exports.validateProofOfAddress = (address) => {
    if (!address || typeof address !== 'object') {
        throw new Error('Address must be an object');
    }

    const required = ['street', 'city', 'postalCode', 'country'];
    const missing = [];

    for (const field of required) {
        if (!address[field]) {
            missing.push(field);
        }
    }

    if (missing.length > 0) {
        throw new Error(`Invalid address: missing required fields: ${missing.join(', ')}`);
    }

    // Validate postal code (SA format)
    if (address.country === 'South Africa' || address.country === 'ZA') {
        if (!/^\d{4}$/.test(address.postalCode.toString())) {
            throw new Error('Invalid South African postal code: expected 4 digits');
        }
    }

    // Validate street address not too short
    if (address.street.length < 5) {
        throw new Error('Street address is too short');
    }

    // Validate city name
    if (address.city.length < 2) {
        throw new Error('City name is too short');
    }

    return {
        isValid: true,
        normalizedCountry: address.country === 'ZA' ? 'South Africa' : address.country,
        postalCodeValid: true
    };
};

/**
 * Validate passport number
 * @param {string} passportNumber - The passport number to validate
 * @param {string} countryOfIssue - The country that issued the passport
 * @returns {Object} Validation result
 * @throws {Error} If validation fails
 */
exports.validatePassport = (passportNumber, countryOfIssue) => {
    if (!passportNumber) {
        throw new Error('Passport number is required');
    }

    if (!countryOfIssue) {
        throw new Error('Country of issue is required');
    }

    _validatePassportFormat(passportNumber);

    return {
        isValid: true,
        passportNumber: passportNumber.toUpperCase(),
        countryOfIssue: countryOfIssue,
        maskedNumber: `******${passportNumber.slice(-4)}`
    };
};

/**
 * Validate identity document based on type
 * @param {string} identityType - The type of identity document
 * @param {string} identityNumber - The identity number
 * @param {string} countryOfIssue - Country of issue (for passports)
 * @returns {Object} Validation result
 * @throws {Error} If validation fails
 */
exports.validateIdentity = (identityType, identityNumber, countryOfIssue = null) => {
    if (!identityType) {
        throw new Error('Identity type is required');
    }

    switch (identityType) {
        case 'SA_ID':
            return exports.validateSAIDNumber(identityNumber);
        case 'PASSPORT':
            return exports.validatePassport(identityNumber, countryOfIssue);
        case 'REFUGEE_ID':
        case 'ASYLUM_SEEKER':
            // Basic validation for refugee/asylum documents
            if (!identityNumber || identityNumber.length < 5) {
                throw new Error('Invalid refugee/asylum document number');
            }
            return {
                isValid: true,
                identityType,
                identityNumber,
                countryOfIssue
            };
        case 'DRIVERS_LICENSE':
            // Basic validation for driver's license
            if (!identityNumber || identityNumber.length < 5) {
                throw new Error('Invalid driver\'s license number');
            }
            return {
                isValid: true,
                identityType,
                identityNumber
            };
        default:
            throw new Error(`Unsupported identity type: ${identityType}`);
    }
};

// =================================================================================================================
// GENERATOR FUNCTIONS
// =================================================================================================================

/**
 * Generate FICA reference number
 * @param {string} sessionId - The session ID to base the reference on
 * @returns {string} FICA reference number
 */
exports.generateFICARefNumber = (sessionId) => {
    if (!sessionId) {
        throw new Error('Session ID is required to generate FICA reference');
    }

    const date = new Date().toISOString().slice(0, 10).replace(/-/g, '');
    const random = crypto.randomBytes(4).toString('hex').toUpperCase();
    const sessionHash = crypto
        .createHash('md5')
        .update(sessionId)
        .digest('hex')
        .substring(0, 8)
        .toUpperCase();

    return `FICA-${date}-${sessionHash}-${random}`;
};

/**
 * Generate POPIA consent reference
 * @param {string} userId - The user ID to base the reference on
 * @returns {string} POPIA consent reference
 */
exports.generatePOPIAConsentRef = (userId) => {
    if (!userId) {
        throw new Error('User ID is required to generate POPIA reference');
    }

    const date = new Date().toISOString().slice(0, 10).replace(/-/g, '');
    const userHash = crypto
        .createHash('md5')
        .update(userId)
        .digest('hex')
        .substring(0, 8)
        .toUpperCase();

    return `POPIA-${date}-${userHash}`;
};

/**
 * Generate compliance reference number
 * @param {string} prefix - Reference prefix (FICA, POPIA, etc.)
 * @param {string} entityId - Entity ID to include in reference
 * @returns {string} Compliance reference
 */
exports.generateComplianceRef = (prefix, entityId) => {
    if (!prefix || !entityId) {
        throw new Error('Prefix and entity ID are required');
    }

    const date = new Date().toISOString().slice(0, 10).replace(/-/g, '');
    const random = crypto.randomBytes(3).toString('hex').toUpperCase();
    const entityHash = crypto
        .createHash('md5')
        .update(entityId)
        .digest('hex')
        .substring(0, 6)
        .toUpperCase();

    return `${prefix}-${date}-${entityHash}-${random}`;
};

// =================================================================================================================
// RISK ASSESSMENT FUNCTIONS
// =================================================================================================================

/**
 * Calculate risk score based on client data
 * @param {string} clientType - The type of client (INDIVIDUAL, COMPANY, etc.)
 * @param {Object} clientData - Client data including risk factors
 * @returns {Object} Risk assessment with score, factors, and level
 */
exports.calculateRiskScore = (clientType, clientData) => {
    if (!clientType) {
        throw new Error('Client type is required for risk assessment');
    }

    let score = 0;
    const factors = [];

    // Base risk by client type
    switch (clientType) {
        case 'COMPANY':
        case 'TRUST':
            score += 30;
            factors.push({
                factor: 'entity_type',
                score: 30,
                description: 'Enhanced due diligence required for business entities',
                weight: 'HIGH'
            });
            break;
        case 'INDIVIDUAL':
            score += 10;
            factors.push({
                factor: 'entity_type',
                score: 10,
                description: 'Standard due diligence for individuals',
                weight: 'LOW'
            });
            break;
        default:
            score += 20;
            factors.push({
                factor: 'entity_type',
                score: 20,
                description: 'Medium due diligence for other entity types',
                weight: 'MEDIUM'
            });
    }

    // Geographic risk
    if (clientData.countryOfResidence && clientData.countryOfResidence !== 'South Africa') {
        score += 20;
        factors.push({
            factor: 'geographic_risk',
            score: 20,
            description: `Foreign national from ${clientData.countryOfResidence}`,
            country: clientData.countryOfResidence,
            weight: 'MEDIUM'
        });
    }

    // PEP check (Politically Exposed Person)
    if (clientData.isPoliticallyExposed) {
        score += 40;
        factors.push({
            factor: 'pep_risk',
            score: 40,
            description: 'Politically exposed person - enhanced due diligence required',
            weight: 'CRITICAL'
        });
    }

    // Income/wealth check
    if (clientData.annualIncome) {
        if (clientData.annualIncome > 10000000) { // R10M+
            score += 15;
            factors.push({
                factor: 'high_net_worth',
                score: 15,
                description: 'High net worth individual (>R10M annual income)',
                weight: 'MEDIUM'
            });
        } else if (clientData.annualIncome > 5000000) { // R5M-R10M
            score += 10;
            factors.push({
                factor: 'high_net_worth',
                score: 10,
                description: 'Affluent individual (R5M-R10M annual income)',
                weight: 'LOW'
            });
        }
    }

    // Industry risk
    const highRiskIndustries = ['GAMBLING', 'CRYPTO', 'WEAPONS', 'ADULT_ENTERTAINMENT'];
    if (clientData.industry && highRiskIndustries.includes(clientData.industry)) {
        score += 25;
        factors.push({
            factor: 'industry_risk',
            score: 25,
            description: `High risk industry: ${clientData.industry}`,
            weight: 'HIGH'
        });
    }

    // Source of funds risk
    const highRiskFundSources = ['CRYPTO', 'CASH', 'FOREIGN'];
    if (clientData.sourceOfFunds && highRiskFundSources.includes(clientData.sourceOfFunds)) {
        score += 15;
        factors.push({
            factor: 'funds_source_risk',
            score: 15,
            description: `High risk source of funds: ${clientData.sourceOfFunds}`,
            weight: 'MEDIUM'
        });
    }

    // Determine risk level
    let level = 'LOW';
    if (score >= 75) {
        level = 'CRITICAL';
    } else if (score >= 50) {
        level = 'HIGH';
    } else if (score >= 25) {
        level = 'MEDIUM';
    }

    return {
        score: Math.min(score, 100),
        factors,
        level,
        requiresEnhancedDueDiligence: score >= 50,
        requiresApproval: score >= 75,
        requiresEscalation: score >= 90,
        timestamp: new Date().toISOString()
    };
};

/**
 * Calculate enhanced due diligence requirements
 * @param {Object} riskAssessment - The risk assessment result
 * @returns {Object} EDD requirements
 */
exports.calculateEDDRequirements = (riskAssessment) => {
    if (!riskAssessment) {
        throw new Error('Risk assessment is required');
    }

    const requirements = {
        sourceOfWealthVerification: false,
        sourceOfFundsVerification: false,
        beneficialOwnership: false,
        independentDirectorInterview: false,
        siteVisit: false,
        externalVerification: false
    };

    if (riskAssessment.score >= 75) {
        requirements.sourceOfWealthVerification = true;
        requirements.sourceOfFundsVerification = true;
        requirements.beneficialOwnership = true;
        requirements.externalVerification = true;
    }

    if (riskAssessment.score >= 90) {
        requirements.independentDirectorInterview = true;
        requirements.siteVisit = true;
    }

    return requirements;
};

// =================================================================================================================
// COMPLIANCE CHECK FUNCTIONS
// =================================================================================================================

/**
 * Check if client is fully FICA compliant
 * @param {Object} session - The onboarding session
 * @returns {Object} Compliance status
 */
exports.checkFICACompliance = (session) => {
    if (!session) {
        throw new Error('Session is required');
    }

    const checks = {
        identityVerified: false,
        addressVerified: false,
        riskAssessed: false,
        ficaReferenceGenerated: false,
        documentsVerified: false
    };

    // Check identity verification
    if (session.identityType &&
        ((session.identityType === 'SA_ID' && session.idNumber) ||
            (session.identityType === 'PASSPORT' && session.passportNumber && session.countryOfIssue))) {
        checks.identityVerified = true;
    }

    // Check address verification
    if (session.clientData?.address && session.clientData.addressVerified) {
        checks.addressVerified = true;
    }

    // Check risk assessment
    if (session.risk && session.risk.score !== undefined) {
        checks.riskAssessed = true;
    }

    // Check FICA reference
    if (session.fica?.reference) {
        checks.ficaReferenceGenerated = true;
    }

    // Check document verification
    if (session.documents && session.documents.length > 0) {
        checks.documentsVerified = session.documents.every(doc => doc.verified === true);
    }

    const allChecksPassed = Object.values(checks).every(value => value === true);

    return {
        isCompliant: allChecksPassed,
        checks,
        missingRequirements: Object.entries(checks)
            .filter(([_, value]) => !value)
            .map(([key]) => key),
        timestamp: new Date().toISOString()
    };
};

/**
 * Check if client is POPIA compliant
 * @param {Object} session - The onboarding session
 * @returns {Object} POPIA compliance status
 */
exports.checkPOPIACompliance = (session) => {
    if (!session) {
        throw new Error('Session is required');
    }

    const checks = {
        consentObtained: false,
        consentRecorded: false,
        purposeSpecified: false,
        dataMinimized: false,
        retentionPolicyApplied: false
    };

    if (session.legalCompliance?.popiaCompliant) {
        checks.consentObtained = true;
        checks.consentRecorded = true;
    }

    if (session.legalCompliance?.popiaReference) {
        checks.consentRecorded = true;
    }

    if (session.clientData?.processingPurpose) {
        checks.purposeSpecified = true;
    }

    if (session.expiresAt) {
        checks.retentionPolicyApplied = true;
    }

    const allChecksPassed = Object.values(checks).every(value => value === true);

    return {
        isCompliant: allChecksPassed,
        checks,
        missingRequirements: Object.entries(checks)
            .filter(([_, value]) => !value)
            .map(([key]) => key),
        timestamp: new Date().toISOString()
    };
};

// =================================================================================================================
// EXPORT ALL FUNCTIONS (EXPLICITLY)
// =================================================================================================================

module.exports = {
    // Validation functions
    validateSAIDNumber: exports.validateSAIDNumber,
    validateBusinessRegistration: exports.validateBusinessRegistration,
    validateTaxNumber: exports.validateTaxNumber,
    validateProofOfAddress: exports.validateProofOfAddress,
    validatePassport: exports.validatePassport,
    validateIdentity: exports.validateIdentity,

    // Generator functions
    generateFICARefNumber: exports.generateFICARefNumber,
    generatePOPIAConsentRef: exports.generatePOPIAConsentRef,
    generateComplianceRef: exports.generateComplianceRef,

    // Risk assessment functions
    calculateRiskScore: exports.calculateRiskScore,
    calculateEDDRequirements: exports.calculateEDDRequirements,

    // Compliance check functions
    checkFICACompliance: exports.checkFICACompliance,
    checkPOPIACompliance: exports.checkPOPIACompliance,

    // Version
    version: '2.0.0'
};
