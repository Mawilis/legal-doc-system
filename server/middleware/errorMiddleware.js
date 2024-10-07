const CustomError = require('../utils/customError');

const errorHandler = (err, req, res, next) => {
    let statusCode = err.statusCode || 500;
    let message = err.message || 'Server Error';

    // Custom error handling for specific cases
    if (err.name === 'ValidationError') {
        message = 'Validation Error';
        statusCode = 400;
    }

    res.status(statusCode).json({
        success: false,
        message,
    });
};

module.exports = errorHandler;
