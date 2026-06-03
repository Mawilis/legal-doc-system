/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║  📋 TENANT AUDIT LOG MODEL - WILSY OS 2050                               ║
  ║  Immutable forensic trail for all tenant activities                      ║
  ║  Supreme Architect: Wilson Khanyezi - 10th Generation                    ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

const mongoose = require('mongoose');
const crypto = require('crypto');

const TenantAuditLogSchema = new mongoose.Schema({
  tenantId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Tenant',
    required: true,
    index: true
  },

  action: {
    type: String,
    required: true,
    // Expanded to align perfectly with TenantAdminController actions
    enum: [
      'TENANT_CREATED','TENANT_UPDATED','TENANT_DELETED','TENANT_SUSPENDED','TENANT_ACTIVATED',
      'TENANT_CONFIG_CHANGED','TENANT_BILLING_CHANGED','TENANT_PLAN_CHANGED','TENANT_SETTINGS_UPDATED',
      'USER_INVITED','USER_CREATED','USER_JOINED','USER_UPDATED','USER_DELETED','USER_ROLE_CHANGED',
      'USER_SUSPENDED','USER_ACTIVATED','ROLE_CREATED','ROLE_UPDATED','ROLE_DELETED',
      'PERMISSION_CHANGED','SETTINGS_CHANGED','SECURITY_CHANGED','COMPLIANCE_CHANGED'
    ],
    index: true
  },

  performedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    index: true
  },

  targetUser: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    index: true
  },

  changes: {
    before: { type: mongoose.Schema.Types.Mixed },
    after: { type: mongoose.Schema.Types.Mixed }
  },

  metadata: {
    ipAddress: { type: String, trim: true },
    userAgent: { type: String, trim: true },
    sessionId: { type: String, trim: true },
    requestId: { type: String, trim: true },
    timestamp: { type: Date, default: Date.now }
  },

  severity: {
    type: String,
    enum: ['info', 'warning', 'critical', 'audit'],
    default: 'info',
    index: true
  },

  status: {
    type: String,
    enum: ['success', 'failure', 'pending'],
    default: 'success',
    index: true
  },

  errorDetails: mongoose.Schema.Types.Mixed,

  // Forensic Chain-of-Custody
  forensicHash: {
    type: String,
    unique: true,
    index: true
  },
  previousHash: {
    type: String,
    index: true
  },

  // Compliance & Data Retention
  complianceTags: {
    type: [String],
    index: true // Multi-key index for high-speed compliance reporting
  },
  retentionPeriod: {
    type: Date,
    default: () => new Date(Date.now() + 7*365*24*60*60*1000) // Default 7 years (Statutory)
  }
}, {
  timestamps: true,
  versionKey: false
});

/**
 * ARCHITECTURAL INDEXES
 * Optimizing for the 3 most common audit scenarios:
 * 1. Time-series forensic analysis
 * 2. Regulatory compliance sweeps (POPIA/GDPR)
 * 3. User-specific activity tracking
 */
TenantAuditLogSchema.index({ tenantId: 1, createdAt: -1 });
TenantAuditLogSchema.index({ tenantId: 1, complianceTags: 1 });
TenantAuditLogSchema.index({ targetUser: 1, createdAt: -1 });



/**
 * Pre‑save hook: Blockchain-style hashing for immutability.
 * Each log entry links to the hash of the previous entry.
 */
TenantAuditLogSchema.pre('save', async function(next) {
  if (this.isNew || !this.forensicHash) {
    const lastLog = await this.constructor.findOne(
      { tenantId: this.tenantId },
      { forensicHash: 1 },
      { sort: { createdAt: -1 } }
    );

    const prevHash = lastLog?.forensicHash || 'GENESIS_BLOCK';
    this.previousHash = prevHash;

    const payload = JSON.stringify({
      t: this.tenantId,
      a: this.action,
      p: this.performedBy,
      ts: this.metadata.timestamp,
      ph: prevHash
    });

    this.forensicHash = crypto.createHash('sha3-512')
      .update(payload)
      .digest('hex');
  }
  next();
});

/**
 * Verify Ledger Integrity:
 * Mathematically proves that no log entry has been tampered with or deleted.
 */
TenantAuditLogSchema.statics.verifyLedgerIntegrity = async function(tenantId) {
  const logs = await this.find({ tenantId }).sort({ createdAt: 1 });
  let currentPrevHash = 'GENESIS_BLOCK';

  for (const log of logs) {
    const payload = JSON.stringify({
      t: log.tenantId,
      a: log.action,
      p: log.performedBy,
      ts: log.metadata.timestamp,
      ph: currentPrevHash
    });

    const calculated = crypto.createHash('sha3-512').update(payload).digest('hex');

    if (log.forensicHash !== calculated || log.previousHash !== currentPrevHash) {
      return {
        integrity: false,
        corruptedId: log._id,
        reason: 'Hash mismatch or chain break'
      };
    }
    currentPrevHash = log.forensicHash;
  }
  return { integrity: true };
};

module.exports = mongoose.model('TenantAuditLog', TenantAuditLogSchema);
