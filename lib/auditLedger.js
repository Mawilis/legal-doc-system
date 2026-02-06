/**
 * =============================================================================
 * WILSY OS - IMMUTABLE AUDIT LEDGER
 * PURPOSE: Append-only ledger with OTS anchoring & tenant isolation
 * =============================================================================
 */
const mongoose = require('mongoose');
const crypto = require('crypto');

const AuditEntrySchema = new mongoose.Schema({
    tenantId: { type: String, required: true, index: true },
    actorId: { type: mongoose.Schema.Types.ObjectId, required: true },
    action: { type: String, required: true },
    resourceId: mongoose.Schema.Types.ObjectId,
    resourceType: String,
    
    // Metadata for POPIA §18(1)
    metadata: {
        ipAddress: String,
        userAgent: String,
        purpose: String
    },

    // Cryptographic Chain
    prevHash: { type: String, required: true },
    currentHash: { type: String, required: true, unique: true },
    
    // OTS (OpenTimestamps) Placeholder
    otsProof: { type: String }, 
    isAnchored: { type: Boolean, default: false }
}, { timestamps: true, capped: { size: 5242880, max: 5000 } }); // Capped collection for performance

// --- SECURITY LOGIC: HASH CHAINING ---
AuditEntrySchema.pre('validate', async function(next) {
    if (this.isNew) {
        // 1. Fetch the last entry for this tenant to get the previous hash
        const lastEntry = await mongoose.model('AuditEntry')
            .findOne({ tenantId: this.tenantId })
            .sort({ createdAt: -1 });

        this.prevHash = lastEntry ? lastEntry.currentHash : 'GENESIS_BLOCK';

        // 2. Calculate Current Hash (Action + Resource + PrevHash + Timestamp)
        const dataToHash = `${this.action}${this.resourceId}${this.prevHash}${this.tenantId}`;
        this.currentHash = crypto.createHash('sha256').update(dataToHash).digest('hex');
    }
    next();
});

// Protect against modifications (Immutable)
AuditEntrySchema.pre('save', function(next) {
    if (!this.isNew) {
        return next(new Error('AUDIT_LEDGER_ERROR: Entries are immutable and cannot be modified.'));
    }
    next();
});

module.exports = mongoose.model('AuditEntry', AuditEntrySchema);
