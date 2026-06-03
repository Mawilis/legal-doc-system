/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ CAT WILSYEOF - SOVEREIGN TENANT ARCHETYPE [V28.12.0-SUPREME]                                                                          ║
 * ║ [LEDGER SCHEMA | IDENTITY ANCHORING | ROOT BRIDGING | DETERMINISTIC SHARDING]                                                         ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 28.12.0-SUPREME | PRODUCTION READY | BILLION DOLLAR SPEC                                                                     ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | REVENUE-GRADE ARCHITECTURE                                                       ║
 * ║ FRAMEWORK: CAT WILSYEOF (Wilsy Electronic Office Framework)                                                                           ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/tenantModel.js                                                     ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Architect): Enforced V28.12.0 Stable Logic with Forensic Precision.                                             ║
 * ║ • AI Engineering: Implemented Deterministic tenantId generation (_SOVEREIGN_ROOT suffix).                                              ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 🛠️ FUNCTIONAL LOGIC:                                                                                                                   ║
 * ║ 1. Deterministic Bridging: tenantId now auto-suffixes with _SOVEREIGN_ROOT for Auth alignment.                                         ║
 * ║ 2. Sparse Alias: Organization Alias now allows sparse indexing to prevent collision on null values.                                    ║
 * ║ 3. Biblical Retention: 2555-day (7 Year) forensic standard locked for POPIA/GDPR compliance.                                           ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';

const tenantSchema = new mongoose.Schema({
  // 🏛️ CORE IDENTITY ANCHORS
  name: {
    type: String,
    required: [true, 'ORGANIZATION_NAME_REQUIRED'],
    trim: true,
    maxlength: 255
  },
  slug: {
    type: String,
    required: [true, 'SOVEREIGN_SLUG_REQUIRED'],
    unique: true,
    lowercase: true,
    trim: true,
    index: true,
    match: [/^[a-z0-9-]+$/, 'SLUG_INVALID_FORMAT']
  },
  organizationAlias: {
    type: String,
    unique: true,
    lowercase: true,
    trim: true,
    index: true,
    sparse: true
  },
  tenantId: {
    type: String,
    unique: true,
    uppercase: true,
    index: true
  },

  // 👑 FOUNDER & GOVERNANCE
  adminEmail: {
    type: String,
    required: [true, 'FOUNDER_EMAIL_REQUIRED'],
    lowercase: true,
    trim: true,
    index: true
  },
  ownerId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },

  // 🛡️ STATUS & TIER ALIGNMENT
  status: {
    type: String,
    enum: ['ACTIVE', 'SUSPENDED', 'PENDING_PROVISIONING', 'DECOMMISSIONED', 'ARCHIVED'],
    default: 'ACTIVE',
    index: true
  },
  subscriptionTier: {
    type: String,
    enum: ['FREE', 'PROFESSIONAL', 'ENTERPRISE', 'SOVEREIGN', 'ULTRA'],
    default: 'SOVEREIGN'
  },

  // 🎨 INSTITUTIONAL BRANDING MATRIX
  branding: {
    logo: String,
    icon: String,
    primaryColor: { type: String, default: '#000000' },
    secondaryColor: { type: String, default: '#FFFFFF' },
    theme: { type: String, enum: ['dark', 'light', 'system'], default: 'dark' }
  },

  // ⚙️ OPERATIONAL PARAMETERS
  settings: {
    mfaRequired: { type: Boolean, default: true },
    ssoEnabled: { type: Boolean, default: false },
    maxUsers: { type: Number, default: 1000 },
    apiEnabled: { type: Boolean, default: true }
  },

  // ⚖️ BIBLICAL COMPLIANCE & FORENSIC RETENTION
  compliance: {
    isPopiaCompliant: { type: Boolean, default: true },
    dataRetentionDays: { type: Number, default: 2555 } // 7 Years Biblical Standard
  },

  // 📊 ANALYTICS SHARD
  metadata: {
    industry: { type: String, default: 'Legal' },
    region: { type: String, default: 'ZA' }
  }
}, {
  timestamps: true,
  collection: 'tenants'
});

tenantSchema.index({ slug: 1, status: 1 });
tenantSchema.index({ organizationAlias: 1 });
tenantSchema.index({ tenantId: 1 });
tenantSchema.index({ adminEmail: 1 });

tenantSchema.pre('save', function(next) {
  if (this.slug && !this.organizationAlias) {
    this.organizationAlias = this.slug;
  }
  if (!this.tenantId && this.slug) {
    this.tenantId = this.slug.toUpperCase().replace(/-/g, '_') + '_SOVEREIGN_ROOT';
  }
  next();
});

const Tenant = mongoose.model('Tenant', tenantSchema);
export default Tenant;
