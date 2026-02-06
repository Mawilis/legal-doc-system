/*
 * File: server/middleware/errorMiddleware.js
 * STATUS: EPITOME | RESILIENCY & FORENSICS GRADE
 * -----------------------------------------------------------------------------
 * PURPOSE: 
 * The Global Resilience Shield. Normalizes all system exceptions, protects 
 * against stack leakage in production, and provides a forensic trail via 
 * Correlation IDs for all API failures.
 * -----------------------------------------------------------------------------
 * COLLABORATION NOTES:
 * - DEVOPS: High-severity errors (500+) are routed to internal logging.
 * - SECURITY: Masks internal Mongoose logic and stack traces in production.
 * - FRONTEND-TEAM: Relies on the 'code' field for internationalization/UI alerts.
 * -----------------------------------------------------------------------------
 */

'use strict';

const logger = require('../utils/logger');
const { errorResponse } = require('./responseHandler');

/**
 * DB ERROR NORMALIZERS
 * Transforms technical Mongoose/Mongo errors into clean, high-level API feedback.
 */
const handleCastErrorDB = (err) => ({
    message: `Invalid resource identifier format: ${err.value}`,
    statusCode: 400,
    code: 'ERR_MALFORMED_ID'
});

const handleDuplicateFieldsDB = (err) => {
    // Extracts the field name causing the unique constraint violation
    const value = err.errmsg?.match(/(["'])(\\?.)*?\1/)?.[0] || 'Unknown';
    return {
        message: `The value ${value} is already in use within this firm. Please use a unique identifier.`,
        statusCode: 400,
        code: 'ERR_DUPLICATE_ENTRY'
    };
};

const handleValidationErrorDB = (err) => {
    const errors = Object.values(err.errors).map(el => el.message);
    return {
        message: `Validation failed: ${errors.join('. ')}`,
        statusCode: 400,
        code: 'ERR_VALIDATION_FAILED'
    };
};

/**
 * AUTH ERROR NORMALIZERS
 */
const handleJWTError = () => ({
    message: 'Invalid security signature. Please log in again.',
    statusCode: 401,
    code: 'ERR_AUTH_INVALID'
});

const handleJWTExpiredError = () => ({
    message: 'Your session has expired. Please re-authenticate.',
    statusCode: 401,
    code: 'ERR_AUTH_EXPIRED'
});

/**
 * GLOBAL ERROR HANDLER MIDDLEWARE
 * The central catch-all for every unhandled exception in the Wilsy OS.
 */
const errorHandler = (err, req, res, next) => {
    // 1. DEFAULT ERROR STATE
    let error = {
        ...err,
        message: err.message || 'An unexpected error occurred.',
        statusCode: err.statusCode || 500,
        code: err.code || 'ERR_SYSTEM_CORE'
    };

    // 2. NORMALIZE SPECIFIC ENGINE ERRORS
    if (err.name === 'CastError') error = handleCastErrorDB(err);
    if (err.code === 11000) error = handleDuplicateFieldsDB(err);
    if (err.name === 'ValidationError') error = handleValidationErrorDB(err);
    if (err.name === 'JsonWebTokenError') error = handleJWTError();
    if (err.name === 'TokenExpiredError') error = handleJWTExpiredError();

    // 3. INTERNAL FORENSIC LOGGING
    // We log the full technical details for the engineering team.
    if (error.statusCode >= 500) {
        logger.error('💥 [SYSTEM_EXCEPTION]:', {
            correlationId: req.id || 'N/A',
            path: req.originalUrl,
            message: err.message,
            stack: err.stack,
            user: req.user?._id || 'ANONYMOUS'
        });
    }

    // 4. CLIENT RESPONSE DELIVERY
    // Leverages our standardized response handler to ensure envelope consistency.
    // We attach the stack trace to the 'req' object if in dev mode for the handler to consume.
    if (process.env.NODE_ENV !== 'production') {
        req.errStack = err.stack;
    }

    return errorResponse(
        req,
        res,
        error.statusCode,
        error.message,
        error.code
    );
};

module.exports = { errorHandler };

