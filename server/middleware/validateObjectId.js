/*
 * File: server/middleware/validateObjectId.js
 * STATUS: PRODUCTION-READY | DATABASE INTEGRITY GRADE
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * Validates that incoming path parameters conform to the MongoDB ObjectId 
 * standard (24-character hex). This prevents malformed queries from reaching 
 * the database.
 *
 * KEY FEATURES FOR FUTURE ENGINEERS:
 * 1. Performance: Uses optimized Regex to fail-fast before hitting the DB.
 * 2. Security: Blocks NoSQL injection attempts via URL parameters.
 * 3. Traceability: Returns correlation IDs on rejection for support desk mapping.
 * 4. Versatility: Can be applied to any named parameter (id, userId, docId).
 * -----------------------------------------------------------------------------
 */

'use strict';

const { emitAudit } = require('./auditMiddleware');

// 24-character hex string (Standard MongoDB ObjectId)
const OBJECT_ID_REGEX = /^[a-fA-F0-9]{24}$/;

/**
 * OBJECT ID VALIDATOR FACTORY
 * @param {string} paramName - The name of the parameter to validate (default: 'id')
 */
const validateObjectId = (paramName = 'id') => {
    return async (req, res, next) => {
        const candidate = req.params[paramName];

        // 1. FORMAT VALIDATION
        if (!candidate || !OBJECT_ID_REGEX.test(candidate)) {

            // 2. FORENSIC AUDIT (Log as a warning: Malformed IDs are suspicious)
            if (req.logAudit) {
                await req.logAudit('INVALID_ID_REJECTED', {
                    paramName,
                    value: candidate,
                    path: req.originalUrl
                });
            }

            return res.status(400).json({
                success: false,
                status: 'error',
                code: 'ERR_INVALID_IDENTIFIER',
                message: `The identifier provided for '${paramName}' is not a valid 24-character hex string.`,
                correlationId: req.correlationId
            });
        }

        // 3. ATTACH TO CONTEXT
        // We ensure the ID is easily accessible for downstream queries
        req.context = {
            ...req.context,
            validatedId: candidate
        };

        next();
    };
};

module.exports = validateObjectId;