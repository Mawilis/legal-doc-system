// server/middleware/errorMiddleware.js

const CustomError = require('../utils/customError');
const logger = require('../utils/logger');

// --- Helper functions for specific error types ---

const handleCastErrorDB = (err) => {
    const message = `Invalid ${err.path}: ${err.value}.`;
    return new CustomError(message, 400);
};

const handleDuplicateFieldsDB = (err) => {
    // Extract the value from the error message for a cleaner output
    const value = err.errmsg.match(/(["'])(\\?.)*?\1/)[0];
    const message = `Duplicate field value: ${value}. Please use another value.`;
    return new CustomError(message, 400);
};

const handleValidationErrorDB = (err) => {
    const errors = Object.values(err.errors).map(el => el.message);
    const message = `Invalid input data. ${errors.join('. ')}`;
    return new CustomError(message, 400);
};

// Specific handlers for JWT authentication errors
const handleJWTError = () => new CustomError('Invalid token. Please log in again.', 401);
const handleJWTExpiredError = () => new CustomError('Your token has expired. Please log in again.', 401);


// --- Response functions for different environments ---

// In development, send a detailed error with the stack trace for debugging
const sendErrorDev = (err, res) => {
    res.status(err.statusCode).json({
        success: false,
        status: err.status,
        error: err,
        message: err.message,
        stack: err.stack
    });
};

// In production, send a more generic and safe error message
const sendErrorProd = (err, res) => {
    // A) For operational, trusted errors that we created, send the specific message to the client
    if (err.isOperational) {
        return res.status(err.statusCode).json({
            success: false,
            status: err.status,
            error: err.message
        });
    }

    // B) For programming or other unknown errors, don't leak details
    // 1) Log the error for the developers to see
    logger.error('CRITICAL ERROR 💥', err);
    // 2) Send a generic message to the client
    return res.status(500).json({
        success: false,
        status: 'error',
        error: 'Something went very wrong on our end. Please try again later.'
    });
};


// --- The Main Error Handling Middleware ---
const errorHandler = (err, req, res, next) => {
    err.statusCode = err.statusCode || 500;
    err.status = err.status || 'error';

    if (process.env.NODE_ENV === 'development') {
        sendErrorDev(err, res);
    } else { // 'production' or any other setting defaults to production for safety
        // Create a separate error object to avoid mutating the original `err`
        let error = { ...err, message: err.message, name: err.name, code: err.code, errmsg: err.errmsg };

        if (error.name === 'CastError') error = handleCastErrorDB(error);
        if (error.code === 11000) error = handleDuplicateFieldsDB(error);
        if (error.name === 'ValidationError') error = handleValidationErrorDB(error);
        if (error.name === 'JsonWebTokenError') error = handleJWTError();
        if (error.name === 'TokenExpiredError') error = handleJWTExpiredError();

        sendErrorProd(error, res);
    }
};

module.exports = errorHandler;
