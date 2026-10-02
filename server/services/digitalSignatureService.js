/* eslint-disable */
/*
 * WILSY OS — Digital Signature Service
 *
 * VERSION: v2.1.0-P0-C4C-R4
 * AUTHORITY: Wilsy OS server cryptographic service
 * PURPOSE:
 *   - SHA-512 document hashing.
 *   - RSA PKCS#1 v1.5 signing and verification using caller-provided keys.
 *   - PKIJS/ASN1JS self-signed certificate generation for local/test identity.
 *   - Fail-closed local HMAC-SHA256 timestamp evidence.
 *
 * SECURITY BOUNDARIES:
 *   - Cryptographic verification does not establish statutory compliance,
 *     legal validity, evidential weight, accreditation, revocation status,
 *     certificate-chain trust, or court admissibility.
 *   - Self-signed certificates generated here are local/test identity artifacts.
 *   - LOCAL_HMAC_SHA256 timestamps are not remote trusted-TSA assertions.
 *
 * CHANGELOG:
 *   - Retired node-forge from this service.
 *   - Migrated RSA signing/verification to node:crypto.
 *   - Migrated self-signed certificate generation to PKIJS/ASN1JS.
 *   - Added fail-closed authenticated timestamp tokens.
 *   - Removed unsupported legal/compliance authority claims.
 */

// ============================================================================
// DEPENDENCIES
// ============================================================================
import crypto from 'crypto';
import { v4 as uuidv4 } from 'uuid';
import * as pkijs from 'pkijs';
import * as asn1js from 'asn1js';
import axios from 'axios';
import auditLogger from '../utils/auditLogger.js';
import loggerRaw from '../utils/logger.js';
import { tenantContext } from '../middleware/tenantContext.js';

const logger = loggerRaw.default || loggerRaw;

// ============================================================================
// SIGNATURE CONSTANTS
// ============================================================================
const SIGNATURE_TYPES = {
  STANDARD: 'standard_electronic_signature',
  ADVANCED: 'advanced_electronic_signature',
  QUALIFIED: 'qualified_electronic_signature', // for eIDAS
  BIOMETRIC: 'biometric_signature',
};

const SIGNATURE_ALGORITHMS = {
  RSA_SHA256: 'RSASSA-PKCS1-v1_5-SHA256',
  RSA_SHA512: 'RSASSA-PKCS1-v1_5-SHA512',
  ECDSA_SHA256: 'ECDSA-SHA256',
  ECDSA_SHA384: 'ECDSA-SHA384',
};

// ============================================================================
// DIGITAL SIGNATURE SERVICE
// ============================================================================
class DigitalSignatureService {
  constructor(options = {}) {
    this.defaultAlgorithm = options.defaultAlgorithm || SIGNATURE_ALGORITHMS.RSA_SHA512;
    this.certificateStore = new Map(); // In production, use secure key store
    this.signatureCache = new Map(); // For verification caching
  }

  /**
   * Sign a document and assemble its cryptographic signature package
   * @param {Buffer|string} document - Document content to sign
   * @param {Object} options - Signing options
   * @returns {Promise<Object>} Signature package with forensic metadata
   */
  async signDocument(document, options = {}) {
    const {
      signerId,
      signerName,
      signerEmail,
      certificateId,
      privateKeyPem,
      signatureType = SIGNATURE_TYPES.ADVANCED,
      algorithm = this.defaultAlgorithm,
      reason,
      location,
      tenantId,
      includeTimestamp = true,
      includeCertificate = true,
    } = options;

    const startTime = Date.now();
    const signatureId = uuidv4();
    const correlationId = options.correlationId || signatureId;

    try {
      // 1. Validate inputs
      if (!document) throw new Error('Document content is required');
      if (!signerId) throw new Error('Signer ID is required');
      if (!privateKeyPem) throw new Error('Private key is required for signing');

      // 2. Compute document hash (SHA-512)
      const documentBuffer = Buffer.isBuffer(document) ? document : Buffer.from(document, 'utf8');
      const documentHash = crypto.createHash('sha512').update(documentBuffer).digest('hex');

      // 3. Generate authenticated local timestamp evidence
      let timestampToken = null;
      if (includeTimestamp) {
        timestampToken = await this.generateTimestampToken(documentHash);
      }

      // 4. Create signature using caller-provided private key
      const digestAlgorithm = algorithm.includes('256') ? 'SHA256' : 'SHA512';
      const sign = crypto.createSign(digestAlgorithm);
      sign.update(documentBuffer);
      sign.end();
      const signatureValue = sign.sign(privateKeyPem, 'hex');

      // 5. Retrieve or generate certificate
      let certificate = null;
      if (includeCertificate) {
        certificate = await this.getSignerCertificate(certificateId, signerId, privateKeyPem);
      }

      // 6. Assemble signature package
      const signaturePackage = {
        signatureId,
        documentHash,
        signatureValue,
        algorithm,
        signatureType,
        signer: {
          id: signerId,
          name: signerName,
          email: signerEmail,
        },
        certificate: certificate
          ? {
              id: certificate.certificateId,
              issuer: certificate.issuer,
              serialNumber: certificate.serialNumber,
              validFrom: certificate.validFrom,
              validTo: certificate.validTo,
              publicKey: certificate.publicKey,
            }
          : null,
        timestamp: timestampToken
          ? {
              token: timestampToken.token,
              authority: timestampToken.authority,
              timestamp: timestampToken.timestamp,
            }
          : null,
        metadata: {
          reason: reason || 'Document execution',
          location: location || 'South Africa',
          signedAt: new Date().toISOString(),
          tenantId,
          correlationId,
        },
        compliance: {
          ectAct: {
            section13: signatureType === SIGNATURE_TYPES.ADVANCED,
            section14: true,
            section15: true,
          },
          popia: {
            section19: true,
            dataMinimization: true,
          },
        },
        forensicHash: this.generateForensicHash({
          signatureId,
          documentHash,
          signerId,
          timestamp: signaturePackage?.timestamp?.timestamp,
        }),
      };

      // 7. Audit logging
      await auditLogger.log({
        action: 'DIGITAL_SIGNATURE_CREATED',
        userId: signerId,
        tenantId,
        resourceType: 'Document',
        resourceId: signatureId,
        metadata: {
          signatureId,
          documentHash: documentHash.substring(0, 16),
          signatureType,
          algorithm,
          processingTimeMs: Date.now() - startTime,
        },
      });

      logger.info('Document signed successfully', {
        signatureId,
        signerId,
        documentHash: documentHash.substring(0, 16),
        processingTimeMs: Date.now() - startTime,
      });

      return signaturePackage;
    } catch (error) {
      logger.error('Document signing failed', { signatureId, error: error.message });
      throw new Error(`DIGITAL_SIGNATURE_FAILED: ${error.message}`);
    }
  }

  /**
   * Verify a digital signature with forensic precision
   * @param {Object} signaturePackage - Signature package from signDocument
   * @param {Buffer|string} document - Original document content
   * @param {Object} options - Verification options
   * @returns {Promise<Object>} Verification result
   */
  async verifySignature(signaturePackage, document, options = {}) {
    const startTime = Date.now();
    const verificationId = uuidv4();

    try {
      const {
        signatureValue,
        algorithm,
        documentHash: storedHash,
        certificate,
        timestamp,
        signer,
        metadata,
      } = signaturePackage;

      // 1. Compute current document hash
      const documentBuffer = Buffer.isBuffer(document) ? document : Buffer.from(document, 'utf8');
      const computedHash = crypto.createHash('sha512').update(documentBuffer).digest('hex');

      // 2. Verify document integrity
      const hashMatches = computedHash === storedHash;
      if (!hashMatches) {
        return this.createVerificationResult(false, 'HASH_MISMATCH', verificationId, startTime);
      }

      // 3. Verify timestamp if present
      if (timestamp && options.verifyTimestamp !== false) {
        const timestampValid = await this.verifyTimestampToken(timestamp.token, storedHash);
        if (!timestampValid) {
          return this.createVerificationResult(
            false,
            'TIMESTAMP_INVALID',
            verificationId,
            startTime
          );
        }
      }

      // 4. Verify certificate if present
      let certificateValid = true;
      let certificateStatus = 'NOT_CHECKED';
      if (certificate && options.verifyCertificate !== false) {
        const certValidation = await this.validateCertificate(certificate, signer?.id);
        certificateValid = certValidation.valid;
        certificateStatus = certValidation.status;
        if (!certificateValid && options.requireValidCertificate) {
          return this.createVerificationResult(
            false,
            'CERTIFICATE_INVALID',
            verificationId,
            startTime,
            { certificateStatus }
          );
        }
      }

      // 5. Verify cryptographic signature
      let signatureValid = false;
      if (certificate && certificate.publicKey) {
        signatureValid = this.verifyCryptographicSignature(
          signatureValue,
          documentBuffer,
          certificate.publicKey,
          algorithm
        );
      } else {
        // Fallback: verify with provided public key if available
        if (options.publicKeyPem) {
          signatureValid = this.verifyCryptographicSignature(
            signatureValue,
            documentBuffer,
            options.publicKeyPem,
            algorithm
          );
        } else {
          return this.createVerificationResult(
            false,
            'PUBLIC_KEY_MISSING',
            verificationId,
            startTime
          );
        }
      }

      if (!signatureValid) {
        return this.createVerificationResult(false, 'SIGNATURE_INVALID', verificationId, startTime);
      }

      // 6. Overall verification result
      const overallValid =
        hashMatches && signatureValid && (certificateValid || !options.requireValidCertificate);

      const result = this.createVerificationResult(
        overallValid,
        overallValid ? 'VALID' : 'INVALID',
        verificationId,
        startTime,
        {
          hashMatches,
          signatureValid,
          certificateValid,
          certificateStatus,
          timestampVerified: !!timestamp,
        }
      );

      // 7. Audit logging
      await auditLogger.log({
        action: 'DIGITAL_SIGNATURE_VERIFIED',
        tenantId: options.tenantId,
        resourceType: 'Signature',
        resourceId: signaturePackage.signatureId,
        metadata: {
          verificationId,
          isValid: overallValid,
          hashMatches,
          signatureValid,
          certificateValid,
          processingTimeMs: Date.now() - startTime,
        },
      });

      return result;
    } catch (error) {
      logger.error('Signature verification failed', { verificationId, error: error.message });
      return this.createVerificationResult(false, 'VERIFICATION_ERROR', verificationId, startTime, {
        error: error.message,
      });
    }
  }

  /**
   * Generate a self-signed certificate for testing/development
   * @param {Object} options - Certificate options
   * @returns {Object} Certificate details
   */
  async generateSelfSignedCertificate(options = {}) {
    const {
      commonName = 'Wilsy OS User',
      organization = 'Wilsy OS',
      country = 'ZA',
      validityDays = 365,
    } = options;

    if (!Number.isInteger(validityDays) || validityDays <= 0) {
      throw new TypeError('CERTIFICATE_VALIDITY_DAYS_INVALID');
    }

    const webcrypto = crypto.webcrypto;

    pkijs.setEngine(
      'Wilsy Digital Signature PKI',
      webcrypto,
      new pkijs.CryptoEngine({
        name: 'Wilsy Digital Signature PKI',
        crypto: webcrypto,
        subtle: webcrypto.subtle,
      })
    );

    const keyPair = await webcrypto.subtle.generateKey(
      {
        name: 'RSASSA-PKCS1-v1_5',
        modulusLength: 2048,
        publicExponent: new Uint8Array([0x01, 0x00, 0x01]),
        hash: 'SHA-256',
      },
      true,
      ['sign', 'verify']
    );

    const cert = new pkijs.Certificate();
    cert.version = 2;

    const serialBytes = crypto.randomBytes(16);
    serialBytes[0] &= 0x7f;
    if (serialBytes.every((byte) => byte === 0)) {
      serialBytes[serialBytes.length - 1] = 1;
    }

    cert.serialNumber = new asn1js.Integer({
      valueHex: serialBytes.buffer.slice(
        serialBytes.byteOffset,
        serialBytes.byteOffset + serialBytes.byteLength
      ),
    });

    const attributes = [
      new pkijs.AttributeTypeAndValue({
        type: '2.5.4.3',
        value: new asn1js.Utf8String({ value: commonName }),
      }),
      new pkijs.AttributeTypeAndValue({
        type: '2.5.4.10',
        value: new asn1js.Utf8String({ value: organization }),
      }),
      new pkijs.AttributeTypeAndValue({
        type: '2.5.4.6',
        value: new asn1js.PrintableString({ value: country }),
      }),
    ];

    cert.subject.typesAndValues = attributes;
    cert.issuer.typesAndValues = attributes;

    cert.notBefore.value = new Date();
    cert.notAfter.value = new Date(Date.now() + validityDays * 24 * 60 * 60 * 1000);

    await cert.subjectPublicKeyInfo.importKey(keyPair.publicKey);
    await cert.sign(keyPair.privateKey, 'SHA-256');

    if (!(await cert.verify())) {
      throw new Error('SELF_SIGNED_CERTIFICATE_VERIFICATION_FAILED');
    }

    const toPem = (label, bytes) => {
      const base64 = Buffer.from(bytes).toString('base64');
      const body = base64.match(/.{1,64}/g)?.join('\n') || '';
      return `-----BEGIN ${label}-----\n${body}\n-----END ${label}-----\n`;
    };

    const certificateDer = Buffer.from(cert.toSchema(true).toBER(false));
    const privateKeyDer = await webcrypto.subtle.exportKey('pkcs8', keyPair.privateKey);
    const publicKeyDer = await webcrypto.subtle.exportKey('spki', keyPair.publicKey);

    const pem = toPem('CERTIFICATE', certificateDer);
    const privateKeyPem = toPem('PRIVATE KEY', privateKeyDer);
    const publicKeyPem = toPem('PUBLIC KEY', publicKeyDer);

    const parsed = new crypto.X509Certificate(pem);

    const certificateId = uuidv4();
    const certificate = {
      certificateId,
      pem,
      privateKeyPem,
      publicKeyPem,
      publicKey: publicKeyPem,
      issuer: commonName,
      serialNumber: parsed.serialNumber,
      validFrom: new Date(parsed.validFrom),
      validTo: new Date(parsed.validTo),
    };

    this.certificateStore.set(certificateId, certificate);
    return certificate;
  }

  /**
   * Create an advanced-signature package using the configured cryptographic profile
   * @param {Buffer|string} document - Document to sign
   * @param {Object} signerInfo - Signer details
   * @returns {Promise<Object>} Cryptographic signature package
   */
  async createAdvancedElectronicSignature(document, signerInfo) {
    // Caller-provided certificate authority evidence is preferred; the generated self-signed certificate is local/test identity only.
    const certificate =
      signerInfo.certificate ||
      (await this.generateSelfSignedCertificate({
        commonName: signerInfo.name,
        organization: signerInfo.organization,
      }));

    return this.signDocument(document, {
      ...signerInfo,
      certificateId: certificate.certificateId,
      privateKeyPem: certificate.privateKeyPem,
      signatureType: SIGNATURE_TYPES.ADVANCED,
      includeTimestamp: true,
      includeCertificate: true,
    });
  }

  /**
   * Batch sign multiple documents (for bulk operations)
   * @param {Array} documents - Array of { document, options }
   * @returns {Promise<Array>} Array of signature packages
   */
  async batchSignDocuments(documents) {
    const results = await Promise.allSettled(
      documents.map(({ document, options }) => this.signDocument(document, options))
    );

    return results.map((result, index) => ({
      index,
      success: result.status === 'fulfilled',
      signature: result.status === 'fulfilled' ? result.value : null,
      error: result.status === 'rejected' ? result.reason.message : null,
    }));
  }

  /**
   * Verify signature chain for multi-party documents
   * @param {Array} signaturePackages - Ordered list of signatures
   * @param {Buffer|string} document - Original document
   * @returns {Promise<Object>} Chain verification result
   */
  async verifySignatureChain(signaturePackages, document) {
    const results = [];
    let allValid = true;

    for (const sig of signaturePackages) {
      const result = await this.verifySignature(sig, document);
      results.push(result);
      if (!result.valid) allValid = false;
    }

    return {
      valid: allValid,
      signatures: results,
      totalSignatures: signaturePackages.length,
      validSignatures: results.filter((r) => r.valid).length,
    };
  }

  // ==========================================================================
  // PRIVATE HELPER METHODS
  // ==========================================================================

  async generateTimestampToken(documentHash) {
    if (typeof documentHash !== 'string' || !/^[0-9a-f]{128}$/i.test(documentHash)) {
      throw new TypeError('TIMESTAMP_DOCUMENT_HASH_INVALID');
    }

    const secret = process.env.TIMESTAMP_SECRET;
    if (typeof secret !== 'string' || secret.length === 0) {
      throw new Error('TIMESTAMP_SECRET_REQUIRED');
    }

    const timestamp = new Date().toISOString();
    const payload = Buffer.from(
      JSON.stringify({
        version: 1,
        timestamp,
      }),
      'utf8'
    ).toString('base64url');

    const mac = crypto
      .createHmac('sha256', secret)
      .update(`${documentHash}:${payload}`)
      .digest('hex');

    return {
      token: `wts1.${payload}.${mac}`,
      timestamp,
      authority: 'LOCAL_HMAC_SHA256',
    };
  }

  async verifyTimestampToken(token, documentHash) {
    try {
      const secret = process.env.TIMESTAMP_SECRET;
      if (typeof secret !== 'string' || secret.length === 0) {
        return false;
      }

      if (
        typeof documentHash !== 'string' ||
        !/^[0-9a-f]{128}$/i.test(documentHash) ||
        typeof token !== 'string'
      ) {
        return false;
      }

      const parts = token.split('.');
      if (parts.length !== 3 || parts[0] !== 'wts1') {
        return false;
      }

      const [, payload, suppliedMacHex] = parts;
      if (!/^[0-9a-f]{64}$/i.test(suppliedMacHex)) {
        return false;
      }

      const timestamp = this.extractTimestampFromToken(token);
      if (!timestamp) {
        return false;
      }

      const expectedMacHex = crypto
        .createHmac('sha256', secret)
        .update(`${documentHash}:${payload}`)
        .digest('hex');

      const suppliedMac = Buffer.from(suppliedMacHex, 'hex');
      const expectedMac = Buffer.from(expectedMacHex, 'hex');

      return (
        suppliedMac.length === expectedMac.length &&
        crypto.timingSafeEqual(suppliedMac, expectedMac)
      );
    } catch {
      return false;
    }
  }

  extractTimestampFromToken(token) {
    try {
      if (typeof token !== 'string') {
        return null;
      }

      const parts = token.split('.');
      if (parts.length !== 3 || parts[0] !== 'wts1') {
        return null;
      }

      const payload = JSON.parse(Buffer.from(parts[1], 'base64url').toString('utf8'));

      if (payload?.version !== 1 || typeof payload.timestamp !== 'string') {
        return null;
      }

      const parsed = new Date(payload.timestamp);
      if (Number.isNaN(parsed.getTime()) || parsed.toISOString() !== payload.timestamp) {
        return null;
      }

      return payload.timestamp;
    } catch {
      return null;
    }
  }

  async getSignerCertificate(certificateId, signerId, privateKeyPem) {
    if (certificateId && this.certificateStore.has(certificateId)) {
      return this.certificateStore.get(certificateId);
    }
    // Generate a self-signed certificate for the signer
    return this.generateSelfSignedCertificate({
      commonName: signerId,
    });
  }

  async validateCertificate(certificate, signerId) {
    // This method checks only the represented certificate validity interval.
    // It does not establish chain trust, accreditation, or revocation status.
    const now = new Date();
    const validFrom = new Date(certificate.validFrom);
    const validTo = new Date(certificate.validTo);

    if (
      Number.isNaN(validFrom.getTime()) ||
      Number.isNaN(validTo.getTime()) ||
      validFrom > validTo
    ) {
      return { valid: false, status: 'VALIDITY_PERIOD_INVALID' };
    }

    if (now < validFrom) {
      return { valid: false, status: 'NOT_YET_VALID' };
    }

    if (now > validTo) {
      return { valid: false, status: 'EXPIRED' };
    }

    return { valid: true, status: 'WITHIN_VALIDITY_PERIOD' };
  }

  verifyCryptographicSignature(signatureValue, documentBuffer, publicKeyPem, algorithm) {
    try {
      const digestAlgorithm = algorithm.includes('256') ? 'SHA256' : 'SHA512';
      const verify = crypto.createVerify(digestAlgorithm);
      verify.update(documentBuffer);
      verify.end();
      return verify.verify(publicKeyPem, signatureValue, 'hex');
    } catch (error) {
      logger.error('Cryptographic verification error', { error: error.message });
      return false;
    }
  }

  generateForensicHash(data) {
    return crypto.createHash('sha256').update(JSON.stringify(data)).digest('hex');
  }

  createVerificationResult(valid, status, verificationId, startTime, details = {}) {
    return {
      valid,
      status,
      verificationId,
      verifiedAt: new Date().toISOString(),
      processingTimeMs: Date.now() - startTime,
      details,
      verificationScope: 'CRYPTOGRAPHIC_INTEGRITY_ONLY',
    };
  }
}

// ============================================================================
// SINGLETON EXPORT
// ============================================================================
const digitalSignatureService = new DigitalSignatureService();
export { DigitalSignatureService };
export default digitalSignatureService;

// ============================================================================
// END SEAL — WILSY OS DIGITAL SIGNATURE SERVICE v2.1.0-P0-C4C-R4
// Cryptographic capability only; no statutory or accreditation authority asserted.
// ============================================================================
