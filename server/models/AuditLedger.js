/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN AUDIT LEDGER MODEL                                                                                                ║
 * ║ [IMMUTABLE FORENSIC ARCHITECTURE | POPIA §19 COMPLIANT | R10B+ AUDITABLE]                                                               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 16.2.0-SINGULARITY-OMEGA | PRODUCTION READY                                                                                 ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL GRADE                                                              ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/AuditLedger.js                                                     ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Jurisprudence Data Strategy                                                                   ║
 * ║ • Gemini (AI Engineering) - Mongoose Schema Hardening & Performance Indexing                                                           ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';

const AuditLedgerSchema = new mongoose.Schema({
  tenantId: {
    type: String,
    required: true,
    index: true // Critical for multi-tenant isolation
  },
  performedBy: {
    type: String, // userId
    required: true,
    index: true
  },
  requestId: {
    type: String,
    index: true
  },
  action: {
    type: String,
    required: true,
    uppercase: true,
    index: true
  },
  resourceType: {
    type: String,
    required: true,
    uppercase: true,
    enum: ['SYSTEM', 'DOCUMENT', 'USER', 'TENANT', 'BIOMETRIC', 'BILLING', 'LEGAL_ENGINE'],
    default: 'SYSTEM'
  },
  resourceId: {
    type: String,
    index: true
  },
  details: {
    type: mongoose.Schema.Types.Mixed,
    default: {}
  },
  previousHash: {
    type: String,
    required: true,
    default: 'GENESIS_BLOCK'
  },
  immutableHash: {
    type: String,
    required: true,
    unique: true // Prevent duplicate entries in the chain
  },
  ipAddress: {
    type: String,
    default: '0.0.0.0'
  },
  dataResidencyCompliance: {
    type: String,
    default: 'SA_RESIDENT'
  },
  integrityVerified: {
    type: Boolean,
    default: true
  }
}, {
  timestamps: true,
  collection: 'audit_ledger',
  versionKey: false // Immutability doesn't need versioning
});

// 🚀 QUANTUM INDEXING - COMPOUND FORENSIC LOOKUPS
AuditLedgerSchema.index({ tenantId: 1, createdAt: -1 });
AuditLedgerSchema.index({ tenantId: 1, action: 1 });
AuditLedgerSchema.index({ immutableHash: 1 }, { unique: true });

/**
 * 🔐 SOVEREIGN PROTECTION: PRE-SAVE LOCK
 * Audit logs cannot be modified once written.
 */
AuditLedgerSchema.pre('save', function(next) {
  if (!this.isNew) {
    return next(new Error('SINGULARITY_VIOLATION: Audit logs are immutable and cannot be updated.'));
  }
  next();
});

const AuditLedger = mongoose.model('AuditLedger', AuditLedgerSchema);

export default AuditLedger;
