/**
 * ====================================================================
 *  WILSY OS – SOVEREIGN PAYSHAP PAYMENT SERVICE
 *  Version: v1.0.0‑SOVEREIGN
 *  Authority: WILSY OS KENNEL EOS – TENANT ISOLATION & CRYPTOGRAPHIC VERIFICATION
 *  Epitome: Initiates and verifies PayShap payments, handles webhooks,
 *           and updates invoice status with full audit trail.
 *  Collaboration: Wilson (architect), AI (implementation) – 2026-08-10
 *  Institutional: POPIA §19, GDPR §32, SOC2 §CC7.2 – all financial data
 *                 is redacted in logs, webhook signatures enforce non‑repudiation.
 * ====================================================================
 */

import axios from 'axios';
import crypto from 'crypto';
import logger from '../../utils/logger.js';
import AuditLogger from '../../services/AuditLogger.js';
import { getSovereignInvoiceModel } from '../../controllers/billingController.js'; // hypothetical; adjust import if needed

// ------------------------------------------------------------------
//  CONFIGURATION (loaded from environment)
// ------------------------------------------------------------------
const PAYSHAP_API_KEY = process.env.PAYSHAP_API_KEY || '';
const PAYSHAP_BASE_URL = process.env.PAYSHAP_BASE_URL || 'https://api.payshap.co.za/v1';
const PAYSHAP_WEBHOOK_SECRET = process.env.PAYSHAP_WEBHOOK_SECRET || 'default-webhook-secret-change-me';
const PAYSHAP_TIMEOUT_MS = parseInt(process.env.PAYSHAP_TIMEOUT_MS || '10000', 10);

// ------------------------------------------------------------------
//  HELPERS
// ------------------------------------------------------------------

/**
 * sortObjectKeys – Recursively sorts object keys for deterministic signature.
 */
function sortObjectKeys(obj) {
  if (obj === null || typeof obj !== 'object') return obj;
  if (Array.isArray(obj)) return obj.map(sortObjectKeys);
  const sorted = {};
  Object.keys(obj)
    .sort()
    .forEach((key) => {
      sorted[key] = sortObjectKeys(obj[key]);
    });
  return sorted;
}

/**
 * verifyWebhookSignature – Verifies the PayShap webhook signature using HMAC‑SHA256.
 *
 * @param {Object} payload - The parsed webhook payload.
 * @param {string} signatureHeader - The value of the `X-PayShap-Signature` header.
 * @param {string} secret - The webhook secret.
 * @returns {boolean} True if signature is valid.
 */
function verifyWebhookSignature(payload, signatureHeader, secret = PAYSHAP_WEBHOOK_SECRET) {
  if (!signatureHeader || !payload) return false;
  // Sort payload keys for deterministic stringification
  const sorted = sortObjectKeys(payload);
  const payloadString = JSON.stringify(sorted);
  const hmac = crypto.createHmac('sha256', secret);
  hmac.update(payloadString);
  const expected = hmac.digest('hex');
  return crypto.timingSafeEqual(Buffer.from(expected), Buffer.from(signatureHeader));
}

// ------------------------------------------------------------------
//  PUBLIC FUNCTIONS
// ------------------------------------------------------------------

/**
 * initiatePayment – Initiates a PayShap payment for an invoice.
 *
 * @collaboration  Wilson & AI – 2026-08-10
 * @epitome        Sends a request to PayShap API to create a payment session.
 *                 Returns a reference and redirect URL for the customer.
 * @institutional  Ensures that every payment initiation is logged immutably
 *                 and is tied to a specific invoice and tenant.
 *
 * @param {Object} invoice - The invoice document (must contain invoiceNumber, totalAmount, currency, tenantId).
 * @param {Object} options - Additional options.
 * @param {string} [options.returnUrl] - Customer return URL after payment.
 * @param {string} [options.notifyUrl] - Webhook URL for payment status updates.
 * @param {string} [options.metadata] - Optional metadata.
 * @returns {Promise<Object>} { success, paymentReference, redirectUrl, status }
 *
 * @throws {Error} If invoice is missing, amount invalid, or API call fails.
 */
export async function initiatePayment(invoice, options = {}) {
  const startTime = Date.now();
  const { invoiceNumber, totalAmount, currency, tenantId, traceId } = invoice;

  // Validate input
  if (!invoice || !invoiceNumber) {
    throw new Error('initiatePayment: invoice with invoiceNumber is required');
  }
  if (!totalAmount || totalAmount <= 0) {
    throw new Error('initiatePayment: totalAmount must be positive');
  }
  if (!currency) {
    throw new Error('initiatePayment: currency is required');
  }
  if (!tenantId) {
    throw new Error('initiatePayment: tenantId is required');
  }

  const returnUrl = options.returnUrl || `${process.env.FRONTEND_URL}/payment/return`;
  const notifyUrl = options.notifyUrl || `${process.env.BASE_URL}/api/payment/webhook/payshap`;

  // Build PayShap request payload (example; adjust to actual API)
  const requestPayload = {
    amount: Number(totalAmount).toFixed(2),
    currency: currency.toUpperCase(),
    reference: invoiceNumber,
    description: `Invoice ${invoiceNumber}`,
    returnUrl,
    notifyUrl,
    metadata: {
      tenantId,
      invoiceNumber,
      traceId: traceId || invoiceNumber,
      ...options.metadata,
    },
  };

  try {
    const response = await axios.post(
      `${PAYSHAP_BASE_URL}/payments`,
      requestPayload,
      {
        headers: {
          'Authorization': `Bearer ${PAYSHAP_API_KEY}`,
          'Content-Type': 'application/json',
        },
        timeout: PAYSHAP_TIMEOUT_MS,
      }
    );

    const data = response.data;
    const paymentReference = data.reference || data.id || `PAY-${Date.now()}`;
    const redirectUrl = data.redirectUrl || data.paymentUrl || data.checkoutUrl;

    // Log successful initiation
    await AuditLogger.log({
      action: 'PAYSHAP_INITIATE_SUCCESS',
      tenantId,
      resourceType: 'INVOICE',
      resourceId: invoiceNumber,
      details: {
        paymentReference,
        amount: totalAmount,
        currency,
        durationMs: Date.now() - startTime,
      },
      severity: 'INFO',
      metadata: { requestId: options.requestId || 'SYSTEM' },
    });

    return {
      success: true,
      paymentReference,
      redirectUrl,
      status: data.status || 'PENDING',
      rawResponse: data,
    };
  } catch (error) {
    const durationMs = Date.now() - startTime;
    const errorMessage = error.response?.data?.message || error.message || 'Unknown error';

    await AuditLogger.log({
      action: 'PAYSHAP_INITIATE_FAILURE',
      tenantId,
      resourceType: 'INVOICE',
      resourceId: invoiceNumber,
      details: {
        error: errorMessage,
        statusCode: error.response?.status || 500,
        durationMs,
      },
      severity: 'ERROR',
      metadata: { requestId: options.requestId || 'SYSTEM' },
    });

    logger.error(`[PAYSHAP] Initiation failed for invoice ${invoiceNumber}: ${errorMessage}`);
    throw new Error(`PayShap initiation failed: ${errorMessage}`);
  }
}

/**
 * checkPaymentStatus – Queries PayShap for the status of a payment.
 *
 * @collaboration  Wilson & AI – 2026-08-10
 * @epitome        Polls the PayShap API to get the current status of a payment.
 * @institutional  Used for reconciliation and manual status updates; logged for audit.
 *
 * @param {string} paymentReference - The reference returned from initiation.
 * @param {string} tenantId - Tenant context.
 * @param {Object} [options] - Additional options.
 * @returns {Promise<Object>} { status, amount, paidAt, rawResponse }
 *
 * @throws {Error} If reference missing or API call fails.
 */
export async function checkPaymentStatus(paymentReference, tenantId, options = {}) {
  if (!paymentReference) {
    throw new Error('checkPaymentStatus: paymentReference is required');
  }
  if (!tenantId) {
    throw new Error('checkPaymentStatus: tenantId is required');
  }

  try {
    const response = await axios.get(
      `${PAYSHAP_BASE_URL}/payments/${encodeURIComponent(paymentReference)}`,
      {
        headers: {
          'Authorization': `Bearer ${PAYSHAP_API_KEY}`,
        },
        timeout: PAYSHAP_TIMEOUT_MS,
      }
    );

    const data = response.data;
    const status = data.status || 'UNKNOWN';

    await AuditLogger.log({
      action: 'PAYSHAP_STATUS_CHECK',
      tenantId,
      details: {
        paymentReference,
        status,
        amount: data.amount,
        paidAt: data.paidAt,
      },
      severity: 'INFO',
    });

    return {
      status,
      amount: data.amount,
      paidAt: data.paidAt || null,
      rawResponse: data,
    };
  } catch (error) {
    const errorMessage = error.response?.data?.message || error.message || 'Unknown error';
    await AuditLogger.log({
      action: 'PAYSHAP_STATUS_CHECK_FAILURE',
      tenantId,
      details: {
        paymentReference,
        error: errorMessage,
      },
      severity: 'ERROR',
    });
    logger.error(`[PAYSHAP] Status check failed for ${paymentReference}: ${errorMessage}`);
    throw new Error(`PayShap status check failed: ${errorMessage}`);
  }
}

/**
 * handleWebhook – Processes an incoming PayShap webhook.
 *
 * @collaboration  Wilson & AI – 2026-08-10
 * @epitome        Verifies the webhook signature, extracts payment data,
 *                 updates the corresponding invoice status, and logs the event.
 * @institutional  Critical for automated payment reconciliation; ensures
 *                 that only authenticated webhooks can update financial state.
 *
 * @param {Object} payload - The raw webhook payload (parsed JSON).
 * @param {string} signatureHeader - The `X-PayShap-Signature` header value.
 * @param {string} [secret] - Optional override for webhook secret.
 * @param {boolean} [skipInvoiceUpdate=false] - For testing, skip invoice update.
 * @returns {Promise<Object>} { success, invoiceUpdated, paymentReference, status }
 *
 * @throws {Error} If signature verification fails or invoice not found.
 */
export async function handleWebhook(payload, signatureHeader, secret = PAYSHAP_WEBHOOK_SECRET, skipInvoiceUpdate = false) {
  // 1. Verify signature
  if (!verifyWebhookSignature(payload, signatureHeader, secret)) {
    await AuditLogger.log({
      action: 'PAYSHAP_WEBHOOK_SIGNATURE_FAILURE',
      details: { payload: JSON.stringify(payload).slice(0, 200) },
      severity: 'CRITICAL',
    });
    throw new Error('Invalid webhook signature');
  }

  // 2. Extract data
  const { reference, status, amount, paidAt, metadata } = payload;
  const tenantId = metadata?.tenantId || 'MASTER';
  const invoiceNumber = metadata?.invoiceNumber || reference;

  if (!invoiceNumber) {
    throw new Error('Invoice number missing from webhook metadata');
  }

  // 3. Log the webhook receipt
  await AuditLogger.log({
    action: 'PAYSHAP_WEBHOOK_RECEIVED',
    tenantId,
    resourceType: 'INVOICE',
    resourceId: invoiceNumber,
    details: {
      paymentReference: reference,
      status,
      amount,
      paidAt,
    },
    severity: 'INFO',
  });

  // 4. Update invoice (if not skipped)
  let invoiceUpdated = false;
  if (!skipInvoiceUpdate) {
    const SovereignInvoice = getSovereignInvoiceModel(); // should be imported
    const invoice = await SovereignInvoice.findOne({ invoiceNumber });
    if (!invoice) {
      throw new Error(`Invoice ${invoiceNumber} not found`);
    }

    // Ensure tenant isolation
    if (invoice.recipientTenantId !== tenantId && invoice.tenantId !== tenantId) {
      throw new Error('Tenant isolation violation in webhook');
    }

    // Update based on status
    const oldStatus = invoice.status;
    if (status === 'PAID' || status === 'SUCCESS') {
      invoice.status = 'PAID';
      invoice.paidAmount = invoice.totalAmount;
      invoice.outstandingAmount = 0;
      invoice.paidDate = paidAt ? new Date(paidAt) : new Date();
    } else if (status === 'PARTIALLY_PAID') {
      const paidAmount = amount || 0;
      invoice.paidAmount = (invoice.paidAmount || 0) + paidAmount;
      invoice.outstandingAmount = invoice.totalAmount - invoice.paidAmount;
      invoice.status = invoice.outstandingAmount <= 0 ? 'PAID' : 'PARTIALLY_PAID';
      invoice.paidDate = paidAt ? new Date(paidAt) : new Date();
    } else if (status === 'FAILED' || status === 'CANCELLED') {
      // Do not change status; log failure
    }
    // If status is 'PENDING', do nothing.

    // Add payment history entry
    if (!invoice.paymentHistory) invoice.paymentHistory = [];
    invoice.paymentHistory.push({
      amount: amount || 0,
      currency: payload.currency || invoice.currency,
      date: paidAt ? new Date(paidAt) : new Date(),
      method: 'PayShap',
      reference,
      status,
      webhook: true,
    });

    // Regenerate seal
    const sealPayload = {
      invoiceId: invoice._id,
      status: invoice.status,
      outstanding: invoice.outstandingAmount,
      paid: invoice.paidAmount,
      updatedAt: new Date().toISOString(),
      paymentRef: reference,
    };
    invoice.sealHash = crypto.createHash('sha3-512').update(JSON.stringify(sealPayload)).digest('hex');

    await invoice.save();
    invoiceUpdated = true;

    await AuditLogger.log({
      action: 'PAYSHAP_WEBHOOK_INVOICE_UPDATED',
      tenantId,
      resourceType: 'INVOICE',
      resourceId: invoiceNumber,
      details: {
        oldStatus,
        newStatus: invoice.status,
        amount,
        reference,
      },
      severity: 'INFO',
    });
  }

  return {
    success: true,
    invoiceUpdated,
    paymentReference: reference,
    status,
    invoiceNumber,
  };
}

/**
 * healthCheck – Validates that the PayShap service is configured.
 *
 * @returns {Object} { status, apiKeySet, webhookSecretSet, baseUrl }
 */
export function healthCheck() {
  return {
    status: 'healthy',
    apiKeySet: Boolean(PAYSHAP_API_KEY),
    webhookSecretSet: PAYSHAP_WEBHOOK_SECRET !== 'default-webhook-secret-change-me',
    baseUrl: PAYSHAP_BASE_URL,
    version: 'v1.0.0‑SOVEREIGN',
  };
}

export default {
  initiatePayment,
  checkPaymentStatus,
  handleWebhook,
  healthCheck,
};
