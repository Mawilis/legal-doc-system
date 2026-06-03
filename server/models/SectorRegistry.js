/* eslint-disable */
/**
 * ####################################################################################################
 * # WILSY OS - GLOBAL SECTOR REGISTRY [THE GENETIC CODE OF BUSINESS]                                #
 * # ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/SectorRegistry.js           #
 * ####################################################################################################
 * # VERSION: 15.0.0-SINGULARITY                                                                      #
 * # EPITOME: BIBLICAL WORTH BILLIONS | 100-YEAR GENERATIONAL ASSET                                   #
 * ####################################################################################################
 * * 👥 COLLABORATION & SOVEREIGN SIGN-OFF:
 * • Wilson Khanyezi (Lead Architect & CEO) - Global Sector Logic & Sovereign Property Rights.
 * • Gemini (AI Engineering) - Schema-less attribute injection & logic orchestration.
 * • Dr. Fatima Cassim (Performance) - High-frequency indexing for global sector lookups.
 * * 🔬 FORENSIC EVIDENCE:
 * 1. UNIVERSAL OWNERSHIP: Can model any industry from Fish & Chips to Space Logistics.
 * 2. DYNAMIC COMPLIANCE: Injects specific legal stacks (LPC, SARS, SEC, FIFA) into the Tenant.
 * 3. ZERO-DOWNTIME EXPANSION: Add new global sectors via API without modifying the kernel.
 */

import mongoose from 'mongoose';

const { Schema } = mongoose;

const SectorRegistrySchema = new Schema({
  sectorId: { type: String, unique: true, required: true, uppercase: true, index: true },
  name: { type: String, required: true, trim: true },
  description: String,

  // 🧬 SECTOR DNA: The fields every business in this sector MUST have
  schemaRequirements: [{
    fieldName: String,
    fieldType: { type: String, enum: ['String', 'Number', 'Date', 'Boolean', 'Object'] },
    isMandatory: { type: Boolean, default: false },
    forensicValidation: String // Regex or validation logic
  }],

  // ⚖️ COMPLIANCE STACK: Statutory requirements for this industry
  complianceStack: {
    regulators: [String], // e.g., ['LPC', 'SARS', 'CIPC']
    statutes: [String],   // e.g., ['POPIA', 'Rule 54']
    auditFrequency: { type: String, default: 'ANNUAL' }
  },

  // 🎨 BRANDING & UI DNA: How the OS "morphs" for this sector
  uxProfile: {
    primaryColor: String,
    dashboardLayout: { type: String, default: 'STANDARD' },
    icon: String
  },

  isGlobal: { type: Boolean, default: true },
  isActive: { type: Boolean, default: true }
}, { timestamps: true });

// Forensic Full-Text Search for Sector Discovery
SectorRegistrySchema.index({ name: 'text', sectorId: 'text', description: 'text' });

export const SectorRegistry = mongoose.models.SectorRegistry || mongoose.model('SectorRegistry', SectorRegistrySchema);
export default SectorRegistry;
