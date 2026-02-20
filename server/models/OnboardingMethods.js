/*╔══════════════════════════════════════════════════════════════════════════════╗
  ║ ONBOARDING METHODS - LEGAL GRADE ● FORENSIC ● PRODUCTION                    ║
  ║ FICA Compliant | POPIA Compliant | Multi-tenant | Blockchain Ready         ║
  ║ Version: 1.0.0 - Sovereign Shield - Method Isolation                       ║
  ╚══════════════════════════════════════════════════════════════════════════════╝*/

'use strict';

const crypto = require('crypto');
const { DateTime } = require('luxon');

// =================================================================================================================
// CONSTANTS - Must match schema constants
// =================================================================================================================
const ONBOARDING_STAGES = {
    INITIATED: { id: 'INITIATED', name: 'Onboarding Initiated', order: 0, requiredRole: null },
    CLIENT_INFO: { id: 'CLIENT_INFO', name: 'Client Information', order: 1, requiredRole: null },
    FICA_SCREENING: { id: 'FICA_SCREENING', name: 'FICA Screening', order: 2, requiredRole: null },
    DOCUMENT_UPLOAD: { id: 'DOCUMENT_UPLOAD', name: 'Document Upload', order: 3, requiredRole: null },
    DOCUMENT_VERIFICATION: { id: 'DOCUMENT_VERIFICATION', name: 'Document Verification', order: 4, requiredRole: null },
    REVIEW: { id: 'REVIEW', name: 'Legal Review', order: 5, requiredRole: 'legal_officer' },
    COMPLETED: { id: 'COMPLETED', name: 'Completed', order: 6, requiredRole: null }
};

const RISK_LEVELS = {
    LOW: 'LOW',
    MEDIUM: 'MEDIUM',
    HIGH: 'HIGH',
    CRITICAL: 'CRITICAL'
};

// =================================================================================================================
// INSTANCE METHODS - Sovereign Shield
// =================================================================================================================

/**
 * Advance to next stage with full legal audit trail
 */
exports.advanceStage = async function(stageId, data = {}, performedBy, options = {}) {
    const stage = ONBOARDING_STAGES[stageId];
    if (!stage) {
        throw new Error(`Invalid stage: ${stageId}`);
    }
    
    // Check if stage requires approval
    if (stage.requiredRole && (!options.approvedBy || options.approvedBy !== stage.requiredRole)) {
        throw new Error(`Stage ${stageId} requires approval by ${stage.requiredRole}`);
    }
    
    const previousHash = this.stages && this.stages.length > 0 
        ? this.stages[this.stages.length - 1].hash 
        : '0'.repeat(64);
    
    const stageEntry = {
        stage: stageId,
        status: 'COMPLETED',
        timestamp: new Date(),
        data,
        performedBy: performedBy || this.metadata?.createdBy || 'system',
        performedByRole: options.role,
        ipAddress: options.ipAddress,
        userAgent: options.userAgent,
        previousHash,
        correlationId: `corr_${Date.now()}_${crypto.randomBytes(4).toString('hex')}`,
        requiresApproval: !!stage.requiredRole,
        approvedBy: options.approvedBy,
        approvedAt: options.approvedAt,
        approvalNotes: options.approvalNotes
    };
    
    // Generate hash
    stageEntry.hash = crypto
        .createHash('sha256')
        .update(`${previousHash}|${stageEntry.stage}|${stageEntry.status}|${stageEntry.timestamp.getTime()}|${JSON.stringify(stageEntry.data)}|${stageEntry.performedBy}`)
        .digest('hex');
    
    if (!this.stages) this.stages = [];
    this.stages.push(stageEntry);
    this.currentStage = stageId;
    
    // Update metadata
    if (!this.metadata) this.metadata = {};
    this.metadata.updatedAt = new Date();
    this.metadata.updatedBy = performedBy;
    this.metadata.version = (this.metadata.version || 0) + 1;
    
    return this.save();
};

/**
 * Add document with full legal chain of custody
 */
exports.addDocument = async function(documentData, options = {}) {
    const required = ['documentId', 'documentType', 'fileHash'];
    for (const field of required) {
        if (!documentData[field]) {
            throw new Error(`Missing required document field: ${field}`);
        }
    }
    
    const document = {
        ...documentData,
        uploadedAt: new Date(),
        uploadedBy: options.uploadedBy || this.metadata?.createdBy || 'system',
        uploadedByIp: options.ipAddress,
        chainOfCustody: [{
            action: 'UPLOADED',
            performedBy: options.uploadedBy || this.metadata?.createdBy || 'system',
            timestamp: new Date(),
            ipAddress: options.ipAddress,
            reason: options.reason || 'Initial upload'
        }]
    };
    
    if (!this.documents) this.documents = [];
    this.documents.push(document);
    
    // Update metadata
    if (!this.metadata) this.metadata = {};
    this.metadata.updatedAt = new Date();
    this.metadata.updatedBy = options.uploadedBy;
    this.metadata.version = (this.metadata.version || 0) + 1;
    
    return this.save();
};

/**
 * Verify document with legal validation
 */
exports.verifyDocument = async function(documentId, verificationData, performedBy) {
    if (!this.documents) this.documents = [];
    const document = this.documents.find(d => d.documentId === documentId);
    if (!document) {
        throw new Error(`Document ${documentId} not found`);
    }
    
    document.verified = true;
    document.verifiedAt = new Date();
    document.verifiedBy = performedBy;
    document.verificationNotes = verificationData.notes;
    
    if (!document.chainOfCustody) document.chainOfCustody = [];
    document.chainOfCustody.push({
        action: 'VERIFIED',
        performedBy,
        timestamp: new Date(),
        reason: verificationData.notes
    });
    
    if (!this.metadata) this.metadata = {};
    this.metadata.updatedAt = new Date();
    this.metadata.updatedBy = performedBy;
    
    return this.save();
};

/**
 * Update FICA status with full audit trail
 */
exports.updateFICAStatus = async function(status, data, performedBy) {
    const validTransitions = {
        'PENDING': ['IN_PROGRESS', 'APPROVED', 'REJECTED'],
        'IN_PROGRESS': ['APPROVED', 'REJECTED', 'ESCALATED'],
        'APPROVED': ['EXPIRED'],
        'REJECTED': ['ESCALATED'],
        'ESCALATED': ['APPROVED', 'REJECTED']
    };
    
    const currentStatus = this.fica?.status || 'PENDING';
    if (!validTransitions[currentStatus]?.includes(status)) {
        throw new Error(`Invalid FICA status transition from ${currentStatus} to ${status}`);
    }
    
    if (!this.fica) this.fica = {};
    this.fica.status = status;
    
    if (status === 'APPROVED') {
        this.fica.reference = data.reference || `FICA-${DateTime.now().toFormat('yyyyMMdd')}-${crypto.randomBytes(2).toString('hex').toUpperCase()}`;
        this.fica.riskScore = data.riskScore;
        this.fica.riskLevel = data.riskLevel;
        if (!this.legalCompliance) this.legalCompliance = {};
        this.legalCompliance.ficaCompliant = true;
        this.legalCompliance.ficaCompliantAt = new Date();
        this.legalCompliance.ficaCompliantBy = performedBy;
    }
    
    if (!this.fica.screeningHistory) this.fica.screeningHistory = [];
    this.fica.screeningHistory.push({
        screenedAt: new Date(),
        screenedBy: performedBy,
        status,
        reference: data.reference,
        notes: data.notes
    });
    
    if (!this.metadata) this.metadata = {};
    this.metadata.updatedAt = new Date();
    this.metadata.updatedBy = performedBy;
    
    return this.save();
};

/**
 * Update risk assessment
 */
exports.updateRiskAssessment = async function(assessment, performedBy) {
    if (!this.risk) this.risk = {};
    
    // Save previous assessment to history
    if (this.risk.score !== undefined) {
        if (!this.risk.assessmentHistory) this.risk.assessmentHistory = [];
        this.risk.assessmentHistory.push({
            assessedAt: new Date(),
            assessedBy: performedBy,
            score: this.risk.score,
            level: this.risk.level,
            factors: this.risk.factors,
            notes: 'Previous assessment'
        });
    }
    
    this.risk.score = assessment.score;
    this.risk.factors = assessment.factors || [];
    
    // Determine risk level
    if (this.risk.score >= 90) this.risk.level = 'CRITICAL';
    else if (this.risk.score >= 75) this.risk.level = 'HIGH';
    else if (this.risk.score >= 50) this.risk.level = 'MEDIUM';
    else this.risk.level = 'LOW';
    
    if (!this.metadata) this.metadata = {};
    this.metadata.updatedAt = new Date();
    this.metadata.updatedBy = performedBy;
    
    return this.save();
};

/**
 * Place on legal hold
 */
exports.placeOnLegalHold = async function(reason, initiatedBy, options = {}) {
    if (!this.compliance) this.compliance = {};
    if (!this.compliance.legalHold) this.compliance.legalHold = {};
    
    this.compliance.legalHold = {
        active: true,
        reason,
        initiatedBy,
        initiatedAt: new Date(),
        expiresAt: options.expiresAt || new Date(Date.now() + 365 * 24 * 60 * 60 * 1000),
        caseNumber: options.caseNumber
    };
    
    if (!this.metadata) this.metadata = {};
    this.metadata.updatedAt = new Date();
    this.metadata.updatedBy = initiatedBy;
    
    return this.save();
};

/**
 * Release legal hold
 */
exports.releaseLegalHold = async function(releasedBy, reason) {
    if (!this.compliance?.legalHold?.active) {
        throw new Error('No active legal hold found');
    }
    
    this.compliance.legalHold.active = false;
    this.compliance.legalHold.releasedBy = releasedBy;
    this.compliance.legalHold.releasedAt = new Date();
    this.compliance.legalHold.releaseReason = reason;
    
    if (!this.metadata) this.metadata = {};
    this.metadata.updatedAt = new Date();
    this.metadata.updatedBy = releasedBy;
    
    return this.save();
};

/**
 * Get comprehensive legal summary
 */
exports.getLegalSummary = function() {
    return {
        sessionId: this.sessionId,
        tenantId: this.tenantId,
        clientType: this.clientType,
        clientName: this.clientData?.businessName || 
                   `${this.clientData?.firstName || ''} ${this.clientData?.lastName || ''}`.trim() || 'Unknown',
        status: this.status,
        currentStage: this.currentStage,
        fica: {
            status: this.fica?.status,
            reference: this.fica?.reference,
            compliant: this.legalCompliance?.ficaCompliant || false
        },
        risk: {
            score: this.risk?.score,
            level: this.risk?.level
        },
        compliance: {
            legalHold: this.compliance?.legalHold?.active || false
        },
        documents: {
            total: this.documents?.length || 0,
            verified: this.documents ? this.documents.filter(d => d.verified).length : 0
        },
        timeline: {
            created: this.metadata?.createdAt,
            lastUpdated: this.metadata?.updatedAt
        }
    };
};

/**
 * Get complete audit trail
 */
exports.getAuditTrail = function() {
    return {
        stages: (this.stages || []).map(s => ({
            stage: s.stage,
            timestamp: s.timestamp,
            performedBy: s.performedBy,
            hash: s.hash,
            previousHash: s.previousHash
        })),
        integrity: this.verifyAuditTrail()
    };
};

/**
 * Verify audit trail integrity
 */
exports.verifyAuditTrail = function() {
    if (!this.stages || this.stages.length === 0) {
        return { valid: true, message: 'No audit trail to verify' };
    }
    
    for (let i = 0; i < this.stages.length; i++) {
        const stage = this.stages[i];
        const previousHash = i === 0 ? '0'.repeat(64) : this.stages[i - 1].hash;
        
        const calculatedHash = crypto
            .createHash('sha256')
            .update(`${previousHash}|${stage.stage}|${stage.status}|${stage.timestamp.getTime()}|${JSON.stringify(stage.data)}|${stage.performedBy}`)
            .digest('hex');
        
        if (calculatedHash !== stage.hash) {
            return { valid: false, brokenAt: i };
        }
    }
    
    return { valid: true, stages: this.stages.length };
};

/**
 * Export for legal discovery
 */
exports.exportForDiscovery = function() {
    const data = this.toObject();
    delete data.__v;
    
    return {
        ...data,
        exportMetadata: {
            exportedAt: new Date().toISOString(),
            verifiedBy: this.verifyAuditTrail()
        }
    };
};

/**
 * Get summary for dashboard
 */
exports.getSummary = function() {
    return {
        sessionId: this.sessionId,
        tenantId: this.tenantId,
        clientType: this.clientType,
        status: this.status,
        currentStage: this.currentStage,
        stageCount: this.stages?.length || 0,
        documentCount: this.documents?.length || 0,
        riskLevel: this.risk?.level,
        ficaStatus: this.fica?.status,
        legalHold: this.compliance?.legalHold?.active || false,
        createdAt: this.metadata?.createdAt
    };
};
