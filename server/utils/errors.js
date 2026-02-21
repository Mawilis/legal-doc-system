/* eslint-disable */
/**
 * 🏛️ WILSYS OS - ERROR HANDLING ENGINE
 * Standard: ES Module (Surgically Standardized)
 * Purpose: Forensic Error Tracking & Compliance Enforcement
 */

export class AppError extends Error {
    constructor(message, statusCode, code, details = {}) {
        super(message);
        this.statusCode = statusCode;
        this.code = code;
        this.details = details;
        this.status = `${statusCode}`.startsWith('4') ? 'fail' : 'error';
        this.isOperational = true;
        this.timestamp = new Date().toISOString();
        Error.captureStackTrace(this, this.constructor);
    }
}

export class ValidationError extends AppError {
    constructor(message, details = {}) {
        super(message, 400, 'VALIDATION_ERROR', details);
    }
}

export class AuthenticationError extends AppError {
    constructor(message = 'Authentication failed', details = {}) {
        super(message, 401, 'AUTHENTICATION_ERROR', details);
    }
}

export class AuthorizationError extends AppError {
    constructor(message = 'Permission denied', details = {}) {
        super(message, 403, 'AUTHORIZATION_ERROR', details);
    }
}

export class NotFoundError extends AppError {
    constructor(message = 'Resource not found', details = {}) {
        super(message, 404, 'NOT_FOUND_ERROR', details);
    }
}

export class ConflictError extends AppError {
    constructor(message, details = {}) {
        super(message, 409, 'CONFLICT_ERROR', details);
    }
}

export class RateLimitError extends AppError {
    constructor(message = 'Too many requests', details = {}) {
        super(message, 429, 'RATE_LIMIT_ERROR', details);
    }
}

export class ComplianceError extends AppError {
    constructor(message, details = {}) {
        super(message, 451, 'COMPLIANCE_VIOLATION', details);
    }
}

export class RetryableError extends AppError {
    constructor(message, details = {}) {
        super(message, 503, 'RETRYABLE_SERVICE_ERROR', details);
    }
}

export class ServiceUnavailableError extends AppError {
    constructor(message, details = {}) {
        super(message, 503, 'SERVICE_UNAVAILABLE', details);
    }
}

export class DataIntegrityError extends AppError {
    constructor(message, details = {}) {
        super(message, 500, 'DATA_INTEGRITY_FAILURE', details);
    }
}

export class CircuitBreakerError extends AppError {
    constructor(message, details = {}) {
        super(message, 503, 'CIRCUIT_BREAKER_OPEN', details);
    }
}

// ============================================================================
// BLOCKCHAIN & REGULATORY SPECIALIZED ERRORS
// ============================================================================

export class BlockchainAnchorError extends AppError {
    constructor(message, details = {}) {
        super(message, 502, 'BLOCKCHAIN_ANCHOR_FAILURE', details);
    }
}

export class LPCComplianceError extends ComplianceError { }
export class FICAComplianceError extends ComplianceError { }
export class GDPRComplianceError extends ComplianceError { }
export class POPIAComplianceError extends ComplianceError { }
export class RegulatoryDeadlineError extends AppError {
    constructor(message, details = {}) {
        super(message, 403, 'REGULATORY_DEADLINE_EXCEEDED', details);
    }
}

/**
 * Investor-Grade Error Factory
 */
export const ErrorFactory = {
    create(type, message, details) {
        switch (type) {
            case 'AUTH': return new AuthenticationError(message, details);
            case 'VALIDATION': return new ValidationError(message, details);
            case 'COMPLIANCE': return new ComplianceError(message, details);
            case 'BLOCKCHAIN': return new BlockchainAnchorError(message, details);
            default: return new AppError(message, 500, 'INTERNAL_SERVER_ERROR', details);
        }
    }
};

export default AppError;