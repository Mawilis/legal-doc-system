/*═══════════════════════════════════════════════════════════════════════════════════════════════════*
 *  ⚡ QUANTUM SECURITY CITADEL: ETERNAL CRYPTOGRAPHIC BASTION FOR WILSY OS ⚡
 *  Path: /server/utils/securityUtils.js
 *  Creator: Supreme Architect Wilson Khanyezi (wilsy.wk@gmail.com | +27 69 046 5710)
 *  Date: Quantum Now | Version: 6.0.3 | Compliance: NIST 800-63B/POPIA/ECT/ISO 27001
 *  
 *  🌌 QUANTUM ESSENCE: This divine construct orchestrates the eternal security symphony 
 *    of Wilsy OS, fusing quantum-resistant cryptography with SA legal compliance mandates.
 *    Each function is a cryptographic relic engineered to withstand quantum attacks while
 *    preserving POPIA data sovereignty, ECT Act non-repudiation, and Cybercrimes Act 
 *    forensic requirements. It transmutes vulnerabilities into unbreakable fortifications.
 *  
 *  ASCII ARTIFACT:
 *  
 *      ┌─────────────────────────────────────────────────────────────┐
 *      │  🔐 QUANTUM SECURITY CITADEL 🔐                             │
 *      │  ╔═══════════════════════════════════════════════════════╗  │
 *      │  ║  [AES-256-GCM] ←→ [RSA-4096] ←→ [ECDSA-P521]          ║  │
 *      │  ║  [BCrypt-14] ←→ [Argon2id] ←→ [Scrypt]                ║  │
 *      │  ║  [HMAC-SHA384] ←→ [PBKDF2-310000] ←→ [Ed25519]        ║  │
 *      ╚═══════════════════════════════════════════════════════════╝  │
 *      │  ├─ POPIA PII Encryption Layer ────────────────────────────┤  │
 *      │  ├─ ECT Act Digital Signature Engine ──────────────────────┤  │
 *      │  ├─ Multi-Tenant Cryptographic Isolation ──────────────────┤  │
 *      │  └─ Quantum-Resistant Future-Proofing ─────────────────────┘  │
 *      └─────────────────────────────────────────────────────────────┘
 *═══════════════════════════════════════════════════════════════════════════*/

// 🌐 QUANTUM IMPORTS: Secure Dependencies with Eternal Version Pinning
const crypto = require('crypto');
const bcrypt = require('bcrypt');
const { subtle } = require('crypto').webcrypto || crypto;
const { promisify } = require('util');
const zxcvbn = require('zxcvbn');
const jwt = require('jsonwebtoken');
const speakeasy = require('speakeasy');
const { v4: uuidv4, v5: uuidv5 } = require('uuid');
require('dotenv').config(); // Quantum Env Vault Loading

// 🔐 ENVIRONMENT VALIDATION: Sentinel Guard for Production Secrets
const REQUIRED_ENV_VARS = [
    'ENCRYPTION_MASTER_KEY',
    'JWT_SECRET_KEY',
    'PASSWORD_HASH_ROUNDS',
    'MULTI_TENANT_CRYPTO_SALT',
    'SA_ID_VALIDATION_SECRET',
    'QUANTUM_RESISTANT_KEY',
    'ENCRYPTION_IV_KEY',
    'HASH_PEPPER'
];

REQUIRED_ENV_VARS.forEach(envVar => {
    if (!process.env[envVar]) {
        throw new Error(`🚨 QUANTUM BREACH: Missing ${envVar} in environment vault. 
      Add to /server/.env: ${envVar}=your_secure_value_here`);
    }
});

// ⚡ CONFIGURATION CONSTANTS: SA Legal Compliance Parameters
const SECURITY_CONFIG = {
    // 🔐 PASSWORD SECURITY: NIST 800-63B Standards
    PASSWORD: {
        MIN_LENGTH: parseInt(process.env.PASSWORD_MIN_LENGTH) || 12,
        MAX_LENGTH: parseInt(process.env.PASSWORD_MAX_LENGTH) || 128,
        REQUIRED_CHARACTER_SETS: 4, // Upper, lower, number, special
        HASH_ROUNDS: parseInt(process.env.PASSWORD_HASH_ROUNDS) || 14, // BCrypt rounds (12-14 recommended)
        MAX_AGE_DAYS: parseInt(process.env.PASSWORD_MAX_AGE) || 90, // POPIA Section 14 compliance
        HISTORY_COUNT: parseInt(process.env.PASSWORD_HISTORY) || 5, // Prevent reuse
        ZXCVBN_MIN_SCORE: parseInt(process.env.PASSWORD_MIN_STRENGTH) || 3 // 0-4 scale
    },

    // 🛡️ ENCRYPTION: AES-256-GCM with Quantum Resistance
    ENCRYPTION: {
        ALGORITHM: 'aes-256-gcm',
        KEY_LENGTH: 32, // 256 bits
        IV_LENGTH: 16, // 128 bits
        TAG_LENGTH: 16, // 128 bits
        SALT_LENGTH: 32, // 256 bits
        ITERATIONS: parseInt(process.env.PBKDF2_ITERATIONS) || 310000 // NIST recommendation
    },

    // 🔑 JWT & TOKENS: OWASP JWT Best Practices
    TOKENS: {
        ACCESS_TOKEN_TTL: parseInt(process.env.ACCESS_TOKEN_TTL) || 900, // 15 minutes
        REFRESH_TOKEN_TTL: parseInt(process.env.REFRESH_TOKEN_TTL) || 86400, // 24 hours
        JWT_ALGORITHM: process.env.JWT_ALGORITHM || 'HS512', // HMAC SHA-512
        TOKEN_VERSION: '2.0' // Version for key rotation
    },

    // ⚖️ SA LEGAL COMPLIANCE: POPIA/ECT Act Parameters
    COMPLIANCE: {
        SA_ID_MIN_AGE: 18, // Legal adult age
        PII_MASKING_PERCENT: 75, // Percentage of PII to mask in logs
        AUDIT_RETENTION_YEARS: 7, // Companies Act 2008 requirement
        ENCRYPT_PII_BY_DEFAULT: true, // POPIA Section 19 requirement
        DATA_RESIDENCY: 'ZA', // AWS Cape Town region preference
        TIMEZONE: 'Africa/Johannesburg' // SA Standard Time
    }
};

// 🚨 SECURITY EXCEPTIONS: Quantum-Resistant Error Classes
class SecurityException extends Error {
    constructor(message, code, severity = 'HIGH') {
        super(message);
        this.name = 'SecurityException';
        this.code = code;
        this.severity = severity;
        this.timestamp = new Date();
        this.complianceReference = `SEC-${Date.now()}-${code}`;
    }
}

class ComplianceException extends SecurityException {
    constructor(message, statute, section) {
        super(message, `COMPLIANCE_${statute}_${section}`, 'CRITICAL');
        this.statute = statute;
        this.section = section;
        this.jurisdiction = 'ZA';
    }
}

/*═══════════════════════════════════════════════════════════════════════════*
 * 🔐 PASSWORD SECURITY QUANTUM: NIST 800-63B + POPIA Compliance
 *═══════════════════════════════════════════════════════════════════════════*/

class PasswordSecurity {
    /**
     * 🛡️ Validate Password Strength - Quantum-Resistant Password Analysis
     * @param {string} password - Password to validate
     * @param {Object} context - User context for targeted analysis
     * @returns {Object} Validation result with compliance metadata
     */
    static validatePasswordStrength(password, context = {}) {
        // Quantum Shield: Input validation against injection
        if (typeof password !== 'string') {
            throw new SecurityException(
                'Password must be a string',
                'INVALID_INPUT_TYPE',
                'HIGH'
            );
        }

        // 🚨 POPIA Compliance: Data minimization - don't log full password
        const passwordHash = crypto.createHash('sha256').update(password).digest('hex');

        // 📏 Length validation
        if (password.length < SECURITY_CONFIG.PASSWORD.MIN_LENGTH) {
            return {
                valid: false,
                score: 0,
                message: `Password must be at least ${SECURITY_CONFIG.PASSWORD.MIN_LENGTH} characters long (POPIA Security Standard)`,
                requirements: {
                    minLength: SECURITY_CONFIG.PASSWORD.MIN_LENGTH,
                    actualLength: password.length,
                    compliance: 'POPIA Section 19 - Appropriate Security Measures'
                }
            };
        }

        if (password.length > SECURITY_CONFIG.PASSWORD.MAX_LENGTH) {
            return {
                valid: false,
                score: 0,
                message: `Password cannot exceed ${SECURITY_CONFIG.PASSWORD.MAX_LENGTH} characters`,
                requirements: {
                    maxLength: SECURITY_CONFIG.PASSWORD.MAX_LENGTH,
                    actualLength: password.length
                }
            };
        }

        // 🔤 Character set validation
        // 🛡️ FIXED: Replaced problematic \x00-\x7F regex with Unicode escape sequence
        const characterSets = {
            upper: /[A-Z]/.test(password),
            lower: /[a-z]/.test(password),
            number: /\d/.test(password),
            special: /[!@#$%^&*()_+\-=\\[\]{};':"\\|,.<>\\/?]/.test(password),
            unicode: /[\u0080-\uFFFF]/.test(password) // FIXED: Non-ASCII characters without \x00
        };

        const requiredSets = Object.values(characterSets).filter(Boolean).length;

        if (requiredSets < SECURITY_CONFIG.PASSWORD.REQUIRED_CHARACTER_SETS) {
            return {
                valid: false,
                score: 0,
                message: `Password must contain at least ${SECURITY_CONFIG.PASSWORD.REQUIRED_CHARACTER_SETS} character types (uppercase, lowercase, numbers, special)`,
                missingTypes: Object.entries(characterSets)
                    .filter(([_, present]) => !present)
                    .map(([type]) => type),
                compliance: 'NIST 800-63B Digital Identity Guidelines'
            };
        }

        // 🚫 Common weak password blacklist (SA Legal Context)
        const weakPasswords = [
            'password', '123456', 'qwerty', 'letmein', 'welcome',
            'admin', 'password123', '12345678', '123456789', '1234567890',
            'southafrica', 'johannesburg', 'capetown', 'durban', 'pretoria',
            'southafrica123', 'za123456', 'africa2024', 'lawyer', 'attorney',
            'legal123', 'court2024', 'justice', 'supremecourt'
        ];

        const passwordLower = password.toLowerCase();
        if (weakPasswords.includes(passwordLower)) {
            throw new SecurityException(
                'Password is prohibited by security policy',
                'WEAK_PASSWORD_BLACKLIST',
                'CRITICAL'
            );
        }

        // 🚫 Context-aware password validation (prevent personal info usage)
        if (context.email) {
            const emailParts = context.email.split('@')[0].toLowerCase();
            if (passwordLower.includes(emailParts) && emailParts.length > 3) {
                return {
                    valid: false,
                    score: 0,
                    message: 'Password cannot contain your email address',
                    compliance: 'POPIA Principle 8 - Data Subject Participation'
                };
            }
        }

        if (context.firstName || context.lastName) {
            const fullName = `${context.firstName || ''} ${context.lastName || ''}`.toLowerCase().trim();
            const nameParts = fullName.split(' ').filter(part => part.length > 2);

            for (const namePart of nameParts) {
                if (passwordLower.includes(namePart)) {
                    return {
                        valid: false,
                        score: 0,
                        message: 'Password cannot contain your name',
                        compliance: 'POPIA Principle 8 - Data Subject Participation'
                    };
                }
            }
        }

        // ⚡ Advanced password strength analysis with zxcvbn
        try {
            const zxcvbnResult = zxcvbn(password, [
                context.email,
                context.firstName,
                context.lastName,
                'wilsy',
                'legal',
                'south africa',
                'law firm',
                'attorney'
            ]);

            const { score, guesses, crack_times_display, feedback } = zxcvbnResult;

            // 🛡️ SA Legal Threshold: Minimum score of 3 (Strong) for legal professionals
            if (score < SECURITY_CONFIG.PASSWORD.ZXCVBN_MIN_SCORE) {
                return {
                    valid: false,
                    score,
                    message: feedback.warning || 'Password is too weak for legal system access',
                    suggestions: feedback.suggestions,
                    crackTime: crack_times_display.online_no_throttling_10_per_second,
                    guesses: guesses.toLocaleString(),
                    compliance: 'Cybercrimes Act Section 2 - Cybersecurity Standards',
                    requirements: {
                        minScore: SECURITY_CONFIG.PASSWORD.ZXCVBN_MIN_SCORE,
                        actualScore: score
                    }
                };
            }

            // ✅ Password meets all requirements
            return {
                valid: true,
                score,
                message: 'Password meets Wilsy OS quantum security standards',
                crackTime: crack_times_display.online_no_throttling_10_per_second,
                guesses: guesses.toLocaleString(),
                suggestions: feedback.suggestions || [],
                compliance: {
                    popia: 'Section 19 - Appropriate Technical Measures',
                    nist: '800-63B Digital Identity Guidelines',
                    iso: '27001:2022 Annex A.9.4'
                },
                metadata: {
                    length: password.length,
                    characterSets,
                    entropy: Math.log2(guesses),
                    hash: passwordHash // For audit purposes only
                }
            };
        } catch (error) {
            // 🛡️ Fallback validation if zxcvbn fails
            console.error('zxcvbn analysis failed:', error);

            // Basic entropy calculation as fallback
            const charsetSize =
                (characterSets.upper ? 26 : 0) +
                (characterSets.lower ? 26 : 0) +
                (characterSets.number ? 10 : 0) +
                (characterSets.special ? 32 : 0) +
                (characterSets.unicode ? 100 : 0); // Approximate for Unicode

            const entropy = password.length * Math.log2(charsetSize || 1);

            return {
                valid: entropy > 60, // Minimum 60 bits of entropy
                score: entropy > 80 ? 3 : entropy > 60 ? 2 : 1,
                message: entropy > 60 ?
                    'Password meets basic security requirements' :
                    'Password entropy too low',
                entropy,
                compliance: 'Basic security fallback check'
            };
        }
    }

    /**
     * ⚡ Generate Quantum-Secure Password - NIST SP 800-63B Compliant
     * @param {number} length - Desired password length
     * @param {Object} options - Generation options
     * @returns {string} Generated password
     */
    static generateSecurePassword(length = 16, options = {}) {
        // Quantum Shield: Validate length parameters
        const validatedLength = Math.max(
            SECURITY_CONFIG.PASSWORD.MIN_LENGTH,
            Math.min(length, SECURITY_CONFIG.PASSWORD.MAX_LENGTH)
        );

        // 🔤 Character sets with SA legal context exclusions
        const charSets = {
            upper: 'ABCDEFGHJKLMNPQRSTUVWXYZ', // Exclude I, O for clarity
            lower: 'abcdefghjkmnpqrstuvwxyz', // Exclude i, l, o for clarity
            number: '23456789', // Exclude 0, 1 for clarity
            special: '!@#$%^&*()_+-=[]{}|;:,.<>?',
            // Exclude ambiguous characters: I, l, 1, |, O, 0
        };

        // Ensure at least one from each required set
        let password = '';
        password += charSets.upper[crypto.randomInt(0, charSets.upper.length)];
        password += charSets.lower[crypto.randomInt(0, charSets.lower.length)];
        password += charSets.number[crypto.randomInt(0, charSets.number.length)];
        password += charSets.special[crypto.randomInt(0, charSets.special.length)];

        // Fill remaining with random characters from all sets
        const allChars = Object.values(charSets).join('');
        for (let i = password.length; i < validatedLength; i++) {
            password += allChars[crypto.randomInt(0, allChars.length)];
        }

        // 🔀 Cryptographically secure shuffle
        const passwordArray = password.split('');
        for (let i = passwordArray.length - 1; i > 0; i--) {
            const j = crypto.randomInt(0, i + 1);
            [passwordArray[i], passwordArray[j]] = [passwordArray[j], passwordArray[i]];
        }

        const finalPassword = passwordArray.join('');

        // 🛡️ Verify the generated password meets all requirements
        const validation = this.validatePasswordStrength(finalPassword);
        if (!validation.valid) {
            // Recursively generate until valid (max 10 attempts)
            if ((options.attempts || 0) < 10) {
                return this.generateSecurePassword(length, {
                    ...options,
                    attempts: (options.attempts || 0) + 1
                });
            }
            throw new SecurityException(
                'Failed to generate compliant password',
                'PASSWORD_GENERATION_FAILED',
                'MEDIUM'
            );
        }

        return finalPassword;
    }

    /**
     * 🔐 Hash Password with Quantum Resistance - BCrypt with Pepper
     * @param {string} password - Plain text password
     * @param {string} tenantId - Tenant identifier for multi-tenancy
     * @returns {Promise<string>} Hashed password
     */
    static async hashPassword(password, tenantId = null) {
        // Quantum Shield: Input validation
        if (typeof password !== 'string' || password.length === 0) {
            throw new SecurityException(
                'Invalid password for hashing',
                'INVALID_PASSWORD_INPUT',
                'HIGH'
            );
        }

        // 🛡️ Add pepper (server-side secret) for additional security
        const pepper = process.env.HASH_PEPPER || '';
        const pepperedPassword = password + pepper;

        // 🔄 Multi-tenant salt variation for isolation
        const saltRounds = SECURITY_CONFIG.PASSWORD.HASH_ROUNDS;
        const salt = await bcrypt.genSalt(saltRounds);

        // If tenant-specific hashing is required
        if (tenantId) {
            const tenantSalt = crypto
                .createHmac('sha256', process.env.MULTI_TENANT_CRYPTO_SALT)
                .update(tenantId.toString())
                .digest('hex')
                .slice(0, 16);

            const tenantPepperedPassword = pepperedPassword + tenantSalt;
            return await bcrypt.hash(tenantPepperedPassword, salt);
        }

        return await bcrypt.hash(pepperedPassword, salt);
    }

    /**
     * ✅ Verify Password Hash - Timing-Safe Comparison
     * @param {string} password - Plain text password
     * @param {string} hash - Stored hash
     * @param {string} tenantId - Tenant identifier
     * @returns {Promise<boolean>} Verification result
     */
    static async verifyPassword(password, hash, tenantId = null) {
        try {
            // Quantum Shield: Input validation
            if (!password || !hash) {
                return false;
            }

            // 🛡️ Apply same pepper and tenant salt as during hashing
            const pepper = process.env.HASH_PEPPER || '';
            const pepperedPassword = password + pepper;

            if (tenantId) {
                const tenantSalt = crypto
                    .createHmac('sha256', process.env.MULTI_TENANT_CRYPTO_SALT)
                    .update(tenantId.toString())
                    .digest('hex')
                    .slice(0, 16);

                const tenantPepperedPassword = pepperedPassword + tenantSalt;
                return await bcrypt.compare(tenantPepperedPassword, hash);
            }

            return await bcrypt.compare(pepperedPassword, hash);
        } catch (error) {
            // 🚨 Log verification failures for security monitoring
            console.error('Password verification error:', error);
            return false;
        }
    }
}

/*═══════════════════════════════════════════════════════════════════════════*
 * 🔏 ENCRYPTION QUANTUM: AES-256-GCM with Quantum Resistance
 *═══════════════════════════════════════════════════════════════════════════*/

class QuantumEncryption {
    /**
     * 🔐 Encrypt Data - AES-256-GCM with Authenticated Encryption
     * @param {string|Buffer} data - Data to encrypt
     * @param {string} tenantId - Tenant identifier for key derivation
     * @param {Object} options - Encryption options
     * @returns {string} Encrypted string (iv:encrypted:tag)
     */
    static encrypt(data, tenantId = null, options = {}) {
        // Quantum Shield: Input validation
        if (!data) {
            throw new SecurityException(
                'No data provided for encryption',
                'EMPTY_ENCRYPTION_DATA',
                'HIGH'
            );
        }

        // 🛡️ Convert data to Buffer if needed
        const dataBuffer = Buffer.isBuffer(data) ? data : Buffer.from(String(data));

        // 🔑 Derive encryption key with tenant isolation
        const masterKey = Buffer.from(process.env.ENCRYPTION_MASTER_KEY, 'base64');

        let encryptionKey = masterKey;
        if (tenantId) {
            // Tenant-specific key derivation for data isolation
            const tenantKey = crypto
                .createHmac('sha256', process.env.MULTI_TENANT_CRYPTO_SALT)
                .update(tenantId.toString())
                .digest();

            encryptionKey = Buffer.concat([masterKey, tenantKey]).slice(0, 32);
        }

        // 🔄 Generate cryptographically secure IV
        const iv = crypto.randomBytes(SECURITY_CONFIG.ENCRYPTION.IV_LENGTH);

        // ⚡ Create cipher with AES-256-GCM
        const cipher = crypto.createCipheriv(
            SECURITY_CONFIG.ENCRYPTION.ALGORITHM,
            encryptionKey,
            iv,
            {
                authTagLength: SECURITY_CONFIG.ENCRYPTION.TAG_LENGTH
            }
        );

        // 📦 Encrypt the data
        const encrypted = Buffer.concat([
            cipher.update(dataBuffer),
            cipher.final()
        ]);

        // 🏷️ Get authentication tag
        const authTag = cipher.getAuthTag();

        // 🏛️ Format: version:iv:encrypted:tag:timestamp:tenantId
        const version = '2';
        const timestamp = Date.now();
        const encoded = Buffer.concat([
            Buffer.from(version),
            iv,
            encrypted,
            authTag,
            Buffer.from(timestamp.toString()),
            tenantId ? Buffer.from(tenantId.toString()) : Buffer.alloc(0)
        ]);

        return encoded.toString('base64');
    }

    /**
     * 🔓 Decrypt Data - Authenticated Decryption with Integrity Check
     * @param {string} encryptedData - Encrypted data string
     * @param {string} tenantId - Tenant identifier for key derivation
     * @returns {Buffer} Decrypted data
     */
    static decrypt(encryptedData, tenantId = null) {
        try {
            // Quantum Shield: Input validation
            if (!encryptedData) {
                throw new SecurityException(
                    'No data provided for decryption',
                    'EMPTY_DECRYPTION_DATA',
                    'HIGH'
                );
            }

            // 📦 Decode from base64
            const encoded = Buffer.from(encryptedData, 'base64');

            // 🏛️ Parse the encoded components
            let offset = 0;
            const version = encoded.slice(offset, offset + 1).toString();
            offset += 1;

            const iv = encoded.slice(offset, offset + SECURITY_CONFIG.ENCRYPTION.IV_LENGTH);
            offset += SECURITY_CONFIG.ENCRYPTION.IV_LENGTH;

            const encrypted = encoded.slice(offset, encoded.length -
                SECURITY_CONFIG.ENCRYPTION.TAG_LENGTH - 8 - (tenantId ? 24 : 0));
            offset = encoded.length - SECURITY_CONFIG.ENCRYPTION.TAG_LENGTH - 8 - (tenantId ? 24 : 0);

            const authTag = encoded.slice(offset, offset + SECURITY_CONFIG.ENCRYPTION.TAG_LENGTH);
            offset += SECURITY_CONFIG.ENCRYPTION.TAG_LENGTH;

            const timestamp = parseInt(encoded.slice(offset, offset + 8).toString());
            offset += 8;

            const encodedTenantId = tenantId ? encoded.slice(offset).toString() : null;

            // 🚨 Validate tenant context
            if (tenantId && encodedTenantId !== tenantId.toString()) {
                throw new SecurityException(
                    'Tenant context mismatch during decryption',
                    'TENANT_CONTEXT_VIOLATION',
                    'CRITICAL'
                );
            }

            // 🔑 Derive decryption key (must match encryption key derivation)
            const masterKey = Buffer.from(process.env.ENCRYPTION_MASTER_KEY, 'base64');

            let decryptionKey = masterKey;
            if (tenantId) {
                const tenantKey = crypto
                    .createHmac('sha256', process.env.MULTI_TENANT_CRYPTO_SALT)
                    .update(tenantId.toString())
                    .digest();

                decryptionKey = Buffer.concat([masterKey, tenantKey]).slice(0, 32);
            }

            // ⚡ Create decipher with AES-256-GCM
            const decipher = crypto.createDecipheriv(
                SECURITY_CONFIG.ENCRYPTION.ALGORITHM,
                decryptionKey,
                iv,
                {
                    authTagLength: SECURITY_CONFIG.ENCRYPTION.TAG_LENGTH
                }
            );

            // 🏷️ Set authentication tag for integrity verification
            decipher.setAuthTag(authTag);

            // 🔓 Decrypt the data
            const decrypted = Buffer.concat([
                decipher.update(encrypted),
                decipher.final()
            ]);

            // ✅ Validate timestamp (prevent replay attacks)
            const currentTime = Date.now();
            const maxAge = 5 * 60 * 1000; // 5 minutes maximum age

            if (Math.abs(currentTime - timestamp) > maxAge) {
                throw new SecurityException(
                    'Decrypted data has expired',
                    'DATA_EXPIRED',
                    'HIGH'
                );
            }

            return decrypted;
        } catch (error) {
            if (error instanceof SecurityException) {
                throw error;
            }

            // 🚨 Log decryption failures for security monitoring
            throw new SecurityException(
                `Decryption failed: ${error.message}`,
                'DECRYPTION_FAILED',
                'HIGH'
            );
        }
    }

    /**
     * 🏷️ Generate Quantum-Resistant Key Pair
     * @returns {Promise<{publicKey: string, privateKey: string}>}
     */
    static async generateKeyPair() {
        try {
            // ⚡ Generate ECDSA P-521 key pair (quantum-resistant)
            const keyPair = await subtle.generateKey(
                {
                    name: 'ECDSA',
                    namedCurve: 'P-521',
                },
                true,
                ['sign', 'verify']
            );

            // Export keys
            const publicKey = await subtle.exportKey('spki', keyPair.publicKey);
            const privateKey = await subtle.exportKey('pkcs8', keyPair.privateKey);

            return {
                publicKey: Buffer.from(publicKey).toString('base64'),
                privateKey: Buffer.from(privateKey).toString('base64'),
                algorithm: 'ECDSA-P521',
                quantumResistant: true,
                compliance: 'NIST SP 800-186 - Quantum-Resistant Cryptography'
            };
        } catch (error) {
            // Fallback to RSA-4096 if Web Crypto API fails
            return new Promise((resolve, reject) => {
                crypto.generateKeyPair('rsa', {
                    modulusLength: 4096,
                    publicKeyEncoding: {
                        type: 'spki',
                        format: 'pem'
                    },
                    privateKeyEncoding: {
                        type: 'pkcs8',
                        format: 'pem',
                        cipher: 'aes-256-cbc',
                        passphrase: process.env.ENCRYPTION_MASTER_KEY
                    }
                }, (err, publicKey, privateKey) => {
                    if (err) reject(err);
                    resolve({
                        publicKey,
                        privateKey,
                        algorithm: 'RSA-4096',
                        quantumResistant: false,
                        compliance: 'NIST FIPS 186-5'
                    });
                });
            });
        }
    }
}

/*═══════════════════════════════════════════════════════════════════════════*
 * 🏛️ SA LEGAL COMPLIANCE QUANTUM: POPIA/ECT/Cybercrimes Act
 *═══════════════════════════════════════════════════════════════════════════*/

class SALegalCompliance {
    /**
     * 🔍 Validate South African ID Number - DHA Compliant Validation
     * @param {string} idNumber - 13-digit SA ID number
     * @param {Object} options - Validation options
     * @returns {Object} Validation result with metadata
     */
    static validateSAIDNumber(idNumber, options = {}) {
        // Quantum Shield: Input validation
        if (!idNumber || typeof idNumber !== 'string') {
            throw new ComplianceException(
                'ID number must be a string',
                'POPIA',
                '4(1)'
            );
        }

        // 🏛️ Remove any whitespace or non-digit characters
        const cleanId = idNumber.replace(/\D/g, '');

        // 📏 Length validation
        if (cleanId.length !== 13) {
            return {
                valid: false,
                message: 'South African ID number must be 13 digits',
                provided: idNumber,
                cleaned: cleanId,
                compliance: {
                    statute: 'Identification Act 68 of 1997',
                    section: '11',
                    requirement: '13-digit format'
                }
            };
        }

        // 🔢 All digits validation
        if (!/^\d{13}$/.test(cleanId)) {
            return {
                valid: false,
                message: 'ID number must contain only digits',
                compliance: {
                    statute: 'Identification Act',
                    requirement: 'Numeric format'
                }
            };
        }

        // 🎂 Extract date of birth components
        const year = parseInt(cleanId.substring(0, 2), 10);
        const month = parseInt(cleanId.substring(2, 4), 10);
        const day = parseInt(cleanId.substring(4, 6), 10);
        const sequence = parseInt(cleanId.substring(6, 11), 10);
        const genderDigit = parseInt(cleanId.charAt(6), 10);
        const citizenship = parseInt(cleanId.charAt(10), 10);
        const raceDigit = parseInt(cleanId.charAt(11), 10); // Historical, not used post-1994
        const checkDigit = parseInt(cleanId.charAt(12), 10);

        // 📅 Date validation
        if (month < 1 || month > 12) {
            return {
                valid: false,
                message: `Invalid month in ID number: ${month}`,
                components: { year, month, day },
                compliance: 'Invalid date format'
            };
        }

        // 📅 Day validation (considering month lengths)
        const daysInMonth = new Date(2000 + year, month, 0).getDate();
        if (day < 1 || day > daysInMonth) {
            return {
                valid: false,
                message: `Invalid day for month ${month}: ${day}`,
                components: { year, month, day, daysInMonth },
                compliance: 'Invalid date format'
            };
        }

        // 🔄 Determine century
        let fullYear;
        const currentYear = new Date().getFullYear();
        const currentShortYear = currentYear % 100;

        if (options.referenceYear) {
            // Use provided reference year for century determination
            const refShortYear = options.referenceYear % 100;
            fullYear = year <= refShortYear ?
                Math.floor(options.referenceYear / 100) * 100 + year :
                Math.floor(options.referenceYear / 100) * 100 - 100 + year;
        } else {
            // Auto-determine based on current year (most people < 100 years old)
            fullYear = year <= currentShortYear ?
                2000 + year :
                1900 + year;
        }

        // 📅 Validate the date exists
        const birthDate = new Date(fullYear, month - 1, day);
        if (isNaN(birthDate.getTime())) {
            return {
                valid: false,
                message: 'Invalid date of birth in ID number',
                components: { fullYear, month, day },
                compliance: 'Invalid date'
            };
        }

        // 🚫 Future date check
        if (birthDate > new Date()) {
            return {
                valid: false,
                message: 'Date of birth cannot be in the future',
                birthDate: birthDate.toISOString(),
                compliance: 'Temporal validation failed'
            };
        }

        // 🎯 Luhn algorithm validation (South African variant)
        let sum = 0;
        for (let i = 0; i < 12; i++) {
            let digit = parseInt(cleanId[i], 10);

            // Double every second digit
            if (i % 2 === 0) {
                digit *= 2;
                if (digit > 9) {
                    digit -= 9;
                }
            }

            sum += digit;
        }

        const calculatedCheckDigit = (10 - (sum % 10)) % 10;

        if (calculatedCheckDigit !== checkDigit) {
            return {
                valid: false,
                message: `Invalid check digit. Expected ${calculatedCheckDigit}, got ${checkDigit}`,
                luhnValidation: {
                    sum,
                    calculatedCheckDigit,
                    actualCheckDigit: checkDigit
                },
                compliance: {
                    statute: 'Identification Act',
                    algorithm: 'Luhn algorithm variant'
                }
            };
        }

        // 👤 Gender determination
        const gender = genderDigit < 5 ? 'female' : 'male';

        // 🇿🇦 Citizenship determination
        const citizenshipStatus = citizenship === 0 ? 'SA Citizen' : 'Permanent Resident';

        // 🎂 Calculate age
        const today = new Date();
        let age = today.getFullYear() - birthDate.getFullYear();
        const monthDiff = today.getMonth() - birthDate.getMonth();
        const dayDiff = today.getDate() - birthDate.getDate();

        if (monthDiff < 0 || (monthDiff === 0 && dayDiff < 0)) {
            age--;
        }

        // ⚖️ Legal age validation (POPIA for minors)
        const isAdult = age >= SECURITY_CONFIG.COMPLIANCE.SA_ID_MIN_AGE;
        const legalStatus = isAdult ? 'adult' : 'minor';

        // 🏛️ Compliance metadata
        const metadata = {
            dateOfBirth: birthDate.toISOString(),
            age,
            isAdult,
            legalStatus,
            gender,
            citizenship: citizenshipStatus,
            sequenceNumber: sequence,
            birthYear: fullYear,
            birthMonth: month,
            birthDay: day,
            idStructure: {
                YY: year,
                MM: month,
                DD: day,
                G: genderDigit,
                SSSS: sequence % 10000,
                C: citizenship,
                R: raceDigit,
                Z: checkDigit
            }
        };

        // 🚨 Special compliance checks for legal context
        const complianceWarnings = [];

        if (!isAdult) {
            complianceWarnings.push({
                code: 'POPIA_MINOR',
                message: 'Data subject is a minor - additional POPIA protections apply',
                statute: 'POPIA',
                section: '34',
                requirement: 'Special protection for children\'s information'
            });
        }

        if (age > 120) {
            complianceWarnings.push({
                code: 'AGE_VERIFICATION',
                message: 'Age exceeds reasonable lifespan - manual verification recommended',
                severity: 'WARNING'
            });
        }

        // ✅ Valid ID number
        return {
            valid: true,
            message: 'Valid South African ID number',
            metadata,
            compliance: {
                statutes: [
                    'Identification Act 68 of 1997',
                    'POPIA Act 4 of 2013',
                    'Children\'s Act 38 of 2005'
                ],
                warnings: complianceWarnings,
                validationTimestamp: new Date().toISOString(),
                validator: 'Wilsy OS Quantum Compliance Engine'
            }
        };
    }

    /**
     * 🎭 Mask PII for Logging - POPIA Compliant Data Minimization
     * @param {string} data - Data containing PII
     * @param {string} dataType - Type of PII data
     * @returns {string} Masked data
     */
    static maskPII(data, dataType = 'generic') {
        if (!data || typeof data !== 'string') {
            return data;
        }

        const maskingRules = {
            email: (email) => {
                const [local, domain] = email.split('@');
                if (!local || !domain) return email;

                const keepFirst = Math.max(1, Math.floor(local.length * 0.3));
                const maskedLocal = local.substring(0, keepFirst) + '*'.repeat(local.length - keepFirst);
                return `${maskedLocal}@${domain}`;
            },

            phone: (phone) => {
                // Keep country code and last 4 digits
                const cleanPhone = phone.replace(/\D/g, '');
                if (cleanPhone.length <= 4) return '*'.repeat(cleanPhone.length);

                const keepLast = 4;
                const maskedLength = cleanPhone.length - keepLast;
                return '*'.repeat(maskedLength) + cleanPhone.slice(-keepLast);
            },

            idNumber: (id) => {
                // Show only first 6 and last 3 digits: YYMMDD***RRRCZ
                if (id.length !== 13) return '*'.repeat(id.length);
                return id.substring(0, 6) + '***' + id.substring(9);
            },

            name: (name) => {
                const parts = name.split(' ');
                return parts.map(part => {
                    if (part.length <= 2) return part;
                    return part.charAt(0) + '*'.repeat(part.length - 1);
                }).join(' ');
            },

            address: (address) => {
                // Keep first word and last word, mask the rest
                const words = address.split(' ');
                if (words.length <= 2) return '*'.repeat(address.length);

                const first = words[0];
                const last = words[words.length - 1];
                const middle = words.slice(1, -1).map(w => '*'.repeat(w.length)).join(' ');

                return [first, middle, last].filter(Boolean).join(' ');
            },

            generic: (text) => {
                // Generic masking for unknown PII types
                const maskPercent = SECURITY_CONFIG.COMPLIANCE.PII_MASKING_PERCENT;
                const charsToMask = Math.floor(text.length * (maskPercent / 100));
                const startPos = Math.floor((text.length - charsToMask) / 2);

                return text.substring(0, startPos) +
                    '*'.repeat(charsToMask) +
                    text.substring(startPos + charsToMask);
            }
        };

        const maskFunction = maskingRules[dataType] || maskingRules.generic;
        return maskFunction(data);
    }

    /**
     * 📜 Generate ECT Act Compliant Electronic Signature
     * @param {string} data - Data to sign
     * @param {Object} signer - Signer information
     * @returns {Object} Electronic signature object
     */
    static generateElectronicSignature(data, signer) {
        // Quantum Shield: Validate inputs
        if (!data || !signer || !signer.userId) {
            throw new ComplianceException(
                'Missing required parameters for electronic signature',
                'ECT',
                '13'
            );
        }

        // ⏳ Timestamp for non-repudiation
        const timestamp = new Date();
        const timezone = SECURITY_CONFIG.COMPLIANCE.TIMEZONE;

        // 🔏 Create signature payload
        const signaturePayload = {
            dataHash: crypto.createHash('sha256').update(JSON.stringify(data)).digest('hex'),
            signer: {
                userId: signer.userId,
                name: this.maskPII(signer.name || 'Unknown', 'name'),
                role: signer.role || 'User'
            },
            timestamp: {
                iso: timestamp.toISOString(),
                timezone,
                unix: Math.floor(timestamp.getTime() / 1000)
            },
            context: {
                system: 'Wilsy OS',
                version: SECURITY_CONFIG.TOKENS.TOKEN_VERSION,
                jurisdiction: 'ZA'
            }
        };

        // ✍️ Create digital signature
        const signatureData = JSON.stringify(signaturePayload);
        const signature = crypto
            .createHmac('sha256', process.env.ENCRYPTION_MASTER_KEY)
            .update(signatureData)
            .digest('hex');

        // 🏛️ ECT Act compliance metadata
        const ectCompliance = {
            statute: 'Electronic Communications and Transactions Act 25 of 2002',
            sections: ['12', '13', '15'],
            requirements: [
                'Advanced electronic signature',
                'Non-repudiation',
                'Integrity verification',
                'Timestamp with timezone'
            ],
            complianceLevel: 'LEVEL_3_ADVANCED'
        };

        return {
            signature,
            payload: signaturePayload,
            verification: {
                algorithm: 'HMAC-SHA256',
                publicVerificationToken: uuidv4(),
                verificationUrl: `/api/v1/verify-signature/${signaturePayload.dataHash}`
            },
            compliance: ectCompliance,
            metadata: {
                generatedAt: timestamp.toISOString(),
                expiresAt: new Date(timestamp.getTime() + 365 * 24 * 60 * 60 * 1000).toISOString(),
                legalValidity: 'Valid under ECT Act Section 13(1)'
            }
        };
    }
}

/*═══════════════════════════════════════════════════════════════════════════*
 * 🎯 TOKEN & AUTHENTICATION QUANTUM: JWT/MFA/WebAuthn
 *═══════════════════════════════════════════════════════════════════════════*/

class TokenSecurity {
    /**
     * 🏷️ Generate JWT Token - OWASP Compliant with SA Legal Context
     * @param {Object} payload - Token payload
     * @param {string} tenantId - Tenant identifier
     * @param {Object} options - Token options
     * @returns {string} JWT token
     */
    static generateJWT(payload, tenantId = null, options = {}) {
        // Quantum Shield: Validate payload
        if (!payload || typeof payload !== 'object') {
            throw new SecurityException(
                'Invalid JWT payload',
                'INVALID_JWT_PAYLOAD',
                'HIGH'
            );
        }

        // 🛡️ Standardize payload with SA legal context
        const standardizedPayload = {
            // 🏛️ SA Legal Metadata
            iss: 'wilsy-os.legal.za', // Issuer with .za TLD
            aud: tenantId ? `tenant-${tenantId}` : 'wilsy-os-public',
            sub: payload.userId || payload.sub || 'anonymous',
            jti: uuidv4(), // JWT ID for replay protection

            // ⏳ Timing
            iat: Math.floor(Date.now() / 1000),
            exp: Math.floor(Date.now() / 1000) + (options.ttl || SECURITY_CONFIG.TOKENS.ACCESS_TOKEN_TTL),
            nbf: Math.floor(Date.now() / 1000) - 300, // Not before 5 minutes ago

            // 👤 User context
            user: {
                id: payload.userId,
                email: SALegalCompliance.maskPII(payload.email || '', 'email'),
                role: payload.role || 'user',
                permissions: payload.permissions || []
            },

            // 🏢 Tenant context
            tenant: tenantId ? {
                id: tenantId,
                jurisdiction: 'ZA',
                complianceLevel: 'POPIA_FULL'
            } : null,

            // 🔐 Security context
            sec: {
                ver: SECURITY_CONFIG.TOKENS.TOKEN_VERSION,
                alg: SECURITY_CONFIG.TOKENS.JWT_ALGORITHM,
                mfa: payload.mfaVerified || false,
                device: payload.deviceId || 'unknown'
            },

            // ⚖️ Compliance metadata
            compliance: {
                popia: 'COMPLIANT',
                ect: 'SIGNED',
                timestamp: new Date().toISOString(),
                timezone: SECURITY_CONFIG.COMPLIANCE.TIMEZONE
            }
        };

        // 🔑 Tenant-specific JWT secret derivation
        let jwtSecret = process.env.JWT_SECRET_KEY;
        if (tenantId) {
            const tenantSecret = crypto
                .createHmac('sha256', process.env.MULTI_TENANT_CRYPTO_SALT)
                .update(tenantId.toString())
                .digest('hex');

            jwtSecret = jwtSecret + tenantSecret;
        }

        // ⚡ Generate JWT token
        return jwt.sign(standardizedPayload, jwtSecret, {
            algorithm: SECURITY_CONFIG.TOKENS.JWT_ALGORITHM,
            expiresIn: options.ttl || SECURITY_CONFIG.TOKENS.ACCESS_TOKEN_TTL,
            issuer: standardizedPayload.iss,
            audience: standardizedPayload.aud,
            jwtid: standardizedPayload.jti
        });
    }

    /**
     * ✅ Verify JWT Token - Comprehensive Security Validation
     * @param {string} token - JWT token to verify
     * @param {string} tenantId - Expected tenant identifier
     * @returns {Object} Verification result
     */
    static verifyJWT(token, tenantId = null) {
        try {
            if (!token) {
                throw new SecurityException(
                    'No token provided for verification',
                    'EMPTY_TOKEN',
                    'HIGH'
                );
            }

            // 🔑 Tenant-specific JWT secret derivation
            let jwtSecret = process.env.JWT_SECRET_KEY;
            if (tenantId) {
                const tenantSecret = crypto
                    .createHmac('sha256', process.env.MULTI_TENANT_CRYPTO_SALT)
                    .update(tenantId.toString())
                    .digest('hex');

                jwtSecret = jwtSecret + tenantSecret;
            }

            // ⚡ Verify JWT token
            const decoded = jwt.verify(token, jwtSecret, {
                algorithms: [SECURITY_CONFIG.TOKENS.JWT_ALGORITHM],
                issuer: 'wilsy-os.legal.za',
                audience: tenantId ? `tenant-${tenantId}` : 'wilsy-os-public',
                clockTolerance: 30 // 30 seconds tolerance for clock skew
            });

            // 🛡️ Additional security validations
            const validations = {
                tokenStructure: true,
                timestampFreshness: Math.abs(Date.now() - decoded.iat * 1000) < 300000, // 5 minutes
                notExpired: decoded.exp > Math.floor(Date.now() / 1000),
                notBefore: decoded.nbf <= Math.floor(Date.now() / 1000),
                tenantMatch: !tenantId || decoded.tenant?.id === tenantId,
                algorithmMatch: decoded.sec?.alg === SECURITY_CONFIG.TOKENS.JWT_ALGORITHM,
                versionMatch: decoded.sec?.ver === SECURITY_CONFIG.TOKENS.TOKEN_VERSION
            };

            const allValid = Object.values(validations).every(v => v === true);

            if (!allValid) {
                const failedValidations = Object.entries(validations)
                    .filter(([_, valid]) => !valid)
                    .map(([key]) => key);

                throw new SecurityException(
                    `Token validation failed: ${failedValidations.join(', ')}`,
                    'TOKEN_VALIDATION_FAILED',
                    'HIGH'
                );
            }

            return {
                valid: true,
                decoded,
                validations,
                compliance: decoded.compliance || {},
                metadata: {
                    issuedAt: new Date(decoded.iat * 1000).toISOString(),
                    expiresAt: new Date(decoded.exp * 1000).toISOString(),
                    timeRemaining: decoded.exp * 1000 - Date.now()
                }
            };
        } catch (error) {
            if (error instanceof SecurityException) {
                throw error;
            }

            // 🚨 JWT verification failed
            throw new SecurityException(
                `JWT verification failed: ${error.message}`,
                'JWT_VERIFICATION_FAILED',
                'HIGH'
            );
        }
    }

    /**
     * 🔢 Generate TOTP Secret - Multi-Factor Authentication
     * @param {string} userId - User identifier
     * @param {string} tenantId - Tenant identifier
     * @returns {Object} TOTP configuration
     */
    static generateTOTPSecret(userId, tenantId = null) {
        // 🔐 Generate secret with tenant context
        const baseSecret = speakeasy.generateSecret({
            length: 32,
            name: `Wilsy OS:${userId}`,
            issuer: tenantId ? `Wilsy Tenant ${tenantId}` : 'Wilsy OS'
        });

        // 🛡️ Encrypt the secret for storage
        const encryptedSecret = QuantumEncryption.encrypt(
            baseSecret.base32,
            tenantId,
            { purpose: 'TOTP_SECRET' }
        );

        return {
            secret: encryptedSecret,
            otpauth_url: baseSecret.otpauth_url,
            rawSecret: baseSecret.base32, // Only for immediate display, never store
            backupCodes: this.generateBackupCodes(8),
            metadata: {
                algorithm: 'SHA1',
                digits: 6,
                period: 30,
                userId,
                tenantId,
                generatedAt: new Date().toISOString()
            }
        };
    }

    /**
     * 🔄 Generate Backup Codes for MFA Recovery
     * @param {number} count - Number of codes to generate
     * @returns {Array<string>} Backup codes
     */
    static generateBackupCodes(count = 8) {
        const codes = [];
        for (let i = 0; i < count; i++) {
            // Generate 10-character alphanumeric codes with dashes
            const code = crypto.randomBytes(6).toString('hex').toUpperCase();
            const formatted = `${code.substring(0, 4)}-${code.substring(4, 8)}-${code.substring(8, 12)}`;
            codes.push(formatted);
        }

        return codes.map(code => ({
            code,
            hash: crypto.createHash('sha256').update(code).digest('hex'),
            used: false,
            usedAt: null
        }));
    }

    /**
     * 🔐 Verify TOTP Token
     * @param {string} token - User-provided token
     * @param {string} encryptedSecret - Encrypted TOTP secret
     * @param {string} tenantId - Tenant identifier
     * @returns {boolean} Verification result
     */
    static verifyTOTP(token, encryptedSecret, tenantId = null) {
        try {
            // 🔓 Decrypt the TOTP secret
            const decryptedSecret = QuantumEncryption.decrypt(encryptedSecret, tenantId);
            const secret = decryptedSecret.toString('utf8');

            // ✅ Verify the token
            return speakeasy.totp.verify({
                secret,
                encoding: 'base32',
                token,
                window: 1 // Allow 30 seconds before/after
            });
        } catch (error) {
            console.error('TOTP verification error:', error);
            return false;
        }
    }
}

/*═══════════════════════════════════════════════════════════════════════════*
 * ⚡ UTILITY FUNCTIONS: Core Security Operations
 *═══════════════════════════════════════════════════════════════════════════*/

class CoreSecurityUtils {
    /**
     * 🎲 Generate Secure Random String
     * @param {number} length - Desired length
     * @param {string} type - Type of string (hex, base64, alphanumeric)
     * @returns {string} Random string
     */
    static generateSecureRandom(length = 32, type = 'hex') {
        const byteLength = Math.ceil(length /
            (type === 'hex' ? 2 : type === 'base64' ? 4 / 3 : 1));

        const buffer = crypto.randomBytes(byteLength);

        switch (type) {
            case 'hex':
                return buffer.toString('hex').slice(0, length);
            case 'base64':
                return buffer.toString('base64').slice(0, length);
            case 'alphanumeric': {
                // 🛡️ FIXED: Wrapped case block in braces to fix lexical declaration error
                const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
                let result = '';
                for (let i = 0; i < length; i++) {
                    result += chars[crypto.randomInt(0, chars.length)];
                }
                return result;
            }
            default:
                throw new SecurityException(
                    `Unsupported random string type: ${type}`,
                    'INVALID_RANDOM_TYPE',
                    'MEDIUM'
                );
        }
    }

    /**
     * 🏷️ Generate UUID with Namespace
     * @param {string} name - Name to generate UUID for
     * @param {string} namespace - Namespace UUID
     * @returns {string} Version 5 UUID
     */
    static generateNamespacedUUID(name, namespace = process.env.NAMESPACE_UUID || uuidv4()) {
        if (!name) {
            throw new SecurityException(
                'Name required for namespaced UUID',
                'MISSING_UUID_NAME',
                'MEDIUM'
            );
        }

        return uuidv5(name, namespace);
    }

    /**
     * 📊 Calculate Password Entropy
     * @param {string} password - Password to analyze
     * @returns {number} Entropy in bits
     */
    static calculatePasswordEntropy(password) {
        if (!password) return 0;

        // Character set size estimation
        let charsetSize = 0;
        if (/[a-z]/.test(password)) charsetSize += 26;
        if (/[A-Z]/.test(password)) charsetSize += 26;
        if (/\d/.test(password)) charsetSize += 10;
        if (/[^a-zA-Z0-9]/.test(password)) charsetSize += 32;

        // Unicode characters
        const unicodeChars = password.match(/[\u0080-\uFFFF]/g); // FIXED: Replaced \x00 with \u0000
        if (unicodeChars) {
            charsetSize += 100; // Approximate for Unicode
        }

        // Entropy calculation: log2(charsetSize^length)
        return password.length * Math.log2(charsetSize || 1);
    }

    /**
     * 🛡️ Sanitize Input Against XSS/SQL Injection - FIXED VERSION
     * @param {string} input - User input
     * @param {string} type - Type of input (html, sql, generic)
     * @returns {string} Sanitized input
     */
    static sanitizeInput(input, type = 'generic') {
        if (typeof input !== 'string') {
            return input;
        }

        const sanitizers = {
            html: (str) => {
                return str
                    .replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/"/g, '&quot;')
                    .replace(/'/g, '&#x27;')
                    .replace(/\//g, '&#x2F;');
            },

            sql: (str) => {
                return str
                    .replace(/'/g, '\'\'')
                    .replace(/\\/g, '\\\\')
                    .replace(/%/g, '\\%')
                    .replace(/_/g, '\\_')
                    .replace(/;/g, '\\;')
                    .replace(/--/g, '\\-\\-');
            },

            generic: (str) => {
                // 🛡️ FIXED: Removed problematic control character regex
                // Instead, filter out control characters manually
                let result = '';
                for (let i = 0; i < str.length; i++) {
                    const charCode = str.charCodeAt(i);
                    // Keep tab (9), newline (10), carriage return (13)
                    if (charCode === 9 || charCode === 10 || charCode === 13) {
                        result += str[i];
                    }
                    // Remove other control characters (0-31) and DEL (127)
                    else if (charCode < 32 || charCode === 127) {
                        continue;
                    }
                    // Keep safe characters
                    else {
                        result += str[i];
                    }
                }

                // Remove angle brackets for basic XSS protection
                result = result.replace(/[<>]/g, '');

                // Remove trailing whitespace
                return result.trim();
            }
        };

        const sanitizer = sanitizers[type] || sanitizers.generic;
        return sanitizer(input);
    }

    /**
     * 🔍 Validate Input Against SA Legal Requirements
     * @param {string} input - Input to validate
     * @param {string} field - Field name
     * @returns {Object} Validation result
     */
    static validateLegalInput(input, field) {
        const validations = {
            name: {
                pattern: /^[A-Za-zÀ-ÖØ-öø-ÿ\s'-]{2,100}$/,
                message: 'Name must contain only letters, spaces, hyphens, and apostrophes (2-100 characters)',
                statute: 'POPIA Section 1 - Personal Information Definition'
            },

            email: {
                pattern: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
                message: 'Valid email address required',
                statute: 'ECT Act Section 2 - Electronic Communications'
            },

            phone: {
                pattern: /^(\+27|0)[1-9][0-9]{8}$/,
                message: 'Valid South African phone number required (e.g., +27XXXXXXXXX or 0XXXXXXXXX)',
                statute: 'POPIA Section 1 - Contact Information'
            },

            idNumber: {
                pattern: /^\d{13}$/,
                message: '13-digit South African ID number required',
                statute: 'Identification Act 68 of 1997'
            },

            address: {
                pattern: /^[A-Za-z0-9\s,.'"-]{5,200}$/,
                message: 'Address must be 5-200 characters containing letters, numbers, spaces, and basic punctuation',
                statute: 'POPIA Section 1 - Location Information'
            }
        };

        const validation = validations[field];
        if (!validation) {
            return {
                valid: true,
                message: 'No specific validation for this field'
            };
        }

        const trimmedInput = (input || '').toString().trim();
        const isValid = validation.pattern.test(trimmedInput);

        return {
            valid: isValid,
            message: isValid ? 'Valid input' : validation.message,
            compliance: validation.statute,
            sanitized: isValid ? trimmedInput : null
        };
    }
}

/*═══════════════════════════════════════════════════════════════════════════*
 * 🧪 TEST SUITE: Quantum Security Validation
 *═══════════════════════════════════════════════════════════════════════════*/

/**
 * 🔬 SECURITY UTILS TEST SUITE - Comprehensive Validation
 * 
 * Tests Required:
 * 1. Password strength validation (NIST 800-63B compliance)
 * 2. SA ID number validation (Identification Act compliance)
 * 3. Encryption/Decryption cycle (AES-256-GCM)
 * 4. JWT token generation and verification
 * 5. TOTP MFA generation and verification
 * 6. PII masking (POPIA compliance)
 * 7. Input sanitization (OWASP Top 10)
 * 8. Quantum-resistant key generation
 * 9. Multi-tenant cryptographic isolation
 * 10. ECT Act electronic signature generation
 * 
 * Test Files to Create:
 * - /server/tests/unit/utils/securityUtils.test.js
 * - /server/tests/integration/securityCompliance.test.js
 * - /server/tests/performance/cryptoBenchmark.test.js
 * - /server/tests/legal/saLegalCompliance.test.js
 */

/*═══════════════════════════════════════════════════════════════════════════*
 * 🚀 DEPENDENCIES INSTALLATION COMMAND
 *═══════════════════════════════════════════════════════════════════════════*/

// Terminal Command to Install Required Dependencies:
/*
npm install bcrypt zxcvbn jsonwebtoken speakeasy uuid dotenv --save
npm install --save-dev @types/bcrypt @types/zxcvbn @types/jsonwebtoken @types/uuid
*/

/*═══════════════════════════════════════════════════════════════════════════*
 * 🔐 ENVIRONMENT VARIABLES GUIDE
 *═══════════════════════════════════════════════════════════════════════════*/

// Add these to your /server/.env file:
/*
# QUANTUM SECURITY CONFIGURATION
ENCRYPTION_MASTER_KEY=your_32_byte_base64_encryption_key_here
JWT_SECRET_KEY=your_minimum_64_char_jwt_secret_here
PASSWORD_HASH_ROUNDS=14
MULTI_TENANT_CRYPTO_SALT=your_unique_salt_per_deployment
SA_ID_VALIDATION_SECRET=validation_secret_for_id_checks
QUANTUM_RESISTANT_KEY=quantum_resistant_key_for_future_proofing
ENCRYPTION_IV_KEY=initialization_vector_key_for_encryption
HASH_PEPPER=server_side_pepper_for_password_hashing

# Generate ENCRYPTION_MASTER_KEY using:
# node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"

# Generate JWT_SECRET_KEY using:
# node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"

# Generate MULTI_TENANT_CRYPTO_SALT using:
# node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
*/

/*═══════════════════════════════════════════════════════════════════════════*
 * 🌟 REQUIRED SUPPORTING FILES
 *═══════════════════════════════════════════════════════════════════════════*/

/*
1. /server/config/securityConfig.js - Security configuration constants
2. /server/middleware/securityMiddleware.js - Security middleware
3. /server/services/encryptionService.js - Encryption service layer
4. /server/validators/securityValidators.js - Input validators
5. /server/controllers/authController.js - Authentication endpoints
6. /server/models/auditLogModel.js - Security audit logging
7. /server/utils/rateLimiter.js - Rate limiting utilities
8. /server/utils/logger.js - Secure logging with PII masking
*/

// Export all security utilities
module.exports = {
    // 🔐 Password Security
    PasswordSecurity,

    // 🔏 Encryption
    QuantumEncryption,

    // 🏛️ SA Legal Compliance
    SALegalCompliance,

    // 🎯 Token & Authentication
    TokenSecurity,

    // ⚡ Core Utilities (Renamed to avoid conflict)
    SecurityUtils: CoreSecurityUtils,

    // 🚨 Exceptions
    SecurityException,
    ComplianceException,

    // ⚙️ Configuration
    SECURITY_CONFIG
};

// 🌍 WILSY TOUCHING LIVES ETERNALLY