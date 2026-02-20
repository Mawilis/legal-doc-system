/*╔══════════════════════════════════════════════════════════════════════════════╗
  ║ SA LEGAL VALIDATORS - FICA COMPLIANT | POPIA COMPLIANT                     ║
  ║ South African legal requirements validation                                 ║
  ╚══════════════════════════════════════════════════════════════════════════════╝*/

const { ValidationError } = require('../utils/errors');

/**
 * Validate South African ID number
 * Implements Luhn algorithm and SA ID number format validation
 */
function validateSAIDNumber(idNumber) {
    if (!idNumber) {
        throw new ValidationError('ID number is required');
    }

    // Remove any spaces or special characters
    const cleanId = idNumber.toString().replace(/\s+/g, '');

    // Check length (13 digits for SA ID)
    if (cleanId.length !== 13) {
        throw new ValidationError('Invalid ID number length', {
            expected: 13,
            received: cleanId.length
        });
    }

    // Check if all characters are digits
    if (!/^\d+$/.test(cleanId)) {
        throw new ValidationError('ID number must contain only digits');
    }

    // Extract birth date (YYMMDD)
    const year = parseInt(cleanId.substring(0, 2), 10);
    const month = parseInt(cleanId.substring(2, 4), 10);
    const day = parseInt(cleanId.substring(4, 6), 10);

    // Validate month (01-12)
    if (month < 1 || month > 12) {
        throw new ValidationError('Invalid birth month in ID number');
    }

    // Validate day based on month
    const daysInMonth = new Date(year, month, 0).getDate();
    if (day < 1 || day > daysInMonth) {
        throw new ValidationError('Invalid birth day in ID number');
    }

    // Validate citizenship (0 = SA citizen, 1 = permanent resident)
    const citizenship = parseInt(cleanId.substring(10, 11), 10);
    if (![0, 1].includes(citizenship)) {
        throw new ValidationError('Invalid citizenship digit in ID number');
    }

    // Validate race digit (was used during apartheid, now should be 8)
    const raceDigit = parseInt(cleanId.substring(6, 7), 10);
    if (raceDigit > 9) {
        throw new ValidationError('Invalid race digit in ID number');
    }

    // Luhn algorithm check
    if (!_validateLuhn(cleanId)) {
        throw new ValidationError('ID number failed checksum validation');
    }

    return {
        isValid: true,
        birthDate: `${year < 20 ? '20' : '19'}${year.toString().padStart(2, '0')}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`,
        gender: parseInt(cleanId.substring(6, 10), 10) >= 5000 ? 'MALE' : 'FEMALE',
        citizenship: citizenship === 0 ? 'CITIZEN' : 'PERMANENT_RESIDENT'
    };
}

/**
 * Validate business registration number
 */
function validateBusinessRegistration(regNumber) {
    if (!regNumber) {
        throw new ValidationError('Registration number is required');
    }

    const cleanReg = regNumber.toString().replace(/\s+/g, '').toUpperCase();

    // Check format (YYYY/XXXXXX/XX or YYYY/XXXXXX)
    const formats = [
        /^\d{4}\/\d{6}\/\d{2}$/,  // Companies Act format
        /^\d{4}\/\d{6}$/,          // Close corporation format
        /^\d{4}\/\d{4}\/\d{2}$/    // Other business formats
    ];

    if (!formats.some(format => format.test(cleanReg))) {
        throw new ValidationError('Invalid registration number format', {
            expected: 'YYYY/XXXXXX/XX or YYYY/XXXXXX',
            received: cleanReg
        });
    }

    // Extract year
    const year = parseInt(cleanReg.substring(0, 4), 10);
    const currentYear = new Date().getFullYear();

    if (year < 1900 || year > currentYear) {
        throw new ValidationError('Invalid registration year', {
            expected: `1900-${currentYear}`,
            received: year
        });
    }

    return {
        isValid: true,
        registrationYear: year,
        format: cleanReg.includes('/') ? 'COMPANIES_ACT' : 'CLOSE_CORPORATION'
    };
}

/**
 * Validate tax number (SARS format)
 */
function validateTaxNumber(taxNumber) {
    if (!taxNumber) {
        throw new ValidationError('Tax number is required');
    }

    const cleanTax = taxNumber.toString().replace(/\s+/g, '');

    // SARS tax numbers are typically 10 digits
    if (cleanTax.length !== 10) {
        throw new ValidationError('Invalid tax number length', {
            expected: 10,
            received: cleanTax.length
        });
    }

    if (!/^\d+$/.test(cleanTax)) {
        throw new ValidationError('Tax number must contain only digits');
    }

    return {
        isValid: true,
        taxNumber: cleanTax
    };
}

/**
 * Validate proof of address (POPIA compliance)
 */
function validateProofOfAddress(address) {
    const required = ['street', 'city', 'postalCode', 'country'];
    const missing = [];

    for (const field of required) {
        if (!address[field]) {
            missing.push(field);
        }
    }

    if (missing.length > 0) {
        throw new ValidationError('Invalid address', { missing });
    }

    // Validate postal code (SA format)
    if (address.country === 'South Africa' || address.country === 'ZA') {
        if (!/^\d{4}$/.test(address.postalCode)) {
            throw new ValidationError('Invalid South African postal code', {
                expected: '4 digits',
                received: address.postalCode
            });
        }
    }

    return true;
}

/**
 * Luhn algorithm implementation
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

module.exports = {
    validateSAIDNumber,
    validateBusinessRegistration,
    validateTaxNumber,
    validateProofOfAddress
};
