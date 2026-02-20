/*╔══════════════════════════════════════════════════════════════════════════════╗
  ║ EVIDENCE GENERATOR - INVESTOR-GRADE MODULE                                  ║
  ║ SHA256 forensic evidence | Deterministic audit trails                       ║
  ╚══════════════════════════════════════════════════════════════════════════════╝*/
/**
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/utils/evidenceGenerator.js
 * VERSION: 2.0.0
 */

'use strict';

const crypto = require('crypto');
const fs = require('fs').promises;
const path = require('path');
const auditLogger = require('./auditLogger');

class EvidenceGenerator {
    constructor() {
        this.evidenceDir = path.join(__dirname, '../docs/evidence');
    }

    /**
     * Generate deterministic evidence.json with SHA256 hash
     */
    async generateEvidence(testName, auditEntries, economicMetric) {
        // Ensure directory exists
        try {
            await fs.mkdir(this.evidenceDir, { recursive: true });
        } catch (err) {
            // Directory already exists
        }

        // Canonicalize audit entries (sort keys for determinism)
        const canonicalEntries = auditEntries.map(entry => 
            JSON.parse(JSON.stringify(entry, Object.keys(entry).sort()))
        );

        // Create evidence object
        const evidence = {
            testName,
            timestamp: new Date().toISOString(),
            auditEntries: canonicalEntries,
            economicMetric,
            hash: null
        };

        // Generate SHA256 hash of the evidence
        const hash = crypto.createHash('sha256')
            .update(JSON.stringify(evidence))
            .digest('hex');
        
        evidence.hash = hash;

        // Save to file
        const filename = `evidence-${Date.now()}.json`;
        const filepath = path.join(this.evidenceDir, filename);
        await fs.writeFile(filepath, JSON.stringify(evidence, null, 2));

        // Audit the evidence generation using .log (test expects this)
        if (auditLogger.log) {
            await auditLogger.log({
                action: 'EVIDENCE_GENERATED',
                tenantId: 'SYSTEM',
                metadata: {
                    testName,
                    filename,
                    hash,
                    entryCount: canonicalEntries.length
                }
            });
        }

        return evidence;
    }

    /**
     * Generate investor evidence with economic metrics
     */
    async generateInvestorEvidence(testRunId, auditEntries, economicMetric) {
        const evidence = {
            metadata: {
                testSuite: 'CIPC Service',
                testRunId,
                timestamp: new Date().toISOString(),
                version: '1.0.0'
            },
            auditEntries,
            economicMetric,
            hash: crypto.createHash('sha256')
                .update(JSON.stringify(auditEntries))
                .digest('hex')
        };

        // Save to file
        const filename = `cipc-evidence-${Date.now()}.json`;
        const filepath = path.join(this.evidenceDir, filename);
        await fs.writeFile(filepath, JSON.stringify(evidence, null, 2));

        return evidence;
    }

    /**
     * Verify evidence integrity
     */
    async verifyEvidence(filepath) {
        const data = await fs.readFile(filepath, 'utf8');
        const evidence = JSON.parse(data);
        
        const calculatedHash = crypto.createHash('sha256')
            .update(JSON.stringify(evidence))
            .digest('hex');
        
        return {
            valid: calculatedHash === evidence.hash,
            evidence,
            calculatedHash
        };
    }
}

module.exports = new EvidenceGenerator();
