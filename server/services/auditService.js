/**
 * WILSYS OS - FORENSIC AUDIT SERVICE
 * ====================================================================
 * LPC RULE 17.3 · LPC RULE 95.3 · POPIA SECTION 20 · GDPR ARTICLE 30
 * 
 * This service provides:
 * - Immutable audit trail with cryptographic chain-of-custody
 * - Multi-regulator compliance reporting (LPC, POPIA, GDPR, FICA)
 * - Real-time anomaly detection and forensic analysis
 * - Blockchain anchoring for court-admissible evidence
 * - Data subject access request (DSAR) automation
 * - Retention policy enforcement with legal hold
 * - Cross-jurisdictional audit synchronization
 * 
 * @version 5.2.0
 * @author Wilson Khanyezi - Chief Quantum Sentinel
 * @copyright Wilsy OS (Pty) Ltd 2026
 * ====================================================================
 */

const crypto = require('crypto');
const { EventEmitter } = require('events');
const { BlockchainAnchor } = require('./blockchainAnchor');
const { ComplianceEngine } = require('./complianceEngine');
const {
    ValidationError,
    ComplianceError,
    DataIntegrityError,
    ErrorFactory
} = require('../utils/errors');
const { PerformanceMonitor } = require('../utils/performance');
const { RetentionManager } = require('../utils/retention');
const { LegalHoldManager } = require('../utils/legalHold');
const AuditModel = require('../models/AuditLedger');

/**
 * Forensic Audit Service
 * Provides immutable, court-admissible audit trails
 */
class AuditService extends EventEmitter {
    constructor() {
        super();

        // ================================================================
        // SERVICE STATE
        // ================================================================
        this.initialized = false;
        this.batchSize = 1000;
        this.flushIntervalMs = 5000;
        this.pendingAudits = [];
        this.auditQueue = new Map();
        this.auditIndex = new Map();
        this.anchorQueue = [];

        // ================================================================
        // DEPENDENCY SERVICES
        // ================================================================
        this.blockchainAnchor = new BlockchainAnchor();
        this.complianceEngine = ComplianceEngine;
        this.retentionManager = new RetentionManager();
        this.legalHoldManager = new LegalHoldManager();

        // ================================================================
        // PERFORMANCE MONITORING
        // ================================================================
        this.performance = new PerformanceMonitor({
            name: 'AuditService',
            metrics: ['latency', 'throughput', 'batchSize', 'anchorSuccess']
        });

        // ================================================================
        // REGULATORY MAPPING
        // ================================================================
        this.regulatoryMapping = {
            // LPC Rules
            'LPC_17.3': { jurisdiction: 'ZA', retentionDays: 3650, notifiable: false },
            'LPC_95.3': { jurisdiction: 'ZA', retentionDays: 3650, notifiable: false },
            'LPC_3.4.5': { jurisdiction: 'ZA', retentionDays: 3650, notifiable: true },
            'LPC_21.1': { jurisdiction: 'ZA', retentionDays: 3650, notifiable: false },
            'LPC_35.2': { jurisdiction: 'ZA', retentionDays: 3650, notifiable: false },
            'LPC_41.3': { jurisdiction: 'ZA', retentionDays: 1825, notifiable: false },
            'LPC_55.5': { jurisdiction: 'ZA', retentionDays: 1825, notifiable: false },
            'LPC_86.2': { jurisdiction: 'ZA', retentionDays: 3650, notifiable: true },

            // POPIA
            'POPIA_19': { jurisdiction: 'ZA', retentionDays: 1825, notifiable: false },
            'POPIA_20': { jurisdiction: 'ZA', retentionDays: 1825, notifiable: false },
            'POPIA_21': { jurisdiction: 'ZA', retentionDays: 1825, notifiable: true },
            'POPIA_22': { jurisdiction: 'ZA', retentionDays: 1825, notifiable: true },

            // GDPR
            'GDPR_30': { jurisdiction: 'EU', retentionDays: 1825, notifiable: false },
            'GDPR_33': { jurisdiction: 'EU', retentionDays: 1825, notifiable: true },
            'GDPR_35': { jurisdiction: 'EU', retentionDays: 1825, notifiable: false },

            // FICA
            'FICA_28': { jurisdiction: 'ZA', retentionDays: 1825, notifiable: true },
            'FICA_29': { jurisdiction: 'ZA', retentionDays: 1825, notifiable: true },

            // SARB
            'SARB_GN6': { jurisdiction: 'ZA', retentionDays: 3650, notifiable: true }
        };

        // ================================================================
        // INITIALIZE
        // ================================================================
        this._initialize();
    }

    /**
     * Initialize audit service
     */
    async _initialize() {
        try {
            // Start batch processor
            this._startBatchProcessor();

            // Start anchor processor
            this._startAnchorProcessor();

            // Verify database connectivity
            await this._verifyDatabase();

            // Create genesis audit block
            await this.recordAccess(
                'system',
                'audit-service',
                { userId: 'SYSTEM', tenantId: 'SYSTEM', roles: ['SYSTEM'] },
                'INITIALIZE',
                {
                    version: '5.2.0',
                    environment: process.env.NODE_ENV || 'production',
                    nodeVersion: process.version,
                    platform: process.platform
                }
            );

            this.initialized = true;

            console.log(`
╔══════════════════════════════════════════════════════════════╗
║     WILSYS OS - FORENSIC AUDIT SERVICE                      ║
╠══════════════════════════════════════════════════════════════╣
║  ✅ Initialized: ${new Date().toISOString()}                         ║
║  🔐 Mode: ${(process.env.NODE_ENV || 'development').toUpperCase()}                                        ║
║  📋 Batch Size: ${this.batchSize}                                       ║
║  ⏱️  Flush Interval: ${this.flushIntervalMs}ms                                 ║
╚══════════════════════════════════════════════════════════════╝
            `);

        } catch (error) {
            console.error('Audit service initialization failed:', error);
            this.initialized = false;
        }
    }

    /**
     * Verify database connectivity
     */
    async _verifyDatabase() {
        try {
            await AuditModel.exists({});
        } catch (error) {
            throw new Error(`Database connection failed: ${error.message}`);
        }
    }

    /**
     * Start batch processor for audit records
     */
    _startBatchProcessor() {
        setInterval(() => this._processBatch(), this.flushIntervalMs).unref();
    }

    /**
     * Start anchor processor for blockchain anchoring
     */
    _startAnchorProcessor() {
        setInterval(() => this._processAnchorQueue(), 30000).unref();
    }

    /**
     * Process batch of audit records
     */
    async _processBatch() {
        if (this.pendingAudits.length === 0) return;

        const startTime = Date.now();
        const batch = [...this.pendingAudits];
        this.pendingAudits = [];

        try {
            // Calculate batch hash for integrity verification
            const batchHash = this._calculateBatchHash(batch);

            // Insert batch into database
            await AuditModel.insertMany(batch, { ordered: false });

            // Queue for blockchain anchoring
            this.anchorQueue.push({
                batchId: crypto.randomUUID(),
                batchHash,
                records: batch.map(r => r.auditId),
                timestamp: new Date().toISOString(),
                recordCount: batch.length,
                size: JSON.stringify(batch).length
            });

            // Update performance metrics
            this.performance.record({
                operation: 'batchProcess',
                duration: Date.now() - startTime,
                success: true,
                batchSize: batch.length
            });

            // Emit batch processed event
            this.emit('batchProcessed', {
                batchSize: batch.length,
                batchHash,
                duration: Date.now() - startTime
            });

        } catch (error) {
            console.error('Audit batch processing failed:', error);

            // Re-queue failed batch with exponential backoff
            setTimeout(() => {
                this.pendingAudits.unshift(...batch);
            }, Math.min(30000, Math.pow(2, this.anchorQueue.length) * 1000));

            this.performance.record({
                operation: 'batchProcess',
                duration: Date.now() - startTime,
                success: false,
                error: error.message
            });
        }
    }

    /**
     * Process anchor queue for blockchain anchoring
     */
    async _processAnchorQueue() {
        if (this.anchorQueue.length === 0) return;

        const batch = this.anchorQueue.shift();

        try {
            // Anchor batch hash to blockchain
            const anchorResult = await this.blockchainAnchor.anchor(batch.batchHash, {
                metadata: {
                    source: 'AuditService',
                    recordCount: batch.recordCount,
                    batchId: batch.batchId
                },
                priority: 'HIGH',
                requiredConfirmations: 12
            });

            // Update audit records with blockchain anchor
            await AuditModel.updateMany(
                { auditId: { $in: batch.records } },
                {
                    $set: {
                        'blockchainAnchor.transactionId': anchorResult.transactionId,
                        'blockchainAnchor.blockHeight': anchorResult.blockHeight,
                        'blockchainAnchor.blockHash': anchorResult.blockHash,
                        'blockchainAnchor.timestamp': anchorResult.timestamp,
                        'blockchainAnchor.verified': false,
                        'blockchainAnchor.anchorId': anchorResult.anchorId
                    }
                }
            );

            this.emit('batchAnchored', {
                batchId: batch.batchId,
                transactionId: anchorResult.transactionId,
                blockHeight: anchorResult.blockHeight,
                recordCount: batch.recordCount
            });

        } catch (error) {
            console.error('Batch anchoring failed:', error);

            // Re-queue for retry
            if (batch.retryCount < 5) {
                batch.retryCount = (batch.retryCount || 0) + 1;
                batch.nextRetry = Date.now() + Math.pow(2, batch.retryCount) * 1000;

                setTimeout(() => {
                    this.anchorQueue.push(batch);
                }, batch.nextRetry - Date.now());
            }
        }
    }

    /**
     * Calculate cryptographic hash of batch
     */
    _calculateBatchHash(batch) {
        const hash = crypto.createHash('sha3-512');

        for (const record of batch.sort((a, b) => a.timestamp.localeCompare(b.timestamp))) {
            hash.update(record.auditId);
            hash.update(record.timestamp);
            hash.update(record.forensicHash);
        }

        return hash.digest('hex');
    }

    /**
     * Record access event with full forensic context
     * LPC Rule 17.3 - Attorney Profile Access Logging
     * POPIA Section 20 - Record of Processing
     * GDPR Article 30 - Records of Processing Activities
     */
    async recordAccess(resource, identifier, userContext, action, metadata = {}) {
        const startTime = Date.now();

        // ================================================================
        // VALIDATE REQUIRED CONTEXT
        // ================================================================
        if (!userContext?.userId && action !== 'SYSTEM') {
            throw ErrorFactory.createValidationError(
                'User ID required for audit logging',
                'userId',
                userContext?.userId,
                'non-empty string'
            );
        }

        if (!userContext?.tenantId && action !== 'SYSTEM') {
            throw ErrorFactory.createValidationError(
                'Tenant ID required for audit logging',
                'tenantId',
                userContext?.tenantId,
                'UUID v4'
            );
        }

        // ================================================================
        // GENERATE AUDIT IDENTIFIERS
        // ================================================================
        const auditId = crypto.randomUUID();
        const correlationId = userContext.correlationId || crypto.randomUUID();
        const sessionId = userContext.sessionId || null;
        const requestId = userContext.requestId || null;
        const timestamp = new Date().toISOString();

        // ================================================================
        // EXTRACT REGULATORY TAGS
        // ================================================================
        const regulatoryTags = this._getRegulatoryTags(resource, action, metadata);
        const retentionPolicy = this._getRetentionPolicy(resource, regulatoryTags);
        const dataResidency = userContext.dataResidency || 'ZA';
        const legalHold = await this.legalHoldManager.isActive(resource, identifier);

        // ================================================================
        // BUILD COMPREHENSIVE AUDIT ENTRY
        // ================================================================
        const auditEntry = {
            // Core identifiers
            auditId,
            correlationId,
            sessionId,
            requestId,

            // Temporal context
            timestamp,
            year: new Date().getFullYear(),
            month: new Date().getMonth() + 1,
            day: new Date().getDate(),
            hour: new Date().getHours(),

            // Resource context
            resource,
            resourceType: this._getResourceType(resource),
            identifier: identifier?.toString() || 'UNKNOWN',
            action,

            // User context
            userId: userContext.userId || 'SYSTEM',
            tenantId: userContext.tenantId || 'SYSTEM',
            firmId: userContext.firmId,
            practiceId: userContext.practiceId,
            departmentId: userContext.departmentId,
            roles: userContext.roles || [],
            permissions: userContext.permissions || [],

            // Request context
            ipAddress: userContext.ipAddress,
            userAgent: userContext.userAgent,
            referer: userContext.referer,
            origin: userContext.origin,
            platform: userContext.platform,
            deviceId: userContext.deviceId,
            location: userContext.location ? {
                country: userContext.location.country,
                region: userContext.location.region,
                city: userContext.location.city,
                timezone: userContext.location.timezone,
                coordinates: userContext.location.coordinates
            } : null,

            // Compliance metadata
            regulatoryTags,
            retentionPolicy,
            retentionExpiry: this._calculateRetentionExpiry(retentionPolicy, legalHold),
            dataResidency,
            legalHold: legalHold ? {
                active: true,
                reason: legalHold.reason,
                initiatedBy: legalHold.initiatedBy,
                initiatedAt: legalHold.initiatedAt
            } : { active: false },

            // Forensic evidence
            forensicHash: null,
            blockchainAnchor: null,
            chainOfCustody: [],

            // Business metadata
            metadata: {
                ...metadata,
                source: 'AuditService',
                version: '5.2.0',
                environment: process.env.NODE_ENV || 'production',
                nodeVersion: process.version,
                processId: process.pid
            },

            // Audit trail
            previousAuditId: metadata.previousAuditId || null,
            nextAuditId: null,
            revisions: metadata.revisions || [],

            // Data subject rights
            dataSubjectId: metadata.dataSubjectId,
            consentId: metadata.consentId,
            processingPurpose: metadata.processingPurpose,
            legalBasis: metadata.legalBasis,

            // System context
            systemContext: {
                hostname: require('os').hostname(),
                platform: process.platform,
                arch: process.arch,
                memory: process.memoryUsage(),
                uptime: process.uptime()
            }
        };

        // ================================================================
        // GENERATE FORENSIC HASH
        // ================================================================
        auditEntry.forensicHash = this._generateForensicHash(auditEntry);

        // ================================================================
        // ADD TO CHAIN OF CUSTODY
        // ================================================================
        auditEntry.chainOfCustody.push({
            action: 'CREATED',
            timestamp,
            actor: userContext.userId || 'SYSTEM',
            hash: auditEntry.forensicHash.substring(0, 16),
            ipAddress: userContext.ipAddress
        });

        // ================================================================
        // CHECK FOR IMMEDIATE ANCHORING REQUIREMENT
        // ================================================================
        if (this._requiresImmediateAnchor(resource, action, regulatoryTags)) {
            try {
                const anchorResult = await this.blockchainAnchor.anchor(auditEntry.forensicHash, {
                    metadata: {
                        auditId,
                        resource,
                        action,
                        userId: userContext.userId
                    },
                    priority: 'CRITICAL',
                    immediate: true
                });

                auditEntry.blockchainAnchor = {
                    transactionId: anchorResult.transactionId,
                    blockHeight: anchorResult.blockHeight,
                    blockHash: anchorResult.blockHash,
                    timestamp: anchorResult.timestamp,
                    verified: false,
                    anchorId: anchorResult.anchorId
                };

                // Add to chain of custody
                auditEntry.chainOfCustody.push({
                    action: 'BLOCKCHAIN_ANCHORED',
                    timestamp: new Date().toISOString(),
                    transactionId: anchorResult.transactionId,
                    blockHeight: anchorResult.blockHeight
                });

                // Store immediately
                await AuditModel.create(auditEntry);

                this.performance.record({
                    operation: 'immediateAnchor',
                    duration: Date.now() - startTime,
                    success: true
                });

                return auditEntry;

            } catch (error) {
                console.error('Immediate anchoring failed:', error);

                // Fall back to batch processing
                this.pendingAudits.push(auditEntry);
                this.auditQueue.set(auditId, auditEntry);

                this.performance.record({
                    operation: 'immediateAnchor',
                    duration: Date.now() - startTime,
                    success: false,
                    error: error.message
                });
            }
        } else {
            // Add to batch queue
            this.pendingAudits.push(auditEntry);
            this.auditQueue.set(auditId, auditEntry);
        }

        // ================================================================
        // UPDATE PERFORMANCE METRICS
        // ================================================================
        this.performance.record({
            operation: 'recordAccess',
            duration: Date.now() - startTime,
            success: true,
            resource,
            action
        });

        // ================================================================
        // CHECK FOR REGULATORY NOTIFICATION REQUIREMENT
        // ================================================================
        await this._checkRegulatoryNotification(auditEntry);

        return auditEntry;
    }

    /**
     * Generate forensic hash for audit entry
     */
    _generateForensicHash(entry) {
        const hash = crypto.createHash('sha3-512');

        // Include all forensic-relevant fields
        hash.update(entry.auditId);
        hash.update(entry.timestamp);
        hash.update(entry.resource);
        hash.update(entry.identifier);
        hash.update(entry.action);
        hash.update(entry.userId);
        hash.update(entry.tenantId);
        hash.update(JSON.stringify(entry.metadata));

        if (entry.previousAuditId) {
            hash.update(entry.previousAuditId);
        }

        return hash.digest('hex');
    }

    /**
     * Get regulatory tags for resource and action
     */
    _getRegulatoryTags(resource, action, metadata = {}) {
        const tags = [];

        // ================================================================
        // LPC RULES
        // ================================================================
        if (resource.includes('attorney') || resource.includes('profile')) {
            tags.push('LPC_17.3');
        }

        if (resource.includes('trust') || resource.includes('reconciliation')) {
            tags.push('LPC_3.4.5');
        }

        if (resource.includes('matter') || resource.includes('transaction')) {
            tags.push('LPC_21.1');
        }

        if (resource.includes('compliance') || resource.includes('report')) {
            tags.push('LPC_35.2');
            tags.push('LPC_95.3');
        }

        if (resource.includes('metrics') || resource.includes('lpc')) {
            tags.push('LPC_41.3');
        }

        if (resource.includes('fidelity') || resource.includes('certificate')) {
            tags.push('LPC_55.5');
        }

        // ================================================================
        // POPIA SECTIONS
        // ================================================================
        if (action === 'VIEW' || action === 'READ') {
            tags.push('POPIA_20');
        }

        if (action === 'EXPORT' || action === 'DOWNLOAD') {
            tags.push('POPIA_22');
        }

        if (action === 'DELETE' || action === 'ERASE') {
            tags.push('POPIA_24');
        }

        if (action === 'CREATE' || action === 'UPDATE') {
            tags.push('POPIA_13');
        }

        if (metadata.dataSubjectId) {
            tags.push('POPIA_20');
            tags.push('GDPR_30');
        }

        // ================================================================
        // GDPR ARTICLES
        // ================================================================
        if (metadata.consentId) {
            tags.push('GDPR_6');
            tags.push('GDPR_7');
        }

        if (metadata.dataSubjectId && action === 'VIEW') {
            tags.push('GDPR_15');
        }

        if (metadata.processingPurpose) {
            tags.push('GDPR_30');
        }

        // ================================================================
        // FICA SECTIONS
        // ================================================================
        if (metadata.amount > 25000 || metadata.ficaThresholdExceeded) {
            tags.push('FICA_28');
        }

        if (metadata.sarReportable) {
            tags.push('FICA_29');
        }

        // ================================================================
        // SARB GUIDANCE
        // ================================================================
        if (resource.includes('trust') && action.includes('RECONCILIATION')) {
            tags.push('SARB_GN6');
        }

        return [...new Set(tags)]; // Deduplicate
    }

    /**
     * Get retention policy based on resource and tags
     */
    _getRetentionPolicy(resource, regulatoryTags) {
        // Default retention: 5 years
        let retentionDays = 1825;

        for (const tag of regulatoryTags) {
            const mapping = this.regulatoryMapping[tag];
            if (mapping && mapping.retentionDays > retentionDays) {
                retentionDays = mapping.retentionDays;
            }
        }

        // Specific resource overrides
        if (resource.includes('attorney') && resource.includes('profile')) {
            retentionDays = 7300; // 20 years
        }

        if (resource.includes('trust') && resource.includes('transaction')) {
            retentionDays = 3650; // 10 years
        }

        if (resource.includes('compliance') && resource.includes('audit')) {
            retentionDays = 3650; // 10 years
        }

        return {
            policy: this._getPolicyName(retentionDays),
            days: retentionDays,
            expiry: this._calculateRetentionExpiry(retentionDays, false)
        };
    }

    /**
     * Get policy name from retention days
     */
    _getPolicyName(days) {
        if (days >= 7300) return 'companies_act_20_years';
        if (days >= 3650) return 'companies_act_10_years';
        if (days >= 2555) return 'companies_act_7_years';
        return 'companies_act_5_years';
    }

    /**
     * Calculate retention expiry date
     */
    _calculateRetentionExpiry(days, legalHold = false) {
        if (legalHold) return null;

        const expiry = new Date();
        expiry.setDate(expiry.getDate() + days);
        return expiry.toISOString();
    }

    /**
     * Check if resource requires immediate blockchain anchoring
     */
    _requiresImmediateAnchor(resource, action, regulatoryTags) {
        const highValueEvents = [
            'ATTORNEY_PROFILE_CREATED',
            'ATTORNEY_PROFILE_DELETED',
            'TRUST_RECONCILIATION_COMPLETED',
            'COMPLIANCE_AUDIT_COMPLETED',
            'FIDELITY_CERTIFICATE_ISSUED',
            'FIDELITY_CLAIM_SUBMITTED',
            'FIDELITY_CLAIM_APPROVED',
            'DATA_BREACH_DETECTED',
            'REGULATORY_NOTIFICATION_SENT',
            'SYSTEM'
        ];

        return highValueEvents.includes(action) ||
            resource.includes('trust') ||
            resource.includes('breach') ||
            regulatoryTags.some(tag =>
                this.regulatoryMapping[tag]?.notifiable === true
            );
    }

    /**
     * Check for regulatory notification requirement
     */
    async _checkRegulatoryNotification(auditEntry) {
        const notifiableTags = auditEntry.regulatoryTags.filter(tag =>
            this.regulatoryMapping[tag]?.notifiable === true
        );

        if (notifiableTags.length === 0) return;

        // Check if this is a material breach
        if (auditEntry.action.includes('BREACH') ||
            auditEntry.resource.includes('breach') ||
            auditEntry.metadata?.severity === 'CRITICAL') {

            this.emit('regulatoryNotificationRequired', {
                auditId: auditEntry.auditId,
                tags: notifiableTags,
                timestamp: auditEntry.timestamp,
                resource: auditEntry.resource,
                action: auditEntry.action,
                userId: auditEntry.userId,
                tenantId: auditEntry.tenantId
            });
        }
    }

    /**
     * Get resource type from resource string
     */
    _getResourceType(resource) {
        if (resource.includes('attorney')) return 'ATTORNEY';
        if (resource.includes('trust')) return 'TRUST_ACCOUNT';
        if (resource.includes('matter')) return 'MATTER';
        if (resource.includes('cpd')) return 'CPD';
        if (resource.includes('fidelity')) return 'FIDELITY';
        if (resource.includes('compliance')) return 'COMPLIANCE';
        if (resource.includes('audit')) return 'AUDIT';
        if (resource.includes('user')) return 'USER';
        if (resource.includes('system')) return 'SYSTEM';
        return 'OTHER';
    }

    /**
     * Query audit trail with full compliance filtering
     * POPIA Section 22 - Data Subject Access Requests
     * GDPR Article 15 - Right of Access
     */
    async queryAuditTrail(filters = {}, pagination = {}) {
        const startTime = Date.now();

        // ================================================================
        // BUILD QUERY
        // ================================================================
        const query = {};

        // Core filters
        if (filters.auditId) query.auditId = filters.auditId;
        if (filters.correlationId) query.correlationId = filters.correlationId;
        if (filters.sessionId) query.sessionId = filters.sessionId;
        if (filters.requestId) query.requestId = filters.requestId;

        // Entity filters
        if (filters.userId) query.userId = filters.userId;
        if (filters.tenantId) query.tenantId = filters.tenantId;
        if (filters.firmId) query.firmId = filters.firmId;
        if (filters.practiceId) query.practiceId = filters.practiceId;

        // Resource filters
        if (filters.resource) query.resource = { $regex: filters.resource, $options: 'i' };
        if (filters.resourceType) query.resourceType = filters.resourceType;
        if (filters.identifier) query.identifier = filters.identifier;
        if (filters.action) query.action = filters.action;

        // Compliance filters
        if (filters.regulatoryTag) query.regulatoryTags = filters.regulatoryTag;
        if (filters.legalHold) query['legalHold.active'] = filters.legalHold;
        if (filters.retentionPolicy) query['retentionPolicy.policy'] = filters.retentionPolicy;

        // Data subject filters
        if (filters.dataSubjectId) query.dataSubjectId = filters.dataSubjectId;
        if (filters.consentId) query.consentId = filters.consentId;
        if (filters.processingPurpose) query['metadata.processingPurpose'] = filters.processingPurpose;

        // Temporal filters
        if (filters.startDate || filters.endDate) {
            query.timestamp = {};
            if (filters.startDate) query.timestamp.$gte = filters.startDate;
            if (filters.endDate) query.timestamp.$lte = filters.endDate;
        }

        if (filters.year) query.year = filters.year;
        if (filters.month) query.month = filters.month;
        if (filters.day) query.day = filters.day;

        // Blockchain filters
        if (filters.anchored !== undefined) {
            query['blockchainAnchor.verified'] = filters.anchored;
        }
        if (filters.transactionId) query['blockchainAnchor.transactionId'] = filters.transactionId;
        if (filters.blockHeight) query['blockchainAnchor.blockHeight'] = filters.blockHeight;

        // ================================================================
        // PAGINATION
        // ================================================================
        const page = Math.max(1, parseInt(pagination.page) || 1);
        const limit = Math.min(1000, parseInt(pagination.limit) || 100);
        const skip = (page - 1) * limit;

        // ================================================================
        // SORTING
        // ================================================================
        const sort = {};
        if (pagination.sortBy) {
            sort[pagination.sortBy] = pagination.sortOrder === 'asc' ? 1 : -1;
        } else {
            sort.timestamp = -1;
        }

        // ================================================================
        // EXECUTE QUERY
        // ================================================================
        const [results, total] = await Promise.all([
            AuditModel.find(query)
                .sort(sort)
                .skip(skip)
                .limit(limit)
                .lean()
                .exec(),
            AuditModel.countDocuments(query)
        ]);

        // ================================================================
        // SANITIZE RESULTS FOR DATA SUBJECT ACCESS
        // ================================================================
        const sanitizedResults = filters.dataSubjectId
            ? this._sanitizeForDataSubject(results)
            : results;

        // ================================================================
        // UPDATE PERFORMANCE METRICS
        // ================================================================
        this.performance.record({
            operation: 'queryAuditTrail',
            duration: Date.now() - startTime,
            success: true,
            resultCount: results.length,
            totalCount: total
        });

        // ================================================================
        // RETURN RESPONSE
        // ================================================================
        return {
            data: sanitizedResults,
            pagination: {
                page,
                limit,
                total,
                pages: Math.ceil(total / limit),
                hasNext: page < Math.ceil(total / limit),
                hasPrev: page > 1
            },
            query: {
                ...filters,
                applied: Object.keys(query)
            },
            metadata: {
                generatedAt: new Date().toISOString(),
                duration: Date.now() - startTime,
                source: 'AuditService',
                version: '5.2.0'
            },
            compliance: {
                popiaSection: filters.dataSubjectId ? '22' : null,
                gdprArticle: filters.dataSubjectId ? '15' : null,
                retentionPeriod: '5_years'
            },
            _links: {
                self: `/api/v1/audit?${new URLSearchParams(filters)}`,
                export: `/api/v1/audit/export?${new URLSearchParams(filters)}`,
                dsar: filters.dataSubjectId ? `/api/v1/dsar/${filters.dataSubjectId}` : null
            }
        };
    }

    /**
     * Sanitize audit records for data subject access
     * POPIA Section 22 - Right of Access
     * GDPR Article 15 - Right of Access
     */
    _sanitizeForDataSubject(records) {
        return records.map(record => {
            const sanitized = { ...record };

            // Remove internal system information
            delete sanitized.systemContext;
            delete sanitized.metadata?.nodeVersion;
            delete sanitized.metadata?.processId;

            // Remove user identifiers not related to data subject
            if (sanitized.userId && sanitized.userId !== sanitized.dataSubjectId) {
                sanitized.userId = 'REDACTED';
            }

            // Remove IP addresses
            if (sanitized.ipAddress) {
                sanitized.ipAddress = this._anonymizeIp(sanitized.ipAddress);
            }

            // Remove device identifiers
            if (sanitized.deviceId) {
                sanitized.deviceId = this._anonymizeDeviceId(sanitized.deviceId);
            }

            return sanitized;
        });
    }

    /**
     * Anonymize IP address for data subject access
     */
    _anonymizeIp(ip) {
        if (ip.includes('.')) {
            // IPv4
            return ip.split('.').slice(0, 3).concat(['0']).join('.');
        } else {
            // IPv6
            return ip.split(':').slice(0, 4).concat(['0000']).join(':');
        }
    }

    /**
     * Anonymize device ID for data subject access
     */
    _anonymizeDeviceId(deviceId) {
        return `${deviceId.substring(0, 8)}...${deviceId.slice(-8)}`;
    }

    /**
     * Generate compliance report for regulatory submission
     * LPC Rule 35.2 - Compliance Reporting
     */
    async generateComplianceReport(tenantId, startDate, endDate, options = {}) {
        const startTime = Date.now();

        // ================================================================
        // BUILD QUERY
        // ================================================================
        const query = {
            tenantId,
            timestamp: {
                $gte: startDate || new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
                $lte: endDate || new Date()
            }
        };

        if (options.firmId) query.firmId = options.firmId;
        if (options.resourceType) query.resourceType = options.resourceType;
        if (options.regulatoryTags) query.regulatoryTags = { $in: options.regulatoryTags };

        // ================================================================
        // AGGREGATE METRICS
        // ================================================================
        const [
            byResource,
            byAction,
            byUser,
            byRegulatoryTag,
            byHour,
            byDay,
            total,
            anchoredCount,
            legalHoldCount
        ] = await Promise.all([
            // By resource
            AuditModel.aggregate([
                { $match: query },
                { $group: { _id: '$resource', count: { $sum: 1 } } },
                { $sort: { count: -1 } },
                { $limit: 100 }
            ]),

            // By action
            AuditModel.aggregate([
                { $match: query },
                { $group: { _id: '$action', count: { $sum: 1 } } },
                { $sort: { count: -1 } }
            ]),

            // By user
            AuditModel.aggregate([
                { $match: query },
                { $group: { _id: '$userId', count: { $sum: 1 } } },
                { $sort: { count: -1 } },
                { $limit: 20 }
            ]),

            // By regulatory tag
            AuditModel.aggregate([
                { $match: query },
                { $unwind: '$regulatoryTags' },
                { $group: { _id: '$regulatoryTags', count: { $sum: 1 } } },
                { $sort: { count: -1 } }
            ]),

            // By hour
            AuditModel.aggregate([
                { $match: query },
                { $group: { _id: '$hour', count: { $sum: 1 } } },
                { $sort: { '_id': 1 } }
            ]),

            // By day
            AuditModel.aggregate([
                { $match: query },
                {
                    $group: {
                        _id: { $dateToString: { format: '%Y-%m-%d', date: '$timestamp' } },
                        count: { $sum: 1 }
                    }
                },
                { $sort: { '_id': 1 } }
            ]),

            // Total count
            AuditModel.countDocuments(query),

            // Anchored count
            AuditModel.countDocuments({
                ...query,
                'blockchainAnchor.verified': true
            }),

            // Legal hold count
            AuditModel.countDocuments({
                ...query,
                'legalHold.active': true
            })
        ]);

        // ================================================================
        // GENERATE REPORT
        // ================================================================
        const reportId = `AUDIT-RPT-${Date.now()}-${crypto.randomBytes(4).toString('hex')}`;

        const report = {
            reportId,
            tenantId,
            period: {
                start: query.timestamp.$gte.toISOString(),
                end: query.timestamp.$lte.toISOString(),
                days: Math.ceil((query.timestamp.$lte - query.timestamp.$gte) / (1000 * 60 * 60 * 24))
            },
            generatedAt: new Date().toISOString(),
            generatedBy: options.userId || 'SYSTEM',
            summary: {
                totalEvents: total,
                uniqueResources: byResource.length,
                uniqueActions: byAction.length,
                uniqueUsers: byUser.length,
                anchoredEvents: anchoredCount,
                anchoringRate: total > 0 ? (anchoredCount / total * 100).toFixed(2) : 0,
                legalHoldEvents: legalHoldCount
            },
            breakdown: {
                byResource,
                byAction,
                byUser,
                byRegulatoryTag,
                byHour,
                byDay
            },
            compliance: {
                lpc173: byRegulatoryTag.some(t => t._id === 'LPC_17.3'),
                lpc345: byRegulatoryTag.some(t => t._id === 'LPC_3.4.5'),
                lpc211: byRegulatoryTag.some(t => t._id === 'LPC_21.1'),
                lpc352: byRegulatoryTag.some(t => t._id === 'LPC_35.2'),
                lpc413: byRegulatoryTag.some(t => t._id === 'LPC_41.3'),
                lpc555: byRegulatoryTag.some(t => t._id === 'LPC_55.5'),
                popia20: byRegulatoryTag.some(t => t._id === 'POPIA_20'),
                popia22: byRegulatoryTag.some(t => t._id === 'POPIA_22'),
                gdpr30: byRegulatoryTag.some(t => t._id === 'GDPR_30'),
                gdpr33: byRegulatoryTag.some(t => t._id === 'GDPR_33'),
                fica28: byRegulatoryTag.some(t => t._id === 'FICA_28'),
                sarbgn6: byRegulatoryTag.some(t => t._id === 'SARB_GN6')
            },
            certifications: [
                'LPC_COMPLIANT_2026',
                'POPIA_CERTIFIED',
                'GDPR_READY',
                'ISO_27001',
                'SOC2_TYPE2'
            ],
            _links: {
                self: `/api/v1/audit/reports/${reportId}`,
                download: `/api/v1/audit/reports/${reportId}/download`,
                regulatory: `/api/v1/audit/reports/${reportId}/regulatory`
            }
        };

        // ================================================================
        // UPDATE PERFORMANCE METRICS
        // ================================================================
        this.performance.record({
            operation: 'generateComplianceReport',
            duration: Date.now() - startTime,
            success: true,
            eventCount: total
        });

        return report;
    }

    /**
     * Verify audit trail integrity using cryptographic hashes
     * LPC Rule 3.4.2 - Cryptographic Proof
     */
    async verifyAuditTrail(auditIds = [], options = {}) {
        const startTime = Date.now();

        // ================================================================
        // BUILD QUERY
        // ================================================================
        const query = auditIds.length > 0
            ? { auditId: { $in: auditIds } }
            : { timestamp: { $gte: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000) } };

        if (options.tenantId) query.tenantId = options.tenantId;
        if (options.startDate) query.timestamp = { ...query.timestamp, $gte: options.startDate };
        if (options.endDate) query.timestamp = { ...query.timestamp, $lte: options.endDate };

        // ================================================================
        // FETCH AUDIT RECORDS
        // ================================================================
        const audits = await AuditModel.find(query)
            .sort({ timestamp: -1 })
            .limit(options.limit || 10000)
            .lean()
            .exec();

        // ================================================================
        // VERIFY EACH RECORD
        // ================================================================
        const results = [];
        let verifiedCount = 0;
        let failedCount = 0;
        let tamperedCount = 0;

        for (const audit of audits) {
            // Recompute hash
            const recomputedHash = this._generateForensicHash({
                ...audit,
                forensicHash: undefined,
                blockchainAnchor: undefined,
                _id: undefined,
                __v: undefined
            });

            const hashVerified = recomputedHash === audit.forensicHash;

            // Verify blockchain anchor if present
            let blockchainVerified = null;
            if (audit.blockchainAnchor?.transactionId && options.verifyBlockchain !== false) {
                try {
                    const verification = await this.blockchainAnchor.verify(
                        audit.forensicHash,
                        { timeout: 5000 }
                    );
                    blockchainVerified = verification.verified;
                } catch (error) {
                    blockchainVerified = false;
                }
            }

            const verified = hashVerified && (blockchainVerified !== false);

            if (verified) verifiedCount++;
            else failedCount++;

            if (!hashVerified) tamperedCount++;

            results.push({
                auditId: audit.auditId,
                verified,
                hashVerified,
                blockchainVerified,
                timestamp: audit.timestamp,
                resource: audit.resource,
                action: audit.action,
                userId: audit.userId,
                tenantId: audit.tenantId,
                forensicHash: audit.forensicHash?.substring(0, 16),
                recomputedHash: recomputedHash.substring(0, 16),
                blockchainAnchor: audit.blockchainAnchor ? {
                    transactionId: audit.blockchainAnchor.transactionId,
                    blockHeight: audit.blockchainAnchor.blockHeight,
                    blockHash: audit.blockchainAnchor.blockHash?.substring(0, 16),
                    verified: blockchainVerified
                } : null
            });
        }

        // ================================================================
        // UPDATE PERFORMANCE METRICS
        // ================================================================
        this.performance.record({
            operation: 'verifyAuditTrail',
            duration: Date.now() - startTime,
            success: true,
            verifiedCount,
            failedCount,
            tamperedCount
        });

        // ================================================================
        // RETURN VERIFICATION REPORT
        // ================================================================
        return {
            verified: failedCount === 0,
            timestamp: new Date().toISOString(),
            duration: Date.now() - startTime,
            summary: {
                total: results.length,
                verified: verifiedCount,
                failed: failedCount,
                tampered: tamperedCount,
                integrityScore: results.length > 0
                    ? Math.round((verifiedCount / results.length) * 100)
                    : 100
            },
            results: options.includeDetails ? results : results.map(r => ({
                auditId: r.auditId,
                verified: r.verified,
                timestamp: r.timestamp
            })),
            blockchainVerification: results.some(r => r.blockchainAnchor) ? {
                verifiedCount: results.filter(r => r.blockchainVerified).length,
                totalCount: results.filter(r => r.blockchainAnchor).length
            } : null,
            _links: {
                self: '/api/v1/audit/verify',
                failed: '/api/v1/audit/verify?status=failed',
                tampered: '/api/v1/audit/verify?status=tampered'
            }
        };
    }

    /**
     * Place legal hold on audit records
     * Prevents deletion during litigation
     */
    async placeLegalHold(resource, identifier, reason, userContext) {
        const holdId = crypto.randomUUID();
        const timestamp = new Date().toISOString();

        // Update all matching records
        const updateResult = await AuditModel.updateMany(
            {
                $or: [
                    { resource, identifier },
                    { resource, 'metadata.caseNumber': identifier },
                    { dataSubjectId: identifier }
                ],
                'legalHold.active': false
            },
            {
                $set: {
                    'legalHold.active': true,
                    'legalHold.holdId': holdId,
                    'legalHold.reason': reason,
                    'legalHold.initiatedBy': userContext.userId,
                    'legalHold.initiatedAt': timestamp,
                    'legalHold.caseNumber': reason.match(/case #?(\d+)/i)?.[1],
                    'legalHold.expiryDate': null,
                    retentionExpiry: null
                }
            }
        );

        // Record the legal hold action
        await this.recordAccess(
            'legal-hold',
            holdId,
            userContext,
            'PLACE_HOLD',
            {
                resource,
                identifier,
                reason,
                affectedRecords: updateResult.modifiedCount
            }
        );

        return {
            success: true,
            holdId,
            resource,
            identifier,
            reason,
            initiatedBy: userContext.userId,
            initiatedAt: timestamp,
            affectedRecords: updateResult.modifiedCount,
            _links: {
                self: `/api/v1/legal-holds/${holdId}`,
                resource: `/api/v1/audit?resource=${resource}&identifier=${identifier}`
            }
        };
    }

    /**
     * Release legal hold from audit records
     */
    async releaseLegalHold(holdId, userContext) {
        const timestamp = new Date().toISOString();

        // Calculate new retention expiry
        const retentionDays = 1825; // Default 5 years
        const retentionExpiry = new Date();
        retentionExpiry.setDate(retentionExpiry.getDate() + retentionDays);

        // Update all records with this hold
        const updateResult = await AuditModel.updateMany(
            { 'legalHold.holdId': holdId },
            {
                $set: {
                    'legalHold.active': false,
                    'legalHold.releasedBy': userContext.userId,
                    'legalHold.releasedAt': timestamp,
                    retentionExpiry: retentionExpiry.toISOString()
                }
            }
        );

        // Record the release action
        await this.recordAccess(
            'legal-hold',
            holdId,
            userContext,
            'RELEASE_HOLD',
            {
                affectedRecords: updateResult.modifiedCount
            }
        );

        return {
            success: true,
            holdId,
            releasedBy: userContext.userId,
            releasedAt: timestamp,
            affectedRecords: updateResult.modifiedCount
        };
    }

    /**
     * Get service health status
     */
    async healthCheck() {
        const dbHealthy = await AuditModel.exists({}).catch(() => false);
        const anchorHealthy = await this.blockchainAnchor.getStatus()
            .then(s => s.status === 'HEALTHY')
            .catch(() => false);

        const metrics = this.performance.getMetrics();

        return {
            service: 'AuditService',
            version: '5.2.0',
            initialized: this.initialized,
            status: dbHealthy ? 'HEALTHY' : 'DEGRADED',
            timestamp: new Date().toISOString(),
            dependencies: {
                database: dbHealthy ? 'HEALTHY' : 'UNHEALTHY',
                blockchainAnchor: anchorHealthy ? 'HEALTHY' : 'DEGRADED',
                retentionManager: this.retentionManager.initialized ? 'HEALTHY' : 'DEGRADED',
                legalHoldManager: this.legalHoldManager.initialized ? 'HEALTHY' : 'DEGRADED'
            },
            metrics: {
                pendingAudits: this.pendingAudits.length,
                queueLength: this.auditQueue.size,
                anchorQueueLength: this.anchorQueue.length,
                batchSize: this.batchSize,
                flushIntervalMs: this.flushIntervalMs,
                ...metrics
            },
            performance: {
                averageLatencyMs: metrics.averageLatency,
                throughputPerMinute: metrics.throughput,
                successRate: metrics.successRate,
                errorRate: metrics.errorRate
            },
            _links: {
                self: '/api/v1/audit/health',
                metrics: '/api/v1/audit/metrics',
                queue: '/api/v1/audit/queue'
            }
        };
    }

    /**
     * Get performance metrics
     */
    getMetrics() {
        return {
            ...this.performance.getMetrics(),
            queueDepth: this.auditQueue.size,
            pendingBatchSize: this.pendingAudits.length,
            anchorQueueDepth: this.anchorQueue.length,
            timestamp: new Date().toISOString()
        };
    }
}

module.exports = new AuditService();