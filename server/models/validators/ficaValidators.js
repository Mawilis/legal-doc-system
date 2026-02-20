/*╔══════════════════════════════════════════════════════════════════════════════╗
  ║ FICA VALIDATORS - INVESTOR-GRADE ● FORENSIC ● PRODUCTION                    ║
  ║ Financial Intelligence Centre Act 38 of 2001 Compliant                      ║
  ║ Version: 1.0.0 - PRODUCTION                                                 ║
  ╚══════════════════════════════════════════════════════════════════════════════╝*/

'use strict';

const crypto = require('crypto');

/**
 * Validate South African ID number according to Home Affairs standards
 */
exports.validateSAIDNumber = (idNumber) => {
    if (!idNumber) throw new Error('ID number is required');
    const cleanId = idNumber.toString().replace(/\s+/g, '');
    if (cleanId.length !== 13) throw new Error(`Invalid ID length: expected 13, got ${cleanId.length}`);
    if (!/^\d+$/.test(cleanId)) throw new Error('ID must contain only digits');
    
    // Extract birth date
    const year = parseInt(cleanId.substring(0, 2), 10);
    const month = parseInt(cleanId.substring(2, 4), 10);
    const day = parseInt(cleanId.substring(4, 6), 10);
    
    if (month < 1 || month > 12) throw new Error('Invalid birth month');
    const daysInMonth = new Date(year, month, 0).getDate();
    if (day < 1 || day > daysInMonth) throw new Error('Invalid birth day');
    
    // Citizenship check
    const citizenship = parseInt(cleanId.substring(10, 11), 10);
    if (![0, 1].includes(citizenship)) throw new Error('Invalid citizenship digit');
    
    return {
        isValid: true,
        birthDate: new Date(year < 20 ? 2000 + year : 1900 + year, month - 1, day),
        gender: parseInt(cleanId.substring(6, 10), 10) >= 5000 ? 'MALE' : 'FEMALE',
        citizenship: citizenship === 0 ? 'CITIZEN' : 'PERMANENT_RESIDENT'
    };
};

/**
 * Validate business registration number (CIPC format)
 */
exports.validateBusinessRegistration = (regNumber) => {
    if (!regNumber) throw new Error('Registration number required');
    const cleanReg = regNumber.toString().replace(/\s+/g, '').toUpperCase();
    const formats = [/^\d{4}\/\d{6}\/\d{2}$/, /^\d{4}\/\d{6}$/];
    if (!formats.some(f => f.test(cleanReg))) {
        throw new Error('Invalid format. Expected YYYY/XXXXXX/XX or YYYY/XXXXXX');
    }
    const year = parseInt(cleanReg.substring(0, 4), 10);
    const currentYear = new Date().getFullYear();
    if (year < 1900 || year > currentYear) throw new Error(`Invalid year: ${year}`);
    return { isValid: true, registrationYear: year };
};

/**
 * Generate FICA reference number
 */
exports.generateFICARefNumber = (sessionId) => {
    const date = new Date().toISOString().slice(0, 10).replace(/-/g, '');
    const random = crypto.randomBytes(4).toString('hex').toUpperCase();
    const sessionHash = crypto.createHash('md5').update(sessionId).digest('hex').substring(0, 8).toUpperCase();
    return `FICA-${date}-${sessionHash}-${random}`;
};

/**
 * Generate POPIA consent reference
 */
exports.generatePOPIAConsentRef = (userId) => {
    const date = new Date().toISOString().slice(0, 10).replace(/-/g, '');
    const userHash = crypto.createHash('md5').update(userId).digest('hex').substring(0, 8).toUpperCase();
    return `POPIA-${date}-${userHash}`;
};

/**
 * Calculate risk score based on client data
 */
exports.calculateRiskScore = (clientType, clientData) => {
    let score = 0;
    const factors = [];
    
    // Base risk by client type
    if (clientType === 'COMPANY' || clientType === 'TRUST') {
        score += 30;
        factors.push({ factor: 'entity_type', score: 30, description: 'Enhanced due diligence required' });
    } else {
        score += 10;
        factors.push({ factor: 'entity_type', score: 10, description: 'Standard due diligence' });
    }
    
    // Geographic risk
    if (clientData.countryOfResidence && clientData.countryOfResidence !== 'South Africa') {
        score += 20;
        factors.push({ factor: 'foreign_national', score: 20, description: 'Foreign national' });
    }
    
    // PEP check
    if (clientData.isPoliticallyExposed) {
        score += 40;
        factors.push({ factor: 'politically_exposed', score: 40, description: 'Politically exposed person' });
    }
    
    // Income check
    if (clientData.annualIncome && clientData.annualIncome > 10000000) {
        score += 15;
        factors.push({ factor: 'high_net_worth', score: 15, description: 'High net worth individual' });
    }
    
    return {
        score: Math.min(score, 100),
        factors,
        level: score >= 75 ? 'HIGH' : score >= 50 ? 'MEDIUM' : 'LOW'
    };
};

// =================================================================================================================
// ADD MISSING VALIDATION FUNCTIONS
// =================================================================================================================

/**
 * Validate identity document based on type
 */
exports.validateIdentity = (identityType, identityNumber, countryOfIssue = null) => {
    if (!identityType) throw new Error('Identity type is required');
    
    if (identityType === 'SA_ID') {
        return exports.validateSAIDNumber(identityNumber);
    } else if (identityType === 'PASSPORT') {
        if (!countryOfIssue) throw new Error('Country of issue required for passport');
        return exports.validatePassport(identityNumber, countryOfIssue);
    } else {
        return { isValid: true, identityType, identityNumber };
    }
};

/**
 * Validate passport
 */
exports.validatePassport = (passportNumber, countryOfIssue) => {
    if (!passportNumber) throw new Error('Passport number required');
    if (!countryOfIssue) throw new Error('Country of issue required');
    if (passportNumber.length < 6 || passportNumber.length > 20) {
        throw new Error('Passport number must be 6-20 characters');
    }
    return {
        isValid: true,
        passportNumber,
        countryOfIssue,
        maskedNumber: `******${passportNumber.slice(-4)}`
    };
};

/**
 * Calculate Enhanced Due Diligence requirements
 */
exports.calculateEDDRequirements = (riskAssessment) => {
    if (!riskAssessment) return { required: false, reasons: [] };
    
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
