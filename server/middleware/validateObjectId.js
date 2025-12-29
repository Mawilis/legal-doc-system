/**
 * /Users/wilsonkhanyezi/legal-doc-system/server/middleware/validateObjectId.js
 *
 * ObjectId Validator
 * ------------------
 * Validates :id-like path params as 24-character hex strings (MongoDB ObjectId format).
 */

const HEX_24_REGEX = /^[a-fA-F0-9]{24}$/;

const validateObjectId = (req, res, next) => {
    // Find first param that looks like an ID, or commonly used 'id', 'userId', etc.
    const candidate = req.params.id || req.params.userId || req.params.documentId || req.params.resettoken;
    if (!candidate || !HEX_24_REGEX.test(candidate)) {
        return res.status(400).json({
            error: 'Invalid identifier format. Expecting 24-character hex string.',
            value: candidate || null,
        });
    }
    next();
};

module.exports = validateObjectId;
