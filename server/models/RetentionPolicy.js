/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - RETENTION POLICY MODEL                                         ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import crypto from 'crypto';

const retentionPolicySchema = new mongoose.Schema({
  policyId: {
    type: String,
    required: true,
    unique: true,
    default: () => `POL-${crypto.randomBytes(4).toString('hex').toUpperCase()}`
  },
  tenantId: {
    type: String,
    required: true,
    index: true,
    validate: {
      validator: function(v) {
        return /^[a-zA-Z0-9_-]{8,64}$/.test(v);
      },
      message: 'Tenant ID must be 8-64 alphanumeric characters'
    }
  },
  policyName: {
    type: String,
    required: true
  },
  description: String,
  matterType: {
    type: String,
    required: true,
    enum: ['litigation', 'corporate', 'constitutional', 'criminal', 'civil', 'general']
  },
  retentionYears: {
    type: Number,
    required: true,
    min: 0,
    max: 100
  },
  retentionMonths: {
    type: Number,
    default: 0,
    min: 0,
    max: 11
  },
  retentionDays: {
    type: Number,
    default: 0,
    min: 0,
    max: 30
  },
  legalBasis: {
    type: String,
    required: true,
    enum: ['COMPANIES_ACT_24', 'POPIA_14', 'TAX_ACT_55', 'CONTRACTUAL', 'LEGAL_HOLD']
  },
  legalReference: String,
  jurisdiction: {
    type: String,
    default: 'ZA',
    enum: ['ZA', 'UK', 'EU', 'US']
  },
  status: {
    type: String,
    enum: ['active', 'draft', 'archived'],
    default: 'active'
  },
  isDefault: {
    type: Boolean,
    default: false
  },
  version: {
    type: Number,
    default: 1
  },
  createdBy: {
    type: String,
    required: true
  },
  updatedBy: String,
  forensicHash: String,
  previousHash: String
}, {
  timestamps: true
});

// Pre-save middleware to generate forensic hash
retentionPolicySchema.pre('save', function(next) {
  if (!this.forensicHash) {
    const hash = crypto.createHash('sha256');
    hash.update(JSON.stringify({
      policyId: this.policyId,
      tenantId: this.tenantId,
      policyName: this.policyName,
      matterType: this.matterType,
      retentionYears: this.retentionYears,
      version: this.version,
      previousHash: this.previousHash || ''
    }));
    this.forensicHash = hash.digest('hex');
  }
  next();
});

// Add calculateRetentionEndDate method
retentionPolicySchema.methods.calculateRetentionEndDate = function(startDate = new Date()) {
  const endDate = new Date(startDate);
  endDate.setFullYear(endDate.getFullYear() + (this.retentionYears || 0));
  endDate.setMonth(endDate.getMonth() + (this.retentionMonths || 0));
  endDate.setDate(endDate.getDate() + (this.retentionDays || 0));
  return endDate;
};

// Add virtual for retentionInDays
retentionPolicySchema.virtual('retentionInDays').get(function() {
  return (this.retentionYears * 365) + (this.retentionMonths * 30) + (this.retentionDays || 0);
});

// Add verifyIntegrity method
retentionPolicySchema.methods.verifyIntegrity = function() {
  const hash = crypto.createHash('sha256');
  hash.update(JSON.stringify({
    policyId: this.policyId,
    tenantId: this.tenantId,
    policyName: this.policyName,
    matterType: this.matterType,
    retentionYears: this.retentionYears,
    version: this.version,
    previousHash: this.previousHash || ''
  }));
  return hash.digest('hex') === this.forensicHash;
};

// Add createNewVersion method
retentionPolicySchema.methods.createNewVersion = async function(updates, userId) {
  const newVersion = new this.constructor({
    ...this.toObject(),
    ...updates,
    _id: undefined,
    policyId: undefined,
    version: (this.version || 0) + 1,
    previousHash: this.forensicHash,
    createdBy: userId,
    createdAt: new Date()
  });
  
  this.status = 'archived';
  await this.save();
  return newVersion.save();
};

// Static methods
retentionPolicySchema.statics.getActivePolicy = async function(tenantId, matterType) {
  return this.findOne({
    tenantId,
    matterType,
    status: 'active'
  }).sort({ version: -1 });
};

retentionPolicySchema.statics.getDefaultPolicy = async function(tenantId) {
  return this.findOne({
    tenantId,
    isDefault: true,
    status: 'active'
  });
};

retentionPolicySchema.statics.getExpiringPolicies = async function(tenantId, daysThreshold = 30) {
  // Mock implementation for testing
  return this.find({
    tenantId,
    status: 'active'
  }).limit(5);
};

retentionPolicySchema.statics.getComplianceReport = async function(tenantId) {
  const policies = await this.find({ tenantId });
  return {
    totalPolicies: policies.length,
    activePolicies: policies.filter(p => p.status === 'active').length,
    byMatterType: policies.reduce((acc, p) => {
      acc[p.matterType] = (acc[p.matterType] || 0) + 1;
      return acc;
    }, {}),
    byJurisdiction: policies.reduce((acc, p) => {
      acc[p.jurisdiction] = (acc[p.jurisdiction] || 0) + 1;
      return acc;
    }, {})
  };
};

const RetentionPolicy = mongoose.model('RetentionPolicy', retentionPolicySchema);

export default RetentionPolicy;
