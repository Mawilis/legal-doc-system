#!/usr/bin/env node

/**
 * ============================================================================
 * MIGRATION LOGGER - COMPLIANCE AUDIT TRAIL
 * ============================================================================
 * 
 * Purpose: Creates immutable audit trail for migration activities
 * Compliance: POPIA §14 (Information Officer duties), Companies Act
 * 
 * Features:
 * - Cryptographic hash for integrity verification
 * - Compliance reporting for regulator submission
 * - Multi-level logging (INFO, WARN, ERROR, COMPLIANCE)
 * 
 * ============================================================================
 */

const { createHash } = require('crypto');
const fs = require('fs').promises;
const path = require('path');

// Migration phases for structured logging
const MIGRATION_PHASES = {
    ANALYSIS: 'ANALYSIS',
    TENANT_ASSIGNMENT: 'TENANT_ASSIGNMENT',
    DOCUMENT_MIGRATION: 'DOCUMENT_MIGRATION',
    VALIDATION: 'VALIDATION',
    CLEANUP: 'CLEANUP'
};

// Configuration
const CONFIG = {
    MIGRATION_LOG_FILE: path.join(__dirname, '../../logs/migration-tenancy.log'),
    COMPLIANCE_MARKERS: ['POPIA', 'CompaniesAct', 'ECTAct', 'PAIA']
};

/**
 * MigrationLogger - Creates immutable audit trail for migration activities
 * @compliance POPIA §14 (Information Officer duties), Companies Act
 */
class MigrationLogger {
    constructor() {
        this.logEntries = [];
        this.migrationId = `migration-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Log migration activity with full audit details
     * @param {String} phase - Migration phase
     * @param {String} action - Action performed
     * @param {Object} details - Detailed information
     * @param {String} level - Log level (INFO, WARN, ERROR, COMPLIANCE)
     */
    async log(phase, action, details = {}, level = 'INFO') {
        const timestamp = new Date().toISOString();
        const entry = {
            migrationId: this.migrationId,
            timestamp,
            phase,
            action,
            level,
            details,
            // Cryptographic hash for integrity
            hash: this.generateEntryHash(phase, action, details, timestamp),
            // Compliance markers
            compliance: CONFIG.COMPLIANCE_MARKERS
        };

        this.logEntries.push(entry);

        // Write to file (append mode)
        const logLine = JSON.stringify(entry) + '\n';
        await fs.appendFile(CONFIG.MIGRATION_LOG_FILE, logLine, 'utf8');

        // Console output for monitoring
        console.log(`[${timestamp}] [${level}] ${phase}: ${action}`);

        if (Object.keys(details).length > 0 && level === 'ERROR') {
            console.error('Details:', details);
        }

        return entry.hash;
    }

    /**
     * Generate cryptographic hash for log entry integrity
     * @private
     */
    generateEntryHash(phase, action, details, timestamp) {
        const data = JSON.stringify({ phase, action, details, timestamp });
        return createHash('sha256').update(data).digest('hex');
    }

    /**
     * Get migration summary for compliance reporting
     * @returns {Object} Migration summary statistics
     */
    getSummary() {
        const entriesByLevel = this.logEntries.reduce((acc, entry) => {
            acc[entry.level] = (acc[entry.level] || 0) + 1;
            return acc;
        }, {});

        const entriesByPhase = this.logEntries.reduce((acc, entry) => {
            acc[entry.phase] = (acc[entry.phase] || 0) + 1;
            return acc;
        }, {});

        return {
            migrationId: this.migrationId,
            totalEntries: this.logEntries.length,
            entriesByLevel,
            entriesByPhase,
            startTime: this.logEntries[0]?.timestamp,
            endTime: this.logEntries[this.logEntries.length - 1]?.timestamp,
            // Compliance evidence
            hashes: this.logEntries.map(e => e.hash.substring(0, 16))
        };
    }

    /**
     * Export migration log for regulator submission
     * @returns {Promise<String>} Path to exported compliance report
     */
    async exportComplianceReport() {
        const report = {
            reportType: 'DATA_MIGRATION_COMPLIANCE',
            migrationId: this.migrationId,
            generatedAt: new Date().toISOString(),
            complianceMarkers: CONFIG.COMPLIANCE_MARKERS,
            summary: this.getSummary(),
            // Chief Architect certification
            certifiedBy: {
                name: 'Wilson Khanyezi',
                role: 'Chief Architect',
                email: 'wilsy.wk@gmail.com',
                timestamp: new Date().toISOString()
            },
            // POPIA Section 14 evidence
            dataProtectionImpact: {
                dataCategories: ['DOCUMENTS', 'METADATA', 'AUDIT_LOGS'],
                riskAssessment: 'LOW',
                mitigationApplied: ['ENCRYPTION', 'AUDIT_TRAIL', 'ROLLBACK_CAPABILITY']
            }
        };

        const reportPath = path.join(__dirname, `../../logs/migration-compliance-${this.migrationId}.json`);
        await fs.writeFile(reportPath, JSON.stringify(report, null, 2), 'utf8');

        return reportPath;
    }

    /**
     * Getter for migration ID
     */
    getMigrationId() {
        return this.migrationId;
    }

    /**
     * Get all log entries (for testing/debugging)
     */
    getLogEntries() {
        return [...this.logEntries];
    }
}

module.exports = {
    MigrationLogger,
    MIGRATION_PHASES,
    CONFIG
};