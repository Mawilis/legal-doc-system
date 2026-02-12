// ====================================================================
// FILE: server/utils/errors.js - COMPLETE ERROR HIERARCHY
// ====================================================================
/**
 * WILSYS OS - FORENSIC ERROR HANDLING FRAMEWORK
 * NIST SP 800-63B Compliant Error Messages
 * POPIA Section 19 - Security Measures
 */

class BaseError extends Error {
    constructor(message, options = {}) {
        super(message);
        this.name = this.constructor.name;
        this.timestamp = new Date().toISOString();
        this.errorId = require('crypto').randomUUID();
        this.statusCode = options.statusCode || 500;
        this.code = options.code || 'ERR_UNKNOWN';
        this.details = options.details || {};
        this.correlationId = options.correlationId;
        this.source = options.source;
        this.stack = options.stack || this.stack;

        // Forensic metadata
        this.forensic = {
            capturedAt: this.timestamp,
            capturedBy: process.pid,
            nodeVersion: process.version,
            environment: process.env.NODE_ENV
        };
    }

    toJSON() {
        return {
            error: this.name,
            message: this.message,
            code: this.code,
            statusCode: this.statusCode,
            errorId: this.errorId,
            timestamp: this.timestamp,
            correlationId: this.correlationId,
            details: this.details,
            forensic: this.forensic
        };
    }
}

class ValidationError extends BaseError {
    constructor(message, details = {}) {
        super(message, {
            statusCode: 400,
            code: 'ERR_VALIDATION',
            details
        });
    }
}

class ComplianceError extends BaseError {
    constructor(message, details = {}) {
        super(message, {
            statusCode: 451, // Unavailable For Legal Reasons
            code: 'ERR_COMPLIANCE',
            details
        });

        this.regulatoryRef = details.regulatoryRef;
        this.violations = details.violations;
        this.remediation = details.remediation;
        this.deadline = details.deadline;
    }
}

class AuthorizationError extends BaseError {
    constructor(message, details = {}) {
        super(message, {
            statusCode: 403,
            code: 'ERR_AUTHORIZATION',
            details
        });

        this.requiredRoles = details.requiredRoles;
        this.userRoles = details.userRoles;
        this.userId = details.userId;
        this.resource = details.resource;
        this.complianceReference = details.complianceReference;
    }
}

class AuthenticationError extends BaseError {
    constructor(message, details = {}) {
        super(message, {
            statusCode: 401,
            code: 'ERR_AUTHENTICATION',
            details
        });
    }
}

class NotFoundError extends BaseError {
    constructor(message, details = {}) {
        super(message, {
            statusCode: 404,
            code: 'ERR_NOT_FOUND',
            details
        });
    }
}

class ConflictError extends BaseError {
    constructor(message, details = {}) {
        super(message, {
            statusCode: 409,
            code: 'ERR_CONFLICT',
            details
        });
    }
}

class RateLimitError extends BaseError {
    constructor(message, details = {}) {
        super(message, {
            statusCode: 429,
            code: 'ERR_RATE_LIMIT',
            details
        });
    }
}

class ServiceUnavailableError extends BaseError {
    constructor(message, details = {}) {
        super(message, {
            statusCode: 503,
            code: 'ERR_SERVICE_UNAVAILABLE',
            details
        });
    }
}

class RetryableError extends BaseError {
    constructor(message, details = {}) {
        super(message, {
            statusCode: 500,
            code: 'ERR_RETRYABLE',
            details
        });

        this.retryAfter = details.retryAfter || 5;
        this.maxRetries = details.maxRetries || 3;
    }
}

module.exports = {
    BaseError,
    ValidationError,
    ComplianceError,
    AuthorizationError,
    AuthenticationError,
    NotFoundError,
    ConflictError,
    RateLimitError,
    ServiceUnavailableError,
    RetryableError
};