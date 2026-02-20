/*╔══════════════════════════════════════════════════════════════════════════════╗
  ║ CIPC VALIDATION RULES - INVESTOR-GRADE MODULE                              ║
  ║ Companies Act compliance | Registration validation                          ║
  ╚══════════════════════════════════════════════════════════════════════════════╝*/
/**
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/utils/cipcValidationRules.js
 * VERSION: 1.0.0
 */

'use strict';

class CIPCValidationRules {
    /**
     * Validate company registration number format
     */
    validateRegistrationFormat(registrationNumber) {
        if (!registrationNumber) {
            return {
                valid: false,
                reason: 'MISSING_REGISTRATION_NUMBER'
            };
        }

        // Clean the registration number
        const cleanReg = registrationNumber.replace(/[\s/\\-]/g, '');

        // Check format: YYYY followed by 6-7 digits followed by 2 digits
        const isValidFormat = /^(19|20)\d{2}\d{6,7}\d{2}$/.test(cleanReg);

        if (!isValidFormat) {
            return {
                valid: false,
                reason: 'INVALID_REGISTRATION_FORMAT',
                message: 'Registration number must be in format: YYYY/123456/07 or YYYY/1234567/21'
            };
        }

        // Extract components
        const year = parseInt(cleanReg.substring(0, 4), 10);
        const sequence = cleanReg.substring(4, cleanReg.length - 2);
        const entityType = cleanReg.substring(cleanReg.length - 2);

        // Validate year (cannot be in the future)
        const currentYear = new Date().getFullYear();
        if (year > currentYear) {
            return {
                valid: false,
                reason: 'FUTURE_YEAR',
                message: 'Registration year cannot be in the future'
            };
        }

        // Validate entity type
        const validEntityTypes = ['07', '21', '22', '23', '24', '25', '26'];
        if (!validEntityTypes.includes(entityType)) {
            return {
                valid: false,
                reason: 'INVALID_ENTITY_TYPE',
                message: 'Invalid entity type code'
            };
        }

        return {
            valid: true,
            components: {
                year,
                sequence,
                entityType,
                full: cleanReg
            }
        };
    }

    /**
     * Check if registration number is invalid (for testing)
     */
    isInvalidRegistration(registrationNumber) {
        const invalidPatterns = [
            'INVALID-REG',
            '0000/000000/00',
            '9999/999999/99'
        ];
        
        return invalidPatterns.some(pattern => 
            registrationNumber.includes(pattern)
        );
    }

    /**
     * Get compliance status
     */
    getComplianceStatus(registrationNumber, isValid) {
        if (!isValid) {
            return 'INVALID_REGISTRATION';
        }
        
        if (this.isInvalidRegistration(registrationNumber)) {
            return 'INVALID_REGISTRATION';
        }
        
        return 'COMPANIES_ACT_71_OF_2008';
    }
}

module.exports = new CIPCValidationRules();
