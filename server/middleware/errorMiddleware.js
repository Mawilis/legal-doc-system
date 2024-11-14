const { CustomError } = require('../utils/customError');
const logger = require('../utils/logger');
const { v4: uuidv4 } = require('uuid');

const env = process.env.NODE_ENV || 'development';

/**
 * Global error handling middleware
 * @param {*} err - Error object
 * @param {*} req - HTTP request
 * @param {*} res - HTTP response
 * @param {*} next - Express next middleware function
 */
const errorHandler = (err, req, res, next) => {
    // Generate a unique error ID for tracing
    const errorId = uuidv4();

    // Default values
    let statusCode = err.statusCode || 500;
    let message = err.message || 'Internal Server Error';

    // Operational errors are trusted errors we can send to the client
    let isOperational = err.isOperational || false;

    // Handle specific Mongoose errors
    if (err.name === 'ValidationError') {
        statusCode = 400;
        message = 'Validation Error';
        isOperational = true;
    } else if (err.name === 'CastError') {
        statusCode = 400;
        message = 'Invalid ID format';
        isOperational = true;
    }

    // Handle JWT errors
    else if (err.name === 'JsonWebTokenError') {
        statusCode = 401;
        message = 'Invalid token, please log in again';
        isOperational = true;
    } else if (err.name === 'TokenExpiredError') {
        statusCode = 401;
        message = 'Token expired, please log in again';
        isOperational = true;
    }

    // Handle MongoDB duplicate key error
    else if (err.code && err.code === 11000) {
        statusCode = 400;
        message = 'Duplicate field value entered';
        isOperational = true;
    }

    // Handle custom operational errors
    else if (err instanceof CustomError) {
        statusCode = err.statusCode;
        message = err.message;
        isOperational = true;
    }

    // Log error details
    logger.error(`Error ID: ${errorId}`, {
        message: err.message,
        stack: err.stack,
        statusCode,
        path: req.originalUrl,
        method: req.method,
        ip: req.ip,
    });

    // Prepare error response
    const errorResponse = {
        success: false,
        error: {
            message: isOperational ? message : 'An unexpected error occurred',
            errorId: errorId, // Include the error ID for client reference
        },
    };

    // Include stack trace in development mode
    if (env === 'development') {
        errorResponse.error.stack = err.stack;
    }

    // Include CORS headers in error response
    res.setHeader('Access-Control-Allow-Origin', req.headers.origin || '*');
    res.setHeader('Access-Control-Allow-Credentials', 'true');
    res.setHeader('Access-Control-Allow-Methods', 'GET,POST,PUT,PATCH,DELETE,OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

    // Send response to client
    res.status(statusCode).json(errorResponse);
};

module.exports = errorHandler;
