/**
 * ============================================================================
 * WILSY OS - CONTRACT ENTERPRISE OBJECT
 * ============================================================================
 *
 * @file         ContractObject.js
 * @directory    server/src/enterprise/objects/
 * @system       Wilsy OS - Legal Enterprise Operating System & SaaS Platform
 * @authority    Wilson Khanyezi, Founder & Chief Architect
 * @version      1.0.0-SOVEREIGN
 * @epitome      Generation 2 Sovereign Contract Kernel Object implementation.
 *               Provides immutable legal document state tracking, multi-party
 *               cryptographic signature recordation, automated valuation updates,
 *               jurisdictional lock verification, and POPIA/GDPR redactor integration.
 *
 * @collaboration
 * - Lead Architect: Wilson Khanyezi (Wilsy OS Architecture Core Team)
 * - Legal Engineering: Sovereign Document Integrity & Multi-Party Cryptography
 * - Compliance Engine: Regulatory Jurisdiction & Execution Audit Standard
 *
 * ============================================================================
 * INSTITUTIONAL AUDIT TRAIL
 * ============================================================================
 * Date       | Author          | Version | Description
 * -----------|-----------------|---------|------------------------------------
 * 2026-07-24 | Wilson Khanyezi | 1.0.0   | Production-ready Contract domain object
 *            |                 |         | with cryptographic signature tracking
 *            |                 |         | and jurisdictional legal audit trails.
 * ============================================================================
 */

const crypto = require('crypto');
const { BaseEnterpriseObject, OBJECT_LIFECYCLE_STATES } = require('./BaseEnterpriseObject');
const { DataRedactor } = require('../kernel/EnterpriseKernel');

/**
 * Custom Error Class for Contract Domain Violations.
 */
class ContractObjectError extends Error {
  /**
   * @param {string} message - Error details.
   * @param {string} [code='CONTRACT_ERR_GENERIC'] - Standard error code.
   * @param {Object} [details={}] - Additional contextual metadata.
   */
  constructor(message, code = 'CONTRACT_ERR_GENERIC', details = {}) {
    super(message);
    this.name = 'ContractObjectError';
    this.code = code;
    this.timestamp = new Date().toISOString();
    this.details = DataRedactor.sanitize(details);
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, ContractObjectError);
    }
  }
}

/**
 * Sovereign Contract Domain Object.
 * Encapsulates legal agreements, bilateral/multilateral execution state,
 * and immutable signature proofs within Wilsy OS.
 */
class ContractObject extends BaseEnterpriseObject {
  /**
   * Constructs a ContractObject.
   *
   * @param {Object} params
   * @param {string} params.id - Unique Contract Identifier (e.g., 'CTR-2026-0089').
   * @param {string} params.tenantId - Sovereign Tenant ID.
   * @param {string} params.title - Contract Title / Matter Reference.
   * @param {number} [params.value=0] - Total monetary value of contract.
   * @param {string} [params.currency='ZAR'] - ISO 4217 Currency Code (ZAR, USD, EUR, GBP).
   * @param {string} [params.jurisdiction='ZA_GAUTENG'] - Legal governing jurisdiction.
   * @param {string} [params.effectiveDate] - ISO Date string when agreement becomes binding.
   * @param {string} [params.expirationDate] - ISO Date string when agreement terminates.
   * @param {Array<Object>} [params.signatories=[]] - List of required contract signatories.
   * @param {string} [params.createdById='SYSTEM'] - Operator ID responsible for drafting.
   */
  constructor({
    id,
    tenantId,
    title,
    value = 0,
    currency = 'ZAR',
    jurisdiction = 'ZA_GAUTENG',
    effectiveDate = new Date().toISOString(),
    expirationDate = null,
    signatories = [],
    createdById = 'SYSTEM'
  }) {
    if (!title || typeof title !== 'string' || title.trim().length === 0) {
      throw new ContractObjectError('Contract title must be a non-empty string', 'CTR_ERR_INVALID_TITLE');
    }

    const numericValue = Number(value);
    if (isNaN(numericValue) || numericValue < 0) {
      throw new ContractObjectError('Contract value must be a non-negative number', 'CTR_ERR_INVALID_VALUE');
    }

    const initialAttributes = {
      title: title.trim(),
      value: numericValue,
      currency: currency.trim().toUpperCase(),
      jurisdiction: jurisdiction.trim().toUpperCase(),
      effectiveDate,
      expirationDate,
      signatories: signatories.map(sig => ({
        id: sig.id || `sig_${crypto.randomBytes(6).toString('hex')}`,
        name: sig.name ? sig.name.trim() : 'UNNAMED_SIGNATORY',
        email: sig.email ? sig.email.trim().toLowerCase() : '',
        role: sig.role ? sig.role.trim().toUpperCase() : 'PARTY',
        hasSigned: Boolean(sig.hasSigned),
        signedAt: sig.signedAt || null,
        signatureProofHash: sig.signatureProofHash || null
      }))
    };

    super({
      id,
      tenantId,
      domain: 'CONTRACT',
      attributes: initialAttributes,
      schemaVersion: '1.0.0',
      status: OBJECT_LIFECYCLE_STATES.DRAFT,
      createdById
    });
  }

  /**
   * Adds a required signatory to the contract prior to final execution.
   *
   * @param {Object} signatory - Signatory details.
   * @param {string} signatory.name - Full Name of signing authority.
   * @param {string} signatory.email - Email address for dispatching signing challenge.
   * @param {string} [signatory.role='PARTY'] - Legal role (e.g., 'CLIENT', 'WITNESS', 'ATTORNEY').
   * @param {string} operatorId - User modifying contract requirements.
   * @returns {Object} Revision result.
   */
  addSignatory({ name, email, role = 'PARTY' }, operatorId = 'SYSTEM') {
    if (this.status !== OBJECT_LIFECYCLE_STATES.DRAFT) {
      throw new ContractObjectError(
        `Signatories can only be added while contract is in DRAFT state. Current status: [${this.status}]`,
        'CTR_ERR_MUTATION_FORBIDDEN'
      );
    }

    if (!email || !email.includes('@')) {
      throw new ContractObjectError('Valid signatory email required', 'CTR_ERR_INVALID_EMAIL');
    }

    const existing = this.attributes.signatories.find(s => s.email === email.trim().toLowerCase());
    if (existing) {
      throw new ContractObjectError(`Signatory with email [${email}] is already registered`, 'CTR_ERR_DUPLICATE_SIGNATORY');
    }

    const newSignatory = {
      id: `sig_${crypto.randomBytes(6).toString('hex')}`,
      name: name.trim(),
      email: email.trim().toLowerCase(),
      role: role.trim().toUpperCase(),
      hasSigned: false,
      signedAt: null,
      signatureProofHash: null
    };

    const updatedSignatories = [...this.attributes.signatories, newSignatory];
    return this.updateAttributes({ signatories: updatedSignatories }, operatorId);
  }

  /**
   * Records an immutable cryptographic signature proof for a designated party.
   * Automatically promotes contract state to ACTIVE if all signatories complete execution.
   *
   * @param {string} signatoryEmail - Registered email of signing party.
   * @param {string} signatureDataPayload - Raw digital signature payload or biometric hash.
   * @param {string} operatorId - Signing challenge trigger operator.
   * @returns {Object} Signature verification & execution state.
   */
  recordSignature(signatoryEmail, signatureDataPayload, operatorId = 'SYSTEM') {
    if (this.status === OBJECT_LIFECYCLE_STATES.ARCHIVED || this.status === OBJECT_LIFECYCLE_STATES.DELETED) {
      throw new ContractObjectError(
        `Cannot sign contract in terminal state [${this.status}]`,
        'CTR_ERR_TERMINAL_STATE'
      );
    }

    const normalizedEmail = signatoryEmail.trim().toLowerCase();
    const signatoryIndex = this.attributes.signatories.findIndex(s => s.email === normalizedEmail);

    if (signatoryIndex === -1) {
      throw new ContractObjectError(
        `Signatory [${normalizedEmail}] is not listed on this contract`,
        'CTR_ERR_SIGNATORY_NOT_FOUND'
      );
    }

    if (this.attributes.signatories[signatoryIndex].hasSigned) {
      throw new ContractObjectError(
        `Signatory [${normalizedEmail}] has already executed this contract`,
        'CTR_ERR_ALREADY_SIGNED'
      );
    }

    // Generate cryptographic proof hash over signature payload
    const timestamp = new Date().toISOString();
    const proofString = `${this.id}:${normalizedEmail}:${timestamp}:${signatureDataPayload}`;
    const signatureProofHash = crypto.createHash('sha256').update(proofString).digest('hex');

    const updatedSignatories = [...this.attributes.signatories];
    updatedSignatories[signatoryIndex] = {
      ...updatedSignatories[signatoryIndex],
      hasSigned: true,
      signedAt: timestamp,
      signatureProofHash
    };

    const updateResult = this.updateAttributes({ signatories: updatedSignatories }, operatorId);

    // Check if contract execution is now 100% complete
    const isFullySigned = updatedSignatories.every(s => s.hasSigned);
    if (isFullySigned && this.status === OBJECT_LIFECYCLE_STATES.DRAFT) {
      this.transitionState(
        OBJECT_LIFECYCLE_STATES.ACTIVE,
        operatorId,
        'Contract fully executed by all designated signatories'
      );
    }

    return {
      success: true,
      isFullySigned,
      signatoryEmail: normalizedEmail,
      signatureProofHash,
      contractStatus: this.status,
      revisionResult: updateResult
    };
  }

  /**
   * Updates monetary contract value and currency safely.
   *
   * @param {number} newValue - Updated monetary value.
   * @param {string} [newCurrency] - Optional currency code update.
   * @param {string} operatorId - Finance / Attorney ID authorizing change.
   * @returns {Object} Update result.
   */
  updateContractValue(newValue, newCurrency, operatorId = 'SYSTEM') {
    const numericValue = Number(newValue);
    if (isNaN(numericValue) || numericValue < 0) {
      throw new ContractObjectError('New contract value must be a non-negative number', 'CTR_ERR_INVALID_VALUE');
    }

    const patch = { value: numericValue };
    if (newCurrency && typeof newCurrency === 'string') {
      patch.currency = newCurrency.trim().toUpperCase();
    }

    return this.updateAttributes(patch, operatorId);
  }

  /**
   * Inspects execution completeness.
   * @returns {boolean} True if all required signatories have executed signatures.
   */
  isFullyExecuted() {
    if (this.attributes.signatories.length === 0) return false;
    return this.attributes.signatories.every(s => s.hasSigned);
  }

  /**
   * Generates a scrubbed overview of contract state suitable for dashboards or APIs.
   * @returns {Object}
   */
  getSanitizedSummary() {
    return {
      contractId: this.id,
      tenantId: this.tenantId,
      title: this.attributes.title,
      value: this.attributes.value,
      currency: this.attributes.currency,
      jurisdiction: this.attributes.jurisdiction,
      status: this.status,
      effectiveDate: this.attributes.effectiveDate,
      totalSignatories: this.attributes.signatories.length,
      signedCount: this.attributes.signatories.filter(s => s.hasSigned).length,
      isFullyExecuted: this.isFullyExecuted(),
      revisionNumber: this.revisionNumber,
      updatedAt: this.updatedAt
    };
  }
}

module.exports = {
  ContractObject,
  ContractObjectError
};
