#!/* eslint-disable */
/* ╔═══════════════════════════════════════════════════════════════════════════════════════╗
  ║ DEAL MODEL - QUANTUM M&A PIPELINE WITH FORENSIC TRACEABILITY                          ║
  ║ [Production Grade | Competition Act Compliant | 100-Year Evidence Chain]              ║
  ╚═══════════════════════════════════════════════════════════════════════════════════════╝ */

import mongoose from 'mongoose';
import crypto from 'crypto';

const dealSchema = new mongoose.Schema({
  dealId: {
    type: String,
    required: true,
    unique: true,
    default: () => `DEAL-${crypto.randomBytes(4).toString('hex').toUpperCase()}`,
  },

  tenantId: {
    type: String,
    required: true,
    index: true,
    validate: {
      validator: (v) => /^[a-zA-Z0-9_-]{8,64}$/.test(v),
      message: 'Invalid tenant ID format',
    },
  },

  acquirer: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Company',
    required: true,
  },

  target: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Target',
    required: true,
  },

  dealType: {
    type: String,
    enum: ['acquisition', 'merger', 'joint_venture', 'strategic_investment',
      'divestiture', 'spin_off', 'takeover', 'scheme_of_arrangement'],
    required: true,
  },

  stage: {
    type: String,
    enum: ['identification', 'screening', 'initial_contact', 'nda', 'preliminary_dd',
      'indicative_offer', 'confirmatory_dd', 'final_agreement', 'regulatory_approval',
      'shareholder_approval', 'closing', 'integration', 'completed', 'withdrawn'],
    default: 'identification',
  },

  value: {
    type: Number,
    required: true,
    min: 0,
  },

  currency: {
    type: String,
    default: 'ZAR',
    enum: ['ZAR', 'USD', 'EUR', 'GBP'],
  },

  consideration: {
    cash: { type: Number, default: 0 },
    shares: { type: Number, default: 0 },
    debt: { type: Number, default: 0 },
    earnout: { type: Number, default: 0 },
  },

  valuation: {
    enterpriseValue: Number,
    equityValue: Number,
    evRevenue: Number,
    evEbitda: Number,
    peRatio: Number,
    premium: Number,
    valuationDate: Date,
    valuationMethod: String,
    fairnessOpinion: {
      generated: Boolean,
      isFair: Boolean,
      fromPrice: Number,
      toPrice: Number,
      recommendedPrice: Number,
      generatedAt: Date,
      validUntil: Date,
    },
  },

  synergyScore: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'SynergyScore',
  },

  integrationSimulation: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'IntegrationSimulation',
  },

  timeline: {
    announced: Date,
    expectedClosing: Date,
    actualClosing: Date,
    dropDeadDate: Date,
    extensionCount: { type: Number, default: 0 },
  },

  regulatory: [{
    jurisdiction: String,
    filingRequired: Boolean,
    filingDate: Date,
    approvalDate: Date,
    status: String,
    conditions: [String],
    filingReference: String,
  }],

  documents: [{
    type: { type: String },
    url: String,
    uploadedAt: Date,
    version: Number,
    forensicHash: String,
  }],

  team: [{
    userId: String,
    role: String,
    assignedAt: Date,
  }],

  probability: {
    overall: { type: Number, min: 0, max: 100 },
    regulatory: { type: Number, min: 0, max: 100 },
    shareholder: { type: Number, min: 0, max: 100 },
    integration: { type: Number, min: 0, max: 100 },
    lastCalculated: Date,
  },

  risks: [{
    category: String,
    description: String,
    impact: { type: String, enum: ['low', 'medium', 'high', 'critical'] },
    probability: { type: Number, min: 0, max: 100 },
    mitigation: String,
    owner: String,
  }],

  milestones: [{
    name: String,
    dueDate: Date,
    completedDate: Date,
    status: String,
    dependents: [String],
  }],

  metadata: {
    createdBy: String,
    updatedBy: String,
    correlationId: String,
    source: String,
  },

  forensicHash: {
    type: String,
    required: true,
    unique: true,
  },

  previousHash: String,
  chainPosition: Number,
}, {
  timestamps: true,
  collection: 'deals',
});

// Indexes
dealSchema.index({ tenantId: 1, stage: 1, 'timeline.expectedClosing': 1 });
dealSchema.index({ 'valuation.enterpriseValue': -1 });
dealSchema.index({ 'regulatory.jurisdiction': 1, 'regulatory.status': 1 });
dealSchema.index({ forensicHash: 1 });
dealSchema.index({ previousHash: 1 });

// Pre-save middleware for forensic hashing
dealSchema.pre('save', async function (next) {
  const canonicalData = JSON.stringify({
    dealId: this.dealId,
    tenantId: this.tenantId,
    acquirer: this.acquirer,
    target: this.target,
    dealType: this.dealType,
    value: this.value,
    stage: this.stage,
    updatedAt: new Date(),
    previousHash: this.previousHash,
  });

  this.forensicHash = crypto
    .createHash('sha256')
    .update(canonicalData)
    .digest('hex');

  next();
});

// Methods
dealSchema.methods.verifyHash = function () {
  const canonicalData = JSON.stringify({
    dealId: this.dealId,
    tenantId: this.tenantId,
    acquirer: this.acquirer,
    target: this.target,
    dealType: this.dealType,
    value: this.value,
    stage: this.stage,
    updatedAt: this.updatedAt,
    previousHash: this.previousHash,
  });

  const calculated = crypto
    .createHash('sha256')
    .update(canonicalData)
    .digest('hex');

  return calculated === this.forensicHash;
};

dealSchema.methods.advanceStage = function (newStage, userId) {
  const validTransitions = {
    identification: ['screening', 'withdrawn'],
    screening: ['initial_contact', 'withdrawn'],
    initial_contact: ['nda', 'withdrawn'],
    nda: ['preliminary_dd', 'withdrawn'],
    preliminary_dd: ['indicative_offer', 'withdrawn'],
    indicative_offer: ['confirmatory_dd', 'withdrawn'],
    confirmatory_dd: ['final_agreement', 'withdrawn'],
    final_agreement: ['regulatory_approval', 'shareholder_approval', 'withdrawn'],
    regulatory_approval: ['shareholder_approval', 'closing', 'withdrawn'],
    shareholder_approval: ['closing', 'withdrawn'],
    closing: ['integration', 'completed'],
    integration: ['completed'],
    completed: [],
    withdrawn: [],
  };

  if (!validTransitions[this.stage]?.includes(newStage)) {
    throw new Error(`Invalid stage transition: ${this.stage} -> ${newStage}`);
  }

  this.stage = newStage;
  this.metadata.updatedBy = userId;

  return this.save();
};

const Deal = mongoose.model('Deal', dealSchema);
export default Deal;
