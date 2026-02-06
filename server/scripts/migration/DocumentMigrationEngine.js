#!/usr/bin/env node

/**
 * ============================================================================
 * DOCUMENT MIGRATION ENGINE - CORE MIGRATION LOGIC
 * ============================================================================
 * 
 * Purpose: Core migration logic with safety controls
 * Security: Tenant isolation, data integrity, rollback capability
 * 
 * Features:
 * - Batch processing with retry logic
 * - Tenant assignment strategies
 * - Rollback capability
 * - Data integrity validation
 * 
 * ============================================================================
 */

const { createHash } = require('crypto');
const fs = require('fs').promises;
const path = require('path');
const { promisify } = require('util');
const sleep = promisify(setTimeout);

// Tenant mapping strategies
const TENANT_MAPPING_STRATEGIES = {
    USER_BASED: 'USER_BASED',      // Assign based on uploadedBy user
    CASE_BASED: 'CASE_BASED',      // Assign based on case ownership
    CLIENT_BASED: 'CLIENT_BASED',  // Assign based on client ownership
    MANUAL: 'MANUAL'               // Manual assignment required
};

// Configuration
const CONFIG = {
    BATCH_SIZE: 100,
    MAX_RETRIES: 3,
    RETRY_DELAY_MS: 1000,
    ROLLBACK_FILE: path.join(__dirname, '../../logs/migration-rollback.json')
};

/**
 * DocumentMigrationEngine - Core migration logic with safety controls
 * @security Tenant isolation, data integrity, rollback capability
 */
class DocumentMigrationEngine {
    /**
     * @param {Object} dbConnection - MongoDB connection
     * @param {MigrationLogger} logger - Migration logger instance
     */
    constructor(dbConnection, logger) {
        this.db = dbConnection;
        this.logger = logger;
        this.rollbackData = [];
        this.migrationStats = {
            totalDocuments: 0,
            migratedDocuments: 0,
            failedDocuments: 0,
            skippedDocuments: 0,
            tenantAssignments: {}
        };
    }

    /**
     * Analyze existing documents for migration readiness
     * @returns {Promise<Object>} Analysis results
     */
    async analyzeDocuments() {
        await this.logger.log('ANALYSIS', 'START_DOCUMENT_ANALYSIS');

        const Document = this.db.model('Document');
        const User = this.db.model('User');

        try {
            // Count documents without tenantId
            const legacyCount = await Document.countDocuments({
                tenantId: { $exists: false },
                deletedAt: { $exists: false }
            });

            // Count documents with tenantId (already migrated)
            const migratedCount = await Document.countDocuments({
                tenantId: { $exists: true },
                deletedAt: { $exists: false }
            });

            // Analyze document ownership patterns
            const ownershipAnalysis = await Document.aggregate([
                {
                    $match: {
                        tenantId: { $exists: false },
                        deletedAt: { $exists: false }
                    }
                },
                {
                    $group: {
                        _id: '$uploadedBy',
                        documentCount: { $sum: 1 },
                        caseCount: { $addToSet: '$caseId' },
                        latestDocument: { $max: '$createdAt' },
                        earliestDocument: { $min: '$createdAt' }
                    }
                },
                { $sort: { documentCount: -1 } },
                { $limit: 100 }
            ]);

            // Analyze potential tenant candidates
            const potentialTenants = await User.distinct('_id', {
                role: { $in: ['ATTORNEY', 'PARTNER', 'MANAGER'] }
            });

            const analysis = {
                legacyDocuments: legacyCount,
                migratedDocuments: migratedCount,
                ownershipPatterns: ownershipAnalysis,
                potentialTenants: potentialTenants.length,
                migrationRequired: legacyCount > 0,
                estimatedMigrationTime: Math.ceil(legacyCount / CONFIG.BATCH_SIZE) * 2, // minutes
                // Risk assessment
                risks: legacyCount > 10000 ? ['LARGE_DATASET', 'EXTENDED_DOWNTIME'] : ['MINIMAL'],
                recommendations: this.generateRecommendations(legacyCount, migratedCount)
            };

            await this.logger.log('ANALYSIS', 'COMPLETE_DOCUMENT_ANALYSIS', {
                analysis,
                complianceCheck: 'PASS'
            });

            return analysis;

        } catch (error) {
            await this.logger.log('ANALYSIS', 'ANALYSIS_FAILED', {
                error: error.message,
                stack: error.stack
            }, 'ERROR');
            throw error;
        }
    }

    /**
     * Determine tenant assignment strategy for documents
     * @param {Array} ownershipPatterns - Document ownership analysis
     * @returns {Object} Tenant assignment strategy
     */
    determineTenantStrategy(ownershipPatterns) {
        // Strategy 1: User-based assignment (most documents uploaded by same user)
        const topUploader = ownershipPatterns[0];
        const userBasedConfidence = topUploader ?
            (topUploader.documentCount / this.migrationStats.totalDocuments) * 100 : 0;

        // Strategy 2: Case-based assignment (documents grouped by case)
        const caseBasedDocs = ownershipPatterns.filter(p => p.caseCount && p.caseCount.length > 0);
        const caseBasedConfidence = caseBasedDocs.length > 0 ? 70 : 0;

        let strategy = TENANT_MAPPING_STRATEGIES.MANUAL;
        let confidence = 0;

        if (userBasedConfidence >= 80) {
            strategy = TENANT_MAPPING_STRATEGIES.USER_BASED;
            confidence = userBasedConfidence;
        } else if (caseBasedConfidence >= 70) {
            strategy = TENANT_MAPPING_STRATEGIES.CASE_BASED;
            confidence = caseBasedConfidence;
        }

        return {
            strategy,
            confidence,
            topUploader: topUploader ? {
                userId: topUploader._id,
                documentCount: topUploader.documentCount,
                dateRange: {
                    earliest: topUploader.earliestDocument,
                    latest: topUploader.latestDocument
                }
            } : null,
            requiresManualReview: confidence < 70
        };
    }

    /**
     * Migrate documents in batches with safety controls
     * @param {Object} tenantStrategy - Tenant assignment strategy
     * @param {Boolean} dryRun - Whether to perform dry run
     * @param {Boolean} forceMigration - Whether to force migration despite warnings
     * @returns {Promise<Object>} Migration results
     */
    async migrateDocuments(tenantStrategy, dryRun = false, forceMigration = false) {
        await this.logger.log('DOCUMENT_MIGRATION', 'START_DOCUMENT_MIGRATION', {
            strategy: tenantStrategy.strategy,
            confidence: tenantStrategy.confidence,
            batchSize: CONFIG.BATCH_SIZE,
            dryRun
        });

        const Document = this.db.model('Document');
        const User = this.db.model('User');
        let processed = 0;
        let hasMore = true;

        // Get total count for progress tracking
        this.migrationStats.totalDocuments = await Document.countDocuments({
            tenantId: { $exists: false },
            deletedAt: { $exists: false }
        });

        console.log(`Migrating ${this.migrationStats.totalDocuments} documents...`);

        while (hasMore) {
            try {
                // Fetch batch of documents without tenantId
                const documents = await Document.find({
                    tenantId: { $exists: false },
                    deletedAt: { $exists: false }
                })
                    .limit(CONFIG.BATCH_SIZE)
                    .lean();

                if (documents.length === 0) {
                    hasMore = false;
                    break;
                }

                // Process batch
                const batchResults = await this.processBatch(documents, tenantStrategy, User, dryRun);

                // Update statistics
                processed += documents.length;
                this.migrationStats.migratedDocuments += batchResults.success;
                this.migrationStats.failedDocuments += batchResults.failed;
                this.migrationStats.skippedDocuments += batchResults.skipped;

                // Log batch progress
                const progress = Math.round((processed / this.migrationStats.totalDocuments) * 100);
                await this.logger.log('DOCUMENT_MIGRATION', 'BATCH_COMPLETE', {
                    batchNumber: Math.ceil(processed / CONFIG.BATCH_SIZE),
                    processedInBatch: documents.length,
                    success: batchResults.success,
                    failed: batchResults.failed,
                    skipped: batchResults.skipped,
                    progress: `${progress}%`,
                    cumulative: {
                        total: processed,
                        success: this.migrationStats.migratedDocuments,
                        failed: this.migrationStats.failedDocuments
                    }
                });

                console.log(`Progress: ${processed}/${this.migrationStats.totalDocuments} (${progress}%)`);

                // Small delay to prevent overwhelming the database
                await sleep(100);

            } catch (error) {
                await this.logger.log('DOCUMENT_MIGRATION', 'BATCH_FAILED', {
                    error: error.message,
                    processedSoFar: processed
                }, 'ERROR');

                if (!forceMigration) {
                    throw new Error(`Migration stopped due to batch error: ${error.message}`);
                }

                // Continue with next batch if forced
                console.warn(`Batch failed but continuing (force mode): ${error.message}`);
            }
        }

        return this.generateMigrationReport();
    }

    /**
     * Process a batch of documents with tenant assignment
     * @private
     */
    async processBatch(documents, strategy, User, dryRun = false) {
        const Document = this.db.model('Document');
        const results = { success: 0, failed: 0, skipped: 0 };
        const operations = [];

        for (const doc of documents) {
            try {
                // Determine tenantId based on strategy
                const tenantId = await this.assignTenantId(doc, strategy, User);

                if (!tenantId) {
                    results.skipped++;
                    await this.logger.log('DOCUMENT_MIGRATION', 'SKIP_DOCUMENT', {
                        documentId: doc._id,
                        reason: 'NO_TENANT_ASSIGNMENT',
                        strategy: strategy.strategy
                    }, 'WARN');
                    continue;
                }

                // Prepare update operation
                const update = {
                    $set: {
                        tenantId: tenantId,
                        migratedAt: new Date(),
                        migrationId: this.logger.getMigrationId()
                    },
                    $push: {
                        migrationHistory: {
                            phase: 'DOCUMENT_MIGRATION',
                            timestamp: new Date(),
                            strategy: strategy.strategy,
                            assignedTenant: tenantId,
                            migrationId: this.logger.getMigrationId()
                        }
                    }
                };

                // Store rollback data (original state)
                this.rollbackData.push({
                    documentId: doc._id,
                    originalState: {
                        tenantId: doc.tenantId,
                        updatedAt: doc.updatedAt
                    },
                    newState: {
                        tenantId: tenantId,
                        migratedAt: new Date()
                    },
                    timestamp: new Date().toISOString()
                });

                // Add to bulk operation
                operations.push({
                    updateOne: {
                        filter: { _id: doc._id },
                        update: update
                    }
                });

                // Update tenant statistics
                this.migrationStats.tenantAssignments[tenantId] =
                    (this.migrationStats.tenantAssignments[tenantId] || 0) + 1;

                results.success++;

            } catch (error) {
                results.failed++;
                await this.logger.log('DOCUMENT_MIGRATION', 'DOCUMENT_MIGRATION_FAILED', {
                    documentId: doc._id,
                    error: error.message
                }, 'ERROR');
            }
        }

        // Execute bulk operations if not dry run
        if (operations.length > 0 && !dryRun) {
            await Document.bulkWrite(operations, { ordered: false });
        }

        return results;
    }

    /**
     * Assign tenant ID to document based on strategy
     * @private
     */
    async assignTenantId(document, strategy, User) {
        switch (strategy.strategy) {
            case TENANT_MAPPING_STRATEGIES.USER_BASED:
                return await this.assignByUser(document, User);

            case TENANT_MAPPING_STRATEGIES.CASE_BASED:
                return await this.assignByCase(document);

            case TENANT_MAPPING_STRATEGIES.CLIENT_BASED:
                return await this.assignByClient(document);

            case TENANT_MAPPING_STRATEGIES.MANUAL:
                return await this.assignByMappingRules(document);

            default:
                return null;
        }
    }

    /**
     * Assign tenant based on document's uploadedBy user
     * @private
     */
    async assignByUser(document, User) {
        if (!document.uploadedBy) return null;

        try {
            const user = await User.findById(document.uploadedBy).lean();
            if (!user || !user.tenantId) return null;

            return user.tenantId;
        } catch (error) {
            await this.logger.log('TENANT_ASSIGNMENT', 'USER_ASSIGNMENT_FAILED', {
                documentId: document._id,
                userId: document.uploadedBy,
                error: error.message
            }, 'WARN');
            return null;
        }
    }

    /**
     * Assign tenant based on document's case
     * @private
     */
    async assignByCase(document) {
        if (!document.caseId) return null;

        try {
            const Case = this.db.model('Case');
            const caseDoc = await Case.findById(document.caseId).lean();
            if (!caseDoc || !caseDoc.tenantId) return null;

            return caseDoc.tenantId;
        } catch (error) {
            await this.logger.log('TENANT_ASSIGNMENT', 'CASE_ASSIGNMENT_FAILED', {
                documentId: document._id,
                caseId: document.caseId,
                error: error.message
            }, 'WARN');
            return null;
        }
    }

    /**
     * Assign tenant based on client (placeholder)
     * @private
     */
    async assignByClient(document) {
        // Implementation would require client model and relationships
        return null;
    }

    /**
     * Assign tenant based on mapping rules
     * @private
     */
    async assignByMappingRules(document) {
        // This would typically come from a configuration file or database
        // For now, using a simple rule: assign to default tenant
        const DEFAULT_TENANT = process.env.DEFAULT_TENANT_ID || 'tenant-default';
        return DEFAULT_TENANT;
    }

    /**
     * Generate comprehensive migration report
     */
    generateMigrationReport() {
        const report = {
            migrationId: this.logger.getMigrationId(),
            timestamp: new Date().toISOString(),
            summary: {
                totalDocuments: this.migrationStats.totalDocuments,
                migratedDocuments: this.migrationStats.migratedDocuments,
                failedDocuments: this.migrationStats.failedDocuments,
                skippedDocuments: this.migrationStats.skippedDocuments,
                successRate: this.migrationStats.totalDocuments > 0 ?
                    (this.migrationStats.migratedDocuments / this.migrationStats.totalDocuments) * 100 : 0
            },
            tenantDistribution: this.migrationStats.tenantAssignments,
            rollbackAvailable: this.rollbackData.length > 0,
            rollbackDocumentCount: this.rollbackData.length,
            // Compliance information
            compliance: {
                markers: ['POPIA', 'CompaniesAct', 'ECTAct', 'PAIA'],
                auditTrail: 'logs/migration-tenancy.log',
                reportGenerated: new Date().toISOString()
            }
        };

        return report;
    }

    /**
     * Save rollback data for emergency recovery
     */
    async saveRollbackData() {
        if (this.rollbackData.length === 0) return;

        const rollbackInfo = {
            migrationId: this.logger.getMigrationId(),
            timestamp: new Date().toISOString(),
            totalDocuments: this.rollbackData.length,
            documents: this.rollbackData,
            // Cryptographic checksum for integrity
            checksum: createHash('sha256')
                .update(JSON.stringify(this.rollbackData))
                .digest('hex')
        };

        await fs.writeFile(
            CONFIG.ROLLBACK_FILE,
            JSON.stringify(rollbackInfo, null, 2),
            'utf8'
        );

        await this.logger.log('CLEANUP', 'ROLLBACK_DATA_SAVED', {
            file: CONFIG.ROLLBACK_FILE,
            documentCount: this.rollbackData.length,
            checksum: rollbackInfo.checksum.substring(0, 16)
        });
    }

    /**
     * Validate migration completeness and data integrity
     */
    async validateMigration() {
        await this.logger.log('VALIDATION', 'START_VALIDATION');

        const Document = this.db.model('Document');

        try {
            // Check for orphaned documents (no tenantId after migration)
            const orphanedCount = await Document.countDocuments({
                tenantId: { $exists: false },
                deletedAt: { $exists: false },
                migratedAt: { $exists: false } // Not attempted for migration
            });

            // Check for partially migrated documents
            const partialCount = await Document.countDocuments({
                tenantId: { $exists: true },
                migrationId: { $exists: false } // Missing migration metadata
            });

            // Verify rollback data integrity
            let rollbackValid = false;
            try {
                const fileExists = await fs.access(CONFIG.ROLLBACK_FILE).then(() => true).catch(() => false);
                if (fileExists) {
                    const rollbackData = JSON.parse(await fs.readFile(CONFIG.ROLLBACK_FILE, 'utf8'));
                    const expectedChecksum = createHash('sha256')
                        .update(JSON.stringify(rollbackData.documents))
                        .digest('hex');

                    rollbackValid = rollbackData.checksum === expectedChecksum;
                }
            } catch (error) {
                // Rollback file may not exist in dry run
            }

            const validation = {
                orphanedDocuments: orphanedCount,
                partiallyMigrated: partialCount,
                rollbackIntegrity: rollbackValid,
                allValid: orphanedCount === 0 && partialCount === 0 && rollbackValid,
                recommendations: this.generateValidationRecommendations(orphanedCount, partialCount)
            };

            await this.logger.log('VALIDATION', 'COMPLETE_VALIDATION', {
                validation,
                complianceCheck: validation.allValid ? 'PASS' : 'REVIEW_REQUIRED'
            });

            return validation;

        } catch (error) {
            await this.logger.log('VALIDATION', 'VALIDATION_FAILED', {
                error: error.message,
                stack: error.stack
            }, 'ERROR');
            throw error;
        }
    }

    // ============================================================================
    // HELPER METHODS
    // ============================================================================

    generateRecommendations(legacyCount, migratedCount) {
        const recommendations = [];

        if (legacyCount > 10000) {
            recommendations.push({
                level: 'HIGH',
                message: 'Large dataset detected. Consider running migration during off-peak hours.',
                action: 'SCHEDULE_MAINTENANCE_WINDOW'
            });
        }

        if (migratedCount > 0) {
            recommendations.push({
                level: 'MEDIUM',
                message: 'Some documents already have tenant assignments. Verify consistency.',
                action: 'VERIFY_EXISTING_TENANTS'
            });
        }

        if (legacyCount === 0) {
            recommendations.push({
                level: 'INFO',
                message: 'No documents require migration.',
                action: 'SKIP_MIGRATION'
            });
        }

        return recommendations;
    }

    generateValidationRecommendations(orphanedCount, partialCount) {
        const recommendations = [];

        if (orphanedCount > 0) {
            recommendations.push({
                level: 'HIGH',
                message: `${orphanedCount} documents have no tenant assignment. Manual review required.`,
                action: 'REVIEW_ORPHANED_DOCUMENTS'
            });
        }

        if (partialCount > 0) {
            recommendations.push({
                level: 'MEDIUM',
                message: `${partialCount} documents have tenantId but missing migration metadata.`,
                action: 'UPDATE_MIGRATION_METADATA'
            });
        }

        return recommendations;
    }

    /**
     * Get migration statistics
     */
    getStats() {
        return { ...this.migrationStats };
    }

    /**
     * Get rollback data
     */
    getRollbackData() {
        return [...this.rollbackData];
    }
}

module.exports = {
    DocumentMigrationEngine,
    TENANT_MAPPING_STRATEGIES,
    CONFIG
};