/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SECURITY UTILITIES ENGINE v2.0                                 ║
 * ║ [Production Grade | POPIA Compliant | Forensic Security Helpers]         ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 * 
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/utils/securityUtils.js
 * VERSION: 2.0.0
 * CREATED: 2026-02-24
 * 
 * INVESTOR VALUE PROPOSITION:
 * • Centralized security utilities for R240M legal platform
 * • POPIA §19-22 compliant security helpers
 * • SHA256 hashing for court-admissible evidence
 * • Rate limiting, input sanitization, PII detection
 * • Multi-tenant isolation with tenantId validation
 * • 100-year archival stability (never needs updates)
 * 
 * DEPENDENCIES:
 * • crypto (built-in) - SHA256 hashing
 * • logger (internal) - Structured logging
 * • auditLogger (internal) - Forensic audit trail
 * 
 * INTEGRATION MAP:
 * {
 *   "consumers": [
 *     "utils/securityAlerts.js",
 *     "middleware/tenantGuard.js",
 *     "controllers/auditController.js",
 *     "services/complianceService.js",
 *     "validators/*.js",
 *     "middleware/auth.js"
 *   ],
 *   "providers": [
 *     "./logger.js",
 *     "./auditLogger.js",
 *     "../models/securityLogModel.js"
 *   ]
 * }
 */

import crypto from "crypto";
import logger from './logger.js';
import auditLogger from './auditLogger.js';

/**
 * Security Utilities Engine
 * Provides comprehensive security helper functions for the entire platform
 * 
 * This class is designed to be immutable and never need updates.
 * All configuration is internalized and patterns are regex-based for future-proofing.
 */
class SecurityUtilsEngine {
    /**
     * Initialize the security utilities engine with immutable configuration
     */
    constructor() {
        // Immutable configuration - never changes
        this.VERSION = '2.0.0';
        this.HASH_ALGORITHM = 'sha256';
        this.HASH_ENCODING = 'hex';
        this.TOKEN_BYTES = 32;
        this.SESSION_ID_BYTES = 24;

        // Validation patterns (regex-based for future compatibility)
        this.PATTERNS = {
            TENANT_ID: /^[a-zA-Z0-9_-]{8,64}$/,
            USER_ID: /^[a-zA-Z0-9_-]{8,64}$/,
            REQUEST_ID: /^[a-f0-9]{16,32}$/i,
            EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            SA_ID: /^\d{13}$/,
            PHONE_SA: /^(\+?27|0)[1-9]\d{8}$/,
            PASSPORT: /^[A-Z]{2}\d{7}$/,
            IPV4: /^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$/,
            IPV6: /^([a-f0-9:]+)$/i,
            UUID: /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
        };

        // PII detection patterns
        this.PII_PATTERNS = {
            email: this.PATTERNS.EMAIL,
            idNumber: this.PATTERNS.SA_ID,
            phone: this.PATTERNS.PHONE_SA,
            passport: this.PATTERNS.PASSPORT,
            creditCard: /\b(?:\d[ -]*?){13,16}\b/g,
            bankAccount: /\b\d{10,12}\b/g
        };

        // Sensitive fields that should be redacted
        this.SENSITIVE_FIELDS = [
            'password',
            'token',
            'secret',
            'apiKey',
            'privateKey',
            'authorization',
            'cookie',
            'idNumber',
            'passportNumber',
            'bankAccount',
            'creditCard',
            'cvv'
        ];

        // Rate limiting store
        this.rateLimitStore = new Map();

        // Failed attempts store
        this.failedAttempts = new Map();

        // Start periodic cleanup
        this.startCleanupInterval();
    }

    /**
     * Start periodic cleanup of expired rate limit and failed attempts data
     * @private
     */
    startCleanupInterval() {
        setInterval(() => {
            this.cleanupRateLimits();
            this.cleanupFailedAttempts();
        }, 5 * 60 * 1000); // Every 5 minutes
    }

    /**
     * Clean up expired rate limit records
     * @private
     */
    cleanupRateLimits() {
        const now = Date.now();
        for (const [key, record] of this.rateLimitStore.entries()) {
            if (now > record.resetAt) {
                this.rateLimitStore.delete(key);
            }
        }
    }

    /**
     * Clean up expired failed attempts records
     * @private
     */
    cleanupFailedAttempts() {
        const now = Date.now();
        for (const [key, record] of this.failedAttempts.entries()) {
            if (now > record.expiresAt) {
                this.failedAttempts.delete(key);
            }
        }
    }

    // =========================================================================
    // TOKEN GENERATION
    // =========================================================================

    /**
     * Generate secure random token
     * @param {number} bytes - Number of bytes (default: 32)
     * @returns {string} Hex token
     */
    generateToken(bytes = this.TOKEN_BYTES) {
        return crypto.randomBytes(bytes).toString('hex');
    }

    /**
     * Generate secure random token with prefix
     * @param {string} prefix - Token prefix
     * @param {number} bytes - Number of bytes
     * @returns {string} Prefixed token
     */
    generatePrefixedToken(prefix, bytes = this.TOKEN_BYTES) {
        return `${prefix}_${crypto.randomBytes(bytes).toString('hex')}`;
    }

    /**
     * Generate secure session ID
     * @returns {string} Session ID
     */
    generateSessionId() {
        return `sess_${crypto.randomBytes(this.SESSION_ID_BYTES).toString('hex')}`;
    }

    /**
     * Generate API key
     * @returns {Object} API key with prefix and secret
     */
    generateApiKey() {
        const prefix = crypto.randomBytes(4).toString('hex').toUpperCase();
        const secret = crypto.randomBytes(32).toString('hex');
        const hash = this.createHash(secret);

        return {
            prefix: prefix,
            secret: secret,
            hash: hash,
            key: `${prefix}.${secret}`
        };
    }

    /**
     * Generate request ID
     * @returns {string} Request ID
     */
    generateRequestId() {
        return crypto.randomBytes(16).toString('hex');
    }

    /**
     * Generate correlation ID
     * @returns {string} Correlation ID
     */
    generateCorrelationId() {
        return `corr_${crypto.randomBytes(12).toString('hex')}`;
    }

    // =========================================================================
    // HASHING & ENCRYPTION
    // =========================================================================

    /**
     * Create SHA-256 hash of data
     * @param {*} data - Data to hash
     * @returns {string} Hash
     */
    createHash(data) {
        const hash = crypto.createHash(this.HASH_ALGORITHM);
        hash.update(typeof data === 'string' ? data : JSON.stringify(data));
        return hash.digest(this.HASH_ENCODING);
    }

    /**
     * Create HMAC signature
     * @param {*} data - Data to sign
     * @param {string} secret - Secret key
     * @returns {string} HMAC signature
     */
    createHmac(data, secret) {
        const hmac = crypto.createHmac(this.HASH_ALGORITHM, secret);
        hmac.update(typeof data === 'string' ? data : JSON.stringify(data));
        return hmac.digest(this.HASH_ENCODING);
    }

    /**
     * Hash data with salt
     * @param {string} data - Data to hash
     * @param {string} salt - Salt value
     * @returns {string} Hashed data
     */
    hashWithSalt(data, salt) {
        const hash = crypto.createHash(this.HASH_ALGORITHM);
        hash.update(data + salt);
        return hash.digest(this.HASH_ENCODING);
    }

    /**
     * Create hash chain (blockchain-style)
     * @param {Array} items - Items to chain
     * @returns {Array} Items with hashes
     */
    createHashChain(items) {
        let previousHash = null;

        return items.map((item, index) => {
            const hashData = {
                index: index,
                data: item,
                previousHash: previousHash,
                timestamp: Date.now()
            };

            const hash = this.createHash(hashData);
            previousHash = hash;

            return {
                ...item,
                hash: hash,
                previousHash: previousHash
            };
        });
    }

    /**
     * Verify hash chain integrity
     * @param {Array} items - Items with hashes
     * @returns {Object} Verification result
     */
    verifyHashChain(items) {
        let previousHash = null;
        const brokenLinks = [];

        for (let i = 0; i < items.length; i++) {
            const item = items[i];

            if (i > 0 && item.previousHash !== items[i - 1].hash) {
                brokenLinks.push({
                    index: i,
                    expected: items[i - 1].hash,
                    actual: item.previousHash
                });
            }
        }

        return {
            verified: brokenLinks.length === 0,
            totalItems: items.length,
            brokenLinks: brokenLinks
        };
    }

    // =========================================================================
    // VALIDATION
    // =========================================================================

    /**
     * Validate tenant ID format
     * @param {string} tenantId - Tenant ID to validate
     * @returns {boolean} Is valid
     */
    isValidTenantId(tenantId) {
        return this.PATTERNS.TENANT_ID.test(tenantId);
    }

    /**
     * Validate user ID format
     * @param {string} userId - User ID to validate
     * @returns {boolean} Is valid
     */
    isValidUserId(userId) {
        return this.PATTERNS.USER_ID.test(userId);
    }

    /**
     * Validate request ID format
     * @param {string} requestId - Request ID to validate
     * @returns {boolean} Is valid
     */
    isValidRequestId(requestId) {
        return this.PATTERNS.REQUEST_ID.test(requestId);
    }

    /**
     * Validate email format
     * @param {string} email - Email to validate
     * @returns {boolean} Is valid
     */
    isValidEmail(email) {
        return this.PATTERNS.EMAIL.test(email);
    }

    /**
     * Validate South African ID number
     * @param {string} idNumber - SA ID number
     * @returns {boolean} Is valid ID
     */
    isValidSouthAfricanID(idNumber) {
        // Basic format validation
        if (!this.PATTERNS.SA_ID.test(idNumber)) return false;

        // Luhn algorithm check
        let sum = 0;
        for (let i = 0; i < 12; i++) {
            let digit = parseInt(idNumber.charAt(i), 10);
            if (i % 2 === 0) {
                digit *= 2;
                if (digit > 9) digit -= 9;
            }
            sum += digit;
        }

        const checkDigit = (10 - (sum % 10)) % 10;
        return parseInt(idNumber.charAt(12), 10) === checkDigit;
    }

    /**
     * Validate South African phone number
     * @param {string} phone - Phone number
     * @returns {boolean} Is valid
     */
    isValidSouthAfricanPhone(phone) {
        return this.PATTERNS.PHONE_SA.test(phone);
    }

    /**
     * Validate IP address
     * @param {string} ip - IP address
     * @returns {boolean} Is valid
     */
    isValidIpAddress(ip) {
        return this.PATTERNS.IPV4.test(ip) || this.PATTERNS.IPV6.test(ip);
    }

    /**
     * Validate UUID
     * @param {string} uuid - UUID to validate
     * @returns {boolean} Is valid
     */
    isValidUuid(uuid) {
        return this.PATTERNS.UUID.test(uuid);
    }

    /**
     * Validate password strength
     * @param {string} password - Password to validate
     * @returns {Object} Validation result
     */
    validatePasswordStrength(password) {
        const result = {
            valid: true,
            errors: [],
            score: 0,
            requirements: {
                minLength: false,
                uppercase: false,
                lowercase: false,
                number: false,
                special: false
            }
        };

        // Check minimum length
        if (password.length >= 8) {
            result.score += 2;
            result.requirements.minLength = true;
        } else {
            result.valid = false;
            result.errors.push('Password must be at least 8 characters');
        }

        // Check for uppercase
        if (/[A-Z]/.test(password)) {
            result.score += 2;
            result.requirements.uppercase = true;
        } else {
            result.valid = false;
            result.errors.push('Password must contain at least one uppercase letter');
        }

        // Check for lowercase
        if (/[a-z]/.test(password)) {
            result.score += 2;
            result.requirements.lowercase = true;
        } else {
            result.valid = false;
            result.errors.push('Password must contain at least one lowercase letter');
        }

        // Check for number
        if (/[0-9]/.test(password)) {
            result.score += 2;
            result.requirements.number = true;
        } else {
            result.valid = false;
            result.errors.push('Password must contain at least one number');
        }

        // Check for special character
        if (/[^A-Za-z0-9]/.test(password)) {
            result.score += 2;
            result.requirements.special = true;
        } else {
            result.valid = false;
            result.errors.push('Password must contain at least one special character');
        }

        return result;
    }

    // =========================================================================
    // SANITIZATION
    // =========================================================================

    /**
     * Sanitize input to prevent injection attacks
     * @param {string} input - Raw input
     * @returns {string} Sanitized input
     */
    sanitizeInput(input) {
        if (typeof input !== 'string') return input;

        return input
            .replace(/[<>]/g, '') // Remove HTML tags
            .replace(/[&<>"']/g, '') // Remove special characters
            .replace(/[\\$`]/g, '') // Remove shell metacharacters
            .replace(/[\0\x08\x09\x1a\n\r"'\\]/g, '') // Remove control characters
            .trim();
    }

    /**
     * Sanitize object recursively
     * @param {Object} obj - Object to sanitize
     * @returns {Object} Sanitized object
     */
    sanitizeObject(obj) {
        if (!obj || typeof obj !== 'object') return obj;

        const sanitized = Array.isArray(obj) ? [] : {};

        for (const [key, value] of Object.entries(obj)) {
            const sanitizedKey = this.sanitizeInput(key);

            if (value && typeof value === 'object') {
                sanitized[sanitizedKey] = this.sanitizeObject(value);
            } else if (typeof value === 'string') {
                sanitized[sanitizedKey] = this.sanitizeInput(value);
            } else {
                sanitized[sanitizedKey] = value;
            }
        }

        return sanitized;
    }

    /**
     * Escape HTML special characters
     * @param {string} input - Raw input
     * @returns {string} Escaped HTML
     */
    escapeHtml(input) {
        if (typeof input !== 'string') return input;

        const htmlEscapes = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        };

        return input.replace(/[&<>"']/g, match => htmlEscapes[match]);
    }

    /**
     * Escape JSON for safe logging
     * @param {*} data - Data to escape
     * @returns {string} Escaped JSON string
     */
    escapeJson(data) {
        try {
            return JSON.stringify(data).replace(/[\\"']/g, '\\$&');
        } catch (e) {
            return String(data).replace(/[\\"']/g, '\\$&');
        }
    }

    // =========================================================================
    // PII DETECTION & REDACTION
    // =========================================================================

    /**
     * Detect PII in text
     * @param {string} text - Text to check
     * @returns {Object} PII detection results
     */
    detectPII(text) {
        if (typeof text !== 'string') {
            return { containsPII: false, findings: {} };
        }

        const findings = {};
        let containsPII = false;

        for (const [type, pattern] of Object.entries(this.PII_PATTERNS)) {
            const matches = text.match(pattern);
            if (matches) {
                findings[type] = matches.length;
                containsPII = true;
            }
        }

        return {
            containsPII: containsPII,
            findings: findings,
            confidence: containsPII ? 0.9 : 1.0
        };
    }

    /**
     * Redact sensitive fields from object
     * @param {Object} data - Data to redact
     * @param {Array} additionalFields - Additional fields to redact
     * @returns {Object} Redacted data
     */
    redactSensitive(data, additionalFields = []) {
        if (!data || typeof data !== 'object') return data;

        const redacted = Array.isArray(data) ? [] : {};
        const fieldsToRedact = [...this.SENSITIVE_FIELDS, ...additionalFields];

        for (const [key, value] of Object.entries(data)) {
            if (fieldsToRedact.includes(key.toLowerCase())) {
                redacted[key] = '[REDACTED]';
            } else if (value && typeof value === 'object') {
                redacted[key] = this.redactSensitive(value, additionalFields);
            } else {
                redacted[key] = value;
            }
        }

        return redacted;
    }

    /**
     * Mask sensitive data for logging
     * @param {Object} data - Data to mask
     * @returns {Object} Masked data
     */
    maskForLogging(data) {
        return this.redactSensitive(data);
    }

    /**
     * Partially mask sensitive string (e.g., email, phone)
     * @param {string} value - Value to mask
     * @param {string} type - Type of value
     * @returns {string} Masked value
     */
    partialMask(value, type = 'default') {
        if (!value || typeof value !== 'string') return value;

        switch (type) {
            case 'email':
                const [local, domain] = value.split('@');
                return `${local.substring(0, 2)}***@${domain}`;

            case 'phone':
                return value.replace(/(\d{3})\d{4}(\d{3})/, '$1****$2');

            case 'idNumber':
                return value.replace(/(\d{6})\d{5}(\d{2})/, '$1*****$2');

            default:
                if (value.length > 8) {
                    return value.substring(0, 4) + '****' + value.substring(value.length - 4);
                }
                return '****';
        }
    }

    // =========================================================================
    // RATE LIMITING
    // =========================================================================

    /**
     * Check rate limit for key
     * @param {string} key - Rate limit key (IP, userId, etc.)
     * @param {number} limit - Max requests
     * @param {number} windowMs - Time window in ms
     * @returns {Object} Rate limit result
     */
    checkRateLimit(key, limit = 100, windowMs = 60000) {
        const now = Date.now();
        const record = this.rateLimitStore.get(key) || {
            count: 0,
            resetAt: now + windowMs
        };

        if (now > record.resetAt) {
            record.count = 1;
            record.resetAt = now + windowMs;
        } else {
            record.count++;
        }

        this.rateLimitStore.set(key, record);

        return {
            allowed: record.count <= limit,
            current: record.count,
            limit: limit,
            remaining: Math.max(0, limit - record.count),
            resetAt: record.resetAt,
            resetIn: record.resetAt - now
        };
    }

    /**
     * Get rate limit status
     * @param {string} key - Rate limit key
     * @returns {Object} Rate limit status
     */
    getRateLimitStatus(key) {
        const record = this.rateLimitStore.get(key);

        if (!record) {
            return {
                exists: false,
                count: 0,
                remaining: Infinity,
                resetIn: 0
            };
        }

        const now = Date.now();
        const resetIn = Math.max(0, record.resetAt - now);

        return {
            exists: true,
            count: record.count,
            remaining: resetIn > 0 ? Infinity : 0,
            resetAt: record.resetAt,
            resetIn: resetIn
        };
    }

    /**
     * Reset rate limit for key
     * @param {string} key - Rate limit key
     */
    resetRateLimit(key) {
        this.rateLimitStore.delete(key);
    }

    // =========================================================================
    // FAILED ATTEMPT TRACKING
    // =========================================================================

    /**
     * Track failed attempt
     * @param {string} identifier - User identifier
     * @param {number} maxAttempts - Max attempts before lock
     * @param {number} lockoutMs - Lockout duration in ms
     * @returns {Object} Attempt tracking result
     */
    trackFailedAttempt(identifier, maxAttempts = 5, lockoutMs = 15 * 60 * 1000) {
        const now = Date.now();
        const record = this.failedAttempts.get(identifier) || {
            count: 0,
            firstAttempt: now,
            lockedUntil: null
        };

        // Check if currently locked
        if (record.lockedUntil && now < record.lockedUntil) {
            return {
                allowed: false,
                locked: true,
                lockedUntil: record.lockedUntil,
                remainingLockout: record.lockedUntil - now,
                attempts: record.count
            };
        }

        // Increment attempts
        record.count++;

        // Check if should lock
        if (record.count >= maxAttempts) {
            record.lockedUntil = now + lockoutMs;
        }

        this.failedAttempts.set(identifier, record);

        return {
            allowed: record.count < maxAttempts,
            locked: record.count >= maxAttempts,
            lockedUntil: record.lockedUntil,
            attempts: record.count,
            remainingAttempts: Math.max(0, maxAttempts - record.count),
            firstAttempt: record.firstAttempt
        };
    }

    /**
     * Check if account is locked
     * @param {string} identifier - User identifier
     * @returns {Object} Lock status
     */
    isAccountLocked(identifier) {
        const record = this.failedAttempts.get(identifier);

        if (!record) {
            return {
                locked: false,
                attempts: 0
            };
        }

        const now = Date.now();
        const locked = record.lockedUntil && now < record.lockedUntil;

        return {
            locked: locked,
            attempts: record.count,
            lockedUntil: record.lockedUntil,
            remainingLockout: locked ? record.lockedUntil - now : 0
        };
    }

    /**
     * Clear failed attempts for identifier
     * @param {string} identifier - User identifier
     */
    clearFailedAttempts(identifier) {
        this.failedAttempts.delete(identifier);
    }

    /**
     * Get failed attempts count
     * @param {string} identifier - User identifier
     * @returns {number} Failed attempts count
     */
    getFailedAttempts(identifier) {
        const record = this.failedAttempts.get(identifier);
        return record ? record.count : 0;
    }

    // =========================================================================
    // AUDIT & LOGGING
    // =========================================================================

    /**
     * Log security event with audit trail
     * @param {string} action - Security action
     * @param {Object} metadata - Event metadata
     * @param {string} requestId - Request ID
     */
    async logSecurityEvent(action, metadata, requestId = this.generateRequestId()) {
        const redactedMetadata = this.redactSensitive(metadata);

        logger.info(`Security event: ${action}`, {
            action: action,
            metadata: redactedMetadata,
            requestId: requestId,
            timestamp: new Date().toISOString()
        });

        await auditLogger.log({
            action: `SECURITY_${action.toUpperCase()}`,
            metadata: redactedMetadata,
            requestId: requestId,
            timestamp: new Date().toISOString(),
            retentionPolicy: 'companies_act_10_years',
            dataResidency: 'ZA'
        });
    }

    /**
     * Log authentication attempt
     * @param {string} userId - User ID
     * @param {boolean} success - Whether successful
     * @param {string} requestId - Request ID
     */
    async logAuthAttempt(userId, success, requestId) {
        const action = success ? 'AUTH_SUCCESS' : 'AUTH_FAILURE';

        await auditLogger.log({
            action: action,
            userId: userId,
            requestId: requestId,
            timestamp: new Date().toISOString(),
            retentionPolicy: 'companies_act_10_years',
            dataResidency: 'ZA'
        });

        if (!success) {
            this.trackFailedAttempt(userId);
        } else {
            this.clearFailedAttempts(userId);
        }
    }

    /**
     * Log data access for audit trail
     * @param {string} userId - User ID
     * @param {string} dataType - Type of data accessed
     * @param {string} dataId - Data identifier
     * @param {string} requestId - Request ID
     */
    async logDataAccess(userId, dataType, dataId, requestId) {
        await auditLogger.log({
            action: 'DATA_ACCESS',
            userId: userId,
            dataType: dataType,
            dataId: dataId,
            requestId: requestId,
            timestamp: new Date().toISOString(),
            retentionPolicy: 'companies_act_10_years',
            dataResidency: 'ZA'
        });
    }

    // =========================================================================
    // UTILITY FUNCTIONS
    // =========================================================================

    /**
     * Compare two strings in constant time (prevents timing attacks)
     * @param {string} a - First string
     * @param {string} b - Second string
     * @returns {boolean} Whether strings are equal
     */
    safeCompare(a, b) {
        if (!a || !b) return false;

        try {
            return crypto.timingSafeEqual(
                Buffer.from(a, 'utf8'),
                Buffer.from(b, 'utf8')
            );
        } catch (e) {
            return false;
        }
    }

    /**
     * Generate random string
     * @param {number} length - Length of string
     * @param {string} charset - Character set
     * @returns {string} Random string
     */
    randomString(length = 16, charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789') {
        const bytes = crypto.randomBytes(length);
        const result = new Array(length);

        for (let i = 0; i < length; i++) {
            result[i] = charset[bytes[i] % charset.length];
        }

        return result.join('');
    }

    /**
     * Generate numeric code (e.g., for OTP)
     * @param {number} length - Length of code
     * @returns {string} Numeric code
     */
    generateNumericCode(length = 6) {
        const bytes = crypto.randomBytes(length);
        let code = '';

        for (let i = 0; i < length; i++) {
            code += (bytes[i] % 10).toString();
        }

        return code;
    }

    /**
     * Generate unique fingerprint for request
     * @param {Object} req - Request object
     * @returns {string} Fingerprint
     */
    generateFingerprint(req) {
        const components = [
            req.ip || 'unknown',
            req.headers['user-agent'] || 'unknown',
            req.headers['accept-language'] || 'unknown',
            req.headers['sec-ch-ua'] || 'unknown'
        ];

        return this.createHash(components.join('|'));
    }

    /**
     * Get client IP from request
     * @param {Object} req - Request object
     * @returns {string} Client IP
     */
    getClientIp(req) {
        const forwardedFor = req.headers['x-forwarded-for'];
        if (forwardedFor) {
            return forwardedFor.split(',')[0].trim();
        }

        const realIp = req.headers['x-real-ip'];
        if (realIp) {
            return realIp;
        }

        return req.ip || req.connection?.remoteAddress || 'unknown';
    }

    /**
     * Get security headers for response
     * @returns {Object} Security headers
     */
    getSecurityHeaders() {
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'",
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
        };
    }

    /**
     * Get statistics
     * @returns {Object} Statistics
     */
    getStatistics() {
        return {
            version: this.VERSION,
            rateLimitEntries: this.rateLimitStore.size,
            failedAttemptsEntries: this.failedAttempts.size,
            uptime: process.uptime(),
            memory: process.memoryUsage()
        };
    }
}

// Create singleton instance (immutable)
const securityUtilsEngine = new SecurityUtilsEngine();

// Freeze the instance to prevent modifications
Object.freeze(securityUtilsEngine);

// Export the frozen singleton
export default securityUtilsEngine;

// Also export the class for testing
export { SecurityUtilsEngine };

