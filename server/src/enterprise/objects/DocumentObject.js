/**
 * ============================================================================
 * WILSY OS - DOCUMENT ENTERPRISE OBJECT
 * ============================================================================
 *
 * @file         DocumentObject.js
 * @directory    server/src/enterprise/objects/
 * @system       Wilsy OS - Legal Enterprise Operating System & SaaS Platform
 * @authority    Wilson Khanyezi, Founder & Chief Architect
 * @version      1.0.0-SOVEREIGN
 * @epitome      Generation 2 Sovereign Document Kernel Object implementation.
 *               Serves as the core legal document entity managing file lifecycle,
 *               cryptographic SHA-256 content verification, Attorney-Client
 *               Privilege designations, version history chains, electronic signatures,
 *               and statutory POPIA / Companies Act retention governance in Wilsy OS.
 *
 * @collaboration
 * - Lead Architect: Wilson Khanyezi (Wilsy OS Architecture Core Team)
 * - Legal Knowledge Core: Document Governance & Legal Privilege Subsystem
 * - Data Security: Cryptographic Verification & Sovereign Storage Core
 *
 * ============================================================================
 * INSTITUTIONAL AUDIT TRAIL
 * ============================================================================
 * Date       | Author          | Version | Description
 * -----------|-----------------|---------|------------------------------------
 * 2026-07-24 | Wilson Khanyezi | 1.0.0   | Production-ready Document domain object
 *            |                 |         | with SHA-256 hash tracking, legal privilege
 *            |                 |         | classification, versioning, and e-signatures.
 * ============================================================================
 */

const { BaseEnterpriseObject, OBJECT_LIFECYCLE_STATES } = require('./BaseEnterpriseObject');
const { DataRedactor } = require('../kernel/EnterpriseKernel');

/**
 * Recognized Legal Privilege Classifications.
 */
const DOCUMENT_PRIVILEGE_LEVEL = Object.freeze({
  PUBLIC: 'PUBLIC',
  CONFIDENTIAL: 'CONFIDENTIAL',
  ATTORNEY_CLIENT_PRIVILEGED: 'ATTORNEY_CLIENT_PRIVILEGED',
  WORK_PRODUCT_PRIVILEGED: 'WORK_PRODUCT_PRIVILEGED',
  RESTRICTED_COURT_SEALED: 'RESTRICTED_COURT_SEALED'
});

/**
 * Functional Document Classifications in Legal Practice.
 */
const DOCUMENT_CLASSIFICATION = Object.freeze({
  PLEADING: 'PLEADING',
  CONTRACT: 'CONTRACT',
  AFFIDAVIT: 'AFFIDAVIT',
  CORRESPONDENCE: 'CORRESPONDENCE',
  OPINION: 'OPINION',
  EVIDENCE: 'EVIDENCE',
  INVOICE: 'INVOICE',
  GOVERNANCE: 'GOVERNANCE'
});

/**
 * Custom Error Class for Document Domain Faults.
 */
class DocumentObjectError extends Error {
  /**
   * @param {string} message - Error details.
   * @param {string} [code='DOC_ERR_GENERIC'] - Standard error code.
   * @param {Object} [details={}] - Additional contextual metadata.
   */
  constructor(message, code = 'DOC_ERR_GENERIC', details = {}) {
    super(message);
    this.name = 'DocumentObjectError';
    this.code = code;
    this.timestamp = new Date().toISOString();
    this.details = DataRedactor.sanitize(details);
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, DocumentObjectError);
    }
  }
}

/**
 * Sovereign Legal Document Enterprise Domain Object.
 * Encapsulates legal document metadata, cryptographic verification hashes,
 * privilege flags, immutable version chains, and digital signature records in Wilsy OS.
 */
class DocumentObject extends BaseEnterpriseObject {
  /**
   * Constructs a DocumentObject.
   *
   * @param {Object} params
   * @param {string} params.id - Unique Document Identifier (e.g. 'DOC-2026-9041').
   * @param {string} params.tenantId - Sovereign Tenant ID.
   * @param {string} params.matterId - Associated Legal Matter ID.
   * @param {string} params.title - Human-readable document title.
   * @param {string} params.filename - Original filename with extension (e.g., 'Summons_v1.pdf').
   * @param {string} params.mimeType - MIME type string (e.g., 'application/pdf').
   * @param {number} params.sizeBytes - File size in bytes.
   * @param {string} params.checksumSha256 - SHA-256 cryptographic hash of current content.
   * @param {string} params.storageUri - Secure S3 / Sovereign Storage URI.
   * @param {string} [params.privilegeLevel='CONFIDENTIAL'] - Legal privilege level.
   * @param {string} [params.classification='CORRESPONDENCE'] - Functional category.
   * @param {boolean} [params.isEncrypted=true] - At-rest encryption status.
   * @param {string} [params.createdById='SYSTEM'] - Operator creating entry.
   */
  constructor({
    id,
    tenantId,
    matterId,
    title,
    filename,
    mimeType,
    sizeBytes,
    checksumSha256,
    storageUri,
    privilegeLevel = DOCUMENT_PRIVILEGE_LEVEL.CONFIDENTIAL,
    classification = DOCUMENT_CLASSIFICATION.CORRESPONDENCE,
    isEncrypted = true,
    createdById = 'SYSTEM'
  }) {
    if (!matterId || typeof matterId !== 'string') {
      throw new DocumentObjectError('Associated legal matter ID is required', 'DOC_ERR_INVALID_MATTER');
    }

    if (!title || typeof title !== 'string' || title.trim().length === 0) {
      throw new DocumentObjectError('Document title is required', 'DOC_ERR_INVALID_TITLE');
    }

    if (!filename || typeof filename !== 'string' || filename.trim().length === 0) {
      throw new DocumentObjectError('Filename is required', 'DOC_ERR_INVALID_FILENAME');
    }

    if (!checksumSha256 || typeof checksumSha256 !== 'string' || checksumSha256.trim().length !== 64) {
      throw new DocumentObjectError('Valid 64-character SHA-256 checksum is required for integrity verification', 'DOC_ERR_INVALID_CHECKSUM');
    }

    if (!storageUri || typeof storageUri !== 'string') {
      throw new DocumentObjectError('Storage URI is required', 'DOC_ERR_INVALID_URI');
    }

    const normPriv = privilegeLevel.trim().toUpperCase();
    if (!Object.values(DOCUMENT_PRIVILEGE_LEVEL).includes(normPriv)) {
      throw new DocumentObjectError(`Invalid privilege level designation [${privilegeLevel}]`, 'DOC_ERR_INVALID_PRIVILEGE');
    }

    const normClass = classification.trim().toUpperCase();
    if (!Object.values(DOCUMENT_CLASSIFICATION).includes(normClass)) {
      throw new DocumentObjectError(`Invalid document classification [${classification}]`, 'DOC_ERR_INVALID_CLASS');
    }

    const initialAttributes = {
      matterId: matterId.trim(),
      title: title.trim(),
      filename: filename.trim(),
      mimeType: mimeType ? mimeType.trim() : 'application/octet-stream',
      sizeBytes: Math.max(0, Number(sizeBytes) || 0),
      checksumSha256: checksumSha256.trim().toLowerCase(),
      storageUri: storageUri.trim(),
      privilegeLevel: normPriv,
      classification: normClass,
      versionNumber: 1,
      versionHistory: [
        {
          version: 1,
          filename: filename.trim(),
          checksumSha256: checksumSha256.trim().toLowerCase(),
          storageUri: storageUri.trim(),
          sizeBytes: Math.max(0, Number(sizeBytes) || 0),
          createdAt: new Date().toISOString(),
          createdById
        }
      ],
      isEncrypted: Boolean(isEncrypted),
      isSigned: false,
      signatures: [],
      retentionPolicyId: 'STD_LEGAL_7_YEARS',
      popiaSensitive: true
    };

    super({
      id,
      tenantId,
      domain: 'DOCUMENT',
      attributes: initialAttributes,
      schemaVersion: '1.0.0',
      status: OBJECT_LIFECYCLE_STATES.ACTIVE,
      createdById
    });
  }

  /**
   * Registers a new version of the document, preserving full historical audit log.
   *
   * @param {Object} versionData
   * @param {string} versionData.filename - New version filename.
   * @param {number} versionData.sizeBytes - New file size.
   * @param {string} versionData.checksumSha256 - SHA-256 checksum of new file version.
   * @param {string} versionData.storageUri - Storage URI of new version file.
   * @param {string} operatorId - Attorney or operator uploading version.
   * @returns {Object} Revision state.
   */
  createNewVersion({ filename, sizeBytes, checksumSha256, storageUri }, operatorId = 'SYSTEM') {
    if (!checksumSha256 || typeof checksumSha256 !== 'string' || checksumSha256.trim().length !== 64) {
      throw new DocumentObjectError('Valid 64-character SHA-256 checksum required for version increment', 'DOC_ERR_INVALID_CHECKSUM');
    }

    if (!storageUri || typeof storageUri !== 'string') {
      throw new DocumentObjectError('Storage URI required for new version', 'DOC_ERR_INVALID_URI');
    }

    const nextVersion = this.attributes.versionNumber + 1;
    const newVersionRecord = {
      version: nextVersion,
      filename: filename ? filename.trim() : this.attributes.filename,
      checksumSha256: checksumSha256.trim().toLowerCase(),
      storageUri: storageUri.trim(),
      sizeBytes: Math.max(0, Number(sizeBytes) || 0),
      createdAt: new Date().toISOString(),
      createdById: operatorId
    };

    return this.updateAttributes(
      {
        versionNumber: nextVersion,
        filename: newVersionRecord.filename,
        checksumSha256: newVersionRecord.checksumSha256,
        storageUri: newVersionRecord.storageUri,
        sizeBytes: newVersionRecord.sizeBytes,
        versionHistory: [...this.attributes.versionHistory, newVersionRecord]
      },
      operatorId
    );
  }

  /**
   * Updates Attorney-Client Privilege or legal classification.
   *
   * @param {string} privilegeLevel - Standard DOCUMENT_PRIVILEGE_LEVEL constant.
   * @param {string} operatorId - Compliance Officer or Attorney updating privilege.
   * @returns {Object} Revision state.
   */
  updatePrivilegeLevel(privilegeLevel, operatorId = 'SYSTEM') {
    const normPriv = privilegeLevel ? privilegeLevel.trim().toUpperCase() : '';
    if (!Object.values(DOCUMENT_PRIVILEGE_LEVEL).includes(normPriv)) {
      throw new DocumentObjectError(`Invalid privilege level designation [${privilegeLevel}]`, 'DOC_ERR_INVALID_PRIVILEGE');
    }

    return this.updateAttributes({ privilegeLevel: normPriv }, operatorId);
  }

  /**
   * Records an electronic signature execution on the document.
   *
   * @param {Object} sigData
   * @param {string} sigData.signedBy - Identity/Email of signer.
   * @param {string} sigData.signatureHash - Cryptographic signature digest.
   * @param {string} [sigData.capacity='ATTORNEY'] - Legal capacity (e.g. ADVOCATE, CLIENT, NOTARY).
   * @param {string} operatorId - System or user recording signature.
   * @returns {Object} Revision state.
   */
  recordDigitalSignature({ signedBy, signatureHash, capacity = 'ATTORNEY' }, operatorId = 'SYSTEM') {
    if (!signedBy || typeof signedBy !== 'string') {
      throw new DocumentObjectError('Signer identity is required', 'DOC_ERR_INVALID_SIGNER');
    }

    if (!signatureHash || typeof signatureHash !== 'string') {
      throw new DocumentObjectError('Signature hash digest is required', 'DOC_ERR_INVALID_SIG_HASH');
    }

    const signatureEntry = {
      signatureId: `SIG-${Date.now()}`,
      signedBy: signedBy.trim(),
      signatureHash: signatureHash.trim(),
      capacity: capacity.trim().toUpperCase(),
      timestamp: new Date().toISOString(),
      recordedBy: operatorId
    };

    return this.updateAttributes(
      {
        isSigned: true,
        signatures: [...this.attributes.signatures, signatureEntry]
      },
      operatorId
    );
  }

  /**
   * Convenience getter for Document Title.
   * @returns {string}
   */
  get title() {
    return this.attributes.title;
  }

  /**
   * Convenience getter for Checksum SHA-256.
   * @returns {string}
   */
  get checksumSha256() {
    return this.attributes.checksumSha256;
  }

  /**
   * Convenience getter for Privilege Level.
   * @returns {string}
   */
  get privilegeLevel() {
    return this.attributes.privilegeLevel;
  }

  /**
   * Generates a scrubbed summary of document metadata suitable for discovery indexing.
   * @returns {Object}
   */
  getSanitizedSummary() {
    return {
      documentId: this.id,
      tenantId: this.tenantId,
      matterId: this.attributes.matterId,
      title: this.attributes.title,
      filename: this.attributes.filename,
      mimeType: this.attributes.mimeType,
      sizeBytes: this.attributes.sizeBytes,
      checksumSha256: this.attributes.checksumSha256,
      privilegeLevel: this.attributes.privilegeLevel,
      classification: this.attributes.classification,
      versionNumber: this.attributes.versionNumber,
      isEncrypted: this.attributes.isEncrypted,
      isSigned: this.attributes.isSigned,
      signatureCount: this.attributes.signatures.length,
      status: this.status,
      revisionNumber: this.revisionNumber,
      updatedAt: this.updatedAt
    };
  }
}

module.exports = {
  DocumentObject,
  DocumentObjectError,
  DOCUMENT_PRIVILEGE_LEVEL,
  DOCUMENT_CLASSIFICATION
};
