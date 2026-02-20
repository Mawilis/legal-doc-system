/*╔══════════════════════════════════════════════════════════════════════════════╗
  ║ CUSTOM ERROR CLASSES - INVESTOR-GRADE                                        ║
  ║ Hierarchical error system with forensic tracking                            ║
  ╚══════════════════════════════════════════════════════════════════════════════╝*/

class BaseError extends Error {
    constructor(message, options = {}) {
        super(message);
        this.name = this.constructor.name;
        this.timestamp = new Date().toISOString();
        this.correlationId = options.correlationId || this._generateCorrelationId();
        this.code = options.code || 'ERR_UNKNOWN';
        this.statusCode = options.statusCode || 500;
        this.details = options.details || {};
        this.stack = options.stack || this.stack;
        
        // Forensic tracking
        this.severity = options.severity || 'ERROR';
        this.auditLogged = false;
    }

    _generateCorrelationId() {
        return `err_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    toJSON() {
        return {
            name: this.name,
            message: this.message,
            code: this.code,
            statusCode: this.statusCode,
            correlationId: this.correlationId,
            timestamp: this.timestamp,
            severity: this.severity,
            details: this.details,
            stack: process.env.NODE_ENV === 'development' ? this.stack : undefined
        };
    }
}

class ValidationError extends BaseError {
    constructor(message, details = {}) {
        super(message, { 
            code: 'ERR_VALIDATION', 
            statusCode: 400,
            severity: 'WARNING',
            details 
        });
    }
}

class DatabaseError extends BaseError {
    constructor(message, options = {}) {
        super(message, { 
            code: 'ERR_DATABASE', 
            statusCode: 503,
            severity: 'CRITICAL',
            ...options 
        });
    }
}

class TenantIsolationError extends BaseError {
    constructor(message, details = {}) {
        super(message, { 
            code: 'ERR_TENANT_ISOLATION', 
            statusCode: 403,
            severity: 'ERROR',
            details 
        });
    }
}

class FICAComplianceError extends BaseError {
    constructor(message, details = {}) {
        super(message, { 
            code: 'ERR_FICA_COMPLIANCE', 
            statusCode: 400,
            severity: 'WARNING',
            details 
        });
    }
}

class CircuitBreakerOpenError extends BaseError {
    constructor(message, details = {}) {
        super(message, { 
            code: 'ERR_CIRCUIT_OPEN', 
            statusCode: 503,
            severity: 'CRITICAL',
            details 
        });
    }
}

module.exports = {
    BaseError,
    ValidationError,
    DatabaseError,
    TenantIsolationError,
    FICAComplianceError,
    CircuitBreakerOpenError
};
