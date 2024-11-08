// ~/legal-doc-system/server/utils/logger.js

const { createLogger, format, transports } = require('winston');
const { combine, timestamp, printf, errors, colorize, json } = format;
const path = require('path');

// Determine the environment
const env = process.env.NODE_ENV || 'development';

// Define custom log formats
const devFormat = printf(({ level, message, timestamp, stack }) => {
    return `[${timestamp}] ${level}: ${stack || message}`;
});

const prodFormat = combine(
    timestamp(),
    errors({ stack: true }),
    json()
);

// Create a logger instance
const logger = createLogger({
    level: env === 'development' ? 'debug' : 'info',
    format: combine(
        errors({ stack: true }), // Capture stack trace
        timestamp()
    ),
    defaultMeta: { service: 'legal-doc-system' },
    transports: [
        // Console transport for development
        new transports.Console({
            format: combine(
                colorize(),
                env === 'development' ? devFormat : prodFormat
            ),
        }),

        // File transports for production
        new transports.File({
            filename: path.join(__dirname, '../../logs/error.log'),
            level: 'error',
            format: prodFormat,
            maxsize: 5242880, // 5MB
            maxFiles: 5,
        }),
        new transports.File({
            filename: path.join(__dirname, '../../logs/combined.log'),
            format: prodFormat,
            maxsize: 5242880, // 5MB
            maxFiles: 5,
        }),
    ],
    exitOnError: false, // Do not exit on handled exceptions
});

// Handle uncaught exceptions and unhandled rejections
if (env !== 'development') {
    logger.exceptions.handle(
        new transports.File({ filename: path.join(__dirname, '../../logs/exceptions.log') })
    );
}

module.exports = logger;
