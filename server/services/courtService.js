#!/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ COURT SERVICE - COMPLETE SA JUDICIAL MANAGEMENT SYSTEM                    ║
  ║ WITH QUANTUM PRECEDENT MATCHING                                           ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import { Court } from '../models/Court.js';
import AuditLogger from '../utils/auditLogger.js';
import loggerRaw from '../utils/logger.js';
const logger = loggerRaw.default || loggerRaw;
import tenantContext from '../middleware/tenantContext.js';
import QuantumPrecedentMatcher from '../utils/quantumPrecedentMatcher.js';
import crypto from 'crypto';

// ============================================================================
// CONSTANTS - EXPORTED FOR TESTS
// ============================================================================

export const COURT_TIERS = {
  CONSTITUTIONAL: 'constitutional',
  SUPREME_APPEAL: 'supreme_appeal',
  HIGH: 'high',
  SPECIALIST: 'specialist',
  MAGISTRATE: 'magistrate',
  TRADITIONAL: 'traditional',
  TRIBUNAL: 'tribunal',
};

export const COURT_CATEGORIES = {
  CONSTITUTIONAL_COURT: 'constitutional_court',
  SUPREME_COURT_APPEAL: 'supreme_court_appeal',
  HIGH_COURT_GP: 'high_court_gauteng',
  HIGH_COURT_KZN: 'high_court_kzn',
  HIGH_COURT_WC: 'high_court_western_cape',
  HIGH_COURT_EC: 'high_court_eastern_cape',
  HIGH_COURT_FS: 'high_court_free_state',
  HIGH_COURT_NC: 'high_court_northern_cape',
  HIGH_COURT_NW: 'high_court_north_west',
  HIGH_COURT_LP: 'high_court_limpopo',
  HIGH_COURT_MP: 'high_court_mpumalanga',
  HIGH_COURT_PRETORIA: 'high_court_pretoria',
  HIGH_COURT_JOHANNESBURG: 'high_court_johannesburg',
  HIGH_COURT_DURBAN: 'high_court_durban',
  HIGH_COURT_PIETERMARITZBURG: 'high_court_pietermaritzburg',
  HIGH_COURT_CAPE_TOWN: 'high_court_cape_town',
  LABOUR_COURT: 'labour_court',
  LABOUR_APPEAL_COURT: 'labour_appeal_court',
  LAND_CLAIMS_COURT: 'land_claims_court',
  ELECTORAL_COURT: 'electoral_court',
  TAX_COURT: 'tax_court',
  COMPETITION_APPEAL_COURT: 'competition_appeal_court',
  DISTRICT_MAGISTRATE: 'district_magistrate',
  REGIONAL_MAGISTRATE: 'regional_magistrate',
  TRADITIONAL_LEADERSHIP_COURT: 'traditional_leadership_court',
  CCMA: 'ccma',
  BARGAINING_COUNCIL: 'bargaining_council',
};

const COURT_ACTIONS = {
  COURT_CREATED: 'court_created',
  COURT_UPDATED: 'court_updated',
  JURISDICTION_CHECKED: 'jurisdiction_checked',
  APPEAL_ROUTE_CALCULATED: 'appeal_route_calculated',
  JUDICIAL_OFFICER_ADDED: 'judicial_officer_added',
  PRACTICE_DIRECTIVE_ADDED: 'practice_directive_added',
  COURT_HIERARCHY_QUERIED: 'court_hierarchy_queried',
  QUANTUM_PREDICTION: 'quantum_prediction',
};

const RETENTION_POLICIES = {
  COURT_RECORDS: {
    name: 'court_records_10_years',
    legalReference: 'Superior Courts Act 10 of 2013 §12',
    retentionYears: 10,
  },
  JUDICIAL_OFFICER_RECORDS: {
    name: 'judicial_officer_records_20_years',
    legalReference: 'Judicial Service Commission Act 9 of 1994',
    retentionYears: 20,
  },
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

const generateCorrelationId = () => {
  return `court-${Date.now()}-${crypto.randomBytes(4).toString('hex')}`;
};

const applyRetentionPolicy = (auditEntry, policyKey = 'COURT_RECORDS') => {
  const policy = RETENTION_POLICIES[policyKey];
  return {
    ...auditEntry,
    retentionPolicy: policy.name,
    retentionPeriod: policy.retentionYears * 365,
    legalReference: policy.legalReference,
    retentionStart: new Date().toISOString(),
    dataResidency: process.env.DEFAULT_DATA_RESIDENCY || 'ZA',
  };
};

// ============================================================================
// COURT SERVICE CLASS
// ============================================================================

export class CourtService {
  constructor(options = {}) {
    this.serviceId = generateCorrelationId();
    this.tenantId = options.tenantId;
    this.region = options.region || 'ZA';
    this.createdAt = new Date().toISOString();
    this.quantumMatcher = new QuantumPrecedentMatcher();
  }

  /**
   * Get tenant context
   */
  getTenantContext() {
    try {
      const ctx = tenantContext.get();
      if (ctx?.tenantId) return ctx;
    } catch (error) {
      logger.debug('Tenant context not available', { error: error.message });
    }

    if (this.tenantId) {
      return { tenantId: this.tenantId, region: this.region };
    }

    throw new Error('No tenant context available');
  }

  /**
   * Create a new court
   */
  async createCourt(courtData, userId) {
    const startTime = Date.now();
    const { tenantId } = this.getTenantContext();
    const correlationId = generateCorrelationId();

    try {
      logger.info('Creating new court', {
        correlationId,
        tenantId,
        courtName: courtData.name,
      });

      if (!courtData.category || !Object.values(COURT_CATEGORIES).includes(courtData.category)) {
        throw new Error('Invalid court category');
      }

      const court = new Court({
        ...courtData,
        tenantId,
        audit: {
          createdBy: userId,
          createdAt: new Date(),
        },
        metadata: {
          correlationId,
          source: 'api',
        },
      });

      const savedCourt = await court.save();

      const auditEntry = applyRetentionPolicy({
        action: COURT_ACTIONS.COURT_CREATED,
        tenantId,
        userId,
        correlationId,
        courtId: savedCourt.courtId,
        courtName: savedCourt.name,
        courtTier: savedCourt.tier,
        processingTimeMs: Date.now() - startTime,
        timestamp: new Date().toISOString(),
      });

      await AuditLogger.log('court-service', auditEntry);

      logger.info('Court created successfully', {
        correlationId,
        courtId: savedCourt.courtId,
        processingTimeMs: Date.now() - startTime,
      });

      return savedCourt;
    } catch (error) {
      logger.error('Court creation failed', {
        correlationId,
        error: error.message,
        stack: error.stack,
      });
      throw new Error(`COURT_CREATION_FAILED: ${error.message}`);
    }
  }

  /**
   * Get court by ID
   */
  async getCourt(courtId) {
    const { tenantId } = this.getTenantContext();

    const court = await Court.findOne({ courtId, tenantId })
      .populate('hierarchy.parentCourt', 'name tier category')
      .populate('hierarchy.appealTo', 'name tier category')
      .lean();

    if (!court) {
      throw new Error('Court not found');
    }

    return court;
  }

  /**
   * Update court
   */
  async updateCourt(courtId, updates, userId) {
    const startTime = Date.now();
    const { tenantId } = this.getTenantContext();
    const correlationId = generateCorrelationId();

    try {
      const court = await Court.findOne({ courtId, tenantId });

      if (!court) {
        throw new Error('Court not found');
      }

      Object.assign(court, updates);
      court.audit.updatedBy = userId;
      court.audit.updatedAt = new Date();
      court.metadata.correlationId = correlationId;

      const updatedCourt = await court.save();

      const auditEntry = applyRetentionPolicy({
        action: COURT_ACTIONS.COURT_UPDATED,
        tenantId,
        userId,
        correlationId,
        courtId: updatedCourt.courtId,
        updatedFields: Object.keys(updates),
        processingTimeMs: Date.now() - startTime,
        timestamp: new Date().toISOString(),
      });

      await AuditLogger.log('court-service', auditEntry);

      return updatedCourt;
    } catch (error) {
      logger.error('Court update failed', {
        correlationId,
        error: error.message,
      });
      throw error;
    }
  }

  /**
   * List courts with filtering
   */
  async listCourts(filters = {}, pagination = {}) {
    const { tenantId } = this.getTenantContext();

    const query = { tenantId, ...filters };
    const limit = pagination.limit || 50;
    const skip = pagination.offset || 0;

    const courts = await Court.find(query)
      .sort({ tier: 1, name: 1 })
      .skip(skip)
      .limit(limit)
      .lean();

    const total = await Court.countDocuments(query);

    return {
      courts,
      pagination: {
        total,
        limit,
        offset: skip,
        pages: Math.ceil(total / limit),
      },
    };
  }

  /**
   * Check jurisdiction for a case
   */
  async checkJurisdiction(caseData) {
    const startTime = Date.now();
    const { tenantId, userId } = this.getTenantContext();
    const correlationId = generateCorrelationId();

    try {
      logger.info('Checking jurisdiction', {
        correlationId,
        tenantId,
        caseType: caseData.type,
      });

      const courts = await Court.find({ tenantId, status: 'active' }).lean();

      const eligibleCourts = [];
      const ineligibleCourts = [];

      for (const court of courts) {
        const hasJurisdiction = await this.evaluateJurisdiction(court, caseData);
        if (hasJurisdiction) {
          eligibleCourts.push({
            courtId: court.courtId,
            name: court.name,
            tier: court.tier,
            appealTo: court.hierarchy?.appealTo,
            confidence: this.calculateJurisdictionConfidence(court, caseData),
          });
        } else {
          ineligibleCourts.push({
            courtId: court.courtId,
            name: court.name,
            reason: this.getIneligibilityReason(court, caseData),
          });
        }
      }

      eligibleCourts.sort((a, b) => b.confidence - a.confidence);

      const result = {
        hasJurisdiction: eligibleCourts.length > 0,
        eligibleCourts: eligibleCourts.slice(0, 5),
        alternativeCourts: ineligibleCourts.slice(0, 5),
        recommendedCourt: eligibleCourts[0] || null,
        requiresAppeal: false,
      };

      if (caseData.isAppeal && caseData.fromCourt) {
        const fromCourt = await Court.findOne({ courtId: caseData.fromCourt, tenantId });
        if (fromCourt && fromCourt.hierarchy?.appealTo) {
          const appealCourt = await Court.findById(fromCourt.hierarchy.appealTo);
          result.requiresAppeal = true;
          result.appealCourt = appealCourt
            ? {
                courtId: appealCourt.courtId,
                name: appealCourt.name,
              }
            : null;
        }
      }

      const auditEntry = applyRetentionPolicy({
        action: COURT_ACTIONS.JURISDICTION_CHECKED,
        tenantId,
        userId,
        correlationId,
        caseType: caseData.type,
        eligibleCount: eligibleCourts.length,
        recommendedCourt: result.recommendedCourt?.courtId,
        processingTimeMs: Date.now() - startTime,
        timestamp: new Date().toISOString(),
      });

      await AuditLogger.log('court-service', auditEntry);

      return result;
    } catch (error) {
      logger.error('Jurisdiction check failed', {
        correlationId,
        error: error.message,
      });
      throw error;
    }
  }

  /**
   * Evaluate jurisdiction for a single court
   */
  async evaluateJurisdiction(court, caseData) {
    try {
      const courtInstance = new Court(court);
      return courtInstance.hasJurisdiction(caseData);
    } catch (error) {
      logger.error('Jurisdiction evaluation failed', { error: error.message });
      return false;
    }
  }

  /**
   * Calculate jurisdiction confidence score
   */
  calculateJurisdictionConfidence(court, caseData) {
    let score = 70;

    if (caseData.location) {
      if (court.geographicJurisdiction?.national) {
        score += 15;
      } else if (court.geographicJurisdiction?.provinces?.includes(caseData.location.province)) {
        score += 20;
      } else if (court.geographicJurisdiction?.districts?.includes(caseData.location.district)) {
        score += 25;
      } else {
        score -= 30;
      }
    }

    switch (caseData.type) {
      case 'civil':
        if (court.jurisdiction.civil?.hasJurisdiction) {
          score += 20;
          if (caseData.value && court.jurisdiction.civil.monetaryMax) {
            if (caseData.value <= court.jurisdiction.civil.monetaryMax) {
              score += 15;
            } else {
              score -= 40;
            }
          }
        }
        break;
      case 'criminal':
        if (court.jurisdiction.criminal?.hasJurisdiction) {
          score += 20;
          if (
            caseData.offence &&
            court.jurisdiction.criminal.offences?.includes(caseData.offence)
          ) {
            score += 15;
          }
        }
        break;
    }

    if (caseData.isAppeal && court.isAppealCourt) {
      score += 30;
    } else if (!caseData.isAppeal && court.isTrialCourt) {
      score += 10;
    }

    return Math.min(Math.max(score, 0), 100);
  }

  /**
   * Get ineligibility reason
   */
  getIneligibilityReason(court, caseData) {
    if (caseData.isAppeal && !court.isAppealCourt) {
      return 'Not an appeal court';
    }
    if (caseData.type === 'civil' && !court.jurisdiction.civil?.hasJurisdiction) {
      return 'No civil jurisdiction';
    }
    if (caseData.type === 'criminal' && !court.jurisdiction.criminal?.hasJurisdiction) {
      return 'No criminal jurisdiction';
    }
    if (caseData.value && court.jurisdiction.civil?.monetaryMax) {
      if (caseData.value > court.jurisdiction.civil.monetaryMax) {
        return 'Exceeds monetary jurisdiction';
      }
    }
    return 'Geographic jurisdiction mismatch';
  }

  /**
   * Get appeal route for a court
   */
  async getAppealRoute(courtId) {
    const startTime = Date.now();
    const { tenantId, userId } = this.getTenantContext();
    const correlationId = generateCorrelationId();

    try {
      const court = await Court.findOne({ courtId, tenantId });
      if (!court) {
        throw new Error('Court not found');
      }

      const route = [];
      let currentCourt = court;

      while (currentCourt.hierarchy?.appealTo) {
        const nextCourt = await Court.findById(currentCourt.hierarchy.appealTo);
        if (!nextCourt) break;

        route.push({
          fromCourt: currentCourt.name,
          toCourt: nextCourt.name,
          level: route.length + 1,
          leaveRequired: currentCourt.jurisdiction?.appeal?.leaveRequired || false,
        });

        currentCourt = nextCourt;
      }

      const auditEntry = applyRetentionPolicy({
        action: COURT_ACTIONS.APPEAL_ROUTE_CALCULATED,
        tenantId,
        userId,
        correlationId,
        courtId: court.courtId,
        appealSteps: route.length,
        processingTimeMs: Date.now() - startTime,
        timestamp: new Date().toISOString(),
      });

      await AuditLogger.log('court-service', auditEntry);

      return {
        courtId: court.courtId,
        courtName: court.name,
        appealRoute: route,
        finalCourt: route.length > 0 ? route[route.length - 1].toCourt : court.name,
      };
    } catch (error) {
      logger.error('Appeal route calculation failed', {
        correlationId,
        error: error.message,
      });
      throw error;
    }
  }

  /**
   * Add judicial officer to court
   */
  async addJudicialOfficer(courtId, officerData, userId) {
    const startTime = Date.now();
    const { tenantId } = this.getTenantContext();
    const correlationId = generateCorrelationId();

    try {
      const court = await Court.findOne({ courtId, tenantId });
      if (!court) {
        throw new Error('Court not found');
      }

      const officer = {
        officerId: `JUD-${crypto.randomBytes(3).toString('hex').toUpperCase()}`,
        ...officerData,
        active: true,
      };

      court.judicialOfficers.push(officer);
      court.audit.updatedBy = userId;
      court.metadata.correlationId = correlationId;

      await court.save();

      const auditEntry = applyRetentionPolicy(
        {
          action: COURT_ACTIONS.JUDICIAL_OFFICER_ADDED,
          tenantId,
          userId,
          correlationId,
          courtId: court.courtId,
          officerName: officer.name,
          officerTitle: officer.title,
          processingTimeMs: Date.now() - startTime,
          timestamp: new Date().toISOString(),
        },
        'JUDICIAL_OFFICER_RECORDS'
      );

      await AuditLogger.log('court-service', auditEntry);

      return officer;
    } catch (error) {
      logger.error('Add judicial officer failed', {
        correlationId,
        error: error.message,
      });
      throw error;
    }
  }

  /**
   * Get court hierarchy
   */
  async getHierarchy() {
    const { tenantId } = this.getTenantContext();
    const correlationId = generateCorrelationId();

    try {
      const hierarchy = await Court.getHierarchy(tenantId);

      logger.info('Court hierarchy retrieved', {
        correlationId,
        tenantId,
      });

      return hierarchy;
    } catch (error) {
      logger.error('Get hierarchy failed', {
        correlationId,
        error: error.message,
      });
      throw error;
    }
  }

  /**
   * Get court statistics
   */
  async getStats() {
    const { tenantId } = this.getTenantContext();

    const stats = await Court.getStats(tenantId);

    return stats;
  }

  /**
   * Add practice directive
   */
  async addPracticeDirective(courtId, directive, userId) {
    const { tenantId } = this.getTenantContext();
    const correlationId = generateCorrelationId();

    try {
      const court = await Court.findOne({ courtId, tenantId });
      if (!court) {
        throw new Error('Court not found');
      }

      const newDirective = {
        ...directive,
        directiveNumber: `DIR-${crypto.randomBytes(2).toString('hex').toUpperCase()}`,
        issuedDate: new Date(),
        active: true,
      };

      court.practiceDirectives.push(newDirective);
      court.audit.updatedBy = userId;
      court.metadata.correlationId = correlationId;

      await court.save();

      return newDirective;
    } catch (error) {
      logger.error('Add practice directive failed', {
        correlationId,
        error: error.message,
      });
      throw error;
    }
  }

  /**
   * Find similar precedents using quantum matching
   */
  async findSimilarPrecedents(query, options = {}) {
    const startTime = Date.now();
    const { tenantId, userId } = this.getTenantContext();
    const correlationId = generateCorrelationId();

    try {
      logger.info('Finding similar precedents with quantum matching', {
        correlationId,
        tenantId,
        query,
      });

      const results = await this.quantumMatcher.findSimilar(query, options);

      const auditEntry = applyRetentionPolicy({
        action: COURT_ACTIONS.QUANTUM_PREDICTION,
        tenantId,
        userId,
        correlationId,
        query,
        resultsCount: results.length,
        processingTimeMs: Date.now() - startTime,
        timestamp: new Date().toISOString(),
      });

      await AuditLogger.log('court-service', auditEntry);

      return results;
    } catch (error) {
      logger.error('Quantum matching failed', {
        correlationId,
        error: error.message,
      });
      throw error;
    }
  }

  /**
   * Predict case outcome using quantum superposition
   */
  async predictOutcome(caseData) {
    const startTime = Date.now();
    const { tenantId, userId } = this.getTenantContext();
    const correlationId = generateCorrelationId();

    try {
      logger.info('Predicting outcome with quantum superposition', {
        correlationId,
        tenantId,
        caseData,
      });

      const prediction = await this.quantumMatcher.predictOutcome(caseData);

      const auditEntry = applyRetentionPolicy({
        action: COURT_ACTIONS.QUANTUM_PREDICTION,
        tenantId,
        userId,
        correlationId,
        caseData,
        prediction: JSON.parse(JSON.stringify(prediction)),
        processingTimeMs: Date.now() - startTime,
        timestamp: new Date().toISOString(),
      });

      await AuditLogger.log('court-service', auditEntry);

      return prediction;
    } catch (error) {
      logger.error('Outcome prediction failed', {
        correlationId,
        error: error.message,
      });
      throw error;
    }
  }

  /**
   * Get quantum stats
   */
  getQuantumStats() {
    return this.quantumMatcher.getStats();
  }
}

// ============================================================================
// EXPORTS
// ============================================================================

export default CourtService;
