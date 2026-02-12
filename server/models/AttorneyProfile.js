const mongoose = require('mongoose');
const crypto = require('crypto');
const auditLogger = require('../utils/auditLogger');
const { redactSensitiveData } = require('../utils/popiaRedaction');

const ATTORNEY_STATUS = {
    ACTIVE: 'ACTIVE',
    SUSPENDED: 'SUSPENDED',
    EXPIRED: 'EXPIRED',
    DECEASED: 'DECEASED',
    RESIGNED: 'RESIGNED',
    RETIRED: 'RETIRED',
    NON_PRACTICING: 'NON_PRACTICING'
};

const PRACTICE_TYPES = {
    PRIVATE: 'PRIVATE',
    GOVERNMENT: 'GOVERNMENT',
    CORPORATE: 'CORPORATE',
    LEGAL_AID: 'LEGAL_AID',
    ACADEMIC: 'ACADEMIC',
    NON_PRACTICING: 'NON_PRACTICING'
};

const PRACTICE_AREAS = {
    URBAN: 'URBAN',
    RURAL: 'RURAL',
    INTERNATIONAL: 'INTERNATIONAL'
};

const FIDELITY_STATUS = {
    ACTIVE: 'ACTIVE',
    EXPIRED: 'EXPIRED',
    REVOKED: 'REVOKED',
    PENDING: 'PENDING'
};

const attorneyProfileSchema = new mongoose.Schema({
    lpcNumber: {
        type: String,
        required: [true, 'LPC number is required'],
        unique: true,
        uppercase: true,
        trim: true,
        immutable: true,
        validate: {
            validator: function(v) {
                return /^(LPC-\d{8}|\d{4}\/\d{4})$/.test(v);
            },
            message: props => `${props.value} is not a valid LPC number`
        },
        index: true
    },
    
    tenantId: {
        type: String,
        required: [true, 'Tenant isolation violation: tenantId is required'],
        index: true,
        immutable: true
    },
    
    practice: {
        name: { type: String, required: true },
        type: { type: String, enum: Object.values(PRACTICE_TYPES), required: true },
        area: { type: String, enum: Object.values(PRACTICE_AREAS), required: true },
        commencementDate: { type: Date, required: true },
        yearsOfPractice: { type: Number, default: 0 }
    },
    
    fidelityFund: {
        certificateNumber: { type: String },
        issueDate: Date,
        expiryDate: Date,
        status: { type: String, enum: Object.values(FIDELITY_STATUS), default: 'PENDING' }
    },
    
    cpd: {
        currentYear: { type: Number, default: new Date().getFullYear() },
        hoursCompleted: { type: Number, default: 0 },
        ethicsHours: { type: Number, default: 0 },
        complianceStatus: { type: String, enum: ['COMPLIANT', 'NON_COMPLIANT', 'PENDING'], default: 'PENDING' }
    },
    
    createdBy: { type: String, required: true },
    updatedBy: { type: String, required: true },
    deleted: { type: Boolean, default: false }
}, { timestamps: true });

module.exports = mongoose.model('AttorneyProfile', attorneyProfileSchema);
