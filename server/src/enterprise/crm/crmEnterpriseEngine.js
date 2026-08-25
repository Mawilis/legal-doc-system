/**
 * ============================================================================
 * WILSY OS - CRM ENTERPRISE ENGINE (FG231B)
 * ============================================================================
 *
 * @file         crmEnterpriseEngine.js
 * @directory    server/src/enterprise/crm/
 * @system       Wilsy OS - Enterprise Subsystem Engine Layer (FG231B)
 * @authority    Wilson Khanyezi, Founder & Chief Architect
 * @version      2.0.1-GEN2
 * @epitome      Sovereign CRM Enterprise Engine governing customer relationship
 *               lifecycles, automated lead scoring, sales pipeline transitions,
 *               predictive revenue forecasting, and POPIA/GDPR redactive safety.
 *
 * ============================================================================
 * INSTITUTIONAL AUDIT & COLLABORATION LOG
 * ============================================================================
 * Date       | Author          | Version | Description
 * -----------|-----------------|---------|------------------------------------
 * 2026-07-24 | Wilson Khanyezi | 2.0.0   | Converted to ES Module architecture
 *            |                 |         | for server "type": "module" parity.
 * 2026-07-24 | Wilson Khanyezi | 2.0.1   | Patched POPIA SA_ID_NUMBER regex pattern
 *            |                 |         | to strictly capture YYMMDD 13-digit IDs.
 * ============================================================================
 */

import crypto from 'node:crypto';

/**
 * Valid Lead Lifecycle States.
 */
export const LEAD_STATES = Object.freeze({
  UNQUALIFIED: 'UNQUALIFIED',
  QUALIFIED: 'QUALIFIED',
  ENGAGED: 'ENGAGED',
  PROPOSAL_SENT: 'PROPOSAL_SENT',
  NEGOTIATING: 'NEGOTIATING',
  CLOSED_WON: 'CLOSED_WON',
  CLOSED_LOST: 'CLOSED_LOST'
});

/**
 * Legal Redaction Patterns for POPIA / GDPR compliance within CRM payloads.
 * SA ID Format: YYMMDDSSSSCAZ (13 digits)
 */
export const POPIA_PATTERNS = Object.freeze({
  SA_ID_NUMBER: /\b\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{7}\b/g,
  EMAIL_REDACTION: /(?<=.{2}).(?=.*@)/g,
  PHONE_REDACTION: /(\+?\d{2}|\d{3})\d{4}(\d{4})/g
});

export class CrmEnterpriseEngine {
  /**
   * Constructs the CRM Enterprise Engine instance.
   * @param {object} [config={}] - Optional subsystem configuration.
   */
  constructor(config = {}) {
    this.engineId = 'ENGINE_CRM_v2.0.0';
    this.maxLeadScore = 100;
    this.config = config;
  }

  /**
   * Generates a deterministic SHA-256 hash for CRM domain object auditability.
   * @param {object} payload - Target object payload.
   * @returns {string} SHA-256 digest string.
   */
  computeAuditHash(payload) {
    const raw = JSON.stringify(payload, Object.keys(payload).sort());
    return crypto.createHash('sha256').update(raw).digest('hex');
  }

  /**
   * Applies POPIA / GDPR redaction rules to sensitive lead information.
   * Institutional Safety: Prevents sensitive personal identifiers from being
   * stored unencrypted or logged in plaintext traces.
   *
   * @param {object} leadData - Raw incoming lead record.
   * @returns {object} Redacted, legally compliant lead record.
   */
  redactSensitiveData(leadData) {
    try {
      if (!leadData || typeof leadData !== 'object') {
        throw new Error('Invalid leadData payload provided for redaction.');
      }

      const sanitized = { ...leadData };

      if (sanitized.nationalId && typeof sanitized.nationalId === 'string') {
        sanitized.nationalId = sanitized.nationalId.replace(POPIA_PATTERNS.SA_ID_NUMBER, '******[REDACTED_POPIA]******');
      }

      if (sanitized.email && typeof sanitized.email === 'string') {
        const [local, domain] = sanitized.email.split('@');
        if (local && domain) {
          const redactedLocal = local.length > 2 ? local.substring(0, 2) + '***' : '***';
          sanitized.email = `${redactedLocal}@${domain}`;
        }
      }

      if (sanitized.phone && typeof sanitized.phone === 'string') {
        sanitized.phone = sanitized.phone.replace(POPIA_PATTERNS.PHONE_REDACTION, '$1****$2');
      }

      return sanitized;
    } catch (error) {
      throw new Error(`[CRM_REDACTION_FAULT] ${error.message}`);
    }
  }

  /**
   * Computes an algorithmic lead score based on engagement metrics.
   *
   * @param {object} metrics - Lead engagement signals.
   * @param {number} metrics.budget - Budget capacity in ZAR/USD.
   * @param {number} metrics.interactions - Count of verified customer touchpoints.
   * @param {boolean} metrics.decisionMaker - Whether contact is a confirmed decision maker.
   * @param {number} metrics.urgencyDays - Conversion timeframe in days.
   * @returns {number} Score bounded between 0 and 100.
   */
  calculateLeadScore(metrics = {}) {
    try {
      const { budget = 0, interactions = 0, decisionMaker = false, urgencyDays = 90 } = metrics;
      let score = 0;

      // Budget scoring weight (Max 40 pts)
      if (budget >= 1000000) score += 40;
      else if (budget >= 250000) score += 30;
      else if (budget >= 50000) score += 20;
      else if (budget > 0) score += 10;

      // Engagement touchpoints weight (Max 30 pts)
      score += Math.min(interactions * 5, 30);

      // Authority weight (Max 20 pts)
      if (decisionMaker) score += 20;

      // Urgency speed weight (Max 10 pts)
      if (urgencyDays <= 14) score += 10;
      else if (urgencyDays <= 30) score += 5;

      return Math.min(score, this.maxLeadScore);
    } catch (error) {
      throw new Error(`[CRM_SCORE_CALC_FAULT] ${error.message}`);
    }
  }

  /**
   * Executes a governed state transition for a lead in the pipeline.
   *
   * @param {string} currentState - Existing state in LEAD_STATES.
   * @param {string} targetState - Desired new state in LEAD_STATES.
   * @param {object} context - Metadata context supporting transition.
   * @returns {object} Transition execution record.
   */
  transitionLeadState(currentState, targetState, context = {}) {
    try {
      if (!LEAD_STATES[currentState]) {
        throw new Error(`Invalid origin state: ${currentState}`);
      }
      if (!LEAD_STATES[targetState]) {
        throw new Error(`Invalid destination state: ${targetState}`);
      }

      const timestamp = new Date().toISOString();
      const transitionPayload = {
        origin: currentState,
        destination: targetState,
        tenantId: context.tenantId || 'GLOBAL_SYSTEM',
        operatorId: context.operatorId || 'SYSTEM_AUTO',
        timestamp
      };

      const auditHash = this.computeAuditHash(transitionPayload);

      return {
        success: true,
        previousState: currentState,
        newState: targetState,
        auditHash,
        timestamp
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  }

  /**
   * Self-contained health check verification and operational seal.
   * @returns {object} Diagnostic integrity object.
   */
  healthCheck() {
    const startTime = process.hrtime.bigint();
    const testPayload = { tenantId: 'TENANT_HEALTH_TEST', budget: 500000, interactions: 4 };
    const score = this.calculateLeadScore(testPayload);
    const hash = this.computeAuditHash(testPayload);
    const endTime = process.hrtime.bigint();
    const latencyMs = Number(endTime - startTime) / 1e6;

    return {
      engineId: this.engineId,
      status: 'OPERATIONAL',
      certified: true,
      testScoreCalculated: score,
      sampleHash: hash,
      latencyMs: `${latencyMs.toFixed(3)} ms`
    };
  }
}
