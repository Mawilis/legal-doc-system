/**
 * =============================================================================
 * WILSY OS - QUANTUM CRYPTOGRAPHY UTILITY
 * PURPOSE: AES-256-GCM Authenticated Encryption for Legal PII
 * =============================================================================
 */
const crypto = require('crypto');

const ALGORITHM = 'aes-256-gcm';
const IV_LENGTH = 12; // Standard for GCM
const AUTH_TAG_LENGTH = 16;

/**
 * Encrypts plain text using a tenant-specific master key
 * @param {string} text - The PII to protect
 * @param {string} secretKey - The 32-byte secret key
 */
exports.encrypt = (text, secretKey) => {
    const iv = crypto.randomBytes(IV_LENGTH);
    const cipher = crypto.createCipheriv(ALGORITHM, Buffer.from(secretKey, 'hex'), iv);
    
    let encrypted = cipher.update(text, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    
    const authTag = cipher.getAuthTag().toString('hex');
    
    // Return: iv + encryptedData + authTag (Self-contained package)
    return `${iv.toString('hex')}:${encrypted}:${authTag}`;
};

/**
 * Decrypts the package
 */
exports.decrypt = (ciphertext, secretKey) => {
    const [ivHex, encrypted, authTagHex] = ciphertext.split(':');
    
    const decipher = crypto.createDecipheriv(
        ALGORITHM, 
        Buffer.from(secretKey, 'hex'), 
        Buffer.from(ivHex, 'hex')
    );
    
    decipher.setAuthTag(Buffer.from(authTagHex, 'hex'));
    
    let decrypted = decipher.update(encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    
    return decrypted;
};
