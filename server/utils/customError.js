// ~/legal-doc-system/server/utils/customError.js

class CustomError extends Error {
    /**
     * CustomError extends the built-in Error class to provide a consistent structure for operational errors.
     * @param {string} message - Error message describing the issue.
     * @param {number} statusCode - HTTP status code associated with the error.
     */
    constructor(message, statusCode) {
        super(message);

        this.statusCode = statusCode || 500;
        this.status = `${statusCode}`.startsWith('4') ? 'fail' : 'error';
        this.isOperational = true; // Indicates that this is an operational error that should be handled gracefully.

        // Capture the stack trace, excluding the constructor call from it.
        Error.captureStackTrace(this, this.constructor);
    }
}

module.exports = { CustomError };
