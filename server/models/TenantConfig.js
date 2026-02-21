/* eslint-disable */
/* ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
   ║                              WILSY OS - SOVEREIGN LEGAL OPERATING SYSTEM                                                               ║
   ║                         TENANT CONFIGURATION MODEL - MULTI-TENANT v3.0                                                                 ║
   ║                                                                                                                                        ║
   ║                              "Isolation without compromise - each tenant a sovereign entity"                                          ║
   ╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝ */

import mongoose from 'mongoose';
import crypto from 'crypto';
import logger from '../utils/logger.js';
import cryptoUtils from '../utils/cryptoUtils.js';

// ============================================================================
// CONSTANTS & ENUMS
// ============================================================================

export const TENANT_TIERS = {
  FREE: 'FREE',
  BASIC: 'BASIC',
  PROFESSIONAL: 'PROFESSIONAL',
  ENTERPRISE: 'ENTERPRISE',
  GOVERNMENT: 'GOVERNMENT'
};

export const TENANT_STATUS = {
  ACTIVE: 'ACTIVE',
  SUSPENDED: 'SUSPENDED',
  PENDING: 'PENDING',
  DEACTIVATED: 'DEACTIVATED',
  TRIAL: 'TRIAL'
};

export const DATA_RESIDENCY = {
  ZA: 'ZA',
  EU: 'EU',
  US: 'US',
  UK: 'UK',
  AU: 'AU'
};

export const VALIDATION_RULES = {
  STRICT: 'STRICT',
  STANDARD: 'STANDARD',
  LENIENT: 'LENIENT'
};

export const API_RATE_LIMITS = {
  FREE: { requests: 1000, window: 3600 },
  BASIC: { requests: 10000, window: 3600 },
  PROFESSIONAL: { requests: 50000, window: 3600 },
  ENTERPRISE: { requests: 200000, window: 3600 },
  GOVERNMENT: { requests: 500000, window: 3600 }
};

// ============================================================================
// SCHEMA DEFINITION
// ============================================================================

const tenantConfigSchema = new mongoose.Schema({
  tenantId: {
    type: String,
    required: true,
    unique: true,
    index: true,
    validate: {
      validator: function(v) {
        return /^[a-zA-Z0-9_-]{8,64}$/.test(v);
      },
      message: props => `${props.value} is not a valid tenant ID format`
    }
  },
  name: {
    type: String,
    required: true,
    trim: true
  },
  registrationNumber: String,
  taxReference: String,
  vatNumber: String,
  contactEmail: {
    type: String,
    required: true,
    lowercase: true,
    trim: true,
    validate: {
      validator: function(v) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
      },
      message: props => `${props.value} is not a valid email`
    }
  },
  contactPhone: String,
  contactPerson: {
    name: String,
    role: String,
    email: String,
    phone: String
  },
  tier: {
    type: String,
    required: true,
    enum: Object.values(TENANT_TIERS),
    default: TENANT_TIERS.BASIC,
    index: true
  },
  status: {
    type: String,
    required: true,
    enum: Object.values(TENANT_STATUS),
    default: TENANT_STATUS.ACTIVE,
    index: true
  },
  subscription: {
    plan: String,
    startDate: Date,
    endDate: Date,
    autoRenew: { type: Boolean, default: true },
    billingCycle: { type: String, enum: ['MONTHLY', 'ANNUAL'] },
    price: Number,
    currency: { type: String, default: 'ZAR' }
  },
  features: {
    advancedValidation: { type: Boolean, default: false },
    bulkValidation: { type: Boolean, default: false },
    apiAccess: { type: Boolean, default: true },
    webhookSupport: { type: Boolean, default: false },
    customRules: { type: Boolean, default: false },
    auditExport: { type: Boolean, default: true },
    evidenceGeneration: { type: Boolean, default: true },
    complianceReports: { type: Boolean, default: false },
    whiteLabel: { type: Boolean, default: false }
  },
  validationSettings: {
    defaultJurisdiction: { type: String, default: 'ZA' },
    validationRuleSet: { 
      type: String, 
      enum: Object.values(VALIDATION_RULES), 
      default: VALIDATION_RULES.STANDARD 
    },
    strictMode: { type: Boolean, default: false },
    autoCorrect: { type: Boolean, default: true },
    customRules: mongoose.Schema.Types.Mixed,
    excludedValidations: [String]
  },
  complianceSettings: {
    popia: {
      enabled: { type: Boolean, default: true },
      piiRedaction: { type: Boolean, default: true },
      dataSubjectRights: { type: Boolean, default: true },
      breachNotification: { type: Boolean, default: true },
      dataProtectionOfficer: {
        name: String,
        email: String,
        phone: String
      }
    },
    fica: {
      enabled: { type: Boolean, default: true },
      riskAssessment: { type: Boolean, default: true },
      enhancedDueDiligence: { type: Boolean, default: false },
      sourceOfFundsRequired: { type: Boolean, default: true }
    },
    lpc: {
      enabled: { type: Boolean, default: true },
      practitionerValidation: { type: Boolean, default: true },
      trustAccountRules: { type: Boolean, default: true },
      cpdTracking: { type: Boolean, default: false }
    },
    ect: {
      enabled: { type: Boolean, default: true },
      signatureValidation: { type: Boolean, default: true },
      certificateValidation: { type: Boolean, default: true }
    }
  },
  retentionPolicies: {
    default: { type: String, default: 'POPIA_6_YEARS' },
    overrides: mongoose.Schema.Types.Mixed,
    autoArchive: {
      enabled: { type: Boolean, default: true },
      archiveAfterDays: { type: Number, default: 365 },
      archiveLocation: String
    },
    autoDelete: {
      enabled: { type: Boolean, default: true },
      deleteAfterExpiry: { type: Boolean, default: true }
    }
  },
  dataResidency: {
    primary: { 
      type: String, 
      enum: Object.values(DATA_RESIDENCY), 
      default: DATA_RESIDENCY.ZA 
    },
    backup: { 
      type: String, 
      enum: Object.values(DATA_RESIDENCY), 
      default: DATA_RESIDENCY.ZA 
    },
    processing: { type: [String], default: [DATA_RESIDENCY.ZA] },
    restrictions: [String]
  },
  apiConfig: {
    enabled: { type: Boolean, default: true },
    rateLimit: {
      requests: { type: Number, default: 10000 },
      window: { type: Number, default: 3600 }
    },
    allowedIps: { type: [String], default: [] },
    blockedIps: { type: [String], default: [] },
    requireApiKey: { type: Boolean, default: true },
    apiKeys: [{
      keyId: { type: String, required: true },
      keyHash: { type: String, required: true },
      name: String,
      permissions: [String],
      expiresAt: Date,
      createdAt: { type: Date, default: Date.now },
      lastUsed: Date
    }],
    webhooks: [{
      url: String,
      events: [String],
      secret: String,
      active: { type: Boolean, default: true },
      createdAt: Date
    }]
  },
  securitySettings: {
    mfaRequired: { type: Boolean, default: false },
    sessionTimeout: { type: Number, default: 3600 },
    passwordPolicy: {
      minLength: { type: Number, default: 8 },
      requireUppercase: { type: Boolean, default: true },
      requireLowercase: { type: Boolean, default: true },
      requireNumbers: { type: Boolean, default: true },
      requireSpecialChars: { type: Boolean, default: true },
      expiryDays: { type: Number, default: 90 }
    },
    ipWhitelist: { type: [String], default: [] },
    allowedDomains: { type: [String], default: [] },
    encryptionKeyId: String,
    auditLevel: { 
      type: String, 
      enum: ['BASIC', 'DETAILED', 'FORENSIC'], 
      default: 'DETAILED' 
    }
  },
  integrations: {
    cipc: {
      enabled: { type: Boolean, default: false },
      apiKey: { type: String, select: false },
      endpoint: String
    },
    sars: {
      enabled: { type: Boolean, default: false },
      apiKey: { type: String, select: false },
      endpoint: String
    },
    lpc: {
      enabled: { type: Boolean, default: false },
      apiKey: { type: String, select: false },
      endpoint: String
    },
    banks: [{
      name: String,
      enabled: { type: Boolean, default: false },
      apiKey: { type: String, select: false }
    }]
  },
  branding: {
    logo: String,
    primaryColor: String,
    secondaryColor: String,
    companyName: String,
    website: String,
    supportEmail: String,
    supportPhone: String
  },
  metadata: mongoose.Schema.Types.Mixed,
  auditTrail: [{
    action: String,
    userId: String,
    timestamp: { type: Date, default: Date.now },
    changes: mongoose.Schema.Types.Mixed,
    ipAddress: String
  }],
  lastActive: Date
}, {
  timestamps: true,
  strict: true,
  collection: 'tenant_configs'
});

// ============================================================================
// INDEXES
// ============================================================================

tenantConfigSchema.index({ tenantId: 1 }, { unique: true });
tenantConfigSchema.index({ status: 1, tier: 1 });
tenantConfigSchema.index({ 'subscription.endDate': 1 });
tenantConfigSchema.index({ 'apiConfig.apiKeys.keyId': 1 });

// ============================================================================
// PRE-VALIDATE HOOK - Ensures rate limits are set BEFORE validation
// ============================================================================

tenantConfigSchema.pre('validate', function(next) {
  try {
    // Set rate limit based on tier BEFORE validation
    if (this.isNew || this.isModified('tier')) {
      const limit = API_RATE_LIMITS[this.tier] || API_RATE_LIMITS.BASIC;
      
      if (!this.apiConfig) {
        this.apiConfig = {};
      }
      
      this.apiConfig.rateLimit = { 
        requests: limit.requests,
        window: limit.window 
      };
      
      logger.debug('Applied rate limit in pre-validate', {
        tenantId: this.tenantId,
        tier: this.tier,
        requests: limit.requests
      });
    }

    next();
  } catch (error) {
    logger.error('Error in tenant config pre-validate', {
      error: error.message,
      tenantId: this.tenantId
    });
    next(error);
  }
});

// ============================================================================
// PRE-SAVE HOOK - Hash API keys
// ============================================================================

tenantConfigSchema.pre('save', function(next) {
  try {
    // Hash API keys before saving
    if (this.apiConfig && this.apiConfig.apiKeys) {
      for (let i = 0; i < this.apiConfig.apiKeys.length; i += 1) {
        const key = this.apiConfig.apiKeys[i];
        if (key.keyHash && key.keyHash.length < 64) {
          key.keyHash = crypto
            .createHash('sha256')
            .update(key.keyHash)
            .digest('hex');
        }
      }
    }

    next();
  } catch (error) {
    logger.error('Error in tenant config pre-save', {
      error: error.message,
      tenantId: this.tenantId
    });
    next(error);
  }
});

// ============================================================================
// INSTANCE METHODS
// ============================================================================

tenantConfigSchema.methods.hasFeature = function(feature) {
  return this.features && this.features[feature] === true;
};

tenantConfigSchema.methods.validateApiKey = function(apiKey) {
  if (!this.apiConfig || !this.apiConfig.apiKeys || !this.apiConfig.apiKeys.length) return false;
  
  const hashedKey = crypto
    .createHash('sha256')
    .update(apiKey)
    .digest('hex');

  const key = this.apiConfig.apiKeys.find(k => k.keyHash === hashedKey);
  
  if (key && key.expiresAt) {
    const now = new Date();
    if (key.expiresAt < now) return false;
  }

  return !!key;
};

tenantConfigSchema.methods.addAuditEntry = async function(entry) {
  if (!this.auditTrail) this.auditTrail = [];
  this.auditTrail.push({
    ...entry,
    timestamp: new Date()
  });
  await this.save();
};

tenantConfigSchema.methods.getRetentionPolicy = function(documentType) {
  const override = this.retentionPolicies?.overrides?.[documentType];
  if (override) {
    return {
      name: override,
      isOverride: true
    };
  }
  
  return {
    name: this.retentionPolicies?.default || 'POPIA_6_YEARS',
    isOverride: false
  };
};

tenantConfigSchema.methods.isIpAllowed = function(ip) {
  if (this.securitySettings?.ipWhitelist?.length > 0) {
    return this.securitySettings.ipWhitelist.includes(ip);
  }
  return true;
};

// ============================================================================
// STATIC METHODS
// ============================================================================

tenantConfigSchema.statics.findActiveTenant = async function(tenantId) {
  return this.findOne({
    tenantId,
    status: TENANT_STATUS.ACTIVE
  });
};

tenantConfigSchema.statics.findByApiKey = async function(apiKey) {
  const hashedKey = crypto
    .createHash('sha256')
    .update(apiKey)
    .digest('hex');

  return this.findOne({
    'apiConfig.apiKeys.keyHash': hashedKey,
    status: TENANT_STATUS.ACTIVE
  });
};

tenantConfigSchema.statics.createTenant = async function(data) {
  const tenantId = data.tenantId || cryptoUtils.generateId('tenant');
  
  const tenant = new this({
    ...data,
    tenantId,
    status: TENANT_STATUS.PENDING,
    auditTrail: [{
      action: 'TENANT_CREATED',
      userId: 'system',
      timestamp: new Date(),
      changes: data
    }]
  });

  await tenant.save();

  logger.info('Tenant created', {
    tenantId: tenant.tenantId,
    tier: tenant.tier
  });

  return tenant;
};

tenantConfigSchema.statics.updateStatus = async function(tenantId, status, userId) {
  const tenant = await this.findOne({ tenantId });
  if (!tenant) throw new Error('Tenant not found');

  const oldStatus = tenant.status;
  tenant.status = status;
  
  await tenant.addAuditEntry({
    action: 'STATUS_CHANGED',
    userId,
    changes: { from: oldStatus, to: status }
  });

  await tenant.save();

  return tenant;
};

tenantConfigSchema.statics.getExpiringSoon = async function(days = 30) {
  const expiryDate = new Date();
  expiryDate.setDate(expiryDate.getDate() + days);

  return this.find({
    'subscription.endDate': { $lte: expiryDate },
    status: TENANT_STATUS.ACTIVE
  });
};

tenantConfigSchema.statics.applyRateLimits = async function() {
  const tenants = await this.find({ status: TENANT_STATUS.ACTIVE });
  let updated = 0;

  for (let i = 0; i < tenants.length; i += 1) {
    const tenant = tenants[i];
    const limit = API_RATE_LIMITS[tenant.tier] || API_RATE_LIMITS.BASIC;
    
    if (!tenant.apiConfig.rateLimit || 
        tenant.apiConfig.rateLimit.requests !== limit.requests) {
      tenant.apiConfig.rateLimit = { 
        requests: limit.requests,
        window: limit.window 
      };
      await tenant.save();
      updated += 1;
    }
  }

  return { updated, total: tenants.length };
};

// ============================================================================
// VIRTUAL PROPERTIES
// ============================================================================

tenantConfigSchema.virtual('isActive').get(function() {
  return this.status === TENANT_STATUS.ACTIVE;
});

tenantConfigSchema.virtual('isOnTrial').get(function() {
  return this.status === TENANT_STATUS.TRIAL;
});

tenantConfigSchema.virtual('subscriptionStatus').get(function() {
  if (!this.subscription || !this.subscription.endDate) return 'NONE';
  
  const now = new Date();
  if (this.subscription.endDate < now) return 'EXPIRED';
  
  const thirtyDaysFromNow = new Date();
  thirtyDaysFromNow.setDate(thirtyDaysFromNow.getDate() + 30);
  
  if (this.subscription.endDate < thirtyDaysFromNow) {
    return 'EXPIRING_SOON';
  }
  return 'ACTIVE';
});

tenantConfigSchema.virtual('daysUntilExpiry').get(function() {
  if (!this.subscription || !this.subscription.endDate) return null;
  
  const now = new Date();
  const diff = this.subscription.endDate - now;
  return Math.max(0, Math.ceil(diff / (24 * 60 * 60 * 1000)));
});

// ============================================================================
// MODEL CREATION
// ============================================================================

const TenantConfig = mongoose.model('TenantConfig', tenantConfigSchema);

export default TenantConfig;
