const { body, validationResult } = require('express-validator');
const CustomError = require('../utils/customError');

/**
 * Central validation middleware
 * Checks validation results and formats errors.
 */
const validate = (req, res, next) => {
    const errors = validationResult(req);
    if (errors.isEmpty()) {
        return next();
    }

    const extractedErrors = errors.array().map(err => ({
        param: err.param,
        msg: err.msg,
    }));

    return next(new CustomError('Validation failed.', 422, extractedErrors));
};

// --- Registration ---
exports.registerRules = () => [
    body('name')
        .trim()
        .notEmpty()
        .withMessage('Name is required.'),
    body('email')
        .isEmail()
        .withMessage('Please provide a valid email address.')
        .normalizeEmail(),
    body('password')
        .isLength({ min: 6 })
        .withMessage('Password must be at least 6 characters long.'),
];

// --- Login ---
exports.loginRules = () => [
    body('email')
        .isEmail()
        .withMessage('Please provide a valid email address.')
        .normalizeEmail(),
    body('password')
        .notEmpty()
        .withMessage('Password is required.'),
];

// --- Update details ---
exports.updateDetailsRules = () => [
    body('name')
        .trim()
        .notEmpty()
        .withMessage('Name is required.'),
    body('email')
        .isEmail()
        .withMessage('Please provide a valid email address.')
        .normalizeEmail(),
];

// --- Update password ---
exports.updatePasswordRules = () => [
    body('currentPassword')
        .notEmpty()
        .withMessage('Current password is required.'),
    body('newPassword')
        .isLength({ min: 6 })
        .withMessage('New password must be at least 6 characters long.'),
];

// --- Forgot password ---
exports.forgotPasswordRules = () => [
    body('email')
        .isEmail()
        .withMessage('Please provide a valid email address.')
        .normalizeEmail(),
];

// --- Reset password ---
exports.resetPasswordRules = () => [
    body('password')
        .isLength({ min: 6 })
        .withMessage('New password must be at least 6 characters long.'),
];

// Export central validator
exports.validate = validate;
