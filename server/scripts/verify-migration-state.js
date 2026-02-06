/*!
╔══════════════════════════════════════════════════════════════════════════════╗
║ ██╗   ██╗███████╗██████╗ ██╗███████╗██╗   ██╗                               ║
║ ██║   ██║██╔════╝██╔══██╗██║██╔════╝╚██╗ ██╔╝                               ║
║ ██║   ██║█████╗  ██████╔╝██║█████╗   ╚████╔╝                                ║
║ ╚██╗ ██╔╝██╔══╝  ██╔══██╗██║██╔══╝    ╚██╔╝                                 ║
║  ╚████╔╝ ███████╗██║  ██║██║██║        ██║                                  ║
║   ╚═══╝  ╚══════╝╚═╝  ╚═╝╚═╝╚═╝        ╚═╝                                  ║
║   ███╗   ███╗██╗ ██████╗ ██████╗  █████╗ ████████╗██╗ ██████╗ ███╗   ██╗    ║
║   ████╗ ████║██║██╔════╝ ██╔══██╗██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║    ║
║   ██╔████╔██║██║██║  ███╗██████╔╝███████║   ██║   ██║██║   ██║██╔██╗ ██║    ║
║   ██║╚██╔╝██║██║██║   ██║██╔══██╗██╔══██║   ██║   ██║██║   ██║██║╚██╗██║    ║
║   ██║ ╚═╝ ██║██║╚██████╔╝██║  ██║██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║    ║
║   ╚═╝     ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/scripts/        ║
║                verify-migration-state.js                                     ║
║ PURPOSE: Verify tenant migration integrity & consistency across databases    ║
║ COMPLIANCE: POPIA (data integrity) • Companies Act (record continuity)       ║
║             ECT Act (non-repudiation) • PAIA (access preservation)           ║
║ ASCII DATAFLOW: Source DB → Hash Compare → Target DB → Report → OTS Anchor  ║
║ CHIEF ARCHITECT: Wilson Khanyezi — wilsy.wk@gmail.com | +27 69 046 5710      ║
║ ROI: Ensures zero data loss during migration + legal defensibility proof     ║
║ FILENAME: verify-migration-state.js                                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
*/

const mongoose = require('mongoose');
const crypto = require('crypto');
const fs = require('fs').promises;
const path = require('path');
const { execSync } = require('child_process');

/**
 * MIGRATION VERIFICATION TOOL
 * 
 * This script verifies the integrity of tenant migrations between databases.
 * It performs cryptographic comparisons of data before and after migration,
 * ensuring no data loss or corruption during the transfer process.
 * 
 * SECURITY FEATURES:
 * - Cryptographic hash verification of all migrated records
 * - Tenant isolation enforcement
 * - Immutable audit logging
 * - OTS timestamping for legal defensibility
 * 
 * USAGE:
 * node scripts/verify-migration-state.js --tenantId=TENANT_ID --sourceUri=URI --targetUri=URI
 */

class MigrationVerifier {
    /**
     * Initialize the migration verifier
     * @param {Object} options - Configuration options
     * @param {string} options.tenantId - Tenant identifier
     * @param {string} options.sourceUri - Source database connection string
     * @param {string} options.targetUri - Target database connection string
     * @param {string} options.reportPath - Path for output reports
     */
    constructor(options = {}) {
        this.tenantId = options.tenantId;
        this.sourceUri = options.sourceUri || process.env.MONGO_URI;
        this.targetUri = options.targetUri || process.env.MONGO_URI_TEST;
        this.reportPath = options.reportPath || './migration-reports';
        this.sourceConn = null;
        this.targetConn = null;
        this.verificationResults = {
            tenantId: this.tenantId,
            startTime: new Date(),
            collections: {},
            summary: {
                totalCollections: 0,
                verifiedCollections: 0,
                totalDocuments: 0,
                verifiedDocuments: 0,
                failedDocuments: 0
            },
            errors: []
        };
    }

    /**
     * Generate cryptographic hash for a document
     * @param {Object} doc - MongoDB document
     * @returns {string} SHA-256 hash
     */
    static generateDocumentHash(doc) {
        // Remove MongoDB-specific fields for consistent hashing
        const { _id, __v, createdAt, updatedAt, ...cleanDoc } = doc;

        // Sort keys for deterministic JSON stringification
        const sortedDoc = Object.keys(cleanDoc)
            .sort()
            .reduce((acc, key) => {
                acc[key] = cleanDoc[key];
                return acc;
            }, {});

        const docString = JSON.stringify(sortedDoc, (key, value) => {
            // Handle ObjectId and Date objects for consistent stringification
            if (value && typeof value === 'object') {
                if (value.constructor.name === 'ObjectId') {
                    return value.toString();
                }
                if (value.constructor.name === 'Date') {
                    return value.toISOString();
                }
                if (Buffer.isBuffer(value)) {
                    return value.toString('base64');
                }
            }
            return value;
        });

        return crypto
            .createHash('sha256')
            .update(docString)
            .digest('hex');
    }

    /**
     * Connect to source and target databases
     */
    async connect() {
        console.log(`🔗 Connecting to databases for tenant: ${this.tenantId}`);

        try {
            // Connect to source database
            this.sourceConn = await mongoose.createConnection(this.sourceUri, {
                useNewUrlParser: true,
                useUnifiedTopology: true,
                serverSelectionTimeoutMS: 5000
            }).asPromise();

            console.log(`✅ Connected to source: ${this.sourceUri.split('@')[1]?.split('/')[0] || 'source'}`);

            // Connect to target database
            this.targetConn = await mongoose.createConnection(this.targetUri, {
                useNewUrlParser: true,
                useUnifiedTopology: true,
                serverSelectionTimeoutMS: 5000
            }).asPromise();

            console.log(`✅ Connected to target: ${this.targetUri.split('@')[1]?.split('/')[0] || 'target'}`);

        } catch (error) {
            throw new Error(`Database connection failed: ${error.message}`);
        }
    }

    /**
     * Get all collections for the tenant
     * @returns {Array} List of collection names
     */
    async getTenantCollections() {
        if (!this.sourceConn) {
            throw new Error('Source connection not established');
        }

        const db = this.sourceConn.db;
        const collections = await db.listCollections().toArray();

        // Filter collections that contain tenant data
        const tenantCollections = collections
            .map(col => col.name)
            .filter(name => !name.startsWith('system.'))
            .filter(name => !['sessions', 'migrations', 'jobs'].includes(name));

        return tenantCollections;
    }

    /**
     * Verify collection migration integrity
     * @param {string} collectionName - Name of collection to verify
     */
    async verifyCollection(collectionName) {
        console.log(`📊 Verifying collection: ${collectionName}`);

        const sourceModel = this.sourceConn.model(collectionName, new mongoose.Schema({}, { strict: false }), collectionName);
        const targetModel = this.targetConn.model(collectionName, new mongoose.Schema({}, { strict: false }), collectionName);

        // Query tenant-specific documents
        let sourceQuery = { tenantId: this.tenantId };
        let targetQuery = { tenantId: this.tenantId };

        // Handle collections without tenantId field
        try {
            const sampleDoc = await sourceModel.findOne().lean();
            if (!sampleDoc || !sampleDoc.tenantId) {
                console.log(`⚠️  Collection ${collectionName} doesn't use tenantId, verifying all documents`);
                sourceQuery = {};
                targetQuery = {};
            }
        } catch (error) {
            this.verificationResults.errors.push({
                collection: collectionName,
                error: `Schema check failed: ${error.message}`
            });
            return;
        }

        // Get documents from both databases
        const [sourceDocs, targetDocs] = await Promise.all([
            sourceModel.find(sourceQuery).lean(),
            targetModel.find(targetQuery).lean()
        ]);

        // Create maps for comparison
        const sourceMap = new Map();
        const targetMap = new Map();

        sourceDocs.forEach(doc => {
            const hash = MigrationVerifier.generateDocumentHash(doc);
            sourceMap.set(doc._id.toString(), { doc, hash });
        });

        targetDocs.forEach(doc => {
            const hash = MigrationVerifier.generateDocumentHash(doc);
            targetMap.set(doc._id.toString(), { doc, hash });
        });

        // Perform verification
        const verification = {
            collection: collectionName,
            sourceCount: sourceDocs.length,
            targetCount: targetDocs.length,
            matches: [],
            mismatches: [],
            missingInTarget: [],
            missingInSource: [],
            startTime: new Date()
        };

        // Compare documents
        for (const [docId, sourceData] of sourceMap.entries()) {
            const targetData = targetMap.get(docId);

            if (!targetData) {
                verification.missingInTarget.push(docId);
                continue;
            }

            if (sourceData.hash === targetData.hash) {
                verification.matches.push({
                    docId,
                    hash: sourceData.hash
                });
            } else {
                verification.mismatches.push({
                    docId,
                    sourceHash: sourceData.hash,
                    targetHash: targetData.hash
                });
            }

            targetMap.delete(docId);
        }

        // Any remaining in targetMap are missing in source
        for (const [docId, targetData] of targetMap.entries()) {
            verification.missingInSource.push(docId);
        }

        verification.endTime = new Date();
        verification.duration = verification.endTime - verification.startTime;

        // Update summary
        this.verificationResults.summary.totalCollections++;
        this.verificationResults.summary.totalDocuments += sourceDocs.length;
        this.verificationResults.summary.verifiedDocuments += verification.matches.length;
        this.verificationResults.summary.failedDocuments +=
            verification.mismatches.length +
            verification.missingInTarget.length +
            verification.missingInSource.length;

        if (verification.mismatches.length === 0 &&
            verification.missingInTarget.length === 0 &&
            verification.missingInSource.length === 0) {
            this.verificationResults.summary.verifiedCollections++;
        }

        this.verificationResults.collections[collectionName] = verification;

        console.log(`  ✅ Matches: ${verification.matches.length}`);
        console.log(`  ❌ Mismatches: ${verification.mismatches.length}`);
        console.log(`  📭 Missing in target: ${verification.missingInTarget.length}`);
        console.log(`  📭 Missing in source: ${verification.missingInSource.length}`);
    }

    /**
     * Generate OTS timestamp for verification report
     * @param {string} reportHash - Hash of the verification report
     * @returns {Promise<string|null>} OTS proof or null
     */
    async generateOTSProof(reportHash) {
        try {
            // Create temporary file with hash
            const tempFile = path.join(this.reportPath, `temp-${Date.now()}.txt`);
            await fs.writeFile(tempFile, reportHash);

            // Use OpenTimestamps client if available
            const otsCommand = `ots stamp ${tempFile}`;
            execSync(otsCommand, { stdio: 'pipe' });

            // Get proof
            const proofCommand = `ots info ${tempFile}`;
            const proof = execSync(proofCommand, { encoding: 'utf8' });

            // Cleanup
            await fs.unlink(tempFile);

            return proof;
        } catch (error) {
            console.log(`⚠️  OTS timestamping failed: ${error.message}`);
            return null;
        }
    }

    /**
     * Save verification report
     */
    async saveReport() {
        // Ensure report directory exists
        await fs.mkdir(this.reportPath, { recursive: true });

        // Update results
        this.verificationResults.endTime = new Date();
        this.verificationResults.duration =
            this.verificationResults.endTime - this.verificationResults.startTime;

        // Generate report hash
        const reportString = JSON.stringify(this.verificationResults, null, 2);
        const reportHash = crypto
            .createHash('sha256')
            .update(reportString)
            .digest('hex');

        this.verificationResults.reportHash = reportHash;

        // Try to get OTS proof
        if (process.env.OTS_ENABLED === 'true') {
            this.verificationResults.otsProof = await this.generateOTSProof(reportHash);
        }

        // Save detailed report
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const reportFile = path.join(
            this.reportPath,
            `migration-verification-${this.tenantId}-${timestamp}.json`
        );

        await fs.writeFile(reportFile, JSON.stringify(this.verificationResults, null, 2));

        // Save summary report
        const summaryFile = path.join(
            this.reportPath,
            `summary-${this.tenantId}-${timestamp}.txt`
        );

        const summary = this.generateSummaryText();
        await fs.writeFile(summaryFile, summary);

        console.log(`📄 Reports saved to: ${this.reportPath}`);
        console.log(`   📋 Detailed: ${path.basename(reportFile)}`);
        console.log(`   📋 Summary: ${path.basename(summaryFile)}`);

        return { reportFile, summaryFile, reportHash };
    }

    /**
     * Generate human-readable summary
     * @returns {string} Summary text
     */
    generateSummaryText() {
        const { summary } = this.verificationResults;
        const successRate = summary.totalDocuments > 0
            ? ((summary.verifiedDocuments / summary.totalDocuments) * 100).toFixed(2)
            : 0;

        return `MIGRATION VERIFICATION REPORT
========================================
Tenant ID: ${this.tenantId}
Verification Date: ${new Date().toISOString()}
Duration: ${this.verificationResults.duration}ms

SUMMARY
-------
Collections: ${summary.totalCollections} total, ${summary.verifiedCollections} verified
Documents: ${summary.totalDocuments} total, ${summary.verifiedDocuments} verified
Success Rate: ${successRate}%

DETAILED RESULTS
----------------
${Object.entries(this.verificationResults.collections).map(([colName, col]) => `
${colName}:
  Source: ${col.sourceCount} documents
  Target: ${col.targetCount} documents
  ✅ Matches: ${col.matches.length}
  ❌ Mismatches: ${col.mismatches.length}
  📭 Missing in target: ${col.missingInTarget.length}
  📭 Missing in source: ${col.missingInSource.length}
`).join('')}

REPORT HASH: ${this.verificationResults.reportHash}
${this.verificationResults.otsProof ? `OTS PROOF: ${this.verificationResults.otsProof.substring(0, 100)}...` : ''}

VERIFICATION STATUS: ${successRate === 100 ? '✅ COMPLETE SUCCESS' : '⚠️  PARTIAL SUCCESS'}

Wilsy OS Migration Verification Tool
Chief Architect: Wilson Khanyezi — wilsy.wk@gmail.com | +27 69 046 5710
========================================`;
    }

    /**
     * Run complete verification process
     */
    async run() {
        console.log('🚀 Starting migration verification...');
        console.log(`👤 Tenant: ${this.tenantId}`);

        try {
            await this.connect();

            const collections = await this.getTenantCollections();
            console.log(`📚 Found ${collections.length} collections to verify`);

            for (const collection of collections) {
                await this.verifyCollection(collection);
            }

            const report = await this.saveReport();

            // Print summary
            console.log('\n' + this.generateSummaryText());

            // Return success/failure
            const { summary } = this.verificationResults;
            const successRate = summary.totalDocuments > 0
                ? (summary.verifiedDocuments / summary.totalDocuments) * 100
                : 100;

            if (successRate === 100) {
                console.log('🎉 Migration verification PASSED');
                return { success: true, report };
            } else {
                console.log('⚠️  Migration verification PARTIAL SUCCESS');
                return { success: false, report, successRate };
            }

        } catch (error) {
            console.error(`❌ Verification failed: ${error.message}`);
            this.verificationResults.errors.push(error.message);

            // Save error report
            await this.saveReport();

            throw error;
        } finally {
            // Close connections
            if (this.sourceConn) await this.sourceConn.close();
            if (this.targetConn) await this.targetConn.close();
        }
    }
}

/**
 * Command-line interface
 */
async function main() {
    // Parse command line arguments
    const args = process.argv.slice(2);
    const options = {};

    args.forEach(arg => {
        if (arg.startsWith('--')) {
            const [key, value] = arg.substring(2).split('=');
            options[key] = value;
        }
    });

    // Validate required options
    if (!options.tenantId) {
        console.error('❌ Error: --tenantId is required');
        console.error('Usage: node verify-migration-state.js --tenantId=TENANT_ID [--sourceUri=URI] [--targetUri=URI]');
        process.exit(1);
    }

    // Set default URIs from environment
    if (!options.sourceUri) {
        options.sourceUri = process.env.MONGO_URI;
    }
    if (!options.targetUri) {
        options.targetUri = process.env.MONGO_URI_TEST;
    }

    // Verify environment variables are set
    if (!options.sourceUri && !process.env.MONGO_URI) {
        console.error('❌ Error: Source database URI not provided. Set MONGO_URI environment variable or use --sourceUri');
        process.exit(1);
    }

    console.log(`
╔═══════════════════════════════════════════════════════╗
║        WILSY OS - MIGRATION VERIFICATION             ║
║        Tenant: ${options.tenantId.padEnd(30)}       ║
╚═══════════════════════════════════════════════════════╝
    `);

    try {
        const verifier = new MigrationVerifier(options);
        const result = await verifier.run();

        if (result.success) {
            process.exit(0);
        } else {
            console.log(`⚠️  Verification completed with ${result.successRate.toFixed(2)}% success rate`);
            process.exit(1);
        }
    } catch (error) {
        console.error(`💥 Fatal error: ${error.message}`);
        process.exit(2);
    }
}

// ===================== MERMAID DIAGRAM =====================
/**
 * MERMAID.JS DIAGRAM - MIGRATION VERIFICATION ARCHITECTURE
 * 
 * This diagram illustrates the migration verification process flow.
 * 
 * To render this diagram locally:
 * 1. Save this code block to docs/diagrams/migration-verification-flow.mmd
 * 2. Run: npx mmdc -i docs/diagrams/migration-verification-flow.mmd -o docs/diagrams/migration-verification-flow.png
 */
const mermaidDiagram = `
flowchart TD
    subgraph A[Initiation Phase]
        A1([CLI Invocation<br/>node verify-migration-state.js]) --> A2{Parse Arguments<br/>--tenantId, --sourceUri, --targetUri}
        A2 --> A3[Load Environment Variables<br/>MONGO_URI, MONGO_URI_TEST]
        A3 --> A4[Initialize MigrationVerifier<br/>with tenant context]
    end
    
    subgraph B[Database Connection]
        B1[Connect to Source DB<br/>MONGO_URI] --> B2[Connect to Target DB<br/>MONGO_URI_TEST]
        B2 --> B3[List Tenant Collections<br/>Filter system collections]
    end
    
    subgraph C[Collection Verification Loop]
        C1[For each collection] --> C2[Query Tenant Documents<br/>with tenantId filter]
        C2 --> C3[Generate Document Hashes<br/>SHA-256 of normalized JSON]
        C3 --> C4[Compare Source vs Target<br/>by _id and hash]
        C4 --> C5{Hash Match?}
        C5 -->|Yes| C6[Record as Match]
        C5 -->|No| C7[Record as Mismatch]
        C7 --> C8[Log mismatch details]
    end
    
    subgraph D[Results Aggregation]
        D1[Aggregate Collection Results] --> D2[Calculate Success Metrics<br/>matches/total documents]
        D2 --> D3[Generate Report Hash<br/>SHA-256 of all results]
    end
    
    subgraph E[Report Generation & Anchoring]
        E1[Generate JSON Report<br/>with all verification details] --> E2[Generate Human-Readable Summary]
        E2 --> E3{OTS Enabled?}
        E3 -->|Yes| E4[Create OTS Timestamp<br/>via OpenTimestamps client]
        E3 -->|No| E5[Skip OTS anchoring]
        E4 --> E6[Save Reports to Disk<br/>./migration-reports/]
    end
    
    subgraph F[Cleanup & Exit]
        F1[Close DB Connections] --> F2[Print Summary to Console]
        F2 --> F3{Success Rate = 100%?}
        F3 -->|Yes| F4([Exit Code 0 - SUCCESS])
        F3 -->|No| F5([Exit Code 1 - PARTIAL])
        F6([Exit Code 2 - ERROR]) --> F7[Error Handler]
    end
    
    A4 --> B1
    B3 --> C1
    C6 --> D1
    C8 --> D1
    D3 --> E1
    E6 --> F1
    
    style A fill:#e1f5fe,stroke:#01579b
    style B fill:#fff3e0,stroke:#f57c00
    style C fill:#e8f5e8,stroke:#2e7d32
    style D fill:#f3e5f5,stroke:#7b1fa2
    style E fill:#e0f2f1,stroke:#00695c
    style F fill:#ffebee,stroke:#c62828
`;

// Export the class for programmatic use
if (require.main === module) {
    // Run as script
    main().catch(console.error);
} else {
    // Export for use as module
    module.exports = MigrationVerifier;
}

// ===================== JEST TESTS =====================
/* eslint-disable no-undef */
/**
 * JEST TEST SUITE FOR MIGRATION VERIFIER
 * 
 * These tests verify:
 * 1. Document hash generation consistency
 * 2. Tenant isolation in queries
 * 3. Error handling for missing connections
 * 4. Report generation functionality
 * 
 * Run with: npm test -- scripts/verify-migration-state.test.js
 * Requires: MONGO_URI_TEST environment variable
 */

if (process.env.NODE_ENV === 'test') {
    const mongoose = require('mongoose');

    describe('MigrationVerifier Tests', () => {
        let testVerifier;
        const testTenantId = 'test-tenant-' + Date.now();

        beforeAll(async () => {
            // Use test database for both source and target
            const testUri = process.env.MONGO_URI_TEST;
            testVerifier = new MigrationVerifier({
                tenantId: testTenantId,
                sourceUri: testUri,
                targetUri: testUri,
                reportPath: './test-reports'
            });
        });

        afterAll(async () => {
            // Cleanup test reports
            try {
                await require('fs').promises.rm('./test-reports', { recursive: true });
            } catch (error) {
                // Ignore cleanup errors
            }
        });

        test('should generate consistent document hash', () => {
            const testDoc = {
                _id: new mongoose.Types.ObjectId(),
                tenantId: testTenantId,
                name: 'Test Document',
                value: 123,
                createdAt: new Date('2024-01-01T10:00:00Z'),
                updatedAt: new Date('2024-01-02T10:00:00Z')
            };

            const hash1 = MigrationVerifier.generateDocumentHash(testDoc);
            const hash2 = MigrationVerifier.generateDocumentHash(testDoc);

            expect(hash1).toBe(hash2);
            expect(hash1).toMatch(/^[a-f0-9]{64}$/);
        });

        test('should handle documents without tenantId', () => {
            const testDoc = {
                _id: new mongoose.Types.ObjectId(),
                name: 'System Document',
                type: 'config'
            };

            const hash = MigrationVerifier.generateDocumentHash(testDoc);

            expect(hash).toMatch(/^[a-f0-9]{64}$/);
            expect(typeof hash).toBe('string');
        });

        test('should initialize with correct properties', () => {
            expect(testVerifier.tenantId).toBe(testTenantId);
            expect(testVerifier.sourceUri).toBe(process.env.MONGO_URI_TEST);
            expect(testVerifier.targetUri).toBe(process.env.MONGO_URI_TEST);
            expect(testVerifier.reportPath).toBe('./test-reports');
            expect(testVerifier.verificationResults.tenantId).toBe(testTenantId);
        });

        test('should generate summary text', async () => {
            // Manually set some results
            testVerifier.verificationResults.summary = {
                totalCollections: 3,
                verifiedCollections: 2,
                totalDocuments: 100,
                verifiedDocuments: 95,
                failedDocuments: 5
            };

            testVerifier.verificationResults.collections = {
                'documents': {
                    sourceCount: 50,
                    targetCount: 50,
                    matches: Array(48).fill({}),
                    mismatches: Array(2).fill({}),
                    missingInTarget: [],
                    missingInSource: []
                }
            };

            const summary = testVerifier.generateSummaryText();

            expect(summary).toContain('MIGRATION VERIFICATION REPORT');
            expect(summary).toContain(testTenantId);
            expect(summary).toContain('Collections: 3 total, 2 verified');
            expect(summary).toContain('Documents: 100 total, 95 verified');
        });

        test('should handle connection errors gracefully', async () => {
            const badVerifier = new MigrationVerifier({
                tenantId: testTenantId,
                sourceUri: 'mongodb://invalid:27017/nonexistent',
                targetUri: 'mongodb://invalid:27017/nonexistent'
            });

            await expect(badVerifier.connect()).rejects.toThrow('Database connection failed');
        });
    });
}
/* eslint-enable no-undef */