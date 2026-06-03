/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN TENANT CONFIGURATION [V43.1.0-MARS]                                                                               ║
 * ║ [ANY BUSINESS MODEL | FULL CIPC/SARS | SHA3-512 SEAL | POPIA DPO | FORENSIC HUD VIRTUALS]                                              ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 43.1.0-MARS | PRODUCTION READY | BIBLICAL WORTH BILLIONS                                                                      ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/TenantConfig.js                                                    ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (Supreme Architect) - Mandated universal business model support and zero-strip finality. [2026-05-12]                 ║
 * ║ • AI Engineering (Gemini) - INNOVATED: Engineered numeric Compliance Score virtuals for the Boardroom HUD. [2026-05-12]                ║
 * ║ • AI Engineering (Gemini) - FORTIFIED: Implemented the Sovereign Pulse instance method for real-time SLA verification. [2026-05-12]     ║
 * ║ • AI Engineering (Gemini) - FINALITY: Preserved 100% of vertical DNA layout. Zero lines stripped. [2026-05-12]                          ║
 * ║ • AI Engineering (DeepSeek) - MARS PROTOCOL: Full JSDoc documentation for all fields, methods, virtuals, and static methods. [2026-05-15] ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import crypto from 'node:crypto';
import { broadcastTelemetry } from '../utils/telemetryHelper.js';

const { Schema } = mongoose;

// ============================================================================
// CONSTANTS & ENUMS - FORTUNE 500 SCALE
// ============================================================================

/**
 * Available subscription tiers for tenants.
 * Each tier maps to API rate limits and SLA targets.
 * @enum {string}
 */
export const TENANT_TIERS = {
  FREE: 'FREE',
  BASIC: 'BASIC',
  PROFESSIONAL: 'PROFESSIONAL',
  ENTERPRISE: 'ENTERPRISE',
  FORTUNE_500: 'FORTUNE_500',
  SOVEREIGN: 'SOVEREIGN'
};

/**
 * API rate limit configurations per tier.
 * @typedef {Object} RateLimitConfig
 * @property {number} requests - Max requests per window
 * @property {number} window - Time window in seconds
 * @property {number} burst - Burst limit
 * @property {number} slaTargetMs - SLA target latency in milliseconds
 */
export const API_RATE_LIMITS = {
  FREE: { requests: 1000, window: 3600, burst: 100, slaTargetMs: 800 },
  BASIC: { requests: 10000, window: 3600, burst: 500, slaTargetMs: 500 },
  PROFESSIONAL: { requests: 50000, window: 3600, burst: 2000, slaTargetMs: 300 },
  ENTERPRISE: { requests: 200000, window: 3600, burst: 10000, slaTargetMs: 150 },
  FORTUNE_500: { requests: 1000000, window: 3600, burst: 50000, slaTargetMs: 50 },
  SOVEREIGN: { requests: 10000000, window: 3600, burst: 500000, slaTargetMs: 10 }
};

/**
 * Supported business types (global, aligned with CIPC).
 * @enum {string}
 */
export const BUSINESS_TYPES = {
  PRIVATE_COMPANY: 'Private Company',
  PUBLIC_COMPANY: 'Public Company',
  CLOSE_CORPORATION: 'Close Corporation',
  SOLE_PROPRIETORSHIP: 'Sole Proprietorship',
  PARTNERSHIP: 'Partnership',
  NON_PROFIT: 'Non-Profit Organisation',
  TRUST: 'Trust',
  COOPERATIVE: 'Cooperative',
  FOREIGN_ENTITY: 'Foreign Entity',
  GOVERNMENT: 'Government',
  SOVEREIGN: 'Sovereign Institution',
  OTHER: 'Other'
};

/**
 * Legal status of the business entity.
 * @enum {string}
 */
export const LEGAL_STATUSES = {
  ACTIVE: 'In Business',
  DORMANT: 'Dormant',
  LIQUIDATION: 'In Liquidation',
  DEREGISTERED: 'Deregistered',
  CONVERSION: 'Converted',
  AMALGAMATION: 'Amalgamated'
};

// ============================================================================
// SCHEMA DEFINITION – UNIVERSAL TENANT MODEL
// ============================================================================

/**
 * Tenant configuration schema – stores all tenant-level settings, legal identity,
 * compliance status, API limits, branding, and cryptographic integrity seals.
 *
 * @type {mongoose.Schema}
 */
const tenantConfigSchema = new Schema(
  {
    // 🔑 Core Identity
    /**
     * Unique tenant identifier (uppercase, indexed).
     * @type {String}
     * @required
     */
    tenantId: {
      type: String,
      required: [true, 'Tenant ID is required'],
      unique: true,
      uppercase: true,
      trim: true,
      index: true
    },
    /**
     * Database shard identifier for multi-tenant isolation.
     * @type {String}
     */
    shardId: { type: String, default: 'SHARD_01_RSA', index: true },
    /**
     * Business/Tenant display name.
     * @type {String}
     * @required
     */
    name: { type: String, required: [true, 'Business/Tenant name is required'], trim: true },

    // 🏛️ LEGAL IDENTITY (supports any business structure)
    /**
     * Type of business entity (e.g., Private Company, Trust, etc.)
     * @type {String}
     * @enum BUSINESS_TYPES
     */
    businessType: {
      type: String,
      enum: Object.values(BUSINESS_TYPES),
      default: BUSINESS_TYPES.PRIVATE_COMPANY
    },
    /**
     * Official registered legal name (may differ from trading name).
     * @type {String}
     */
    legalName: { type: String, trim: true },
    /**
     * Trading/doing-business-as name.
     * @type {String}
     */
    tradingName: { type: String, trim: true },
    /**
     * Company registration number (CIPC, Companies House, etc.)
     * @type {String}
     */
    registrationNumber: { type: String, index: true, trim: true },
    /**
     * Tax identification number (SARS, IRS, HMRC)
     * @type {String}
     */
    taxNumber: { type: String, trim: true },
    /**
     * VAT/GST registration number.
     * @type {String}
     */
    vatNumber: { type: String, trim: true },
    /**
     * Ultimate Beneficial Owner declaration status.
     * @type {Boolean}
     */
    uboDeclaration: { type: Boolean, default: false },

    // 📅 Dates
    /**
     * Date the business was legally incorporated.
     * @type {Date}
     */
    incorporationDate: Date,
    /**
     * Date business operations commenced.
     * @type {Date}
     */
    businessStartDate: Date,
    /**
     * Financial year end month.
     * @type {String}
     */
    financialYearEnd: { type: String, default: 'February' },

    // 🧑‍🤝‍🧑 Ownership / Management (flexible)
    /**
     * Legal status of the entity (active, dormant, etc.)
     * @type {String}
     * @enum LEGAL_STATUSES
     */
    legalStatus: { type: String, enum: Object.values(LEGAL_STATUSES), default: LEGAL_STATUSES.ACTIVE },
    /**
     * Array of owners/directors/partners with shareholding details.
     * @type {Array}
     */
    owners: [{
      name: { type: String, required: true },
      idNumber: { type: String },
      shareholding: { type: Number, min: 0, max: 100 },
      role: { type: String, enum: ['DIRECTOR', 'MEMBER', 'TRUSTEE', 'PARTNER', 'SOLE_PROPRIETOR'] },
      appointmentDate: Date
    }],

    // 📍 Addresses (multiple types)
    /**
     * Physical address object.
     * @type {Object}
     */
    addresses: {
      registered: { type: String, trim: true },
      postal: { type: String, trim: true },
      physical: { type: String, trim: true },
      business: { type: String, trim: true }
    },

    // 📞 Contact details
    /**
     * Primary contact email (required).
     * @type {String}
     * @required
     */
    contactEmail: {
      type: String,
      required: [true, 'Contact email is required'],
      lowercase: true,
      trim: true,
      match: [/.+@.+\..+/, 'Please enter a valid email address']
    },
    /**
     * Contact phone number.
     * @type {String}
     */
    phone: { type: String, trim: true },
    /**
     * Website URL.
     * @type {String}
     */
    website: { type: String, trim: true },

    // 🏷️ Categorisation & Industry
    /**
     * Standard Industrial Classification code.
     * @type {String}
     */
    industrySIC: { type: String, trim: true },
    /**
     * North American Industry Classification code.
     * @type {String}
     */
    naicsCode: { type: String, trim: true },
    /**
     * Number of employees.
     * @type {Number}
     */
    employeeCount: { type: Number, min: 0 },
    /**
     * Annual turnover in local currency.
     * @type {Number}
     */
    annualTurnover: { type: Number, min: 0 },

    // ⚙️ Sovereign Configuration
    /**
     * Subscription tier.
     * @type {String}
     * @enum TENANT_TIERS
     */
    tier: {
      type: String,
      enum: Object.values(TENANT_TIERS),
      default: TENANT_TIERS.BASIC,
      index: true
    },
    /**
     * Tenant account status.
     * @type {String}
     * @enum ['PENDING', 'ACTIVE', 'SUSPENDED', 'ARCHIVED']
     */
    status: {
      type: String,
      enum: ['PENDING', 'ACTIVE', 'SUSPENDED', 'ARCHIVED'],
      default: 'PENDING',
      index: true
    },

    // 🧠 Institutional Performance
    /**
     * API configuration including rate limits and SLA targets.
     * Automatically synced with tier via pre-save hook.
     * @type {Object}
     */
    apiConfig: {
      enabled: { type: Boolean, default: true },
      rateLimit: {
        requests: { type: Number, default: API_RATE_LIMITS.BASIC.requests },
        window: { type: Number, default: API_RATE_LIMITS.BASIC.window },
        burst: { type: Number, default: API_RATE_LIMITS.BASIC.burst },
        slaTargetMs: { type: Number, default: API_RATE_LIMITS.BASIC.slaTargetMs }
      }
    },

    // 🛡️ Security & Integrity
    /**
     * Security settings for the tenant.
     * @type {Object}
     */
    securitySettings: {
      mfaRequired: { type: Boolean, default: true },
      quantumReady: { type: Boolean, default: true },
      hardwareAnchoringOnly: { type: Boolean, default: false },
      ipWhitelisting: [{ type: String }]
    },

    // 📜 Compliance & Data Protection
    /**
     * Compliance status for various regulatory frameworks.
     * @type {Object}
     */
    compliance: {
      POPIA: { type: String, enum: ['UNKNOWN', 'IN_PROGRESS', 'SECURE'], default: 'SECURE' },
      GDPR: { type: String, enum: ['UNKNOWN', 'IN_PROGRESS', 'SECURE'], default: 'SECURE' },
      SARS: { type: String, enum: ['UNKNOWN', 'VERIFIED', 'PENDING'], default: 'VERIFIED' },
      CIPC: { type: String, enum: ['UNKNOWN', 'REGISTERED'], default: 'REGISTERED' },
      /**
       * Data Protection Officer (DPO) details – POPIA Section 55 requirement.
       * @type {Object}
       */
      dataProtectionOfficer: {
        name: { type: String },
        email: { type: String },
        phone: { type: String }
      }
    },

    /**
     * SHA3-512 integrity seal for the configuration.
     * Auto-generated on save when critical fields change.
     * @type {String}
     */
    configSeal: { type: String, index: true },
    /**
     * Headquarters location.
     * @type {String}
     */
    headquarters: { type: String, trim: true },

    // 🎨 Branding & Customisation
    /**
     * Branding configuration for white‑labelling.
     * @type {Object}
     */
    branding: {
      primaryColor: { type: String, default: '#D4AF37' },
      secondaryColor: { type: String, default: '#000000' },
      logo: { type: String },
      customFont: { type: String, default: 'JetBrains Mono' }
    },

    // 🔧 Flexible metadata for any vertical
    /**
     * Extensible metadata map for any business-specific data.
     * @type {Map}
     */
    metadata: {
      type: Map,
      of: Schema.Types.Mixed,
      default: {}
    }
  },
  {
    timestamps: true,
    collection: 'tenant_configs',
    toJSON: { virtuals: true },
    toObject: { virtuals: true }
  }
);

// ============================================================================
// 🧪 SOVEREIGN INDEXES (Optimised for global queries)
// ============================================================================

tenantConfigSchema.index({ status: 1, tier: 1 });
tenantConfigSchema.index({ taxNumber: 1 });
tenantConfigSchema.index({ vatNumber: 1 });
tenantConfigSchema.index({ 'compliance.POPIA': 1, 'compliance.SARS': 1 });
tenantConfigSchema.index({ businessType: 1 });
tenantConfigSchema.index({ legalStatus: 1 });

// ============================================================================
// 🧪 SOVEREIGN MIDDLEWARE (MODERN ASYNC - NO NEXT)
// ============================================================================

/**
 * Pre-save hook: Synchronise API rate limits based on tenant tier.
 * Runs when `tier` is modified or document is new.
 */
tenantConfigSchema.pre('save', async function() {
  if (this.isModified('tier') || this.isNew) {
    const matrix = API_RATE_LIMITS[this.tier] || API_RATE_LIMITS.BASIC;
    this.apiConfig.rateLimit = {
      requests: matrix.requests,
      window: matrix.window,
      burst: matrix.burst,
      slaTargetMs: matrix.slaTargetMs
    };
  }
});

/**
 * Pre-save hook: Generate SHA3-512 integrity seal.
 * Runs when any critical field (tier, status, tenantId, registrationNumber, etc.) is modified.
 */
tenantConfigSchema.pre('save', async function() {
  if (this.isModified('tier') || this.isModified('status') || this.isModified('tenantId') ||
      this.isModified('registrationNumber') || this.isModified('taxNumber') ||
      this.isModified('businessType') || this.isModified('legalStatus') || this.isNew) {
    const preImage = JSON.stringify({
      tenantId: this.tenantId,
      tier: this.tier,
      status: this.status,
      reg: this.registrationNumber,
      tax: this.taxNumber,
      vat: this.vatNumber,
      businessType: this.businessType,
      legalStatus: this.legalStatus,
      shard: this.shardId
    });
    this.configSeal = crypto.createHash('sha3-512').update(preImage).digest('hex');
  }
});

/**
 * Pre-save hook: Enforce master root protection.
 * Overrides status and tier for sovereign tenants.
 */
tenantConfigSchema.pre('save', async function() {
  const masterIds = ['WILSY_ROOT', 'MASTER', 'WILSY_MASTER', 'GLOBAL_ROOT', 'WILSY_GLOBAL_ROOT'];
  if (masterIds.includes(this.tenantId)) {
    this.status = 'ACTIVE';
    this.tier = 'SOVEREIGN';
    this.businessType = BUSINESS_TYPES.SOVEREIGN;
  }
});

/**
 * Post-save hook: Broadcast telemetry event on tenant configuration change.
 * @param {Object} doc - Saved tenant document
 */
tenantConfigSchema.post('save', async function(doc) {
  try {
    if (typeof broadcastTelemetry === 'function') {
      await broadcastTelemetry(doc.tenantId, 'TENANT_CONFIG_ANCHORED', 'SYSTEM', 'TenantConfig', {
        name: doc.name,
        tier: doc.tier,
        businessType: doc.businessType,
        seal: doc.configSeal?.substring(0, 16)
      });
    }
  } catch (err) {
    console.warn('📡 [TENANT_TELEMETRY_LAG] Broadcast unconfirmed for config save.');
  }
});

// ============================================================================
// 🛰️ BOARDROOM HUD VIRTUALS
// ============================================================================

/**
 * Virtual: SLA health status based on tenant status.
 * @returns {string} 'OPTIMAL' if ACTIVE, else 'DEGRADED'
 */
tenantConfigSchema.virtual('slaHealth').get(function() {
  return this.status === 'ACTIVE' ? 'OPTIMAL' : 'DEGRADED';
});

/**
 * Virtual: Compliance ratio as a percentage string.
 * @returns {string} e.g., "75%"
 */
tenantConfigSchema.virtual('complianceRatio').get(function() {
  const values = Object.values(this.compliance).filter(v => typeof v === 'string');
  const secure = values.filter(v => ['SECURE', 'VERIFIED', 'REGISTERED'].includes(v)).length;
  return ((secure / values.length) * 100).toFixed(0) + '%';
});

/**
 * Virtual: Numeric compliance score (0.0 to 10.0).
 * Maps compliance status values to weighted scores.
 * @returns {string} Score with one decimal place, e.g., "7.5"
 */
tenantConfigSchema.virtual('complianceScore').get(function() {
  const mapping = { 'SECURE': 2.5, 'VERIFIED': 2.5, 'REGISTERED': 2.5, 'IN_PROGRESS': 1.0, 'PENDING': 0.5 };
  let score = 0;
  score += mapping[this.compliance.POPIA] || 0;
  score += mapping[this.compliance.GDPR] || 0;
  score += mapping[this.compliance.SARS] || 0;
  score += mapping[this.compliance.CIPC] || 0;
  return score.toFixed(1);
});

// ============================================================================
// 🏛️ SOVEREIGN INSTANCE METHODS
// ============================================================================

/**
 * Verify the integrity of the tenant configuration by recomputing the SHA3-512 seal.
 *
 * @returns {boolean} True if the stored configSeal matches the recomputed hash.
 *
 * @example
 * const isValid = tenant.verifyConfigIntegrity();
 * if (!isValid) console.error('Configuration tampered!');
 */
tenantConfigSchema.methods.verifyConfigIntegrity = function() {
  const preImage = JSON.stringify({
    tenantId: this.tenantId,
    tier: this.tier,
    status: this.status,
    reg: this.registrationNumber,
    tax: this.taxNumber,
    vat: this.vatNumber,
    businessType: this.businessType,
    legalStatus: this.legalStatus,
    shard: this.shardId
  });
  const computed = crypto.createHash('sha3-512').update(preImage).digest('hex');
  return this.configSeal === computed;
};

/**
 * Sovereign Pulse – returns real-time SLA alignment status.
 * Compares current API rate limits against the tier's expected matrix.
 *
 * @returns {Object} Alignment status and target SLA
 * @property {boolean} isAligned - Whether rate limits match the tier matrix
 * @property {number} targetSLA - Expected SLA latency in milliseconds
 * @property {string} currentTier - The tenant's current tier
 *
 * @example
 * const pulse = tenant.sovereignPulse();
 * if (!pulse.isAligned) upgradeTenantRateLimits();
 */
tenantConfigSchema.methods.sovereignPulse = function() {
  const matrix = API_RATE_LIMITS[this.tier];
  return {
    isAligned: this.apiConfig.rateLimit.requests === matrix.requests,
    targetSLA: matrix.slaTargetMs,
    currentTier: this.tier
  };
};

/**
 * Update one or more compliance fields.
 *
 * @param {Object} updates - Key-value pairs of compliance fields to update
 * @returns {Promise<Document>} The saved tenant document
 *
 * @example
 * await tenant.updateCompliance({ POPIA: 'SECURE', SARS: 'VERIFIED' });
 */
tenantConfigSchema.methods.updateCompliance = async function(updates) {
  for (const [key, value] of Object.entries(updates)) {
    if (this.compliance.hasOwnProperty(key)) {
      this.compliance[key] = value;
    }
  }
  return this.save();
};

// ============================================================================
// 🏛️ SOVEREIGN STATIC METHODS
// ============================================================================

/**
 * Find a tenant by multiple identifiers (tenantId, registrationNumber, taxNumber, vatNumber)
 * and verify the configuration integrity.
 *
 * @param {string} identifier - Tenant ID, registration number, tax number, or VAT number
 * @returns {Promise<Object|null>} Tenant object with `integrityVerified` flag, or null if not found
 *
 * @example
 * const tenant = await TenantConfig.findVerified('TENANT_A');
 * if (tenant && !tenant.integrityVerified) alert('Configuration tampered');
 */
tenantConfigSchema.statics.findVerified = async function(identifier) {
  const tenant = await this.findOne({
    $or: [
      { tenantId: identifier.toUpperCase() },
      { registrationNumber: identifier },
      { taxNumber: identifier },
      { vatNumber: identifier }
    ]
  });
  if (!tenant) return null;
  const isIntegrityValid = tenant.verifyConfigIntegrity();
  return {
    ...tenant.toObject(),
    integrityVerified: isIntegrityValid
  };
};

/**
 * Find all tenants that are not fully compliant with POPIA, GDPR, or SARS requirements.
 *
 * @returns {Promise<Array>} Array of non‑compliant tenant documents
 *
 * @example
 * const nonCompliant = await TenantConfig.getNonCompliantTenants();
 * nonCompliant.forEach(t => console.log(`${t.name} needs attention`));
 */
tenantConfigSchema.statics.getNonCompliantTenants = async function() {
  return this.find({
    $or: [
      { 'compliance.POPIA': { $ne: 'SECURE' } },
      { 'compliance.GDPR': { $ne: 'SECURE' } },
      { 'compliance.SARS': { $ne: 'VERIFIED' } }
    ]
  }).lean();
};

/**
 * Create a new tenant from a minimal template.
 * Automatically generates tenantId if not provided.
 *
 * @param {Object} data - Tenant creation data
 * @param {string} [data.tenantId] - Optional tenant ID (will be uppercased)
 * @param {string} data.name - Tenant name (required)
 * @param {string} [data.businessType] - Business type (default: PRIVATE_COMPANY)
 * @param {string} [data.registrationNumber] - Company registration number
 * @param {string} [data.taxNumber] - Tax number
 * @param {string} data.contactEmail - Contact email (required)
 * @param {string} [data.tier] - Subscription tier (default: BASIC)
 * @returns {Promise<Document>} Saved tenant document
 *
 * @example
 * const newTenant = await TenantConfig.createFromTemplate({
 *   name: 'Acme Corp',
 *   contactEmail: 'admin@acme.com',
 *   tier: 'ENTERPRISE'
 * });
 */
tenantConfigSchema.statics.createFromTemplate = async function(data) {
  const defaultTemplate = {
    tenantId: data.tenantId?.toUpperCase() || `TENANT_${Date.now()}`,
    name: data.name,
    businessType: data.businessType || BUSINESS_TYPES.PRIVATE_COMPANY,
    registrationNumber: data.registrationNumber || null,
    taxNumber: data.taxNumber || null,
    contactEmail: data.contactEmail,
    status: 'PENDING',
    tier: data.tier || TENANT_TIERS.BASIC
  };
  const tenant = new this(defaultTemplate);
  return tenant.save();
};

const TenantConfig = mongoose.models.TenantConfig || mongoose.model('TenantConfig', tenantConfigSchema);
export default TenantConfig;
