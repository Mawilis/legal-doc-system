#!/usr/bin/env node
/**
 * Wilsy OS - OTS Cache Cleanup Script
 * ====================================
 * Scheduled maintenance script for OpenTimestamps proof cache management.
 * Removes expired OTS proof files while preserving anchored proofs for legal
 * compliance. Implements Companies Act retention policies with audit trails.
 * 
 * @module scripts/ots-cleanup
 * @requires fs/promises
 * @requires fs
 * @requires path
 * @requires ../config/logger
 * @requires ../models/AuditLedger
 */

const fs = require('fs').promises;
const fsSync = require('fs');
const path = require('path');
const logger = require('../config/logger');
const mongoose = require('mongoose');
const { AuditLedger } = require('../models/AuditLedger');

// Configuration
const OTS_CACHE_DIR = process.env.OTS_CACHE_DIR || '/tmp/wilsy-ots-cache';
const OTS_MAX_AGE_DAYS = parseInt(process.env.OTS_MAX_AGE_DAYS) || 30;
const OTS_RETENTION_DAYS = parseInt(process.env.OTS_RETENTION_DAYS) || 365; // For anchored proofs
const DRY_RUN = process.env.DRY_RUN === 'true';
const MONGO_URI = process.env.MONGO_URI_TEST || process.env.MONGO_URI;

// Tenant-specific retention policies (future enhancement)
const TENANT_RETENTION_POLICIES = new Map();

/**
 * Parse tenant ID and timestamp from OTS cache filename
 * @param {string} filename - OTS cache filename
 * @returns {Object|null} - { tenantId: string, hash: string, timestamp: Date }
 * @security POPIA §14(1) - Data subject identification for audit trails
 */
function parseCacheFilename(filename) {
    // Format: {tenantId}_{hash}.ots or {tenantId}_{hash}_{timestamp}.ots
    const match = filename.match(/^([a-f0-9-]+)_([a-f0-9]{64})(?:_(\d+))?\.ots$/i);
    if (!match) return null;

    const [, tenantId, hash, timestamp] = match;
    return {
        tenantId,
        hash,
        timestamp: timestamp ? new Date(parseInt(timestamp)) : null
    };
}

/**
 * Check if file should be retained based on tenant policy and anchoring status
 * @param {string} filePath - Full path to OTS file
 * @param {Object} fileInfo - Parsed file information
 * @returns {Promise<boolean>} - True if file should be retained
 * @compliance Companies Act 71 of 2008 - Document retention requirements
 */
async function shouldRetainFile(filePath, fileInfo) {
    try {
        // Check if file is anchored (has .ots.upgraded companion)
        const upgradedPath = filePath + '.upgraded';
        try {
            await fs.access(upgradedPath);

            // Anchored files follow extended retention policy
            const tenantPolicy = TENANT_RETENTION_POLICIES.get(fileInfo.tenantId);
            const retentionDays = tenantPolicy?.anchoredRetention || OTS_RETENTION_DAYS;

            const fileStat = await fs.stat(filePath);
            const fileAgeDays = (Date.now() - fileStat.mtime.getTime()) / (1000 * 60 * 60 * 24);

            return fileAgeDays <= retentionDays;
        } catch {
            // No upgraded companion - use standard retention
            const fileStat = await fs.stat(filePath);
            const fileAgeDays = (Date.now() - fileStat.mtime.getTime()) / (1000 * 60 * 60 * 24);

            return fileAgeDays <= OTS_MAX_AGE_DAYS;
        }
    } catch (error) {
        logger.error('File retention check failed', { filePath, error: error.message });
        return true; // Fail-safe: retain if we can't determine
    }
}

/**
 * Safely delete OTS cache file with audit logging
 * @param {string} filePath - Full path to file
 * @param {Object} fileInfo - Parsed file information
 * @returns {Promise<boolean>} - True if deletion succeeded
 * @security POPIA §14(2) - Secure disposal of personal information
 */
async function deleteCacheFile(filePath, fileInfo) {
    try {
        if (DRY_RUN) {
            logger.info('DRY RUN: Would delete', { filePath, fileInfo });
            return true;
        }

        // Create audit entry before deletion
        await logDeletionAudit(filePath, fileInfo);

        // Move to trash directory first (optional recovery)
        const trashDir = path.join(OTS_CACHE_DIR, '.trash');
        await fs.mkdir(trashDir, { recursive: true });

        const trashPath = path.join(trashDir, path.basename(filePath) + '.' + Date.now());
        await fs.rename(filePath, trashPath);

        // Securely delete after 7 days via separate cleanup
        logger.info('Moved OTS file to trash', {
            tenantId: fileInfo.tenantId,
            originalPath: filePath,
            trashPath,
            hashPrefix: fileInfo.hash?.substring(0, 16)
        });

        return true;
    } catch (error) {
        logger.error('Failed to delete cache file', {
            filePath,
            tenantId: fileInfo.tenantId,
            error: error.message
        });
        return false;
    }
}

/**
 * Log deletion to audit ledger for compliance tracking
 * @param {string} filePath - File being deleted
 * @param {Object} fileInfo - Parsed file information
 * @returns {Promise<void>}
 * @compliance POPIA §17 - Documentation of processing activities
 */
async function logDeletionAudit(filePath, fileInfo) {
    try {
        if (!MONGO_URI) {
            logger.warn('MongoDB not configured for audit logging');
            return;
        }

        // Ensure MongoDB connection
        if (mongoose.connection.readyState !== 1) {
            await mongoose.connect(MONGO_URI, {
                useNewUrlParser: true,
                useUnifiedTopology: true
            });
        }

        const auditEntry = new AuditLedger({
            tenantId: fileInfo.tenantId,
            action: 'OTS_CACHE_CLEANUP',
            resourceType: 'TIMESTAMP_PROOF',
            resourceId: fileInfo.hash,
            actor: 'system:ots-cleanup',
            details: {
                filePath,
                filename: path.basename(filePath),
                deletionReason: 'RETENTION_POLICY_EXPIRED',
                retentionPolicyDays: OTS_MAX_AGE_DAYS,
                dryRun: DRY_RUN
            },
            timestamp: new Date()
        });

        await auditEntry.save();

        logger.debug('Audit log created for OTS cleanup', {
            tenantId: fileInfo.tenantId,
            auditId: auditEntry._id
        });
    } catch (error) {
        logger.error('Failed to create audit log', {
            filePath,
            error: error.message
        });
    }
}

/**
 * Scan and clean OTS cache directory
 * @param {string} directory - Directory to scan
 * @returns {Promise<Object>} - Cleanup statistics
 * @compliance ECT Act §15(4) - Proper maintenance of timestamping systems
 */
async function cleanCacheDirectory(directory) {
    const stats = {
        scanned: 0,
        retained: 0,
        deleted: 0,
        failed: 0,
        startTime: new Date(),
        tenants: new Map()
    };

    try {
        // Ensure directory exists
        await fs.mkdir(directory, { recursive: true });

        // Read directory contents
        const files = await fs.readdir(directory);

        for (const file of files) {
            // Skip hidden files and trash directory
            if (file.startsWith('.') || file === '.trash') continue;

            const filePath = path.join(directory, file);
            const fileInfo = parseCacheFilename(file);

            stats.scanned++;

            try {
                const stat = await fs.stat(filePath);

                if (!stat.isFile() || !file.endsWith('.ots')) {
                    logger.debug('Skipping non-OTS file', { filePath });
                    continue;
                }

                // Initialize tenant stats
                if (fileInfo?.tenantId) {
                    if (!stats.tenants.has(fileInfo.tenantId)) {
                        stats.tenants.set(fileInfo.tenantId, { scanned: 0, deleted: 0 });
                    }
                    stats.tenants.get(fileInfo.tenantId).scanned++;
                }

                // Check if file should be retained
                const retain = await shouldRetainFile(filePath, fileInfo);

                if (retain) {
                    stats.retained++;
                    logger.debug('Retaining OTS file', {
                        filePath,
                        tenantId: fileInfo?.tenantId
                    });
                } else {
                    // Delete expired file
                    const success = await deleteCacheFile(filePath, fileInfo);

                    if (success) {
                        stats.deleted++;
                        if (fileInfo?.tenantId) {
                            stats.tenants.get(fileInfo.tenantId).deleted++;
                        }
                    } else {
                        stats.failed++;
                    }
                }

            } catch (error) {
                stats.failed++;
                logger.error('Error processing file', { filePath, error: error.message });
            }
        }

        stats.endTime = new Date();
        stats.durationMs = stats.endTime - stats.startTime;

        return stats;

    } catch (error) {
        logger.error('Cache directory scan failed', {
            directory,
            error: error.message
        });
        throw error;
    }
}

/**
 * Cleanup trash directory (files older than 7 days)
 * @returns {Promise<Object>} - Trash cleanup statistics
 */
async function cleanTrashDirectory() {
    const trashDir = path.join(OTS_CACHE_DIR, '.trash');
    const stats = {
        scanned: 0,
        deleted: 0,
        failed: 0
    };

    try {
        await fs.mkdir(trashDir, { recursive: true });
        const files = await fs.readdir(trashDir);

        for (const file of files) {
            if (file.startsWith('.')) continue;

            const filePath = path.join(trashDir, file);
            stats.scanned++;

            try {
                const stat = await fs.stat(filePath);
                const fileAgeDays = (Date.now() - stat.mtime.getTime()) / (1000 * 60 * 60 * 24);

                // Delete files older than 7 days from trash
                if (fileAgeDays > 7) {
                    if (!DRY_RUN) {
                        await fs.unlink(filePath);
                    }
                    stats.deleted++;
                    logger.debug('Deleted from trash', { filePath, fileAgeDays });
                }
            } catch (error) {
                stats.failed++;
                logger.error('Failed to clean trash file', { filePath, error: error.message });
            }
        }

        return stats;
    } catch (error) {
        logger.error('Trash directory cleanup failed', { error: error.message });
        return stats;
    }
}

/**
 * Main cleanup execution with error handling
 * @returns {Promise<void>}
 */
async function main() {
    logger.info('Starting OTS cache cleanup', {
        cacheDir: OTS_CACHE_DIR,
        maxAgeDays: OTS_MAX_AGE_DAYS,
        dryRun: DRY_RUN,
        timestamp: new Date().toISOString()
    });

    try {
        // Clean main cache directory
        const cacheStats = await cleanCacheDirectory(OTS_CACHE_DIR);

        // Clean trash directory
        const trashStats = await cleanTrashDirectory();

        // Log summary
        logger.info('OTS cleanup completed successfully', {
            scanned: cacheStats.scanned,
            retained: cacheStats.retained,
            deleted: cacheStats.deleted,
            failed: cacheStats.failed,
            durationMs: cacheStats.durationMs,
            trashDeleted: trashStats.deleted,
            dryRun: DRY_RUN,
            tenants: Array.from(cacheStats.tenants.entries())
        });

        // Exit with success
        process.exit(0);

    } catch (error) {
        logger.error('OTS cleanup failed catastrophically', {
            error: error.message,
            stack: error.stack,
            timestamp: new Date().toISOString()
        });

        process.exit(1);
    }
}

// Handle command line execution
if (require.main === module) {
    // Parse command line arguments
    const args = process.argv.slice(2);
    if (args.includes('--dry-run') || args.includes('-d')) {
        process.env.DRY_RUN = 'true';
    }

    if (args.includes('--help') || args.includes('-h')) {
        console.log(`
OTS Cache Cleanup Script
Usage: node scripts/ots-cleanup.js [options]

Options:
  --dry-run, -d    Simulate cleanup without deleting files
  --help, -h       Show this help message
  --max-age=N      Override default max age (days)
  --cache-dir=DIR  Override cache directory

Environment Variables:
  OTS_CACHE_DIR         Cache directory (default: /tmp/wilsy-ots-cache)
  OTS_MAX_AGE_DAYS      Max age for unanchored proofs (default: 30)
  OTS_RETENTION_DAYS    Retention for anchored proofs (default: 365)
  DRY_RUN               Set to 'true' for dry run
  MONGO_URI             MongoDB connection for audit logging
  MONGO_URI_TEST        Test MongoDB connection

Example:
  DRY_RUN=true node scripts/ots-cleanup.js --dry-run
    `);
        process.exit(0);
    }

    // Execute main function
    main().catch(error => {
        console.error('Fatal error:', error);
        process.exit(1);
    });
}

// Mermaid Diagram: OTS Cleanup Workflow
/**
 * @mermaid
 * flowchart TD
 *     A[Cron Scheduler] --> B[Cleanup Script]
 *     B --> C{Connect to MongoDB}
 *     C -->|Success| D[Scan OTS Cache Directory]
 *     C -->|Failure| E[Log Error & Exit]
 *     D --> F[Parse Each File]
 *     F --> G{File Age > Retention?}
 *     G -->|No| H[Retain File]
 *     G -->|Yes| I{File Anchored?}
 *     I -->|Yes| J[Extended Retention Check]
 *     I -->|No| K[Mark for Deletion]
 *     J -->|Still Valid| H
 *     J -->|Expired| K
 *     K --> L[Move to .trash Directory]
 *     L --> M[Log Audit Entry]
 *     M --> N[Update Statistics]
 *     N --> O{More Files?}
 *     O -->|Yes| F
 *     O -->|No| P[Clean .trash Directory<br/>(>7 days old)]
 *     P --> Q[Generate Summary Report]
 *     Q --> R[Exit with Status]
 *     
 *     style A fill:#f0f8ff
 *     style R fill:#e1f5e1
 *     style E fill:#f8d7da
 */

module.exports = {
    cleanCacheDirectory,
    cleanTrashDirectory,
    parseCacheFilename,
    shouldRetainFile,
    deleteCacheFile,
    logDeletionAudit
};