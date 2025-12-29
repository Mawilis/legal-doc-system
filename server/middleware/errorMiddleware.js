const CustomError = require('../utils/customError');
const logger = require('../utils/logger');

// --- Helper functions for specific error types ---

const handleCastErrorDB = (err) => {
    const message = `Invalid ${err.path}: ${err.value}.`;
    return new CustomError(message, 400);
};

const handleDuplicateFieldsDB = (err) => {
    let value = '';
    try {
        value = err.errmsg.match(/(["'])(\\?.)*?\1/)[0];
    } catch {
        value = 'duplicate value';
    }
    const message = `Duplicate field value: ${value}. Please use another value.`;
    return new CustomError(message, 400);
};

const handleValidationErrorDB = (err) => {
    const errors = Object.values(err.errors).map(el => el.message);
    const message = `Invalid input data. ${errors.join('. ')}`;
    return new CustomError(message, 400);
};

// JWT errors
const handleJWTError = () => new CustomError('Invalid token. Please log in again.', 401);
const handleJWTExpiredError = () => new CustomError('Your token has expired. Please log in again.', 401);

// --- Response functions ---

const sendErrorDev = (err, req, res) => {
    res.status(err.statusCode).json({
        success: false,
        status: err.status,
        statusCode: err.statusCode,
        message: err.message,
        error: err,
        stack: err.stack,
        path: req.originalUrl,
        method: req.method
    });
};

const sendErrorProd = (err, req, res) => {
    if (err.isOperational) {
        return res.status(err.statusCode).json({
            success: false,
            status: err.status,
            statusCode: err.statusCode,
            error: err.message,
            path: req.originalUrl,
            method: req.method
        });
    }

    // Log unknown errors
    logger.error('CRITICAL ERROR 💥', {
        message: err.message,
        stack: err.stack,
        path: req.originalUrl,
        method: req.method
    });

    return res.status(500).json({
        success: false,
        status: 'error',
        statusCode: 500,
        error: 'Something went very wrong on our end. Please try again later.',
        path: req.originalUrl,
        method: req.method
    });
};

// --- Main Middleware ---
const errorHandler = (err, req, res, next) => {
    err.statusCode = err.statusCode || 500;
    err.status = err.status || 'error';

    let error = { ...err, message: err.message };

    if (process.env.NODE_ENV === 'development') {
        sendErrorDev(error, req, res);
    } else {
        if (error.name === 'CastError') error = handleCastErrorDB(error);
        if (error.code === 11000) error = handleDuplicateFieldsDB(error);
        if (error.name === 'ValidationError') error = handleValidationErrorDB(error);
        if (error.name === 'JsonWebTokenError') error = handleJWTError();
        if (error.name === 'TokenExpiredError') error = handleJWTExpiredError();

        sendErrorProd(error, req, res);
    }
};

module.exports = errorHandler;
