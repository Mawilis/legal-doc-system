/* eslint-disable */
/**
 * Wilsy OS - Logger Utility
 * Structured JSON logging with levels
 */

const LOG_LEVELS = {
  error: 0,
  warn: 1,
  info: 2,
  debug: 3
};

class Logger {
  constructor(level = 'info') {
    this.level = level;
  }

  error(message, meta = {}) {
    this._log('error', message, meta);
  }

  warn(message, meta = {}) {
    this._log('warn', message, meta);
  }

  info(message, meta = {}) {
    this._log('info', message, meta);
  }

  debug(message, meta = {}) {
    this._log('debug', message, meta);
  }

  _log(level, message, meta) {
    if (LOG_LEVELS[level] <= LOG_LEVELS[this.level]) {
      const logEntry = {
        timestamp: new Date().toISOString(),
        level,
        message,
        ...meta
      };
      
      // In production, this would go to a proper logging service
      if (level === 'error') {
        console.error(JSON.stringify(logEntry));
      } else {
        console.log(JSON.stringify(logEntry));
      }
    }
  }
}

const defaultLogger = new Logger(process.env.LOG_LEVEL || 'info');

export default defaultLogger;
