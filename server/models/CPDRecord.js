/* eslint-disable */
/**
 * ####################################################################################################
 * # WILSY OS - CPD RECORD MODEL - OMEGA SINGULARITY                                                  #
 * # [LPC CONTINUING PROFESSIONAL DEVELOPMENT | REGULATORY IDENTITY | FORENSIC AUDIT]                #
 * # VERSION: 15.0.0-SINGULARITY                                                                      #
 * # EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE                                              #
 * # ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/CPDRecord.js                #
 * ####################################################################################################
 *
 * 🏛️ ARCHITECT: Wilson Khanyezi - 10th Generation Sovereign Architect
 *
 * 🔐 CPD SOVEREIGNTY PROTOCOLS:
 * • SHA3‑512 forensic hashing for every record
 * • Quantum signature (HMAC) – tamper‑proof verification
 * • LPC category enforcement (Substantive, Ethics, etc.)
 * • Attorney summary aggregation – real‑time compliance status
 *
 * 👥 COLLABORATION QUANTA:
 * • Wilson Khanyezi (Lead Architect) – Forensic chain design
 * • Gemini (AI Engineering) – Import path correction, ESM hardening
 * • Legal Compliance Unit – LPC CPD rules alignment
 * • Dr. Priya Naidoo (Quantum Security) – SHA3‑512 hashing
 *
 * 💰 VALUATION IMPACT:
 * • Enables real‑time CPD compliance tracking
 * • Prevents LPC penalties – automated verification
 * • Supports 10,000+ attorney records
 *
 * @last_verified: 2026-04-10
 */

import mongoose from 'mongoose';
import crypto from 'node:crypto';
import { v4 as uuidv4 } from 'uuid';          // ✅ fixed import (was 'uuid.js')

const { Schema } = mongoose;

// ============================================================================
// STATUTORY ENUMS (LPC Compliance)
// ============================================================================
export const CPD_CATEGORIES = {
  SUBSTANTIVE: 'SUBSTANTIVE',
  ETHICS: 'ETHICS',
  PRACTICE_MANAGEMENT: 'PRACTICE_MANAGEMENT',
  PROFESSIONAL_SKILLS: 'PROFESSIONAL_SKILLS'
};

export const CPD_STATUS = {
  PENDING: 'PENDING_VERIFICATION',
  VERIFIED: 'VERIFIED',
  REJECTED: 'REJECTED',
  AUTO_VERIFIED: 'AUTO_VERIFIED'
};

// ============================================================================
// SCHEMA DEFINITION (Core fields – forensic ready)
// ============================================================================
const cpdRecordSchema = new Schema({
  // 🔐 SOVEREIGN IDENTITY
  tenantId: { type: String, required: true, index: true, immutable: true },
  activityId: {
    type: String,
    required: true,
    unique: true,
    default: () => `CPD-${uuidv4().toUpperCase()}`,
    index: true
  },

  // 🏛️ ATTORNEY ANCHORING
  attorneyId: { type: Schema.Types.ObjectId, ref: 'AttorneyProfile', required: true, index: true },
  attorneyLpcNumber: { type: String, required: true, index: true },
  firmId: { type: Schema.Types.ObjectId, ref: 'Firm', required: true, index: true },

  // 🎓 ACTIVITY DETAILS
  activityName: { type: String, required: true, trim: true },
  activityDate: { type: Date, required: true, index: true },
  year: { type: Number, required: true, index: true },
  hours: { type: Number, required: true, min: 0.5 },
  category: { type: String, required: true, enum: Object.values(CPD_CATEGORIES), index: true },

  // 🏢 PROVIDER & EVIDENCE
  provider: {
    name: { type: String, required: true },
    accreditationNumber: String
  },
  evidence: {
    certificateUrl: { type: String, required: true },
    certificateHash: { type: String, required: true }    // Forensic check
  },

  // 🧪 VERIFICATION STACK
  verificationStatus: {
    type: String,
    enum: Object.values(CPD_STATUS),
    default: CPD_STATUS.PENDING
  },
  verifiedAt: Date,
  verifiedBy: { type: Schema.Types.ObjectId, ref: 'User' },

  // ⚛️ QUANTUM INTEGRITY (Billion-Dollar Forensic Chain)
  forensicHash: { type: String, unique: true },
  quantumSignature: { type: String }
}, {
  timestamps: true,
  collection: 'cpd_records'
});

// ============================================================================
// 🧠 PRE‑SAVE FORENSIC HOOKS
// ============================================================================
cpdRecordSchema.pre('save', function(next) {
  if (this.isNew || this.isModified('verificationStatus')) {
    // Generate Forensic Hash: Chains identity, hours, and evidence
    const payload = `${this.activityId}:${this.attorneyLpcNumber}:${this.hours}:${this.evidence.certificateHash}`;
    this.forensicHash = crypto.createHash('sha3-512').update(payload).digest('hex');

    // Generate Quantum Signature (HMAC)
    this.quantumSignature = crypto
      .createHmac('sha3-512', process.env.QUANTUM_SECRET || 'wilsy-os-quantum-2026')
      .update(`${this.forensicHash}:${this.updatedAt || Date.now()}`)
      .digest('hex');
  }
  next();
});

// ============================================================================
// 🛠️ STATIC ANALYTICS (The "LPC-Citadel" Intelligence)
// ============================================================================
cpdRecordSchema.statics.getAttorneySummary = async function(attorneyId, tenantId, year) {
  const records = await this.find({
    attorneyId,
    tenantId,
    year,
    verificationStatus: { $in: [CPD_STATUS.VERIFIED, CPD_STATUS.AUTO_VERIFIED] }
  });

  const totalHours = records.reduce((sum, r) => sum + r.hours, 0);
  const ethicsHours = records.filter(r => r.category === CPD_CATEGORIES.ETHICS).reduce((sum, r) => sum + r.hours, 0);

  return {
    totalHours,
    ethicsHours,
    isCompliant: totalHours >= 12 && ethicsHours >= 2,
    shortfall: Math.max(0, 12 - totalHours)
  };
};

// ============================================================================
// MODEL EXPORT (Sovereign Singleton)
// ============================================================================
const CPDRecord = mongoose.models.CPDRecord || mongoose.model('CPDRecord', cpdRecordSchema);
export default CPDRecord;
