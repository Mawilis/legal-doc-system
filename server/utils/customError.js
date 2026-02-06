/*
 * File: server/utils/customError.js
 * STATUS: PRODUCTION-READY | OPERATIONAL EXCELLENCE GRADE
 * -----------------------------------------------------------------------------
 * PURPOSE: 
 * Standardizes exception handling across the platform. Distinguishes between 
 * predictable operational failures and unpredictable system crashes.
 * -----------------------------------------------------------------------------
 */

'use strict';

/**
 * CUSTOM ERROR ARCHITECT
 * Extends the native Error object to support HTTP-aware exception handling.
 */
class CustomError extends Error {
  /**
   * @param {string} message - Human-readable explanation
   * @param {number} statusCode - HTTP status code (400, 401, 403, etc.)
   * @param {string} errorCode - Stable internal error code (e.g., 'AUTH_EXPIRED')
   */
  constructor(message, statusCode, errorCode = 'ERR_INTERNAL_SERVER') {
    super(message);

    this.statusCode = statusCode;
    this.code = errorCode;

    // 'fail' for 4xx errors (client-side), 'error' for 5xx (server-side)
    this.status = `${statusCode}`.startsWith('4') ? 'fail' : 'error';

    // isOperational: true means this is a predictable failure (e.g., validation)
    // False means it's a bug or system failure.
    this.isOperational = true;

    // Capture the stack trace but hide this constructor from it
    Error.captureStackTrace(this, this.constructor);
  }
}

module.exports = CustomError;