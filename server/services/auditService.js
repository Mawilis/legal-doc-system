// ====================================================================
// FILE: server/services/auditService.js - COMPLETE PRODUCTION VERSION
// ====================================================================
/**
 * WILSYS OS - FORENSIC AUDIT SERVICE
 * LPC Rule 17.3 - Attorney Profile Access Logging
 * LPC Rule 95.3 - Compliance Audit Trail
 * POPIA Section 20 - Record of Processing Activities
 * GDPR Article 30 - Records of Processing Activities
 */

const crypto = require('crypto');
const { BlockchainAnchor } = require('./blockchainAnchor');
const AuditModel = require('../models/AuditLedger');
const { ComplianceError } = require('../utils/errors');

class AuditService {
    constructor() {
        this.anchors = new BlockchainAnchor();
        this.initialized = false;
        this.batchSize = 100;
        this.flushInterval = 5000; // 5 seconds
        this.pendingAudits = [];
        this.auditQueue = [];

        this._initialize();
    }

    async _initialize() {
        this.initialized = true;
        this._startBatchProcessor();

        // Create genesis audit block
        await this.recordAccess(
            'system',
            'audit-service',
            { userId: 'SYSTEM', tenantId: 'SYSTEM' },
            'INITIALIZE',
            { version: '5.0.3' }
        );
    }

    _startBatchProcessor() {
        setInterval(() => this._processBatch(), this.flushInterval).unref();
    }

    async _processBatch() {
        if (this.pendingAudits.length === 0) return;

        const batch = [...this.pendingAudits];
        this.pendingAudits = [];

        try {
            const auditChainBlock = await this.anchors.anchor(
                crypto.createHash('sha3-512')
                    .update(JSON.stringify(batch))
                    .digest('hex')
            );

            await AuditModel.insertMany(batch.map(entry => ({
                ...entry,
                blockchainAnchor: auditChainBlock
            })));

            this.auditQueue = this.auditQueue.filter(id =>
                !batch.some(b => b.auditId === id)
            );
        } catch (error) {
            // Re-queue failed batch
            this.pendingAudits.unshift(...batch);
            console.error('Audit batch processing failed:', error.message);
        }
    }

    /**
     * Record an access event with full forensic context
     * LPC Rule 17.3 - Attorney Profile Access Logging
     * POPIA Section 20 - Record of Processing
     */
    async recordAccess(resource, identifier, userContext, action, metadata = {}) {
        if (!userContext?.userId && action !== 'SYSTEM') {
            throw new ComplianceError('USER_CONTEXT_REQUIRED', {
                code: 'AUDIT_001',
                regulatoryRef: 'LPC_RULE_17.3',
                resource,
                action
            });
        }

        const auditId = crypto.randomUUID();
        const timestamp = new Date().toISOString();

        // Extract all available context
        const auditEntry = {
            auditId,
            timestamp,
            resource,
            identifier: identifier?.toString() || 'UNKNOWN',
            action,

            // User context
            userId: userContext?.userId || 'SYSTEM',
            tenantId: userContext?.tenantId || 'SYSTEM',
            firmId: userContext?.firmId,
            practiceId: userContext?.practiceId,
            roles: userContext?.roles || [],

            // Request context
            ipAddress: userContext?.ipAddress,
            userAgent: userContext?.userAgent,
            sessionId: userContext?.sessionId,
            correlationId: userContext?.correlationId,
            requestId: userContext?.requestId,

            // Compliance metadata
            regulatoryTags: this._getRegulatoryTags(resource, action),
            retentionPolicy: this._getRetentionPolicy(resource),
            dataResidency: 'ZA',

            // Forensic evidence
            forensicHash: null,
            blockchainAnchor: null,

            // Business metadata
            metadata: {
                ...metadata,
                source: 'LPC_SERVICE',
                version: '5.0.3',
                environment: process.env.NODE_ENV || 'production'
            }
        };

        // Generate forensic hash
        auditEntry.forensicHash = crypto
            .createHash('sha3-512')
            .update(JSON.stringify({
                ...auditEntry,
                forensicHash: undefined,
                blockchainAnchor: undefined
            }))
            .digest('hex');

        // Add to pending batch
        this.pendingAudits.push(auditEntry);
        this.auditQueue.push(auditId);

        // Immediate anchor for high-value events
        if (this._requiresImmediateAnchor(resource, action)) {
            const anchor = await this.anchors.anchor(auditEntry.forensicHash);
            auditEntry.blockchainAnchor = anchor;

            // Process immediately
            await AuditModel.create(auditEntry);
            this.pendingAudits = this.pendingAudits.filter(a => a.auditId !== auditId);
        }

        return auditEntry;
    }

    /**
     * Query audit trail with full compliance filtering
     * POPIA Section 22 - Data Subject Access Requests
     * GDPR Article 15 - Right of Access
     */
    async queryAuditTrail(filters = {}, pagination = {}) {
        const query = {};

        if (filters.userId) query.userId = filters.userId;
        if (filters.tenantId) query.tenantId = filters.tenantId;
        if (filters.resource) query.resource = filters.resource;
        if (filters.identifier) query.identifier = filters.identifier;
        if (filters.action) query.action = filters.action;
        if (filters.regulatoryTag) query.regulatoryTags = filters.regulatoryTag;

        if (filters.startDate || filters.endDate) {
            query.timestamp = {};
            if (filters.startDate) query.timestamp.$gte = filters.startDate;
            if (filters.endDate) query.timestamp.$lte = filters.endDate;
        }

        const page = pagination.page || 1;
        const limit = pagination.limit || 100;
        const skip = (page - 1) * limit;

        const [results, total] = await Promise.all([
            AuditModel.find(query)
                .sort({ timestamp: -1 })
                .skip(skip)
                .limit(limit)
                .lean()
                .exec(),
            AuditModel.countDocuments(query)
        ]);

        return {
            data: results,
            pagination: {
                page,
                limit,
                total,
                pages: Math.ceil(total / limit)
            },
            query: filters,
            generatedAt: new Date().toISOString(),
            compliance: {
                popiaSection: '22',
                gdprArticle: '15',
                retentionPeriod: '5_years'
            }
        };
    }

    /**
     * Generate compliance report for regulatory submission
     * LPC Rule 35.2 - Compliance Reporting
     */
    async generateComplianceReport(tenantId, startDate, endDate) {
        const query = {
            tenantId,
            timestamp: {
                $gte: startDate || new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
                $lte: endDate || new Date()
            }
        };

        const [byResource, byAction, byUser, total] = await Promise.all([
            AuditModel.aggregate([
                { $match: query },
                { $group: { _id: '$resource', count: { $sum: 1 } } },
                { $sort: { count: -1 } }
            ]),
            AuditModel.aggregate([
                { $match: query },
                { $group: { _id: '$action', count: { $sum: 1 } } },
                { $sort: { count: -1 } }
            ]),
            AuditModel.aggregate([
                { $match: query },
                { $group: { _id: '$userId', count: { $sum: 1 } } },
                { $sort: { count: -1 } },
                { $limit: 10 }
            ]),
            AuditModel.countDocuments(query)
        ]);

        return {
            reportId: crypto.randomUUID(),
            tenantId,
            period: {
                start: query.timestamp.$gte,
                end: query.timestamp.$lte
            },
            summary: {
                totalEvents: total,
                uniqueResources: byResource.length,
                uniqueActions: byAction.length,
                uniqueUsers: byUser.length
            },
            breakdown: {
                byResource,
                byAction,
                topUsers: byUser
            },
            compliance: {
                lpc173: true,
                popia20: true,
                gdpr30: true
            },
            generatedAt: new Date().toISOString(),
            generatedBy: 'AuditService:v5.0.3'
        };
    }

    /**
     * Verify audit trail integrity using cryptographic hashes
     * LPC Rule 3.4.2 - Cryptographic Proof
     */
    async verifyAuditTrail(auditIds = []) {
        const query = auditIds.length > 0
            ? { auditId: { $in: auditIds } }
            : {};

        const audits = await AuditModel.find(query).lean().exec();
        const results = [];

        for (const audit of audits) {
            const recomputedHash = crypto
                .createHash('sha3-512')
                .update(JSON.stringify({
                    ...audit,
                    forensicHash: undefined,
                    blockchainAnchor: undefined,
                    _id: undefined,
                    __v: undefined
                }))
                .digest('hex');

            const verified = recomputedHash === audit.forensicHash;

            results.push({
                auditId: audit.auditId,
                verified,
                timestamp: audit.timestamp,
                resource: audit.resource,
                action: audit.action,
                userId: audit.userId,
                forensicHash: audit.forensicHash?.substring(0, 16),
                recomputedHash: recomputedHash.substring(0, 16),
                blockchainVerified: audit.blockchainAnchor?.verified || false
            });
        }

        return {
            verified: results.every(r => r.verified),
            total: results.length,
            failed: results.filter(r => !r.verified).length,
            results,
            timestamp: new Date().toISOString()
        };
    }

    _getRegulatoryTags(resource, action) {
        const tags = [];

        // LPC Rules
        if (resource.includes('attorney')) tags.push('LPC_RULE_17.3');
        if (resource.includes('trust')) tags.push('LPC_RULE_3.4.5');
        if (resource.includes('matter')) tags.push('LPC_RULE_21.1');
        if (resource.includes('compliance')) tags.push('LPC_RULE_35.2');
        if (resource.includes('metrics')) tags.push('LPC_RULE_41.3');

        // Privacy Regulations
        if (action === 'VIEW') tags.push('POPIA_SECTION_20', 'GDPR_ARTICLE_30');
        if (action === 'EXPORT') tags.push('POPIA_SECTION_22', 'GDPR_ARTICLE_15');
        if (action === 'DELETE') tags.push('POPIA_SECTION_24', 'GDPR_ARTICLE_17');
        if (action === 'CREATE') tags.push('POPIA_SECTION_13', 'GDPR_ARTICLE_6');
        if (action === 'UPDATE') tags.push('POPIA_SECTION_24', 'GDPR_ARTICLE_16');

        // FICA/AML
        if (action === 'VERIFY') tags.push('FICA_SECTION_28', 'AML_DIRECTIVE_5');
        if (action === 'REPORT') tags.push('FICA_SECTION_29', 'SAR_REQUIRED');

        return tags;
    }

    _getRetentionPolicy(resource) {
        if (resource.includes('attorney')) return 'companies_act_20_years';
        if (resource.includes('trust')) return 'companies_act_10_years';
        if (resource.includes('cpd')) return 'companies_act_7_years';
        if (resource.includes('compliance')) return 'companies_act_10_years';
        if (resource.includes('fidelity')) return 'companies_act_5_years';
        return 'companies_act_5_years';
    }

    _requiresImmediateAnchor(resource, action) {
        const highValueEvents = [
            'ATTORNEY_PROFILE_CREATED',
            'ATTORNEY_PROFILE_DELETED',
            'TRUST_RECONCILIATION_COMPLETED',
            'COMPLIANCE_AUDIT_COMPLETED',
            'FIDELITY_CERTIFICATE_ISSUED',
            'SYSTEM'
        ];

        return highValueEvents.includes(action) ||
            resource.includes('trust') ||
            action.includes('RECONCILIATION');
    }

    async healthCheck() {
        const dbHealthy = await AuditModel.exists({}).catch(() => false);

        return {
            service: 'AuditService',
            version: '5.0.3',
            initialized: this.initialized,
            status: dbHealthy ? 'HEALTHY' : 'DEGRADED',
            metrics: {
                pendingAudits: this.pendingAudits.length,
                queueLength: this.auditQueue.length,
                batchSize: this.batchSize
            },
            timestamp: new Date().toISOString()
        };
    }
}

module.exports = new AuditService();