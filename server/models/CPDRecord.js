const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');
const crypto = require('crypto');

const CPD_CATEGORIES = {
    SUBSTANTIVE: 'SUBSTANTIVE',
    ETHICS: 'ETHICS',
    PRACTICE_MANAGEMENT: 'PRACTICE_MANAGEMENT',
    PROFESSIONAL_SKILLS: 'PROFESSIONAL_SKILLS'
};

const CPD_STATUS = {
    PENDING_VERIFICATION: 'PENDING_VERIFICATION',
    VERIFIED: 'VERIFIED',
    REJECTED: 'REJECTED',
    AUTO_VERIFIED: 'AUTO_VERIFIED'
};

const PROVIDER_TYPES = {
    LPC_ACCREDITED: 'LPC_ACCREDITED',
    UNIVERSITY: 'UNIVERSITY',
    LAW_SOCIETY: 'LAW_SOCIETY',
    PRIVATE_PROVIDER: 'PRIVATE_PROVIDER'
};

const cpdRecordSchema = new mongoose.Schema({
    activityId: {
        type: String,
        required: true,
        unique: true,
        default: () => `CPD-${uuidv4()}`
    },
    
    attorneyId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'AttorneyProfile',
        required: true
    },
    
    attorneyLpcNumber: { type: String, required: true },
    tenantId: { type: String, required: true, index: true },
    
    activityName: { type: String, required: true },
    activityDate: { type: Date, required: true },
    year: { type: Number, required: true },
    
    hours: { type: Number, required: true, min: 0.5, max: 8 },
    category: { type: String, enum: Object.values(CPD_CATEGORIES), required: true },
    
    provider: {
        name: { type: String, required: true },
        type: { type: String, enum: Object.values(PROVIDER_TYPES) },
        accreditationNumber: String
    },
    
    evidence: {
        certificateUrl: { type: String, required: true },
        certificateHash: { type: String, required: true }
    },
    
    verificationStatus: { type: String, enum: Object.values(CPD_STATUS), default: 'PENDING_VERIFICATION' },
    verificationCode: { type: String, unique: true, sparse: true },
    verifiedAt: Date,
    verifiedBy: String,
    
    submittedBy: { type: String, required: true },
    submissionDate: { type: Date, default: Date.now },
    
    certificateGenerated: { type: Boolean, default: false },
    complianceCertificate: mongoose.Schema.Types.Mixed,
    
    deleted: { type: Boolean, default: false }
}, { timestamps: true });

module.exports = mongoose.model('CPDRecord', cpdRecordSchema);
