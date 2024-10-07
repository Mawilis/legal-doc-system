// middleware/errorMiddleware.js
const CustomError = require('../utils/customError');

const errorHandler = (err, req, res, next) => {
    let statusCode = err.statusCode || 500;
    let message = err.message || 'Server Error';

    // Log error details (only in development)
    if (process.env.NODE_ENV === 'development') {
        console.error('Error:', err);
    }

    // Handle specific error types with custom messages
    if (err.name === 'ValidationError') {
        message = 'Validation Error';
        statusCode = 400;
    } else if (err.name === 'CastError') {
        message = 'Resource not found';
        statusCode = 404;
    } else if (err.name === 'JsonWebTokenError') {
        message = 'Invalid token, please log in again';
        statusCode = 401;
    } else if (err.name === 'TokenExpiredError') {
        message = 'Token expired, please log in again';
        statusCode = 401;
    }

    res.status(statusCode).json({
        success: false,
        error: {
            message,
            stack: process.env.NODE_ENV === 'production' ? null : err.stack,  // Include stack trace in development only
        },
    });
};

module.exports = errorHandler;
