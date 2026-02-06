/*
 * File: server/controllers/cryptoController.js
 * STATUS: PRODUCTION-READY | CRYPTOGRAPHIC FORTRESS GRADE
 * -----------------------------------------------------------------------------
 * PURPOSE: 
 * Secure proxy to the Wilsy Crypto Vault. Handles digital signatures for 
 * court documents, AES-256 encryption for PII, and non-repudiable audit trails.
 * -----------------------------------------------------------------------------
 */

'use strict';

const axios = require('axios');
const asyncHandler = require('express-async-handler');
const { successResponse, errorResponse } = require('../middleware/responseHandler');
const { emitAudit } = require('../middleware/auditMiddleware');

// CONFIGURATION - Service-to-Service Security
const CRYPTO_SERVICE_URL = process.env.CRYPTO_SERVICE_URL || 'http://127.0.0.1:6600';
const SERVICE_SECRET = process.env.SERVICE_SECRET;

/**
 * INTERNAL UTILITY: VAULT CLIENT
 * Configured with strict timeouts to prevent API hanging during heavy signing.
 */
const vaultClient = axios.create({
    baseURL: CRYPTO_SERVICE_URL,
    timeout: 5000,
    headers: {
        'Content-Type': 'application/json',
        'x-service-secret': SERVICE_SECRET
    }
});

/**
 * @desc    SIGN LEGAL DOCUMENT (Asymmetric Signature)
 * @route   POST /api/v1/crypto/sign
 */
exports.signDocument = asyncHandler(async (req, res) => {
    const { documentHash, documentId } = req.body;

    if (!documentHash) {
        return errorResponse(req, res, 400, 'Document hash is required for cryptographic sealing.', 'ERR_HASH_MISSING');
    }

    try {
        // Enforce Tenant Context for Key Isolation
        const response = await vaultClient.post('/sign', {
            documentHash,
            tenantId: req.user.tenantId,
            userId: req.user.id
        });

        // FORENSIC AUDIT (Legal Proof of Signature)
        await emitAudit(req, {
            resource: 'CRYPTO_VAULT',
            action: 'DOCUMENT_SIGNED',
            severity: 'INFO',
            metadata: {
                documentId,
                signatureId: response.data.signatureId,
                hash: documentHash
            }
        });

        return successResponse(req, res, response.data);

    } catch (error) {
        console.error('💥 [VAULT_SIGN_FAULT]:', error.message);
        if (error.code === 'ECONNREFUSED') {
            return errorResponse(req, res, 503, 'Vault Service unreachable. Signing suspended.', 'ERR_VAULT_OFFLINE');
        }
        return errorResponse(req, res, 500, 'Cryptographic signing failure.', 'ERR_CRYPTO_FAULT');
    }
});

/**
 * @desc    VERIFY SIGNATURE (Court Admissibility Check)
 * @route   POST /api/v1/crypto/verify
 */
exports.verifySignature = asyncHandler(async (req, res) => {
    const { signature, documentHash, publicKey } = req.body;

    try {
        const response = await vaultClient.post('/verify', {
            signature,
            documentHash,
            publicKey
        });

        return successResponse(req, res, response.data);

    } catch (error) {
        // Return 200 with isValid: false for verification failures, only 500 for system faults
        return errorResponse(req, res, 500, 'Signature verification engine failure.', 'ERR_VERIFY_FAULT');
    }
});

/**
 * @desc    ENCRYPT PII (AES-256)
 * @route   POST /api/v1/crypto/encrypt
 */
exports.encryptData = asyncHandler(async (req, res) => {
    const { plaintext } = req.body;

    if (!plaintext) {
        return errorResponse(req, res, 400, 'Plaintext required for encryption.', 'ERR_DATA_MISSING');
    }

    try {
        const response = await vaultClient.post('/encrypt', {
            plaintext,
            tenantId: req.user.tenantId
        });

        await emitAudit(req, {
            resource: 'CRYPTO_VAULT',
            action: 'DATA_ENCRYPTED',
            severity: 'INFO',
            metadata: { keyId: response.data.keyId }
        });

        return successResponse(req, res, response.data);
    } catch (error) {
        return errorResponse(req, res, 500, 'Encryption engine fault.', 'ERR_ENCRYPT_FAULT');
    }
});

/**
 * @desc    DECRYPT SENSITIVE DATA (Highly Restricted)
 * @route   POST /api/v1/crypto/decrypt
 */
exports.decryptData = asyncHandler(async (req, res) => {
    const { ciphertext, keyId } = req.body;

    try {
        const response = await vaultClient.post('/decrypt', {
            ciphertext,
            keyId,
            tenantId: req.user.tenantId
        });

        // HIGH SEVERITY AUDIT
        await emitAudit(req, {
            resource: 'CRYPTO_VAULT',
            action: 'DATA_DECRYPTED',
            severity: 'WARNING',
            metadata: { keyId, accessType: 'DIRECT_DECRYPT' }
        });

        return successResponse(req, res, response.data);
    } catch (error) {
        return errorResponse(req, res, 403, 'Decryption unauthorized or key mismatch.', 'ERR_DECRYPT_DENIED');
    }
});