/* ╔══════════════════════════════════════════════════════════════════════════════╗
  ║ VALIDATION UTILS - INPUT VALIDATION UTILITIES                               ║
  ╚══════════════════════════════════════════════════════════════════════════════╝ */

const validationUtils = {
  isValidEmail: (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  },

  isValidPhone: (phone) => {
    const re = /^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/;
    return re.test(phone);
  },

  isRequired: (value) => value !== undefined && value !== null && value !== '',
};

export default validationUtils;
