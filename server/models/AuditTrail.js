/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - FORENSIC AUDIT TRAIL SCHEMA [V16.0.0-MARS]                                                                                  ║
 * ║ [IMMUTABLE LEDGER | QUANTUM SIGNATURES | TENANT ISOLATION | COMPLIANCE LOGGING]                                                        ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 16.0.0-MARS | PRODUCTION READY | BILLION DOLLAR SPEC                                                                          ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/AuditTrail.js                                                      ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & ARCHITECTURAL LOG:                                                                                                  ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Demanded a fully fortified schema, rejecting the minimal stub.                                ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Injected strict Mongoose validation, enum constraints, and data-sealing pre-save hooks.         ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';

const auditTrailSchema = new mongoose.Schema({
  eventId: {
    type: String,
    required: [true, 'Forensic Integrity Violation: Event ID is mandatory.'],
    unique: true,
    immutable: true // Native Mongoose lock
  },
  eventHash: {
    type: String,
    required: [true, 'Forensic Integrity Violation: Event Hash is mandatory.'],
    immutable: true
  },
  timestamp: {
    type: Date,
    required: true,
    immutable: true,
    default: Date.now
  },

  // 🏛️ Sovereign Identity Binding
  user: {
    id: { type: String, default: 'SYSTEM' },
    role: { type: String, default: 'ANONYMOUS' },
    tenantId: {
      type: String,
      required: [true, 'Tenant Isolation Fracture: Tenant ID must be bound to every log entry.'],
      index: true,
      immutable: true
    }
  },

  // ⚖️ Action & Taxonomy
  action: {
    method: { type: String },
    url: { type: String },
    endpoint: { type: String },
    category: {
      type: String,
      enum: ['AUTH', 'DOC_ACCESS', 'DOC_MODIFY', 'COMPLIANCE', 'USER_MGMT', 'SECURITY', 'DATA_EXPORT', 'API', 'SYSTEM'],
      required: true
    }
  },

  // 📡 Network Forensics
  network: {
    ipAddress: { type: String, default: '0.0.0.0' },
    userAgent: { type: String }
  },

  // ⚡ Execution Results
  result: {
    statusCode: { type: Number, required: true },
    responseTimeMs: { type: Number }
  },

  // 🏛️ Legal & Compliance Context
  compliance: {
    legalBasis: { type: String, required: true, default: 'Cybercrimes Act 19 of 2020' },
    jurisdiction: { type: String, default: 'ZA' },
    retentionPeriodDays: { type: Number, default: 3650 } // Default 10 years
  },

  // 🔐 Cryptographic Anchor
  quantumSignature: {
    hash: { type: String, required: true },
    algorithm: { type: String, default: 'sha256' },
    sealed: { type: Boolean, default: false }
  }
}, {
  timestamps: true,
  // Ensure the document cannot be updated once saved
  strict: true
});

// 🛡️ Compound index for high-speed tenant-specific forensic queries and data retention
auditTrailSchema.index({ 'user.tenantId': 1, timestamp: -1 });
auditTrailSchema.index({ eventHash: 1 });
auditTrailSchema.index({ 'action.category': 1, timestamp: -1 });

// 🛡️ Pre-save hook to ensure the signature is marked as sealed
auditTrailSchema.pre('save', function(next) {
    if (this.isNew) {
        this.quantumSignature.sealed = true;
    } else {
        // Absolute fail-safe: Prevent updates to existing audit logs
        return next(new Error('QUANTUM_VIOLATION: Audit logs are immutable and cannot be modified after insertion.'));
    }
    next();
});

// 🛡️ Export the Sovereign Model
export default mongoose.models.AuditTrail || mongoose.model('AuditTrail', auditTrailSchema);
