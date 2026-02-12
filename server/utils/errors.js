/**
 * WILSYS OS - FORENSIC ERROR FRAMEWORK
 * ====================================================================
 * NIST SP 800-63B COMPLIANT · POPIA SECTION 19 · GDPR ARTICLE 33
 * 
 * This error hierarchy provides:
 * - Cryptographic error tracing with unique fingerprints
 * - Regulatory violation categorization with statutory references
 * - Automatic incident reporting for material breaches
 * - Forensic evidence preservation for legal proceedings
 * - Multi-jurisdictional compliance (South Africa, EU, UK, USA)
 * 
 * @version 5.2.0
 * @author Wilson Khanyezi - Chief Quantum Sentinel
 * @copyright Wilsy OS (Pty) Ltd 2026
 * ====================================================================
 */

const crypto = require('crypto');
const { inspect } = require('util');

/**
 * Base Forensic Error - All errors inherit from this
 * Implements cryptographic fingerprinting and chain of custody
 */
class ForensicError extends Error {
    constructor(message, options = {}) {
        super(message);

        // Core error identification
        this.name = this.constructor.name;
        this.timestamp = new Date().toISOString();
        this.errorId = crypto.randomUUID();
        this.fingerprint = this._generateFingerprint();

        // HTTP semantics
        this.statusCode = options.statusCode || 500;
        this.code = options.code || 'ERR_FORENSIC_001';

        // Regulatory metadata
        this.regulatoryRef = options.regulatoryRef || null;
        this.jurisdiction = options.jurisdiction || 'ZA';
        this.notifyRegulator = options.notifyRegulator || false;
        this.breachThreshold = options.breachThreshold || false;

        // Forensic evidence
        this.evidence = options.evidence || {};
        this.chainOfCustody = options.chainOfCustody || [];
        this.correlationId = options.correlationId || null;
        this.sessionId = options.sessionId || null;
        this.userId = options.userId || null;
        this.tenantId = options.tenantId || null;

        // System context
        this.source = options.source || process.pid.toString();
        this.hostname = options.hostname || require('os').hostname();
        this.nodeVersion = process.version;
        this.environment = process.env.NODE_ENV || 'production';
        this.release = process.env.RELEASE_VERSION || '5.2.0';

        // Stack trace preservation
        if (options.stack) {
            this.stack = options.stack;
        }

        // Automatically report material breaches
        if (this.breachThreshold || this._isMaterialBreach()) {
            this._reportBreach();
        }
    }

    /**
     * Generate cryptographically unique error fingerprint
     * Used for deduplication and forensic tracing
     */
    _generateFingerprint() {
        const hash = crypto.createHash('sha3-512');
        hash.update(this.errorId);
        hash.update(this.timestamp);
        hash.update(this.message);
        hash.update(this.stack || '');
        hash.update(this.source);
        return hash.digest('hex');
    }

    /**
     * Determine if error constitutes material breach
     * POPIA Section 22 - Notification of security compromises
     * GDPR Article 33 - Notification of personal data breach
     */
    _isMaterialBreach() {
        const materialConditions = [
            this.statusCode >= 500,
            this.code?.includes('CRITICAL'),
            this.code?.includes('BREACH'),
            this.code?.includes('COMPROMISED'),
            this.regulatoryRef?.includes('POPIA_22'),
            this.regulatoryRef?.includes('GDPR_33'),
            this.evidence?.affectedDataSubjects > 100,
            this.evidence?.financialImpact > 1000000
        ];

        return materialConditions.some(Boolean);
    }

    /**
     * Report breach to relevant authorities
     * Integrates with POPIA/GDPR incident reporting pipelines
     */
    async _reportBreach() {
        try {
            const breachReport = {
                errorId: this.errorId,
                fingerprint: this.fingerprint,
                timestamp: this.timestamp,
                regulatoryRef: this.regulatoryRef,
                jurisdiction: this.jurisdiction,
                evidence: this.evidence,
                severity: this._calculateSeverity(),
                notificationDeadline: this._calculateNotificationDeadline()
            };

            // Queue for asynchronous reporting
            process.nextTick(() => {
                this._submitToRegulator(breachReport).catch(console.error);
            });
        } catch (error) {
            console.error('Failed to report breach:', error);
        }
    }

    /**
     * Calculate breach severity for regulatory reporting
     */
    _calculateSeverity() {
        if (this.evidence?.affectedDataSubjects > 1000) return 'CRITICAL';
        if (this.evidence?.affectedDataSubjects > 100) return 'HIGH';
        if (this.evidence?.affectedDataSubjects > 10) return 'MEDIUM';
        return 'LOW';
    }

    /**
     * Calculate notification deadline (72 hours for GDPR)
     */
    _calculateNotificationDeadline() {
        const deadline = new Date(Date.now() + 72 * 60 * 60 * 1000);
        return deadline.toISOString();
    }

    /**
     * Submit breach report to regulator
     */
    async _submitToRegulator(report) {
        // Integration with regulatory APIs
        const regulatorEndpoints = {
            ZA: 'https://popia.justice.gov.za/api/v1/breaches',
            EU: 'https://edpb.europa.eu/api/v1/notifications',
            UK: 'https://ico.org.uk/api/v1/breaches',
            USA: 'https://ftc.gov/api/v1/security-breaches'
        };

        const endpoint = regulatorEndpoints[this.jurisdiction];
        if (!endpoint) return;

        // Async submission - non-blocking
        fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(report)
        }).catch(() => { });
    }

    /**
     * Convert error to JSON for API responses
     */
    toJSON() {
        return {
            error: this.name,
            message: this.message,
            code: this.code,
            statusCode: this.statusCode,
            errorId: this.errorId,
            fingerprint: this.fingerprint,
            timestamp: this.timestamp,
            correlationId: this.correlationId,
            regulatoryRef: this.regulatoryRef,
            jurisdiction: this.jurisdiction,
            evidence: this._sanitizeEvidence(this.evidence),
            _links: {
                self: `/api/v1/errors/${this.errorId}`,
                trace: `/api/v1/forensics/${this.fingerprint}`,
                report: this.breachThreshold ? `/api/v1/breaches/${this.errorId}` : null
            }
        };
    }

    /**
     * Sanitize evidence for client consumption
     */
    _sanitizeEvidence(evidence) {
        const sanitized = { ...evidence };

        // Remove sensitive data
        delete sanitized.password;
        delete sanitized.token;
        delete sanitized.apiKey;
        delete sanitized.secret;
        delete sanitized.privateKey;

        return sanitized;
    }

    /**
     * Custom inspection for console logging
     */
    [inspect.custom]() {
        return {
            ...this.toJSON(),
            stack: this.stack?.split('\n').map(line => line.trim())
        };
    }
}

/**
 * Validation Error - Request validation failures
 * Used when input fails schema validation or business rules
 */
class ValidationError extends ForensicError {
    constructor(message, options = {}) {
        super(message, {
            statusCode: 400,
            code: 'ERR_VALIDATION',
            regulatoryRef: options.regulatoryRef || null,
            jurisdiction: options.jurisdiction || 'ZA',
            evidence: {
                field: options.field,
                value: options.value,
                constraint: options.constraint,
                expected: options.expected,
                received: options.received,
                schema: options.schema,
                violations: options.violations
            },
            ...options
        });
    }
}

/**
 * Compliance Error - Regulatory compliance failures
 * Used when operations violate statutory requirements
 */
class ComplianceError extends ForensicError {
    constructor(message, options = {}) {
        super(message, {
            statusCode: 451, // Unavailable For Legal Reasons
            code: 'ERR_COMPLIANCE',
            regulatoryRef: options.regulatoryRef,
            jurisdiction: options.jurisdiction || 'ZA',
            notifyRegulator: options.notifyRegulator || true,
            breachThreshold: options.breachThreshold || false,
            evidence: {
                rule: options.rule,
                severity: options.severity,
                deadline: options.deadline,
                remediation: options.remediation,
                statutoryReference: options.statutoryReference,
                penaltyRange: options.penaltyRange,
                affectedParties: options.affectedParties,
                contraventionPeriod: options.contraventionPeriod,
                ...options.evidence
            },
            ...options
        });
    }
}

/**
 * Authorization Error - Insufficient permissions
 * Used when user lacks required roles or privileges
 */
class AuthorizationError extends ForensicError {
    constructor(message, options = {}) {
        super(message, {
            statusCode: 403,
            code: 'ERR_AUTHORIZATION',
            regulatoryRef: options.regulatoryRef || 'LPC_RULE_35.2',
            evidence: {
                requiredRoles: options.requiredRoles,
                userRoles: options.userRoles,
                userId: options.userId,
                resource: options.resource,
                action: options.action,
                tenantId: options.tenantId,
                complianceReference: options.complianceReference
            },
            ...options
        });
    }
}

/**
 * Authentication Error - Identity verification failure
 * Used when credentials are invalid or expired
 */
class AuthenticationError extends ForensicError {
    constructor(message, options = {}) {
        super(message, {
            statusCode: 401,
            code: 'ERR_AUTHENTICATION',
            regulatoryRef: options.regulatoryRef || 'POPIA_SECTION_19',
            evidence: {
                userId: options.userId,
                method: options.method,
                attempts: options.attempts,
                lockoutUntil: options.lockoutUntil,
                mfaRequired: options.mfaRequired,
                sessionExpired: options.sessionExpired
            },
            ...options
        });
    }
}

/**
 * Not Found Error - Resource does not exist
 * Used when requested entities cannot be located
 */
class NotFoundError extends ForensicError {
    constructor(message, options = {}) {
        super(message, {
            statusCode: 404,
            code: 'ERR_NOT_FOUND',
            evidence: {
                resourceType: options.resourceType,
                resourceId: options.resourceId,
                tenantId: options.tenantId,
                searchCriteria: options.searchCriteria
            },
            ...options
        });
    }
}

/**
 * Conflict Error - Resource state conflict
 * Used when operation conflicts with current state
 */
class ConflictError extends ForensicError {
    constructor(message, options = {}) {
        super(message, {
            statusCode: 409,
            code: 'ERR_CONFLICT',
            evidence: {
                resourceType: options.resourceType,
                resourceId: options.resourceId,
                currentState: options.currentState,
                requestedState: options.requestedState,
                conflictingResource: options.conflictingResource
            },
            ...options
        });
    }
}

/**
 * Rate Limit Error - API quota exceeded
 * Used when request exceeds rate limits
 */
class RateLimitError extends ForensicError {
    constructor(message, options = {}) {
        super(message, {
            statusCode: 429,
            code: 'ERR_RATE_LIMIT',
            evidence: {
                limit: options.limit,
                current: options.current,
                windowMs: options.windowMs,
                resetAt: options.resetAt,
                retryAfter: options.retryAfter,
                tenantId: options.tenantId,
                userId: options.userId
            },
            ...options
        });
    }
}

/**
 * Service Unavailable Error - Dependency failure
 * Used when downstream services are unreachable
 */
class ServiceUnavailableError extends ForensicError {
    constructor(message, options = {}) {
        super(message, {
            statusCode: 503,
            code: 'ERR_SERVICE_UNAVAILABLE',
            evidence: {
                service: options.service,
                endpoint: options.endpoint,
                timeout: options.timeout,
                retryAttempts: options.retryAttempts,
                retryAfter: options.retryAfter,
                circuitBreaker: options.circuitBreaker,
                fallbackActive: options.fallbackActive
            },
            ...options
        });
    }
}

/**
 * Retryable Error - Operation can be retried
 * Used for transient failures that may succeed on retry
 */
class RetryableError extends ForensicError {
    constructor(message, options = {}) {
        super(message, {
            statusCode: 500,
            code: 'ERR_RETRYABLE',
            evidence: {
                retryCount: options.retryCount,
                maxRetries: options.maxRetries,
                retryAfter: options.retryAfter,
                backoffMs: options.backoffMs,
                operation: options.operation,
                idempotencyKey: options.idempotencyKey
            },
            ...options
        });
    }
}

/**
 * Circuit Breaker Error - Service protection activated
 * Used when circuit breaker prevents requests to failing service
 */
class CircuitBreakerError extends ForensicError {
    constructor(message, options = {}) {
        super(message, {
            statusCode: 503,
            code: 'ERR_CIRCUIT_BREAKER',
            evidence: {
                service: options.service,
                state: options.state,
                openSince: options.openSince,
                failureThreshold: options.failureThreshold,
                timeoutMs: options.timeoutMs,
                halfOpenAttempts: options.halfOpenAttempts
            },
            ...options
        });
    }
}

/**
 * Data Integrity Error - Corruption detected
 * Used when data fails integrity checks
 */
class DataIntegrityError extends ForensicError {
    constructor(message, options = {}) {
        super(message, {
            statusCode: 500,
            code: 'ERR_DATA_INTEGRITY',
            regulatoryRef: options.regulatoryRef || 'LPC_RULE_3.4.2',
            breachThreshold: true,
            evidence: {
                entityType: options.entityType,
                entityId: options.entityId,
                expectedHash: options.expectedHash,
                actualHash: options.actualHash,
                algorithm: options.algorithm,
                corruptedFields: options.corruptedFields,
                recoveryAttempted: options.recoveryAttempted,
                recoverySuccessful: options.recoverySuccessful
            },
            ...options
        });
    }
}

/**
 * Regulatory Deadline Error - Compliance deadline missed
 * Used when statutory deadlines are not met
 */
class RegulatoryDeadlineError extends ForensicError {
    constructor(message, options = {}) {
        super(message, {
            statusCode: 451,
            code: 'ERR_REGULATORY_DEADLINE',
            regulatoryRef: options.regulatoryRef,
            jurisdiction: options.jurisdiction || 'ZA',
            notifyRegulator: true,
            breachThreshold: true,
            evidence: {
                requirement: options.requirement,
                deadline: options.deadline,
                daysOverdue: options.daysOverdue,
                penaltyPerDay: options.penaltyPerDay,
                totalPenalty: options.totalPenalty,
                responsibleParty: options.responsibleParty,
                remediationPlan: options.remediationPlan,
                escalationLevel: options.escalationLevel
            },
            ...options
        });
    }
}

/**
 * Multi-Jurisdiction Error - Cross-border compliance
 * Used when operation affects multiple legal frameworks
 */
class MultiJurisdictionError extends ForensicError {
    constructor(message, options = {}) {
        super(message, {
            statusCode: 451,
            code: 'ERR_MULTI_JURISDICTION',
            regulatoryRef: options.regulatoryRef,
            jurisdiction: 'MULTI',
            notifyRegulator: true,
            evidence: {
                jurisdictions: options.jurisdictions,
                conflicts: options.conflicts,
                primaryJurisdiction: options.primaryJurisdiction,
                secondaryJurisdiction: options.secondaryJurisdiction,
                applicableTreaties: options.applicableTreaties,
                legalOpinionRequired: options.legalOpinionRequired
            },
            ...options
        });
    }
}

/**
 * Error Factory - Create errors with context propagation
 */
class ErrorFactory {
    static createValidationError(message, field, value, constraint) {
        return new ValidationError(message, { field, value, constraint });
    }

    static createComplianceError(message, rule, severity, regulatoryRef) {
        return new ComplianceError(message, { rule, severity, regulatoryRef });
    }

    static createAuthorizationError(message, requiredRoles, userRoles, userId) {
        return new AuthorizationError(message, { requiredRoles, userRoles, userId });
    }

    static createRateLimitError(message, limit, current, resetAt) {
        return new RateLimitError(message, { limit, current, resetAt });
    }

    static fromAxiosError(error, context = {}) {
        if (error.code === 'ECONNREFUSED' || error.code === 'ETIMEDOUT') {
            return new ServiceUnavailableError(error.message, {
                service: context.service,
                endpoint: context.endpoint,
                originalError: error.message
            });
        }

        if (error.response?.status === 429) {
            return new RateLimitError('Rate limit exceeded', {
                limit: error.response.headers['x-rate-limit-limit'],
                current: error.response.headers['x-rate-limit-current'],
                resetAt: error.response.headers['x-rate-limit-reset']
            });
        }

        if (error.response?.status >= 500) {
            return new RetryableError(error.message, {
                retryCount: context.retryCount,
                maxRetries: context.maxRetries,
                operation: context.operation
            });
        }

        return error;
    }
}

module.exports = {
    ForensicError,
    ValidationError,
    ComplianceError,
    AuthorizationError,
    AuthenticationError,
    NotFoundError,
    ConflictError,
    RateLimitError,
    ServiceUnavailableError,
    RetryableError,
    CircuitBreakerError,
    DataIntegrityError,
    RegulatoryDeadlineError,
    MultiJurisdictionError,
    ErrorFactory
};