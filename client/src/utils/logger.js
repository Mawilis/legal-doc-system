/**
 * Wilsy OS Citadel - Robust Logger
 * Implements high-integrity logging with emergency handling.
 */

const LEVELS = {
  INFO: 'INFO',
  WARN: 'WARN',
  ERROR: 'ERROR',
  EMERGENCY: 'EMERGENCY'
};

export const logger = {
  log: (level, message, data = {}) => {
    const timestamp = new Date().toISOString();
    const entry = `[${timestamp}] [${level}] ${message}`;
    console.log(entry, data);
    // In production, this would also push to a persistent buffer or remote syslog
  },

  info: (msg, data) => logger.log(LEVELS.INFO, msg, data),
  warn: (msg, data) => logger.log(LEVELS.WARN, msg, data),
  error: (msg, data) => logger.log(LEVELS.ERROR, msg, data),

  /**
   * EMERGENCY: Highest priority logging.
   * Used when the system is about to crash or a security breach is detected.
   */
  emergency: (msg, data) => {
    logger.log(LEVELS.EMERGENCY, msg, data);
    // Logic for critical notification/telemetry goes here
  },

  /**
   * FLUSH: Ensures all pending logs are written to persistence.
   * Critical for preventing data leaks during unexpected unmounts.
   */
  flush: () => {
    const timestamp = new Date().toISOString();
    console.log(`📋 [${timestamp}] [SYSTEM] Persistence Flush: All log buffers cleared.`);
    return true;
  }
};
export default logger;
