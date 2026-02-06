/**
 * /Users/wilsonkhanyezi/legal-doc-system/server/validators/passwordValidator.js
 *
 * Password Flow Validators
 * ------------------------
 * Express-validator rules for email, password complexity, and reset token format.
 */

const { check } = require('express-validator');

const COMMON_PASSWORDS = new Set([
    'password', '123456', 'qwerty', 'letmein', 'admin', 'welcome', 'passw0rd',
]);

/**
 * emailRules()
 * - Validates 'email' in req.body.
 */
const emailRules = () => [
    check('email')
        .exists({ checkFalsy: true }).withMessage('Email is required.')
        .isEmail().withMessage('Invalid email format.')
        .isLength({ max: 254 }).withMessage('Email is too long.')
];

/**
 * passwordRules(path = 'body.password')
 * - Enforces strong password rules: min length, mixed charset, and not common.
 * - Path may be 'body.password' (default) or any body field (e.g., 'body.newPassword').
 */
const passwordRules = (path = 'body.password') => {
    const param = path.replace(/^body\./, '');
    return [
        check(param)
            .exists({ checkFalsy: true }).withMessage('Password is required.')
            .isLength({ min: 12 }).withMessage('Password must be at least 12 characters.')
            .matches(/[A-Z]/).withMessage('Password must include an uppercase letter.')
            .matches(/[a-z]/).withMessage('Password must include a lowercase letter.')
            .matches(/[0-9]/).withMessage('Password must include a number.')
            .matches(/[^A-Za-z0-9]/).withMessage('Password must include a special character.')
            .custom((value) => !COMMON_PASSWORDS.has(value.toLowerCase()))
            .withMessage('Password is too common. Choose a stronger one.')
    ];
};

/**
 * tokenRules(path = 'params.resettoken')
 * - Validates the structure/length of a reset token.
 * - Supports hex/base64/uuid-like formats. Adjust to your issuance strategy.
 */
const tokenRules = (path = 'params.resettoken') => {
    const [location, param] = path.split('.');
    const rule = check(param)
        .exists({ checkFalsy: true }).withMessage('Reset token is required.')
        .isLength({ min: 20, max: 256 }).withMessage('Reset token length is invalid.')
        .matches(/^[A-Za-z0-9._\\-]+$/).withMessage('Reset token contains invalid characters.');

    // express-validator uses field names, not path prefixes; ensure correct location hinting
    return [rule];
};

module.exports = {
    emailRules,
    passwordRules,
    tokenRules,
};
