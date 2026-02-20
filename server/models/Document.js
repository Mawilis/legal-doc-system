'use strict';
const mongoose = require('mongoose');
const auditLogger = require('../utils/auditLogger');
const cryptoUtils = require('../utils/cryptoUtils');

const documentSchema = new mongoose.Schema({
    documentId: {
        type: String,
        required: true,
        unique: true,
        index: true
    },
    originalName: String,
    storagePath: String,
    fileHash: {
        type: String,
        required: true,
        validate: {
            validator: function(v) {
                return /^[a-f0-9]{64}$/.test(v);
            },
            message: 'File hash must be a valid SHA-256 hash'
        }
    },
    claimedType: { 
        type: String, 
        enum: ['ID_DOCUMENT', 'PROOF_OF_ADDRESS', 'PROOF_OF_INCOME', 'COMPANY_REGISTRATION', 'TAX_CLEARANCE', 'FINANCIAL_STATEMENTS', 'TRUST_DEED', 'BANK_STATEMENT'] 
    },
    aiType: String,
    confidence: Number,
    verificationStatus: { 
        type: String, 
        enum: ['PENDING', 'VERIFIED', 'MISMATCH', 'FLAGGED'], 
        default: 'PENDING' 
    },
    metadata: {
        uploadedAt: { type: Date, default: Date.now },
        uploadedBy: String,
        uploadedByIp: String,
        fileSize: Number,
        mimeType: String,
        pageCount: Number
    },
    auditLog: [{
        action: String,
        timestamp: { type: Date, default: Date.now },
        performedBy: String,
        ipAddress: String,
        details: mongoose.Schema.Types.Mixed,
        hash: String
    }]
}, { 
    timestamps: true,
    collection: 'documents'
});

// Pre-save middleware to generate audit hash
documentSchema.pre('save', async function(next) {
    if (this.isNew) {
        // Generate file hash using cryptoUtils
        if (this.fileData) {
            this.fileHash = cryptoUtils.generateForensicHash(this.fileData);
        }
        
        // Create audit log entry
        const auditEntry = {
            action: 'DOCUMENT_CREATED',
            timestamp: new Date(),
            performedBy: this.metadata?.uploadedBy || 'system',
            ipAddress: this.metadata?.uploadedByIp,
            details: {
                documentId: this.documentId,
                documentType: this.claimedType,
                fileName: this.originalName
            }
        };
        
        // Generate hash for audit entry
        auditEntry.hash = cryptoUtils.generateForensicHash(auditEntry);
        this.auditLog.push(auditEntry);
        
        // Log to audit system
        await auditLogger.audit({
            action: 'DOCUMENT_CREATED',
            documentId: this.documentId,
            tenantId: this.tenantId,
            userId: this.metadata?.uploadedBy,
            details: {
                documentType: this.claimedType,
                fileHash: this.fileHash?.substring(0, 8)
            }
        });
    }
    next();
});

// Method to add audit entry
documentSchema.methods.addAuditEntry = async function(action, performedBy, details = {}, ipAddress = null) {
    const entry = {
        action,
        timestamp: new Date(),
        performedBy,
        ipAddress,
        details
    };
    
    // Generate hash for the entry
    entry.hash = cryptoUtils.generateForensicHash(entry);
    this.auditLog.push(entry);
    
    // Also log to central audit system
    await auditLogger.audit({
        action,
        documentId: this.documentId,
        userId: performedBy,
        details
    });
    
    return this.save();
};

// Method to verify document integrity
documentSchema.methods.verifyIntegrity = function() {
    if (!this.fileData && !this.fileHash) {
        return { valid: false, reason: 'No file data or hash available' };
    }
    
    if (this.fileData) {
        const computedHash = cryptoUtils.generateForensicHash(this.fileData);
        return {
            valid: computedHash === this.fileHash,
            computedHash,
            storedHash: this.fileHash
        };
    }
    
    return { valid: true, message: 'File data not available for verification' };
};

// Method to update AI classification
documentSchema.methods.updateAIClassification = async function(aiType, confidence, performedBy = 'ai-system') {
    this.aiType = aiType;
    this.confidence = confidence;
    
    if (confidence > 0.6 && aiType === this.claimedType) {
        this.verificationStatus = 'VERIFIED';
    } else if (confidence < 0.3) {
        this.verificationStatus = 'FLAGGED';
    } else {
        this.verificationStatus = 'MISMATCH';
    }
    
    await this.addAuditEntry('AI_CLASSIFICATION_UPDATED', performedBy, {
        aiType,
        confidence,
        claimedType: this.claimedType,
        verificationStatus: this.verificationStatus
    });
    
    return this;
};

// Method to get classification summary
documentSchema.methods.getClassificationSummary = function() {
    return {
        documentId: this.documentId,
        claimedType: this.claimedType,
        aiType: this.aiType,
        confidence: this.confidence,
        verificationStatus: this.verificationStatus,
        uploadedAt: this.metadata?.uploadedAt,
        uploadedBy: this.metadata?.uploadedBy,
        auditCount: this.auditLog?.length || 0
    };
};

// Static method to find documents by verification status
documentSchema.statics.findByVerificationStatus = function(status) {
    return this.find({ verificationStatus: status });
};

// Static method to get AI statistics
documentSchema.statics.getAIStatistics = async function() {
    const stats = await this.aggregate([
        {
            $group: {
                _id: '$verificationStatus',
                count: { $sum: 1 },
                avgConfidence: { $avg: '$confidence' },
                documents: { $push: { documentId: '$documentId', claimedType: '$claimedType', aiType: '$aiType' } }
            }
        }
    ]);
    
    // Also log to audit system
    await auditLogger.audit({
        action: 'AI_STATISTICS_GENERATED',
        details: { stats }
    });
    
    return stats;
};

module.exports = mongoose.model('Document', documentSchema);
