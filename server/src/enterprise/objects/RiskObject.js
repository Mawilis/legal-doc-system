/**
 * ============================================================================
 * WILSY OS - RISK ENTERPRISE OBJECT
 * ============================================================================
 *
 * @file         RiskObject.js
 * @directory    server/src/enterprise/objects/
 * @system       Wilsy OS - Legal Enterprise Operating System & SaaS Platform
 * @authority    Wilson Khanyezi, Founder & Chief Architect
 * @version      1.0.0-SOVEREIGN
 * @epitome      Generation 2 Sovereign Risk Kernel Object implementation.
 *               Provides quantitative legal, financial, operational, and regulatory
 *               risk matrix scoring, threat probability evaluations, automated mitigation
 *               plan tracking, and POPIA/GDPR compliance risk auditing.
 *
 * @collaboration
 * - Lead Architect: Wilson Khanyezi (Wilsy OS Architecture Core Team)
 * - Risk & Governance: GRC (Governance, Risk, & Compliance) Engine Core
 * - Legal Audit: Sovereign Regulatory Exposure Analytics & Assessment
 *
 * ============================================================================
 * INSTITUTIONAL AUDIT TRAIL
 * ============================================================================
 * Date       | Author          | Version | Description
 * -----------|-----------------|---------|------------------------------------
 * 2026-07-24 | Wilson Khanyezi | 1.0.0   | Production-ready Risk domain object
 *            |                 |         | with quantitative risk scoring,
 *            |                 |         | probability vectors, and mitigation logs.
 * ============================================================================
 */

const { BaseEnterpriseObject, OBJECT_LIFECYCLE_STATES } = require('./BaseEnterpriseObject');
const { DataRedactor } = require('../kernel/EnterpriseKernel');

/**
 * Standard Risk Severity Levels.
 */
const RISK_SEVERITY = Object.freeze({
  LOW: 'LOW',
  MEDIUM: 'MEDIUM',
  HIGH: 'HIGH',
  CRITICAL: 'CRITICAL'
});

/**
 * Standard Enterprise Risk Categories.
 */
const RISK_CATEGORIES = Object.freeze({
  LEGAL_LITIGATION: 'LEGAL_LITIGATION',
  REGULATORY_COMPLIANCE: 'REGULATORY_COMPLIANCE',
  FINANCIAL_EXPOSURE: 'FINANCIAL_EXPOSURE',
  OPERATIONAL_DISRUPTION: 'OPERATIONAL_DISRUPTION',
  CYBER_DATA_PRIVACY: 'CYBER_DATA_PRIVACY'
});

/**
 * Custom Error Class for Risk Domain Violations.
 */
class RiskObjectError extends Error {
  /**
   * @param {string} message - Error details.
   * @param {string} [code='RISK_ERR_GENERIC'] - Standard error code.
   * @param {Object} [details={}] - Additional contextual metadata.
   */
  constructor(message, code = 'RISK_ERR_GENERIC', details = {}) {
    super(message);
    this.name = 'RiskObjectError';
    this.code = code;
    this.timestamp = new Date().toISOString();
    this.details = DataRedactor.sanitize(details);
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, RiskObjectError);
    }
  }
}

/**
 * Sovereign Risk Domain Object.
 * Encapsulates exposure assessments, probability matrices, risk mitigation status,
 * and regulatory compliance risks across enterprise matters inside Wilsy OS.
 */
class RiskObject extends BaseEnterpriseObject {
  /**
   * Constructs a RiskObject.
   *
   * @param {Object} params
   * @param {string} params.id - Unique Risk Identifier (e.g. 'RSK-2026-0019').
   * @param {string} params.tenantId - Sovereign Tenant ID.
   * @param {string} params.title - Title or concise threat summary.
   * @param {string} [params.category='REGULATORY_COMPLIANCE'] - Category of risk vector.
   * @param {string} [params.severity='MEDIUM'] - Severity level (LOW, MEDIUM, HIGH, CRITICAL).
   * @param {number} [params.probability=0.5] - Calculated likelihood of occurrence (0.00 to 1.00).
   * @param {string} [params.mitigationPlan=''] - Documented mitigation strategy.
   * @param {string} [params.assignedToId='UNASSIGNED'] - ID of Risk/Compliance owner.
   * @param {string} [params.createdById='SYSTEM'] - Operator creating entry.
   */
  constructor({
    id,
    tenantId,
    title,
    category = RISK_CATEGORIES.REGULATORY_COMPLIANCE,
    severity = RISK_SEVERITY.MEDIUM,
    probability = 0.5,
    mitigationPlan = '',
    assignedToId = 'UNASSIGNED',
    createdById = 'SYSTEM'
  }) {
    if (!title || typeof title !== 'string' || title.trim().length === 0) {
      throw new RiskObjectError('Risk title must be a non-empty string', 'RSK_ERR_INVALID_TITLE');
    }

    const prob = Number(probability);
    if (isNaN(prob) || prob < 0 || prob > 1) {
      throw new RiskObjectError('Risk probability must be a decimal between 0.0 and 1.0', 'RSK_ERR_INVALID_PROBABILITY');
    }

    const normalizedSeverity = severity.trim().toUpperCase();
    if (!Object.values(RISK_SEVERITY).includes(normalizedSeverity)) {
      throw new RiskObjectError(`Invalid risk severity level [${severity}]`, 'RSK_ERR_INVALID_SEVERITY');
    }

    const initialAttributes = {
      title: title.trim(),
      category: category.trim().toUpperCase(),
      severity: normalizedSeverity,
      probability: Number(prob.toFixed(4)),
      riskScore: RiskObject.calculateScore(normalizedSeverity, prob),
      mitigationPlan: mitigationPlan.trim(),
      assignedToId: assignedToId.trim(),
      isMitigated: false,
      lastReviewedAt: new Date().toISOString()
    };

    super({
      id,
      tenantId,
      domain: 'RISK',
      attributes: initialAttributes,
      schemaVersion: '1.0.0',
      status: OBJECT_LIFECYCLE_STATES.ACTIVE,
      createdById
    });
  }

  /**
   * Quantitative algorithm mapping severity weights and probability to a normalized risk score (1 - 100).
   *
   * @param {string} severity - Severity level constant.
   * @param {number} probability - Likelihood scalar (0.0 - 1.0).
   * @returns {number} Score from 1 to 100.
   */
  static calculateScore(severity, probability) {
    const severityMultiplierMap = {
      [RISK_SEVERITY.LOW]: 25,
      [RISK_SEVERITY.MEDIUM]: 50,
      [RISK_SEVERITY.HIGH]: 75,
      [RISK_SEVERITY.CRITICAL]: 100
    };

    const multiplier = severityMultiplierMap[severity] || 50;
    return Number((multiplier * probability).toFixed(2));
  }

  /**
   * Re-evaluates risk matrix inputs (severity and probability).
   *
   * @param {Object} evalData
   * @param {string} [evalData.severity] - Updated severity constant.
   * @param {number} [evalData.probability] - Updated probability (0.0 to 1.0).
   * @param {string} operatorId - Risk Assessor identity.
   * @returns {Object} Update execution result.
   */
  reevaluateRisk({ severity, probability }, operatorId = 'SYSTEM') {
    const patch = {
      lastReviewedAt: new Date().toISOString()
    };

    let targetSeverity = this.attributes.severity;
    let targetProbability = this.attributes.probability;

    if (severity && typeof severity === 'string') {
      const normSev = severity.trim().toUpperCase();
      if (!Object.values(RISK_SEVERITY).includes(normSev)) {
        throw new RiskObjectError(`Invalid severity level [${severity}]`, 'RSK_ERR_INVALID_SEVERITY');
      }
      targetSeverity = normSev;
      patch.severity = targetSeverity;
    }

    if (probability !== undefined) {
      const prob = Number(probability);
      if (isNaN(prob) || prob < 0 || prob > 1) {
        throw new RiskObjectError('Probability must be between 0.0 and 1.0', 'RSK_ERR_INVALID_PROBABILITY');
      }
      targetProbability = Number(prob.toFixed(4));
      patch.probability = targetProbability;
    }

    patch.riskScore = RiskObject.calculateScore(targetSeverity, targetProbability);

    return this.updateAttributes(patch, operatorId);
  }

  /**
   * Updates or replaces the active mitigation strategy plan.
   *
   * @param {string} newPlanText - Clear description of action steps taken to neutralize risk.
   * @param {boolean} [isMitigated=false] - Flag if risk vector is fully controlled.
   * @param {string} operatorId - User recording mitigation.
   * @returns {Object} Revision metadata.
   */
  updateMitigationPlan(newPlanText, isMitigated = false, operatorId = 'SYSTEM') {
    if (!newPlanText || typeof newPlanText !== 'string' || newPlanText.trim().length === 0) {
      throw new RiskObjectError('Mitigation plan text cannot be empty', 'RSK_ERR_INVALID_PLAN');
    }

    const patch = {
      mitigationPlan: newPlanText.trim(),
      isMitigated: Boolean(isMitigated),
      lastReviewedAt: new Date().toISOString()
    };

    return this.updateAttributes(patch, operatorId);
  }

  /**
   * Reassigns ownership of risk control item to another compliance officer.
   *
   * @param {string} newOwnerId - User ID of new risk custodian.
   * @param {string} operatorId - Manager performing reassignment.
   * @returns {Object} Update result.
   */
  assignOwner(newOwnerId, operatorId = 'SYSTEM') {
    if (!newOwnerId || typeof newOwnerId !== 'string') {
      throw new RiskObjectError('Valid owner ID required', 'RSK_ERR_INVALID_OWNER');
    }

    return this.updateAttributes({ assignedToId: newOwnerId.trim() }, operatorId);
  }

  /**
   * Convenience getter for Risk Score.
   * @returns {number}
   */
  get riskScore() {
    return this.attributes.riskScore;
  }

  /**
   * Generates a scrubbed summary suitable for executive risk dashboards.
   * @returns {Object}
   */
  getSanitizedSummary() {
    return {
      riskId: this.id,
      tenantId: this.tenantId,
      title: this.attributes.title,
      category: this.attributes.category,
      severity: this.attributes.severity,
      probability: this.attributes.probability,
      riskScore: this.attributes.riskScore,
      isMitigated: this.attributes.isMitigated,
      assignedToId: this.attributes.assignedToId,
      status: this.status,
      lastReviewedAt: this.attributes.lastReviewedAt,
      revisionNumber: this.revisionNumber,
      updatedAt: this.updatedAt
    };
  }
}

module.exports = {
  RiskObject,
  RiskObjectError,
  RISK_SEVERITY,
  RISK_CATEGORIES
};
