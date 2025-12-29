/**
 * /Users/wilsonkhanyezi/legal-doc-system/server/validators/userValidator.js
 *
 * Enterprise User Validator (Masterpiece Edition)
 * -----------------------------------------------
 * Complete, production-grade validation rules for user lifecycle.
 * - Security: strict email normalization, strong password rules, input sanitization.
 * - Features: registration, login, profile update, password flows.
 * - Documentation: consistent error formatting for API consumers.
 * - Future-proof: structured for expansion (roles, MFA, phone validation).
 */

const { body, validationResult } = require('express-validator');
const CustomError = require('../utils/customError');

// ------------------------------------------
// Central Validation Middleware
// ------------------------------------------
const validate = (req, res, next) => {
    const errors = validationResult(req);
    if (errors.isEmpty()) return next();

    const extractedErrors = errors.array().map((err) => ({
        field: err.param,
        message: err.msg,
        value: err.value,
    }));

    return next(new CustomError('Validation failed.', 422, extractedErrors));
};

// ------------------------------------------
// Registration Rules
// ------------------------------------------
exports.registerRules = () => [
    body('name')
        .trim()
        .notEmpty()
        .withMessage('Name is required.')
        .isLength({ max: 100 })
        .withMessage('Name must not exceed 100 characters.'),
    body('email')
        .isEmail()
        .withMessage('Please provide a valid email address.')
        .normalizeEmail(),
    body('password')
        .isLength({ min: 12 })
        .withMessage('Password must be at least 12 characters long.')
        .matches(/[A-Z]/).withMessage('Password must include an uppercase letter.')
        .matches(/[a-z]/).withMessage('Password must include a lowercase letter.')
        .matches(/[0-9]/).withMessage('Password must include a number.')
        .matches(/[^A-Za-z0-9]/).withMessage('Password must include a special character.'),
];

// ------------------------------------------
// Login Rules
// ------------------------------------------
exports.loginRules = () => [
    body('email')
        .isEmail()
        .withMessage('Please provide a valid email address.')
        .normalizeEmail(),
    body('password')
        .notEmpty()
        .withMessage('Password is required.'),
];

// ------------------------------------------
// Update Details Rules
// ------------------------------------------
exports.updateDetailsRules = () => [
    body('name')
        .trim()
        .notEmpty()
        .withMessage('Name is required.')
        .isLength({ max: 100 })
        .withMessage('Name must not exceed 100 characters.'),
    body('email')
        .isEmail()
        .withMessage('Please provide a valid email address.')
        .normalizeEmail(),
];

// ------------------------------------------
// Update Password Rules
// ------------------------------------------
exports.updatePasswordRules = () => [
    body('currentPassword')
        .notEmpty()
        .withMessage('Current password is required.'),
    body('newPassword')
        .isLength({ min: 12 })
        .withMessage('New password must be at least 12 characters long.')
        .matches(/[A-Z]/).withMessage('New password must include an uppercase letter.')
        .matches(/[a-z]/).withMessage('New password must include a lowercase letter.')
        .matches(/[0-9]/).withMessage('New password must include a number.')
        .matches(/[^A-Za-z0-9]/).withMessage('New password must include a special character.'),
];

// ------------------------------------------
// Forgot Password Rules
// ------------------------------------------
exports.forgotPasswordRules = () => [
    body('email')
        .isEmail()
        .withMessage('Please provide a valid email address.')
        .normalizeEmail(),
];

// ------------------------------------------
// Reset Password Rules
// ------------------------------------------
exports.resetPasswordRules = () => [
    body('password')
        .isLength({ min: 12 })
        .withMessage('New password must be at least 12 characters long.')
        .matches(/[A-Z]/).withMessage('Password must include an uppercase letter.')
        .matches(/[a-z]/).withMessage('Password must include a lowercase letter.')
        .matches(/[0-9]/).withMessage('Password must include a number.')
        .matches(/[^A-Za-z0-9]/).withMessage('Password must include a special character.'),
];

// ------------------------------------------
// Export Central Validator
// ------------------------------------------
exports.validate = validate;
