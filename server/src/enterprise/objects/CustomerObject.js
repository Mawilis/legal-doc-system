/**
 * ============================================================================
 * WILSY OS - CUSTOMER ENTERPRISE OBJECT
 * ============================================================================
 *
 * @file         CustomerObject.js
 * @directory    server/src/enterprise/objects/
 * @system       Wilsy OS - Legal Enterprise Operating System & SaaS Platform
 * @authority    Wilson Khanyezi, Founder & Chief Architect
 * @version      1.0.0-SOVEREIGN
 * @epitome      Generation 2 Sovereign Customer Kernel Object implementation.
 *               Serves as the foundational client domain entity in Wilsy OS.
 *               Encapsulates Natural and Juristic Person identities, FICA statutory
 *               due diligence records, POPIA Section 13 data processing consent,
 *               AML risk scores, and primary communication parameters.
 *
 * @collaboration
 * - Lead Architect: Wilson Khanyezi (Wilsy OS Architecture Core Team)
 * - Practice Management: Client Relations & Account Intake Core
 * - Statutory Compliance: FICA, Anti-Money Laundering & POPIA Compliance Core
 *
 * ============================================================================
 * INSTITUTIONAL AUDIT TRAIL
 * ============================================================================
 * Date       | Author          | Version | Description
 * -----------|-----------------|---------|------------------------------------
 * 2026-07-24 | Wilson Khanyezi | 1.0.0   | Production-ready Customer domain object
 *            |                 |         | with FICA verification, POPIA consent
 *            |                 |         | tracking, and juristic entity profiles.
 * ============================================================================
 */

const { BaseEnterpriseObject, OBJECT_LIFECYCLE_STATES } = require('./BaseEnterpriseObject');
const { DataRedactor } = require('../kernel/EnterpriseKernel');

/**
 * Recognized Legal Entity Types.
 */
const CUSTOMER_TYPE = Object.freeze({
  INDIVIDUAL: 'INDIVIDUAL',
  JURISTIC_COMPANY: 'JURISTIC_COMPANY',
  TRUST: 'TRUST',
  PARTNERSHIP: 'PARTNERSHIP',
  GOVERNMENT_BODY: 'GOVERNMENT_BODY',
  NON_PROFIT: 'NON_PROFIT'
});

/**
 * FICA Statutory Compliance Verification States.
 */
const FICA_STATUS = Object.freeze({
  UNVERIFIED: 'UNVERIFIED',
  PENDING_DOCUMENTS: 'PENDING_DOCUMENTS',
  VERIFIED: 'VERIFIED',
  EXPIRED: 'EXPIRED',
  REJECTED: 'REJECTED'
});

/**
 * POPIA (Protection of Personal Information Act) Data Processing Consent States.
 */
const POPIA_CONSENT_STATE = Object.freeze({
  PENDING: 'PENDING',
  GRANTED: 'GRANTED',
  REVOKED: 'REVOKED',
  EXEMPT: 'EXEMPT'
});

/**
 * Anti-Money Laundering (AML) & FICA Risk Classifications.
 */
const RISK_RATING = Object.freeze({
  LOW: 'LOW',
  MEDIUM: 'MEDIUM',
  HIGH: 'HIGH',
  PROHIBITED: 'PROHIBITED'
});

/**
 * Custom Error Class for Customer Domain Faults.
 */
class CustomerObjectError extends Error {
  /**
   * @param {string} message - Error details.
   * @param {string} [code='CUST_ERR_GENERIC'] - Standard error code.
   * @param {Object} [details={}] - Additional contextual metadata.
   */
  constructor(message, code = 'CUST_ERR_GENERIC', details = {}) {
    super(message);
    this.name = 'CustomerObjectError';
    this.code = code;
    this.timestamp = new Date().toISOString();
    this.details = DataRedactor.sanitize(details);
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, CustomerObjectError);
    }
  }
}

/**
 * Sovereign Customer / Client Domain Object.
 * Encapsulates client legal profiles, contact channels, FICA statutory verification,
 * POPIA consent compliance, and AML risk categorization in Wilsy OS.
 */
class CustomerObject extends BaseEnterpriseObject {
  /**
   * Constructs a CustomerObject.
   *
   * @param {Object} params
   * @param {string} params.id - Unique Customer Identifier (e.g. 'CUST-2026-9012').
   * @param {string} params.tenantId - Sovereign Tenant ID.
   * @param {string} params.legalName - Full Legal Name or Company Registered Name.
   * @param {string} [params.customerType='INDIVIDUAL'] - Entity type constant.
   * @param {string} [params.registrationNumber=null] - RSA ID Number or CIPC Registration Number.
   * @param {string} params.primaryEmail - Official email address for billing and notices.
   * @param {string} params.primaryPhone - Phone number.
   * @param {Object} [params.physicalAddress={}] - Structured address object.
   * @param {string} [params.ficaStatus='UNVERIFIED'] - Initial FICA verification state.
   * @param {string} [params.popiaConsent='PENDING'] - Initial POPIA consent state.
   * @param {string} [params.riskRating='LOW'] - AML risk classification.
   * @param {boolean} [params.isPep=false] - Politically Exposed Person flag.
   * @param {string} [params.createdById='SYSTEM'] - Operator onboarding client.
   */
  constructor({
    id,
    tenantId,
    legalName,
    customerType = CUSTOMER_TYPE.INDIVIDUAL,
    registrationNumber = null,
    primaryEmail,
    primaryPhone,
    physicalAddress = {},
    ficaStatus = FICA_STATUS.UNVERIFIED,
    popiaConsent = POPIA_CONSENT_STATE.PENDING,
    riskRating = RISK_RATING.LOW,
    isPep = false,
    createdById = 'SYSTEM'
  }) {
    if (!legalName || typeof legalName !== 'string' || legalName.trim().length === 0) {
      throw new CustomerObjectError('Legal name is required to onboard a customer', 'CUST_ERR_INVALID_NAME');
    }

    if (!primaryEmail || typeof primaryEmail !== 'string' || !primaryEmail.includes('@')) {
      throw new CustomerObjectError('A valid primary email address is required', 'CUST_ERR_INVALID_EMAIL');
    }

    if (!primaryPhone || typeof primaryPhone !== 'string' || primaryPhone.trim().length < 5) {
      throw new CustomerObjectError('A valid contact phone number is required', 'CUST_ERR_INVALID_PHONE');
    }

    const normType = customerType.trim().toUpperCase();
    if (!Object.values(CUSTOMER_TYPE).includes(normType)) {
      throw new CustomerObjectError(`Invalid customer entity type [${customerType}]`, 'CUST_ERR_INVALID_TYPE');
    }

    const normFica = ficaStatus.trim().toUpperCase();
    if (!Object.values(FICA_STATUS).includes(normFica)) {
      throw new CustomerObjectError(`Invalid FICA status [${ficaStatus}]`, 'CUST_ERR_INVALID_FICA');
    }

    const normPopia = popiaConsent.trim().toUpperCase();
    if (!Object.values(POPIA_CONSENT_STATE).includes(normPopia)) {
      throw new CustomerObjectError(`Invalid POPIA consent state [${popiaConsent}]`, 'CUST_ERR_INVALID_POPIA');
    }

    const normRisk = riskRating.trim().toUpperCase();
    if (!Object.values(RISK_RATING).includes(normRisk)) {
      throw new CustomerObjectError(`Invalid risk rating [${riskRating}]`, 'CUST_ERR_INVALID_RISK');
    }

    const initialAttributes = {
      legalName: legalName.trim(),
      customerType: normType,
      registrationNumber: registrationNumber ? registrationNumber.trim() : null,
      primaryEmail: primaryEmail.trim().toLowerCase(),
      primaryPhone: primaryPhone.trim(),
      physicalAddress: DataRedactor.sanitize(physicalAddress),
      ficaStatus: normFica,
      ficaVerifiedAt: normFica === FICA_STATUS.VERIFIED ? new Date().toISOString() : null,
      ficaVerifiedBy: normFica === FICA_STATUS.VERIFIED ? createdById : null,
      ficaDocuments: [],
      popiaConsentState: normPopia,
      popiaConsentGrantedAt: normPopia === POPIA_CONSENT_STATE.GRANTED ? new Date().toISOString() : null,
      riskRating: normRisk,
      isPep: Boolean(isPep),
      activeMattersCount: 0
    };

    super({
      id,
      tenantId,
      domain: 'CUSTOMER',
      attributes: initialAttributes,
      schemaVersion: '1.0.0',
      status: OBJECT_LIFECYCLE_STATES.ACTIVE,
      createdById
    });
  }

  /**
   * Updates FICA statutory compliance state following due diligence review.
   *
   * @param {Object} ficaData
   * @param {string} ficaData.status - New FICA_STATUS constant.
   * @param {Array<Object>} [ficaData.documents=[]] - Verification documents metadata.
   * @param {string} operatorId - Compliance Officer identity.
   * @returns {Object} Revision state.
   */
  updateFicaCompliance({ status, documents = [] }, operatorId = 'SYSTEM') {
    const normStatus = status ? status.trim().toUpperCase() : '';
    if (!Object.values(FICA_STATUS).includes(normStatus)) {
      throw new CustomerObjectError(`Invalid FICA compliance state [${status}]`, 'CUST_ERR_INVALID_FICA_STATE');
    }

    const sanitizedDocs = DataRedactor.sanitize(documents);

    return this.updateAttributes(
      {
        ficaStatus: normStatus,
        ficaVerifiedAt: normStatus === FICA_STATUS.VERIFIED ? new Date().toISOString() : this.attributes.ficaVerifiedAt,
        ficaVerifiedBy: normStatus === FICA_STATUS.VERIFIED ? operatorId : this.attributes.ficaVerifiedBy,
        ficaDocuments: [...this.attributes.ficaDocuments, ...sanitizedDocs]
      },
      operatorId
    );
  }

  /**
   * Records explicit POPIA consent action by client or legal representative.
   *
   * @param {string} consentState - Target state from POPIA_CONSENT_STATE.
   * @param {string} operatorId - User updating consent record.
   * @returns {Object} Revision state.
   */
  updatePopiaConsent(consentState, operatorId = 'SYSTEM') {
    const normConsent = consentState ? consentState.trim().toUpperCase() : '';
    if (!Object.values(POPIA_CONSENT_STATE).includes(normConsent)) {
      throw new CustomerObjectError(`Invalid POPIA consent designation [${consentState}]`, 'CUST_ERR_INVALID_POPIA_STATE');
    }

    return this.updateAttributes(
      {
        popiaConsentState: normConsent,
        popiaConsentGrantedAt: normConsent === POPIA_CONSENT_STATE.GRANTED ? new Date().toISOString() : null
      },
      operatorId
    );
  }

  /**
   * Updates primary contact coordinates.
   *
   * @param {Object} contactData
   * @param {string} [contactData.primaryEmail] - New email address.
   * @param {string} [contactData.primaryPhone] - New phone number.
   * @param {Object} [contactData.physicalAddress] - Updated physical address.
   * @param {string} operatorId - User updating contact details.
   * @returns {Object} Revision state.
   */
  updateContactDetails({ primaryEmail, primaryPhone, physicalAddress }, operatorId = 'SYSTEM') {
    const updates = {};

    if (primaryEmail) {
      if (!primaryEmail.includes('@')) {
        throw new CustomerObjectError('Invalid email format', 'CUST_ERR_INVALID_EMAIL');
      }
      updates.primaryEmail = primaryEmail.trim().toLowerCase();
    }

    if (primaryPhone) {
      if (primaryPhone.trim().length < 5) {
        throw new CustomerObjectError('Invalid phone number length', 'CUST_ERR_INVALID_PHONE');
      }
      updates.primaryPhone = primaryPhone.trim();
    }

    if (physicalAddress && typeof physicalAddress === 'object') {
      updates.physicalAddress = DataRedactor.sanitize(physicalAddress);
    }

    return this.updateAttributes(updates, operatorId);
  }

  /**
   * Convenience getter for Legal Name.
   * @returns {string}
   */
  get legalName() {
    return this.attributes.legalName;
  }

  /**
   * Convenience getter for FICA Verification Status.
   * @returns {string}
   */
  get ficaStatus() {
    return this.attributes.ficaStatus;
  }

  /**
   * Convenience getter for POPIA Consent State.
   * @returns {string}
   */
  get popiaConsentState() {
    return this.attributes.popiaConsentState;
  }

  /**
   * Generates a scrubbed overview of customer profile for firm directory.
   * @returns {Object}
   */
  getSanitizedSummary() {
    return {
      customerId: this.id,
      tenantId: this.tenantId,
      legalName: this.attributes.legalName,
      customerType: this.attributes.customerType,
      registrationNumber: this.attributes.registrationNumber,
      primaryEmail: this.attributes.primaryEmail,
      primaryPhone: this.attributes.primaryPhone,
      ficaStatus: this.attributes.ficaStatus,
      popiaConsentState: this.attributes.popiaConsentState,
      riskRating: this.attributes.riskRating,
      isPep: this.attributes.isPep,
      activeMattersCount: this.attributes.activeMattersCount,
      status: this.status,
      revisionNumber: this.revisionNumber,
      updatedAt: this.updatedAt
    };
  }
}

module.exports = {
  CustomerObject,
  CustomerObjectError,
  CUSTOMER_TYPE,
  FICA_STATUS,
  POPIA_CONSENT_STATE,
  RISK_RATING
};
