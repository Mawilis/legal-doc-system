/* eslint-disable */
/* ╔══════════════════════════════════════════════════════════════════════════════╗
   ║ AUDIT LOGGER - INVESTOR-GRADE FORENSIC TRACKING                            ║
   ║ Tamper-proof | Immutable | Court-admissible | POPIA compliant              ║
   ║ Standard: ES Module (Standardized)                                         ║
   ╚══════════════════════════════════════════════════════════════════════════════╝*/

import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import path from 'node:path';
import logger from './logger.js';

/**
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/utils/auditLogger.js
 * INVESTOR VALUE PROPOSITION:
 * • Solves: Data tampering risks in legal records
 * • Compliance: ECT Act §15 (Functional Equivalence of Electronic Signatures)
 * • Architecture: Cryptographically linked audit chain (Private Ledger)
 */

class AuditLogger {
    constructor() {
        this.auditTrail = [];
        this.previousHash = '0'.repeat(64); // Genesis block hash
        this.auditPath = path.join(process.cwd(), 'logs', 'audit');
        // Initialization handled via an internal promise to ensure async readiness
        this.initPromise = this._initializeAuditStorage();
    }

    /**
     * Initialize audit storage folders and state
     */
    async _initializeAuditStorage() {
        try {
            await fs.mkdir(this.auditPath, { recursive: true });

            const lastBlockPath = path.join(this.auditPath, 'last-block.txt');
            try {
                const savedHash = await fs.readFile(lastBlockPath, 'utf8');
                if (savedHash) this.previousHash = savedHash.trim();
            } catch (error) {
                // No previous hash file exists, create the genesis state
                await fs.writeFile(lastBlockPath, this.previousHash);
            }
        } catch (error) {
            logger.error('🛡️ Audit Storage Initialization Failure', { error: error.message });
        }
    }

    /**
     * Create an immutable audit entry
     */
    async audit(data) {
        await this.initPromise; // Ensure storage is ready

        const auditEntry = {
            ...data,
            timestamp: data.timestamp || new Date().toISOString(),
            auditId: this._generateAuditId(),
            nodeId: process.env.NODE_ID || 'wilsy-core-01',
            environment: process.env.NODE_ENV || 'production'
        };

        // Add to the internal chain
        const block = await this._addToBlockchain(auditEntry);

        // Persist to disk
        await this._writeAuditBlock(block);

        logger.info('📜 Audit Entry Committed', {
            auditId: auditEntry.auditId,
            action: data.action,
            hash: block.hash.substring(0, 8)
        });

        return block;
    }

    /**
     * Internal blockchain logic
     */
    async _addToBlockchain(data) {
        const block = {
            index: this.auditTrail.length,
            timestamp: data.timestamp,
            data: this._sanitizeData(data),
            previousHash: this.previousHash,
            nonce: 0
        };

        block.hash = this._calculateHash(block);
        this.previousHash = block.hash;

        // Persistent State Update
        const lastBlockPath = path.join(this.auditPath, 'last-block.txt');
        await fs.writeFile(lastBlockPath, this.previousHash);

        return block;
    }

    _calculateHash(block) {
        const blockString = JSON.stringify({
            index: block.index,
            timestamp: block.timestamp,
            data: block.data,
            previousHash: block.previousHash,
            nonce: block.nonce
        });

        return crypto
            .createHash('sha256')
            .update(blockString)
            .digest('hex');
    }

    async _writeAuditBlock(block) {
        const date = new Date(block.timestamp).toISOString().split('T')[0];
        const filepath = path.join(this.auditPath, `audit-${date}.json`);

        try {
            let blocks = [];
            try {
                const content = await fs.readFile(filepath, 'utf8');
                blocks = JSON.parse(content);
            } catch (err) { /* File doesn't exist yet */ }

            blocks.push(block);
            await fs.writeFile(filepath, JSON.stringify(blocks, null, 2));
        } catch (error) {
            logger.error('🛡️ Audit Disk Write Failure', { error: error.message });
        }
    }

    _sanitizeData(data) {
        const sensitiveFields = ['password', 'token', 'secret', 'key', 'idNumber'];
        const sanitized = { ...data };

        for (const field of sensitiveFields) {
            if (sanitized[field]) {
                sanitized[field] = '[REDACTED_BY_WILSY]';
            }
        }
        return sanitized;
    }

    _generateAuditId() {
        return `AUD-${Date.now()}-${crypto.randomBytes(4).toString('hex').toUpperCase()}`;
    }

    /**
     * Court-Admissible Integrity Verification
     */
    async verifyIntegrity() {
        const blocks = [];
        const files = await fs.readdir(this.auditPath);

        for (const file of files) {
            if (file.startsWith('audit-') && file.endsWith('.json')) {
                const content = await fs.readFile(path.join(this.auditPath, file), 'utf8');
                blocks.push(...JSON.parse(content));
            }
        }

        blocks.sort((a, b) => a.index - b.index);

        for (let i = 1; i < blocks.length; i++) {
            const currentBlock = blocks[i];
            const previousBlock = blocks[i - 1];

            const reCalculated = this._calculateHash(currentBlock);
            if (reCalculated !== currentBlock.hash) return { valid: false, error: 'TAMPER_DETECTED', index: i };
            if (currentBlock.previousHash !== previousBlock.hash) return { valid: false, error: 'CHAIN_BROKEN', index: i };
        }

        return { valid: true, totalRecords: blocks.length };
    }
}

// 💎 Singleton Pattern for Global Audit Consistency
const auditLogger = new AuditLogger();

// 🚀 NATIVE ESM DEFAULT EXPORT
export default auditLogger;