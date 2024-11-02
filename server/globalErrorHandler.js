const logger = require('../utils/logger');

const globalErrorHandler = (err, req, res, next) => {
    const statusCode = err.statusCode || 500;
    const message = err.message || 'Internal Server Error';

    logger.error(`[${req.method}] ${req.originalUrl} - ${statusCode} - ${message}`);

    res.status(statusCode).json({
        status: 'error',
        message
    });
};

module.exports = globalErrorHandler;
