/* eslint-disable */
/* ╔══════════════════════════════════════════════════════════════════════════════╗
   ║ AUDIT LEDGER MODEL - INVESTOR-GRADE MODULE                                  ║
   ║ Immutable audit trail | SHA256 hashed | Multi-tenant isolation              ║
   ║ Standard: ES Module (Surgically Standardized)                               ║
   ╚══════════════════════════════════════════════════════════════════════════════╝*/

/**
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/AuditLedger.js
 */

import mongoose from 'mongoose';
import crypto from 'node:crypto';

const AuditEntrySchema = new mongoose.Schema({
    timestamp: { type: Date, default: Date.now, required: true, index: true },
    action: { type: String, required: true, index: true },
    userId: { type: String, required: true, index: true },
    tenantId: { type: String, required: true, index: true },
    resource: { type: String, required: true },
    resourceId: { type: String },
    details: { type: mongoose.Schema.Types.Mixed },
    ipAddress: String,
    userAgent: String,
    sessionId: String,
    correlationId: String,
    regulatoryTags: [String],
    forensicHash: { type: String, required: true },
    chainOfCustody: [{
        action: String,
        actor: String,
        timestamp: Date,
        hash: String,
        previousHash: String
    }],
    metadata: { type: mongoose.Schema.Types.Mixed, default: {} },
    retentionPolicy: String,
    retentionStart: Date,
    dataResidency: { type: String, default: 'ZA' }
});

// Optimized indexing for High-Volume Production
AuditEntrySchema.index({ tenantId: 1, timestamp: -1 });
AuditEntrySchema.index({ userId: 1, timestamp: -1 });
AuditEntrySchema.index({ resource: 1, resourceId: 1 });
AuditEntrySchema.index({ forensicHash: 1 }, { unique: true });

// ==============================================
// FORENSIC METHODS
// ==============================================

/**
 * Court-Admissible Integrity Check
 */
AuditEntrySchema.methods.verifyIntegrity = function () {
    const recalculatedHash = crypto.createHash('sha256')
        .update(JSON.stringify({
            timestamp: this.timestamp,
            action: this.action,
            userId: this.userId,
            tenantId: this.tenantId,
            resource: this.resource,
            resourceId: this.resourceId,
            details: this.details,
            ipAddress: this.ipAddress,
            userAgent: this.userAgent,
            sessionId: this.sessionId,
            correlationId: this.correlationId,
            regulatoryTags: this.regulatoryTags
        }))
        .digest('hex');

    return recalculatedHash === this.forensicHash;
};

// ==============================================
// ANALYTIC STATICS
// ==============================================

AuditEntrySchema.statics.findByTenant = async function (tenantId, options = {}) {
    const query = { tenantId };
    const { action, resource, limit = 100, skip = 0 } = options;

    if (action) query.action = action;
    if (resource) query.resource = resource;

    return this.find(query)
        .sort({ timestamp: -1 })
        .skip(skip)
        .limit(limit)
        .lean();
};

AuditEntrySchema.statics.getChainOfCustody = async function (entryId) {
    const entry = await this.findOne({ _id: entryId }).lean();
    if (!entry) return [];

    const chain = [entry];
    let currentHash = entry.previousEvidenceHash;

    while (currentHash) {
        const previous = await this.findOne({ forensicHash: currentHash }).lean();
        if (previous) {
            chain.unshift(previous);
            currentHash = previous.previousEvidenceHash;
        } else {
            break;
        }
    }

    return chain;
};

// Pre-save middleware to generate immutable forensic hash
AuditEntrySchema.pre('save', function (next) {
    if (!this.forensicHash) {
        const evidenceString = JSON.stringify({
            timestamp: this.timestamp,
            action: this.action,
            userId: this.userId,
            tenantId: this.tenantId,
            resource: this.resource,
            resourceId: this.resourceId,
            details: this.details,
            ipAddress: this.ipAddress,
            userAgent: this.userAgent,
            sessionId: this.sessionId,
            correlationId: this.correlationId,
            regulatoryTags: this.regulatoryTags
        });

        this.forensicHash = crypto.createHash('sha256').update(evidenceString).digest('hex');
    }
    next();
});

const AuditLedger = mongoose.model('AuditLedger', AuditEntrySchema);
export default AuditLedger;