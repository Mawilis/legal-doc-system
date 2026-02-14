const mongoose = require('mongoose');
const { Schema } = mongoose;

const AuditEntrySchema = new Schema({
    timestamp: { type: Date, default: Date.now, required: true, index: true },
    action: { type: String, required: true, index: true },
    userId: { type: String, required: true, index: true },
    tenantId: { type: String, required: true, index: true },
    resource: { type: String, required: true },
    resourceId: { type: String },
    details: { type: Schema.Types.Mixed },
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
    metadata: { type: Schema.Types.Mixed, default: {} },
    retentionPolicy: String,
    retentionStart: Date,
    dataResidency: { type: String, default: 'ZA' }
});

// Add indexes for common queries
AuditEntrySchema.index({ tenantId: 1, timestamp: -1 });
AuditEntrySchema.index({ userId: 1, timestamp: -1 });
AuditEntrySchema.index({ resource: 1, resourceId: 1 });
AuditEntrySchema.index({ forensicHash: 1 }, { unique: true });

const AuditLedger = mongoose.model('AuditLedger', AuditEntrySchema);
module.exports = AuditLedger;
