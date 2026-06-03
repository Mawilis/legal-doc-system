/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║   █████╗ ██╗    ███████╗ █████╗ ██╗     ███████╗███████╗    ██████╗  █████╗ ███████╗██╗  ██╗██████╗  ██████╗  █████╗ ██████╗ ██████╗ ║
 * ║  ██╔══██╗██║    ██╔════╝██╔══██╗██║     ██╔════╝██╔════╝    ██╔══██╗██╔══██╗██╔════╝██║  ██║██╔══██╗██╔══██╗██╔══██╗██╔══██╗██╔══██╗║
 * ║  ███████║██║    ███████╗███████║██║     █████╗  ███████╗    ██║  ██║███████║███████╗███████║██████╔╝██║  ██║███████║██████╔╝██║  ██║║
 * ║  ██╔══██║██║    ╚════██║██╔══██║██║     ██╔══╝  ╚════██║    ██║  ██║██╔══██║╚════██║██╔══██║██╔══██╗██║  ██║██╔══██║██╔══██╗██║  ██║║
 * ║  ██║  ██║███████╗███████║██║  ██║███████╗███████╗███████║    ██████╔╝██║  ██║███████║██║  ██║██║  ██║██████╔╝██║  ██║██║  ██║██████╔╝║
 * ║  ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ║
 * ║                                                                                                                                    ║
 * ║                         THE SOVEREIGN OPERATING SYSTEM FOR GLOBAL BUSINESS                                                         ║
 * ║               QUANTUM AI NEURAL SCHEMA | TENANT METADATA SHARD                                                                     ║
 * ║                                                                                                                                    ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 * 🏛️ WILSY OS - TENANT METADATA SCHEMA [V1.0.0-MARS-OMEGA]
 * [JURISDICTIONAL DNA | COMPLIANCE MAPPING | DATA RESIDENCY | FORENSIC ROTATION]
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-MARS | PRODUCTION READY | BILLION DOLLAR SPEC                                                                           ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/TenantMetadata.js                                                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated complete separation of concerns between Tenant Identity and Jurisdictional DNA.      ║
 * ║ • AI Engineering (Gemini) - EPITOMISED: Engineered high-velocity indexes to hydrate boardroom dashboards instantly.                    ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import crypto from 'node:crypto';

const { Schema } = mongoose;

/**
 * @class TenantMetadataSchema
 * @description Stores granular, multi-jurisdictional data for Wilsy OS tenants.
 * Designed for massive scalability (R100B+).
 * @property {String} tenantId - Sovereign Anchor linking metadata to the Tenant.
 * @property {String} jurisdiction - The legal territory (e.g., 'ZA', 'EU', 'US').
 * @property {Object} complianceDNA - Mapping of required legal frameworks (POPIA, GDPR, etc).
 * @property {String} dataResidency - Physical server location tag for sovereignty.
 * @property {Object} forensicRotation - Cryptographic rotation history for the tenant.
 */
const TenantMetadataSchema = new Schema({
  tenantId: {
    type: String,
    required: [true, 'Sovereign Anchor Required'],
    unique: true,
    index: true
  },
  jurisdiction: {
    type: String,
    default: 'ZA',
    index: true
  },
  complianceDNA: {
    frameworks: [{ type: String }],
    dpoContact: String,
    lastAuditDate: Date
  },
  dataResidency: {
    type: String,
    default: 'JOHANNESBURG-NORTH'
  },
  forensicRotation: {
    lastReset: { type: Date, default: Date.now },
    keyFingerprint: String
  },
  customSettings: {
    type: Schema.Types.Mixed,
    default: {}
  }
}, {
  timestamps: true,
  collection: 'tenant_metadata'
});

// ============================================================================
// 🏛️ SOVEREIGN COMPOUND INDEXING
// ============================================================================
TenantMetadataSchema.index({ tenantId: 1, jurisdiction: 1 });

export const TenantMetadata = mongoose.models.TenantMetadata || mongoose.model('TenantMetadata', TenantMetadataSchema);
export default TenantMetadata;
