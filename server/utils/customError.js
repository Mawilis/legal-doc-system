/**
 * CustomError extends the built-in Error class to provide a consistent structure for operational errors.
 * This ensures predictable error handling with associated HTTP status codes throughout the application.
 */
class CustomError extends Error {
    /**
     * @param {string} message - Description of the error.
     * @param {number} statusCode - Associated HTTP status code.
     */
    constructor(message, statusCode) {
        super(message);

        this.statusCode = statusCode || 500;
        this.status = String(statusCode).startsWith('4') ? 'fail' : 'error';
        this.isOperational = true;

        // Improve debuggability: Capture precise stack trace without constructor
        Error.captureStackTrace(this, this.constructor);
    }
}

module.exports = CustomError;
