/**
 * ============================================================================
 * WILSY OS - AUDIT LOG ENTERPRISE OBJECT
 * ============================================================================
 *
 * @file         AuditLogObject.js
 * @directory    server/src/enterprise/objects/
 * @system       Wilsy OS - Legal Enterprise Operating System & SaaS Platform
 * @authority    Wilson Khanyezi, Founder & Chief Architect
 * @version      1.0.0-SOVEREIGN
 * @epitome      Generation 2 Sovereign Audit Log Kernel Object implementation.
 *               Serves as the immutable forensic event logging entity in Wilsy OS.
 *               Captures user actions, security alerts, state deltas, and access
 *               trail telemetry under POPIA, LPC, and ISO/IEC 27001 standards.
 *
 * @collaboration
 * - Lead Architect: Wilson Khanyezi (Wilsy OS Architecture Core Team)
 * - Information Security: Forensics & Audit Trail Infrastructure
 * - Regulatory Compliance: POPIA Data Protection & LPC Telemetry Subsystem
 *
 * ============================================================================
 * INSTITUTIONAL AUDIT TRAIL
 * ============================================================================
 * Date       | Author          | Version | Description
 * -----------|-----------------|---------|------------------------------------
 * 2026-07-24 | Wilson Khanyezi | 1.0.0   | Production-ready Audit Log domain
 *            |                 |         | object with strict immutability,
 *            |                 |         | PII redactors, and event categorisation.
 * ============================================================================
 */

const { BaseEnterpriseObject, OBJECT_LIFECYCLE_STATES } = require('./BaseEnterpriseObject');
const { DataRedactor } = require('../kernel/EnterpriseKernel');

/**
 * Audit Event Severity Levels.
 */
const AUDIT_SEVERITY = Object.freeze({
  INFO: 'INFO',
  WARNING: 'WARNING',
  SECURITY_ALERT: 'SECURITY_ALERT',
  COMPLIANCE_BREACH: 'COMPLIANCE_BREACH'
});

/**
 * Standard Audit Action Verbs.
 */
const AUDIT_ACTION = Object.freeze({
  CREATE: 'CREATE',
  READ: 'READ',
  UPDATE: 'UPDATE',
  DELETE: 'DELETE',
  EXECUTE: 'EXECUTE',
  DECRYPT: 'DECRYPT',
  LOGIN_SUCCESS: 'LOGIN_SUCCESS',
  LOGIN_FAILURE: 'LOGIN_FAILURE',
  EXCEED_PRIVILEGE: 'EXCEED_PRIVILEGE'
});

/**
 * Custom Error Class for Audit Log Domain Faults.
 */
class AuditLogObjectError extends Error {
  /**
   * @param {string} message - Error details.
   * @param {string} [code='AUDIT_ERR_GENERIC'] - Standard error code.
   * @param {Object} [details={}] - Additional contextual metadata.
   */
  constructor(message, code = 'AUDIT_ERR_GENERIC', details = {}) {
    super(message);
    this.name = 'AuditLogObjectError';
    this.code = code;
    this.timestamp = new Date().toISOString();
    this.details = DataRedactor.sanitize(details);
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, AuditLogObjectError);
    }
  }
}

/**
 * Sovereign Audit Log Domain Object.
 * Encapsulates security telemetry, state diffs, user action lineage, and regulatory
 * audit points in Wilsy OS. Enforces strict write-once immutability.
 */
class AuditLogObject extends BaseEnterpriseObject {
  /**
   * Constructs an AuditLogObject.
   *
   * @param {Object} params
   * @param {string} params.id - Unique Audit Log Identifier (e.g. 'AUD-2026-9901').
   * @param {string} params.tenantId - Sovereign Tenant ID.
   * @param {string} params.actorId - Operator or Service Account ID executing action.
   * @param {string} [params.action='READ'] - Audit action constant.
   * @param {string} params.targetEntityDomain - Domain of object acted upon (e.g. 'CUSTOMER', 'INVOICE').
   * @param {string} params.targetEntityId - Specific ID of object acted upon.
   * @param {string} [params.severity='INFO'] - Event severity classification.
   * @param {string} [params.ipAddress=null] - Network IP address of actor.
   * @param {string} [params.userAgent=null] - User Agent browser string or SDK identifier.
   * @param {Object} [params.previousState=null] - Pre-action object snapshot (redacted).
   * @param {Object} [params.newState=null] - Post-action object snapshot (redacted).
   * @param {Object} [params.metadata={}] - Additional operational metadata.
   */
  constructor({
    id,
    tenantId,
    actorId,
    action = AUDIT_ACTION.READ,
    targetEntityDomain,
    targetEntityId,
    severity = AUDIT_SEVERITY.INFO,
    ipAddress = null,
    userAgent = null,
    previousState = null,
    newState = null,
    metadata = {}
  }) {
    if (!actorId || typeof actorId !== 'string') {
      throw new AuditLogObjectError('Actor ID executing action is required', 'AUDIT_ERR_INVALID_ACTOR');
    }

    if (!targetEntityDomain || typeof targetEntityDomain !== 'string') {
      throw new AuditLogObjectError('Target entity domain is required', 'AUDIT_ERR_INVALID_TARGET_DOMAIN');
    }

    if (!targetEntityId || typeof targetEntityId !== 'string') {
      throw new AuditLogObjectError('Target entity ID is required', 'AUDIT_ERR_INVALID_TARGET_ID');
    }

    const normAction = action.trim().toUpperCase();
    if (!Object.values(AUDIT_ACTION).includes(normAction)) {
      throw new AuditLogObjectError(`Invalid audit action [${action}]`, 'AUDIT_ERR_INVALID_ACTION');
    }

    const normSeverity = severity.trim().toUpperCase();
    if (!Object.values(AUDIT_SEVERITY).includes(normSeverity)) {
      throw new AuditLogObjectError(`Invalid audit severity level [${severity}]`, 'AUDIT_ERR_INVALID_SEVERITY');
    }

    const initialAttributes = {
      actorId: actorId.trim(),
      action: normAction,
      targetEntityDomain: targetEntityDomain.trim().toUpperCase(),
      targetEntityId: targetEntityId.trim(),
      severity: normSeverity,
      ipAddress: ipAddress ? ipAddress.trim() : null,
      userAgent: userAgent ? userAgent.trim() : null,
      previousState: previousState ? DataRedactor.sanitize(previousState) : null,
      newState: newState ? DataRedactor.sanitize(newState) : null,
      metadata: DataRedactor.sanitize(metadata),
      loggedAt: new Date().toISOString()
    };

    super({
      id,
      tenantId,
      domain: 'AUDIT_LOG',
      attributes: initialAttributes,
      schemaVersion: '1.0.0',
      status: OBJECT_LIFECYCLE_STATES.ACTIVE,
      createdById: actorId
    });
  }

  /**
   * Overrides updateAttributes to strictly enforce write-once immutability for audit records.
   *
   * @throws {AuditLogObjectError} Always throws error as audit logs cannot be modified.
   */
  updateAttributes() {
    throw new AuditLogObjectError(
      'Audit log entries are cryptographically sealed and immutable. Revisions are prohibited by system policy.',
      'AUDIT_ERR_IMMUTABLE_RECORD'
    );
  }

  /**
   * Convenience getter for Action.
   * @returns {string}
   */
  get action() {
    return this.attributes.action;
  }

  /**
   * Convenience getter for Target Domain.
   * @returns {string}
   */
  get targetEntityDomain() {
    return this.attributes.targetEntityDomain;
  }

  /**
   * Convenience getter for Severity.
   * @returns {string}
   */
  get severity() {
    return this.attributes.severity;
  }

  /**
   * Generates a scrubbed overview of audit log entry for security dashboards.
   * @returns {Object}
   */
  getSanitizedSummary() {
    return {
      auditLogId: this.id,
      tenantId: this.tenantId,
      actorId: this.attributes.actorId,
      action: this.attributes.action,
      targetEntityDomain: this.attributes.targetEntityDomain,
      targetEntityId: this.attributes.targetEntityId,
      severity: this.attributes.severity,
      ipAddress: this.attributes.ipAddress,
      loggedAt: this.attributes.loggedAt
    };
  }
}

module.exports = {
  AuditLogObject,
  AuditLogObjectError,
  AUDIT_SEVERITY,
  AUDIT_ACTION
};
