/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - QUANTUM COMPLIANCE CATHEDRAL [V2.1.0-OMEGA-FINAL]                                                                           ║
 * ║ [ANCHOR: REGULATORY GENOME | CROSS-JURISDICTIONAL DNA | MULTI-TENANT ISOLATION | CRYPTOGRAPHIC PROOF]                                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 2.1.0 | PRODUCTION READY | BIBLICAL WORTH BILLIONS                                                                            ║
 * ║ EPITOME: NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY | THE IMMUTABLE LEDGER                                                            ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/ComplianceRecord.js                                               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated the Regulatory DNA Mapping and ECT Act compliance.                                   ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Resolved ESM resolution fractures and anchored named service exports. [2026-05-10]              ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import crypto from 'node:crypto';

// 🛡️ ANCHORED: Sovereign ESM Service Imports
import {
  anchorToBlockchain,
  createSmartContractCompliance,
} from '../services/blockchainService.js';

const { Schema } = mongoose;

const complianceRecordSchema = new Schema(
  {
    quantumId: {
      type: String,
      required: [true, 'Quantum ID mandatory for blockchain anchoring'],
      unique: true,
      default: () => `compliance-${crypto.randomBytes(16).toString('hex')}-${Date.now()}`,
      index: true,
      immutable: true,
    },
    firmId: {
      type: Schema.Types.ObjectId,
      ref: 'Firm',
      required: [true, 'Firm ID required for regulatory jurisdiction isolation'],
      index: true,
      immutable: true,
    },
    complianceType: {
      type: String,
      required: [true, 'Compliance type required for regulatory DNA mapping'],
      index: true,
    },
    jurisdiction: {
      type: String,
      required: true,
      default: 'ZA',
      index: true,
    },
    applicableSections: [
      {
        regulation: String,
        section: String,
        requirement: String,
        complianceDeadline: Date,
      },
    ],
    status: {
      type: String,
      enum: ['DRAFT', 'PENDING_REVIEW', 'APPROVED', 'REJECTED', 'EXPIRED', 'ARCHIVED'],
      default: 'DRAFT',
      index: true,
    },
    riskAssessment: {
      inherentRisk: { type: String, enum: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'], default: 'MEDIUM' },
      lastAssessed: Date,
      nextAssessment: Date,
    },
    complianceDocuments: [
      {
        documentId: { type: String, required: true, default: () => `doc-${crypto.randomBytes(12).toString('hex')}` },
        documentHash: { type: String, required: true },
        documentCategory: { type: String, required: true },
        effectiveDate: { type: Date, default: Date.now },
        expiryDate: { type: Date, required: true },
        uploadedBy: { type: Schema.Types.ObjectId, ref: 'User' },
        blockchainAnchor: { transactionId: String, timestamp: Date },
      },
    ],
    complianceMetrics: {
      overallScore: { type: Number, min: 0, max: 100, default: 0 },
    },
  },
  {
    timestamps: true,
    toJSON: { virtuals: true },
    toObject: { virtuals: true },
  }
);

// 🏛️ QUANTUM METHODS
complianceRecordSchema.methods.sealAndAnchor = async function (userId) {
  const result = await anchorToBlockchain(this.quantumId, {
    documentId: this._id,
    firmId: this.firmId,
    userId: userId,
  });

  this.status = 'APPROVED';
  return await this.save();
};

const ComplianceRecord = mongoose.models.ComplianceRecord || mongoose.model('ComplianceRecord', complianceRecordSchema);

export default ComplianceRecord;
