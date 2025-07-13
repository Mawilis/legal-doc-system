const rateLimit = require('express-rate-limit');

// --- API Rate Limiter Configuration ---
// This helps protect your API from abuse (e.g. DDoS, brute-force attacks)
const apiLimiter = rateLimit({
    // Time window: 15 minutes (in milliseconds)
    windowMs: 15 * 60 * 1000,

    // Maximum number of requests per IP within the window
    max: 100,

    // Response to send when rate limit is exceeded
    message: {
        success: false,
        error: 'Too many requests from this IP. Please try again after 15 minutes.'
    },

    // Enable RateLimit-* headers (for modern clients)
    standardHeaders: true,

    // Disable legacy X-RateLimit-* headers
    legacyHeaders: false,

    // Optionally you can log rate limit exceed attempts here
    handler: (req, res, next, options) => {
        console.warn(`Rate limit exceeded for IP: ${req.ip}`);
        res.status(options.statusCode).json(options.message);
    }
});

module.exports = apiLimiter;
