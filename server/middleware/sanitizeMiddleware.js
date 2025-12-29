/**
 * /Users/wilsonkhanyezi/legal-doc-system/server/middleware/sanitizeMiddleware.js
 *
 * Request Body Sanitizer
 * ----------------------
 * Normalizes and strips unsafe characters from specified fields.
 */

const CONTROL_CHAR_REGEX = /[\u0000-\u001F\u007F]+/g;

const sanitizeValue = (value, field) => {
    if (typeof value !== 'string') return value;
    let v = value.trim().replace(CONTROL_CHAR_REGEX, '');
    if (field === 'email') v = v.toLowerCase();
    return v;
};

/**
 * sanitizeBody(fields: string[])
 * - Sanitizes only the specified fields in req.body.
 */
const sanitizeBody = (fields = []) => {
    return (req, _res, next) => {
        if (!req.body) return next();
        fields.forEach((field) => {
            if (Object.prototype.hasOwnProperty.call(req.body, field)) {
                req.body[field] = sanitizeValue(req.body[field], field);
            }
        });
        next();
    };
};

module.exports = { sanitizeBody };
