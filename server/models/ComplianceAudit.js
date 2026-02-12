const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');
const crypto = require('crypto');

const AUDIT_TYPES = {
    TRUST_RECONCILIATION: 'TRUST_RECONCILIATION',
    CPD_COMPLIANCE: 'CPD_COMPLIANCE',
    FIDELITY_CERTIFICATE: 'FIDELITY_CERTIFICATE',
    POPIA_COMPLIANCE: 'POPIA_COMPLIANCE'
};

const AUDIT_STATUS = {
    PENDING: 'PENDING',
    IN_PROGRESS: 'IN_PROGRESS',
    COMPLETED: 'COMPLETED',
    FAILED: 'FAILED'
};

const SEVERITY_LEVELS = {
    CRITICAL: 'CRITICAL',
    HIGH: 'HIGH',
    MEDIUM: 'MEDIUM',
    LOW: 'LOW'
};

const complianceAuditSchema = new mongoose.Schema({
    auditId: {
        type: String,
        required: true,
        unique: true,
        default: () => `AUDIT-${uuidv4()}`
    },
    
    tenantId: { type: String, required: true, index: true },
    auditType: { type: String, enum: Object.values(AUDIT_TYPES), required: true },
    
    subjectId: { type: mongoose.Schema.Types.ObjectId, required: true, refPath: 'subjectModel' },
    subjectModel: { type: String, required: true, enum: ['AttorneyProfile', 'TrustAccount', 'CPDRecord'] },
    subjectIdentifier: { type: String, required: true },
    
    findings: [{
        findingId: { type: String, default: () => `FIND-${uuidv4()}` },
        description: { type: String, required: true },
        severity: { type: String, enum: Object.values(SEVERITY_LEVELS), required: true },
        status: { type: String, enum: ['OPEN', 'REMEDIATED', 'ACCEPTED'], default: 'OPEN' }
    }],
    
    score: { type: Number, min: 0, max: 100, required: true },
    reportData: { type: mongoose.Schema.Types.Mixed, required: true },
    reportHash: { type: String, required: true },
    
    auditor: { type: String, required: true },
    auditDate: { type: Date, default: Date.now },
    completedAt: Date,
    
    workflow: {
        status: { type: String, enum: Object.values(AUDIT_STATUS), default: 'PENDING' }
    },
    
    createdBy: { type: String, required: true },
    updatedBy: { type: String, required: true },
    deleted: { type: Boolean, default: false }
}, { timestamps: true });

module.exports = mongoose.model('ComplianceAudit', complianceAuditSchema);
