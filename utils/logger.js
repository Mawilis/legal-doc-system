const winston = require('winston');

// Create a logger instance with a defined format and transport options
const logger = winston.createLogger({
    level: 'info',
    format: winston.format.combine(
        winston.format.timestamp({
            format: 'YYYY-MM-DD HH:mm:ss',
        }),
        winston.format.printf((info) => {
            return `[${info.timestamp}] ${info.level.toUpperCase()}: ${info.message}`;
        })
    ),
    transports: [
        new winston.transports.Console({
            format: winston.format.combine(
                winston.format.colorize(),
                winston.format.printf((info) => {
                    return `[${info.timestamp}] ${info.level.toUpperCase()}: ${info.message}`;
                })
            ),
        }),
        new winston.transports.File({ filename: 'logs/server.log' }),
    ],
});

module.exports = logger;
