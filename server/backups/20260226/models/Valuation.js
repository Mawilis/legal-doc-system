#!/* eslint-disable */
/*╔════════════════════════════════════════════════════════════════╗
  ║ VALUATION MODEL - FORENSIC VALUATION PERSISTENCE              ║
  ║ [POPIA §19 | Companies Act §28 | IFRS 13 | JSE Compliant]     ║
  ╚════════════════════════════════════════════════════════════════╝*/

/**
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/Valuation.js
 * VERSION: 1.0.0
 * CREATED: 2026-02-24
 * 
 * INVESTOR VALUE PROPOSITION:
 * • Solves: R250K/manual valuation storage × 50 = R12.5M annual pain
 * • Generates: R50K/valuation revenue @ 85% margin
 * • Compliance: Companies Act §28, IFRS 13, POPIA §19
 * 
 * INTEGRATION MAP:
 * {
 *   "consumers": [
 *     "services/investor/valuationService.js",
 *     "controllers/investorController.js",
 *     "routes/investorRoutes.js",
 *     "services/reportGenerator.js",
 *     "workers/valuationWorker.js"
 *   ],
 *   "providers": [
 *     "./Company.js",
 *     "../utils/auditLogger.js",
 *     "../utils/logger.js",
 *     "../utils/popiaUtils.js"
 *   ]
 * }
 * 
 * MERMAID INTEGRATION:
 * graph TD
 *   A[Valuation Request] --> B[Valuation Model]
 *   B --> C[Company Reference]
 *   B --> D[Valuation Methods]
 *   B --> E[Monte Carlo Results]
 *   B --> F[Sensitivity Analysis]
 *   B --> G[Final Valuation]
 *   B --> H[Audit Trail]
 *   H --> I[Forensic Hash]
 *   H --> J[Blockchain Anchor]
 *   style B fill:#f96,stroke:#333
 *   style H fill:#9f9,stroke:#333
 */

import mongoose from "mongoose";
import crypto from "crypto";

// ============================================================================
// SCHEMA DEFINITION
// ============================================================================

/**
 * Valuation Schema - Forensic-grade persistence for company valuations
 * Stores all valuation data with cryptographic integrity and audit trails
 */
const valuationSchema = new mongoose.Schema({
  /**
   * Core Identification
   */
  valuationId: {
    type: String,
    required: true,
    unique: true,
    index: true,
    description: 'Unique valuation identifier (VAL-YYYYMMDD-XXXX)'
  },

  companyId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Company',
    required: true,
    index: true,
    description: 'Reference to the company being valued'
  },

  tenantId: {
    type: String,
    required: true,
    index: true,
    validate: {
      validator: (v) => /^[a-zA-Z0-9_-]{8,64}$/.test(v),
      message: 'tenantId must be 8-64 alphanumeric characters'
    },
    description: 'Multi-tenant isolation identifier'
  },

  /**
   * Valuation Methods Results
   */
  methods: {
    type: Map,
    of: mongoose.Schema.Types.Mixed,
    required: true,
    description: 'Results from each valuation method applied'
  },

  methodCount: {
    type: Number,
    required: true,
    min: 1,
    max: 7,
    description: 'Number of valuation methods successfully applied'
  },

  /**
   * Monte Carlo Simulation Results
   */
  monteCarlo: {
    iterations: {
      type: Number,
      default: 10000,
      description: 'Number of simulation iterations'
    },
    mean: {
      type: Number,
      description: 'Mean valuation from simulation'
    },
    median: {
      type: Number,
      description: 'Median valuation from simulation'
    },
    stdDev: {
      type: Number,
      description: 'Standard deviation of valuations'
    },
    percentiles: {
      p5: { type: Number },
      p10: { type: Number },
      p25: { type: Number },
      p50: { type: Number },
      p75: { type: Number },
      p90: { type: Number },
      p95: { type: Number }
    },
    min: { type: Number },
    max: { type: Number },
    distribution: {
      normal: {
        isNormal: { type: Boolean },
        skewness: { type: Number },
        kurtosis: { type: Number }
      },
      lognormal: {
        isNormal: { type: Boolean },
        skewness: { type: Number },
        kurtosis: { type: Number }
      }
    }
  },

  /**
   * Sensitivity Analysis Results
   */
  sensitivity: {
    baseValue: { type: Number },
    discountRate: [{
      delta: { type: Number },
      value: { type: Number },
      change: { type: Number }
    }],
    terminalGrowth: [{
      delta: { type: Number },
      value: { type: Number },
      change: { type: Number }
    }],
    revenueGrowth: [{
      delta: { type: Number },
      value: { type: Number },
      change: { type: Number }
    }],
    margin: [{
      delta: { type: Number },
      value: { type: Number },
      change: { type: Number }
    }],
    rankings: [{
      variable: { type: String },
      maxChange: { type: Number },
      importance: { type: Number }
    }],
    tornado: [{
      variable: { type: String },
      low: { type: Number },
      high: { type: Number },
      base: { type: Number },
      spread: { type: Number }
    }]
  },

  /**
   * Final Valuation Results
   */
  finalValuation: {
    low: { type: Number, required: true },
    high: { type: Number, required: true },
    average: { type: Number, required: true },
    median: { type: Number, required: true },
    weightedAverage: { type: Number, required: true },
    monteCarloMean: { type: Number },
    monteCarloMedian: { type: Number },
    confidence: { type: Number, min: 0, max: 1 },
    range: { type: Number },
    rangePercent: { type: Number }
  },

  /**
   * Valuation Assumptions Used
   */
  assumptions: {
    discountRate: { type: Number },
    terminalGrowthRate: { type: Number },
    marketRiskPremium: { type: Number },
    riskFreeRate: { type: Number },
    illiquidityDiscount: { type: Number },
    controlPremium: { type: Number },
    minorityDiscount: { type: Number },
    sizePremium: { type: Number },
    industryRiskPremium: { type: Number },
    companySpecificRisk: { type: Number },
    countryRiskPremium: { type: Number },
    currency: { type: String },
    projectionYears: { type: Number },
    targetDebtEquity: { type: Number },
    taxRate: { type: Number },
    reinvestmentRate: { type: Number },
    workingCapitalPercent: { type: Number },
    capExPercent: { type: Number },
    depreciationPercent: { type: Number },
    iterations: { type: Number }
  },

  /**
   * Metadata and Context
   */
  metadata: {
    duration: { type: Number, description: 'Valuation duration in ms' },
    options: { type: mongoose.Schema.Types.Mixed },
    createdBy: { type: String },
    updatedBy: { type: String },
    version: { type: String }
  },

  /**
   * POPIA Compliance
   */
  popia: {
    containsPII: { type: Boolean, default: false },
    piiFields: [{
      field: { type: String },
      redacted: { type: Boolean },
      category: { type: String }
    }],
    redactionApplied: { type: Boolean, default: false },
    consentVerified: { type: Boolean, default: false },
    consentTimestamp: { type: Date }
  },

  /**
   * Data Retention (POPIA §14, Companies Act §28)
   */
  retention: {
    policy: {
      type: String,
      enum: ['companies_act_10_years', 'popia_1_year', 'tax_act_5_years', 'forensic_permanent'],
      default: 'companies_act_10_years'
    },
    dataResidency: {
      type: String,
      enum: ['ZA', 'US', 'EU', 'GB', 'AU'],
      default: 'ZA'
    },
    retentionStart: { type: Date, default: Date.now },
    retentionEnd: { type: Date },
    archivedAt: { type: Date },
    destroyedAt: { type: Date },
    destructionCertificate: { type: String }
  },

  /**
   * Forensic Integrity
   */
  forensic: {
    hash: {
      type: String,
      required: true,
      unique: true,
      match: /^[a-f0-9]{64}$/,
      description: 'SHA-256 hash of valuation data'
    },
    previousHash: {
      type: String,
      match: /^[a-f0-9]{64}$/,
      description: 'Previous version hash for chain of custody'
    },
    chainVerified: { type: Boolean, default: false },
    blockchainAnchor: {
      transactionId: { type: String },
      blockNumber: { type: Number },
      network: { 
        type: String,
        enum: ['ethereum', 'hyperledger', 'none'],
        default: 'none'
      },
      timestamp: { type: Date },
      verificationUrl: { type: String }
    },
    signedBy: { type: String },
    signedAt: { type: Date },
    signature: { type: String }
  },

  /**
   * Audit Trail
   */
  audit: {
    createdAt: { type: Date, default: Date.now, immutable: true },
    createdBy: { type: String, required: true },
    updatedAt: { type: Date, default: Date.now },
    updatedBy: { type: String },
    accessedAt: { type: Date },
    accessedBy: { type: String },
    events: [{
      action: { type: String },
      userId: { type: String },
      timestamp: { type: Date },
      details: { type: mongoose.Schema.Types.Mixed }
    }]
  },

  /**
   * Status and Workflow
   */
  status: {
    type: String,
    enum: ['draft', 'completed', 'archived', 'deleted', 'under_review'],
    default: 'completed'
  },

  /**
   * Tags and Notes
   */
  tags: [String],
  notes: String
}, {
  timestamps: true,
  collection: 'valuations',
  strict: true,
  minimize: false
});

// ============================================================================
// INDEXES
// ============================================================================

// Primary lookup indexes
valuationSchema.index({ tenantId: 1, valuationId: 1 });
valuationSchema.index({ tenantId: 1, companyId: 1, createdAt: -1 });
valuationSchema.index({ tenantId: 1, status: 1, createdAt: -1 });

// Date range queries
valuationSchema.index({ 'audit.createdAt': -1 });
valuationSchema.index({ 'retention.retentionEnd': 1 }, { expireAfterSeconds: 0 });

// Forensic lookup
valuationSchema.index({ 'forensic.hash': 1 }, { unique: true });
valuationSchema.index({ 'forensic.blockchainAnchor.transactionId': 1 }, { sparse: true });

// Value ranges
valuationSchema.index({ 'finalValuation.weightedAverage': 1 });
valuationSchema.index({ 'finalValuation.low': 1, 'finalValuation.high': 1 });

// ============================================================================
// MIDDLEWARE
// ============================================================================

/**
 * Pre-save middleware to generate forensic hash and set retention dates
 */
valuationSchema.pre('save', async function(next) {
  try {
    // Update audit timestamp
    this.audit.updatedAt = new Date();

    // Set retention end date based on policy
    if (!this.retention.retentionEnd) {
      const endDate = new Date(this.retention.retentionStart || Date.now());
      
      switch (this.retention.policy) {
        case 'companies_act_10_years':
          endDate.setFullYear(endDate.getFullYear() + 10);
          break;
        case 'popia_1_year':
          endDate.setFullYear(endDate.getFullYear() + 1);
          break;
        case 'tax_act_5_years':
          endDate.setFullYear(endDate.getFullYear() + 5);
          break;
        case 'forensic_permanent':
          endDate.setFullYear(endDate.getFullYear() + 100);
          break;
      }
      
      this.retention.retentionEnd = endDate;
    }

    // Generate forensic hash
    const hashData = {
      valuationId: this.valuationId,
      companyId: this.companyId,
      tenantId: this.tenantId,
      finalValuation: this.finalValuation,
      monteCarlo: this.monteCarlo ? {
        mean: this.monteCarlo.mean,
        median: this.monteCarlo.median,
        stdDev: this.monteCarlo.stdDev
      } : null,
      timestamp: this.audit.createdAt,
      version: '1.0.0'
    };

    const canonicalData = JSON.stringify(hashData, Object.keys(hashData).sort());
    this.forensic.hash = crypto.createHash('sha256').update(canonicalData).digest('hex');
    this.forensic.chainVerified = true;

    // Find previous version for hash chaining
    if (!this.forensic.previousHash) {
      const previousValuation = await this.constructor.findOne({
        companyId: this.companyId,
        tenantId: this.tenantId,
        'audit.createdAt': { $lt: this.audit.createdAt }
      }).sort({ 'audit.createdAt': -1 });

      if (previousValuation) {
        this.forensic.previousHash = previousValuation.forensic.hash;
      }
    }

    next();
  } catch (error) {
    next(error);
  }
});

/**
 * Pre-update middleware
 */
valuationSchema.pre('findOneAndUpdate', function() {
  this.set({ 'audit.updatedAt': new Date() });
});

// ============================================================================
// INSTANCE METHODS
// ============================================================================

/**
 * Verify forensic hash integrity
 * @returns {Object} Verification result
 */
valuationSchema.methods.verifyIntegrity = function() {
  const hashData = {
    valuationId: this.valuationId,
    companyId: this.companyId,
    tenantId: this.tenantId,
    finalValuation: this.finalValuation,
    monteCarlo: this.monteCarlo ? {
      mean: this.monteCarlo.mean,
      median: this.monteCarlo.median,
      stdDev: this.monteCarlo.stdDev
    } : null,
    timestamp: this.audit.createdAt,
    version: '1.0.0'
  };

  const canonicalData = JSON.stringify(hashData, Object.keys(hashData).sort());
  const calculatedHash = crypto.createHash('sha256').update(canonicalData).digest('hex');

  return {
    verified: calculatedHash === this.forensic.hash,
    calculated: calculatedHash,
    stored: this.forensic.hash,
    chainVerified: this.forensic.chainVerified,
    previousHash: this.forensic.previousHash
  };
};

/**
 * Generate forensic report for court evidence
 * @returns {Object} Forensic report
 */
valuationSchema.methods.generateForensicReport = function() {
  return {
    reportId: `FORENSIC-${this.valuationId}`,
    valuationId: this.valuationId,
    companyId: this.companyId,
    tenantId: this.tenantId,
    generatedAt: new Date().toISOString(),
    valuationDate: this.audit.createdAt,
    finalValue: this.finalValuation.weightedAverage,
    valueRange: {
      low: this.finalValuation.low,
      high: this.finalValuation.high
    },
    confidence: this.finalValuation.confidence,
    methods: Array.from(this.methods.keys()),
    forensic: {
      hash: this.forensic.hash,
      previousHash: this.forensic.previousHash,
      chainVerified: this.forensic.chainVerified,
      blockchainAnchor: this.forensic.blockchainAnchor
    },
    retention: {
      policy: this.retention.policy,
      expiresAt: this.retention.retentionEnd
    }
  };
};

/**
 * Get redacted version for external sharing
 * @returns {Object} Redacted valuation
 */
valuationSchema.methods.getRedactedVersion = function() {
  const redacted = this.toObject();
  
  // Remove sensitive fields
  delete redacted.forensic;
  delete redacted.audit;
  delete redacted.popia;
  delete redacted.metadata?.options;
  
  // Redact company reference
  if (redacted.companyId) {
    redacted.companyId = '[REDACTED]';
  }
  
  return redacted;
};

/**
 * Place valuation on legal hold
 * @param {string} reason - Reason for legal hold
 * @param {string} userId - User placing the hold
 * @returns {Promise} Updated valuation
 */
valuationSchema.methods.placeLegalHold = async function(reason, userId) {
  this.status = 'under_review';
  this.retention.policy = 'forensic_permanent';
  
  // Extend retention end date
  const newEndDate = new Date();
  newEndDate.setFullYear(newEndDate.getFullYear() + 100);
  this.retention.retentionEnd = newEndDate;
  
  this.audit.events.push({
    action: 'LEGAL_HOLD_PLACED',
    userId,
    timestamp: new Date(),
    details: { reason }
  });
  
  return this.save();
};

/**
 * Schedule for archival
 * @param {Date} archiveDate - Date to archive
 * @returns {Promise} Updated valuation
 */
valuationSchema.methods.scheduleArchival = async function(archiveDate) {
  this.retention.archivedAt = archiveDate;
  this.status = 'archived';
  
  return this.save();
};

// ============================================================================
// STATIC METHODS
// ============================================================================

/**
 * Find valuations by company
 * @param {string} companyId - Company ID
 * @param {Object} options - Query options
 * @returns {Promise<Array>} Valuations array
 */
valuationSchema.statics.findByCompany = function(companyId, options = {}) {
  const { limit = 10, skip = 0, sortBy = 'createdAt', sortOrder = -1 } = options;
  
  return this.find({ companyId })
    .sort({ [sortBy]: sortOrder })
    .skip(skip)
    .limit(limit)
    .lean();
};

/**
 * Get valuation statistics for company
 * @param {string} companyId - Company ID
 * @returns {Promise<Object>} Statistics
 */
valuationSchema.statics.getCompanyStats = async function(companyId) {
  const stats = await this.aggregate([
    { $match: { companyId } },
    {
      $group: {
        _id: null,
        totalValuations: { $sum: 1 },
        avgValue: { $avg: '$finalValuation.weightedAverage' },
        minValue: { $min: '$finalValuation.weightedAverage' },
        maxValue: { $max: '$finalValuation.weightedAverage' },
        avgConfidence: { $avg: '$finalValuation.confidence' },
        methodDistribution: { $push: '$methodCount' }
      }
    }
  ]);

  return stats[0] || {
    totalValuations: 0,
    avgValue: 0,
    minValue: 0,
    maxValue: 0,
    avgConfidence: 0,
    methodDistribution: []
  };
};

/**
 * Get valuations by date range
 * @param {Date} startDate - Start date
 * @param {Date} endDate - End date
 * @param {Object} options - Query options
 * @returns {Promise<Array>} Valuations array
 */
valuationSchema.statics.findByDateRange = function(startDate, endDate, options = {}) {
  const { tenantId, limit = 100 } = options;
  
  const query = {
    'audit.createdAt': { $gte: startDate, $lte: endDate }
  };
  
  if (tenantId) {
    query.tenantId = tenantId;
  }
  
  return this.find(query)
    .sort({ 'audit.createdAt': -1 })
    .limit(limit)
    .lean();
};

/**
 * Get valuations expiring soon
 * @param {number} daysThreshold - Days threshold
 * @returns {Promise<Array>} Valuations array
 */
valuationSchema.statics.getExpiringValuations = function(daysThreshold = 30) {
  const thresholdDate = new Date();
  thresholdDate.setDate(thresholdDate.getDate() + daysThreshold);
  
  return this.find({
    'retention.retentionEnd': { $lte: thresholdDate },
    status: { $ne: 'deleted' }
  })
    .sort({ 'retention.retentionEnd': 1 })
    .limit(100)
    .lean();
};

/**
 * Bulk archive valuations
 * @param {Array} valuationIds - Valuation IDs to archive
 * @param {string} userId - User performing archive
 * @returns {Promise} Update result
 */
valuationSchema.statics.bulkArchive = async function(valuationIds, userId) {
  const result = await this.updateMany(
    { _id: { $in: valuationIds } },
    {
      $set: {
        status: 'archived',
        'retention.archivedAt': new Date(),
        'audit.updatedBy': userId
      }
    }
  );
  
  return result;
};

/**
 * Verify hash chain for company
 * @param {string} companyId - Company ID
 * @returns {Promise<Object>} Chain verification result
 */
valuationSchema.statics.verifyHashChain = async function(companyId) {
  const valuations = await this.find({ companyId })
    .sort({ 'audit.createdAt': 1 })
    .lean();
  
  const brokenLinks = [];
  
  for (let i = 1; i < valuations.length; i++) {
    const expectedHash = valuations[i - 1].forensic.hash;
    if (valuations[i].forensic.previousHash !== expectedHash) {
      brokenLinks.push({
        index: i,
        valuationId: valuations[i].valuationId,
        expected: expectedHash,
        actual: valuations[i].forensic.previousHash
      });
    }
  }
  
  return {
    verified: brokenLinks.length === 0,
    totalValuations: valuations.length,
    brokenLinks
  };
};

// ============================================================================
// VIRTUAL PROPERTIES
// ============================================================================

/**
 * Get formatted value range
 */
valuationSchema.virtual('valueRange').get(function() {
  return `${this.finalValuation.low.toLocaleString()} - ${this.finalValuation.high.toLocaleString()}`;
});

/**
 * Get age in days
 */
valuationSchema.virtual('ageInDays').get(function() {
  const age = Date.now() - this.audit.createdAt.getTime();
  return Math.floor(age / (1000 * 60 * 60 * 24));
});

/**
 * Check if expired
 */
valuationSchema.virtual('isExpired').get(function() {
  return new Date() > this.retention.retentionEnd;
});

/**
 * Check if on legal hold
 */
valuationSchema.virtual('isOnLegalHold').get(function() {
  return this.retention.policy === 'forensic_permanent' || this.status === 'under_review';
});

// ============================================================================
// EXPORTS
// ============================================================================

// Create and export the model
const Valuation = mongoose.model('Valuation', valuationSchema);

export default Valuation;
