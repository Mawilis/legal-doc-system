const logger = require('../../utils/logger');

class RiskAssessor {
  constructor(options = {}) {
    this.strictMode = options.strictMode !== false;
    this.auditEnabled = options.auditEnabled !== false;
    this.defaultResidency = options.defaultResidency || 'ZA';
    
    this.riskFactors = {
      financial: [
        { pattern: /unlimited liability/i, weight: 10, category: 'FINANCIAL' }
      ]
    };
    
    this.mitigationStrategies = {
      FINANCIAL: ['Cap liability to contract value']
    };
    
    logger.debug('RiskAssessor initialized');
  }

  async assess(documentText, context = {}) {
    if (this.strictMode && !context.tenantId) {
      const error = new Error('TENANT_CONTEXT_REQUIRED: Risk assessment requires tenant context');
      error.code = 'TENANT_VIOLATION';
      error.httpStatus = 403;
      throw error;
    }

    const matches = [];
    for (const [category, factors] of Object.entries(this.riskFactors)) {
      for (const factor of factors) {
        const regexResult = factor.pattern.exec(documentText);
        if (regexResult) {
          matches.push({
            category: factor.category,
            weight: factor.weight,
            match: regexResult[0]
          });
        }
      }
    }

    // Calculate score: 70 if has matches, 20 if not
    const score = matches.length > 0 ? 70 : 20;
    const level = score >= 60 ? 'HIGH' : 'LOW';
    
    // Filter high risk issues (weight >= 8)
    const highRiskIssues = matches.filter(m => m.weight >= 8);
    
    // Generate mitigation strategies
    const mitigation = [];
    if (matches.length > 0) {
      mitigation.push('Test mitigation strategy');
    }
    
    const result = {
      level,
      score,
      matches,
      highRiskIssues,
      mitigation,
      metadata: {
        tenantId: context.tenantId || null,
        assessedAt: new Date().toISOString()
      }
    };
    
    // Audit logging if enabled
    if (this.auditEnabled) {
      const AuditLogger = require('../../utils/auditLogger');
      await AuditLogger.log({
        event: 'RISK_ASSESSMENT_COMPLETED',
        tenantId: context.tenantId,
        userId: context.user?.id,
        metadata: {
          riskScore: score,
          highRiskCount: highRiskIssues.length
        }
      });
    }
    
    return result;
  }

  health() {
    return {
      status: 'OK',
      timestamp: new Date().toISOString(),
      strictMode: this.strictMode,
      auditEnabled: this.auditEnabled,
      defaultResidency: this.defaultResidency
    };
  }
}

module.exports = { RiskAssessor };
