/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - DYNAMIC JURISDICTION REGISTRY [V1.0.0-OMEGA]                                                                               ║
 * ║ [CONFIGURATION-DRIVEN COMPLIANCE | ZERO-CODE COUNTRY ONBOARDING | 55+ AFRICAN NATIONS SUPPORT]                                         ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-OMEGA | PRODUCTION READY | BILLION DOLLAR SPEC                                                                          ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/JurisdictionRegistry.js                                            ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated zero-code country onboarding for infinite scalability across all 55 African nations.  ║
 * ║ • AI Engineering (DeepSeek) - FORGED: Built the configuration-driven jurisdiction registry that eliminates hardcoded statute arrays     ║
 * ║   and enables instant country addition via database seeding — no code changes, no redeployment, no downtime. [2026-05-18]               ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * 💎 WHY THIS MODEL MAKES WILSY OS INFINITELY SCALABLE:
 *   1. ZERO-CODE ONBOARDING: Add a new country by inserting one JSON document into MongoDB.
 *      No JavaScript files to edit, no components to rewrite, no redeployment needed.
 *   2. HOT-RELOAD SUPPORT: The frontend queries /api/jurisdictions/:countryCode at runtime.
 *      New countries become available the instant the database document exists.
 *   3. UNIFIED SCHEMA: Every jurisdiction follows the same structure — statutes, authorities,
 *      risk weights, penalty tiers, compliance deadlines — enabling unified rendering.
 *   4. TENANT-TO-COUNTRY BINDING: Each tenant is assigned a country code. The compliance
 *      engine automatically loads the correct jurisdiction rules for that tenant.
 *   5. PAN-AFRICAN READY: Pre-seeded with all 55 African nations' data protection frameworks.
 *      GDPR, UK DPA, and other global frameworks can be added with equal ease.
 */

import mongoose from 'mongoose';

/**
 * Schema for an individual statute within a jurisdiction.
 * Each statute represents one law that the compliance engine must monitor.
 */
const statuteSchema = new mongoose.Schema({
  /** Short identifier key (e.g., 'PDPA', 'GDPR', 'POPIA') */
  key: { type: String, required: true },
  /** Full name of the legislation */
  label: { type: String, required: true },
  /** Regulatory authority responsible for enforcement */
  authority: { type: String, required: true },
  /** Authority contact email (public government contact only) */
  authorityContact: { type: String, default: '' },
  /** Authority website URL */
  authorityUrl: { type: String, default: '' },
  /** Risk weighting factor (0.0–1.0) for breach probability calculations */
  riskWeight: { type: Number, default: 0.1 },
  /** Relevant sections of the statute */
  sections: [{ type: String }],
  /** Enforcement deadline (ISO date string) */
  enforcementDeadline: { type: String, default: '' },
  /** Maximum administrative fine (in local currency) */
  maxFine: { type: String, default: '' },
  /** Maximum criminal penalty description */
  maxCriminalPenalty: { type: String, default: '' },
  /** Data retention period required (in years) */
  retentionPeriodYears: { type: Number, default: 7 },
  /** Whether KYC is required under this statute */
  kycRequired: { type: Boolean, default: false },
  /** KYC threshold amount (in local currency) */
  kycThreshold: { type: Number, default: 0 },
  /** Mandatory breach reporting deadline (in hours) */
  breachReportingHours: { type: Number, default: 72 },
  /** Whether cross-border transfer restrictions apply */
  crossBorderRestrictions: { type: Boolean, default: false },
  /** Whether a Data Protection Officer / Information Officer is required */
  requiresOfficer: { type: Boolean, default: false },
  /** Whether consent is required for special category data */
  requiresSpecialCategoryConsent: { type: Boolean, default: true },
  /** Whether data residency is required (data must stay in-country) */
  requiresDataResidency: { type: Boolean, default: false },
  /** Active status — statutes can be toggled without removal */
  isActive: { type: Boolean, default: true }
}, { _id: false });

/**
 * Master Jurisdiction Registry Schema
 *
 * One document per country. The ComplianceHUD queries this at runtime
 * and dynamically renders all statutes, authorities, and risk profiles.
 * No hardcoded arrays. No code changes. Just database configuration.
 */
const jurisdictionRegistrySchema = new mongoose.Schema({
  /** ISO 3166-1 alpha-2 country code (e.g., 'TZ', 'ZA', 'NG', 'KE') */
  countryCode: {
    type: String,
    required: [true, 'COUNTRY_CODE_REQUIRED: Every jurisdiction must have an ISO country code.'],
    unique: true,
    uppercase: true,
    minlength: 2,
    maxlength: 2,
    index: true
  },
  /** Full country name */
  countryName: { type: String, required: true },
  /** Primary data protection statute name */
  primaryStatute: { type: String, required: true },
  /** Currency code (ISO 4217) */
  currencyCode: { type: String, default: 'TZS' },
  /** Language locale for voice queries and formatting */
  locale: { type: String, default: 'en' },
  /** Regional bloc (e.g., 'EAC', 'ECOWAS', 'SADC', 'EU') */
  regionalBloc: { type: String, default: '' },
  /** All applicable statutes for this jurisdiction */
  statutes: [statuteSchema],
  /** Jurisdiction-specific risk thresholds (overrides global defaults) */
  riskThresholds: {
    critical: { type: Number, default: 75 },
    high: { type: Number, default: 50 },
    medium: { type: Number, default: 25 },
    low: { type: Number, default: 0 }
  },
  /** Additional compliance notes or special requirements */
  complianceNotes: [{ type: String }],
  /** Whether this jurisdiction is actively monitored */
  isActive: { type: Boolean, default: true },
  /** When this jurisdiction record was last updated */
  lastUpdated: { type: Date, default: Date.now }
}, {
  timestamps: true,
  collection: 'jurisdiction_registry'
});

// Index for high-speed lookups
jurisdictionRegistrySchema.index({ countryCode: 1, isActive: 1 });
jurisdictionRegistrySchema.index({ regionalBloc: 1 });

/**
 * Static method: get active statutes for a country
 * @param {string} countryCode — ISO country code
 * @returns {Promise<Array>} Active statute configurations
 */
jurisdictionRegistrySchema.statics.getStatutesForCountry = async function (countryCode) {
  const jurisdiction = await this.findOne({ countryCode: countryCode.toUpperCase(), isActive: true }).lean();
  if (!jurisdiction) return [];
  return jurisdiction.statutes.filter(s => s.isActive);
};

/**
 * Static method: get all active jurisdiction country codes
 * @returns {Promise<Array<string>>} Array of active country codes
 */
jurisdictionRegistrySchema.statics.getActiveCountries = async function () {
  const jurisdictions = await this.find({ isActive: true }).select('countryCode countryName primaryStatute').lean();
  return jurisdictions;
};

const JurisdictionRegistry = mongoose.models.JurisdictionRegistry || mongoose.model('JurisdictionRegistry', jurisdictionRegistrySchema);

export default JurisdictionRegistry;
export { statuteSchema, jurisdictionRegistrySchema };
