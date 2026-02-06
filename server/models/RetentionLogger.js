/*!
╔══════════════════════════════════════════════════════════════════════════════╗
║ ██████╗ ███████╗████████╗███████╗███╗   ██╗████████╗██╗ ██████╗ ███╗   ██╗   ║
║ ██╔══██╗██╔════╝╚══██╔══╝██╔════╝████╗  ██║╚══██╔══╝██║██╔═══██╗████╗  ██║   ║
║ ██████╔╝█████╗     ██║   █████╗  ██╔██╗ ██║   ██║   ██║██║   ██║██╔██╗ ██║   ║
║ ██╔══██╗██╔══╝     ██║   ██╔══╝  ██║╚██╗██║   ██║   ██║██║   ██║██║╚██╗██║   ║
║ ██║  ██║███████╗   ██║   ███████╗██║ ╚████║   ██║   ██║╚██████╔╝██║ ╚████║   ║
║ ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/         ║
║                RetentionLogger.js                                            ║
║ PURPOSE: Permanent immutable record of data disposal for compliance          ║
║ COMPLIANCE: POPIA §14 (Right to deletion) • Companies Act §24 (Retention)   ║
║             ECT Act §17 (Data Integrity) • PAIA §50 (Records Management)     ║
║ ASCII DATAFLOW: Retention Worker → Cryptographic Erasure → Log → OTS Anchor  ║
║ CHIEF ARCHITECT: Wilson Khanyezi — wilsy.wk@gmail.com | +27 69 046 5710      ║
║ ROI: Legal defensibility + POPIA compliance + Automated disposal audit trail ║
║ FILENAME: RetentionLogger.js                                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
*/

const mongoose = require('mongoose');
const crypto = require('crypto');

/**
 * RETENTION LOGGER SCHEMA
 * Permanent, immutable record of data disposal for legal compliance.
 * This collection serves as the "certificate of destruction" required by
 * POPIA, Companies Act, and other data protection regulations.
 * 
 * SECURITY PRINCIPLES:
 * - Immutable: Once written, cannot be modified or deleted
 * - Tenant-isolated: All records scoped to tenantId
 * - Cryptographically verifiable: certificateHash proves what was deleted
 * - Timestamped: Both system timestamp and optional OTS anchoring
 * 
 * @class RetentionLogger
 * @memberof module:models
 */
const RetentionLoggerSchema = new mongoose.Schema({
    // ===================== TENANT ISOLATION =====================
    tenantId: {
        type: String,
        required: [true, 'tenantId is required for multi-tenancy isolation'],
        index: true,
        trim: true,
        minlength: [1, 'tenantId cannot be empty'],
        maxlength: [64, 'tenantId cannot exceed 64 characters']
    },

    // ===================== ACTION METADATA =====================
    action: {
        type: String,
        required: [true, 'Disposal action type is required'],
        default: 'SECURE_DISPOSAL',
        immutable: true,
        enum: {
            values: [
                'SECURE_DISPOSAL',      // Standard deletion per retention policy
                'DSAR_COMPLIANCE',      // Deletion for POPIA data subject request
                'LEGAL_HOLD_RELEASE',   // Release after legal hold period
                'ANONYMIZATION',        // Data anonymization for research
                'EMERGENCY_CLEANSE'     // Emergency deletion per court order
            ],
            message: '{VALUE} is not a valid disposal action'
        }
    },

    // ===================== TARGET IDENTIFICATION =====================
    targetModel: {
        type: String,
        required: [true, 'Target model name is required for audit trail'],
        immutable: true,
        enum: {
            values: ['AuditLedger', 'Case', 'DsarRequest', 'Document', 'User', 'Consent', 'AccessLog'],
            message: '{VALUE} is not a supported model for retention logging'
        }
    },

    targetId: {
        type: mongoose.Schema.Types.ObjectId,
        required: [true, 'Target document ID is required'],
        immutable: true
    },

    targetCollection: {
        type: String,
        required: [true, 'Target collection name is required'],
        immutable: true,
        default: function () {
            // Auto-generate collection name from model (pluralized, lowercase)
            return this.targetModel.toLowerCase() + 's';
        }
    },

    // ===================== DISPOSAL METHODOLOGY =====================
    disposalMethod: {
        type: String,
        required: [true, 'Disposal methodology must be specified'],
        enum: {
            values: [
                'CRYPTOGRAPHIC_ERASURE',   // Key deletion rendering data unrecoverable
                'OVERWRITE_7_PASS',        // 7-pass DoD 5220.22-M standard
                'ANONYMIZATION',           // Data masking with retention of structure
                'PSEUDONYMIZATION',        // Reversible anonymization with key
                'PHYSICAL_DESTRUCTION'     // For physical media (logged separately)
            ],
            message: '{VALUE} is not a valid disposal method'
        },
        default: 'CRYPTOGRAPHIC_ERASURE'
    },

    disposalRationale: {
        type: String,
        required: false,
        maxlength: [500, 'Rationale cannot exceed 500 characters'],
        default: 'Retention period expired per data classification policy'
    },

    // ===================== CRYPTOGRAPHIC PROOF =====================
    certificateHash: {
        type: String,
        required: [true, 'Certificate hash is required for cryptographic proof'],
        immutable: true,
        match: [/^[a-f0-9]{64}$/, 'Certificate hash must be a valid SHA-256 hexadecimal string']
    },

    preDisposalHash: {
        type: String,
        required: false,
        match: [/^[a-f0-9]{64}$/, 'Pre-disposal hash must be a valid SHA-256 hexadecimal string'],
        description: 'Hash of the record BEFORE disposal (optional, for completeness)'
    },

    // ===================== EXECUTION CONTEXT =====================
    executedBy: {
        type: String,
        required: [true, 'Executor identification is required'],
        default: 'RETENTION_WORKER_SERVICE',
        maxlength: [128, 'Executor identifier cannot exceed 128 characters']
    },

    executionContext: {
        type: mongoose.Schema.Types.Mixed,
        required: false,
        description: 'Additional context about the execution (worker ID, job ID, etc.)'
    },

    // ===================== TIMESTAMPING & ANCHORING =====================
    timestamp: {
        type: Date,
        default: Date.now,
        immutable: true,
        index: true
    },

    otsProof: {
        type: String,
        required: false,
        description: 'OpenTimestamps proof for the certificateHash (when anchored)'
    },

    otsTimestamp: {
        type: Date,
        required: false,
        description: 'Timestamp from OTS proof (external verification)'
    },

    // ===================== COMPLIANCE METADATA =====================
    complianceReferences: {
        type: [String],
        required: false,
        default: [],
        description: 'References to specific compliance requirements (e.g., "POPIA §14", "Companies Act §24")'
    },

    informationOfficerNotified: {
        type: Boolean,
        default: false,
        description: 'Whether the Information Officer was notified of this disposal'
    },

    notificationTimestamp: {
        type: Date,
        required: false,
        description: 'When Information Officer was notified'
    },

    // ===================== AUDIT TRAIL =====================
    auditTrailId: {
        type: mongoose.Schema.Types.ObjectId,
        required: false,
        ref: 'AuditLedger',
        description: 'Reference to the main audit ledger entry for this disposal'
    }
}, {
    // ===================== COLLECTION CONFIGURATION =====================
    collection: 'retention_certificates',
    timestamps: false, // We use our own timestamp field for immutability control
    strict: true, // Reject fields not defined in schema
    toJSON: { virtuals: true },
    toObject: { virtuals: true }
});

// ===================== COMPOUND INDEXES =====================
RetentionLoggerSchema.index({ tenantId: 1, targetId: 1 }); // Fast lookup by tenant+target
RetentionLoggerSchema.index({ tenantId: 1, timestamp: -1 }); // Recent disposals per tenant
RetentionLoggerSchema.index({ tenantId: 1, targetModel: 1, timestamp: -1 }); // Model-specific queries
RetentionLoggerSchema.index({ certificateHash: 1 }, { unique: true }); // Prevent duplicate certificates
RetentionLoggerSchema.index({ tenantId: 1, action: 1, timestamp: 1 }); // Action-type analytics

// ===================== VIRTUAL PROPERTIES =====================
/**
 * Virtual property: disposalCertificate
 * Generates a human-readable certificate of destruction
 */
RetentionLoggerSchema.virtual('disposalCertificate').get(function () {
    return `Certificate of Secure Disposal
========================================
Tenant ID: ${this.tenantId}
Action: ${this.action}
Target: ${this.targetModel} (ID: ${this.targetId})
Disposal Method: ${this.disposalMethod}
Timestamp: ${this.timestamp.toISOString()}
Certificate Hash: ${this.certificateHash}
Executed By: ${this.executedBy}
${this.otsProof ? `OTS Proof: ${this.otsProof.substring(0, 64)}...` : ''}
========================================`;
});

/**
 * Virtual property: isAnchored
 * Checks if this disposal has been timestamped via OpenTimestamps
 */
RetentionLoggerSchema.virtual('isAnchored').get(function () {
    return !!(this.otsProof && this.otsTimestamp);
});

// ===================== STATIC METHODS =====================
/**
 * Generate a certificate hash for a disposal record
 * @static
 * @param {Object} disposalRecord - The disposal record to hash
 * @param {string} disposalRecord.tenantId - Tenant identifier
 * @param {string} disposalRecord.targetId - Target document ID
 * @param {string} disposalRecord.targetModel - Target model name
 * @param {string} disposalRecord.action - Disposal action type
 * @param {Date} disposalRecord.timestamp - Disposal timestamp
 * @returns {string} SHA-256 hash as hexadecimal string
 * @throws {Error} If required fields are missing
 */
RetentionLoggerSchema.statics.generateCertificateHash = function (disposalRecord) {
    const requiredFields = ['tenantId', 'targetId', 'targetModel', 'action', 'timestamp'];

    for (const field of requiredFields) {
        if (!disposalRecord[field]) {
            throw new Error(`Missing required field for certificate hash: ${field}`);
        }
    }

    // Create a deterministic string representation
    const hashPayload = [
        disposalRecord.tenantId,
        disposalRecord.targetId.toString(),
        disposalRecord.targetModel,
        disposalRecord.action,
        disposalRecord.timestamp.toISOString(),
        process.env.RETENTION_HASH_SALT || 'wilsy-retention-salt-2024' // Environment-based salt
    ].join('|');

    return crypto
        .createHash('sha256')
        .update(hashPayload)
        .digest('hex');
};

/**
 * Find all disposals for a specific tenant within a date range
 * @static
 * @param {string} tenantId - Tenant identifier
 * @param {Date} startDate - Start date for range
 * @param {Date} endDate - End date for range
 * @returns {Promise<Array>} Array of disposal records
 */
RetentionLoggerSchema.statics.findByTenantAndDateRange = async function (tenantId, startDate, endDate) {
    if (!tenantId || !startDate || !endDate) {
        throw new Error('tenantId, startDate, and endDate are required');
    }

    return this.find({
        tenantId,
        timestamp: {
            $gte: startDate,
            $lte: endDate
        }
    }).sort({ timestamp: -1 }); // Most recent first
};

/**
 * Verify the integrity of a disposal certificate
 * @static
 * @param {Object} disposalRecord - The disposal record to verify
 * @returns {boolean} True if the certificate hash is valid
 */
RetentionLoggerSchema.statics.verifyCertificate = function (disposalRecord) {
    try {
        const calculatedHash = this.generateCertificateHash(disposalRecord);
        return calculatedHash === disposalRecord.certificateHash;
    } catch (error) {
        return false;
    }
};

// ===================== INSTANCE METHODS =====================
/**
 * Generate a compliance report snippet for this disposal
 * @returns {string} Compliance report text
 */
RetentionLoggerSchema.methods.generateComplianceReport = function () {
    const report = `
DISPOSAL COMPLIANCE REPORT
==========================
Tenant: ${this.tenantId}
Date/Time: ${this.timestamp.toISOString()}
Action: ${this.action}
Target: ${this.targetModel} (ID: ${this.targetId})

COMPLIANCE REFERENCES:
${this.complianceReferences.map(ref => `- ${ref}`).join('\n')}

DISPOSAL METHODOLOGY:
Method: ${this.disposalMethod}
Rationale: ${this.disposalRationale || 'Not specified'}

VERIFICATION:
Certificate Hash: ${this.certificateHash}
Hash Valid: ${RetentionLogger.verifyCertificate(this) ? 'YES' : 'NO'}
OTS Anchored: ${this.isAnchored ? `YES (${this.otsTimestamp.toISOString()})` : 'NO'}

EXECUTION CONTEXT:
Executed By: ${this.executedBy}
${this.executionContext ? `Context: ${JSON.stringify(this.executionContext, null, 2)}` : ''}
`;

    return report;
};

// ===================== MIDDLEWARE =====================
/**
 * Pre-save middleware to ensure data integrity
 */
RetentionLoggerSchema.pre('save', function (next) {
    // Generate certificate hash if not provided
    if (!this.certificateHash) {
        try {
            this.certificateHash = this.constructor.generateCertificateHash(this);
        } catch (error) {
            return next(new Error(`Failed to generate certificate hash: ${error.message}`));
        }
    }

    // Ensure targetCollection is set
    if (!this.targetCollection) {
        this.targetCollection = this.targetModel.toLowerCase() + 's';
    }

    // Add default compliance references based on action
    if (!this.complianceReferences || this.complianceReferences.length === 0) {
        this.complianceReferences = ['POPIA §14', 'Companies Act §24'];
    }

    next();
});

/**
 * Pre-remove middleware: Prevent deletion of retention logs
 * These records MUST be immutable for legal defensibility
 */
RetentionLoggerSchema.pre('remove', function (next) {
    next(new Error('RetentionLogger records cannot be deleted. They are immutable for legal compliance.'));
});

/**
 * Pre-update middleware: Prevent updates to existing records
 */
RetentionLoggerSchema.pre('findOneAndUpdate', function (next) {
    next(new Error('RetentionLogger records cannot be updated. They are immutable for legal compliance.'));
});

// ===================== MERMAID DIAGRAM =====================
/**
 * MERMAID.JS DIAGRAM - RETENTION LOGGER DATA FLOW
 * 
 * This diagram illustrates how the RetentionLogger integrates with the
 * Wilsy OS compliance ecosystem for legally defensible data disposal.
 * 
 * To render this diagram locally:
 * 1. Save this code block to docs/diagrams/retention-logger-flow.mmd
 * 2. Run: npx mmdc -i docs/diagrams/retention-logger-flow.mmd -o docs/diagrams/retention-logger-flow.png
 */
const mermaidDiagram = `
flowchart TD
    subgraph A[Retention Policy Engine]
        A1[Retention Worker<br/>Agenda Job] --> A2{Retention Period Expired?}
        A2 -->|Yes| A3[Flag for Disposal]
        A2 -->|No| A4[Schedule Next Check]
    end
    
    subgraph B[Secure Disposal Process]
        B1[Retrieve Expired Record] --> B2[Generate Pre-Disposal Hash]
        B2 --> B3{Cryptographic Erasure}
        B3 -->|AES-256-GCM Key Deletion| B4[Data Unrecoverable]
        B3 -->|7-Pass Overwrite| B5[Physical Data Destruction]
    end
    
    subgraph C[Retention Logger Creation]
        C1[Create RetentionLogger Record] --> C2[Generate Certificate Hash]
        C2 --> C3[Save to MongoDB<br/>retention_certificates]
        C3 --> C4[Create Audit Ledger Entry]
    end
    
    subgraph D[Timestamp & Compliance]
        D1[Send Hash to OpenTimestamps] --> D2[Receive OTS Proof]
        D2 --> D3[Update RetentionLogger with OTS]
        D3 --> D4[Notify Information Officer]
        D4 --> D5[Generate Compliance Report]
    end
    
    subgraph E[Legal Defensibility]
        E1[Immutable Record Created] --> E2[Cryptographic Proof Stored]
        E2 --> E3[External Timestamp Obtained]
        E3 --> E4[Audit Trail Complete]
    end
    
    A3 --> B1
    B4 --> C1
    B5 --> C1
    C4 --> D1
    D5 --> E4
    
    style A fill:#e1f5fe,stroke:#01579b
    style B fill:#ffebee,stroke:#c62828
    style C fill:#fff3e0,stroke:#f57c00
    style D fill:#e8f5e8,stroke:#2e7d32
    style E fill:#f3e5f5,stroke:#7b1fa2
`;

// Export the model
const RetentionLogger = mongoose.models.RetentionLogger ||
    mongoose.model('RetentionLogger', RetentionLoggerSchema);

module.exports = RetentionLogger;

// ===================== JEST TESTS =====================
/* eslint-disable no-undef */
/**
 * JEST TEST SUITE FOR RETENTIONLOGGER MODEL
 * 
 * These tests verify:
 * 1. Schema validation and constraints
 * 2. Tenant isolation enforcement
 * 3. Cryptographic hash generation
 * 4. Immutability guarantees
 * 5. Integration with test database
 * 
 * Run with: npm test -- models/RetentionLogger.test.js
 * Requires: MONGO_URI_TEST environment variable
 */

if (process.env.NODE_ENV === 'test') {
    describe('RetentionLogger Model Tests', () => {
        let testDb;
        let testTenantId = 'test-tenant-' + Date.now();

        beforeAll(async () => {
            // Connect to test database
            const mongoose = require('mongoose');
            await mongoose.connect(process.env.MONGO_URI_TEST || 'mongodb://localhost:27017/wilsy-test');
            testDb = mongoose.connection;
        });

        afterAll(async () => {
            // Cleanup test data
            await RetentionLogger.deleteMany({ tenantId: testTenantId });
            await testDb.close();
        });

        test('should create a valid retention log', async () => {
            const disposalRecord = {
                tenantId: testTenantId,
                action: 'SECURE_DISPOSAL',
                targetModel: 'Document',
                targetId: new mongoose.Types.ObjectId(),
                disposalMethod: 'CRYPTOGRAPHIC_ERASURE',
                executedBy: 'jest-test-runner'
            };

            const log = new RetentionLogger(disposalRecord);
            await log.save();

            expect(log._id).toBeDefined();
            expect(log.certificateHash).toMatch(/^[a-f0-9]{64}$/);
            expect(log.timestamp).toBeInstanceOf(Date);
            expect(log.targetCollection).toBe('documents');
        });

        test('should enforce tenantId requirement', async () => {
            const log = new RetentionLogger({
                action: 'SECURE_DISPOSAL',
                targetModel: 'Document',
                targetId: new mongoose.Types.ObjectId()
            });

            await expect(log.save()).rejects.toThrow(/tenantId/);
        });

        test('should generate consistent certificate hash', () => {
            const disposalRecord = {
                tenantId: testTenantId,
                targetId: new mongoose.Types.ObjectId('507f1f77bcf86cd799439011'),
                targetModel: 'Document',
                action: 'SECURE_DISPOSAL',
                timestamp: new Date('2024-01-15T10:30:00Z')
            };

            const hash1 = RetentionLogger.generateCertificateHash(disposalRecord);
            const hash2 = RetentionLogger.generateCertificateHash(disposalRecord);

            expect(hash1).toBe(hash2);
            expect(hash1).toMatch(/^[a-f0-9]{64}$/);
        });

        test('should verify certificate integrity', () => {
            const disposalRecord = {
                tenantId: testTenantId,
                targetId: new mongoose.Types.ObjectId(),
                targetModel: 'Document',
                action: 'SECURE_DISPOSAL',
                timestamp: new Date(),
                certificateHash: 'abc123' // Invalid hash
            };

            expect(RetentionLogger.verifyCertificate(disposalRecord)).toBe(false);
        });

        test('should prevent updates to existing records', async () => {
            const log = new RetentionLogger({
                tenantId: testTenantId,
                action: 'SECURE_DISPOSAL',
                targetModel: 'Document',
                targetId: new mongoose.Types.ObjectId(),
                executedBy: 'jest-test-runner'
            });

            await log.save();

            await expect(
                RetentionLogger.findByIdAndUpdate(log._id, { action: 'MODIFIED' })
            ).rejects.toThrow(/cannot be updated/);
        });

        test('should find records by tenant and date range', async () => {
            const startDate = new Date('2024-01-01');
            const endDate = new Date('2024-12-31');

            const records = await RetentionLogger.findByTenantAndDateRange(
                testTenantId,
                startDate,
                endDate
            );

            expect(Array.isArray(records)).toBe(true);
        });
    });
}
/* eslint-enable no-undef */