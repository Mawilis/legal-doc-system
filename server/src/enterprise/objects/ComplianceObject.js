/**
 * ============================================================================
 * WILSY OS - COMPLIANCE ENTERPRISE OBJECT
 * ============================================================================
 *
 * @file         ComplianceObject.js
 * @directory    server/src/enterprise/objects/
 * @system       Wilsy OS - Legal Enterprise Operating System & SaaS Platform
 * @authority    Wilson Khanyezi, Founder & Chief Architect
 * @version      1.0.0-SOVEREIGN
 * @epitome      Generation 2 Sovereign Compliance Kernel Object implementation.
 *               Provides statutory regulatory auditing, legal framework tracking
 *               (POPIA, GDPR, FICA, LSSA, Companies Act), compliance evaluation
 *               lifecycle management, non-compliance remediations, and institutional
 *               audit logging.
 *
 * @collaboration
 * - Lead Architect: Wilson Khanyezi (Wilsy OS Architecture Core Team)
 * - Regulatory Affairs: Sovereign Legal & Statutory Compliance Subsystem
 * - Data Governance: Information Regulator & Privacy Enforcement Engine
 *
 * ============================================================================
 * INSTITUTIONAL AUDIT TRAIL
 * ============================================================================
 * Date       | Author          | Version | Description
 * -----------|-----------------|---------|------------------------------------
 * 2026-07-24 | Wilson Khanyezi | 1.0.0   | Production-ready Compliance object
 *            |                 |         | with statutory audit controls, FICA/POPIA
 *            |                 |         | state tracking, and remediation logs.
 * ============================================================================
 */

const { BaseEnterpriseObject, OBJECT_LIFECYCLE_STATES } = require('./BaseEnterpriseObject');
const { DataRedactor } = require('../kernel/EnterpriseKernel');

/**
 * Recognized Sovereign Statutory & Industry Frameworks.
 */
const COMPLIANCE_FRAMEWORKS = Object.freeze({
  POPIA: 'POPIA',             // Protection of Personal Information Act (South Africa)
  GDPR: 'GDPR',               // General Data Protection Regulation (EU)
  FICA: 'FICA',               // Financial Intelligence Centre Act (AML/KYC)
  LSSA: 'LSSA',               // Law Society of South Africa Practice Guidelines
  COMPANIES_ACT: 'COMPANIES_ACT', // Companies Act 71 of 2008
  ISO27001: 'ISO27001'         // Information Security Management Standard
});

/**
 * Compliance Lifecycle Evaluation States.
 */
const COMPLIANCE_STATUS = Object.freeze({
  PENDING_REVIEW: 'PENDING_REVIEW',
  COMPLIANT: 'COMPLIANT',
  NON_COMPLIANT: 'NON_COMPLIANT',
  ACTION_REQUIRED: 'ACTION_REQUIRED',
  EXEMPT: 'EXEMPT'
});

/**
 * Custom Error Class for Compliance Domain Violations.
 */
class ComplianceObjectError extends Error {
  /**
   * @param {string} message - Error details.
   * @param {string} [code='COMPLIANCE_ERR_GENERIC'] - Standard error code.
   * @param {Object} [details={}] - Additional contextual metadata.
   */
  constructor(message, code = 'COMPLIANCE_ERR_GENERIC', details = {}) {
    super(message);
    this.name = 'ComplianceObjectError';
    this.code = code;
    this.timestamp = new Date().toISOString();
    this.details = DataRedactor.sanitize(details);
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, ComplianceObjectError);
    }
  }
}

/**
 * Sovereign Compliance Domain Object.
 * Encapsulates regulatory checks, statutory audit trails, risk remediation steps,
 * and data privacy enforcement records across legal matters in Wilsy OS.
 */
class ComplianceObject extends BaseEnterpriseObject {
  /**
   * Constructs a ComplianceObject.
   *
   * @param {Object} params
   * @param {string} params.id - Unique Compliance Identifier (e.g. 'CMP-2026-0104').
   * @param {string} params.tenantId - Sovereign Tenant ID.
   * @param {string} [params.framework='POPIA'] - Regulatory framework constant.
   * @param {string} params.regulationSection - Statutory clause or section (e.g. 'POPIA-SEC-19').
   * @param {string} params.title - Scope or requirement summary.
   * @param {string} [params.description=''] - Detailed regulatory mandate explanation.
   * @param {string} [params.assignedAuditorId='UNASSIGNED'] - ID of assigned compliance auditor.
   * @param {string} [params.dueDate] - Targeted compliance completion date (ISO string).
   * @param {string} [params.createdById='SYSTEM'] - Identity generating record.
   */
  constructor({
    id,
    tenantId,
    framework = COMPLIANCE_FRAMEWORKS.POPIA,
    regulationSection,
    title,
    description = '',
    assignedAuditorId = 'UNASSIGNED',
    dueDate = null,
    createdById = 'SYSTEM'
  }) {
    if (!title || typeof title !== 'string' || title.trim().length === 0) {
      throw new ComplianceObjectError('Compliance title must be a non-empty string', 'CMP_ERR_INVALID_TITLE');
    }

    if (!regulationSection || typeof regulationSection !== 'string' || regulationSection.trim().length === 0) {
      throw new ComplianceObjectError('Statutory regulation section standard is required', 'CMP_ERR_INVALID_SECTION');
    }

    const normFramework = framework.trim().toUpperCase();
    if (!Object.values(COMPLIANCE_FRAMEWORKS).includes(normFramework)) {
      throw new ComplianceObjectError(`Unsupported regulatory framework [${framework}]`, 'CMP_ERR_INVALID_FRAMEWORK');
    }

    let parsedDueDate = null;
    if (dueDate) {
      const d = new Date(dueDate);
      if (isNaN(d.getTime())) {
        throw new ComplianceObjectError('Due date must be a valid ISO date string', 'CMP_ERR_INVALID_DUE_DATE');
      }
      parsedDueDate = d.toISOString();
    }

    const initialAttributes = {
      framework: normFramework,
      regulationSection: regulationSection.trim().toUpperCase(),
      title: title.trim(),
      description: description.trim(),
      complianceStatus: COMPLIANCE_STATUS.PENDING_REVIEW,
      assignedAuditorId: assignedAuditorId.trim(),
      dueDate: parsedDueDate,
      findings: '',
      remediationPlan: '',
      auditHistory: []
    };

    super({
      id,
      tenantId,
      domain: 'COMPLIANCE',
      attributes: initialAttributes,
      schemaVersion: '1.0.0',
      status: OBJECT_LIFECYCLE_STATES.ACTIVE,
      createdById
    });
  }

  /**
   * Records statutory audit result and sets compliance status.
   *
   * @param {Object} auditData
   * @param {string} auditData.status - Target status (COMPLIANT, NON_COMPLIANT, etc.).
   * @param {string} [auditData.findings=''] - Legal compliance officer findings.
   * @param {string} [auditData.remediationPlan=''] - Mandatory action steps if non-compliant.
   * @param {string} operatorId - Identity of performing compliance officer.
   * @returns {Object} Revision state.
   */
  recordAuditResult({ status, findings = '', remediationPlan = '' }, operatorId = 'SYSTEM') {
    if (!status || !Object.values(COMPLIANCE_STATUS).includes(status.trim().toUpperCase())) {
      throw new ComplianceObjectError(`Invalid compliance status [${status}]`, 'CMP_ERR_INVALID_STATUS');
    }

    const normStatus = status.trim().toUpperCase();
    const cleanFindings = findings ? findings.trim() : '';
    const cleanRemediation = remediationPlan ? remediationPlan.trim() : '';

    if (normStatus === COMPLIANCE_STATUS.NON_COMPLIANT && cleanRemediation.length === 0) {
      throw new ComplianceObjectError('Remediation plan is required when recording NON_COMPLIANT status', 'CMP_ERR_REMEDIATION_REQUIRED');
    }

    const auditEntry = {
      timestamp: new Date().toISOString(),
      auditorId: operatorId,
      previousStatus: this.attributes.complianceStatus,
      newStatus: normStatus,
      findings: cleanFindings,
      remediationPlan: cleanRemediation
    };

    const updatedHistory = [...(this.attributes.auditHistory || []), auditEntry];

    return this.updateAttributes(
      {
        complianceStatus: normStatus,
        findings: cleanFindings,
        remediationPlan: cleanRemediation,
        auditHistory: updatedHistory
      },
      operatorId
    );
  }

  /**
   * Reassigns compliance audit custodian.
   *
   * @param {string} newAuditorId - User ID of legal compliance officer.
   * @param {string} operatorId - Authorizing manager.
   * @returns {Object} Update execution result.
   */
  assignAuditor(newAuditorId, operatorId = 'SYSTEM') {
    if (!newAuditorId || typeof newAuditorId !== 'string') {
      throw new ComplianceObjectError('Valid auditor identity required', 'CMP_ERR_INVALID_AUDITOR');
    }

    return this.updateAttributes({ assignedAuditorId: newAuditorId.trim() }, operatorId);
  }

  /**
   * Updates or extends compliance review deadline.
   *
   * @param {string|Date} newDueDate - ISO date string or Date instance.
   * @param {string} operatorId - Identity extending deadline.
   * @returns {Object} Update execution result.
   */
  extendDueDate(newDueDate, operatorId = 'SYSTEM') {
    const d = new Date(newDueDate);
    if (isNaN(d.getTime())) {
      throw new ComplianceObjectError('Invalid date provided for due date extension', 'CMP_ERR_INVALID_DUE_DATE');
    }

    return this.updateAttributes({ dueDate: d.toISOString() }, operatorId);
  }

  /**
   * Convenience getter for framework type.
   * @returns {string}
   */
  get framework() {
    return this.attributes.framework;
  }

  /**
   * Convenience getter for current compliance status.
   * @returns {string}
   */
  get complianceStatus() {
    return this.attributes.complianceStatus;
  }

  /**
   * Generates a scrubbed summary suitable for regulatory audit reports.
   * @returns {Object}
   */
  getSanitizedSummary() {
    return {
      complianceId: this.id,
      tenantId: this.tenantId,
      framework: this.attributes.framework,
      regulationSection: this.attributes.regulationSection,
      title: this.attributes.title,
      complianceStatus: this.attributes.complianceStatus,
      assignedAuditorId: this.attributes.assignedAuditorId,
      dueDate: this.attributes.dueDate,
      hasRemediationPlan: Boolean(this.attributes.remediationPlan),
      auditCount: (this.attributes.auditHistory || []).length,
      status: this.status,
      revisionNumber: this.revisionNumber,
      updatedAt: this.updatedAt
    };
  }
}

module.exports = {
  ComplianceObject,
  ComplianceObjectError,
  COMPLIANCE_FRAMEWORKS,
  COMPLIANCE_STATUS
};
