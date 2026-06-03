/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - FORENSIC ERROR NUCLEUS [V1.1.0-SINGULARITY]                                                                                 ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

export class WilsyBaseError extends Error {
  constructor(message, options = {}) {
    super(message);
    this.options = options;
    this.code = options.code || 'ERR_WILSY_INTERNAL';
    this.status = options.status || 500;
  }
}

export class ValidationError extends WilsyBaseError { constructor(m, o) { super(m, { ...o, status: 400 }); } }
export class ComplianceError extends WilsyBaseError { constructor(m, o) { super(m, { ...o, status: 403 }); } }
export class RegulatoryDeadlineError extends WilsyBaseError { constructor(m, o) { super(m, { ...o, status: 403 }); } }
export class AuthorizationError extends WilsyBaseError { constructor(m, o) { super(m, { ...o, status: 403 }); } }
export class NotFoundError extends WilsyBaseError { constructor(m, o) { super(m, { ...o, status: 404 }); } }
export class DataIntegrityError extends WilsyBaseError { constructor(m, o) { super(m, { ...o, status: 500 }); } }
export class CircuitBreakerError extends WilsyBaseError { constructor(m, o) { super(m, { ...o, status: 503 }); } }
export class RetryableError extends WilsyBaseError { constructor(m, o) { super(m, { ...o, status: 503 }); } }
export class ServiceUnavailableError extends WilsyBaseError { constructor(m, o) { super(m, { ...o, status: 503 }); } }
export class ConflictError extends WilsyBaseError { constructor(m, o) { super(m, { ...o, status: 409 }); } }
export class AuthenticationError extends WilsyBaseError { constructor(m, o) { super(m, { ...o, status: 401 }); } }
export class RateLimitError extends WilsyBaseError { constructor(m, o) { super(m, { ...o, status: 429 }); } }
export class LPCComplianceError extends ComplianceError {}
export class FICAComplianceError extends ComplianceError {}
export class GDPRComplianceError extends ComplianceError {}
export class POPIAComplianceError extends ComplianceError {}
export class MultiJurisdictionError extends ComplianceError {}
export class BlockchainAnchorError extends WilsyBaseError {}
export class QuantumSecurityError extends WilsyBaseError {}
