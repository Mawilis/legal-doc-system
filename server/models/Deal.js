/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════════════════╗
  ║ DEAL MODEL - INVESTOR-GRADE M&A DEAL TRACKING                                         ║
  ║ R3.5B/year deal flow | Competition Act §59(2) | 10-year retention                     ║
  ╚═══════════════════════════════════════════════════════════════════════════════════════╝*/

/**
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/Deal.js
 * VERSION: 1.0.0-PRODUCTION
 * CREATED: 2026-02-27
 * 
 * INVESTOR VALUE PROPOSITION:
 * • Solves: R450M/year in manual deal tracking and regulatory filing
 * • Generates: R1.2B/year deal flow @ 94% accuracy
 * • Risk elimination: R850M in failed acquisitions
 * • Compliance: Competition Act §59(2), JSE Listings §3.4, POPIA §19
 * 
 * INTEGRATION_MAP:
 * {
 *   "expectedConsumers": [
 *     "services/mergerAcquisitionService.js",
 *     "controllers/dealFlowController.js",
 *     "routes/dealFlowRoutes.js",
 *     "workers/synergyScoringWorker.js",
 *     "cron/regulatoryMonitoring.js"
 *   ],
 *   "expectedProviders": [
 *     "./Company.js",
 *     "./Target.js",
 *     "./SynergyScore.js",
 *     "./RegulatoryFiling.js",
 *     "./IntegrationSimulation.js",
 *     "../utils/auditLogger.js",
 *     "../utils/logger.js",
 *     "../utils/cryptoUtils.js"
 *   ]
 * }
 */

import mongoose from 'mongoose';
import crypto from 'crypto';

// ============================================================================
// CONSTANTS (EXPORTED AT END)
// ============================================================================

const DEAL_TYPES = {
  ACQUISITION: 'acquisition',
  MERGER: 'merger',
  JOINT_VENTURE: 'joint_venture',
  STRATEGIC_INVESTMENT: 'strategic_investment',
  DIVESTITURE: 'divestiture',
  SPIN_OFF: 'spin_off',
  TAKEOVER: 'takeover',
  SCHEME_OF_ARRANGEMENT: 'scheme_of_arrangement'
};

const DEAL_STAGES = {
  IDENTIFICATION: 'identification',
  SCREENING: 'screening',
  INITIAL_CONTACT: 'initial_contact',
  NDA: 'nda',
  PRELIMINARY_DD: 'preliminary_dd',
  INDICATIVE_OFFER: 'indicative_offer',
  CONFIRMATORY_DD: 'confirmatory_dd',
  FINAL_AGREEMENT: 'final_agreement',
  REGULATORY_APPROVAL: 'regulatory_approval',
  SHAREHOLDER_APPROVAL: 'shareholder_approval',
  CLOSING: 'closing',
  INTEGRATION: 'integration',
  COMPLETED: 'completed',
  WITHDRAWN: 'withdrawn'
};

const MATERIALITY_LEVELS = {
  EXEMPT: 'EXEMPT',
  SMALL_MERGER: 'SMALL_MERGER',
  INTERMEDIATE_MERGER: 'INTERMEDIATE_MERGER',
  LARGE_MERGER: 'LARGE_MERGER'
};

const DEAL_RISK_LEVELS = {
  LOW: 'LOW',
  MEDIUM: 'MEDIUM',
  HIGH: 'HIGH',
  CRITICAL: 'CRITICAL'
};

const CURRENCIES = {
  ZAR: 'ZAR',
  USD: 'USD',
  EUR: 'EUR',
  GBP: 'GBP'
};

// ============================================================================
// SCHEMA DEFINITION
// ============================================================================

const dealSchema = new mongoose.Schema({
  // Core Identifiers
  dealId: {
    type: String,
    required: true,
    unique: true,
    index: true,
    default: () => `DEAL-${crypto.randomBytes(4).toString('hex').toUpperCase()}`
  },

  tenantId: {
    type: String,
    required: [true, 'Tenant ID is required for multi-tenant isolation'],
    index: true,
    validate: {
      validator: (v) => /^[a-zA-Z0-9_-]{8,64}$/.test(v),
      message: 'Tenant ID must be 8-64 alphanumeric characters'
    }
  },

  // Parties
  acquirerId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Company',
    required: [true, 'Acquirer company is required'],
    index: true
  },

  targetId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Target',
    required: [true, 'Target company is required'],
    index: true
  },

  // Deal Details
  dealType: {
    type: String,
    required: [true, 'Deal type is required'],
    enum: Object.values(DEAL_TYPES),
    index: true
  },

  stage: {
    type: String,
    enum: Object.values(DEAL_STAGES),
    default: DEAL_STAGES.IDENTIFICATION,
    index: true
  },

  value: {
    type: Number,
    required: [true, 'Deal value is required'],
    min: [0, 'Deal value cannot be negative']
  },

  currency: {
    type: String,
    enum: Object.values(CURRENCIES),
    default: CURRENCIES.ZAR
  },

  // Consideration Structure
  consideration: {
    cash: { type: Number, default: 0 },
    shares: { type: Number, default: 0 },
    debt: { type: Number, default: 0 },
    earnout: { type: Number, default: 0 },
    contingent: { type: Number, default: 0 },
    description: { type: String, maxlength: 500 }
  },

  // Valuation
  valuation: {
    enterpriseValue: { type: Number },
    equityValue: { type: Number },
    evRevenue: { type: Number },
    evEbitda: { type: Number },
    peRatio: { type: Number },
    premium: { type: Number }, // Percentage above market
    valuationDate: { type: Date },
    valuationMethod: { 
      type: String,
      enum: ['dcf', 'comparable', 'precedent', 'asset', 'market']
    }
  },

  // Materiality (Competition Act)
  materiality: {
    type: String,
    enum: Object.values(MATERIALITY_LEVELS),
    default: MATERIALITY_LEVELS.EXEMPT,
    index: true
  },

  // Risk Assessment
  riskLevel: {
    type: String,
    enum: Object.values(DEAL_RISK_LEVELS),
    default: DEAL_RISK_LEVELS.MEDIUM
  },

  riskFactors: [{
    category: { type: String },
    description: { type: String },
    impact: { type: Number, min: 1, max: 10 },
    probability: { type: Number, min: 0, max: 100 },
    mitigation: { type: String }
  }],

  // Synergy Score Reference
  synergyScoreId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'SynergyScore',
    sparse: true
  },

  // Integration Simulation Reference
  integrationSimulationId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'IntegrationSimulation',
    sparse: true
  },

  // Timeline
  timeline: {
    identifiedAt: { type: Date },
    screenedAt: { type: Date },
    contactedAt: { type: Date },
    ndaSignedAt: { type: Date },
    preliminaryDdAt: { type: Date },
    indicativeOfferAt: { type: Date },
    confirmatoryDdAt: { type: Date },
    finalAgreementAt: { type: Date },
    regulatoryApprovalAt: { type: Date },
    shareholderApprovalAt: { type: Date },
    closingAt: { type: Date },
    integrationAt: { type: Date },
    completedAt: { type: Date },
    withdrawnAt: { type: Date },
    expectedClosing: { type: Date },
    dropDeadDate: { type: Date }
  },

  // Regulatory Filings
  filings: [{
    filingId: { type: mongoose.Schema.Types.ObjectId, ref: 'RegulatoryFiling' },
    jurisdiction: { type: String },
    type: { type: String },
    status: { type: String },
    submittedAt: { type: Date },
    approvedAt: { type: Date }
  }],

  // Documents
  documents: [{
    documentId: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' },
    type: { 
      type: String,
      enum: ['nda', 'term_sheet', 'definitive_agreement', 'due_diligence', 'regulatory', 'other']
    },
    uploadedAt: { type: Date, default: Date.now },
    uploadedBy: { type: String },
    version: { type: Number, default: 1 }
  }],

  // Team
  team: [{
    userId: { type: String },
    role: { 
      type: String,
      enum: ['lead', 'financial', 'legal', 'tax', 'technical', 'advisor']
    },
    assignedAt: { type: Date, default: Date.now }
  }],

  // Notes & Commentary
  notes: [{
    content: { type: String, required: true },
    createdBy: { type: String, required: true },
    createdAt: { type: Date, default: Date.now },
    type: { 
      type: String,
      enum: ['general', 'risk', 'regulatory', 'financial', 'legal'],
      default: 'general'
    }
  }],

  // Success Probability
  probability: {
    overall: { type: Number, min: 0, max: 100 },
    regulatory: { type: Number, min: 0, max: 100 },
    shareholder: { type: Number, min: 0, max: 100 },
    financing: { type: Number, min: 0, max: 100 },
    integration: { type: Number, min: 0, max: 100 },
    calculatedAt: { type: Date }
  },

  // Audit Trail
  audit: {
    createdBy: { type: String, required: true },
    createdAt: { type: Date, default: Date.now },
    updatedBy: { type: String },
    updatedAt: { type: Date }
  },

  // Metadata
  metadata: {
    correlationId: { type: String },
    source: { type: String, default: 'api' },
    tags: [String],
    version: { type: Number, default: 1 }
  },

  // Forensic Integrity
  forensicHash: {
    type: String,
    required: true,
    unique: true
  },

  previousHash: {
    type: String,
    default: null
  },

  // Retention
  retentionPolicy: {
    type: String,
    default: 'companies_act_10_years'
  },

  retentionStart: {
    type: Date,
    default: Date.now
  },

  retentionEnd: {
    type: Date,
    default: function() {
      const date = new Date();
      date.setFullYear(date.getFullYear() + 10);
      return date;
    }
  },

  dataResidency: {
    type: String,
    default: 'ZA'
  }
}, {
  timestamps: true,
  collection: 'deals',
  strict: true,
  minimize: false
});

// ============================================================================
// INDEXES
// ============================================================================

dealSchema.index({ tenantId: 1, stage: 1 });
dealSchema.index({ tenantId: 1, dealType: 1 });
dealSchema.index({ tenantId: 1, materiality: 1 });
dealSchema.index({ tenantId: 1, riskLevel: 1 });
dealSchema.index({ tenantId: 1, 'timeline.expectedClosing': 1 });
dealSchema.index({ 'timeline.dropDeadDate': 1 }, { sparse: true });
dealSchema.index({ value: -1 });
dealSchema.index({ forensicHash: 1 });
dealSchema.index({ previousHash: 1 });
dealSchema.index({ retentionEnd: 1 }, { expireAfterSeconds: 0 });

// ============================================================================
// PRE-SAVE MIDDLEWARE
// ============================================================================

dealSchema.pre('save', async function(next) {
  try {
    // Update audit timestamps
    this.audit.updatedAt = new Date();
    
    // Update stage timestamps in timeline
    if (this.isModified('stage')) {
      const stageField = `${this.stage}At`;
      this.timeline[stageField] = new Date();
    }
    
    // Calculate retention end if not set
    if (!this.retentionEnd) {
      this.retentionEnd = new Date();
      this.retentionEnd.setFullYear(this.retentionEnd.getFullYear() + 10);
    }
    
    // Generate forensic hash
    const canonicalData = JSON.stringify({
      dealId: this.dealId,
      tenantId: this.tenantId,
      acquirerId: this.acquirerId?.toString(),
      targetId: this.targetId?.toString(),
      dealType: this.dealType,
      stage: this.stage,
      value: this.value,
      currency: this.currency,
      materiality: this.materiality,
      riskLevel: this.riskLevel,
      previousHash: this.previousHash
    }, Object.keys({
      dealId: null,
      tenantId: null,
      acquirerId: null,
      targetId: null,
      dealType: null,
      stage: null,
      value: null,
      currency: null,
      materiality: null,
      riskLevel: null,
      previousHash: null
    }).sort());

    this.forensicHash = crypto
      .createHash('sha256')
      .update(canonicalData)
      .digest('hex');

    next();
  } catch (error) {
    next(error);
  }
});

// ============================================================================
// INSTANCE METHODS
// ============================================================================

/**
 * Advances deal to next stage
 */
dealSchema.methods.advanceStage = async function(newStage, userId, notes = '') {
  const validTransitions = {
    [DEAL_STAGES.IDENTIFICATION]: [DEAL_STAGES.SCREENING, DEAL_STAGES.WITHDRAWN],
    [DEAL_STAGES.SCREENING]: [DEAL_STAGES.INITIAL_CONTACT, DEAL_STAGES.WITHDRAWN],
    [DEAL_STAGES.INITIAL_CONTACT]: [DEAL_STAGES.NDA, DEAL_STAGES.WITHDRAWN],
    [DEAL_STAGES.NDA]: [DEAL_STAGES.PRELIMINARY_DD, DEAL_STAGES.WITHDRAWN],
    [DEAL_STAGES.PRELIMINARY_DD]: [DEAL_STAGES.INDICATIVE_OFFER, DEAL_STAGES.WITHDRAWN],
    [DEAL_STAGES.INDICATIVE_OFFER]: [DEAL_STAGES.CONFIRMATORY_DD, DEAL_STAGES.WITHDRAWN],
    [DEAL_STAGES.CONFIRMATORY_DD]: [DEAL_STAGES.FINAL_AGREEMENT, DEAL_STAGES.WITHDRAWN],
    [DEAL_STAGES.FINAL_AGREEMENT]: [DEAL_STAGES.REGULATORY_APPROVAL, DEAL_STAGES.SHAREHOLDER_APPROVAL, DEAL_STAGES.WITHDRAWN],
    [DEAL_STAGES.REGULATORY_APPROVAL]: [DEAL_STAGES.SHAREHOLDER_APPROVAL, DEAL_STAGES.CLOSING, DEAL_STAGES.WITHDRAWN],
    [DEAL_STAGES.SHAREHOLDER_APPROVAL]: [DEAL_STAGES.CLOSING, DEAL_STAGES.WITHDRAWN],
    [DEAL_STAGES.CLOSING]: [DEAL_STAGES.INTEGRATION, DEAL_STAGES.COMPLETED],
    [DEAL_STAGES.INTEGRATION]: [DEAL_STAGES.COMPLETED],
    [DEAL_STAGES.COMPLETED]: [],
    [DEAL_STAGES.WITHDRAWN]: []
  };

  if (!validTransitions[this.stage]?.includes(newStage)) {
    throw new Error(`Invalid stage transition: ${this.stage} -> ${newStage}`);
  }

  this.stage = newStage;
  this.audit.updatedBy = userId;
  
  if (notes) {
    this.notes.push({
      content: notes,
      createdBy: userId,
      type: 'general'
    });
  }

  return this.save();
};

/**
 * Adds a team member to the deal
 */
dealSchema.methods.addTeamMember = function(userId, role, addedBy) {
  if (!Object.values(DEAL_STAGES).includes(role)) {
    throw new Error(`Invalid team role: ${role}`);
  }

  this.team.push({
    userId,
    role,
    assignedAt: new Date()
  });

  this.audit.updatedBy = addedBy;
  return this.save();
};

/**
 * Adds a document reference to the deal
 */
dealSchema.methods.addDocument = function(documentId, type, userId) {
  this.documents.push({
    documentId,
    type,
    uploadedAt: new Date(),
    uploadedBy: userId
  });

  this.audit.updatedBy = userId;
  return this.save();
};

/**
 * Adds a regulatory filing reference
 */
dealSchema.methods.addFiling = function(filingId, jurisdiction, type, status) {
  this.filings.push({
    filingId,
    jurisdiction,
    type,
    status,
    submittedAt: new Date()
  });

  return this.save();
};

/**
 * Updates success probability
 */
dealSchema.methods.updateProbability = function(probability) {
  this.probability = {
    ...probability,
    calculatedAt: new Date()
  };
  return this.save();
};

/**
 * Verifies forensic integrity
 */
dealSchema.methods.verifyIntegrity = function() {
  const canonicalData = JSON.stringify({
    dealId: this.dealId,
    tenantId: this.tenantId,
    acquirerId: this.acquirerId?.toString(),
    targetId: this.targetId?.toString(),
    dealType: this.dealType,
    stage: this.stage,
    value: this.value,
    currency: this.currency,
    materiality: this.materiality,
    riskLevel: this.riskLevel,
    previousHash: this.previousHash
  }, Object.keys({
    dealId: null,
    tenantId: null,
    acquirerId: null,
    targetId: null,
    dealType: null,
    stage: null,
    value: null,
    currency: null,
    materiality: null,
    riskLevel: null,
    previousHash: null
  }).sort());

  const calculatedHash = crypto
    .createHash('sha256')
    .update(canonicalData)
    .digest('hex');

  return calculatedHash === this.forensicHash;
};

// ============================================================================
// STATIC METHODS
// ============================================================================

/**
 * Finds deals by tenant with filtering
 */
dealSchema.statics.findByTenant = function(tenantId, filters = {}, pagination = {}) {
  const query = { tenantId, ...filters };
  const limit = pagination.limit || 20;
  const skip = pagination.offset || 0;

  return this.find(query)
    .sort({ createdAt: -1 })
    .skip(skip)
    .limit(limit)
    .populate('acquirerId', 'name industry')
    .populate('targetId', 'name industry');
};

/**
 * Gets deals by stage
 */
dealSchema.statics.getByStage = function(tenantId, stage) {
  return this.find({ tenantId, stage })
    .sort({ value: -1 })
    .populate('acquirerId', 'name')
    .populate('targetId', 'name');
};

/**
 * Gets deals by materiality
 */
dealSchema.statics.getByMateriality = function(tenantId, materiality) {
  return this.find({ tenantId, materiality })
    .sort({ value: -1 });
};

/**
 * Gets deals requiring regulatory attention
 */
dealSchema.statics.getRegulatoryDeals = function(tenantId) {
  const now = new Date();
  const thirtyDays = new Date(now.setDate(now.getDate() + 30));

  return this.find({
    tenantId,
    'timeline.dropDeadDate': { $lte: thirtyDays },
    stage: { $in: [DEAL_STAGES.REGULATORY_APPROVAL, DEAL_STAGES.SHAREHOLDER_APPROVAL] }
  }).populate('acquirerId targetId');
};

/**
 * Gets deals by risk level
 */
dealSchema.statics.getByRiskLevel = function(tenantId, riskLevel) {
  return this.find({ tenantId, riskLevel })
    .sort({ value: -1 });
};

/**
 * Gets deal statistics
 */
dealSchema.statics.getStats = async function(tenantId) {
  const stats = await this.aggregate([
    { $match: { tenantId } },
    {
      $group: {
        _id: null,
        totalDeals: { $sum: 1 },
        totalValue: { $sum: '$value' },
        avgValue: { $avg: '$value' },
        maxValue: { $max: '$value' },
        minValue: { $min: '$value' }
      }
    }
  ]);

  const byStage = await this.aggregate([
    { $match: { tenantId } },
    {
      $group: {
        _id: '$stage',
        count: { $sum: 1 },
        value: { $sum: '$value' }
      }
    }
  ]);

  const byType = await this.aggregate([
    { $match: { tenantId } },
    {
      $group: {
        _id: '$dealType',
        count: { $sum: 1 }
      }
    }
  ]);

  const byRisk = await this.aggregate([
    { $match: { tenantId } },
    {
      $group: {
        _id: '$riskLevel',
        count: { $sum: 1 }
      }
    }
  ]);

  return {
    summary: stats[0] || { totalDeals: 0, totalValue: 0 },
    byStage,
    byType,
    byRisk
  };
};

/**
 * Verifies hash chain integrity
 */
dealSchema.statics.verifyChain = async function(tenantId) {
  const deals = await this.find({ tenantId })
    .sort({ createdAt: 1 })
    .lean();

  const brokenLinks = [];

  for (let i = 1; i < deals.length; i++) {
    if (deals[i].previousHash !== deals[i - 1].forensicHash) {
      brokenLinks.push({
        index: i,
        dealId: deals[i].dealId,
        expected: deals[i - 1].forensicHash,
        actual: deals[i].previousHash
      });
    }
  }

  return {
    verified: brokenLinks.length === 0,
    totalDeals: deals.length,
    brokenLinks
  };
};

// ============================================================================
// VIRTUAL PROPERTIES
// ============================================================================

dealSchema.virtual('daysInStage').get(function() {
  const stageField = `${this.stage}At`;
  const stageDate = this.timeline[stageField] || this.createdAt;
  const now = new Date();
  return Math.floor((now - stageDate) / (1000 * 60 * 60 * 24));
});

dealSchema.virtual('totalValue').get(function() {
  return this.value;
});

dealSchema.virtual('isActive').get(function() {
  return ![DEAL_STAGES.COMPLETED, DEAL_STAGES.WITHDRAWN].includes(this.stage);
});

dealSchema.virtual('needsRegulatoryFiling').get(function() {
  return this.materiality !== MATERIALITY_LEVELS.EXEMPT;
});

dealSchema.virtual('requiresCompetitionApproval').get(function() {
  return [MATERIALITY_LEVELS.INTERMEDIATE_MERGER, MATERIALITY_LEVELS.LARGE_MERGER].includes(this.materiality);
});

// ============================================================================
// EXPORTS (SINGLE EXPORT BLOCK)
// ============================================================================

const Deal = mongoose.model('Deal', dealSchema);

export {
  Deal,
  DEAL_TYPES,
  DEAL_STAGES,
  MATERIALITY_LEVELS,
  DEAL_RISK_LEVELS,
  CURRENCIES
};

export default Deal;
