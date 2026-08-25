/**
 * ============================================================================
 * WILSY OS - DISBURSEMENT ENTERPRISE OBJECT
 * ============================================================================
 *
 * @file         DisbursementObject.js
 * @directory    server/src/enterprise/objects/
 * @system       Wilsy OS - Legal Enterprise Operating System & SaaS Platform
 * @authority    Wilson Khanyezi, Founder & Chief Architect
 * @version      1.0.0-SOVEREIGN
 * @epitome      Generation 2 Sovereign Disbursement Kernel Object implementation.
 *               Serves as the client expense & out-of-pocket ledger domain entity in Wilsy OS.
 *               Manages advocate fee notes, court fees, sheriff fees, expert witness charges,
 *               and VAT agent/principal tax classification under LPC & SARS rules.
 *
 * @collaboration
 * - Lead Architect: Wilson Khanyezi (Wilsy OS Architecture Core Team)
 * - Practice Accounting: Client Expense & Accounts Payable Core
 * - Revenue Systems: Invoice Billing & Disbursement Ledger Subsystem
 *
 * ============================================================================
 * INSTITUTIONAL AUDIT TRAIL
 * ============================================================================
 * Date       | Author          | Version | Description
 * -----------|-----------------|---------|------------------------------------
 * 2026-07-24 | Wilson Khanyezi | 1.0.0   | Production-ready Disbursement domain object
 *            |                 |         | with agent/principal VAT rules, invoice
 *            |                 |         | linkage locks, and vendor auditing.
 * ============================================================================
 */

const { BaseEnterpriseObject, OBJECT_LIFECYCLE_STATES } = require('./BaseEnterpriseObject');
const { DataRedactor } = require('../kernel/EnterpriseKernel');

/**
 * Recognized Legal Disbursement Expense Categories.
 */
const DISBURSEMENT_TYPE = Object.freeze({
  SHERIFF_FEE: 'SHERIFF_FEE',
  ADVOCATE_FEE_NOTE: 'ADVOCATE_FEE_NOTE',
  COURT_STAMP_FEE: 'COURT_STAMP_FEE',
  EXPERT_WITNESS_FEE: 'EXPERT_WITNESS_FEE',
  CORRESPONDENT_ATTORNEY_FEE: 'CORRESPONDENT_ATTORNEY_FEE',
  TRACER_FEE: 'TRACER_FEE',
  DEEDS_OFFICE_FEE: 'DEEDS_OFFICE_FEE',
  TRAVEL_LODGING: 'TRAVEL_LODGING',
  GENERAL_EXPENSE: 'GENERAL_EXPENSE'
});

/**
 * Operational Billing Status for Disbursements.
 */
const DISBURSEMENT_STATUS = Object.freeze({
  UNBILLED: 'UNBILLED',
  INVOICED: 'INVOICED',
  PAID: 'PAID',
  WRITTEN_OFF: 'WRITTEN_OFF'
});

/**
 * Custom Error Class for Disbursement Domain Faults.
 */
class DisbursementObjectError extends Error {
  /**
   * @param {string} message - Error details.
   * @param {string} [code='DISB_ERR_GENERIC'] - Standard error code.
   * @param {Object} [details={}] - Additional contextual metadata.
   */
  constructor(message, code = 'DISB_ERR_GENERIC', details = {}) {
    super(message);
    this.name = 'DisbursementObjectError';
    this.code = code;
    this.timestamp = new Date().toISOString();
    this.details = DataRedactor.sanitize(details);
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, DisbursementObjectError);
    }
  }
}

/**
 * Sovereign Disbursement Domain Object.
 * Encapsulates out-of-pocket client expenses, advocate fee notes, vendor invoices,
 * VAT agent/principal classifications, and invoice attachment lifecycles in Wilsy OS.
 */
class DisbursementObject extends BaseEnterpriseObject {
  /**
   * Constructs a DisbursementObject.
   *
   * @param {Object} params
   * @param {string} params.id - Unique Disbursement Identifier (e.g. 'DISB-2026-3011').
   * @param {string} params.tenantId - Sovereign Tenant ID.
   * @param {string} params.matterId - Associated Legal Matter ID.
   * @param {string} params.customerId - Client Customer ID receiving billing.
   * @param {string} [params.disbursementType='GENERAL_EXPENSE'] - Expense category constant.
   * @param {string} params.description - Narrative breakdown of expense incurred.
   * @param {number} params.amountExcludingVat - Subtotal amount before tax.
   * @param {number} [params.vatRate=0.15] - Standard VAT rate (15% in RSA).
   * @param {string} [params.vendorName=null] - Payee / Supplier Name (e.g. 'Sheriff Johannesburg').
   * @param {string} [params.voucherReference=null] - Third-party invoice / receipt reference.
   * @param {boolean} [params.isAgentDisbursement=false] - SARS Section 54 Agent vs Principal flag.
   * @param {string} [params.createdById='SYSTEM'] - Operator recording disbursement.
   */
  constructor({
    id,
    tenantId,
    matterId,
    customerId,
    disbursementType = DISBURSEMENT_TYPE.GENERAL_EXPENSE,
    description,
    amountExcludingVat,
    vatRate = 0.15,
    vendorName = null,
    voucherReference = null,
    isAgentDisbursement = false,
    createdById = 'SYSTEM'
  }) {
    if (!matterId || typeof matterId !== 'string') {
      throw new DisbursementObjectError('Associated matter ID is required', 'DISB_ERR_INVALID_MATTER');
    }

    if (!customerId || typeof customerId !== 'string') {
      throw new DisbursementObjectError('Associated customer ID is required', 'DISB_ERR_INVALID_CUSTOMER');
    }

    if (!description || typeof description !== 'string' || description.trim().length === 0) {
      throw new DisbursementObjectError('Disbursement narrative description is required', 'DISB_ERR_INVALID_DESCRIPTION');
    }

    const subtotal = Number(amountExcludingVat);
    if (isNaN(subtotal) || subtotal <= 0) {
      throw new DisbursementObjectError('Amount excluding VAT must be a positive number', 'DISB_ERR_INVALID_AMOUNT');
    }

    const rate = Number(vatRate);
    if (isNaN(rate) || rate < 0 || rate > 1) {
      throw new DisbursementObjectError('VAT rate must be a valid decimal fraction between 0.0 and 1.0', 'DISB_ERR_INVALID_VAT_RATE');
    }

    const normType = disbursementType.trim().toUpperCase();
    if (!Object.values(DISBURSEMENT_TYPE).includes(normType)) {
      throw new DisbursementObjectError(`Invalid disbursement type [${disbursementType}]`, 'DISB_ERR_INVALID_TYPE');
    }

    const taxAmount = Number((subtotal * rate).toFixed(2));
    const totalAmount = Number((subtotal + taxAmount).toFixed(2));

    const initialAttributes = {
      matterId: matterId.trim(),
      customerId: customerId.trim(),
      disbursementType: normType,
      description: description.trim(),
      amountExcludingVat: Number(subtotal.toFixed(2)),
      vatRate: rate,
      vatAmount: taxAmount,
      totalAmount: totalAmount,
      vendorName: vendorName ? vendorName.trim() : null,
      voucherReference: voucherReference ? voucherReference.trim() : null,
      isAgentDisbursement: Boolean(isAgentDisbursement),
      disbursementStatus: DISBURSEMENT_STATUS.UNBILLED,
      invoiceId: null,
      invoicedAt: null,
      paidAt: null,
      paymentReference: null,
      writeOffReason: null
    };

    super({
      id,
      tenantId,
      domain: 'DISBURSEMENT',
      attributes: initialAttributes,
      schemaVersion: '1.0.0',
      status: OBJECT_LIFECYCLE_STATES.ACTIVE,
      createdById
    });
  }

  /**
   * Links unbilled disbursement to an issued or draft tax invoice.
   *
   * @param {string} invoiceId - Target Invoice ID.
   * @param {string} operatorId - Billing clerk or partner linking expense.
   * @returns {Object} Revision state.
   */
  linkToInvoice(invoiceId, operatorId = 'SYSTEM') {
    if (this.attributes.disbursementStatus !== DISBURSEMENT_STATUS.UNBILLED) {
      throw new DisbursementObjectError(
        `Cannot link disbursement in status [${this.attributes.disbursementStatus}] to invoice`,
        'DISB_ERR_LOCKED_STATUS'
      );
    }

    if (!invoiceId || typeof invoiceId !== 'string') {
      throw new DisbursementObjectError('Valid target invoice ID is required', 'DISB_ERR_INVALID_INVOICE');
    }

    return this.updateAttributes(
      {
        disbursementStatus: DISBURSEMENT_STATUS.INVOICED,
        invoiceId: invoiceId.trim(),
        invoicedAt: new Date().toISOString()
      },
      operatorId
    );
  }

  /**
   * Marks invoiced disbursement as fully settled / paid.
   *
   * @param {string} [paymentReference=null] - Banking / settlement reference.
   * @param {string} operatorId - Operator recording payment.
   * @returns {Object} Revision state.
   */
  markAsPaid(paymentReference = null, operatorId = 'SYSTEM') {
    if (
      this.attributes.disbursementStatus !== DISBURSEMENT_STATUS.INVOICED &&
      this.attributes.disbursementStatus !== DISBURSEMENT_STATUS.UNBILLED
    ) {
      throw new DisbursementObjectError(
        `Cannot mark disbursement in status [${this.attributes.disbursementStatus}] as paid`,
        'DISB_ERR_INVALID_PAYMENT_STATE'
      );
    }

    return this.updateAttributes(
      {
        disbursementStatus: DISBURSEMENT_STATUS.PAID,
        paidAt: new Date().toISOString(),
        paymentReference: paymentReference ? paymentReference.trim() : null
      },
      operatorId
    );
  }

  /**
   * Writes off disbursement in the event of bad debt or unrecoverable client expense.
   *
   * @param {string} reason - Accounting explanation for write-off.
   * @param {string} operatorId - Authorizing Senior Partner identity.
   * @returns {Object} Revision state.
   */
  writeOff(reason, operatorId = 'SYSTEM') {
    if (!reason || typeof reason !== 'string' || reason.trim().length === 0) {
      throw new DisbursementObjectError('Write-off justification reason is required', 'DISB_ERR_REASON_REQUIRED');
    }

    if (this.attributes.disbursementStatus === DISBURSEMENT_STATUS.PAID) {
      throw new DisbursementObjectError('Cannot write off a paid disbursement', 'DISB_ERR_PAID_WRITE_OFF_PROHIBITED');
    }

    return this.updateAttributes(
      {
        disbursementStatus: DISBURSEMENT_STATUS.WRITTEN_OFF,
        writeOffReason: reason.trim()
      },
      operatorId
    );
  }

  /**
   * Convenience getter for Total Amount.
   * @returns {number}
   */
  get totalAmount() {
    return this.attributes.totalAmount;
  }

  /**
   * Convenience getter for Disbursement Status.
   * @returns {string}
   */
  get disbursementStatus() {
    return this.attributes.disbursementStatus;
  }

  /**
   * Convenience getter for Invoice ID link.
   * @returns {string|null}
   */
  get invoiceId() {
    return this.attributes.invoiceId;
  }

  /**
   * Generates a scrubbed overview of disbursement metadata for billing ledgers.
   * @returns {Object}
   */
  getSanitizedSummary() {
    return {
      disbursementId: this.id,
      tenantId: this.tenantId,
      matterId: this.attributes.matterId,
      customerId: this.attributes.customerId,
      disbursementType: this.attributes.disbursementType,
      description: this.attributes.description,
      amountExcludingVat: this.attributes.amountExcludingVat,
      vatAmount: this.attributes.vatAmount,
      totalAmount: this.attributes.totalAmount,
      vendorName: this.attributes.vendorName,
      voucherReference: this.attributes.voucherReference,
      isAgentDisbursement: this.attributes.isAgentDisbursement,
      disbursementStatus: this.attributes.disbursementStatus,
      invoiceId: this.attributes.invoiceId,
      status: this.status,
      revisionNumber: this.revisionNumber,
      updatedAt: this.updatedAt
    };
  }
}

module.exports = {
  DisbursementObject,
  DisbursementObjectError,
  DISBURSEMENT_TYPE,
  DISBURSEMENT_STATUS
};
