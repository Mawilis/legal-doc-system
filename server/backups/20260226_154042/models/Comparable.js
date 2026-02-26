/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ WILSY OS - COMPARABLE COMPANY MODEL v1.0                                  ║
  ║ [Valuation Multiples | Industry Benchmarks | Market Data]                ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

/**
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/Comparable.js
 * VERSION: 1.0.0
 * CREATED: 2026-02-24
 */

import mongoose from "mongoose";
import crypto from "crypto";

// ============================================================================
// ENUMS & CONSTANTS
// ============================================================================

export const COMPARABLE_MARKETS = {
  JSE: 'jse',
  ALTX: 'altx',
  NYSE: 'nyse',
  NASDAQ: 'nasdaq',
  LSE: 'lse',
  AIM: 'aim',
  TSX: 'tsx',
  ASX: 'asx',
  HKEX: 'hkex',
  SSE: 'sse',
  BSE: 'bse',
  EURONEXT: 'euronext',
  DEUTSCHE_BORSE: 'deutsche_borse',
  SIX: 'six',
  TSE: 'tse',
  KOSPI: 'kospi',
  OTC: 'otc',
  PRIVATE: 'private',
};

export const COMPARABLE_SOURCES = {
  BLOOMBERG: 'bloomberg',
  REUTERS: 'reuters',
  S_P: 's_and_p',
  MSCI: 'msci',
  FTSE: 'ftse',
  JSE: 'jse',
  COMPANY_REPORT: 'company_report',
  MANUAL: 'manual',
  API: 'api',
  WEB_SCRAPE: 'web_scrape',
};

export const COMPARABLE_CURRENCY = {
  ZAR: 'ZAR',
  USD: 'USD',
  EUR: 'EUR',
  GBP: 'GBP',
  JPY: 'JPY',
  CNY: 'CNY',
  AUD: 'AUD',
  CAD: 'CAD',
  CHF: 'CHF',
  HKD: 'HKD',
};

export const CONFIDENCE_LEVELS = {
  HIGH: 'high',
  MEDIUM: 'medium',
  LOW: 'low',
  ESTIMATED: 'estimated',
};

// ============================================================================
// SUB-SCHEMAS
// ============================================================================

const companyProfileSchema = new mongoose.Schema({
  name: { type: String, required: true, trim: true, index: true },
  ticker: { type: String, uppercase: true, trim: true, sparse: true, index: true },
  isin: {
    type: String,
    uppercase: true,
    trim: true,
    sparse: true,
    validate: { validator: (v) => !v || /^[A-Z]{2}[A-Z0-9]{9}\d$/.test(v) }
  },
  cusip: { type: String, uppercase: true, trim: true, sparse: true },
  sedol: { type: String, uppercase: true, trim: true, sparse: true },
  market: { type: String, enum: Object.values(COMPARABLE_MARKETS), required: true },
  country: { type: String, default: 'ZA', uppercase: true, maxlength: 2 },
  sector: { type: String, required: true, index: true },
  industry: { type: String, required: true, index: true },
  subIndustry: String,
  description: String,
  website: String,
  foundedYear: Number,
  employees: Number,
  headquarters: String,
  businessDescription: String,
  businessModel: String,
  competitiveAdvantages: [String],
  keyRisks: [String],
});

const financialMultiplesSchema = new mongoose.Schema({
  asOfDate: { type: Date, required: true },
  fiscalYear: { type: Number, required: true },
  currency: { type: String, enum: Object.values(COMPARABLE_CURRENCY), required: true, default: 'ZAR' },

  marketCap: { value: { type: Number, required: true }, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'high' } },
  enterpriseValue: { value: { type: Number, required: true }, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'high' } },

  peRatio: { ttm: Number, forward: Number, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'medium' } },
  pegRatio: { value: Number, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'medium' } },
  psRatio: { value: Number, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'medium' } },
  pbRatio: { value: Number, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'medium' } },
  pcfRatio: { value: Number, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'medium' } },

  evRevenue: { ttm: Number, forward: Number, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'medium' } },
  evEbitda: { ttm: Number, forward: Number, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'medium' } },
  evEbit: { ttm: Number, forward: Number, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'medium' } },
  evFcf: { ttm: Number, forward: Number, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'medium' } },
  evInvestedCapital: { value: Number, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'medium' } },

  dividendYield: { value: Number, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'medium' } },
  buybackYield: { value: Number, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'medium' } },
  fcfYield: { value: Number, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'medium' } },

  revenueGrowth: { qoq: Number, yoy: Number, threeYearCAGR: Number, fiveYearCAGR: Number, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'medium' } },
  ebitdaGrowth: { yoy: Number, threeYearCAGR: Number, fiveYearCAGR: Number, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'medium' } },
  epsGrowth: { yoy: Number, threeYearCAGR: Number, fiveYearCAGR: Number, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'medium' } },

  grossMargin: { value: Number, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'high' } },
  operatingMargin: { value: Number, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'high' } },
  netMargin: { value: Number, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'high' } },
  ebitdaMargin: { value: Number, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'high' } },
  fcfMargin: { value: Number, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'high' } },

  roe: { value: Number, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'medium' } },
  roa: { value: Number, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'medium' } },
  roce: { value: Number, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'medium' } },
  roic: { value: Number, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'medium' } },

  currentRatio: { value: Number, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'high' } },
  quickRatio: { value: Number, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'high' } },
  debtToEquity: { value: Number, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'high' } },
  interestCover: { value: Number, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'medium' } },

  cashPerShare: { value: Number, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'high' } },
  assetTurnover: { value: Number, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'medium' } },
  inventoryTurnover: { value: Number, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'medium' } },
  daysSalesOutstanding: { value: Number, confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'medium' } },
});

const tradingDataSchema = new mongoose.Schema({
  asOfDate: { type: Date, required: true },
  price: { value: { type: Number, required: true }, currency: { type: String, enum: Object.values(COMPARABLE_CURRENCY), default: 'ZAR' } },
  sharesOutstanding: Number,
  volume: { daily: Number, average30Day: Number, average90Day: Number },
  priceRange: { dayLow: Number, dayHigh: Number, week52Low: Number, week52High: Number },
  beta: { value: Number, period: { type: String, enum: ['1y', '3y', '5y'], default: '5y' } },
  volatility: { daily: Number, annualized: Number },
  shortInterest: { shares: Number, percentFloat: Number, ratio: Number },
  analystCoverage: { count: Number, buy: Number, hold: Number, sell: Number, targetPrice: Number },
  liquidity: { bid: Number, ask: Number, spread: Number, depth: Number }
});

const sourceMetadataSchema = new mongoose.Schema({
  source: { type: String, enum: Object.values(COMPARABLE_SOURCES), required: true },
  sourceId: String,
  sourceUrl: String,
  sourceName: String,
  retrievedAt: { type: Date, default: Date.now },
  dataFreshness: { type: String, enum: ['real_time', 'daily', 'weekly', 'monthly', 'quarterly', 'annual'], required: true },
  confidence: { type: String, enum: Object.values(CONFIDENCE_LEVELS), default: 'medium' },
  notes: String,
  rawData: mongoose.Schema.Types.Mixed
});

const peerComparisonSchema = new mongoose.Schema({
  metric: String,
  companyValue: Number,
  peerMedian: Number,
  peerMean: Number,
  peerMin: Number,
  peerMax: Number,
  percentileRank: Number,
  zScore: Number,
  interpretation: String
});

// ============================================================================
// MAIN SCHEMA
// ============================================================================

const comparableSchema = new mongoose.Schema({
  comparableId: {
    type: String,
    required: true,
    unique: true,
    index: true,
    default: () => `CMP-${Date.now()}-${crypto.randomBytes(4).toString('hex')}`
  },

  tenantId: {
    type: String,
    required: true,
    index: true,
    validate: { validator: (v) => /^[a-zA-Z0-9_-]{8,64}$/.test(v) }
  },

  company: { type: companyProfileSchema, required: true },
  financials: [financialMultiplesSchema],
  tradingData: [tradingDataSchema],
  sources: [sourceMetadataSchema],

  peerGroup: { type: String, index: true, required: true },
  peerGroupDescription: String,
  inclusionCriteria: [String],
  exclusionCriteria: [String],

  comparabilityScore: { type: Number, min: 0, max: 100, default: 50 },
  similarityScore: { type: Number, min: 0, max: 100, default: 50 },

  isActive: { type: Boolean, default: true, index: true },
  isPublic: { type: Boolean, default: true },

  tags: [String],
  notes: String,
  peerComparisons: [peerComparisonSchema],

  statistics: {
    count: { type: Number, default: 0 },
    averageMarketCap: Number,
    medianMarketCap: Number,
    averagePE: Number,
    medianPE: Number,
    averageEVEBITDA: Number,
    medianEVEBITDA: Number,
    asOfDate: Date
  },

  retention: {
    policy: { type: String, enum: ['market_data_1_year', 'companies_act_10_years', 'forensic_permanent'], default: 'market_data_1_year' },
    dataResidency: { type: String, enum: ['ZA', 'US', 'EU', 'GB', 'AU'], default: 'ZA' },
    retentionStart: { type: Date, default: Date.now },
    retentionEnd: Date
  },

  forensic: {
    hash: { type: String, required: true, unique: true, match: /^[a-f0-9]{64}$/ },
    previousHash: { type: String, match: /^[a-f0-9]{64}$/ },
    chainVerified: { type: Boolean, default: false }
  },

  audit: {
    createdAt: { type: Date, default: Date.now, immutable: true },
    createdBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    updatedAt: { type: Date, default: Date.now },
    updatedBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    changeHistory: [{
      field: String,
      oldValue: mongoose.Schema.Types.Mixed,
      newValue: mongoose.Schema.Types.Mixed,
      changedBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
      changedAt: Date,
      reason: String
    }]
  },

  version: { type: Number, default: 1 }
}, {
  timestamps: true,
  collection: 'comparables',
  strict: true,
  minimize: false,
  toJSON: { virtuals: true, transform: (doc, ret) => { delete ret.forensic; return ret; } }
});

// ============================================================================
// HELPER STATIC METHODS (used by both middleware & static/instance methods)
// ============================================================================

comparableSchema.statics.calculateAverage = function (numbers) {
  if (!numbers || numbers.length === 0) return 0;
  const sum = numbers.reduce((a, b) => a + b, 0);
  return sum / numbers.length;
};

comparableSchema.statics.calculateMedian = function (numbers) {
  if (!numbers || numbers.length === 0) return 0;
  const sorted = [...numbers].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
};

comparableSchema.statics.calculateStdDev = function (numbers) {
  if (!numbers || numbers.length === 0) return 0;
  const mean = this.calculateAverage(numbers);
  const squaredDiffs = numbers.map(v => Math.pow(v - mean, 2));
  const variance = this.calculateAverage(squaredDiffs);
  return Math.sqrt(variance);
};

// ============================================================================
// INDEXES
// ============================================================================

comparableSchema.index({ tenantId: 1, comparableId: 1 });
comparableSchema.index({ tenantId: 1, 'company.sector': 1, 'company.industry': 1 });
comparableSchema.index({ tenantId: 1, peerGroup: 1 });
comparableSchema.index({ tenantId: 1, isActive: 1 });
comparableSchema.index({ 'company.ticker': 1 });
comparableSchema.index({ 'company.isin': 1 });
comparableSchema.index({ 'financials.asOfDate': -1 });
comparableSchema.index({ 'retention.retentionEnd': 1 }, { expireAfterSeconds: 0 });
comparableSchema.index({ 'forensic.hash': 1 }, { unique: true });

comparableSchema.index({
  'company.name': 'text',
  'company.ticker': 'text',
  'company.sector': 'text',
  'company.industry': 'text',
  tags: 'text'
}, {
  weights: { 'company.name': 10, 'company.ticker': 8, 'company.sector': 5, 'company.industry': 5, tags: 3 },
  name: 'comparable_search_index'
});

// ============================================================================
// MIDDLEWARE
// ============================================================================

comparableSchema.pre('save', async function (next) {
  try {
    this.audit.updatedAt = new Date();

    if (!this.retention.retentionEnd) {
      const endDate = new Date(this.retention.retentionStart || Date.now());
      switch (this.retention.policy) {
        case 'market_data_1_year': endDate.setFullYear(endDate.getFullYear() + 1); break;
        case 'companies_act_10_years': endDate.setFullYear(endDate.getFullYear() + 10); break;
        case 'forensic_permanent': endDate.setFullYear(endDate.getFullYear() + 100); break;
      }
      this.retention.retentionEnd = endDate;
    }

    if (this.financials && this.financials.length > 0) {
      this.statistics = {
        count: this.financials.length,
        averageMarketCap: this.constructor.calculateAverage(this.financials.map(f => f.marketCap?.value).filter(v => v != null)),
        medianMarketCap: this.constructor.calculateMedian(this.financials.map(f => f.marketCap?.value).filter(v => v != null)),
        averagePE: this.constructor.calculateAverage(this.financials.map(f => f.peRatio?.ttm).filter(v => v != null)),
        medianPE: this.constructor.calculateMedian(this.financials.map(f => f.peRatio?.ttm).filter(v => v != null)),
        averageEVEBITDA: this.constructor.calculateAverage(this.financials.map(f => f.evEbitda?.ttm).filter(v => v != null)),
        medianEVEBITDA: this.constructor.calculateMedian(this.financials.map(f => f.evEbitda?.ttm).filter(v => v != null)),
        asOfDate: new Date()
      };
    }

    // Forensic hash
    const hashData = {
      comparableId: this.comparableId,
      tenantId: this.tenantId,
      companyName: this.company.name,
      ticker: this.company.ticker,
      peerGroup: this.peerGroup,
      latestFinancials: this.financials?.[0],
      version: this.version
    };
    const canonicalData = JSON.stringify(hashData, Object.keys(hashData).sort());
    this.forensic.hash = crypto.createHash('sha256').update(canonicalData).digest('hex');

    if (!this.forensic.previousHash) {
      const prev = await this.constructor.findOne({
        'company.ticker': this.company.ticker,
        tenantId: this.tenantId,
        version: this.version - 1
      });
      if (prev) this.forensic.previousHash = prev.forensic.hash;
    }

    this.forensic.chainVerified = true;
    next();
  } catch (error) {
    next(error);
  }
});

comparableSchema.pre('findOneAndUpdate', function () {
  this.set({ 'audit.updatedAt': new Date() });
});

// ============================================================================
// INSTANCE & STATIC METHODS (updated to use static helpers)
// ============================================================================

// ... (all other methods remain the same except the calculate calls)

comparableSchema.methods.getLatestFinancials = function () {
  return this.financials?.length ? this.financials.sort((a, b) => b.asOfDate - a.asOfDate)[0] : null;
};

comparableSchema.methods.getLatestTradingData = function () {
  return this.tradingData?.length ? this.tradingData.sort((a, b) => b.asOfDate - a.asOfDate)[0] : null;
};

comparableSchema.methods.getPeerComparison = async function (metric) {
  const peers = await this.constructor.find({ 'company.sector': this.company.sector, isActive: true, tenantId: this.tenantId });
  const values = peers.map(p => p.getLatestFinancials()?.[metric]).filter(v => v != null && !isNaN(v));

  if (!values.length) return null;

  const mean = this.constructor.calculateAverage(values);
  const median = this.constructor.calculateMedian(values);
  const min = Math.min(...values);
  const max = Math.max(...values);

  const latest = this.getLatestFinancials();
  const companyValue = latest?.[metric];

  let percentileRank = 0;
  if (companyValue != null) {
    const below = values.filter(v => v < companyValue).length;
    percentileRank = (below / values.length) * 100;
  }

  const zScore = companyValue != null ? (companyValue - mean) / this.constructor.calculateStdDev(values) : null;

  return {
    metric,
    companyValue,
    peerMedian: median,
    peerMean: mean,
    peerMin: min,
    peerMax: max,
    percentileRank,
    zScore,
    interpretation: this.interpretZScore(zScore)
  };
};

comparableSchema.methods.interpretZScore = function (zScore) {
  if (zScore === null) return 'Unknown';
  if (Math.abs(zScore) < 1) return 'Within 1 standard deviation';
  if (Math.abs(zScore) < 2) return 'Within 2 standard deviations';
  if (Math.abs(zScore) < 3) return 'Within 3 standard deviations';
  return 'Outlier (>3 std dev)';
};

// (addFinancials, addTradingData, calculateSimilarity, etc. remain unchanged)

// ============================================================================
// STATIC METHODS
// ============================================================================

// ... (findByTicker, findByISIN, getSectorStats, search, getForValuation remain the same – they already use this.calculateAverage which is now static)

// ============================================================================
// VIRTUALS
// ============================================================================

comparableSchema.virtual('latestPrice').get(function () { return this.getLatestTradingData()?.price?.value; });
comparableSchema.virtual('latestPE').get(function () { return this.getLatestFinancials()?.peRatio?.ttm; });
comparableSchema.virtual('latestEVEbitda').get(function () { return this.getLatestFinancials()?.evEbitda?.ttm; });
comparableSchema.virtual('marketCapDisplay').get(function () {
  const v = this.getLatestFinancials()?.marketCap?.value;
  if (!v) return 'N/A';
  if (v >= 1e12) return `$${(v / 1e12).toFixed(2)}T`;
  if (v >= 1e9) return `$${(v / 1e9).toFixed(2)}B`;
  if (v >= 1e6) return `$${(v / 1e6).toFixed(2)}M`;
  return `$${v.toFixed(2)}`;
});

// ============================================================================
// MODEL & EXPORT
// ============================================================================

const Comparable = mongoose.model('Comparable', comparableSchema);

export default Comparable;