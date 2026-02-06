/*
╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                                      ║
║    ███████╗██╗ ██████╗ ███╗    ██╗ █████╗ ████████╗██╗   ██╗██████╗ ███████╗                         ║
║    ██╔════╝██║██╔════╝ ████╗   ██║██╔══██╗╚══██╔══╝██║   ██║██╔══██╗██╔════╝                         ║
║    ███████╗██║██║   ███╗██╔██╗ ██║███████║   ██║   ██║   ██║██████╔╝█████╗                           ║
║    ╚════██║██║██║   ██║██║╚██╗██║██╔══██║   ██║   ██║   ██║██╔══██╗██╔══╝                           ║
║    ███████║██║╚██████╔╝██║ ╚████║██║  ██║   ██║   ╚██████╔╝██║  ██║███████╗                         ║
║    ╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝                         ║
║                                                                                                      ║
║    ELECTRONIC SIGNATURE QUANTUM SERVICE - THE DIGITAL COVENANT SENTINEL                              ║
║    This divine service orchestrates the sacred act of electronic signature,                          ║
║    transmuting legal intent into immutable digital evidence with quantum precision.                  ║
║    Each signature is an eternal quantum bond, compliant with South African ECT Act,                  ║
║    POPIA, and global standards, creating unbreakable chains of legal accountability.                  ║
║                                                                                                      ║
║    File: /server/services/signatureService.js                                                        ║
║    Chief Architect: Wilson Khanyezi                                                                  ║
║    Quantum Version: 1.0.0                                                                            ║
║    Legal Compliance: ECT Act §13, §15, POPIA §6-11, Companies Act 2008, CPA §22                      ║
║                                                                                                      ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝

⚖️  LEGAL QUANTUM: This service encodes the sacred principles of the ECT Act—non-repudiation,
    authentication, integrity, and consent—into every digital signature, creating legally
    binding quantum artifacts that withstand the most rigorous South African court scrutiny.
*/

// ============================================================================
// QUANTUM DEPENDENCIES - SECURELY PINNED FOR PRODUCTION
// ============================================================================
const crypto = require('crypto');
const jwt = require('jsonwebtoken');
const forge = require('node-forge');
const axios = require('axios');
const mongoose = require('mongoose');
const moment = require('moment-timezone');
const { v4: uuidv4 } = require('uuid');
const { globalQuantumLogger } = require('../utils/quantumLogger');
const AuditTrailService = require('./auditTrailService');
const EncryptionService = require('./encryptionService');
const LegalComplianceEngine = require('./legalComplianceEngine');
const NotificationService = require('./notificationService');
require('dotenv').config({ path: '/server/.env' });

// ============================================================================
// QUANTUM CONSTANTS & ENVIRONMENT VALIDATION
// ============================================================================
const QUANTUM_CONSTANTS = Object.freeze({
    SIGNATURE_TYPES: {
        SIMPLE: 'SIMPLE_ELECTRONIC_SIGNATURE',
        ADVANCED: 'ADVANCED_ELECTRONIC_SIGNATURE',
        QUALIFIED: 'QUALIFIED_ELECTRONIC_SIGNATURE'
    },
    PROVIDERS: {
        DOCUSIGN: 'docuSign',
        SIGNREQUEST: 'signRequest',
        INTERNAL: 'internal',
        ADOBESIGN: 'adobeSign'
    },
    LEGAL_REQUIREMENTS: {
        ECT_ACT: 'ELECTRONIC_COMMUNICATIONS_AND_TRANSACTIONS_ACT_2002',
        POPIA: 'PROTECTION_OF_PERSONAL_INFORMATION_ACT_2013',
        COMPANIES_ACT: 'COMPANIES_ACT_2008',
        CPA: 'CONSUMER_PROTECTION_ACT_2008'
    },
    CRYPTOGRAPHY: {
        HASH_ALGORITHM: 'SHA-256',
        ENCRYPTION_ALGORITHM: 'AES-256-GCM',
        ASYMMETRIC_ALGORITHM: 'RSA-PSS',
        KEY_SIZE: 2048,
        CERTIFICATE_VALIDITY: parseInt(process.env.SIGNATURE_VALIDITY_DAYS) || 1825
    },
    OPERATIONAL: {
        MAX_SIGNERS_PER_DOCUMENT: 10,
        MAX_DOCUMENT_SIZE_MB: 25,
        SIGNATURE_TIMEOUT_MS: 300000,
        RETRY_ATTEMPTS: 3,
        RETRY_DELAY_MS: 5000
    },
    AUDIT: {
        AUDIT_RETENTION_DAYS: 3650,
        PROOF_OF_SIGNATURE_STORAGE: 'IMMUTABLE_AUDIT_TRAIL',
        TIMESTAMP_AUTHORITY_REQUIRED: true
    }
});

/**
 * Validates the environment for the Signature Service.
 */
const validateSignatureEnvironment = function () {
    const requiredVars = ['ECT_SIGNATURE_PROVIDER'];
    const missing = requiredVars.filter(varName => !process.env[varName]);

    if (missing.length > 0) {
        globalQuantumLogger.critical('SIGNATURE_ENV_VALIDATION', 'Missing required environment variables', {
            missing: missing,
            service: 'SignatureService'
        });
        throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
    }

    const provider = process.env.ECT_SIGNATURE_PROVIDER;
    if (provider === QUANTUM_CONSTANTS.PROVIDERS.DOCUSIGN) {
        const docusignVars = ['DOCUSIGN_CLIENT_ID', 'DOCUSIGN_CLIENT_SECRET', 'DOCUSIGN_ACCOUNT_ID'];
        const missingDocusign = docusignVars.filter(varName => !process.env[varName]);
        if (missingDocusign.length > 0) {
            throw new Error(`Missing DocuSign configuration: ${missingDocusign.join(', ')}`);
        }
    }

    globalQuantumLogger.info('SIGNATURE_ENV_VALIDATED', 'Signature service environment validated', {
        provider: provider,
        compliance: Object.values(QUANTUM_CONSTANTS.LEGAL_REQUIREMENTS)
    });
};

validateSignatureEnvironment();

// ============================================================================
// QUANTUM SIGNATURE CERTIFICATE AUTHORITY
// ============================================================================
class QuantumCertificateAuthority {
    /**
     * Collaboration Comment: This class handles RSA key generation and X.509 certificate
     * issuance to ensure Advanced Electronic Signatures (AES) under the ECT Act.
     * Fixed: Moved assignments into constructor to avoid 'Unexpected token =' error.
     */
    constructor() {
        this.caPrivateKey = null;
        this.caCertificate = null;
        this.initialized = false;
        this.certificateCache = new Map();
        this.keyStorage = new Map();
    }

    async initialize() {
        try {
            const caKeyPem = process.env.SIGNATURE_CA_PRIVATE_KEY;
            if (caKeyPem) {
                this.caPrivateKey = forge.pki.privateKeyFromPem(caKeyPem);
                globalQuantumLogger.info('CA_KEY_LOADED', 'Loaded existing CA private key');
            } else {
                const keys = forge.pki.rsa.generateKeyPair(QUANTUM_CONSTANTS.CRYPTOGRAPHY.KEY_SIZE);
                this.caPrivateKey = keys.privateKey;
                globalQuantumLogger.info('CA_KEY_GENERATED', 'Generated new CA key pair');
                globalQuantumLogger.warn('CA_KEY_STORAGE', 'CA private key not persisted - configure secure storage');
            }

            await this.generateCACertificate();
            this.initialized = true;
            globalQuantumLogger.info('CA_INITIALIZED', 'Quantum Certificate Authority initialized');
        } catch (error) {
            globalQuantumLogger.error('CA_INITIALIZATION_FAILED', error.message);
            throw new Error(`CA initialization failed: ${error.message}`);
        }
    }

    async generateCACertificate() {
        const cert = forge.pki.createCertificate();
        cert.publicKey = this.caPrivateKey.publicKey;
        cert.serialNumber = '01' + crypto.randomBytes(8).toString('hex');
        cert.validity.notBefore = new Date();
        cert.validity.notAfter = new Date();
        cert.validity.notAfter.setDate(cert.validity.notBefore.getDate() + QUANTUM_CONSTANTS.CRYPTOGRAPHY.CERTIFICATE_VALIDITY);

        const attrs = [
            { name: 'commonName', value: 'Wilsy OS Quantum Certificate Authority' },
            { name: 'organizationName', value: 'Wilsy Legal Technologies' },
            { name: 'countryName', value: 'ZA' },
            { name: 'stateOrProvinceName', value: 'Gauteng' }
        ];

        cert.setSubject(attrs);
        cert.setIssuer(attrs);
        cert.setExtensions([
            { name: 'basicConstraints', cA: true, pathLenConstraint: 0 },
            { name: 'keyUsage', keyCertSign: true, cRLSign: true, digitalSignature: true },
            { name: 'subjectKeyIdentifier' }
        ]);

        cert.sign(this.caPrivateKey, forge.md.sha256.create());
        this.caCertificate = cert;
        globalQuantumLogger.info('CA_CERTIFICATE_GENERATED', 'CA certificate generated', { serialNumber: cert.serialNumber });
    }

    async issueCertificate(signer, certificateType) {
        if (!this.initialized) await this.initialize();
        try {
            const keys = forge.pki.rsa.generateKeyPair(QUANTUM_CONSTANTS.CRYPTOGRAPHY.KEY_SIZE);
            const cert = forge.pki.createCertificate();
            cert.publicKey = keys.publicKey;
            cert.serialNumber = uuidv4().replace(/-/g, '').substring(0, 16);
            cert.validity.notBefore = new Date();
            cert.validity.notAfter = new Date();
            cert.validity.notAfter.setDate(cert.validity.notBefore.getDate() + QUANTUM_CONSTANTS.CRYPTOGRAPHY.CERTIFICATE_VALIDITY);

            const subjectAttrs = [
                { name: 'commonName', value: `${signer.fullName} (${signer.email})` },
                { name: 'emailAddress', value: signer.email },
                { name: 'countryName', value: signer.country || 'ZA' }
            ];

            cert.setSubject(subjectAttrs);
            cert.setIssuer(this.caCertificate.subject.attributes);
            cert.setExtensions([
                { name: 'basicConstraints', cA: false },
                { name: 'keyUsage', digitalSignature: true, nonRepudiation: true },
                { name: 'subjectKeyIdentifier' },
                { name: 'authorityKeyIdentifier' }
            ]);

            cert.sign(this.caPrivateKey, forge.md.sha256.create());
            const certificateId = uuidv4();

            this.certificateCache.set(certificateId, {
                certificate: cert,
                privateKey: keys.privateKey,
                signer: signer,
                type: certificateType
            });

            const encryptedPrivateKey = await EncryptionService.encryptData(
                forge.pki.privateKeyToPem(keys.privateKey),
                'SIGNATURE_PRIVATE_KEY'
            );
            this.keyStorage.set(certificateId, encryptedPrivateKey);

            return {
                certificateId,
                certificatePem: forge.pki.certificateToPem(cert),
                publicKeyPem: forge.pki.publicKeyToPem(keys.publicKey),
                validity: { notBefore: cert.validity.notBefore, notAfter: cert.validity.notAfter }
            };
        } catch (error) {
            globalQuantumLogger.error('CERTIFICATE_ISSUE_FAILED', error.message);
            throw error;
        }
    }

    async validateCertificate(certificatePem) {
        try {
            const cert = forge.pki.certificateFromPem(certificatePem);
            const now = new Date();
            if (now < cert.validity.notBefore || now > cert.validity.notAfter) {
                return { valid: false, reason: 'CERTIFICATE_EXPIRED_OR_NOT_YET_VALID' };
            }
            const verified = this.caCertificate.verify(cert);
            return { valid: verified, compliance: verified ? 'ECT_ACT_COMPLIANT' : 'INVALID_CHAIN' };
        } catch (error) {
            return { valid: false, error: error.message };
        }
    }

    async revokeCertificate(certificateId, reason) {
        const certData = this.certificateCache.get(certificateId);
        if (!certData) throw new Error('Certificate not found');
        certData.revoked = true;
        this.keyStorage.delete(certificateId);
        globalQuantumLogger.info('CERTIFICATE_REVOKED', { certificateId, reason });
        return { success: true };
    }
}

// ============================================================================
// QUANTUM SIGNATURE PROVIDER ABSTRACTION
// ============================================================================
class SignatureProvider {
    /**
     * Collaborative Comment: Orchestrates external APIs (DocuSign/SignRequest) 
     * or the Internal Quantum CA.
     */
    constructor(providerType) {
        this.providerType = providerType;
        this.config = this.loadProviderConfig();
        this.client = null;
        this.initialized = false;
    }

    loadProviderConfig() {
        const provider = process.env.ECT_SIGNATURE_PROVIDER;
        switch (provider) {
            case QUANTUM_CONSTANTS.PROVIDERS.DOCUSIGN:
                return {
                    clientId: process.env.DOCUSIGN_CLIENT_ID,
                    clientSecret: process.env.DOCUSIGN_CLIENT_SECRET,
                    accountId: process.env.DOCUSIGN_ACCOUNT_ID,
                    userId: process.env.DOCUSIGN_USER_ID,
                    privateKey: process.env.DOCUSIGN_PRIVATE_KEY,
                    baseUrl: 'https://demo.docusign.net/restapi/v2.1',
                    authUrl: 'https://account-d.docusign.com/oauth/token'
                };
            case QUANTUM_CONSTANTS.PROVIDERS.SIGNREQUEST:
                return {
                    apiKey: process.env.SIGNREQUEST_API_KEY,
                    baseUrl: 'https://signrequest.com/api/v1'
                };
            case QUANTUM_CONSTANTS.PROVIDERS.INTERNAL:
                return {
                    certificateAuthority: new QuantumCertificateAuthority(),
                    storageUrl: process.env.INTERNAL_SIGNATURE_STORAGE_URL
                };
            default:
                throw new Error(`Unsupported signature provider: ${provider}`);
        }
    }

    async initialize() {
        try {
            switch (this.providerType) {
                case QUANTUM_CONSTANTS.PROVIDERS.DOCUSIGN:
                    await this.initializeDocuSign();
                    break;
                case QUANTUM_CONSTANTS.PROVIDERS.SIGNREQUEST:
                    await this.initializeSignRequest();
                    break;
                case QUANTUM_CONSTANTS.PROVIDERS.INTERNAL:
                    await this.config.certificateAuthority.initialize();
                    break;
            }
            this.initialized = true;
            globalQuantumLogger.info('SIGNATURE_PROVIDER_INITIALIZED', { provider: this.providerType });
        } catch (error) {
            throw new Error(`Provider initialization failed: ${error.message}`);
        }
    }

    async initializeDocuSign() {
        const jwtPayload = {
            iss: this.config.clientId,
            sub: this.config.userId,
            iat: Math.floor(Date.now() / 1000),
            exp: Math.floor(Date.now() / 1000) + 3600,
            aud: 'account-d.docusign.com',
            scope: 'signature'
        };
        const privateKey = Buffer.from(this.config.privateKey, 'base64').toString('ascii');
        const jwtToken = jwt.sign(jwtPayload, privateKey, { algorithm: 'RS256' });
        const tokenResponse = await axios.post(this.config.authUrl, null, {
            params: { grant_type: 'urn:ietf:params:oauth:grant-type:jwt-bearer', assertion: jwtToken },
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
        this.client = axios.create({
            baseURL: `${this.config.baseUrl}/accounts/${this.config.accountId}`,
            headers: { 'Authorization': `Bearer ${tokenResponse.data.access_token}`, 'Content-Type': 'application/json' }
        });
    }

    async initializeSignRequest() {
        this.client = axios.create({
            baseURL: this.config.baseUrl,
            headers: { 'Authorization': `Token ${this.config.apiKey}`, 'Content-Type': 'application/json' }
        });
    }

    async createSignatureRequest(requestData) {
        if (!this.initialized) await this.initialize();
        try {
            switch (this.providerType) {
                case QUANTUM_CONSTANTS.PROVIDERS.DOCUSIGN:
                    return await this.createDocuSignEnvelope(requestData);
                case QUANTUM_CONSTANTS.PROVIDERS.SIGNREQUEST:
                    return await this.createSignRequest(requestData);
                case QUANTUM_CONSTANTS.PROVIDERS.INTERNAL:
                    return await this.createInternalSignature(requestData);
            }
        } catch (error) {
            globalQuantumLogger.error('SIGNATURE_REQUEST_FAILED', error.message);
            throw error;
        }
    }

    async createDocuSignEnvelope(requestData) {
        const envelopeDefinition = {
            emailSubject: requestData.subject || 'Document for Signature',
            documents: requestData.documents.map(doc => ({
                documentBase64: doc.content,
                name: doc.name,
                fileExtension: doc.extension || 'pdf',
                documentId: doc.documentId
            })),
            recipients: {
                signers: requestData.signers.map((signer, index) => ({
                    email: signer.email,
                    name: signer.name,
                    recipientId: (index + 1).toString(),
                    tabs: {
                        signHereTabs: signer.signatureLocations.map(loc => ({
                            xPosition: loc.x, yPosition: loc.y, pageNumber: loc.page, documentId: loc.documentId
                        }))
                    }
                }))
            },
            status: 'sent'
        };
        const response = await this.client.post('/envelopes', envelopeDefinition);
        return { signatureId: response.data.envelopeId, status: response.data.status, compliance: { ectActCompliant: true, provider: 'DocuSign' } };
    }

    async createSignRequest(requestData) {
        const signRequestData = {
            from_email: requestData.senderEmail,
            files: requestData.documents.map(doc => ({ name: doc.name, file: doc.content })),
            signers: requestData.signers.map(signer => ({ email: signer.email })),
            message: requestData.message,
            subject: requestData.subject
        };
        const response = await this.client.post('/signrequests/', signRequestData);
        return { signatureId: response.data.uuid, status: response.data.status, compliance: { ectActCompliant: true, provider: 'SignRequest' } };
    }

    async createInternalSignature(requestData) {
        const signatureId = uuidv4();
        const certificates = await Promise.all(requestData.signers.map(async (signer) => {
            return await this.config.certificateAuthority.issueCertificate(signer, QUANTUM_CONSTANTS.SIGNATURE_TYPES.ADVANCED);
        }));
        return { signatureId, status: 'PENDING', certificates, compliance: { provider: 'Internal Quantum CA' } };
    }
}

module.exports = {
    SignatureProvider,
    QuantumCertificateAuthority,
    QUANTUM_CONSTANTS
};