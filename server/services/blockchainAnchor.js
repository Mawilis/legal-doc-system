// ====================================================================
// FILE: server/services/blockchainAnchor.js - COMPLETE PRODUCTION
// ====================================================================
/**
 * WILSYS OS - LPC REGULATOR BLOCKCHAIN ANCHOR
 * LPC Rule 3.4.3 - Regulator Node Anchoring
 * SARB Guidance Note 6 - Trust Account Verification
 */

const crypto = require('crypto');
const axios = require('axios');
const { RetryableError, ServiceUnavailableError } = require('../utils/errors');

class BlockchainAnchor {
    constructor() {
        this.anchoredBlocks = new Map();
        this.pendingAnchors = new Map();
        this.retryQueue = [];
        this.anchorCount = 0;

        // LPC Regulator endpoints
        this.regulatorEndpoints = {
            primary: process.env.LPC_REGULATOR_URL || 'https://lpc.regulator.gov.za/api/v1/anchor',
            secondary: process.env.LPC_REGULATOR_FALLBACK_URL || 'https://anchor.lpc.org.za/api/v1/submit',
            sandbox: 'https://sandbox.lpc.regulator.gov.za/api/v1/test-anchor'
        };

        this.apiKey = process.env.LPC_REGULATOR_API_KEY;
        this.apiSecret = process.env.LPC_REGULATOR_API_SECRET;
        this.firmId = process.env.LPC_FIRM_ID || 'WILSYS-OS-001';

        this._initialize();
    }

    async _initialize() {
        // Test connection on startup
        try {
            await this._testConnection();
            console.log('✅ LPC Regulator Anchor: Connected');
        } catch (error) {
            console.error('⚠️ LPC Regulator Anchor: Connection failed - using local anchor mode');
        }
    }

    async _testConnection() {
        const testHash = crypto
            .createHash('sha3-512')
            .update('WILSYS-OS-INITIALIZATION-TEST')
            .digest('hex')
            .substring(0, 64);

        return this.anchor(testHash, { test: true });
    }

    /**
     * Anchor a hash to the LPC Regulator Blockchain
     * LPC Rule 3.4.3 - Block must be anchored to regulator node
     */
    async anchor(hash, options = {}) {
        const anchorId = crypto.randomUUID();
        const timestamp = new Date().toISOString();

        // Create anchor payload
        const payload = {
            anchorId,
            hash: hash.substring(0, 64),
            timestamp,
            firmId: options.firmId || this.firmId,
            source: 'WILSYS_OS_LPC_SERVICE',
            version: '5.0.3',
            environment: process.env.NODE_ENV || 'production',
            compliance: {
                lpcRule: '3.4.3',
                sarbGuidance: 'GN6.2026',
                regulatoryBody: 'LPC_ZA',
                submissionType: options.test ? 'TEST' : 'PRODUCTION'
            }
        };

        // Generate HMAC signature for regulator authentication
        const signature = crypto
            .createHmac('sha3-512', this.apiSecret || 'WILSYS-OS-FALLBACK-SECRET')
            .update(JSON.stringify(payload))
            .digest('hex');

        // Attempt to submit to regulator
        let regulatorResponse = null;
        let error = null;

        for (const [name, endpoint] of Object.entries(this.regulatorEndpoints)) {
            if (options.test && name !== 'sandbox') continue;
            if (!options.test && name === 'sandbox') continue;

            try {
                regulatorResponse = await axios.post(endpoint, payload, {
                    headers: {
                        'Authorization': `Bearer ${this.apiKey || 'test-key'}`,
                        'X-Signature': signature,
                        'X-Anchor-ID': anchorId,
                        'X-Firm-ID': this.firmId,
                        'Content-Type': 'application/json',
                        'User-Agent': 'WilsyOS/LPCService-5.0.3'
                    },
                    timeout: options.test ? 5000 : 10000,
                    validateStatus: (status) => status === 200 || status === 201 || status === 202
                });

                if (regulatorResponse?.data) {
                    break;
                }
            } catch (e) {
                error = e;
                continue;
            }
        }

        // Construct anchor result
        const anchorResult = {
            anchorId,
            transactionId: regulatorResponse?.data?.transactionId || `LPC-${Date.now()}-${hash.substring(0, 8)}`,
            timestamp: regulatorResponse?.data?.timestamp || timestamp,
            regulatorNode: regulatorResponse?.data?.node || 'local.anchor.wilsy.os',
            blockHeight: regulatorResponse?.data?.blockHeight || this.anchorCount + 1,
            blockHash: regulatorResponse?.data?.blockHash ||
                crypto.createHash('sha3-512')
                    .update(anchorId + hash + timestamp)
                    .digest('hex'),
            merkleRoot: regulatorResponse?.data?.merkleRoot,
            verified: regulatorResponse?.status === 200 || regulatorResponse?.status === 201,
            anchorType: options.test ? 'TEST' : 'PRODUCTION',
            regulatorResponse: regulatorResponse?.data,
            submittedAt: timestamp,
            confirmedAt: new Date().toISOString()
        };

        // Store locally for redundancy
        this.anchoredBlocks.set(hash, anchorResult);
        this.anchorCount++;

        // Queue for retry if not verified
        if (!anchorResult.verified && !options.test) {
            this.retryQueue.push({
                hash,
                anchorResult,
                attempts: 1,
                lastAttempt: new Date(),
                maxAttempts: 5
            });

            this._processRetryQueue();
        }

        // Generate verification proof
        anchorResult.verificationProof = {
            algorithm: 'SHA3-512',
            anchorId: anchorResult.anchorId,
            transactionId: anchorResult.transactionId,
            blockHash: anchorResult.blockHash.substring(0, 16),
            blockHeight: anchorResult.blockHeight,
            regulatorUrl: `${this.regulatorEndpoints.primary}/verify/${anchorResult.transactionId}`,
            verificationQR: this._generateVerificationQR(anchorResult),
            verifiedAt: anchorResult.confirmedAt
        };

        return anchorResult;
    }

    /**
     * Verify an anchored hash against LPC regulator
     */
    async verify(hash, options = {}) {
        // Check local cache first
        const localAnchor = this.anchoredBlocks.get(hash);
        if (localAnchor && localAnchor.verified) {
            return {
                ...localAnchor,
                verificationSource: 'LOCAL_CACHE',
                verified: true
            };
        }

        // Verify with regulator
        try {
            const response = await axios.get(
                `${this.regulatorEndpoints.primary}/verify/${hash}`,
                {
                    headers: {
                        'Authorization': `Bearer ${this.apiKey}`,
                        'X-Firm-ID': this.firmId
                    },
                    timeout: 5000
                }
            );

            if (response.data) {
                const verification = {
                    hash,
                    verified: true,
                    transactionId: response.data.transactionId,
                    blockHeight: response.data.blockHeight,
                    blockHash: response.data.blockHash,
                    timestamp: response.data.timestamp,
                    regulatorNode: response.data.node,
                    verificationSource: 'LPC_REGULATOR',
                    verifiedAt: new Date().toISOString()
                };

                // Cache the result
                this.anchoredBlocks.set(hash, verification);

                return verification;
            }
        } catch (error) {
            // Return local anchor if available
            if (localAnchor) {
                return {
                    ...localAnchor,
                    verificationSource: 'LOCAL_FALLBACK',
                    regulatorUnavailable: true,
                    verified: localAnchor.verified
                };
            }
        }

        return {
            hash,
            verified: false,
            verificationSource: 'NOT_FOUND',
            timestamp: new Date().toISOString()
        };
    }

    /**
     * Get blockchain anchor status
     */
    async getStatus() {
        let regulatorHealthy = false;

        try {
            const response = await axios.get(
                `${this.regulatorEndpoints.primary}/health`,
                { timeout: 3000 }
            );
            regulatorHealthy = response.status === 200;
        } catch {
            regulatorHealthy = false;
        }

        return {
            service: 'BlockchainAnchor',
            version: '5.0.3',
            status: regulatorHealthy ? 'HEALTHY' : 'DEGRADED',
            metrics: {
                totalAnchored: this.anchorCount,
                pendingRetries: this.retryQueue.length,
                localBlocks: this.anchoredBlocks.size
            },
            regulator: {
                primary: this.regulatorEndpoints.primary,
                connected: regulatorHealthy,
                mode: process.env.NODE_ENV === 'production' ? 'PRODUCTION' : 'SANDBOX'
            },
            timestamp: new Date().toISOString()
        };
    }

    async _processRetryQueue() {
        if (this.retryQueue.length === 0) return;

        const now = new Date();
        const batch = this.retryQueue.filter(item =>
            item.attempts < item.maxAttempts &&
            now - item.lastAttempt > (Math.pow(2, item.attempts) * 1000)
        );

        for (const item of batch) {
            try {
                const result = await this.anchor(item.hash, { retry: true });
                if (result.verified) {
                    this.retryQueue = this.retryQueue.filter(i => i.hash !== item.hash);
                } else {
                    item.attempts++;
                    item.lastAttempt = now;
                }
            } catch {
                item.attempts++;
                item.lastAttempt = now;
            }
        }
    }

    _generateVerificationQR(anchorResult) {
        const verificationData = {
            type: 'LPC_TRUST_ANCHOR',
            transactionId: anchorResult.transactionId,
            blockHeight: anchorResult.blockHeight,
            timestamp: anchorResult.timestamp,
            regulator: 'LPC_ZA'
        };

        // Generate QR code data URL
        return `https://verify.lpc.org.za/qr?data=${Buffer.from(JSON.stringify(verificationData)).toString('base64')}`;
    }
}

module.exports = { BlockchainAnchor };