/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ LOGGER - FORTUNE 500 FORENSIC LOGGING                                    ║
  ║ Structured logging with POPIA-compliant redaction                        ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

/**
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/utils/logger.js
 * VERSION: 1.0.0-PRODUCTION
 * CREATED: 2026-03-09
 */

import { hash } from './cryptoUtils.js';
import { redactSensitive } from './redactSensitive.js';

// Log levels
export const LOG_LEVELS = {
  DEBUG: 'DEBUG',
  INFO: 'INFO',
  WARN: 'WARN',
  ERROR: 'ERROR',
  FATAL: 'FATAL'
};

// Current log level (can be changed at runtime)
let currentLogLevel = LOG_LEVELS.INFO;

/**
 * Set the current log level
 */
export const setLogLevel = (level) => {
  if (Object.values(LOG_LEVELS).includes(level)) {
    currentLogLevel = level;
  }
};

/**
 * Get the current log level
 */
export const getLogLevel = () => currentLogLevel;

/**
 * Check if a log level should be logged
 */
const shouldLog = (level) => {
  const levels = Object.values(LOG_LEVELS);
  return levels.indexOf(level) >= levels.indexOf(currentLogLevel);
};

/**
 * Format a log entry
 */
const formatLogEntry = (level, message, metadata = {}) => {
  // Redact any PII from metadata
  const redactedMetadata = redactSensitive(metadata);
  
  // Generate hash for forensic verification
  const logHash = hash(JSON.stringify({
    timestamp: new Date().toISOString(),
    level,
    message,
    metadata: redactedMetadata
  }));

  return {
    timestamp: new Date().toISOString(),
    level,
    message,
    metadata: redactedMetadata,
    logHash,
    environment: process.env.NODE_ENV || 'development',
    version: process.env.npm_package_version || '1.0.0'
  };
};

/**
 * Base log function
 */
const log = (level, message, metadata = {}) => {
  if (!shouldLog(level)) return null;

  const entry = formatLogEntry(level, message, metadata);
  
  // In production, you might want to send this to a logging service
  if (process.env.NODE_ENV === 'production') {
    // Send to logging service
    console.log(JSON.stringify(entry));
  } else {
    // Pretty print in development
    const prefix = `[${entry.timestamp}] [${level}]`;
    switch (level) {
      case LOG_LEVELS.ERROR:
      case LOG_LEVELS.FATAL:
        console.error(prefix, message, entry.metadata);
        break;
      case LOG_LEVELS.WARN:
        console.warn(prefix, message, entry.metadata);
        break;
      default:
        console.log(prefix, message, entry.metadata);
    }
  }

  return entry;
};

// Convenience methods
export const debug = (message, metadata = {}) => log(LOG_LEVELS.DEBUG, message, metadata);
export const info = (message, metadata = {}) => log(LOG_LEVELS.INFO, message, metadata);
export const warn = (message, metadata = {}) => log(LOG_LEVELS.WARN, message, metadata);
export const error = (message, metadata = {}) => log(LOG_LEVELS.ERROR, message, metadata);
export const fatal = (message, metadata = {}) => log(LOG_LEVELS.FATAL, message, metadata);

// Default export with all methods
export default {
  debug,
  info,
  warn,
  error,
  fatal,
  setLogLevel,
  getLogLevel,
  LOG_LEVELS
};
