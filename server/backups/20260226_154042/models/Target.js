/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════════════════╗
  ║ TARGET MODEL - ACQUISITION TARGET WITH QUANTUM FEATURE VECTORS                        ║
  ║ [Production Grade | 127-Dimensional Analysis | Real-time Scoring]                     ║
  ╚═══════════════════════════════════════════════════════════════════════════════════════╝*/

import mongoose from "mongoose";
import crypto from "crypto";

const targetSchema = new mongoose.Schema({
  targetId: {
    type: String,
    required: true,
    unique: true,
    default: () => `TGT-${crypto.randomBytes(4).toString('hex').toUpperCase()}`
  },

  tenantId: {
    type: String,
    required: true,
    index: true
  },

  name: {
    type: String,
    required: true,
    trim: true
  },

  registrationNumber: {
    type: String,
    required: true,
    unique: true,
    validate: {
      validator: v => /^\d{4}\/\d{6}\/\d{2}$/.test(v),
      message: 'Invalid company registration number format'
    }
  },

  jurisdiction: {
    type: String,
    required: true,
    enum: ['ZA', 'NA', 'BW', 'KE', 'NG', 'GB', 'EU', 'US', 'CN', 'IN']
  },

  status: {
    type: String,
    enum: ['identified', 'screened', 'contacted', 'nda_signed', 'dd_in_progress', 
           'offered', 'negotiating', 'agreed', 'withdrawn', 'acquired'],
    default: 'identified'
  },

  // Quantum Feature Vectors (127 dimensions)
  quantumVectors: {
    financial: mongoose.Schema.Types.Mixed,  // 32 dimensions
    operational: mongoose.Schema.Types.Mixed, // 28 dimensions
    market: mongoose.Schema.Types.Mixed,      // 24 dimensions
    technological: mongoose.Schema.Types.Mixed, // 18 dimensions
    humanCapital: mongoose.Schema.Types.Mixed, // 15 dimensions
    regulatory: mongoose.Schema.Types.Mixed,   // 10 dimensions
    magnitude: Number,
    lastCalculated: Date
  },

  // Financial Data
  financials: {
    lastFiscalYear: Number,
    currency: { type: String, default: 'ZAR' },
    revenue: {
      current: Number,
      forecast: [{ year: Number, value: Number }],
      growth: Number,
      historical: [Number]
    },
    ebitda: {
      current: Number,
      margin: Number,
      historical: [Number]
    },
    netIncome: Number,
    totalAssets: Number,
    totalLiabilities: Number,
    equity: Number,
    cash: Number,
    debt: Number,
    workingCapital: Number,
    capex: Number,
    fcf: Number
  },

  // Market Data
  market: {
    sector: String,
    industry: String,
    subIndustry: String,
    marketShare: Number,
    competitors: [String],
    customerConcentration: [{
      customerId: String,
      percentage: Number
    }],
    geographicPresence: [String],
    marketGrowth: Number,
    marketPosition: String
  },

  // Operational Data
  operational: {
    employees: Number,
    locations: [String],
    facilities: [{
      type: String,
      location: String,
      size: Number,
      owned: Boolean
    }],
    capacity: mongoose.Schema.Types.Mixed,
    utilization: Number,
    suppliers: [String],
    patents: [{
      patentNumber: String,
      filingDate: Date,
      expiryDate: Date,
      jurisdiction: String
    }]
  },

  // Management Data
  management: {
    ceo: {
      name: String,
      tenure: Number,
      age: Number,
      background: String
    },
    cfo: {
      name: String,
      tenure: Number
    },
    boardSize: Number,
    independentDirectors: Number,
    keyExecutives: [{
      name: String,
      title: String,
      tenure: Number,
      equity: Number
    }],
    sentiment: {
      score: Number,
      confidence: Number,
      keyPhrases: [String],
      concerns: [String],
      lastAnalyzed: Date
    }
  },

  // Cultural DNA
  culturalDNA: {
    leadership: mongoose.Schema.Types.Mixed,
    communication: mongoose.Schema.Types.Mixed,
    decisionMaking: mongoose.Schema.Types.Mixed,
    riskTolerance: Number,
    innovationIndex: Number,
    hierarchyScore: Number,
    values: [String],
    compatibility: {
      withAcquirer: mongoose.Schema.Types.ObjectId,
      score: Number,
      dimensions: mongoose.Schema.Types.Mixed
    }
  },

  // Synergy Scores
  synergyScores: [{
    acquirerId: mongoose.Schema.Types.ObjectId,
    score: Number,
    confidence: Number,
    breakdown: mongoose.Schema.Types.Mixed,
    calculatedAt: Date
  }],

  // Deal History
  dealHistory: [{
    dealId: mongoose.Schema.Types.ObjectId,
    acquirer: String,
    status: String,
    date: Date,
    value: Number
  }],

  // Source Information
  source: {
    type: { type: String, enum: ['database', 'scraped', 'network', 'inbound'] },
    url: String,
    confidence: Number,
    lastVerified: Date
  },

  // Scoring Metadata
  scoringMetadata: {
    lastScored: Date,
    scoringMethod: String,
    quantumIterations: Number,
    convergenceScore: Number,
    featuresUsed: [String]
  },

  forensicHash: String,
  previousHash: String,
  chainPosition: Number
}, {
  timestamps: true,
  collection: 'targets'
});

// Indexes
targetSchema.index({ tenantId: 1, status: 1 });
targetSchema.index({ 'financials.revenue.current': -1 });
targetSchema.index({ 'quantumVectors.magnitude': -1 });
targetSchema.index({ 'synergyScores.score': -1 });
targetSchema.index({ registrationNumber: 1 });

// Pre-save middleware
targetSchema.pre('save', async function(next) {
  if (this.isModified('quantumVectors') || !this.quantumVectors?.magnitude) {
    this.quantumVectors.magnitude = Math.sqrt(
      Object.values(this.quantumVectors || {}).reduce((sum, vec) => {
        if (typeof vec === 'object') {
          return sum + Object.values(vec).reduce((s, v) => s + (v * v), 0);
        }
        return sum;
      }, 0)
    );
    this.quantumVectors.lastCalculated = new Date();
  }

  const canonicalData = JSON.stringify({
    targetId: this.targetId,
    name: this.name,
    registrationNumber: this.registrationNumber,
    jurisdiction: this.jurisdiction,
    status: this.status,
    updatedAt: new Date(),
    previousHash: this.previousHash
  });

  this.forensicHash = crypto
    .createHash('sha256')
    .update(canonicalData)
    .digest('hex');

  next();
});

// Methods
targetSchema.methods.calculateSimilarity = function(otherTarget) {
  // Cosine similarity between quantum vectors
  const dotProduct = Object.keys(this.quantumVectors).reduce((sum, key) => {
    if (typeof this.quantumVectors[key] === 'object' && otherTarget.quantumVectors[key]) {
      return sum + Object.keys(this.quantumVectors[key]).reduce((s, subKey) => {
        return s + (this.quantumVectors[key][subKey] || 0) * (otherTarget.quantumVectors[key][subKey] || 0);
      }, 0);
    }
    return sum;
  }, 0);

  return dotProduct / (this.quantumVectors.magnitude * otherTarget.quantumVectors.magnitude);
};

targetSchema.methods.updateSynergyScore = function(acquirerId, score, breakdown) {
  this.synergyScores.push({
    acquirerId,
    score,
    breakdown,
    confidence: this.calculateConfidence(breakdown),
    calculatedAt: new Date()
  });

  // Keep only last 10 scores per acquirer
  this.synergyScores = this.synergyScores
    .sort((a, b) => b.calculatedAt - a.calculatedAt)
    .slice(0, 10);
};

targetSchema.methods.calculateConfidence = function(breakdown) {
  // Calculate confidence based on data completeness
  const requiredFields = ['financial', 'operational', 'market', 'management'];
  const presentFields = requiredFields.filter(f => breakdown[f] !== undefined);
  return (presentFields.length / requiredFields.length) * 100;
};

const Target = mongoose.model('Target', targetSchema);
export default Target;
