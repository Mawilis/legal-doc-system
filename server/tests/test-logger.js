const winston = require('winston');
const chalk = require('chalk');

// Test with custom levels
const logger = winston.createLogger({
    levels: {
        generational: 0,
        billion: 1,
        sovereign: 2,
        error: 3,
        warn: 4,
        info: 5,
        debug: 6
    },
    transports: [
        new winston.transports.Console()
    ]
});

console.log('Testing logger...');
try {
    logger.generational('Test generational');
    console.log('✅ Success!');
} catch (err) {
    console.log('❌ Error:', err.message);
}
