/**
 * /Users/wilsonkhanyezi/legal-doc-system/server/middleware/validator.js
 *
 * Validation Result Handler
 * -------------------------
 * Centralizes express-validator result processing.
 */

const { validationResult } = require('express-validator');

const validate = (req, res, next) => {
    const result = validationResult(req);
    if (result.isEmpty()) return next();

    const errors = result.array().map((e) => ({
        field: e.param,
        message: e.msg,
        value: e.value,
    }));

    return res.status(422).json({
        error: 'Validation failed',
        errors,
    });
};

module.exports = { validate };
