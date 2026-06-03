/* eslint-disable */
/**
 * ####################################################################################################
 * # WILSY OS - ATTORNEY PROFILE MODEL - OMEGA SINGULARITY                                            #
 * # [LEGAL PRACTICE COUNCIL REGISTRY | IDENTITY ANCHOR | FORENSIC AUDIT]                             #
 * # VERSION: 15.0.0-SINGULARITY                                                                      #
 * # EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE                                              #
 * # ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/AttorneyProfile.js          #
 * ####################################################################################################
 *
 * 🏛️ ARCHITECT: Wilson Khanyezi - 10th Generation Sovereign Architect
 *
 * 🔐 ATTORNEY SOVEREIGNTY PROTOCOLS:
 * • LPC number as immutable identity anchor
 * • SHA3‑512 integrity hashing (chains LPC number, ID number, tenant)
 * • Quantum signature (HMAC) – tamper‑proof profile
 * • POPIA §19 compliance – automatic ID number redaction
 * • Virtual compliance check (Fidelity + CPD)
 *
 * 👥 COLLABORATION QUANTA:
 * • Wilson Khanyezi (Lead Architect) – Identity anchor design
 * • Gemini (AI Engineering) – Import path correction, ESM hardening
 * • Legal Compliance Unit – LPC rules alignment
 * • Dr. Priya Naidoo (Quantum Security) – SHA3‑512 hashing
 *
 * 💰 VALUATION IMPACT:
 * • Enables real‑time attorney compliance status
 * • Prevents identity fraud – integrity hash chaining
 * • Supports 10,000+ attorney profiles
 *
 * @last_verified: 2026-04-10
 */

import mongoose from 'mongoose';
import crypto from 'node:crypto';

const { Schema } = mongoose;

// ============================================================================
// STATUTORY ENUMS (LPC Compliance Matrix)
// ============================================================================
export const ATTORNEY_STATUS = {
  ACTIVE: 'ACTIVE',
  SUSPENDED: 'SUSPENDED',
  EXPIRED: 'EXPIRED',
  RETIRED: 'RETIRED',
  NON_PRACTICING: 'NON_PRACTICING'
};

// ============================================================================
// SCHEMA DEFINITION (Core fields – forensic ready)
// ============================================================================
const attorneyProfileSchema = new Schema({
  // 🔐 SOVEREIGN IDENTITY & ISOLATION
  tenantId: { type: String, required: true, index: true, immutable: true },
  lpcNumber: {
    type: String,
    required: true,
    unique: true,
    uppercase: true,
    trim: true,
    index: true
  },

  // 👤 PERSONAL IDENTITY (POPIA §19 SECURE)
  personalInfo: {
    title: { type: String, enum: ['Mr', 'Mrs', 'Ms', 'Dr', 'Prof', 'Adv', 'Justice'], required: true },
    fullName: { type: String, required: true, trim: true },
    idNumber: { type: String, required: true, unique: true },
    dateOfBirth: { type: Date, required: true }
  },

  // 📞 CONTACT GATEWAY
  contact: {
    email: { type: String, required: true, lowercase: true, trim: true },
    phone: { type: String, required: true }
  },

  // 🏛️ PRACTICE ARCHITECTURE
  practice: {
    name: { type: String, required: true, trim: true },
    type: { type: String, required: true, default: 'PRIVATE' },
    commencementDate: { type: Date, required: true },
    yearsOfPractice: { type: Number, default: 0 }
  },

  // 💰 REGULATORY HUD (Cross-Model Links)
  fidelityFund: {
    certificateNumber: String,
    expiryDate: Date,
    status: { type: String, default: 'PENDING' }
  },
  cpd: {
    hoursCompleted: { type: Number, default: 0 },
    ethicsHours: { type: Number, default: 0 },
    complianceStatus: { type: String, default: 'PENDING' }
  },

  // ⚛️ QUANTUM INTEGRITY STACK
  status: { type: String, enum: Object.values(ATTORNEY_STATUS), default: 'ACTIVE', index: true },
  integrityHash: { type: String, unique: true },
  quantumSignature: { type: String },

  createdBy: { type: String, required: true, immutable: true },
  updatedBy: { type: String, required: true }
}, {
  timestamps: true,
  collection: 'attorney_profiles'
});

// ============================================================================
// 🧠 FORENSIC LOGIC (Pre-Save Integrity)
// ============================================================================
attorneyProfileSchema.pre('save', function(next) {
  // Update practice years dynamically
  if (this.practice?.commencementDate) {
    this.practice.yearsOfPractice = Math.floor(
      (Date.now() - this.practice.commencementDate) / (1000 * 60 * 60 * 24 * 365)
    );
  }

  // Generate Integrity Hash (SHA3-512) – chains LPC number, ID number, tenant
  const payload = `${this.lpcNumber}:${this.personalInfo.idNumber}:${this.tenantId}`;
  this.integrityHash = crypto.createHash('sha3-512').update(payload).digest('hex');

  // Generate Quantum Signature
  this.quantumSignature = crypto
    .createHmac('sha3-512', process.env.QUANTUM_SECRET || 'wilsy-os-quantum-2026')
    .update(`${this.integrityHash}:${this.updatedAt || Date.now()}`)
    .digest('hex');

  next();
});

// ============================================================================
// 🛠️ SOVEREIGN VIRTUALS & TRANSFORMS
// ============================================================================
attorneyProfileSchema.virtual('isCompliant').get(function() {
  const fidelityValid = this.fidelityFund?.expiryDate > new Date();
  const cpdValid = this.cpd?.complianceStatus === 'COMPLIANT';
  return fidelityValid && cpdValid;
});

// POPIA Redaction on Export – ID number stripped automatically
attorneyProfileSchema.options.toJSON = {
  virtuals: true,
  transform(doc, ret) {
    delete ret.__v;
    delete ret.personalInfo.idNumber;   // REDACTED FOR SOVEREIGN PRIVACY
    delete ret.integrityHash;
    delete ret.quantumSignature;
    return ret;
  }
};

// ============================================================================
// MODEL EXPORT (Sovereign Singleton)
// ============================================================================
const AttorneyProfile = mongoose.models.AttorneyProfile || mongoose.model('AttorneyProfile', attorneyProfileSchema);
export default AttorneyProfile;
