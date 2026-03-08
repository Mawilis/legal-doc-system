/* eslint-disable */

/**
 * Forensic Evidence Writer
 * Atomic writes to /tmp/f500-certification-v8-final-<timestamp>.json
 */
import fs from 'fs/promises';
import path from 'path';
import crypto from 'crypto';

export class ForensicsManager {
    constructor(options = {}) {
        this.basePath = options.basePath || '/tmp';
        this.prefix = 'f500-certification-v8-final';
    }

    /**
     * Generate timestamp for filename
     */
    _getTimestamp() {
        const now = new Date();
        return now.toISOString().replace(/[:.]/g, '-').replace('T', '_').slice(0, 19);
    }

    /**
     * Generate filename with timestamp
     */
    _getFilename(timestamp = null) {
        const ts = timestamp || this._getTimestamp();
        return `${this.prefix}-${ts}.json`;
    }

    /**
     * Get full path
     */
    _getPath(timestamp = null) {
        return path.join(this.basePath, this._getFilename(timestamp));
    }

    /**
     * Write forensic evidence atomically
     */
    async writeEvidence(data) {
        const timestamp = this._getTimestamp();
        const finalPath = this._getPath(timestamp);
        const tempPath = `${finalPath}.tmp.${crypto.randomBytes(4).toString('hex')}`;

        // Add forensic metadata
        const evidence = {
            ...data,
            forensic: {
                generatedAt: new Date().toISOString(),
                timestamp,
                generator: 'WILSY-OS-FORENSICS-V8',
                checksum: null, // Will be filled
                signature: null // Will be filled
            }
        };

        // Calculate checksum
        const content = JSON.stringify(evidence, null, 2);
        evidence.forensic.checksum = crypto
            .createHash('sha3-512')
            .update(content)
            .digest('hex');

        // Add signature (stub - would be HSM in production)
        evidence.forensic.signature = crypto
            .createHash('sha3-512')
            .update(evidence.forensic.checksum + 'WILSY-OS-V8-FORTUNE-500')
            .digest('hex');

        // Atomic write
        await fs.writeFile(tempPath, JSON.stringify(evidence, null, 2), { mode: 0o644 });
        await fs.rename(tempPath, finalPath);

        return {
            path: finalPath,
            timestamp,
            evidence
        };
    }

    /**
     * Read forensic evidence
     */
    async readEvidence(timestamp = null) {
        const filepath = timestamp ? this._getPath(timestamp) : await this.getLatestFile();
        const content = await fs.readFile(filepath, 'utf8');
        return JSON.parse(content);
    }

    /**
     * Get latest forensic file
     */
    async getLatestFile() {
        const files = await fs.readdir(this.basePath);
        const forensicFiles = files
            .filter(f => f.startsWith(this.prefix))
            .sort()
            .reverse();

        if (forensicFiles.length === 0) {
            throw new Error('No forensic files found');
        }

        return path.join(this.basePath, forensicFiles[0]);
    }

    /**
     * Verify forensic evidence integrity
     */
    async verifyEvidence(timestamp = null) {
        const evidence = await this.readEvidence(timestamp);
        const content = JSON.stringify({ ...evidence, forensic: { ...evidence.forensic, checksum: null, signature: null } }, null, 2);
        const calculatedChecksum = crypto
            .createHash('sha3-512')
            .update(content)
            .digest('hex');

        return {
            valid: calculatedChecksum === evidence.forensic.checksum,
            timestamp: evidence.forensic.timestamp,
            checksumMatch: calculatedChecksum === evidence.forensic.checksum
        };
    }
}

// Singleton instance
let instance = null;

export function getForensicsManager(options = {}) {
    if (!instance) {
        instance = new ForensicsManager(options);
    }
    return instance;
}

export default getForensicsManager;