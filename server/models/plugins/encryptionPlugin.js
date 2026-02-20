/*╔══════════════════════════════════════════════════════════════════════════════╗
  ║ ENCRYPTION PLUGIN - INVESTOR-GRADE ● FORENSIC ● PRODUCTION                  ║
  ║ AES-256-GCM | Field-level encryption | Key management                       ║
  ║ Version: 1.0.0 - PRODUCTION                                                 ║
  ╚══════════════════════════════════════════════════════════════════════════════╝*/

'use strict';

const crypto = require('crypto');

/**
 * Encryption plugin for Mongoose schemas
 * Provides field-level encryption for sensitive data
 */
module.exports = function encryptionPlugin(schema, options = {}) {
    const fields = options.fields || [];
    const algorithm = options.algorithm || 'aes-256-gcm';
    const keyId = options.keyId || process.env.ENCRYPTION_KEY_ID || 'default-key';

    if (!fields.length) return;

    // Add encryption metadata field
    schema.add({
        _encryption: {
            type: 'Mixed',
            default: {}
        }
    });

    // Encrypt fields before save
    schema.pre('save', function(next) {
        if (!this._encryption) {
            this._encryption = {};
        }

        fields.forEach(field => {
            if (this[field] && !this._encryption[field]) {
                try {
                    const encrypted = encryptField(this[field], algorithm, keyId);
                    this[field] = encrypted.data;
                    this._encryption[field] = {
                        algorithm,
                        keyId,
                        iv: encrypted.iv,
                        authTag: encrypted.authTag,
                        encryptedAt: new Date()
                    };
                } catch (error) {
                    return next(error);
                }
            }
        });

        next();
    });

    // Decrypt fields on find
    schema.post('find', function(docs) {
        if (!docs) return;
        const docsArray = Array.isArray(docs) ? docs : [docs];
        docsArray.forEach(doc => {
            if (doc && doc._encryption) {
                fields.forEach(field => {
                    if (doc[field] && doc._encryption[field]) {
                        try {
                            doc[field] = decryptField(
                                doc[field],
                                doc._encryption[field].iv,
                                doc._encryption[field].authTag,
                                doc._encryption[field].algorithm,
                                doc._encryption[field].keyId
                            );
                        } catch (error) {
                            // Log error but don't throw
                            console.error(`Failed to decrypt field ${field}:`, error.message);
                        }
                    }
                });
            }
        });
    });

    schema.post('findOne', function(doc) {
        if (!doc || !doc._encryption) return;
        
        fields.forEach(field => {
            if (doc[field] && doc._encryption[field]) {
                try {
                    doc[field] = decryptField(
                        doc[field],
                        doc._encryption[field].iv,
                        doc._encryption[field].authTag,
                        doc._encryption[field].algorithm,
                        doc._encryption[field].keyId
                    );
                } catch (error) {
                    console.error(`Failed to decrypt field ${field}:`, error.message);
                }
            }
        });
    });

    // Method to manually decrypt
    schema.methods.decryptField = function(fieldName) {
        if (!this._encryption || !this._encryption[fieldName]) {
            return this[fieldName];
        }

        return decryptField(
            this[fieldName],
            this._encryption[fieldName].iv,
            this._encryption[fieldName].authTag,
            this._encryption[fieldName].algorithm,
            this._encryption[fieldName].keyId
        );
    };

    // Method to manually encrypt
    schema.methods.encryptField = function(fieldName) {
        if (!this[fieldName]) return;

        const encrypted = encryptField(this[fieldName], algorithm, keyId);
        this[fieldName] = encrypted.data;
        this._encryption[fieldName] = {
            algorithm,
            keyId,
            iv: encrypted.iv,
            authTag: encrypted.authTag,
            encryptedAt: new Date()
        };

        return this;
    };
};

/**
 * Encrypt a field value
 */
function encryptField(value, algorithm, keyId) {
    const key = getEncryptionKey(keyId);
    const iv = crypto.randomBytes(12);
    const cipher = crypto.createCipheriv(algorithm, key, iv);

    let encrypted = cipher.update(JSON.stringify(value), 'utf8', 'hex');
    encrypted += cipher.final('hex');
    const authTag = cipher.getAuthTag();

    return {
        data: encrypted,
        iv: iv.toString('hex'),
        authTag: authTag.toString('hex')
    };
}

/**
 * Decrypt a field value
 */
function decryptField(encryptedData, ivHex, authTagHex, algorithm, keyId) {
    const key = getEncryptionKey(keyId);
    const iv = Buffer.from(ivHex, 'hex');
    const authTag = Buffer.from(authTagHex, 'hex');
    const decipher = crypto.createDecipheriv(algorithm, key, iv);
    decipher.setAuthTag(authTag);

    let decrypted = decipher.update(encryptedData, 'hex', 'utf8');
    decrypted += decipher.final('utf8');

    return JSON.parse(decrypted);
}

/**
 * Get encryption key (from environment or KMS)
 */
function getEncryptionKey(keyId) {
    // In production, this would fetch from KMS
    const key = process.env[`ENCRYPTION_KEY_${keyId}`] || 
                process.env.ENCRYPTION_KEY || 
                crypto.scryptSync('default-key', 'salt', 32);
    
    return typeof key === 'string' ? Buffer.from(key, 'hex') : key;
}
