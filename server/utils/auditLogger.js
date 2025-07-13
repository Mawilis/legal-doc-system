const fs = require('fs');
const path = require('path');

const logPath = path.join(__dirname, '../logs/audit.log');

// Ensure logs directory exists
if (!fs.existsSync(path.dirname(logPath))) {
    fs.mkdirSync(path.dirname(logPath));
}

const logAuditEvent = (message) => {
    const timestamp = new Date().toISOString();
    const entry = `[${timestamp}] ${message}\n`;
    fs.appendFile(logPath, entry, (err) => {
        if (err) {
            console.error('Failed to write audit log:', err);
        }
    });
};

module.exports = { logAuditEvent };
