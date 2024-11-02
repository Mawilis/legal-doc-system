const { createLogger, format, transports } = require('winston');
const { combine, timestamp, printf } = format;

// Define the custom log format
const logFormat = printf(({ level, message, timestamp }) => {
    return `[${timestamp}] ${level.toUpperCase()}: ${message}`;
});

// Create a logger instance
const logger = createLogger({
    format: combine(
        timestamp(),
        logFormat
    ),
    transports: [
        new transports.Console(),
        new transports.File({ filename: 'error.log', level: 'error' }),
        new transports.File({ filename: 'combined.log' })
    ],
});

module.exports = logger;
