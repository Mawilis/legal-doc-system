/**
 * File: server/utils/logger.js
 * Path: server/utils/logger.js
 * STATUS: PRODUCTION-READY | STRUCTURED LOGGER | INVESTOR-GRADE
 * VERSION: 1.0.0
 *
 * PURPOSE
 * - Structured, centralized logging utility for Wilsy OS.
 * - Provides JSON logs for ingestion by observability systems (ELK, Datadog, Azure Monitor).
 * - Supports correlation id propagation, log levels, and optional audit forwarding.
 *
 * GUIDING PRINCIPLES
 * - Structured: logs emitted as JSON objects with consistent fields.
 * - Non-blocking: logging should never block request flow.
 * - Safe: avoid logging sensitive PII by default; provide helpers to redact.
 * - Configurable: environment-driven transports and log levels.
 *
 * OWNERSHIP
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - PRIMARY OWNER: @platform
 * - SRE OWNER: @sre
 * - SECURITY OWNER: @security
 * - QA OWNER: @qa
 *
 * REVIEW CHECKLIST
 * - @sre: confirm transports (console, file, remote) and rotation policy.
 * - @security: confirm redaction rules and ensure no secrets are logged.
 * - @platform: confirm JSON schema and field names for downstream parsers.
 *
 * USAGE
 * const logger = require('../utils/logger');
 * logger.info('message', { correlationId: req.context?.correlationId, actor: req.user?.id });
 */

'use strict';

const { createLogger, format, transports } = (() => {
    try {
        return require('winston');
    } catch (e) {
        // Minimal fallback if winston is not installed
        return null;
    }
})();

const os = require('os');

const DEFAULT_LEVEL = process.env.LOG_LEVEL || (process.env.NODE_ENV === 'production' ? 'info' : 'debug');
const SERVICE_NAME = process.env.SERVICE_NAME || 'wilsy-os';
const ENV = process.env.NODE_ENV || 'development';

/* -------------------------
   Redaction helpers
   ------------------------- */

/**
 * redactObject
 * - Shallow redaction for common sensitive keys. Use sparingly.
 */
function redactObject(obj = {}, keysToRedact = ['password', 'token', 'accessToken', 'refreshToken', 'ssn', 'idNumber', 'creditCard']) {
    if (!obj || typeof obj !== 'object') return obj;
    const out = {};
    for (const [k, v] of Object.entries(obj)) {
        if (keysToRedact.includes(k)) {
            out[k] = '[REDACTED]';
        } else {
            out[k] = v;
        }
    }
    return out;
}

/* -------------------------
   Build logger
   ------------------------- */

let logger = null;

if (createLogger) {
    const { combine, timestamp, printf, json, colorize, splat } = format;

    // Custom formatter to include service and environment
    const baseFormat = combine(
        splat(),
        timestamp(),
        json()
    );

    // Console transport for non-production with colorized human output
    const consoleTransport = new transports.Console({
        level: DEFAULT_LEVEL,
        format: process.env.NODE_ENV === 'production'
            ? baseFormat
            : combine(colorize(), timestamp(), printf(({ level, message, timestamp, ...meta }) => {
                const metaStr = Object.keys(meta).length ? JSON.stringify(meta, null, 2) : '';
                return `${timestamp} [${SERVICE_NAME}] ${level}: ${message} ${metaStr}`;
            }))
    });

    const transportList = [consoleTransport];

    // Optional file transport (rotated externally by logrotate or similar)
    if (process.env.LOG_FILE_PATH) {
        transportList.push(new transports.File({
            filename: process.env.LOG_FILE_PATH,
            level: process.env.LOG_FILE_LEVEL || DEFAULT_LEVEL,
            format: baseFormat,
            maxsize: Number(process.env.LOG_FILE_MAX_BYTES || 10 * 1024 * 1024) // 10MB default
        }));
    }

    // Optional remote transport (e.g., HTTP/Logstash) can be added by SRE
    // Example: if (process.env.LOGSTASH_URL) { transportList.push(new transports.Http({...})) }

    logger = createLogger({
        level: DEFAULT_LEVEL,
        defaultMeta: { service: SERVICE_NAME, env: ENV, host: os.hostname() },
        transports: transportList,
        exitOnError: false
    });

    /**
     * safeLog
     * - Wraps logger methods to redact sensitive fields and ensure non-blocking behavior.
     */
    const safeLog = (level, msg, meta = {}) => {
        try {
            const safeMeta = redactObject(meta);
            // Ensure meta is serializable
            logger[level](msg, safeMeta);
        } catch (e) {
            // Fallback to console to avoid throwing
            // eslint-disable-next-line no-console
            console[level](`[LOGGER_FAIL] ${msg}`, meta, e && e.message ? e.message : e);
        }
    };

    // Expose convenience methods
    module.exports = {
        debug: (msg, meta) => safeLog('debug', msg, meta),
        info: (msg, meta) => safeLog('info', msg, meta),
        warn: (msg, meta) => safeLog('warn', msg, meta),
        error: (msg, meta) => safeLog('error', msg, meta),
        child: (meta) => logger.child ? logger.child(meta) : logger, // for structured child loggers
        raw: logger // expose raw winston logger for advanced use
    };
} else {
    // Minimal console fallback for environments without winston
    const levels = ['debug', 'info', 'warn', 'error'];
    const noop = () => { };
    const make = (lvl) => (msg, meta) => {
        try {
            const out = { ts: new Date().toISOString(), level: lvl, service: SERVICE_NAME, env: ENV, message: msg, meta: redactObject(meta || {}) };
            // eslint-disable-next-line no-console
            console.log(JSON.stringify(out));
        } catch (e) {
            // eslint-disable-next-line no-console
            console.log(lvl, msg, meta);
        }
    };

    module.exports = {
        debug: make('debug'),
        info: make('info'),
        warn: make('warn'),
        error: make('error'),
        child: () => module.exports,
        raw: console
    };
}
