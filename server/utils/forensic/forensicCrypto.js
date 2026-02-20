/*╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
  ║ FORENSIC CRYPTO UTILITIES — PRODUCTION GRADE ● NO CONFLICTS                                                    ║
  ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝*/

const crypto = require('crypto');

// REDACT_FIELDS constant
const REDACT_FIELDS = Object.freeze([
    'password', 'idNumber', 'idnumber', 'saId', 'southAfricanId',
    'email', 'emailAddress', 'phone', 'phoneNumber', 'mobile',
    'cellphone', 'clientName', 'fullName', 'firstName', 'lastName',
    'accountNumber', 'bankAccount', 'creditCard', 'passport'
]);

/**
 * Generate SHA-256 hash
 */
function generateHash(data) {
    if (data === null || data === undefined) {
        throw new Error('generateHash: data cannot be null or undefined');
    }
    const hash = crypto.createHash('sha256');
    hash.update(typeof data === 'object' ? JSON.stringify(data) : String(data));
    return hash.digest('hex');
}

/**
 * Create digital signature
 */
async function createDigitalSignature(payload) {
    if (!payload || typeof payload !== 'object') {
        throw new Error('createDigitalSignature: payload must be an object');
    }
    
    const { privateKey, publicKey } = crypto.generateKeyPairSync('rsa', {
        modulusLength: 2048,
        publicKeyEncoding: { type: 'spki', format: 'pem' },
        privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
    });

    const sign = crypto.createSign('SHA256');
    sign.update(JSON.stringify(payload));
    sign.end();
    
    return {
        value: sign.sign(privateKey, 'hex'),
        algorithm: 'RSA-SHA256',
        timestamp: new Date().toISOString(),
        publicKey
    };
}

/**
 * Verify signature
 */
async function verifySignature(payload, signature, publicKey) {
    if (!payload || !signature || !publicKey) {
        throw new Error('verifySignature: all parameters required');
    }
    
    const verify = crypto.createVerify('SHA256');
    verify.update(JSON.stringify(payload));
    verify.end();
    
    return verify.verify(publicKey, signature, 'hex');
}

/**
 * Redact sensitive data (POPIA compliance)
 */
function redactSensitive(data) {
    if (data === null || data === undefined) return data;
    
    if (typeof data === 'string') {
        for (const field of REDACT_FIELDS) {
            if (data.toLowerCase().includes(field.toLowerCase())) {
                return '[REDACTED]';
            }
        }
        return data;
    }
    
    if (Array.isArray(data)) {
        return data.map(item => redactSensitive(item));
    }
    
    if (typeof data === 'object') {
        const redacted = {};
        for (const [key, value] of Object.entries(data)) {
            if (REDACT_FIELDS.includes(key.toLowerCase())) {
                redacted[key] = '[REDACTED]';
            } else {
                redacted[key] = redactSensitive(value);
            }
        }
        return redacted;
    }
    
    return data;
}

/**
 * Generate random bytes
 */
function generateRandomBytes(size = 32) {
    if (typeof size !== 'number' || size < 1) {
        throw new Error('generateRandomBytes: size must be a positive number');
    }
    return crypto.randomBytes(size).toString('hex');
}

/**
 * Calculate HMAC
 */
function calculateHMAC(data, key) {
    if (!data) throw new Error('calculateHMAC: data required');
    if (!key) throw new Error('calculateHMAC: key required');
    
    const hmac = crypto.createHmac('sha256', key);
    hmac.update(String(data));
    return hmac.digest('hex');
}

module.exports = {
    REDACT_FIELDS,
    generateHash,
    createDigitalSignature,
    verifySignature,
    redactSensitive,
    generateRandomBytes,
    calculateHMAC
};
