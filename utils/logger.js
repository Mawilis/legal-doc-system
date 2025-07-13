const fs = require('fs');
const path = require('path');
const winston = require('winston');
const DailyRotateFile = require('winston-daily-rotate-file');
const Sentry = require('@sentry/node');

// Ensure log directory exists
const logDir = path.join(__dirname, '../logs');
if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir);
}

// Initialize Sentry
Sentry.init({
    dsn: process.env.SENTRY_DSN,
    environment: process.env.NODE_ENV,
    tracesSampleRate: 1.0,
});

// --- Sanitize sensitive fields ---
const sanitize = (message) => {
    if (typeof message !== 'string') return message;
    return message
        .replace(/Bearer\s+[a-zA-Z0-9-_]+\.[a-zA-Z0-9-_]+\.[a-zA-Z0-9-_]+/g, 'Bearer [REDACTED]')
        .replace(/"token"\s*:\s*"[^"]+"/g, '"token":"[REDACTED]"')
        .replace(/"password"\s*:\s*"[^"]+"/g, '"password":"[REDACTED]"');
};

// --- Format for all transports ---
const logFormat = winston.format.combine(
    winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
    winston.format.errors({ stack: true }),
    winston.format.printf(({ timestamp, level, message, stack }) => {
        const cleanMessage = sanitize(stack || message);
        return `[${timestamp}] ${level.toUpperCase()}: ${cleanMessage}`;
    })
);

// --- Create Winston logger ---
const logger = winston.createLogger({
    level: process.env.NODE_ENV === 'development' ? 'debug' : 'info',
    format: logFormat,
    transports: [
        new DailyRotateFile({
            filename: path.join(logDir, 'server-%DATE%.log'),
            datePattern: 'YYYY-MM-DD',
            maxSize: '10m',
            maxFiles: '14d',
        }),
        new DailyRotateFile({
            filename: path.join(logDir, 'error-%DATE%.log'),
            level: 'error',
            datePattern: 'YYYY-MM-DD',
            maxSize: '5m',
            maxFiles: '30d',
        }),
    ],
});

// --- Add colorized console transport in non-production ---
if (process.env.NODE_ENV !== 'production') {
    logger.add(new winston.transports.Console({
        format: winston.format.combine(
            winston.format.colorize(),
            logFormat
        ),
    }));
}

// --- Send errors to Sentry ---
logger.on('error', (err) => {
    Sentry.captureException(err);
});

// --- Optionally wrap logger.error to send to Sentry manually ---
const originalError = logger.error;
logger.error = function (msg, ...args) {
    if (msg instanceof Error) {
        Sentry.captureException(msg);
    } else {
        Sentry.captureMessage(sanitize(msg));
    }
    return originalError.call(this, msg, ...args);
};

module.exports = logger;
