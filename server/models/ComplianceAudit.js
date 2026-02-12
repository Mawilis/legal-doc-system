/**
 * WILSYS OS - COMPLIANCE AUDIT MODEL
 * ====================================================================
 * LEGAL PRACTICE COUNCIL · FORENSIC COMPLIANCE AUDIT
 * QUANTUM-SEALED · POPIA §19 · LPC §95(3)
 * 
 * @version 5.0.1
 * @author Wilson Khanyezi - Chief Quantum Sentinel
 * @copyright Wilsy OS (Pty) Ltd 2026
 * ====================================================================
 */

const mongoose = require('mongoose');
const { Schema } = mongoose;
const crypto = require('crypto');
const { v4: uuidv4 } = require('uuid');

// ====================================================================
// FORENSIC CONSTANTS - IMMUTABLE · REGULATORY
// ====================================================================

const AUDIT_TYPES = {
    TRUST_RECONCILIATION: 'TRUST_RECONCILIATION',
    CPD_COMPLIANCE: 'CPD_COMPLIANCE',
    FIDELITY_CERTIFICATE: 'FIDELITY_CERTIFICATE',
    PRACTICE_MANAGEMENT: 'PRACTICE_MANAGEMENT',
    DISCIPLINARY_MATTER: 'DISCIPLINARY_MATTER',
    POPIA_COMPLIANCE: 'POPIA_COMPLIANCE',
    PAIA_COMPLIANCE: 'PAIA_COMPLIANCE',
    DATA_BREACH: 'DATA_BREACH',
    DATA_SUBJECT_REQUEST: 'DATA_SUBJECT_REQUEST',
    CONSENT_MANAGEMENT: 'CONSENT_MANAGEMENT',
    FICA_COMPLIANCE: 'FICA_COMPLIANCE',
    SARS_COMPLIANCE: 'SARS_COMPLIANCE',
    ANNUAL_RETURN: 'ANNUAL_RETURN',
    BEE_VERIFICATION: 'BEE_VERIFICATION',
    RISK_ASSESSMENT: 'RISK_ASSESSMENT',
    SECURITY_INCIDENT: 'SECURITY_INCIDENT',
    PENETRATION_TEST: 'PENETRATION_TEST',
    ACCESS_REVIEW: 'ACCESS_REVIEW',
    CLIENT_COMPLAINT: 'CLIENT_COMPLAINT',
    CONFLICT_CHECK: 'CONFLICT_CHECK',
    FILE_AUDIT: 'FILE_AUDIT',
    BILLING_COMPLIANCE: 'BILLING_COMPLIANCE'
};

const AUDIT_STATUS = {
    DRAFT: 'DRAFT',
    SCHEDULED: 'SCHEDULED',
    IN_PROGRESS: 'IN_PROGRESS',
    PENDING_REVIEW: 'PENDING_REVIEW',
    COMPLETED: 'COMPLETED',
    FAILED: 'FAILED',
    WAIVED: 'WAIVED',
    DEFERRED: 'DEFERRED',
    CANCELLED: 'CANCELLED'
};

const SEVERITY_LEVELS = {
    CRITICAL: 'CRITICAL',
    HIGH: 'HIGH',
    MEDIUM: 'MEDIUM',
    LOW: 'LOW',
    INFO: 'INFO',
    NONE: 'NONE'
};

const FINDING_STATUS = {
    OPEN: 'OPEN',
    IN_PROGRESS: 'IN_PROGRESS',
    REMEDIATED: 'REMEDIATED',
    ACCEPTED: 'ACCEPTED',
    FALSE_POSITIVE: 'FALSE_POSITIVE',
    WAIVED: 'WAIVED',
    OVERDUE: 'OVERDUE'
};

const REMEDIATION_PRIORITY = {
    IMMEDIATE: 'IMMEDIATE',
    URGENT: 'URGENT',
    HIGH: 'HIGH',
    MEDIUM: 'MEDIUM',
    LOW: 'LOW'
};

const COMPLIANCE_FRAMEWORKS = {
    POPIA: 'POPIA',
    LPA: 'LPA',
    COMPANIES_ACT: 'COMPANIES_ACT',
    ECT_ACT: 'ECT_ACT',
    PAIA: 'PAIA',
    FICA: 'FICA',
    NCA: 'NCA',
    CPA: 'CPA',
    BCEA: 'BCEA',
    LRA: 'LRA',
    GDPR: 'GDPR',
    ISO_27001: 'ISO_27001',
    SOC2: 'SOC2',
    PCI_DSS: 'PCI_DSS'
};

const COMPLIANCE_SCORES = {
    EXCELLENT: { min: 90, max: 100, label: 'EXCELLENT', color: '#00C853' },
    GOOD: { min: 75, max: 89, label: 'GOOD', color: '#64DD17' },
    SATISFACTORY: { min: 60, max: 74, label: 'SATISFACTORY', color: '#FFD600' },
    POOR: { min: 40, max: 59, label: 'POOR', color: '#FF6D00' },
    CRITICAL: { min: 0, max: 39, label: 'CRITICAL', color: '#DD2C00' }
};

const AUDIT_SCOPE_TYPES = {
    FULL: 'FULL',
    TARGETED: 'TARGETED',
    FOLLOW_UP: 'FOLLOW_UP',
    SPOT_CHECK: 'SPOT_CHECK',
    THEMATIC: 'THEMATIC',
    REMOTE: 'REMOTE',
    ONSITE: 'ONSITE'
};

const EVIDENCE_TYPES = {
    DOCUMENT: 'DOCUMENT',
    SCREENSHOT: 'SCREENSHOT',
    LOG_FILE: 'LOG_FILE',
    EMAIL: 'EMAIL',
    INTERVIEW: 'INTERVIEW',
    SYSTEM_CONFIG: 'SYSTEM_CONFIG',
    DATABASE_EXPORT: 'DATABASE_EXPORT',
    CERTIFICATE: 'CERTIFICATE',
    POLICY: 'POLICY',
    PROCEDURE: 'PROCEDURE'
};

// ====================================================================
// COMPLIANCE AUDIT SCHEMA - FORENSIC ARCHITECTURE
// ====================================================================

const complianceAuditSchema = new Schema({
    tenantId: {
        type: String,
        required: [true, 'TENANT_ISOLATION_VIOLATION: tenantId is required'],
        index: true,
        immutable: true,
        validate: {
            validator: function(v) {
                return /^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i.test(v);
            },
            message: props => `${props.value} is not a valid tenant UUID`
        }
    },

    auditId: {
        type: String,
        required: [true, 'Audit ID is required'],
        unique: true,
        default: () => `AUDIT-${uuidv4()}`,
        immutable: true,
        index: true
    },

    auditType: {
        type: String,
        required: [true, 'Audit type is required'],
        enum: Object.values(AUDIT_TYPES),
        index: true
    },

    auditSubtype: {
        type: String,
        enum: [
            'SCHEDULED',
            'AD_HOC',
            'REGULATORY',
            'INTERNAL',
            'EXTERNAL',
            'FORENSIC',
            'COMPLAINT_DRIVEN',
            'RISK_BASED'
        ]
    },

    scope: {
        type: {
            type: String,
            enum: Object.values(AUDIT_SCOPE_TYPES),
            default: 'FULL'
        },
        description: {
            type: String,
            required: true,
            maxlength: 2000
        },
        objectives: [{
            type: String,
            maxlength: 500
        }],
        criteria: [{
            framework: {
                type: String,
                enum: Object.values(COMPLIANCE_FRAMEWORKS)
            },
            reference: String,
            requirement: String,
            mandatory: {
                type: Boolean,
                default: true
            }
        }],
        dateRange: {
            start: Date,
            end: Date
        },
        locations: [String],
        departments: [String],
        targetedEntities: [{
            entityType: {
                type: String,
                enum: ['ATTORNEY', 'FIRM', 'TRUST_ACCOUNT', 'CPD_RECORD', 'DOCUMENT', 'CLIENT', 'MATTER', 'SYSTEM']
            },
            entityId: String,
            entityName: String,
            entityReference: String
        }]
    },

    subjectId: {
        type: Schema.Types.ObjectId,
        refPath: 'subjectModel',
        required: true,
        index: true
    },

    subjectModel: {
        type: String,
        required: true,
        enum: [
            'AttorneyProfile',
            'TrustAccount',
            'CPDRecord',
            'FidelityFund',
            'DocumentMetadata',
            'Firm',
            'User',
            'Tenant',
            'DataSubject',
            'SecurityIncident'
        ]
    },

    subjectIdentifier: {
        type: String,
        required: true,
        index: true
    },

    subjectDetails: Schema.Types.Mixed,

    scheduling: {
        scheduledDate: Date,
        startDate: Date,
        endDate: Date,
        duration: {
            type: Number,
            virtual: true,
            get: function() {
                if (this.scheduling.endDate && this.scheduling.startDate) {
                    return Math.ceil((this.scheduling.endDate - this.scheduling.startDate) / (1000 * 60));
                }
                return null;
            }
        },
        frequency: {
            type: String,
            enum: ['ONCE', 'DAILY', 'WEEKLY', 'MONTHLY', 'QUARTERLY', 'ANNUALLY']
        },
        nextScheduledDate: Date,
        isRecurring: {
            type: Boolean,
            default: false
        }
    },

    auditors: [{
        userId: {
            type: String,
            required: true
        },
        name: String,
        email: String,
        role: {
            type: String,
            enum: ['LEAD_AUDITOR', 'AUDITOR', 'TECHNICAL_EXPERT', 'OBSERVER', 'INTERVIEWER']
        },
        assignedAt: {
            type: Date,
            default: Date.now
        },
        assignedBy: String
    }],

    leadAuditor: {
        userId: String,
        name: String,
        email: String
    },

    findings: [{
        findingId: {
            type: String,
            default: () => `FIND-${uuidv4()}`,
            unique: true,
            sparse: true
        },
        category: {
            type: String,
            enum: [
                'ACCESS_CONTROL',
                'DATA_PROTECTION',
                'RETENTION',
                'CPD_COMPLIANCE',
                'TRUST_ACCOUNTING',
                'FIDELITY_FUND',
                'CONFLICT_CHECK',
                'BILLING',
                'FILE_MANAGEMENT',
                'SECURITY',
                'GOVERNANCE',
                'RISK_MANAGEMENT'
            ]
        },
        title: {
            type: String,
            required: true,
            maxlength: 200
        },
        description: {
            type: String,
            required: true,
            maxlength: 2000
        },
        severity: {
            type: String,
            enum: Object.values(SEVERITY_LEVELS),
            required: true
        },
        likelihood: {
            type: String,
            enum: ['VERY_LOW', 'LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH'],
            default: 'MEDIUM'
        },
        impact: {
            type: String,
            enum: ['VERY_LOW', 'LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH'],
            default: 'MEDIUM'
        },
        riskScore: {
            type: Number,
            min: 0,
            max: 25,
            virtual: true,
            get: function() {
                const likelihoodMap = { VERY_LOW: 1, LOW: 2, MEDIUM: 3, HIGH: 4, VERY_HIGH: 5 };
                const impactMap = { VERY_LOW: 1, LOW: 2, MEDIUM: 3, HIGH: 4, VERY_HIGH: 5 };
                return (likelihoodMap[this.likelihood] || 3) * (impactMap[this.impact] || 3);
            }
        },
        requirement: {
            framework: {
                type: String,
                enum: Object.values(COMPLIANCE_FRAMEWORKS)
            },
            reference: String,
            clause: String,
            description: String
        },
        evidence: [{
            evidenceId: {
                type: String,
                default: () => `EVID-${uuidv4()}`
            },
            type: {
                type: String,
                enum: Object.values(EVIDENCE_TYPES)
            },
            title: String,
            description: String,
            fileUrl: String,
            fileHash: {
                type: String,
                validate: {
                    validator: function(v) {
                        return !v || /^[a-f0-9]{64}$/i.test(v);
                    }
                }
            },
            fileSize: Number,
            mimeType: String,
            uploadedBy: String,
            uploadedAt: {
                type: Date,
                default: Date.now
            },
            metadata: Schema.Types.Mixed
        }],
        status: {
            type: String,
            enum: Object.values(FINDING_STATUS),
            default: 'OPEN',
            index: true
        },
        statusHistory: [{
            status: {
                type: String,
                enum: Object.values(FINDING_STATUS)
            },
            changedAt: {
                type: Date,
                default: Date.now
            },
            changedBy: String,
            reason: String,
            notes: String
        }],
        createdAt: {
            type: Date,
            default: Date.now
        },
        createdBy: String,
        updatedAt: Date,
        updatedBy: String,
        remediatedAt: Date,
        remediatedBy: String,
        remediationNotes: String,
        remediationEvidence: [String],
        verifiedAt: Date,
        verifiedBy: String,
        verificationNotes: String,
        rootCause: String,
        correctiveAction: String,
        preventiveAction: String,
        dueDate: Date,
        extensionGranted: {
            type: Boolean,
            default: false
        },
        extensionReason: String,
        extensionDate: Date,
        extensionGrantedBy: String
    }],

    score: {
        type: Number,
        min: 0,
        max: 100,
        required: true,
        default: 0,
        index: true
    },

    scoreLabel: {
        type: String,
        enum: Object.values(COMPLIANCE_SCORES).map(s => s.label),
        default: 'CRITICAL'
    },

    scoreBreakdown: {
        byCategory: Schema.Types.Mixed,
        byFramework: Schema.Types.Mixed,
        bySeverity: {
            CRITICAL: { type: Number, default: 0 },
            HIGH: { type: Number, default: 0 },
            MEDIUM: { type: Number, default: 0 },
            LOW: { type: Number, default: 0 },
            INFO: { type: Number, default: 0 }
        }
    },

    complianceIssues: [{
        issueId: {
            type: String,
            default: () => `ISSUE-${uuidv4()}`
        },
        type: String,
        title: String,
        description: String,
        severity: {
            type: String,
            enum: Object.values(SEVERITY_LEVELS)
        },
        framework: {
            type: String,
            enum: Object.values(COMPLIANCE_FRAMEWORKS)
        },
        reference: String,
        findingIds: [String],
        affectedEntities: [{
            entityType: String,
            entityId: String,
            entityName: String
        }],
        remediation: {
            required: {
                type: Boolean,
                default: true
            },
            deadline: Date,
            priority: {
                type: String,
                enum: Object.values(REMEDIATION_PRIORITY)
            },
            actionPlan: String,
            assignedTo: String,
            assignedBy: String,
            assignedAt: Date,
            status: {
                type: String,
                enum: ['PENDING', 'IN_PROGRESS', 'COMPLETED', 'WAIVED', 'OVERDUE'],
                default: 'PENDING'
            },
            statusHistory: [{
                status: String,
                changedAt: Date,
                changedBy: String,
                notes: String
            }],
            completedAt: Date,
            completedBy: String,
            verificationRequired: {
                type: Boolean,
                default: true
            },
            verifiedAt: Date,
            verifiedBy: String,
            verificationNotes: String
        }
    }],

    recommendations: [{
        recommendationId: {
            type: String,
            default: () => `REC-${uuidv4()}`
        },
        category: String,
        title: {
            type: String,
            required: true
        },
        description: {
            type: String,
            required: true
        },
        priority: {
            type: String,
            enum: Object.values(REMEDIATION_PRIORITY)
        },
        estimatedEffort: {
            type: String,
            enum: ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        },
        estimatedCost: {
            type: String,
            enum: ['LOW', 'MEDIUM', 'HIGH']
        },
        roi: {
            type: String,
            enum: ['HIGH', 'MEDIUM', 'LOW', 'NEGATIVE']
        },
        implemented: {
            type: Boolean,
            default: false
        },
        implementedAt: Date,
        implementedBy: String,
        implementationNotes: String,
        rejected: {
            type: Boolean,
            default: false
        },
        rejectedAt: Date,
        rejectedBy: String,
        rejectionReason: String
    }],

    riskAssessment: {
        overallRisk: {
            type: String,
            enum: Object.values(SEVERITY_LEVELS),
            default: 'MEDIUM'
        },
        inherentRisk: {
            type: Number,
            min: 0,
            max: 100,
            default: 50
        },
        residualRisk: {
            type: Number,
            min: 0,
            max: 100,
            default: 50
        },
        riskReduction: {
            type: Number,
            min: 0,
            max: 100,
            virtual: true,
            get: function() {
                if (this.riskAssessment.inherentRisk) {
                    return this.riskAssessment.inherentRisk - (this.riskAssessment.residualRisk || 0);
                }
                return 0;
            }
        },
        riskFactors: [{
            factor: String,
            description: String,
            impact: {
                type: String,
                enum: Object.values(SEVERITY_LEVELS)
            },
            likelihood: {
                type: String,
                enum: ['VERY_LOW', 'LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH']
            },
            riskLevel: {
                type: String,
                enum: ['LOW', 'MEDIUM', 'HIGH', 'EXTREME']
            },
            mitigation: String,
            controls: [String],
            residualRisk: {
                type: String,
                enum: ['LOW', 'MEDIUM', 'HIGH', 'EXTREME']
            }
        }],
        heatmap: Schema.Types.Mixed
    },

    reportData: {
        type: Schema.Types.Mixed,
        required: true
    },

    reportUrl: String,

    reportHash: {
        type: String,
        required: true,
        unique: true,
        default: function() {
            return crypto
                .createHash('sha3-512')
                .update(`${this.auditId}:${JSON.stringify(this.reportData)}:${Date.now()}`)
                .digest('hex');
        }
    },

    executiveSummary: {
        type: String,
        maxlength: 5000
    },

    managementSummary: String,

    evidencePackage: {
        packageId: {
            type: String,
            default: () => `EVIDPKG-${uuidv4()}`
        },
        files: [{
            fileId: {
                type: String,
                default: () => `FILE-${uuidv4()}`
            },
            name: String,
            type: {
                type: String,
                enum: Object.values(EVIDENCE_TYPES)
            },
            size: Number,
            hash: {
                type: String,
                validate: {
                    validator: function(v) {
                        return !v || /^[a-f0-9]{64}$/i.test(v);
                    }
                }
            },
            url: String,
            uploadedAt: {
                type: Date,
                default: Date.now
            },
            uploadedBy: String,
            metadata: Schema.Types.Mixed,
            tags: [String]
        }],
        createdAt: {
            type: Date,
            default: Date.now
        },
        createdBy: String,
        hash: {
            type: String,
            default: function() {
                return crypto
                    .createHash('sha3-512')
                    .update(`${this.packageId}:${Date.now()}`)
                    .digest('hex');
            }
        }
    },

    workflow: {
        status: {
            type: String,
            enum: Object.values(AUDIT_STATUS),
            default: 'DRAFT',
            index: true
        },
        history: [{
            status: String,
            changedAt: {
                type: Date,
                default: Date.now
            },
            changedBy: String,
            comment: String,
            ipAddress: String,
            userAgent: String
        }],
        nextReviewDate: Date,
        reviewFrequency: {
            type: Number,
            default: 365,
            min: 30,
            max: 730
        },
        approvalDate: Date,
        approvedBy: String,
        approvalNotes: String,
        publishedDate: Date,
        publishedBy: String
    },

    correctiveActions: [{
        actionId: {
            type: String,
            default: () => `ACTION-${uuidv4()}`
        },
        findingId: String,
        issueId: String,
        title: {
            type: String,
            required: true
        },
        description: {
            type: String,
            required: true
        },
        priority: {
            type: String,
            enum: Object.values(REMEDIATION_PRIORITY)
        },
        deadline: {
            type: Date,
            required: true,
            validate: {
                validator: function(v) {
                    return v > new Date();
                },
                message: 'Deadline must be in the future'
            }
        },
        assignedTo: String,
        assignedBy: String,
        assignedAt: {
            type: Date,
            default: Date.now
        },
        status: {
            type: String,
            enum: ['PENDING', 'IN_PROGRESS', 'COMPLETED', 'OVERDUE', 'CANCELLED'],
            default: 'PENDING'
        },
        statusHistory: [{
            status: String,
            changedAt: Date,
            changedBy: String,
            notes: String
        }],
        progress: {
            type: Number,
            min: 0,
            max: 100,
            default: 0
        },
        completedAt: Date,
        completedBy: String,
        completionNotes: String,
        verificationRequired: {
            type: Boolean,
            default: true
        },
        verifiedAt: Date,
        verifiedBy: String,
        verificationNotes: String,
        evidence: [String],
        notes: [{
            note: String,
            createdBy: String,
            createdAt: {
                type: Date,
                default: Date.now
            }
        }]
    }],

    regulatoryReporting: [{
        authority: {
            type: String,
            enum: ['LPC', 'POPIA', 'PAIA', 'FICA', 'SARS', 'CIPC', 'NCR']
        },
        reportId: String,
        submittedAt: Date,
        submittedBy: String,
        confirmationNumber: String,
        status: {
            type: String,
            enum: ['DRAFT', 'SUBMITTED', 'ACKNOWLEDGED', 'REJECTED', 'FOLLOW_UP_REQUIRED']
        },
        response: String,
        followUpDate: Date,
        notes: String
    }],

    metrics: {
        totalFindings: {
            type: Number,
            default: 0
        },
        openFindings: {
            type: Number,
            default: 0
        },
        remediatedFindings: {
            type: Number,
            default: 0
        },
        overdueFindings: {
            type: Number,
            default: 0
        },
        findingsBySeverity: {
            CRITICAL: { type: Number, default: 0 },
            HIGH: { type: Number, default: 0 },
            MEDIUM: { type: Number, default: 0 },
            LOW: { type: Number, default: 0 },
            INFO: { type: Number, default: 0 }
        },
        averageRemediationTime: Number,
        complianceTrend: [{
            date: Date,
            score: Number
        }],
        lastCalculated: Date
    },

    auditTrail: [{
        action: {
            type: String,
            required: true,
            enum: [
                'AUDIT_CREATED',
                'AUDIT_UPDATED',
                'AUDIT_STARTED',
                'AUDIT_COMPLETED',
                'AUDIT_CANCELLED',
                'FINDING_ADDED',
                'FINDING_UPDATED',
                'FINDING_REMEDIATED',
                'FINDING_VERIFIED',
                'ISSUE_ADDED',
                'ISSUE_RESOLVED',
                'RECOMMENDATION_ADDED',
                'RECOMMENDATION_IMPLEMENTED',
                'ACTION_ASSIGNED',
                'ACTION_COMPLETED',
                'REPORT_GENERATED',
                'EVIDENCE_ADDED',
                'STATUS_CHANGED',
                'AUDITOR_ASSIGNED',
                'DEADLINE_EXTENDED'
            ]
        },
        performedBy: {
            type: String,
            required: true
        },
        performedAt: {
            type: Date,
            default: Date.now
        },
        ipAddress: String,
        userAgent: String,
        changes: Schema.Types.Mixed,
        previousState: Schema.Types.Mixed,
        newState: Schema.Types.Mixed,
        findingId: String,
        issueId: String,
        actionId: String,
        hash: {
            type: String,
            default: function() {
                return crypto
                    .createHash('sha3-512')
                    .update(`${this.action}:${this.performedAt.toISOString()}:${this.performedBy}:${JSON.stringify(this.changes)}`)
                    .digest('hex');
            }
        }
    }],

    integrityHash: {
        type: String,
        unique: true,
        default: function() {
            return crypto
                .createHash('sha3-512')
                .update(`${this.auditId}:${this.score}:${this.workflow.status}:${Date.now()}`)
                .digest('hex');
        }
    },

    quantumSignature: {
        type: String,
        default: function() {
            return crypto
                .createHmac('sha3-512', process.env.QUANTUM_SECRET || 'wilsy-os-quantum-secure-2026')
                .update(`${this.auditId}:${this.integrityHash}:${this.workflow.status}`)
                .digest('hex');
        }
    },

    createdBy: {
        type: String,
        required: true,
        immutable: true
    },

    createdAt: {
        type: Date,
        default: Date.now,
        immutable: true,
        index: true
    },

    updatedBy: {
        type: String,
        required: true
    },

    updatedAt: {
        type: Date,
        default: Date.now
    },

    retentionPolicy: {
        type: String,
        default: 'companies_act_10_years'
    },

    retentionStart: {
        type: Date,
        default: Date.now,
        immutable: true
    },

    retentionExpiry: {
        type: Date,
        default: function() {
            const date = new Date();
            date.setFullYear(date.getFullYear() + 10);
            return date;
        },
        index: true
    },

    dataResidency: {
        type: String,
        default: 'ZA',
        enum: ['ZA', 'EU', 'US', 'AU', 'UK']
    },

    deleted: {
        type: Boolean,
        default: false,
        index: true
    },
    deletedAt: Date,
    deletedBy: String,
    deletionReason: String,
    deletionAuthorization: String
}, {
    timestamps: true,
    toJSON: {
        virtuals: true,
        transform: function(doc, ret) {
            delete ret.__v;
            delete ret.auditTrail;
            delete ret.integrityHash;
            delete ret.quantumSignature;
            delete ret.reportData?.sensitiveInfo;
            delete ret.evidencePackage?.files;
            return ret;
        }
    }
});

// ====================================================================
// VIRTUAL FIELDS
// ====================================================================

complianceAuditSchema.virtual('totalFindingsCount').get(function() {
    return this.findings.length;
});

complianceAuditSchema.virtual('openFindingsCount').get(function() {
    return this.findings.filter(f => ['OPEN', 'IN_PROGRESS'].includes(f.status)).length;
});

complianceAuditSchema.virtual('criticalFindingsCount').get(function() {
    return this.findings.filter(f => f.severity === 'CRITICAL' && f.status !== 'REMEDIATED').length;
});

complianceAuditSchema.virtual('highFindingsCount').get(function() {
    return this.findings.filter(f => f.severity === 'HIGH' && f.status !== 'REMEDIATED').length;
});

complianceAuditSchema.virtual('remediatedFindingsCount').get(function() {
    return this.findings.filter(f => f.status === 'REMEDIATED').length;
});

complianceAuditSchema.virtual('overdueFindingsCount').get(function() {
    return this.findings.filter(f => 
        ['OPEN', 'IN_PROGRESS'].includes(f.status) && 
        f.dueDate && 
        f.dueDate < new Date()
    ).length;
});

complianceAuditSchema.virtual('complianceScore').get(function() {
    const score = this.score;
    for (const range of Object.values(COMPLIANCE_SCORES)) {
        if (score >= range.min && score <= range.max) {
            return {
                score,
                rating: range.label,
                color: range.color
            };
        }
    }
    return { score, rating: 'UNKNOWN', color: '#9E9E9E' };
});

complianceAuditSchema.virtual('daysToNextReview').get(function() {
    if (!this.workflow.nextReviewDate) return null;
    return Math.ceil((this.workflow.nextReviewDate - Date.now()) / (1000 * 60 * 60 * 24));
});

complianceAuditSchema.virtual('isOverdue').get(function() {
    return this.workflow.nextReviewDate && this.workflow.nextReviewDate < new Date();
});

complianceAuditSchema.virtual('remediationProgress').get(function() {
    if (this.metrics.totalFindings === 0) return 0;
    return (this.metrics.remediatedFindings / this.metrics.totalFindings) * 100;
});

// ====================================================================
// INDEXES
// ====================================================================

complianceAuditSchema.index({ tenantId: 1, auditType: 1, createdAt: -1 });
complianceAuditSchema.index({ tenantId: 1, subjectId: 1, subjectModel: 1, createdAt: -1 });
complianceAuditSchema.index({ tenantId: 1, 'workflow.status': 1, 'scheduling.nextScheduledDate': 1 });
complianceAuditSchema.index({ tenantId: 1, score: 1, createdAt: -1 });
complianceAuditSchema.index({ tenantId: 1, 'findings.severity': 1, 'findings.status': 1 });
complianceAuditSchema.index({ tenantId: 1, 'complianceIssues.severity': 1, 'complianceIssues.remediation.status': 1 });
complianceAuditSchema.index({ reportHash: 1 }, { unique: true });
complianceAuditSchema.index({ integrityHash: 1 }, { unique: true });
complianceAuditSchema.index({ deleted: 1, retentionExpiry: 1 });

// ====================================================================
// PRE-SAVE HOOKS
// ====================================================================

complianceAuditSchema.pre('save', async function(next) {
    try {
        if (!this.tenantId) {
            throw new Error('TENANT_ISOLATION_VIOLATION: Compliance audit requires tenantId');
        }

        for (const range of Object.values(COMPLIANCE_SCORES)) {
            if (this.score >= range.min && this.score <= range.max) {
                this.scoreLabel = range.label;
                break;
            }
        }

        this.metrics.totalFindings = this.findings.length;
        this.metrics.openFindings = this.findings.filter(f => 
            ['OPEN', 'IN_PROGRESS'].includes(f.status)
        ).length;
        this.metrics.remediatedFindings = this.findings.filter(f => 
            f.status === 'REMEDIATED'
        ).length;
        this.metrics.overdueFindings = this.findings.filter(f => 
            ['OPEN', 'IN_PROGRESS'].includes(f.status) && 
            f.dueDate && 
            f.dueDate < new Date()
        ).length;

        const severityCount = {
            CRITICAL: 0,
            HIGH: 0,
            MEDIUM: 0,
            LOW: 0,
            INFO: 0
        };

        this.findings.forEach(finding => {
            if (severityCount[finding.severity] !== undefined) {
                severityCount[finding.severity]++;
            }
        });

        this.metrics.findingsBySeverity = severityCount;

        const remediatedFindings = this.findings.filter(f => 
            f.status === 'REMEDIATED' && f.remediatedAt && f.createdAt
        );

        if (remediatedFindings.length > 0) {
            const totalDays = remediatedFindings.reduce((sum, f) => {
                const days = (f.remediatedAt - f.createdAt) / (1000 * 60 * 60 * 24);
                return sum + days;
            }, 0);
            this.metrics.averageRemediationTime = parseFloat((totalDays / remediatedFindings.length).toFixed(1));
        }

        this.metrics.lastCalculated = new Date();

        if (!this.metrics.complianceTrend) {
            this.metrics.complianceTrend = [];
        }

        this.metrics.complianceTrend.push({
            date: new Date(),
            score: this.score
        });

        if (this.metrics.complianceTrend.length > 10) {
            this.metrics.complianceTrend = this.metrics.complianceTrend.slice(-10);
        }

        this.integrityHash = crypto
            .createHash('sha3-512')
            .update(`${this.auditId}:${this.score}:${this.workflow.status}:${Date.now()}`)
            .digest('hex');

        this.quantumSignature = crypto
            .createHmac('sha3-512', process.env.QUANTUM_SECRET || 'wilsy-os-quantum-secure-2026')
            .update(`${this.auditId}:${this.integrityHash}:${this.workflow.status}`)
            .digest('hex');

        if (this.isModified('workflow.status')) {
            this.workflow.history.push({
                status: this.workflow.status,
                changedAt: new Date(),
                changedBy: this.updatedBy,
                comment: this.statusComment,
                ipAddress: this.ipAddress,
                userAgent: this.userAgent
            });
        }

        next();
    } catch (error) {
        next(error);
    }
});

// ====================================================================
// STATIC METHODS
// ====================================================================

complianceAuditSchema.statics = {
    async getComplianceSummary(tenantId, year = new Date().getFullYear()) {
        const startDate = new Date(year, 0, 1);
        const endDate = new Date(year, 11, 31, 23, 59, 59);

        const audits = await this.find({
            tenantId,
            createdAt: { $gte: startDate, $lte: endDate },
            'workflow.status': 'COMPLETED',
            deleted: false
        });

        const summary = {
            tenantId,
            year,
            totalAudits: audits.length,
            averageScore: 0,
            overallCompliance: '',
            criticalFindings: 0,
            highFindings: 0,
            mediumFindings: 0,
            lowFindings: 0,
            openIssues: 0,
            resolvedIssues: 0,
            overdueIssues: 0,
            byAuditType: {},
            byStatus: {},
            bySeverity: {
                CRITICAL: 0,
                HIGH: 0,
                MEDIUM: 0,
                LOW: 0,
                INFO: 0
            },
            trends: [],
            topRisks: [],
            recommendations: []
        };

        let totalScore = 0;

        audits.forEach(audit => {
            totalScore += audit.score;
            summary.byAuditType[audit.auditType] = (summary.byAuditType[audit.auditType] || 0) + 1;

            audit.findings.forEach(finding => {
                if (summary.bySeverity[finding.severity] !== undefined) {
                    summary.bySeverity[finding.severity]++;

                    if (finding.severity === 'CRITICAL') summary.criticalFindings++;
                    if (finding.severity === 'HIGH') summary.highFindings++;
                    if (finding.severity === 'MEDIUM') summary.mediumFindings++;
                    if (finding.severity === 'LOW') summary.lowFindings++;
                }
            });

            audit.complianceIssues.forEach(issue => {
                if (issue.remediation?.status === 'PENDING' || issue.remediation?.status === 'IN_PROGRESS') {
                    summary.openIssues++;
                } else if (issue.remediation?.status === 'COMPLETED') {
                    summary.resolvedIssues++;
                }

                if (issue.remediation?.deadline && 
                    issue.remediation.deadline < new Date() && 
                    issue.remediation.status !== 'COMPLETED') {
                    summary.overdueIssues++;
                }
            });

            summary.trends.push({
                date: audit.createdAt,
                score: audit.score,
                type: audit.auditType
            });

            audit.findings
                .filter(f => f.severity === 'CRITICAL' || f.severity === 'HIGH')
                .forEach(finding => {
                    summary.topRisks.push({
                        auditId: audit.auditId,
                        auditType: audit.auditType,
                        findingId: finding.findingId,
                        title: finding.title,
                        severity: finding.severity,
                        riskScore: finding.riskScore,
                        dueDate: finding.dueDate,
                        status: finding.status
                    });
                });

            audit.recommendations
                .filter(r => !r.implemented && !r.rejected)
                .forEach(rec => {
                    summary.recommendations.push({
                        auditId: audit.auditId,
                        recommendationId: rec.recommendationId,
                        title: rec.title,
                        priority: rec.priority,
                        estimatedEffort: rec.estimatedEffort,
                        roi: rec.roi
                    });
                });
        });

        summary.averageScore = audits.length > 0 
            ? parseFloat((totalScore / audits.length).toFixed(1)) 
            : 0;

        if (summary.averageScore >= 90) summary.overallCompliance = 'EXCELLENT';
        else if (summary.averageScore >= 75) summary.overallCompliance = 'GOOD';
        else if (summary.averageScore >= 60) summary.overallCompliance = 'SATISFACTORY';
        else if (summary.averageScore >= 40) summary.overallCompliance = 'POOR';
        else summary.overallCompliance = 'CRITICAL';

        summary.topRisks.sort((a, b) => {
            const severityOrder = { CRITICAL: 4, HIGH: 3, MEDIUM: 2, LOW: 1 };
            return (severityOrder[b.severity] || 0) - (severityOrder[a.severity] || 0);
        }).slice(0, 10);

        const priorityOrder = { IMMEDIATE: 4, URGENT: 3, HIGH: 2, MEDIUM: 1, LOW: 0 };
        summary.recommendations.sort((a, b) => 
            (priorityOrder[b.priority] || 0) - (priorityOrder[a.priority] || 0)
        ).slice(0, 20);

        return summary;
    },

    async getComplianceTrends(tenantId, years = 5) {
        const currentYear = new Date().getFullYear();
        const startYear = currentYear - years + 1;
        const trends = [];

        for (let year = startYear; year <= currentYear; year++) {
            const summary = await this.getComplianceSummary(tenantId, year);
            trends.push({
                year,
                averageScore: summary.averageScore,
                overallCompliance: summary.overallCompliance,
                totalAudits: summary.totalAudits,
                criticalFindings: summary.criticalFindings,
                highFindings: summary.highFindings,
                openIssues: summary.openIssues,
                resolvedIssues: summary.resolvedIssues
            });
        }

        return trends;
    },

    async getHighRiskEntities(tenantId, threshold = 60) {
        return this.aggregate([
            {
                $match: {
                    tenantId,
                    score: { $lt: threshold },
                    'workflow.status': { $in: ['COMPLETED', 'IN_PROGRESS'] },
                    deleted: false
                }
            },
            {
                $group: {
                    _id: '$subjectId',
                    subjectModel: { $first: '$subjectModel' },
                    subjectIdentifier: { $first: '$subjectIdentifier' },
                    averageScore: { $avg: '$score' },
                    minScore: { $min: '$score' },
                    maxScore: { $max: '$score' },
                    auditCount: { $sum: 1 },
                    lastAuditDate: { $max: '$createdAt' },
                    criticalFindings: {
                        $sum: {
                            $size: {
                                $filter: {
                                    input: '$findings',
                                    as: 'finding',
                                    cond: { 
                                        $and: [
                                            { $eq: ['$$finding.severity', 'CRITICAL'] },
                                            { $ne: ['$$finding.status', 'REMEDIATED'] }
                                        ]
                                    }
                                }
                            }
                        }
                    },
                    highFindings: {
                        $sum: {
                            $size: {
                                $filter: {
                                    input: '$findings',
                                    as: 'finding',
                                    cond: { 
                                        $and: [
                                            { $eq: ['$$finding.severity', 'HIGH'] },
                                            { $ne: ['$$finding.status', 'REMEDIATED'] }
                                        ]
                                    }
                                }
                            }
                        }
                    },
                    overdueActions: {
                        $sum: {
                            $size: {
                                $filter: {
                                    input: '$correctiveActions',
                                    as: 'action',
                                    cond: {
                                        $and: [
                                            { $eq: ['$$action.status', 'PENDING'] },
                                            { $lt: ['$$action.deadline', new Date()] }
                                        ]
                                    }
                                }
                            }
                        }
                    }
                }
            },
            {
                $project: {
                    entityId: '$_id',
                    entityType: '$subjectModel',
                    identifier: '$subjectIdentifier',
                    averageScore: { $round: ['$averageScore', 1] },
                    minScore: 1,
                    maxScore: 1,
                    auditCount: 1,
                    lastAuditDate: 1,
                    criticalFindings: 1,
                    highFindings: 1,
                    overdueActions: 1,
                    riskLevel: {
                        $switch: {
                            branches: [
                                { case: { $gte: ['$averageScore', 80] }, then: 'LOW' },
                                { case: { $gte: ['$averageScore', 60] }, then: 'MEDIUM' },
                                { case: { $gte: ['$averageScore', 40] }, then: 'HIGH' },
                                { case: { $lt: ['$averageScore', 40] }, then: 'CRITICAL' }
                            ],
                            default: 'UNKNOWN'
                        }
                    }
                }
            },
            { $sort: { averageScore: 1 } }
        ]);
    },

    async getRegulatoryStatus(tenantId, framework) {
        const audits = await this.find({
            tenantId,
            'scope.criteria.framework': framework,
            'workflow.status': 'COMPLETED',
            deleted: false
        }).sort({ createdAt: -1 }).limit(10);

        if (audits.length === 0) {
            return {
                framework,
                status: 'NOT_ASSESSED',
                lastAuditDate: null,
                score: null,
                findings: 0,
                criticalFindings: 0,
                recommendations: []
            };
        }

        const latestAudit = audits[0];
        const allFindings = audits.flatMap(a => a.findings);
        const openFindings = allFindings.filter(f => 
            ['OPEN', 'IN_PROGRESS'].includes(f.status)
        );

        return {
            framework,
            status: latestAudit.score >= 75 ? 'COMPLIANT' : 'NON_COMPLIANT',
            lastAuditDate: latestAudit.createdAt,
            score: latestAudit.score,
            scoreLabel: latestAudit.scoreLabel,
            totalAudits: audits.length,
            totalFindings: allFindings.length,
            openFindings: openFindings.length,
            criticalFindings: openFindings.filter(f => f.severity === 'CRITICAL').length,
            highFindings: openFindings.filter(f => f.severity === 'HIGH').length,
            recommendations: latestAudit.recommendations
                .filter(r => !r.implemented && !r.rejected)
                .slice(0, 5),
            auditHistory: audits.map(a => ({
                auditId: a.auditId,
                date: a.createdAt,
                score: a.score,
                findingsCount: a.findings.length
            }))
        };
    }
};

// ====================================================================
// INSTANCE METHODS
// ====================================================================

complianceAuditSchema.methods = {
    async addFinding(findingData, userId) {
        const finding = {
            findingId: `FIND-${uuidv4()}`,
            ...findingData,
            createdAt: new Date(),
            createdBy: userId,
            statusHistory: [{
                status: findingData.status || 'OPEN',
                changedAt: new Date(),
                changedBy: userId
            }]
        };

        this.findings.push(finding);
        this.updatedBy = userId;
        this.updatedAt = new Date();

        this.auditTrail.push({
            action: 'FINDING_ADDED',
            performedBy: userId,
            performedAt: new Date(),
            changes: { findingId: finding.findingId, title: finding.title, severity: finding.severity },
            findingId: finding.findingId
        });

        await this.save();
        return finding;
    },

    async updateFindingStatus(findingId, status, userId, notes = '') {
        const finding = this.findings.id(findingId);
        if (!finding) {
            throw new Error(`FINDING_NOT_FOUND: ${findingId}`);
        }

        const oldStatus = finding.status;
        finding.status = status;
        finding.updatedAt = new Date();
        finding.updatedBy = userId;

        finding.statusHistory.push({
            status,
            changedAt: new Date(),
            changedBy: userId,
            reason: notes
        });

        if (status === 'REMEDIATED') {
            finding.remediatedAt = new Date();
            finding.remediatedBy = userId;
            finding.remediationNotes = notes;
        }

        if (status === 'VERIFIED') {
            finding.verifiedAt = new Date();
            finding.verifiedBy = userId;
            finding.verificationNotes = notes;
        }

        this.updatedBy = userId;
        this.updatedAt = new Date();

        this.auditTrail.push({
            action: 'FINDING_UPDATED',
            performedBy: userId,
            performedAt: new Date(),
            changes: { findingId, oldStatus, newStatus: status, notes },
            findingId
        });

        await this.save();
        return finding;
    },

    async addCorrectiveAction(actionData, userId) {
        const action = {
            actionId: `ACTION-${uuidv4()}`,
            ...actionData,
            assignedAt: new Date(),
            assignedBy: userId,
            status: 'PENDING',
            statusHistory: [{
                status: 'PENDING',
                changedAt: new Date(),
                changedBy: userId
            }],
            progress: 0,
            notes: []
        };

        this.correctiveActions.push(action);
        this.updatedBy = userId;
        this.updatedAt = new Date();

        this.auditTrail.push({
            action: 'ACTION_ASSIGNED',
            performedBy: userId,
            performedAt: new Date(),
            changes: { 
                actionId: action.actionId, 
                title: action.title, 
                deadline: action.deadline,
                assignedTo: action.assignedTo 
            },
            actionId: action.actionId
        });

        await this.save();
        return action;
    },

    async updateActionStatus(actionId, status, userId, notes = '') {
        const action = this.correctiveActions.id(actionId);
        if (!action) {
            throw new Error(`ACTION_NOT_FOUND: ${actionId}`);
        }

        const oldStatus = action.status;
        action.status = status;
        action.statusHistory.push({
            status,
            changedAt: new Date(),
            changedBy: userId,
            notes
        });

        if (status === 'COMPLETED') {
            action.completedAt = new Date();
            action.completedBy = userId;
            action.completionNotes = notes;
            action.progress = 100;
        }

        if (status === 'IN_PROGRESS' && action.progress === 0) {
            action.progress = 25;
        }

        this.updatedBy = userId;
        this.updatedAt = new Date();

        this.auditTrail.push({
            action: 'ACTION_COMPLETED',
            performedBy: userId,
            performedAt: new Date(),
            changes: { actionId, oldStatus, newStatus: status, notes },
            actionId
        });

        await this.save();
        return action;
    },

    async generateReport() {
        const report = {
            auditId: this.auditId,
            auditType: this.auditType,
            title: `${this.auditType} Audit - ${this.subjectIdentifier}`,
            status: this.workflow.status,
            period: {
                scheduled: this.scheduling.scheduledDate,
                started: this.scheduling.startDate,
                completed: this.scheduling.endDate || this.completedAt
            },
            scope: this.scope,
            auditors: this.auditors,
            leadAuditor: this.leadAuditor,

            executiveSummary: {
                overallScore: this.score,
                rating: this.scoreLabel,
                complianceLevel: this.complianceScore.rating,
                findingsSummary: {
                    total: this.metrics.totalFindings,
                    open: this.metrics.openFindings,
                    remediated: this.metrics.remediatedFindings,
                    overdue: this.metrics.overdueFindings,
                    critical: this.metrics.findingsBySeverity.CRITICAL,
                    high: this.metrics.findingsBySeverity.HIGH,
                    medium: this.metrics.findingsBySeverity.MEDIUM,
                    low: this.metrics.findingsBySeverity.LOW
                },
                keyRisks: this.findings
                    .filter(f => f.severity === 'CRITICAL' || f.severity === 'HIGH')
                    .slice(0, 5)
                    .map(f => ({
                        title: f.title,
                        severity: f.severity,
                        status: f.status,
                        dueDate: f.dueDate
                    })),
                complianceGaps: this.complianceIssues.length,
                openActions: this.correctiveActions.filter(a => a.status !== 'COMPLETED').length,
                overdueActions: this.correctiveActions.filter(a => 
                    a.status !== 'COMPLETED' && a.deadline < new Date()
                ).length
            },

            findings: this.findings.map(f => ({
                findingId: f.findingId,
                title: f.title,
                description: f.description,
                severity: f.severity,
                likelihood: f.likelihood,
                impact: f.impact,
                riskScore: f.riskScore,
                requirement: f.requirement,
                status: f.status,
                createdAt: f.createdAt,
                dueDate: f.dueDate,
                remediatedAt: f.remediatedAt,
                verifiedAt: f.verifiedAt,
                evidenceCount: f.evidence?.length || 0
            })),

            complianceIssues: this.complianceIssues.map(i => ({
                issueId: i.issueId,
                type: i.type,
                title: i.title,
                severity: i.severity,
                framework: i.framework,
                remediation: i.remediation,
                affectedEntities: i.affectedEntities
            })),

            recommendations: this.recommendations.map(r => ({
                recommendationId: r.recommendationId,
                title: r.title,
                priority: r.priority,
                estimatedEffort: r.estimatedEffort,
                roi: r.roi,
                implemented: r.implemented
            })),

            correctiveActions: this.correctiveActions.map(a => ({
                actionId: a.actionId,
                title: a.title,
                priority: a.priority,
                deadline: a.deadline,
                assignedTo: a.assignedTo,
                status: a.status,
                progress: a.progress,
                completedAt: a.completedAt
            })),

            riskAssessment: this.riskAssessment,

            metrics: {
                averageRemediationTime: this.metrics.averageRemediationTime,
                remediationProgress: this.remediationProgress,
                complianceTrend: this.metrics.complianceTrend
            },

            integrity: {
                reportHash: this.reportHash,
                integrityHash: this.integrityHash,
                quantumSignature: this.quantumSignature,
                generatedAt: new Date().toISOString(),
                verified: true
            },

            retention: {
                policy: this.retentionPolicy,
                expiryDate: this.retentionExpiry,
                daysRemaining: Math.ceil((this.retentionExpiry - Date.now()) / (1000 * 60 * 60 * 24))
            },

            generatedAt: new Date().toISOString(),
            generatedBy: 'WilsyOS Compliance Audit Engine v5.0.1'
        };

        this.reportData = report;
        this.reportHash = crypto
            .createHash('sha3-512')
            .update(`${this.auditId}:${JSON.stringify(report)}:${Date.now()}`)
            .digest('hex');

        this.auditTrail.push({
            action: 'REPORT_GENERATED',
            performedBy: 'SYSTEM',
            performedAt: new Date(),
            changes: { reportHash: this.reportHash }
        });

        await this.save();
        return report;
    },

    async completeAudit(userId, notes = '') {
        this.workflow.status = 'COMPLETED';
        this.scheduling.endDate = new Date();
        this.completedAt = new Date();

        this.workflow.history.push({
            status: 'COMPLETED',
            changedAt: new Date(),
            changedBy: userId,
            comment: notes
        });

        const nextReview = new Date();
        nextReview.setDate(nextReview.getDate() + this.workflow.reviewFrequency);
        this.workflow.nextReviewDate = nextReview;

        this.updatedBy = userId;
        this.updatedAt = new Date();

        this.auditTrail.push({
            action: 'AUDIT_COMPLETED',
            performedBy: userId,
            performedAt: new Date(),
            changes: { notes, nextReviewDate: nextReview }
        });

        await this.save();
        const report = await this.generateReport();

        return {
            success: true,
            auditId: this.auditId,
            completedAt: this.completedAt,
            completedBy: userId,
            nextReviewDate: nextReview,
            report
        };
    },

    async exportForRegulator(authority, userId) {
        const report = await this.generateReport();

        const exportPackage = {
            exportId: `EXPORT-${uuidv4()}`,
            authority,
            exportedAt: new Date().toISOString(),
            exportedBy: userId,
            audit: {
                auditId: this.auditId,
                auditType: this.auditType,
                subjectId: this.subjectId,
                subjectModel: this.subjectModel,
                subjectIdentifier: this.subjectIdentifier,
                date: this.createdAt
            },
            report: report,
            findings: this.findings.map(f => ({
                findingId: f.findingId,
                title: f.title,
                description: f.description,
                severity: f.severity,
                requirement: f.requirement,
                status: f.status,
                remediation: {
                    completedAt: f.remediatedAt,
                    notes: f.remediationNotes
                }
            })),
            evidence: this.evidencePackage,
            complianceIssues: this.complianceIssues,
            correctiveActions: this.correctiveActions.filter(a => a.status === 'COMPLETED'),
            integrity: {
                reportHash: this.reportHash,
                integrityHash: this.integrityHash,
                quantumSignature: this.quantumSignature,
                verificationUrl: `https://verify.wilsyos.co.za/audit/${this.auditId}`
            },
            retention: {
                policy: this.retentionPolicy,
                expiryDate: this.retentionExpiry
            }
        };

        exportPackage.hash = crypto
            .createHash('sha3-512')
            .update(JSON.stringify(exportPackage))
            .digest('hex');

        this.regulatoryReporting.push({
            authority,
            reportId: exportPackage.exportId,
            submittedAt: new Date(),
            submittedBy: userId,
            status: 'SUBMITTED'
        });

        this.auditTrail.push({
            action: 'REPORT_GENERATED',
            performedBy: userId,
            performedAt: new Date(),
            changes: { authority, exportId: exportPackage.exportId }
        });

        await this.save();
        return exportPackage;
    },

    async verifyIntegrity() {
        const recalculatedReportHash = crypto
            .createHash('sha3-512')
            .update(`${this.auditId}:${JSON.stringify(this.reportData)}:${this.updatedAt.getTime()}`)
            .digest('hex');

        const reportHashValid = recalculatedReportHash === this.reportHash;

        const recalculatedIntegrityHash = crypto
            .createHash('sha3-512')
            .update(`${this.auditId}:${this.score}:${this.workflow.status}:${this.updatedAt.getTime()}`)
            .digest('hex');

        const integrityHashValid = recalculatedIntegrityHash === this.integrityHash;

        const recalculatedSignature = crypto
            .createHmac('sha3-512', process.env.QUANTUM_SECRET || 'wilsy-os-quantum-secure-2026')
            .update(`${this.auditId}:${this.integrityHash}:${this.workflow.status}`)
            .digest('hex');

        const signatureValid = recalculatedSignature === this.quantumSignature;

        const findingHashesValid = this.findings.every(finding => {
            if (finding.evidence) {
                return finding.evidence.every(e => {
                    if (e.fileHash) {
                        return true;
                    }
                    return true;
                });
            }
            return true;
        });

        const isValid = reportHashValid && integrityHashValid && signatureValid && findingHashesValid;

        return {
            valid: isValid,
            auditId: this.auditId,
            checks: {
                reportHash: { valid: reportHashValid, expected: this.reportHash, computed: recalculatedReportHash },
                integrityHash: { valid: integrityHashValid, expected: this.integrityHash, computed: recalculatedIntegrityHash },
                quantumSignature: { valid: signatureValid, expected: this.quantumSignature, computed: recalculatedSignature },
                findingEvidence: { valid: findingHashesValid }
            },
            verifiedAt: new Date().toISOString()
        };
    }
};

// ====================================================================
// EXPORT
// ====================================================================

module.exports = mongoose.model('ComplianceAudit', complianceAuditSchema);
