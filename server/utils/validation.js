/*╔══════════════════════════════════════════════════════════════════════════════╗
  ║ VALIDATION UTILS - INPUT VALIDATION UTILITIES                               ║
  ╚══════════════════════════════════════════════════════════════════════════════╝*/
'use strict';

const validationUtils = {
    isValidEmail: (email) => {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },
    
    isValidPhone: (phone) => {
        const re = /^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/;
        return re.test(phone);
    },
    
    isRequired: (value) => {
        return value !== undefined && value !== null && value !== '';
    }
};

module.exports = validationUtils;
