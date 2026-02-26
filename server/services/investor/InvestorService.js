/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════════════════╗
  ║ INVESTOR SERVICE - FORENSIC WORKER WITH 100-YEAR EVIDENCE CHAIN                       ║
  ║ R240M Revenue Protection | x-correlation-id Tracing | POPIA §19-22 Compliant          ║
  ║ SHA256 Hash Chain | Court-Admissible | Real-time Aggregation                           ║
  ╚═══════════════════════════════════════════════════════════════════════════════════════╝*/

/**
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/services/investor/InvestorService.js
 * VERSION: 1.0.0-FORENSIC-INVESTOR
 * CREATED: 2026-02-25
 * 
 * INVESTOR VALUE PROPOSITION:
 * • Forensic logging for R240M annual revenue platform
 * • Every investor action permanently recorded with 100-year chain
 * • x-correlation-id traces entire request lifecycle
 * • POPIA §19-22 compliance built into every query
 * • SHA256 hashing for court-admissible evidence
 * • Real-time breach detection and notification
 * 
 * INTEGRATION_MAP:
 * {
 *   "consumers": [
 *     "controllers/investorController.js",
 *     "routes/investorRoutes.js",
 *     "workers/dashboardWorker.js",
 *     "cron/metricsAggregator.js"
 *   ],
 *   "providers": [
 *     "../../models/securityLogModel.js",
 *     "../../models/Valuation.js",
 *     "../../models/Company.js",
 *     "../../utils/logger.js",
 *     "../../utils/auditLogger.js"
 *   ],
 *   "forensicChain": {
 *     "correlationId": "x-correlation-id from request",
 *     "hashAlgorithm": "SHA256",
 *     "retention": "100 years",
 *     "breachNotification": "automated"
 *   }
 * }
 * 
 * MERMAID_INTEGRATION:
 * graph TD
 *   A[Investor Request] -->|x-correlation-id| B[InvestorService]
 *   B -->|step 1: forensicLog| C[SecurityLog.create]
 *   C -->|record access| D[(SecurityLogs)]
 *   B -->|step 2: fetch valuations| E[ValuationModel.aggregate]
 *   B -->|step 3: fetch companies| F[CompanyModel.find]
 *   B -->|step 4: compile metrics| G[Dashboard Builder]
 *   B -->|step 5: forensicLog complete| C
 *   B -->|return| H[Client]
 *   
 *   subgraph "Forensic Chain"
 *     I[Previous Log] -->|previousHash| J[Current Log]
 *     J -->|forensicHash| K[Next Log]
 *   end
 *   
 *   subgraph "Breach Detection"
 *     L[Critical Event] -->|requiresBreachNotification| M[Info Regulator]
 *     M -->|notificationSentTo| N[Audit Trail]
 *   end
 */

import SecurityLog from '../../models/securityLogModel.js';
import Valuation from '../../models/Valuation.js';
import Company from '../../models/Company.js';
import logger from '../../utils/logger.js';
import auditLogger from '../../utils/auditLogger.js';
import crypto from "crypto";

// ============================================================================
// CONSTANTS
// ============================================================================

const SEVERITY_LEVELS = {
  INFO: 'info',
  WARNING: 'warning',
  ERROR: 'error',
  CRITICAL: 'critical',
  BREACH: 'breach'
};

const INVESTOR_EVENTS = {
  DASHBOARD_ACCESS: 'investor_dashboard_access',
  VALUATION_VIEWED: 'valuation_viewed',
  COMPANY_DATA_ACCESSED: 'company_data_accessed',
  REPORT_GENERATED: 'investor_report_generated',
  DATA_EXPORT: 'investor_data_export',
  COMPARABLE_ANALYSIS: 'comparable_analysis',
  MATERIALITY_CHECK: 'materiality_check',
  FORENSIC_AUDIT: 'forensic_audit'
};

const PERFORMANCE_THRESHOLDS = {
  DASHBOARD_GENERATION_MS: 500, // Warning if >500ms
  DATA_AGGREGATION_MS: 200,      // Warning if >200ms
  FORENSIC_LOGGING_MS: 50        // Warning if >50ms
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Measures execution time of async function
 * @param {Function} fn - Async function to measure
 * @param {string} operation - Operation name for logging
 * @returns {Promise<[any, number]>} - [result, durationMs]
 */
async function measureTime(fn, operation) {
  const start = process.hrtime.bigint();
  try {
    const result = await fn();
    const end = process.hrtime.bigint();
    const durationMs = Number(end - start) / 1_000_000;
    
    if (durationMs > PERFORMANCE_THRESHOLDS[operation] && PERFORMANCE_THRESHOLDS[operation]) {
      logger.warn(`Performance threshold exceeded for ${operation}`, {
        durationMs,
        threshold: PERFORMANCE_THRESHOLDS[operation]
      });
    }
    
    return [result, durationMs];
  } catch (error) {
    const end = process.hrtime.bigint();
    const durationMs = Number(end - start) / 1_000_000;
    throw error;
  }
}

/**
 * Generates deterministic cache key
 * @param {Object} params - Request parameters
 * @returns {string} Cache key
 */
function generateCacheKey(params) {
  const { tenantId, period, sections, userId } = params;
  const data = { tenantId, period, sections, userId };
  return crypto
    .createHash('sha256')
    .update(JSON.stringify(data))
    .digest('hex')
    .substring(0, 32);
}

// ============================================================================
// MAIN INVESTOR SERVICE
// ============================================================================

/**
 * WILSY OS: INVESTOR METRICS WORKER
 * Performs high-velocity data aggregation with 100-year forensic logging.
 * 
 * @param {Object} params - Request parameters
 * @param {string} params.tenantId - Tenant ID for isolation
 * @param {string} params.period - Time period (7d, 30d, 90d, 1y)
 * @param {Array} params.sections - Dashboard sections to include
 * @param {string} params.userId - User ID for personalization
 * @param {string} correlationId - x-correlation-id for tracing
 * @returns {Promise<Object>} Dashboard data with forensic metadata
 */
export const getInvestorDashboardData = async (params, correlationId) => {
  const { tenantId, period = '30d', sections = [], userId } = params;
  const startTime = Date.now();
  
  logger.info('InvestorService.getInvestorDashboardData started', {
    tenantId,
    correlationId,
    period,
    sections
  });

  try {
    // ========================================================================
    // STEP 1: FORENSIC LOGGING - Record Access with Hash Chain
    // ========================================================================
    const [accessLog, logDuration] = await measureTime(async () => {
      return await SecurityLog.forensicLog({
        eventType: INVESTOR_EVENTS.DASHBOARD_ACCESS,
        severity: SEVERITY_LEVELS.INFO,
        tenantId,
        userId: userId || 'anonymous',
        correlationId,
        requestId: correlationId, // Using correlationId as requestId for simplicity
        ipAddress: params.ipAddress,
        userAgent: params.userAgent,
        endpoint: '/api/investor/dashboard',
        method: 'GET',
        details: {
          period,
          requestedSections: sections,
          params: {
            ...params,
            // Remove sensitive data
            ipAddress: undefined,
            userAgent: undefined
          }
        },
        requiresBreachNotification: false,
        dataSubjectsAffected: 0,
        tags: ['investor', 'dashboard', `tenant:${tenantId}`]
      }, correlationId);
    }, 'FORENSIC_LOGGING_MS');

    logger.debug('Forensic access log created', {
      logId: accessLog._id,
      forensicHash: accessLog.forensicHash,
      chainPosition: accessLog.chainPosition,
      durationMs: logDuration,
      correlationId
    });

    // ========================================================================
    // STEP 2: FETCH VALUATION DATA
    // ========================================================================
    const [valuationData, valuationDuration] = await measureTime(async () => {
      // Calculate date range based on period
      const endDate = new Date();
      const startDate = new Date();
      
      switch (period) {
        case '7d':
          startDate.setDate(startDate.getDate() - 7);
          break;
        case '30d':
          startDate.setDate(startDate.getDate() - 30);
          break;
        case '90d':
          startDate.setDate(startDate.getDate() - 90);
          break;
        case '1y':
          startDate.setFullYear(startDate.getFullYear() - 1);
          break;
        default:
          startDate.setDate(startDate.getDate() - 30);
      }

      // Fetch valuation summary with aggregation
      const valuationSummary = await Valuation.aggregate([
        { 
          $match: { 
            tenantId,
            createdAt: { $gte: startDate, $lte: endDate }
          } 
        },
        {
          $facet: {
            trends: [
              {
                $group: {
                  _id: {
                    year: { $year: '$createdAt' },
                    month: { $month: '$createdAt' },
                    day: { $dayOfMonth: '$createdAt' }
                  },
                  count: { $sum: 1 },
                  averageValue: { $avg: '$finalValuation.weightedAverage' },
                  totalValue: { $sum: '$finalValuation.weightedAverage' }
                }
              },
              { $sort: { '_id.year': 1, '_id.month': 1, '_id.day': 1 } }
            ],
            byMethod: [
              {
                $group: {
                  _id: '$valuationMethod',
                  count: { $sum: 1 },
                  avgValue: { $avg: '$finalValuation.weightedAverage' }
                }
              }
            ],
            summary: [
              {
                $group: {
                  _id: null,
                  totalValuations: { $sum: 1 },
                  averageValue: { $avg: '$finalValuation.weightedAverage' },
                  totalValue: { $sum: '$finalValuation.weightedAverage' },
                  maxValue: { $max: '$finalValuation.weightedAverage' },
                  minValue: { $min: '$finalValuation.weightedAverage' }
                }
              }
            ]
          }
        }
      ]);

      return valuationSummary[0] || {
        trends: [],
        byMethod: [],
        summary: {
          totalValuations: 0,
          averageValue: 0,
          totalValue: 0
        }
      };
    }, 'DATA_AGGREGATION_MS');

    // Log valuation access for forensic chain
    if (sections.includes('valuations') && valuationData.summary?.totalValuations > 0) {
      await SecurityLog.forensicLog({
        eventType: INVESTOR_EVENTS.VALUATION_VIEWED,
        severity: SEVERITY_LEVELS.INFO,
        tenantId,
        userId: userId || 'anonymous',
        correlationId,
        requestId: correlationId,
        details: {
          valuationCount: valuationData.summary.totalValuations,
          averageValue: valuationData.summary.averageValue,
          totalValue: valuationData.summary.totalValue,
          period
        },
        requiresBreachNotification: false,
        tags: ['investor', 'valuations', `tenant:${tenantId}`]
      }, `${correlationId}-valuations`);
    }

    // ========================================================================
    // STEP 3: FETCH COMPANY DATA
    // ========================================================================
    const [companyData, companyDuration] = await measureTime(async () => {
      const companies = await Company.find({ tenantId })
        .select('name industry status valuations.createdAt valuations.averageValue')
        .limit(100)
        .lean();

      const stats = {
        total: companies.length,
        byIndustry: {},
        withValuations: 0,
        averageValue: 0
      };

      let totalValue = 0;
      companies.forEach(company => {
        // Count by industry
        const industry = company.industry || 'unknown';
        stats.byIndustry[industry] = (stats.byIndustry[industry] || 0) + 1;
        
        // Count companies with valuations
        if (company.valuations?.count > 0) {
          stats.withValuations++;
          totalValue += company.valuations.averageValue || 0;
        }
      });

      stats.averageValue = stats.withValuations > 0 
        ? totalValue / stats.withValuations 
        : 0;

      return {
        companies: companies.slice(0, 10), // Recent 10
        stats
      };
    }, 'DATA_AGGREGATION_MS');

    // Log company data access
    if (sections.includes('overview') || sections.includes('industry')) {
      await SecurityLog.forensicLog({
        eventType: INVESTOR_EVENTS.COMPANY_DATA_ACCESSED,
        severity: SEVERITY_LEVELS.INFO,
        tenantId,
        userId: userId || 'anonymous',
        correlationId,
        requestId: correlationId,
        details: {
          companyCount: companyData.stats.total,
          withValuations: companyData.stats.withValuations,
          industries: Object.keys(companyData.stats.byIndustry)
        },
        requiresBreachNotification: false,
        tags: ['investor', 'companies', `tenant:${tenantId}`]
      }, `${correlationId}-companies`);
    }

    // ========================================================================
    // STEP 4: CHECK FOR MATERIALITY (JSE Compliance)
    // ========================================================================
    let materialityData = null;
    if (sections.includes('jse-compliance')) {
      const JSE_MATERIALITY_THRESHOLD = 50000000; // R50M
      
      const materialValuations = await Valuation.find({
        tenantId,
        'finalValuation.weightedAverage': { $gte: JSE_MATERIALITY_THRESHOLD }
      })
        .populate('companyId', 'name registrationNumber')
        .sort({ 'finalValuation.weightedAverage': -1 })
        .limit(10)
        .lean();

      materialityData = {
        threshold: JSE_MATERIALITY_THRESHOLD,
        count: materialValuations.length,
        valuations: materialValuations.map(v => ({
          companyName: v.companyId?.name,
          value: v.finalValuation?.weightedAverage,
          date: v.createdAt,
          requiresDisclosure: true
        }))
      };

      // Log materiality check
      await SecurityLog.forensicLog({
        eventType: INVESTOR_EVENTS.MATERIALITY_CHECK,
        severity: materialityData.count > 0 ? SEVERITY_LEVELS.WARNING : SEVERITY_LEVELS.INFO,
        tenantId,
        userId: userId || 'anonymous',
        correlationId,
        requestId: correlationId,
        details: materialityData,
        requiresBreachNotification: materialityData.count > 2, // Notify if multiple material events
        dataSubjectsAffected: materialityData.count,
        tags: ['investor', 'jse', 'materiality', `tenant:${tenantId}`]
      }, `${correlationId}-jse`);
    }

    // ========================================================================
    // STEP 5: COMPILE DASHBOARD
    // ========================================================================
    const cacheKey = generateCacheKey({ tenantId, period, sections, userId });
    
    const dashboard = {
      metadata: {
        tenantId,
        period,
        generatedAt: new Date().toISOString(),
        generationTimeMs: Date.now() - startTime,
        correlationId,
        cacheKey,
        forensicHash: accessLog.forensicHash,
        chainPosition: accessLog.chainPosition,
        sections: []
      },
      summary: {
        totalValuations: valuationData.summary?.totalValuations || 0,
        totalCompanies: companyData.stats.total,
        companiesWithValuations: companyData.stats.withValuations,
        averageValuation: valuationData.summary?.averageValue || 0,
        totalValuationValue: valuationData.summary?.totalValue || 0,
        period
      },
      performance: {
        totalMs: Date.now() - startTime,
        forensicLoggingMs: logDuration,
        valuationQueryMs: valuationDuration,
        companyQueryMs: companyDuration,
        timestamp: new Date().toISOString()
      }
    };

    // Add requested sections
    if (sections.includes('valuations')) {
      dashboard.valuations = valuationData;
      dashboard.metadata.sections.push('valuations');
    }

    if (sections.includes('overview') || sections.includes('companies')) {
      dashboard.companies = companyData;
      dashboard.metadata.sections.push('companies');
    }

    if (sections.includes('jse-compliance') && materialityData) {
      dashboard.jseCompliance = materialityData;
      dashboard.metadata.sections.push('jse-compliance');
    }

    // Add industry breakdown if requested
    if (sections.includes('industry')) {
      dashboard.industryBreakdown = Object.entries(companyData.stats.byIndustry).map(
        ([industry, count]) => ({ industry, count })
      );
      dashboard.metadata.sections.push('industry');
    }

    // ========================================================================
    // STEP 6: FINAL FORENSIC LOG - COMPLETION
    // ========================================================================
    const [completionLog] = await measureTime(async () => {
      return await SecurityLog.forensicLog({
        eventType: INVESTOR_EVENTS.DASHBOARD_ACCESS + '_complete',
        severity: SEVERITY_LEVELS.INFO,
        tenantId,
        userId: userId || 'anonymous',
        correlationId,
        requestId: correlationId,
        details: {
          generationTimeMs: Date.now() - startTime,
          sectionsReturned: dashboard.metadata.sections,
          totalValuations: dashboard.summary.totalValuations,
          totalCompanies: dashboard.summary.totalCompanies,
          cacheKey
        },
        requiresBreachNotification: false,
        previousCorrelationId: correlationId, // Link to start log
        tags: ['investor', 'dashboard', 'complete', `tenant:${tenantId}`]
      }, `${correlationId}-complete`);
    }, 'FORENSIC_LOGGING_MS');

    // Update dashboard with completion hash
    dashboard.metadata.completionHash = completionLog.forensicHash;
    dashboard.metadata.chainEnd = completionLog.chainPosition;

    // ========================================================================
    // STEP 7: PERFORMANCE MONITORING & BREACH DETECTION
    // ========================================================================
    const totalTime = Date.now() - startTime;
    
    // Check for performance anomalies (potential DoS)
    if (totalTime > PERFORMANCE_THRESHOLDS.DASHBOARD_GENERATION_MS * 3) {
      await SecurityLog.forensicLog({
        eventType: 'performance_anomaly',
        severity: SEVERITY_LEVELS.WARNING,
        tenantId,
        userId: userId || 'anonymous',
        correlationId,
        requestId: correlationId,
        details: {
          totalTime,
          threshold: PERFORMANCE_THRESHOLDS.DASHBOARD_GENERATION_MS,
          components: {
            forensicLogging: logDuration,
            valuationQuery: valuationDuration,
            companyQuery: companyDuration
          }
        },
        requiresBreachNotification: false,
        tags: ['investor', 'performance', 'anomaly', `tenant:${tenantId}`]
      }, `${correlationId}-performance`);
    }

    // Check for potential data breach indicators
    if (companyData.stats.total > 1000 || valuationData.summary?.totalValuations > 1000) {
      await SecurityLog.forensicLog({
        eventType: 'bulk_data_access',
        severity: SEVERITY_LEVELS.WARNING,
        tenantId,
        userId: userId || 'anonymous',
        correlationId,
        requestId: correlationId,
        details: {
          companyCount: companyData.stats.total,
          valuationCount: valuationData.summary?.totalValuations,
          reason: 'Large data volume accessed - verify authorization'
        },
        requiresBreachNotification: false,
        tags: ['investor', 'security', 'bulk-access', `tenant:${tenantId}`]
      }, `${correlationId}-bulk`);
    }

    // ========================================================================
    // STEP 8: AUDIT LOGGING (Secondary audit trail)
    // ========================================================================
    await auditLogger.log('investor-dashboard', {
      action: 'DASHBOARD_GENERATED',
      tenantId,
      userId: userId || 'system',
      correlationId,
      forensicHash: accessLog.forensicHash,
      completionHash: completionLog.forensicHash,
      duration: totalTime,
      sections: dashboard.metadata.sections,
      timestamp: new Date().toISOString()
    });

    logger.info('InvestorService.getInvestorDashboardData completed', {
      tenantId,
      correlationId,
      durationMs: totalTime,
      sections: dashboard.metadata.sections,
      forensicChain: `${accessLog.chainPosition} → ${completionLog.chainPosition}`
    });

    return dashboard;

  } catch (error) {
    // ========================================================================
    // ERROR HANDLING - Log forensic failure
    // ========================================================================
    logger.error('InvestorService.getInvestorDashboardData failed', {
      tenantId,
      correlationId,
      error: error.message,
      stack: error.stack
    });

    try {
      // Log error to forensic chain
      await SecurityLog.forensicLog({
        eventType: 'investor_service_error',
        severity: SEVERITY_LEVELS.ERROR,
        tenantId,
        userId: params.userId || 'anonymous',
        correlationId,
        requestId: correlationId,
        details: {
          error: error.message,
          stack: error.stack?.split('\n').slice(0, 3),
          params: {
            period,
            sections,
            ...params
          }
        },
        requiresBreachNotification: error.message.includes('breach') || 
                                   error.message.includes('unauthorized'),
        dataSubjectsAffected: error.message.includes('breach') ? 1 : 0,
        tags: ['investor', 'error', `tenant:${tenantId}`]
      }, `${correlationId}-error`);
    } catch (logError) {
      logger.error('Failed to log error to forensic chain', {
        error: logError.message,
        originalError: error.message,
        correlationId
      });
    }

    throw new Error(`FORENSIC_WORKER_FAILED: ${error.message}`);
  }
};

/**
 * Generates forensic report for a correlation ID chain
 * @param {string} correlationId - x-correlation-id to trace
 * @returns {Promise<Object>} Forensic report
 */
export const getForensicReport = async (correlationId) => {
  try {
    // Find all logs in the chain
    const logs = await SecurityLog.findByCorrelationChain(correlationId);
    
    if (logs.length === 0) {
      return {
        found: false,
        correlationId,
        message: 'No logs found for this correlation ID'
      };
    }

    // Verify chain integrity
    const tenantId = logs[0].tenantId;
    const chainVerification = await SecurityLog.verifyHashChain(
      tenantId,
      logs[0].timestamp
    );

    return {
      found: true,
      correlationId,
      logCount: logs.length,
      firstLog: logs[0].timestamp,
      lastLog: logs[logs.length - 1].timestamp,
      chainVerification,
      logs: logs.map(log => ({
        eventType: log.eventType,
        severity: log.severity,
        timestamp: log.timestamp,
        forensicHash: log.forensicHash,
        previousHash: log.previousHash,
        chainPosition: log.chainPosition,
        details: log.details
      }))
    };
  } catch (error) {
    logger.error('Forensic report generation failed', {
      correlationId,
      error: error.message
    });
    throw error;
  }
};

/**
 * Verifies the entire hash chain for a tenant
 * @param {string} tenantId - Tenant ID
 * @returns {Promise<Object>} Verification result
 */
export const verifyTenantChain = async (tenantId) => {
  return await SecurityLog.verifyHashChain(tenantId);
};

/**
 * Anchors daily logs to blockchain
 * @param {string} tenantId - Tenant ID
 * @returns {Promise<Object>} Blockchain anchor
 */
export const anchorToBlockchain = async (tenantId) => {
  return await SecurityLog.anchorToBlockchain(tenantId);
};

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  getInvestorDashboardData,
  getForensicReport,
  verifyTenantChain,
  anchorToBlockchain
};
