/**
 * ============================================================================
 * WILSY OS - INVOICE ENTERPRISE OBJECT
 * ============================================================================
 *
 * @file         InvoiceObject.js
 * @directory    server/src/enterprise/objects/
 * @system       Wilsy OS - Legal Enterprise Operating System & SaaS Platform
 * @authority    Wilson Khanyezi, Founder & Chief Architect
 * @version      1.0.0-SOVEREIGN
 * @epitome      Generation 2 Sovereign Invoice Kernel Object implementation.
 *               Serves as the core tax invoicing engine for legal practices under
 *               the Value-Added Tax Act and Legal Practice Council guidelines.
 *               Manages fee line items, automated 15% VAT calculations, statutory
 *               trust allocations, payment recording, and lifecycle status transitions.
 *
 * @collaboration
 * - Lead Architect: Wilson Khanyezi (Wilsy OS Architecture Core Team)
 * - Practice Accounting: Legal Billing & Tax Invoice Core
 * - Revenue Systems: Accounts Receivable & Trust Settlement Subsystem
 *
 * ============================================================================
 * INSTITUTIONAL AUDIT TRAIL
 * ============================================================================
 * Date       | Author          | Version | Description
 * -----------|-----------------|---------|------------------------------------
 * 2026-07-24 | Wilson Khanyezi | 1.0.0   | Production-ready Invoice domain object
 *            |                 |         | with VAT math, payment ledgers, trust
 *            |                 |         | settlement linkage, and state locks.
 * ============================================================================
 */

const { BaseEnterpriseObject, OBJECT_LIFECYCLE_STATES } = require('./BaseEnterpriseObject');
const { DataRedactor } = require('../kernel/EnterpriseKernel');

/**
 * Standard Legal Invoice Lifecycle States.
 */
const INVOICE_STATUS = Object.freeze({
  DRAFT: 'DRAFT',
  ISSUED: 'ISSUED',
  PARTIALLY_PAID: 'PARTIALLY_PAID',
  PAID: 'PAID',
  OVERDUE: 'OVERDUE',
  CANCELLED: 'CANCELLED'
});

/**
 * Recognized Payment Methods for Fee Settlement.
 */
const PAYMENT_METHOD = Object.freeze({
  EFT: 'EFT',
  TRUST_TRANSFER: 'TRUST_TRANSFER',
  CREDIT_CARD: 'CREDIT_CARD',
  DIRECT_DEBIT: 'DIRECT_DEBIT',
  CHECK: 'CHECK'
});

/**
 * Custom Error Class for Invoice Domain Faults.
 */
class InvoiceObjectError extends Error {
  /**
   * @param {string} message - Error details.
   * @param {string} [code='INV_ERR_GENERIC'] - Standard error code.
   * @param {Object} [details={}] - Additional contextual metadata.
   */
  constructor(message, code = 'INV_ERR_GENERIC', details = {}) {
    super(message);
    this.name = 'InvoiceObjectError';
    this.code = code;
    this.timestamp = new Date().toISOString();
    this.details = DataRedactor.sanitize(details);
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, InvoiceObjectError);
    }
  }
}

/**
 * Sovereign Legal Tax Invoice Domain Object.
 * Encapsulates statutory tax invoicing, VAT computation, line item details,
 * trust payment allocations, and accounts receivable tracking in Wilsy OS.
 */
class InvoiceObject extends BaseEnterpriseObject {
  /**
   * Constructs an InvoiceObject.
   *
   * @param {Object} params
   * @param {string} params.id - Unique Invoice Identifier (e.g. 'INV-2026-0042').
   * @param {string} params.tenantId - Sovereign Tenant ID.
   * @param {string} params.matterId - Associated Legal Matter ID.
   * @param {string} params.customerId - Client Customer ID receiving invoice.
   * @param {Array<Object>} [params.lineItems=[]] - Initial list of fee or disbursement items.
   * @param {number} [params.taxRate=0.15] - Applicable VAT rate (default 15% for South Africa).
   * @param {string} [params.dueDate] - ISO String for payment due date (default +30 days).
   * @param {string} [params.currency='ZAR'] - Standard ISO currency code.
   * @param {string} [params.createdById='SYSTEM'] - Operator creating invoice.
   */
  constructor({
    id,
    tenantId,
    matterId,
    customerId,
    lineItems = [],
    taxRate = 0.15,
    dueDate = null,
    currency = 'ZAR',
    createdById = 'SYSTEM'
  }) {
    if (!matterId || typeof matterId !== 'string') {
      throw new InvoiceObjectError('Associated legal matter ID is required', 'INV_ERR_INVALID_MATTER');
    }

    if (!customerId || typeof customerId !== 'string') {
      throw new InvoiceObjectError('Recipient customer ID is required', 'INV_ERR_INVALID_CUSTOMER');
    }

    const rate = Number(taxRate);
    if (isNaN(rate) || rate < 0 || rate > 1) {
      throw new InvoiceObjectError('Tax rate must be a valid decimal fraction between 0.0 and 1.0', 'INV_ERR_INVALID_TAX_RATE');
    }

    // Default due date to 30 days in the future if unspecified
    const defaultDueDate = dueDate
      ? new Date(dueDate).toISOString()
      : new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString();

    const initialAttributes = {
      matterId: matterId.trim(),
      customerId: customerId.trim(),
      currency: currency.trim().toUpperCase(),
      taxRate: rate,
      invoiceStatus: INVOICE_STATUS.DRAFT,
      issuedAt: null,
      dueDate: defaultDueDate,
      lineItems: [],
      subtotalAmount: 0,
      taxAmount: 0,
      totalAmount: 0,
      amountPaid: 0,
      balanceDue: 0,
      payments: [],
      cancellationReason: null
    };

    super({
      id,
      tenantId,
      domain: 'INVOICE',
      attributes: initialAttributes,
      schemaVersion: '1.0.0',
      status: OBJECT_LIFECYCLE_STATES.ACTIVE,
      createdById
    });

    // Process initial line items if provided during construction
    if (Array.isArray(lineItems) && lineItems.length > 0) {
      for (const item of lineItems) {
        this.addLineItem(item, createdById);
      }
    }
  }

  /**
   * Recalculates subtotal, VAT, total amount, and balance due based on current line items and payments.
   * @private
   */
  recalculateTotals() {
    const subtotal = this.attributes.lineItems.reduce((acc, item) => acc + item.amount, 0);
    const tax = Number((subtotal * this.attributes.taxRate).toFixed(2));
    const total = Number((subtotal + tax).toFixed(2));
    const balance = Number((total - this.attributes.amountPaid).toFixed(2));

    this.attributes.subtotalAmount = subtotal;
    this.attributes.taxAmount = tax;
    this.attributes.totalAmount = total;
    this.attributes.balanceDue = Math.max(0, balance);
  }

  /**
   * Adds a fee or disbursement line item to draft invoice.
   *
   * @param {Object} itemData
   * @param {string} itemData.description - Narrative description of legal service/disbursement.
   * @param {number} itemData.amount - Value before tax.
   * @param {string} [itemData.timeEntryId=null] - Linked time entry ID if applicable.
   * @param {string} operatorId - User modifying invoice.
   * @returns {Object} Revision state.
   */
  addLineItem({ description, amount, timeEntryId = null }, operatorId = 'SYSTEM') {
    if (this.attributes.invoiceStatus !== INVOICE_STATUS.DRAFT) {
      throw new InvoiceObjectError(
        `Cannot add line items to an invoice with status [${this.attributes.invoiceStatus}]`,
        'INV_ERR_LOCKED_STATUS'
      );
    }

    if (!description || typeof description !== 'string' || description.trim().length === 0) {
      throw new InvoiceObjectError('Line item description is required', 'INV_ERR_INVALID_DESCRIPTION');
    }

    const itemVal = Number(amount);
    if (isNaN(itemVal) || itemVal <= 0) {
      throw new InvoiceObjectError('Line item amount must be a positive number', 'INV_ERR_INVALID_AMOUNT');
    }

    const lineItem = {
      lineItemId: `LINE-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
      description: description.trim(),
      amount: Number(itemVal.toFixed(2)),
      timeEntryId: timeEntryId ? timeEntryId.trim() : null
    };

    const updatedLineItems = [...this.attributes.lineItems, lineItem];

    // Temporarily mutate local array to recalculate totals
    this.attributes.lineItems = updatedLineItems;
    this.recalculateTotals();

    return this.updateAttributes(
      {
        lineItems: updatedLineItems,
        subtotalAmount: this.attributes.subtotalAmount,
        taxAmount: this.attributes.taxAmount,
        totalAmount: this.attributes.totalAmount,
        balanceDue: this.attributes.balanceDue
      },
      operatorId
    );
  }

  /**
   * Issues draft invoice, locking line items and enabling payment processing.
   *
   * @param {string} operatorId - Partner or Billing Clerk issuing invoice.
   * @returns {Object} Revision state.
   */
  issueInvoice(operatorId = 'SYSTEM') {
    if (this.attributes.invoiceStatus !== INVOICE_STATUS.DRAFT) {
      throw new InvoiceObjectError(
        `Cannot issue invoice currently in status [${this.attributes.invoiceStatus}]`,
        'INV_ERR_INVALID_TRANSITION'
      );
    }

    if (this.attributes.lineItems.length === 0) {
      throw new InvoiceObjectError('Cannot issue an invoice with zero line items', 'INV_ERR_NO_LINE_ITEMS');
    }

    return this.updateAttributes(
      {
        invoiceStatus: INVOICE_STATUS.ISSUED,
        issuedAt: new Date().toISOString()
      },
      operatorId
    );
  }

  /**
   * Records a payment against the invoice (direct EFT or trust transfer settlement).
   *
   * @param {Object} paymentData
   * @param {number} paymentData.amount - Payment amount.
   * @param {string} [paymentData.method='EFT'] - Payment method constant.
   * @param {string} paymentData.reference - Transaction / bank reference number.
   * @param {string} [paymentData.trustAccountId=null] - Linked trust account ID if trust transfer.
   * @param {string} operatorId - Operator recording payment.
   * @returns {Object} Revision state.
   */
  recordPayment({ amount, method = PAYMENT_METHOD.EFT, reference, trustAccountId = null }, operatorId = 'SYSTEM') {
    if (
      this.attributes.invoiceStatus !== INVOICE_STATUS.ISSUED &&
      this.attributes.invoiceStatus !== INVOICE_STATUS.PARTIALLY_PAID &&
      this.attributes.invoiceStatus !== INVOICE_STATUS.OVERDUE
    ) {
      throw new InvoiceObjectError(
        `Payments can only be recorded on ISSUED, PARTIALLY_PAID, or OVERDUE invoices. Current status: [${this.attributes.invoiceStatus}]`,
        'INV_ERR_UNPAYABLE_STATUS'
      );
    }

    const paymentVal = Number(amount);
    if (isNaN(paymentVal) || paymentVal <= 0) {
      throw new InvoiceObjectError('Payment amount must be a positive number', 'INV_ERR_INVALID_PAYMENT_AMOUNT');
    }

    if (paymentVal > this.attributes.balanceDue) {
      throw new InvoiceObjectError(
        `Payment amount [R${paymentVal}] exceeds outstanding invoice balance [R${this.attributes.balanceDue}]`,
        'INV_ERR_OVERPAYMENT_PROHIBITED'
      );
    }

    const normMethod = method.trim().toUpperCase();
    if (!Object.values(PAYMENT_METHOD).includes(normMethod)) {
      throw new InvoiceObjectError(`Invalid payment method [${method}]`, 'INV_ERR_INVALID_METHOD');
    }

    const paymentRecord = {
      paymentId: `PAY-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
      amount: Number(paymentVal.toFixed(2)),
      method: normMethod,
      reference: reference ? reference.trim() : `REF-${Date.now()}`,
      trustAccountId: trustAccountId ? trustAccountId.trim() : null,
      paidAt: new Date().toISOString(),
      recordedBy: operatorId
    };

    const newAmountPaid = Number((this.attributes.amountPaid + paymentVal).toFixed(2));
    const newBalanceDue = Number((this.attributes.totalAmount - newAmountPaid).toFixed(2));

    const newStatus = newBalanceDue <= 0 ? INVOICE_STATUS.PAID : INVOICE_STATUS.PARTIALLY_PAID;

    return this.updateAttributes(
      {
        amountPaid: newAmountPaid,
        balanceDue: Math.max(0, newBalanceDue),
        invoiceStatus: newStatus,
        payments: [...this.attributes.payments, paymentRecord]
      },
      operatorId
    );
  }

  /**
   * Cancels invoice with explicit justification audit log.
   *
   * @param {string} reason - Commercial or administrative reason for cancellation.
   * @param {string} operatorId - Authorizing Partner identity.
   * @returns {Object} Revision state.
   */
  cancelInvoice(reason, operatorId = 'SYSTEM') {
    if (!reason || typeof reason !== 'string' || reason.trim().length === 0) {
      throw new InvoiceObjectError('Cancellation reason required', 'INV_ERR_REASON_REQUIRED');
    }

    if (this.attributes.amountPaid > 0) {
      throw new InvoiceObjectError('Cannot cancel an invoice that has payments recorded against it', 'INV_ERR_PAID_INVOICE_CANCEL');
    }

    return this.updateAttributes(
      {
        invoiceStatus: INVOICE_STATUS.CANCELLED,
        cancellationReason: reason.trim(),
        balanceDue: 0
      },
      operatorId
    );
  }

  /**
   * Convenience getter for Invoice Status.
   * @returns {string}
   */
  get invoiceStatus() {
    return this.attributes.invoiceStatus;
  }

  /**
   * Convenience getter for Total Amount.
   * @returns {number}
   */
  get totalAmount() {
    return this.attributes.totalAmount;
  }

  /**
   * Convenience getter for Balance Due.
   * @returns {number}
   */
  get balanceDue() {
    return this.attributes.balanceDue;
  }

  /**
   * Generates a scrubbed summary of invoice metadata for accounts receivable ledger.
   * @returns {Object}
   */
  getSanitizedSummary() {
    return {
      invoiceId: this.id,
      tenantId: this.tenantId,
      matterId: this.attributes.matterId,
      customerId: this.attributes.customerId,
      currency: this.attributes.currency,
      invoiceStatus: this.attributes.invoiceStatus,
      issuedAt: this.attributes.issuedAt,
      dueDate: this.attributes.dueDate,
      lineItemsCount: this.attributes.lineItems.length,
      subtotalAmount: this.attributes.subtotalAmount,
      taxAmount: this.attributes.taxAmount,
      totalAmount: this.attributes.totalAmount,
      amountPaid: this.attributes.amountPaid,
      balanceDue: this.attributes.balanceDue,
      paymentCount: this.attributes.payments.length,
      status: this.status,
      revisionNumber: this.revisionNumber,
      updatedAt: this.updatedAt
    };
  }
}

module.exports = {
  InvoiceObject,
  InvoiceObjectError,
  INVOICE_STATUS,
  PAYMENT_METHOD
};
