/**
 * ============================================================================
 * WILSY OS - PAYMENT RECEIPT ENTERPRISE OBJECT
 * ============================================================================
 *
 * @file         PaymentReceiptObject.js
 * @directory    server/src/enterprise/objects/
 * @system       Wilsy OS - Legal Enterprise Operating System & SaaS Platform
 * @authority    Wilson Khanyezi, Founder & Chief Architect
 * @version      1.0.0-SOVEREIGN
 * @epitome      Generation 2 Sovereign Payment Receipt Kernel Object implementation.
 *               Serves as the financial receipting and payment ledger domain entity.
 *               Enforces Section 86 Legal Practice Act trust vs. business account
 *               segregation, split invoice allocations, banking clearance states,
 *               and immutable reversal audit trails.
 *
 * @collaboration
 * - Lead Architect: Wilson Khanyezi (Wilsy OS Architecture Core Team)
 * - Practice Accounting: Trust & Business Accounting Ledger Core
 * - Statutory Compliance: LPC Section 86 & Banking Integrity Subsystem
 *
 * ============================================================================
 * INSTITUTIONAL AUDIT TRAIL
 * ============================================================================
 * Date       | Author          | Version | Description
 * -----------|-----------------|---------|------------------------------------
 * 2026-07-24 | Wilson Khanyezi | 1.0.0   | Production-ready Payment Receipt domain
 *            |                 |         | object with trust split allocations,
 *            |                 |         | clearance state locks, and reversal chains.
 * ============================================================================
 */

const { BaseEnterpriseObject, OBJECT_LIFECYCLE_STATES } = require('./BaseEnterpriseObject');
const { DataRedactor } = require('../kernel/EnterpriseKernel');

/**
 * Account Destination Types for Payments.
 */
const PAYMENT_ACCOUNT_TYPE = Object.freeze({
  TRUST_ACCOUNT: 'TRUST_ACCOUNT',
  BUSINESS_ACCOUNT: 'BUSINESS_ACCOUNT'
});

/**
 * Supported Legal Payment Channels.
 */
const PAYMENT_CHANNEL = Object.freeze({
  EFT_ELECTRONIC: 'EFT_ELECTRONIC',
  CREDIT_CARD: 'CREDIT_CARD',
  DEBIT_ORDER: 'DEBIT_ORDER',
  DIRECT_DEPOSIT: 'DIRECT_DEPOSIT',
  TRUST_TRANSFER: 'TRUST_TRANSFER'
});

/**
 * Operational Clearance States for Receipts.
 */
const PAYMENT_STATUS = Object.freeze({
  PENDING_CLEARANCE: 'PENDING_CLEARANCE',
  CLEARED: 'CLEARED',
  REVERSED: 'REVERSED',
  ALLOCATED_FULL: 'ALLOCATED_FULL',
  ALLOCATED_PARTIAL: 'ALLOCATED_PARTIAL'
});

/**
 * Custom Error Class for Payment Receipt Domain Faults.
 */
class PaymentReceiptObjectError extends Error {
  /**
   * @param {string} message - Error details.
   * @param {string} [code='PAY_ERR_GENERIC'] - Standard error code.
   * @param {Object} [details={}] - Additional contextual metadata.
   */
  constructor(message, code = 'PAY_ERR_GENERIC', details = {}) {
    super(message);
    this.name = 'PaymentReceiptObjectError';
    this.code = code;
    this.timestamp = new Date().toISOString();
    this.details = DataRedactor.sanitize(details);
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, PaymentReceiptObjectError);
    }
  }
}

/**
 * Sovereign Payment Receipt Domain Object.
 * Encapsulates client payments, trust/business account allocations, invoice linkage,
 * banking reference numbers, and transaction clearance lifecycles in Wilsy OS.
 */
class PaymentReceiptObject extends BaseEnterpriseObject {
  /**
   * Constructs a PaymentReceiptObject.
   *
   * @param {Object} params
   * @param {string} params.id - Unique Payment Receipt Identifier (e.g. 'RCT-2026-8801').
   * @param {string} params.tenantId - Sovereign Tenant ID.
   * @param {string} params.customerId - Paying Client Customer ID.
   * @param {string} [params.matterId=null] - Associated Legal Matter ID (if matter-specific).
   * @param {string} [params.accountType='TRUST_ACCOUNT'] - Destination account constant.
   * @param {string} [params.paymentChannel='EFT_ELECTRONIC'] - Payment channel constant.
   * @param {number} params.amount - Total ZAR amount received.
   * @param {string} params.paymentReference - Banking payment reference or transaction hash.
   * @param {string} [params.bankName=null] - Originating or receiving banking institution.
   * @param {string} [params.createdById='SYSTEM'] - Operator recording receipt.
   */
  constructor({
    id,
    tenantId,
    customerId,
    matterId = null,
    accountType = PAYMENT_ACCOUNT_TYPE.TRUST_ACCOUNT,
    paymentChannel = PAYMENT_CHANNEL.EFT_ELECTRONIC,
    amount,
    paymentReference,
    bankName = null,
    createdById = 'SYSTEM'
  }) {
    if (!customerId || typeof customerId !== 'string') {
      throw new PaymentReceiptObjectError('Client Customer ID is required to record a payment', 'PAY_ERR_INVALID_CUSTOMER');
    }

    const receiptAmount = Number(amount);
    if (isNaN(receiptAmount) || receiptAmount <= 0) {
      throw new PaymentReceiptObjectError('Receipt amount must be a positive number', 'PAY_ERR_INVALID_AMOUNT');
    }

    if (!paymentReference || typeof paymentReference !== 'string' || paymentReference.trim().length === 0) {
      throw new PaymentReceiptObjectError('Banking payment reference is required', 'PAY_ERR_INVALID_REFERENCE');
    }

    const normAccount = accountType.trim().toUpperCase();
    if (!Object.values(PAYMENT_ACCOUNT_TYPE).includes(normAccount)) {
      throw new PaymentReceiptObjectError(`Invalid account type designation [${accountType}]`, 'PAY_ERR_INVALID_ACCOUNT_TYPE');
    }

    const normChannel = paymentChannel.trim().toUpperCase();
    if (!Object.values(PAYMENT_CHANNEL).includes(normChannel)) {
      throw new PaymentReceiptObjectError(`Invalid payment channel [${paymentChannel}]`, 'PAY_ERR_INVALID_CHANNEL');
    }

    const initialAttributes = {
      customerId: customerId.trim(),
      matterId: matterId ? matterId.trim() : null,
      accountType: normAccount,
      paymentChannel: normChannel,
      amount: Number(receiptAmount.toFixed(2)),
      allocatedAmount: 0.0,
      unallocatedBalance: Number(receiptAmount.toFixed(2)),
      paymentReference: paymentReference.trim(),
      bankName: bankName ? bankName.trim() : null,
      paymentStatus: PAYMENT_STATUS.CLEARED,
      allocations: [],
      clearedAt: new Date().toISOString(),
      reversedAt: null,
      reversalReason: null,
      reversalOperatorId: null
    };

    super({
      id,
      tenantId,
      domain: 'PAYMENT_RECEIPT',
      attributes: initialAttributes,
      schemaVersion: '1.0.0',
      status: OBJECT_LIFECYCLE_STATES.ACTIVE,
      createdById
    });
  }

  /**
   * Allocates a portion or full amount of this receipt towards a specific invoice.
   *
   * @param {Object} params
   * @param {string} params.invoiceId - Target Invoice ID.
   * @param {number} params.amount - Amount in ZAR to allocate.
   * @param {string} [operatorId='SYSTEM'] - Operator executing allocation.
   * @returns {Object} Revision state.
   */
  allocateToInvoice({ invoiceId, amount }, operatorId = 'SYSTEM') {
    if (this.attributes.paymentStatus === PAYMENT_STATUS.REVERSED) {
      throw new PaymentReceiptObjectError('Cannot allocate funds from a reversed payment receipt', 'PAY_ERR_REVERSED_ALLOCATION_PROHIBITED');
    }

    if (!invoiceId || typeof invoiceId !== 'string') {
      throw new PaymentReceiptObjectError('Valid target invoice ID is required for allocation', 'PAY_ERR_INVALID_INVOICE');
    }

    const allocAmount = Number(amount);
    if (isNaN(allocAmount) || allocAmount <= 0) {
      throw new PaymentReceiptObjectError('Allocation amount must be a positive number', 'PAY_ERR_INVALID_ALLOC_AMOUNT');
    }

    const currentUnallocated = this.attributes.unallocatedBalance;
    if (allocAmount > currentUnallocated) {
      throw new PaymentReceiptObjectError(
        `Allocation amount [R${allocAmount.toFixed(2)}] exceeds available unallocated balance [R${currentUnallocated.toFixed(2)}]`,
        'PAY_ERR_EXCEEDS_UNALLOCATED'
      );
    }

    const newAllocated = Number((this.attributes.allocatedAmount + allocAmount).toFixed(2));
    const newUnallocated = Number((this.attributes.amount - newAllocated).toFixed(2));

    const newAllocationRecord = {
      invoiceId: invoiceId.trim(),
      amountAllocated: Number(allocAmount.toFixed(2)),
      allocatedAt: new Date().toISOString(),
      allocatedBy: operatorId
    };

    const nextStatus = newUnallocated === 0 ? PAYMENT_STATUS.ALLOCATED_FULL : PAYMENT_STATUS.ALLOCATED_PARTIAL;

    return this.updateAttributes(
      {
        allocatedAmount: newAllocated,
        unallocatedBalance: newUnallocated,
        paymentStatus: nextStatus,
        allocations: [...this.attributes.allocations, newAllocationRecord]
      },
      operatorId
    );
  }

  /**
   * Reverses a payment receipt in the event of a dishonored check, bank recall, or deposit error.
   *
   * @param {string} reason - Compliance reason for transaction reversal.
   * @param {string} operatorId - Authorizing Finance Officer ID.
   * @returns {Object} Revision state.
   */
  reversePayment(reason, operatorId = 'SYSTEM') {
    if (!reason || typeof reason !== 'string' || reason.trim().length === 0) {
      throw new PaymentReceiptObjectError('Reversal justification reason is required', 'PAY_ERR_REASON_REQUIRED');
    }

    if (this.attributes.paymentStatus === PAYMENT_STATUS.REVERSED) {
      throw new PaymentReceiptObjectError('Payment receipt has already been reversed', 'PAY_ERR_ALREADY_REVERSED');
    }

    if (this.attributes.allocatedAmount > 0) {
      throw new PaymentReceiptObjectError(
        'Cannot reverse a payment that has existing invoice allocations. De-allocate funds first.',
        'PAY_ERR_HAS_ALLOCATIONS'
      );
    }

    return this.updateAttributes(
      {
        paymentStatus: PAYMENT_STATUS.REVERSED,
        unallocatedBalance: 0.0,
        reversedAt: new Date().toISOString(),
        reversalReason: reason.trim(),
        reversalOperatorId: operatorId
      },
      operatorId
    );
  }

  /**
   * Convenience getter for Receipt Amount.
   * @returns {number}
   */
  get amount() {
    return this.attributes.amount;
  }

  /**
   * Convenience getter for Unallocated Balance.
   * @returns {number}
   */
  get unallocatedBalance() {
    return this.attributes.unallocatedBalance;
  }

  /**
   * Convenience getter for Account Type.
   * @returns {string}
   */
  get accountType() {
    return this.attributes.accountType;
  }

  /**
   * Convenience getter for Payment Status.
   * @returns {string}
   */
  get paymentStatus() {
    return this.attributes.paymentStatus;
  }

  /**
   * Generates a scrubbed overview of receipt metadata for financial auditing.
   * @returns {Object}
   */
  getSanitizedSummary() {
    return {
      receiptId: this.id,
      tenantId: this.tenantId,
      customerId: this.attributes.customerId,
      matterId: this.attributes.matterId,
      accountType: this.attributes.accountType,
      paymentChannel: this.attributes.paymentChannel,
      amount: this.attributes.amount,
      allocatedAmount: this.attributes.allocatedAmount,
      unallocatedBalance: this.attributes.unallocatedBalance,
      paymentReference: this.attributes.paymentReference,
      bankName: this.attributes.bankName,
      paymentStatus: this.attributes.paymentStatus,
      allocationCount: this.attributes.allocations.length,
      status: this.status,
      revisionNumber: this.revisionNumber,
      updatedAt: this.updatedAt
    };
  }
}

module.exports = {
  PaymentReceiptObject,
  PaymentReceiptObjectError,
  PAYMENT_ACCOUNT_TYPE,
  PAYMENT_CHANNEL,
  PAYMENT_STATUS
};
