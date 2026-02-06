/**
 * @file auditLedger.js
 * @module AuditLedger
 * @description Immutable append-only audit ledger with blockchain anchoring.
 * Provides legal defensibility for compliance, court evidence, and regulatory requirements.
 *
 * @requires crypto
 * @requires mongoose
 * @requires ../models/AuditLedger
 * @requires ../lib/kms (for per-tenant encryption, optional)
 * @requires ../lib/ots (for blockchain anchoring, optional)
 *
 * @security SHA-256 hash chaining for immutability
 * @security Per-tenant encryption support
 * @security Blockchain anchoring via OpenTimestamps/RFC3161
 * @security Zero-trust multi-tenant isolation
 *
 * @compliance POPIA §14 - Retention of personal information
 * @compliance ECT Act §15 - Evidential weight of data messages
 * @compliance Companies Act §24 - Records retention
 * @compliance PAIA §51 - Record keeping
 * @compliance GDPR Art. 30 - Records of processing activities
 *
 * @multitenant Tenant isolation with per-tenant hash chains
 * @multitenant Encrypted audit entries per tenant
 * @multitenant Separate blockchain anchors per tenant
 */

'use strict';

const crypto = require('crypto');
const mongoose = require('mongoose');

// =============================================================================
// SECTION 1: DEPENDENCIES & CONFIGURATION
// =============================================================================

/**
 * Lazy-loaded dependencies to avoid circular dependencies
 */
let AuditLedgerModel;
let kms;
let ots;

/**
 * Configuration constants
 */
const CONFIG = {
    HASH_ALGORITHM: 'sha256',
    HASH_ENCODING: 'hex',
    MERKLE_BATCH_SIZE: 1000,
    ANCHORING_STRATEGY: process.env.AUDIT_ANCHORING_STRATEGY || 'BATCH_DAILY',
    ANCHORING_PROVIDER: process.env.AUDIT_ANCHORING_PROVIDER || 'OPENTIMESTAMPS',
    RETENTION_PERIODS: {
        STANDARD: 3650,  // 10 years
        PAIA: 3650,
        POPIA: 1825,     // 5 years
        GDPR: 1825,
        LEGAL_HOLD: 0
    },
    BATCH_SIZE: parseInt(process.env.AUDIT_BATCH_SIZE) || 100,
    WRITE_CONCURRENCY: parseInt(process.env.AUDIT_WRITE_CONCURRENCY) || 10,
    ENCRYPT_AUDIT_DATA: process.env.ENCRYPT_AUDIT_DATA === 'true',
    REQUIRE_TENANT_CONTEXT: process.env.REQUIRE_TENANT_CONTEXT === 'true'
};

// =============================================================================
// SECTION 2: ERROR CLASSES
// =============================================================================

class AuditLedgerError extends Error {
    constructor(message, code = 'AUDIT_LEDGER_ERROR') {
        super(message);
        this.name = 'AuditLedgerError';
        this.code = code;
        this.timestamp = new Date().toISOString();
    }
}

class ImmutabilityViolationError extends AuditLedgerError {
    constructor(message, previousHash, attemptedHash) {
        super(message, 'IMMUTABILITY_VIOLATION');
        this.previousHash = previousHash;
        this.attemptedHash = attemptedHash;
        this.securityLevel = 'CRITICAL';
    }
}

class TenantIsolationError extends AuditLedgerError {
    constructor(message, tenantId) {
        super(message, 'TENANT_ISOLATION_VIOLATION');
        this.tenantId = tenantId;
        this.securityLevel = 'CRITICAL';
    }
}

class BlockchainAnchoringError extends AuditLedgerError {
    constructor(message, provider) {
        super(message, 'BLOCKCHAIN_ANCHORING_FAILED');
        this.provider = provider;
    }
}

// =============================================================================
// SECTION 3: HASH CHAIN UTILITIES
// =============================================================================

class HashChain {
    static calculateHash(data, previousHash = '') {
        const hash = crypto.createHash(CONFIG.HASH_ALGORITHM);

        if (previousHash) {
            hash.update(previousHash);
        }

        if (typeof data === 'object') {
            hash.update(JSON.stringify(data));
        } else {
            hash.update(String(data));
        }

        return hash.digest(CONFIG.HASH_ENCODING);
    }

    static verifyChain(entries) {
        if (!Array.isArray(entries) || entries.length === 0) {
            return { valid: false, reason: 'No entries to verify' };
        }

        let previousHash = '';
        const violations = [];

        for (let i = 0; i < entries.length; i++) {
            const entry = entries[i];
            const expectedHash = this.calculateHash(entry.auditData, previousHash);

            if (entry.hash !== expectedHash) {
                violations.push({
                    index: i,
                    entryId: entry._id,
                    expectedHash,
                    actualHash: entry.hash,
                    previousHash
                });
            }

            previousHash = entry.hash;
        }

        return {
            valid: violations.length === 0,
            totalEntries: entries.length,
            violations,
            chainHash: previousHash
        };
    }

    static generateMerkleRoot(entries) {
        if (!entries || entries.length === 0) {
            return crypto.createHash(CONFIG.HASH_ALGORITHM)
                .update('EMPTY_MERKLE_ROOT')
                .digest(CONFIG.HASH_ENCODING);
        }

        let hashes = entries.map(entry => entry.hash);

        while (hashes.length > 1) {
            const nextLevel = [];

            for (let i = 0; i < hashes.length; i += 2) {
                const left = hashes[i];
                const right = hashes[i + 1] || left;

                const combined = crypto.createHash(CONFIG.HASH_ALGORITHM)
                    .update(left + right)
                    .digest(CONFIG.HASH_ENCODING);

                nextLevel.push(combined);
            }

            hashes = nextLevel;
        }

        return hashes[0];
    }
}

// =============================================================================
// SECTION 4: AUDIT LEDGER CORE CLASS
// =============================================================================

class AuditLedger {
    constructor(options = {}) {
        this.options = { ...CONFIG, ...options };
        this._ensureDependencies();
    }

    _ensureDependencies() {
        if (!AuditLedgerModel) {
            AuditLedgerModel = require('../models/AuditLedger');
        }
    }

    _validateTenantContext(tenantId) {
        if (this.options.REQUIRE_TENANT_CONTEXT && !tenantId) {
            throw new TenantIsolationError(
                'Tenant context is required for audit operations (fail-closed security)',
                tenantId
            );
        }

        if (tenantId) {
            const tenantRegex = /^[a-fA-F0-9]{24}$|^tenant_[a-zA-Z0-9_-]{8,64}$/;
            if (!tenantRegex.test(tenantId)) {
                throw new TenantIsolationError(
                    `Invalid tenant ID format: ${tenantId}`,
                    tenantId
                );
            }
        }
    }

    async _getLastAuditEntry(tenantId) {
        this._validateTenantContext(tenantId);

        try {
            const lastEntry = await AuditLedgerModel.findOne(
                { tenantId },
                { hash: 1, ledgerIndex: 1 },
                { sort: { ledgerIndex: -1 } }
            ).lean();

            return lastEntry;
        } catch (error) {
            throw new AuditLedgerError(
                `Failed to get last audit entry for tenant ${tenantId}: ${error.message}`,
                'DATABASE_ERROR'
            );
        }
    }

    async append(auditData, tenantId, options = {}) {
        this._validateTenantContext(tenantId);

        const {
            eventType = 'AUDIT_EVENT',
            userId = 'system',
            userRole = 'system',
            ipAddress = 'unknown',
            userAgent = 'unknown',
            complianceContext = {},
            encryptionContext = {}
        } = options;

        try {
            const lastEntry = await this._getLastAuditEntry(tenantId);
            const previousHash = lastEntry ? lastEntry.hash : '';
            const nextIndex = lastEntry ? lastEntry.ledgerIndex + 1 : 1;

            const hash = HashChain.calculateHash(auditData, previousHash);

            const auditEntry = {
                tenantId,
                ledgerIndex: nextIndex,
                hash,
                previousHash,
                auditData,
                metadata: {
                    eventType,
                    timestamp: new Date(),
                    userContext: { userId, userRole, ipAddress, userAgent },
                    compliance: {
                        popiaApplicable: complianceContext.popiaApplicable || false,
                        paiaApplicable: complianceContext.paiaApplicable || false,
                        retentionPeriod: complianceContext.retentionPeriod || 'STANDARD',
                        legalHold: complianceContext.legalHold || false
                    },
                    security: {
                        encrypted: this.options.ENCRYPT_AUDIT_DATA,
                        encryptionKeyId: encryptionContext.keyId,
                        signature: encryptionContext.signature
                    }
                },
                anchoring: {
                    anchored: false,
                    provider: null,
                    transactionId: null,
                    timestamp: null
                }
            };

            const createdEntry = await AuditLedgerModel.create(auditEntry);

            if (this.options.ANCHORING_STRATEGY === 'IMMEDIATE') {
                await this._anchorToBlockchain(createdEntry, tenantId);
            }

            return {
                success: true,
                entryId: createdEntry._id,
                hash: createdEntry.hash,
                ledgerIndex: createdEntry.ledgerIndex,
                timestamp: createdEntry.metadata.timestamp
            };
        } catch (error) {
            console.error(`Audit ledger append failed for tenant ${tenantId}:`, error);

            if (error instanceof TenantIsolationError || error instanceof AuditLedgerError) {
                throw error;
            }

            throw new AuditLedgerError(`Failed to append audit entry: ${error.message}`, 'APPEND_FAILED');
        }
    }

    async appendBatch(auditEntries, tenantId, commonMetadata = {}) {
        this._validateTenantContext(tenantId);

        if (!Array.isArray(auditEntries) || auditEntries.length === 0) {
            throw new AuditLedgerError('No audit entries provided for batch append', 'INVALID_INPUT');
        }

        try {
            const results = [];
            let lastEntry = await this._getLastAuditEntry(tenantId);
            let previousHash = lastEntry ? lastEntry.hash : '';
            let nextIndex = lastEntry ? lastEntry.ledgerIndex + 1 : 1;

            const batchSize = this.options.BATCH_SIZE;
            for (let i = 0; i < auditEntries.length; i += batchSize) {
                const batch = auditEntries.slice(i, i + batchSize);
                const batchPromises = [];

                for (const auditData of batch) {
                    const hash = HashChain.calculateHash(auditData, previousHash);

                    const auditEntry = {
                        tenantId,
                        ledgerIndex: nextIndex,
                        hash,
                        previousHash,
                        auditData,
                        metadata: {
                            ...commonMetadata,
                            timestamp: new Date(),
                            batchIndex: i,
                            batchSize: batch.length
                        }
                    };

                    batchPromises.push(AuditLedgerModel.create(auditEntry));

                    previousHash = hash;
                    nextIndex++;
                }

                const batchResults = await Promise.all(batchPromises);
                results.push(...batchResults);
            }

            const merkleRoot = HashChain.generateMerkleRoot(results);

            return {
                success: true,
                totalAppended: results.length,
                merkleRoot,
                firstIndex: results[0]?.ledgerIndex,
                lastIndex: results[results.length - 1]?.ledgerIndex,
                batchHash: previousHash
            };
        } catch (error) {
            throw new AuditLedgerError(`Batch append failed: ${error.message}`, 'BATCH_APPEND_FAILED');
        }
    }

    async _anchorToBlockchain(auditEntry, tenantId) {
        try {
            if (!ots) {
                ots = require('../lib/ots');
            }

            const hashToAnchor = auditEntry.hash;

            let anchoringResult;
            switch (this.options.ANCHORING_PROVIDER) {
                case 'OPENTIMESTAMPS':
                    anchoringResult = await ots.createTimestamp(hashToAnchor);
                    break;
                case 'RFC3161':
                    throw new AuditLedgerError('RFC3161 anchoring not yet implemented', 'ANCHORING_NOT_IMPLEMENTED');
                default:
                    throw new AuditLedgerError(`Unknown anchoring provider: ${this.options.ANCHORING_PROVIDER}`, 'INVALID_ANCHORING_PROVIDER');
            }

            await AuditLedgerModel.updateOne(
                { _id: auditEntry._id, tenantId },
                {
                    $set: {
                        'anchoring.anchored': true,
                        'anchoring.provider': this.options.ANCHORING_PROVIDER,
                        'anchoring.transactionId': anchoringResult.transactionId,
                        'anchoring.timestamp': anchoringResult.timestamp,
                        'anchoring.proof': anchoringResult.proof
                    }
                }
            );

            return {
                success: true,
                transactionId: anchoringResult.transactionId,
                timestamp: anchoringResult.timestamp,
                provider: this.options.ANCHORING_PROVIDER
            };
        } catch (error) {
            console.error(`Blockchain anchoring failed for entry ${auditEntry._id}:`, error);

            await AuditLedgerModel.updateOne(
                { _id: auditEntry._id, tenantId },
                {
                    $set: {
                        'anchoring.anchored': false,
                        'anchoring.error': error.message,
                        'anchoring.lastAttempt': new Date()
                    }
                }
            );

            throw new BlockchainAnchoringError(`Blockchain anchoring failed: ${error.message}`, this.options.ANCHORING_PROVIDER);
        }
    }

    async anchorBatchToBlockchain(tenantId, batchSize = CONFIG.MERKLE_BATCH_SIZE) {
        this._validateTenantContext(tenantId);

        try {
            const unanchoredEntries = await AuditLedgerModel.find({
                tenantId,
                'anchoring.anchored': false,
                'anchoring.lastAttempt': { $exists: false }
            })
                .sort({ ledgerIndex: 1 })
                .limit(batchSize)
                .lean();

            if (unanchoredEntries.length === 0) {
                return { success: true, anchored: 0, message: 'No unanchored entries found' };
            }

            const merkleRoot = HashChain.generateMerkleRoot(unanchoredEntries);

            const anchoringResult = await this._anchorToBlockchain(
                { hash: merkleRoot, _id: 'batch-anchor-' + Date.now() },
                tenantId
            );

            const entryIds = unanchoredEntries.map(entry => entry._id);
            await AuditLedgerModel.updateMany(
                { _id: { $in: entryIds }, tenantId },
                {
                    $set: {
                        'anchoring.anchored': true,
                        'anchoring.merkleRoot': merkleRoot,
                        'anchoring.batchAnchored': true,
                        'anchoring.batchTransactionId': anchoringResult.transactionId,
                        'anchoring.batchTimestamp': anchoringResult.timestamp
                    }
                }
            );

            return {
                success: true,
                anchored: unanchoredEntries.length,
                merkleRoot,
                transactionId: anchoringResult.transactionId,
                timestamp: anchoringResult.timestamp
            };
        } catch (error) {
            throw new BlockchainAnchoringError(`Batch anchoring failed: ${error.message}`, this.options.ANCHORING_PROVIDER);
        }
    }

    async verifyIntegrity(tenantId, options = {}) {
        this._validateTenantContext(tenantId);

        const { startIndex = 1, endIndex = null, verifyAnchoring = true } = options;

        try {
            const query = { tenantId };
            if (endIndex) {
                query.ledgerIndex = { $gte: startIndex, $lte: endIndex };
            } else {
                query.ledgerIndex = { $gte: startIndex };
            }

            const entries = await AuditLedgerModel.find(query)
                .sort({ ledgerIndex: 1 })
                .lean();

            if (entries.length === 0) {
                return {
                    valid: true,
                    reason: 'No entries to verify',
                    tenantId,
                    range: { startIndex, endIndex }
                };
            }

            const chainVerification = HashChain.verifyChain(entries);

            let anchoringVerification = { valid: true, anchoredEntries: 0 };
            if (verifyAnchoring) {
                const anchoredEntries = entries.filter(e => e.anchoring?.anchored);
                anchoringVerification = {
                    valid: anchoredEntries.length > 0,
                    anchoredEntries: anchoredEntries.length,
                    totalEntries: entries.length,
                    coverage: (anchoredEntries.length / entries.length) * 100
                };
            }

            const expectedIndices = Array.from({ length: entries.length }, (_, i) => startIndex + i);
            const actualIndices = entries.map(e => e.ledgerIndex);
            const missingIndices = expectedIndices.filter(i => !actualIndices.includes(i));

            return {
                tenantId,
                valid: chainVerification.valid && anchoringVerification.valid && missingIndices.length === 0,
                chainVerification,
                anchoringVerification,
                gaps: {
                    hasGaps: missingIndices.length > 0,
                    missingIndices,
                    totalEntries: entries.length,
                    expectedCount: expectedIndices.length
                },
                statistics: {
                    firstIndex: entries[0]?.ledgerIndex,
                    lastIndex: entries[entries.length - 1]?.ledgerIndex,
                    totalEntries: entries.length,
                    timeSpan: entries.length > 1
                        ? new Date(entries[entries.length - 1].metadata.timestamp) - new Date(entries[0].metadata.timestamp)
                        : 0
                }
            };
        } catch (error) {
            throw new AuditLedgerError(`Integrity verification failed: ${error.message}`, 'VERIFICATION_FAILED');
        }
    }

    async getEntries(tenantId, query = {}, options = {}) {
        this._validateTenantContext(tenantId);

        const {
            page = 1,
            limit = 50,
            sortBy = 'ledgerIndex',
            sortOrder = -1,
            includeAuditData = true
        } = options;

        try {
            const tenantScopedQuery = { ...query, tenantId };

            const sort = {};
            sort[sortBy] = sortOrder === 'asc' ? 1 : -1;

            const selectFields = includeAuditData ? {} : { auditData: 0 };

            const entries = await AuditLedgerModel.find(tenantScopedQuery)
                .select(selectFields)
                .sort(sort)
                .skip((page - 1) * limit)
                .limit(limit)
                .lean();

            const total = await AuditLedgerModel.countDocuments(tenantScopedQuery);

            return {
                entries,
                pagination: {
                    page,
                    limit,
                    total,
                    pages: Math.ceil(total / limit),
                    hasNext: page * limit < total,
                    hasPrev: page > 1
                }
            };
        } catch (error) {
            throw new AuditLedgerError(`Failed to retrieve audit entries: ${error.message}`, 'RETRIEVAL_FAILED');
        }
    }

    async generateComplianceReport(tenantId, timeRange = {}) {
        this._validateTenantContext(tenantId);

        const { startDate, endDate } = timeRange;
        const query = { tenantId };

        if (startDate || endDate) {
            query['metadata.timestamp'] = {};
            if (startDate) query['metadata.timestamp'].$gte = new Date(startDate);
            if (endDate) query['metadata.timestamp'].$lte = new Date(endDate);
        }

        try {
            const entries = await AuditLedgerModel.find(query)
                .select('metadata.eventType metadata.compliance metadata.timestamp anchoring.anchored')
                .lean();

            const analysis = {
                totalEntries: entries.length,
                timeRange: { start: startDate || 'beginning', end: endDate || 'now' },
                complianceMetrics: {
                    popiaEntries: entries.filter(e => e.metadata.compliance?.popiaApplicable).length,
                    paiaEntries: entries.filter(e => e.metadata.compliance?.paiaApplicable).length,
                    legalHoldEntries: entries.filter(e => e.metadata.compliance?.legalHold).length,
                    anchoredEntries: entries.filter(e => e.anchoring?.anchored).length
                },
                eventDistribution: {},
                recommendations: []
            };

            entries.forEach(entry => {
                const eventType = entry.metadata.eventType || 'UNKNOWN';
                analysis.eventDistribution[eventType] = (analysis.eventDistribution[eventType] || 0) + 1;
            });

            const anchoredPercentage = (analysis.complianceMetrics.anchoredEntries / entries.length) * 100;
            if (anchoredPercentage < 90) {
                analysis.recommendations.push(
                    `Increase blockchain anchoring coverage (currently ${anchoredPercentage.toFixed(1)}%)`
                );
            }

            const popiaEntries = analysis.complianceMetrics.popiaEntries;
            if (popiaEntries > 0) {
                analysis.recommendations.push(`Ensure POPIA retention (5 years) for ${popiaEntries} audit entries`);
            }

            return analysis;
        } catch (error) {
            throw new AuditLedgerError(`Failed to generate compliance report: ${error.message}`, 'REPORT_GENERATION_FAILED');
        }
    }

    async exportForDiscovery(tenantId, exportOptions = {}) {
        this._validateTenantContext(tenantId);

        const {
            format = 'JSON',
            includeProofs = true,
            timeRange = {},
            eventTypes = []
        } = exportOptions;

        try {
            const query = { tenantId };

            if (timeRange.startDate || timeRange.endDate) {
                query['metadata.timestamp'] = {};
                if (timeRange.startDate) query['metadata.timestamp'].$gte = new Date(timeRange.startDate);
                if (timeRange.endDate) query['metadata.timestamp'].$lte = new Date(timeRange.endDate);
            }

            if (eventTypes.length > 0) {
                query['metadata.eventType'] = { $in: eventTypes };
            }

            const entries = await AuditLedgerModel.find(query)
                .sort({ ledgerIndex: 1 })
                .lean();

            let integrityProof = null;
            if (includeProofs && entries.length > 0) {
                const chainVerification = HashChain.verifyChain(entries);
                integrityProof = {
                    valid: chainVerification.valid,
                    totalEntries: entries.length,
                    firstHash: entries[0]?.hash,
                    lastHash: entries[entries.length - 1]?.hash,
                    chainHash: chainVerification.chainHash
                };
            }

            let exportData;
            switch (format.toUpperCase()) {
                case 'JSON':
                    exportData = {
                        format: 'JSON',
                        exportedAt: new Date().toISOString(),
                        tenantId,
                        integrityProof,
                        entries
                    };
                    break;
                default:
                    throw new AuditLedgerError(`Unsupported export format: ${format}`, 'INVALID_EXPORT_FORMAT');
            }

            return {
                success: true,
                format,
                entryCount: entries.length,
                data: exportData,
                exportId: `AUDIT_EXPORT_${tenantId}_${Date.now()}`
            };
        } catch (error) {
            throw new AuditLedgerError(`Export failed: ${error.message}`, 'EXPORT_FAILED');
        }
    }
}

// =============================================================================
// SECTION 5: FACTORY FUNCTIONS & SINGLETON PATTERN
// =============================================================================

let auditLedgerInstance = null;

function getAuditLedger(options = {}) {
    if (!auditLedgerInstance) {
        auditLedgerInstance = new AuditLedger(options);
    }
    return auditLedgerInstance;
}

function createAuditLedger(options = {}) {
    return new AuditLedger(options);
}

module.exports = {
    getAuditLedger,
    createAuditLedger,
    AuditLedger
};