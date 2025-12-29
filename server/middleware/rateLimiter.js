'use strict';
const rateLimit = require('express-rate-limit');

// If package missing, return dummy middleware
if (!rateLimit) {
    module.exports = (req, res, next) => next();
} else {
    const apiLimiter = rateLimit({
        windowMs: 15 * 60 * 1000, // 15 minutes
        max: 100, // Limit each IP to 100 requests per windowMs
        message: {
            success: false,
            message: 'Too many requests from this IP, please try again after 15 minutes'
        },
        standardHeaders: true,
        legacyHeaders: false,
    });
    module.exports = apiLimiter;
}