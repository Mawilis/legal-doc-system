/**
 * ============================================================================
 * QUANTUM AUDIT NEXUS: IMMUTABLE LEGAL CHRONICLE FORGER
 * ============================================================================
 * 
 * ░█▀▀░█▀█░█▀█░█░█░█▀▀░░░█▀▀░█░█░█▀█░█░░░▀█▀░█▀▀
 * ░▀▀█░█▀▀░█▀█░█▄█░█▀▀░░░█░░░█░█░█▀█░█░░░░█░░▀▀█
 * ░▀▀▀░▀░░░▀░▀░▀░▀░▀▀▀░░░▀▀▀░▀▀▀░▀░▀░▀▀▀░▀▀▀░▀▀▀
 * 
 *  █████╗ ██╗   ██╗██████╗ ██╗████████╗
 * ██╔══██╗██║   ██║██╔══██╗██║╚══██╔══╝
 * ███████║██║   ██║██║  ██║██║   ██║   
 * ██╔══██║██║   ██║██║  ██║██║   ██║   
 * ██║  ██║╚██████╔╝██████╔╝██║   ██║   
 * ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝   ╚═╝   
 * 
 * FILE: /server/utils/auditUtils.js
 * QUANTUM MANDATE: Forge unbreakable audit trails for legal compliance orchestration
 * CREATION DATE: 2024
 * LAST QUANTUM UPDATE: 2024
 * SUPREME ARCHITECT: Wilson Khanyezi
 * COLLABORATION QUANTA: Extension-ready for blockchain ledger integration
 * 
 * ============================================================================
 * COSMIC ESSENCE: This quantum nexus transmutes legal operations into immutable
 * audit quanta—eternal proof chains that withstand judicial scrutiny across
 * all African jurisdictions. Each audit entry is a time-stamped, cryptographically
 * sealed quantum in the continuum of legal truth, propelling Wilsy OS to
 * unassailable compliance dominance across the continent.
 * ============================================================================
 */

// ============================================================================
// QUANTUM IMPORTS: Secure, Pinned Dependencies
// ============================================================================
const crypto = require('crypto');
const fs = require('fs').promises;
const path = require('path');
const { v4: uuidv4 } = require('uuid');
const zlib = require('zlib');
const { promisify } = require('util');

// Environment Configuration (Quantum Shield: Never hardcode)
require('dotenv').config({ path: path.join(__dirname, '..', '.env') });

// Quantum Sentinel: Validate critical environment variables
const validateEnvironment = () => {
    const requiredEnvVars = ['AUDIT_ENCRYPTION_KEY', 'AUDIT_SALT'];
    const missingVars = requiredEnvVars.filter(varName => !process.env[varName]);

    if (missingVars.length > 0) {
        throw new Error(`QUANTUM BREACH: Missing environment variables: ${missingVars.join(', ')}`);
    }

    // Validate encryption key length
    if (process.env.AUDIT_ENCRYPTION_KEY && process.env.AUDIT_ENCRYPTION_KEY.length < 32) {
        throw new Error('QUANTUM BREACH: AUDIT_ENCRYPTION_KEY must be at least 32 characters');
    }
};
validateEnvironment();

// Optional: Redis for distributed audit caching (Future Quantum Expansion)
let redisClient = null;
if (process.env.REDIS_URL) {
    try {
        const Redis = require('ioredis');
        redisClient = new Redis(process.env.REDIS_URL, {
            maxRetriesPerRequest: 3,
            retryStrategy: (times) => Math.min(times * 50, 2000),
            enableOfflineQueue: false,
            connectTimeout: 10000
        });

        redisClient.on('error', (error) => {
            console.error('❌ Quantum Audit Redis connection error:', error.message);
            redisClient = null;
        });

        redisClient.on('connect', () => {
            console.log('🔗 Quantum Audit connected to Redis cache layer');
        });
    } catch (error) {
        console.warn('⚠️ Redis not available for audit caching:', error.message);
    }
}

// ============================================================================
// QUANTUM CONSTANTS: Immutable Configuration
// ============================================================================
const AUDIT_CONFIG = Object.freeze({
    // Storage Paths (Env Addition: Customize AUDIT_BASE_PATH if needed)
    BASE_PATH: process.env.AUDIT_BASE_PATH || path.join(__dirname, '..', 'audit_logs'),

    // Retention Periods (Compliance Quantum: Aligned with legal statutes)
    RETENTION_PERIODS: Object.freeze({
        POPIA: 365 * 5, // 5 years for personal information processing
        COMPANIES_ACT: 365 * 7, // 7 years for company records
        FICA: 365 * 5, // 5 years for financial transactions
        GDPR: 365 * 6, // 6 years for processing activities
        DEFAULT: 365 * 5 // Default 5-year retention
    }),

    // Encryption Settings (Quantum Security Citadel)
    ENCRYPTION: Object.freeze({
        ALGORITHM: 'aes-256-gcm',
        KEY_LENGTH: 32,
        IV_LENGTH: 16,
        SALT: process.env.AUDIT_SALT,
        ITERATIONS: 100000,
        DIGEST: 'sha512'
    }),

    // Audit Categories (Legal Compliance Omniscience)
    CATEGORIES: Object.freeze({
        USER_ACCESS: 'user_access',
        DATA_PROCESSING: 'data_processing',
        DOCUMENT_OPERATION: 'document_operation',
        CONSENT_MANAGEMENT: 'consent_management',
        SECURITY_INCIDENT: 'security_incident',
        COMPLIANCE_EVENT: 'compliance_event',
        SYSTEM_OPERATION: 'system_operation',
        LEGAL_FILING: 'legal_filing',
        PAYMENT_PROCESSING: 'payment_processing',
        API_CALL: 'api_call'
    }),

    // SA Legal Jurisdiction Codes
    JURISDICTIONS: Object.freeze({
        ZA: 'ZA', // South Africa
        NG: 'NG', // Nigeria
        KE: 'KE', // Kenya
        GH: 'GH', // Ghana
        BW: 'BW', // Botswana
        EU: 'EU', // European Union
        GLOBAL: 'GLOBAL'
    }),

    // Security Settings
    SECURITY: Object.freeze({
        MAX_AUDIT_SIZE_BYTES: 1024 * 1024 * 100, // 100MB per audit file
        MAX_BATCH_SIZE: 1000,
        COMPRESSION_THRESHOLD: 1024 // Compress entries larger than 1KB
    })
});

// ============================================================================
// QUANTUM CORE: AuditLogger Class (Immutable Chronicle Forger)
// ============================================================================
class QuantumAuditLogger {
    constructor() {
        this.chainHash = null; // For blockchain-like chaining (Horizon Expansion)
        this.compressionEnabled = process.env.AUDIT_COMPRESSION === 'true';
        this.lastFlushTime = Date.now();
        this.batchQueue = [];
        this.batchSize = Math.min(
            parseInt(process.env.AUDIT_BATCH_SIZE) || 100,
            AUDIT_CONFIG.SECURITY.MAX_BATCH_SIZE
        );
        this.batchInterval = Math.max(
            parseInt(process.env.AUDIT_BATCH_INTERVAL) || 5000,
            1000
        );

        this._initialized = false;
        this._initializationPromise = this.initializeAuditDirectory();

        // Start batch processor if enabled
        if (process.env.AUDIT_BATCH_PROCESSING === 'true') {
            this._batchProcessor = setInterval(() => this._processBatch(), this.batchInterval);
            this._batchProcessor.unref(); // Don't keep process alive
        }
    }

    /**
     * QUANTUM INIT: Create secure audit directory structure
     * Security Quantum: Directory permissions set to 700 (owner only)
     */
    async initializeAuditDirectory() {
        if (this._initialized) return;

        try {
            await fs.mkdir(AUDIT_CONFIG.BASE_PATH, { recursive: true, mode: 0o700 });

            // Create subdirectories for categorized audits
            const categoryPromises = Object.values(AUDIT_CONFIG.CATEGORIES).map(async (category) => {
                const categoryPath = path.join(AUDIT_CONFIG.BASE_PATH, category);
                await fs.mkdir(categoryPath, { recursive: true, mode: 0o700 });
                return categoryPath;
            });

            await Promise.all(categoryPromises);

            // Create today's dated directory
            const today = new Date().toISOString().split('T')[0];
            const datedPath = path.join(AUDIT_CONFIG.BASE_PATH, 'daily', today);
            await fs.mkdir(datedPath, { recursive: true, mode: 0o700 });

            this._initialized = true;
            console.log(`✅ Quantum Audit directory initialized at: ${AUDIT_CONFIG.BASE_PATH}`);
        } catch (error) {
            console.error('❌ Quantum Audit directory initialization failed:', error);
            throw new Error(`Audit directory creation failed: ${error.message}`);
        }
    }

    /**
     * NEXUS CORE: Create Immutable Audit Entry
     * @param {Object} auditData - The audit payload
     * @returns {Promise<Object>} - Encrypted audit entry with proof chain
     * 
     * Compliance Quantum: POPIA Section 14 - Accountability for processing
     * Security Quantum: STRIDE Threat Model - Tampering protection
     */
    async createAuditEntry(auditData) {
        // Ensure initialization is complete
        if (!this._initialized) {
            await this._initializationPromise;
        }

        const auditId = uuidv4();
        const timestamp = new Date().toISOString();

        // Quantum Validation: Ensure required fields (POPIA Compliance)
        const requiredFields = ['userId', 'action', 'entityType'];
        const missingFields = requiredFields.filter(field => !auditData[field]);

        if (missingFields.length > 0) {
            throw new Error(`QUANTUM BREACH: Missing required audit fields: ${missingFields.join(', ')}`);
        }

        // Validate audit data size
        const auditDataSize = Buffer.byteLength(JSON.stringify(auditData), 'utf8');
        if (auditDataSize > AUDIT_CONFIG.SECURITY.COMPRESSION_THRESHOLD) {
            console.warn(`⚠️ Large audit entry detected: ${auditDataSize} bytes`);
        }

        // Construct quantum audit object
        const auditEntry = {
            // Metadata
            auditId,
            timestamp,
            jurisdiction: auditData.jurisdiction || AUDIT_CONFIG.JURISDICTIONS.ZA,
            legalBasis: auditData.legalBasis || 'POPIA_8(1)',

            // Core Data (Compliance Quantum)
            userId: String(auditData.userId),
            userRole: String(auditData.userRole || 'unknown'),
            userIp: this._sanitizeIp(auditData.userIp),
            userAgent: String(auditData.userAgent || 'Unknown').substring(0, 500),

            // Action Data
            action: String(auditData.action),
            actionType: String(auditData.actionType || 'system'),
            entityType: String(auditData.entityType),
            entityId: auditData.entityId ? String(auditData.entityId) : null,
            resource: String(auditData.resource || 'unknown'),

            // Changes/Details
            beforeState: this._sanitizeData(auditData.beforeState),
            afterState: this._sanitizeData(auditData.afterState),
            changes: this._sanitizeData(auditData.changes),
            metadata: this._sanitizeData(auditData.metadata),

            // Security Chain
            sessionId: auditData.sessionId ? String(auditData.sessionId) : null,
            requestId: auditData.requestId ? String(auditData.requestId) : null,
            correlationId: auditData.correlationId ? String(auditData.correlationId) : uuidv4(),

            // Compliance Tags
            complianceTags: {
                popia: Boolean(auditData.complianceTags?.popia),
                paia: Boolean(auditData.complianceTags?.paia),
                fica: Boolean(auditData.complianceTags?.fica),
                gdpr: Boolean(auditData.complianceTags?.gdpr),
                ectAct: Boolean(auditData.complianceTags?.ectAct)
            },

            // Integrity Proofs
            hashChain: {
                previousHash: this.chainHash,
                currentHash: null, // Will be set after encryption
                merkleRoot: null
            },

            // Retention Schedule
            retention: {
                category: auditData.retentionCategory || AUDIT_CONFIG.CATEGORIES.SYSTEM_OPERATION,
                periodDays: auditData.retentionPeriod || AUDIT_CONFIG.RETENTION_PERIODS.DEFAULT,
                expiryDate: this._calculateExpiryDate(
                    auditData.retentionPeriod || AUDIT_CONFIG.RETENTION_PERIODS.DEFAULT
                )
            }
        };

        try {
            // Quantum Shield: Encrypt sensitive data before storage
            const encryptedEntry = await this._encryptAuditEntry(auditEntry);

            // Generate cryptographic hash for chain integrity
            auditEntry.hashChain.currentHash = this._generateHash(JSON.stringify(encryptedEntry));
            this.chainHash = auditEntry.hashChain.currentHash;

            // Store the audit entry
            await this._persistAuditEntry(auditEntry, encryptedEntry);

            // Optional: Cache for fast retrieval
            if (redisClient) {
                await this._cacheAuditEntry(auditId, auditEntry);
            }

            // Batch processing if enabled
            if (process.env.AUDIT_BATCH_PROCESSING === 'true') {
                this.batchQueue.push({ auditId, timestamp, category: auditEntry.retention.category });
                if (this.batchQueue.length >= this.batchSize) {
                    await this._flushBatch();
                }
            }

            return {
                success: true,
                auditId,
                timestamp,
                proofHash: auditEntry.hashChain.currentHash,
                message: 'Quantum audit entry created with immutable proof chain'
            };
        } catch (error) {
            console.error('❌ Audit entry creation failed:', error);

            // Emergency fallback storage
            await this._emergencyStorage({
                auditId,
                timestamp,
                userId: auditData.userId,
                action: auditData.action,
                error: error.message
            });

            throw new Error(`Audit creation failed: ${error.message}`);
        }
    }

    /**
     * QUANTUM SHIELD: AES-256-GCM Encryption for Audit Data
     * Security Quantum: Encrypt PII and sensitive audit data at rest
     */
    async _encryptAuditEntry(auditEntry) {
        try {
            // Derive encryption key from environment secret
            const key = crypto.pbkdf2Sync(
                process.env.AUDIT_ENCRYPTION_KEY,
                AUDIT_CONFIG.ENCRYPTION.SALT,
                AUDIT_CONFIG.ENCRYPTION.ITERATIONS,
                AUDIT_CONFIG.ENCRYPTION.KEY_LENGTH,
                AUDIT_CONFIG.ENCRYPTION.DIGEST
            );

            const iv = crypto.randomBytes(AUDIT_CONFIG.ENCRYPTION.IV_LENGTH);
            const cipher = crypto.createCipheriv(
                AUDIT_CONFIG.ENCRYPTION.ALGORITHM,
                key,
                iv
            );

            // Encrypt the audit data
            const dataToEncrypt = JSON.stringify(auditEntry);
            let encrypted = cipher.update(dataToEncrypt, 'utf8', 'hex');
            encrypted += cipher.final('hex');

            // Get authentication tag for GCM
            const authTag = cipher.getAuthTag();

            return {
                iv: iv.toString('hex'),
                encryptedData: encrypted,
                authTag: authTag.toString('hex'),
                algorithm: AUDIT_CONFIG.ENCRYPTION.ALGORITHM,
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            console.error('❌ Quantum encryption failed:', error);
            throw new Error(`Audit encryption failed: ${error.message}`);
        }
    }

    /**
     * QUANTUM DECRYPTION: Decrypt audit entry for authorized access
     * Security Quantum: Only authorized compliance officers can decrypt
     */
    async decryptAuditEntry(encryptedData, requesterRole) {
        // Authorization check (RBAC+ABAC Enforcement)
        if (!this._isAuthorizedForDecryption(requesterRole)) {
            throw new Error('QUANTUM BREACH: Unauthorized decryption attempt');
        }

        try {
            const key = crypto.pbkdf2Sync(
                process.env.AUDIT_ENCRYPTION_KEY,
                AUDIT_CONFIG.ENCRYPTION.SALT,
                AUDIT_CONFIG.ENCRYPTION.ITERATIONS,
                AUDIT_CONFIG.ENCRYPTION.KEY_LENGTH,
                AUDIT_CONFIG.ENCRYPTION.DIGEST
            );

            const decipher = crypto.createDecipheriv(
                AUDIT_CONFIG.ENCRYPTION.ALGORITHM,
                key,
                Buffer.from(encryptedData.iv, 'hex')
            );

            decipher.setAuthTag(Buffer.from(encryptedData.authTag, 'hex'));

            let decrypted = decipher.update(encryptedData.encryptedData, 'hex', 'utf8');
            decrypted += decipher.final('utf8');

            return JSON.parse(decrypted);
        } catch (error) {
            console.error('❌ Quantum decryption failed:', error);
            throw new Error(`Audit decryption failed: ${error.message}`);
        }
    }

    /**
     * PERSISTENCE NEXUS: Store audit entry with integrity proofs
     */
    async _persistAuditEntry(auditEntry, encryptedEntry) {
        const category = auditEntry.retention.category;
        const date = new Date().toISOString().split('T')[0];

        // Determine storage path
        const storagePath = path.join(
            AUDIT_CONFIG.BASE_PATH,
            category,
            `${date}.audit`
        );

        try {
            // Prepare entry for storage
            const storageEntry = {
                header: {
                    version: '2.0',
                    hash: auditEntry.hashChain.currentHash,
                    previousHash: auditEntry.hashChain.previousHash,
                    timestamp: auditEntry.timestamp
                },
                encryptedData: encryptedEntry,
                publicMetadata: {
                    auditId: auditEntry.auditId,
                    userId: auditEntry.userId,
                    action: auditEntry.action,
                    entityType: auditEntry.entityType,
                    timestamp: auditEntry.timestamp,
                    jurisdiction: auditEntry.jurisdiction
                }
            };

            // Check file size before writing
            await this._enforceFileSizeLimit(storagePath);

            // Convert to JSON
            let dataToStore = JSON.stringify(storageEntry);

            // Optional compression
            if (this.compressionEnabled && dataToStore.length > 1024) {
                dataToStore = await promisify(zlib.deflate)(dataToStore);
            }

            // Append to daily audit file
            await fs.appendFile(
                storagePath,
                dataToStore + (this.compressionEnabled ? '' : '\n'),
                { flag: 'a', mode: 0o600 }
            );

            // Create individual proof file for critical audits
            if (auditEntry.actionType === 'critical' || auditEntry.complianceTags.popia) {
                await this._createIndividualProofFile(auditEntry, encryptedEntry);
            }

            console.log(`📝 Quantum audit stored: ${auditEntry.auditId} | ${auditEntry.action}`);
        } catch (error) {
            console.error('❌ Audit persistence failed:', error);
            await this._emergencyStorage(auditEntry, error);
        }
    }

    /**
     * INTEGRITY VERIFICATION: Validate audit trail integrity
     */
    async verifyAuditIntegrity(auditId, category, date) {
        try {
            const filePath = path.join(
                AUDIT_CONFIG.BASE_PATH,
                category,
                `${date}.audit`
            );

            // Check if file exists
            try {
                await fs.access(filePath);
            } catch {
                return {
                    auditId,
                    verified: false,
                    chainIntegrity: false,
                    entriesChecked: 0,
                    tamperedEntries: [],
                    error: 'Audit file not found'
                };
            }

            const fileContent = await fs.readFile(filePath, 'utf8');
            const entries = fileContent.trim().split('\n');

            let previousHash = null;
            let foundEntry = null;
            let integrity = true;
            let verificationReport = {
                auditId,
                verified: false,
                chainIntegrity: true,
                entriesChecked: 0,
                tamperedEntries: []
            };

            for (const entryStr of entries) {
                if (!entryStr.trim()) continue;

                verificationReport.entriesChecked++;

                try {
                    const entry = JSON.parse(entryStr);

                    // Check hash chain
                    if (previousHash && entry.header.previousHash !== previousHash) {
                        integrity = false;
                        verificationReport.tamperedEntries.push({
                            auditId: entry.publicMetadata.auditId,
                            expectedPreviousHash: previousHash,
                            actualPreviousHash: entry.header.previousHash
                        });
                    }

                    // Verify current hash matches content
                    const calculatedHash = this._generateHash(JSON.stringify(entry.encryptedData));
                    if (calculatedHash !== entry.header.hash) {
                        integrity = false;
                        verificationReport.tamperedEntries.push({
                            auditId: entry.publicMetadata.auditId,
                            expectedHash: entry.header.hash,
                            calculatedHash
                        });
                    }

                    // Check if this is our target entry
                    if (entry.publicMetadata.auditId === auditId) {
                        foundEntry = entry;
                    }

                    previousHash = entry.header.hash;
                } catch (parseError) {
                    integrity = false;
                    verificationReport.tamperedEntries.push({
                        error: 'Invalid JSON',
                        entry: entryStr.substring(0, 100)
                    });
                }
            }

            verificationReport.chainIntegrity = integrity;
            verificationReport.verified = !!(foundEntry && integrity);

            return verificationReport;
        } catch (error) {
            console.error('❌ Integrity verification failed:', error);
            return {
                auditId,
                verified: false,
                chainIntegrity: false,
                entriesChecked: 0,
                tamperedEntries: [],
                error: error.message
            };
        }
    }

    /**
     * COMPLIANCE EXPORT: Generate regulatory compliance reports
     */
    async generateComplianceReport(params) {
        const {
            startDate,
            endDate,
            jurisdiction,
            complianceType,
            userId,
            entityType,
            requesterRole
        } = params;

        // Validate parameters
        if (!startDate || !endDate) {
            throw new Error('Missing required parameters: startDate and endDate');
        }

        // Authorization check
        if (!this._isAuthorizedForComplianceReport(requesterRole)) {
            throw new Error('QUANTUM BREACH: Unauthorized compliance report request');
        }

        const report = {
            metadata: {
                generated: new Date().toISOString(),
                generator: 'Wilsy OS Quantum Audit Nexus',
                jurisdiction: jurisdiction || 'ALL',
                complianceType: complianceType || 'GENERAL',
                dateRange: { startDate, endDate }
            },
            summary: {
                totalEntries: 0,
                byCategory: {},
                byAction: {},
                byUser: {},
                complianceEvents: 0
            },
            entries: [],
            complianceFindings: []
        };

        try {
            // Convert dates to Date objects
            const start = new Date(startDate);
            const end = new Date(endDate);

            if (isNaN(start.getTime()) || isNaN(end.getTime())) {
                throw new Error('Invalid date format');
            }

            // Iterate through date range
            const currentDate = new Date(start);
            while (currentDate <= end) {
                const dateStr = currentDate.toISOString().split('T')[0];

                // Check each category directory
                for (const category of Object.values(AUDIT_CONFIG.CATEGORIES)) {
                    const filePath = path.join(
                        AUDIT_CONFIG.BASE_PATH,
                        category,
                        `${dateStr}.audit`
                    );

                    try {
                        await fs.access(filePath);
                        const entries = await this._readAuditFile(filePath);

                        for (const entry of entries) {
                            // Apply filters
                            if (userId && entry.publicMetadata.userId !== userId) continue;
                            if (entityType && entry.publicMetadata.entityType !== entityType) continue;
                            if (jurisdiction && entry.publicMetadata.jurisdiction !== jurisdiction) continue;

                            // Add to report
                            report.summary.totalEntries++;
                            report.entries.push({
                                timestamp: entry.publicMetadata.timestamp,
                                auditId: entry.publicMetadata.auditId,
                                userId: entry.publicMetadata.userId,
                                action: entry.publicMetadata.action,
                                entityType: entry.publicMetadata.entityType,
                                jurisdiction: entry.publicMetadata.jurisdiction
                            });

                            // Update summary counters
                            report.summary.byCategory[category] =
                                (report.summary.byCategory[category] || 0) + 1;
                            report.summary.byAction[entry.publicMetadata.action] =
                                (report.summary.byAction[entry.publicMetadata.action] || 0) + 1;
                            report.summary.byUser[entry.publicMetadata.userId] =
                                (report.summary.byUser[entry.publicMetadata.userId] || 0) + 1;
                        }
                    } catch (error) {
                        // File doesn't exist for this date/category, skip
                        continue;
                    }
                }

                currentDate.setDate(currentDate.getDate() + 1);
            }

            // Generate compliance findings
            report.complianceFindings = await this._analyzeComplianceFindings(report);
            report.summary.complianceEvents = report.complianceFindings.length;

        } catch (error) {
            console.error('❌ Compliance report generation failed:', error);
            throw new Error(`Compliance report failed: ${error.message}`);
        }

        return report;
    }

    /**
     * RETENTION ENFORCER: Auto-purge expired audit records
     */
    async enforceRetentionPolicy() {
        console.log('🔍 Quantum retention enforcement initiated');

        const today = new Date();
        let purgedCount = 0;
        let retainedCount = 0;
        let errors = [];

        try {
            // Walk through all audit directories
            for (const category of Object.values(AUDIT_CONFIG.CATEGORIES)) {
                const categoryPath = path.join(AUDIT_CONFIG.BASE_PATH, category);

                try {
                    const files = await fs.readdir(categoryPath);

                    for (const file of files) {
                        if (file.endsWith('.audit')) {
                            const filePath = path.join(categoryPath, file);
                            const fileDate = this._extractDateFromFilename(file);

                            if (fileDate) {
                                const daysOld = Math.floor((today - fileDate) / (1000 * 60 * 60 * 24));
                                const retentionDays = AUDIT_CONFIG.RETENTION_PERIODS[category.toUpperCase()] ||
                                    AUDIT_CONFIG.RETENTION_PERIODS.DEFAULT;

                                if (daysOld > retentionDays) {
                                    try {
                                        await fs.unlink(filePath);
                                        purgedCount++;
                                        console.log(`🗑️ Purged expired audit: ${file} (${daysOld} days old)`);
                                    } catch (unlinkError) {
                                        errors.push(`Failed to purge ${file}: ${unlinkError.message}`);
                                    }
                                } else {
                                    retainedCount++;
                                }
                            }
                        }
                    }
                } catch (categoryError) {
                    errors.push(`Category ${category}: ${categoryError.message}`);
                }
            }
        } catch (error) {
            errors.push(`Retention enforcement failed: ${error.message}`);
        }

        return {
            purgedCount,
            retainedCount,
            errors,
            timestamp: today.toISOString(),
            message: `Retention enforcement complete. Purged ${purgedCount}, retained ${retainedCount} audit files.`
        };
    }

    /**
     * Cleanup resources
     */
    async destroy() {
        if (this._batchProcessor) {
            clearInterval(this._batchProcessor);
        }

        if (redisClient) {
            await redisClient.quit();
        }

        // Flush any remaining batch entries
        if (this.batchQueue.length > 0) {
            await this._flushBatch();
        }
    }

    // ============================================================================
    // PRIVATE QUANTUM UTILITIES: Core Helper Functions
    // ============================================================================

    /**
     * Generate cryptographic hash for integrity proof
     */
    _generateHash(data) {
        return crypto
            .createHash('sha256')
            .update(data + AUDIT_CONFIG.ENCRYPTION.SALT)
            .digest('hex');
    }

    /**
     * Sanitize data to remove sensitive information before logging
     */
    _sanitizeData(data) {
        if (!data || typeof data !== 'object') return data;

        const sensitiveFields = [
            'password', 'token', 'secret', 'key', 'ssn', 'idnumber',
            'creditcard', 'cvv', 'pin', 'dob', 'phone', 'email',
            'credit_card', 'id_number'
        ];

        // Create a deep copy
        const sanitized = JSON.parse(JSON.stringify(data));

        const sanitizeRecursive = (obj) => {
            if (!obj || typeof obj !== 'object') return;

            // Handle arrays
            if (Array.isArray(obj)) {
                obj.forEach((item, index) => {
                    if (item && typeof item === 'object') {
                        sanitizeRecursive(item);
                    }
                });
                return;
            }

            // Handle objects
            const keys = Object.keys(obj);
            for (const key of keys) {
                const keyLower = key.toLowerCase();

                // Check if field is sensitive
                if (sensitiveFields.some(field => keyLower.includes(field))) {
                    obj[key] = '***REDACTED***';
                } else if (obj[key] && typeof obj[key] === 'object') {
                    sanitizeRecursive(obj[key]);
                }
            }
        };

        sanitizeRecursive(sanitized);
        return sanitized;
    }

    /**
     * Sanitize IP address
     */
    _sanitizeIp(ip) {
        if (!ip || ip === '::1' || ip === '127.0.0.1') {
            return '0.0.0.0';
        }

        // Basic IP validation
        const ipRegex = /^(\d{1,3}\.){3}\d{1,3}$/;
        if (ipRegex.test(ip)) {
            // Check if it's a local IP
            if (ip.startsWith('192.168.') || ip.startsWith('10.')) {
                return '0.0.0.0';
            }
        }

        return ip.substring(0, 45); // Truncate to prevent overflow
    }

    /**
     * Calculate expiry date based on retention period
     */
    _calculateExpiryDate(days) {
        const expiry = new Date();
        expiry.setDate(expiry.getDate() + days);
        return expiry.toISOString();
    }

    /**
     * Check authorization for decryption (RBAC+ABAC)
     */
    _isAuthorizedForDecryption(role) {
        if (!role) return false;

        const authorizedRoles = [
            'compliance_officer',
            'system_administrator',
            'legal_counsel',
            'data_protection_officer',
            'auditor',
            'admin'
        ];

        return authorizedRoles.includes(role.toLowerCase());
    }

    /**
     * Check authorization for compliance reports
     */
    _isAuthorizedForComplianceReport(role) {
        if (!role) return false;

        const authorizedRoles = [
            'compliance_officer',
            'data_protection_officer',
            'regulatory_affairs',
            'chief_legal_officer',
            'admin'
        ];

        return authorizedRoles.includes(role.toLowerCase());
    }

    /**
     * Create individual proof file for critical audits
     */
    async _createIndividualProofFile(auditEntry, encryptedEntry) {
        const proofDir = path.join(AUDIT_CONFIG.BASE_PATH, 'proofs');
        await fs.mkdir(proofDir, { recursive: true, mode: 0o700 });

        const proofPath = path.join(proofDir, `${auditEntry.auditId}.proof`);

        const proofData = {
            auditId: auditEntry.auditId,
            timestamp: auditEntry.timestamp,
            hash: auditEntry.hashChain.currentHash,
            previousHash: auditEntry.hashChain.previousHash,
            encryptedDataHash: this._generateHash(JSON.stringify(encryptedEntry)),
            witness: {
                system: 'Wilsy OS Quantum Audit Nexus',
                version: '2.0',
                witnessTimestamp: new Date().toISOString()
            }
        };

        await fs.writeFile(
            proofPath,
            JSON.stringify(proofData, null, 2),
            { mode: 0o600 }
        );
    }

    /**
     * Emergency storage when primary persistence fails
     */
    async _emergencyStorage(data, error = null) {
        const emergencyDir = path.join(AUDIT_CONFIG.BASE_PATH, 'emergency');
        await fs.mkdir(emergencyDir, { recursive: true, mode: 0o700 });

        const emergencyFile = path.join(
            emergencyDir,
            `emergency_${Date.now()}.json`
        );

        const emergencyRecord = {
            timestamp: new Date().toISOString(),
            originalError: error?.message || 'Unknown error',
            data
        };

        try {
            await fs.writeFile(
                emergencyFile,
                JSON.stringify(emergencyRecord, null, 2),
                { flag: 'a', mode: 0o600 }
            );

            console.log('⚠️ Emergency audit storage used:', emergencyFile);
        } catch (writeError) {
            console.error('❌ Emergency storage failed:', writeError);
            // Last resort: console error
            console.error('🚨 CRITICAL AUDIT FAILURE:', emergencyRecord);
        }
    }

    /**
     * Read and parse audit file
     */
    async _readAuditFile(filePath) {
        try {
            let content = await fs.readFile(filePath, 'utf8');

            if (this.compressionEnabled) {
                try {
                    content = await promisify(zlib.inflate)(Buffer.from(content, 'binary'));
                    content = content.toString('utf8');
                } catch (compressionError) {
                    // File might not be compressed
                    console.warn('File may not be compressed:', compressionError.message);
                }
            }

            const lines = content.trim().split('\n');
            const entries = [];

            for (const line of lines) {
                if (!line.trim()) continue;

                try {
                    entries.push(JSON.parse(line));
                } catch (parseError) {
                    console.warn('Failed to parse audit line:', parseError.message);
                }
            }

            return entries;
        } catch (error) {
            throw new Error(`Failed to read audit file: ${error.message}`);
        }
    }

    /**
     * Extract date from filename
     */
    _extractDateFromFilename(filename) {
        const dateMatch = filename.match(/(\d{4}-\d{2}-\d{2})/);
        if (!dateMatch) return null;

        const date = new Date(dateMatch[1]);
        return isNaN(date.getTime()) ? null : date;
    }

    /**
     * Analyze compliance findings from audit data
     */
    async _analyzeComplianceFindings(report) {
        const findings = [];

        // POPIA Compliance Checks
        const popiaEntries = report.entries.filter(entry =>
            entry.action.includes('consent') ||
            entry.action.includes('data_access') ||
            entry.action.includes('data_deletion') ||
            entry.action.includes('privacy')
        );

        if (popiaEntries.length > 0) {
            findings.push({
                complianceType: 'POPIA',
                check: 'Lawful Processing Audit',
                status: popiaEntries.length > 100 ? 'REVIEW_REQUIRED' : 'COMPLIANT',
                details: `${popiaEntries.length} POPIA-relevant actions recorded`,
                recommendation: 'Ensure all processing has valid legal basis recorded',
                severity: 'MEDIUM'
            });
        }

        // GDPR Cross-Border Checks
        const gdprEntries = report.entries.filter(entry =>
            entry.jurisdiction === 'EU'
        );

        if (gdprEntries.length > 0) {
            findings.push({
                complianceType: 'GDPR',
                check: 'Cross-Border Data Transfer',
                status: 'REVIEW_REQUIRED',
                details: `${gdprEntries.length} EU jurisdiction actions detected`,
                recommendation: 'Verify Standard Contractual Clauses or adequacy decisions',
                severity: 'HIGH'
            });
        }

        // Security Incident Detection
        const securityEntries = report.entries.filter(entry =>
            entry.action.includes('failed_login') ||
            entry.action.includes('access_denied') ||
            entry.action.includes('security_breach') ||
            entry.action.includes('unauthorized')
        );

        if (securityEntries.length > 10) {
            findings.push({
                complianceType: 'CYBERCRIMES_ACT',
                check: 'Security Incident Logging',
                status: 'INVESTIGATE',
                details: `${securityEntries.length} security-related events detected`,
                recommendation: 'Review for potential attack patterns',
                severity: 'HIGH'
            });
        }

        // Data Retention Compliance
        const retentionEntries = report.entries.filter(entry =>
            entry.action.includes('delete') ||
            entry.action.includes('archive') ||
            entry.action.includes('purge')
        );

        if (retentionEntries.length > 0) {
            findings.push({
                complianceType: 'COMPANIES_ACT',
                check: 'Record Retention Compliance',
                status: 'COMPLIANT',
                details: `${retentionEntries.length} retention-related actions`,
                recommendation: 'Maintain retention schedule documentation',
                severity: 'MEDIUM'
            });
        }

        return findings;
    }

    /**
     * Process batch queue
     */
    async _processBatch() {
        if (this.batchQueue.length === 0) return;

        try {
            await this._flushBatch();
        } catch (error) {
            console.error('❌ Batch processing failed:', error);
        }
    }

    /**
     * Flush batch queue to storage
     */
    async _flushBatch() {
        if (this.batchQueue.length === 0) return;

        const batch = [...this.batchQueue];
        this.batchQueue = [];

        const batchSummary = {
            batchId: uuidv4(),
            timestamp: new Date().toISOString(),
            entryCount: batch.length,
            entries: batch
        };

        const batchDir = path.join(AUDIT_CONFIG.BASE_PATH, 'batches');
        await fs.mkdir(batchDir, { recursive: true, mode: 0o700 });

        const batchPath = path.join(batchDir, `${batchSummary.batchId}.batch`);

        try {
            await fs.writeFile(
                batchPath,
                JSON.stringify(batchSummary, null, 2),
                { mode: 0o600 }
            );

            console.log(`📦 Flushed audit batch: ${batch.length} entries`);
        } catch (error) {
            console.error('❌ Batch storage failed:', error);
            // Add back to queue for retry
            this.batchQueue.unshift(...batch);
        }
    }

    /**
     * Enforce file size limits
     */
    async _enforceFileSizeLimit(filePath) {
        try {
            const stats = await fs.stat(filePath);
            if (stats.size > AUDIT_CONFIG.SECURITY.MAX_AUDIT_SIZE_BYTES) {
                // Rotate file
                const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
                const newPath = `${filePath}.${timestamp}.full`;
                await fs.rename(filePath, newPath);
                console.log(`🔄 Audit file rotated: ${newPath}`);
            }
        } catch (error) {
            // File doesn't exist yet, that's fine
            if (error.code !== 'ENOENT') {
                throw error;
            }
        }
    }

    /**
     * Cache audit entry in Redis for fast retrieval
     */
    async _cacheAuditEntry(auditId, auditEntry, ttl = 3600) {
        if (!redisClient) return;

        try {
            await redisClient.setex(
                `audit:${auditId}`,
                ttl,
                JSON.stringify(auditEntry)
            );
        } catch (error) {
            console.warn('⚠️ Audit cache failed:', error.message);
        }
    }

    /**
     * Retrieve cached audit entry
     */
    async getCachedAuditEntry(auditId) {
        if (!redisClient) return null;

        try {
            const cached = await redisClient.get(`audit:${auditId}`);
            return cached ? JSON.parse(cached) : null;
        } catch (error) {
            console.warn('⚠️ Audit cache retrieval failed:', error.message);
            return null;
        }
    }
}

// ============================================================================
// QUANTUM FACTORY: Singleton Instance Export
// ============================================================================
let quantumAuditInstance = null;

function getQuantumAuditLogger() {
    if (!quantumAuditInstance) {
        quantumAuditInstance = new QuantumAuditLogger();
    }
    return quantumAuditInstance;
}

// ============================================================================
// QUANTUM MIDDLEWARE: Express.js Integration
// ============================================================================
function auditMiddleware(req, res, next) {
    // Skip audit for health checks and monitoring endpoints
    const skipPaths = ['/health', '/metrics', '/favicon.ico', '/robots.txt'];
    if (skipPaths.includes(req.path)) {
        return next();
    }

    // Capture request start time
    const startTime = Date.now();

    // Store original end method
    const originalEnd = res.end;
    const originalWrite = res.write;

    let responseBody = Buffer.from('');

    // Override write to capture response body
    res.write = function (chunk, encoding) {
        if (chunk) {
            responseBody = Buffer.concat([responseBody, Buffer.from(chunk)]);
        }
        return originalWrite.call(this, chunk, encoding);
    };

    // Override end method to capture response
    res.end = async function (chunk, encoding) {
        if (chunk) {
            responseBody = Buffer.concat([responseBody, Buffer.from(chunk)]);
        }

        // Restore original methods
        res.write = originalWrite;
        res.end = originalEnd;

        // Call original end
        res.end(chunk, encoding);

        // Calculate response time
        const responseTime = Date.now() - startTime;

        // Create audit data
        const auditData = {
            userId: req.user?.id || 'anonymous',
            userRole: req.user?.role || 'guest',
            userIp: _sanitizeIpForMiddleware(req.ip),
            userAgent: req.get('user-agent') || 'Unknown',
            action: `${req.method} ${req.path}`,
            actionType: _classifyActionType(req),
            entityType: 'http_request',
            entityId: req.id || uuidv4(),
            resource: req.path,
            sessionId: req.session?.id,
            requestId: req.id,
            jurisdiction: _determineJurisdiction(req),
            legalBasis: 'POPIA_8(1)(f)',
            metadata: {
                queryParams: _sanitizeDataForMiddleware(req.query),
                headers: _sanitizeHeadersForMiddleware(req.headers),
                bodyHash: req.body ? crypto.createHash('sha256').update(JSON.stringify(req.body)).digest('hex') : null,
                responseTime,
                statusCode: res.statusCode,
                responseSize: responseBody.length
            },
            complianceTags: {
                popia: req.path.includes('/api/data') || req.path.includes('/consent'),
                paia: req.path.includes('/api/access-request'),
                ectAct: req.path.includes('/api/sign')
            }
        };

        // Create audit entry asynchronously (don't block response)
        setTimeout(async () => {
            try {
                const auditLogger = getQuantumAuditLogger();
                await auditLogger.createAuditEntry(auditData);
            } catch (error) {
                console.error('⚠️ Audit middleware failed:', error.message);
            }
        }, 0);
    };

    next();
}

// Helper functions for middleware
function _classifyActionType(req) {
    if (req.method === 'DELETE') return 'critical';
    if (req.method === 'POST' && req.path.includes('/admin/')) return 'administrative';
    if (req.path.includes('/api/data/')) return 'data_processing';
    if (req.path.includes('/api/payment/')) return 'financial';
    return 'system';
}

function _determineJurisdiction(req) {
    // Extract from headers or IP geolocation
    const geoHeader = req.get('CF-IPCountry') || req.get('X-Geo-Country') || req.get('X-Forwarded-For-Country');
    if (geoHeader) {
        const country = geoHeader.toUpperCase();
        if (Object.values(AUDIT_CONFIG.JURISDICTIONS).includes(country)) {
            return country;
        }
    }

    // Default to South Africa for Wilsy OS
    return 'ZA';
}

function _sanitizeIpForMiddleware(ip) {
    if (!ip) return '0.0.0.0';

    // Handle IPv6 localhost
    if (ip === '::1' || ip === '::ffff:127.0.0.1') {
        return '0.0.0.0';
    }

    // Extract first IP if it's a list (behind proxy)
    const firstIp = ip.split(',')[0].trim();

    // Basic sanitization
    if (firstIp.startsWith('192.168.') || firstIp.startsWith('10.') || firstIp.startsWith('172.')) {
        return '0.0.0.0';
    }

    return firstIp.substring(0, 45);
}

function _sanitizeHeadersForMiddleware(headers) {
    const sanitized = {};
    const sensitiveHeaders = ['authorization', 'cookie', 'x-api-key', 'x-secret', 'x-access-token'];

    for (const [key, value] of Object.entries(headers)) {
        const keyLower = key.toLowerCase();
        if (sensitiveHeaders.some(sensitive => keyLower.includes(sensitive))) {
            sanitized[key] = '***REDACTED***';
        } else {
            sanitized[key] = String(value).substring(0, 500);
        }
    }

    return sanitized;
}

function _sanitizeDataForMiddleware(data) {
    if (!data || typeof data !== 'object') return data;

    const sensitiveFields = ['password', 'token', 'secret', 'key', 'credit', 'card', 'cvv', 'pin'];

    const sanitized = JSON.parse(JSON.stringify(data));

    const sanitizeRecursive = (obj) => {
        if (!obj || typeof obj !== 'object') return;

        if (Array.isArray(obj)) {
            obj.forEach(item => sanitizeRecursive(item));
            return;
        }

        const keys = Object.keys(obj);
        for (const key of keys) {
            const keyLower = key.toLowerCase();
            if (sensitiveFields.some(field => keyLower.includes(field))) {
                obj[key] = '***REDACTED***';
            } else if (obj[key] && typeof obj[key] === 'object') {
                sanitizeRecursive(obj[key]);
            }
        }
    };

    sanitizeRecursive(sanitized);
    return sanitized;
}

// ============================================================================
// QUANTUM VALIDATION: Test Suite Exports
// ============================================================================
const TEST_CONFIG = {
    mockEncryptionKey: 'test-key-32-chars-long-for-testing-only',
    mockSalt: 'test-salt-16-chars',
    testAuditPath: path.join(__dirname, '..', 'test_audit_logs')
};

// ============================================================================
// QUANTUM SENTINEL BEACONS: Extension Points
// ============================================================================
const QUANTUM_EXTENSIONS = {
    // Blockchain Ledger Integration
    BLOCKCHAIN_HOOK: '// Eternal Extension: Integrate with Hyperledger Fabric',

    // AI Anomaly Detection
    AI_HOOK: '// Eternal Extension: TensorFlow.js for audit pattern analysis',

    // Quantum-Resistant Cryptography
    CRYPTO_HOOK: '// Eternal Extension: Migrate to post-quantum cryptography',

    // Real-time Compliance Dashboard
    DASHBOARD_HOOK: '// Eternal Extension: WebSocket stream to admin dashboard',

    // Cross-Jurisdiction Compliance Engine
    JURISDICTION_HOOK: '// Eternal Extension: Dynamic compliance for 50+ jurisdictions'
};

// ============================================================================
// BIBLICAL DEPLOYMENT: Production Readiness
// ============================================================================
console.log(`
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   "And the writing was written, and noted, and sealed according to the law"  ║
║                                    - Daniel 6:10                             ║
║                                                                              ║
║   QUANTUM AUDIT NEXUS ACTIVATED                                              ║
║   Legal Chronicles Forged • Compliance Proofs Sealed                         ║
║   Pan-African Justice Democratization Accelerated                            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
`);

// ============================================================================
// QUANTUM EXPORTS
// ============================================================================
module.exports = {
    QuantumAuditLogger,
    getQuantumAuditLogger,
    auditMiddleware,
    AUDIT_CONFIG,
    TEST_CONFIG,
    QUANTUM_EXTENSIONS
};

// FINAL QUANTUM INVOCATION
console.log('🌟 Wilsy Touching Lives Eternally 🌟');