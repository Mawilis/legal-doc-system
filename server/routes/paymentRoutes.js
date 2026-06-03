/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN PAYMENT API ROUTER [V28.92.15-SUPREME]                                                                            ║
 * ║ [LIQUIDITY GATEWAY | MULTI-CURRENCY HANDSHAKE | WEBHOOK ORCHESTRATOR | INSTITUTIONAL FINALITY]                                         ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 28.92.15-SUPREME | PRODUCTION READY | BILLION DOLLAR SPEC                                                                     ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | REVENUE-GRADE ARCHITECTURE                                                       ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/routes/paymentRoutes.js                                                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated absolute functional alignment and 10/10 forensic terminal logging.                   ║
 * ║ • Gemini (AI Engineering) - RECTIFIED: Integrated forensic exit logs for bulletproof transaction debugging.                            ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

// 1. USAGE COMMENTS
// -----------------------------------------------------------------------------
// Usage:
//   app.use('/api/payments', paymentRoutes);
//
// Functionality:
//   - POST /checkout: Create a payment session (Redirect to Gateway).
//   - POST /webhook: Receive async payment confirmation (Server-to-Server).
//   - GET /methods: List saved cards/payment methods.
// -----------------------------------------------------------------------------

import express from 'express';
import paymentController from '../controllers/paymentController.js';

// 2. MIDDLEWARE (The "Godly" Stack)
import { emitAudit } from '../middleware/auditMiddleware.js';
import { protect } from '../middleware/auth.js';
import { requireSameTenant, restrictTo } from '../middleware/rbacMiddleware.js';
import validate from '../middleware/validationMiddleware.js';

const router = express.Router();
const { Joi } = validate;

// 3. VALIDATION SCHEMAS (Joi)
const checkoutSchema = {
  invoiceId: Joi.string().required(), // Link to Invoice
  amount: Joi.number().min(10).required(), // Minimum amount check
  currency: Joi.string().valid('ZAR', 'USD').default('ZAR'),
  gateway: Joi.string().valid('PAYFAST', 'STRIPE', 'PAYGATE').default('PAYFAST'),
  successUrl: Joi.string().uri().required(),
  cancelUrl: Joi.string().uri().required(),
};

const refundSchema = {
  paymentId: Joi.string().required(),
  reason: Joi.string().valid('DUPLICATE', 'FRAUDULENT', 'REQUESTED_BY_CLIENT', 'OTHER').required(),
  amount: Joi.number().optional(), // Partial refund allowed
};

// ------------------------------
// ROUTES
// ------------------------------

/**
 * @route   POST /api/payments/checkout
 * @desc    Initiate Payment Session (Redirect URL)
 * @access  Authenticated Users (Client, Admin)
 */
router.post(
  '/checkout',
  protect,
  requireSameTenant,
  validate(checkoutSchema, 'body'),
  async (req, res, next) => {
    console.log("[PAYMENT_ROUTES] 💰 Checkout Session Initiated - Body:", req.body);
    console.log("[PAYMENT_ROUTES] 🛰️ Trace Info - Tenant:", req.tenantId, "User:", req.user?.id);

    try {
      const result = await paymentController.createCheckoutSession(req, res);

      // 🛡️ FORENSIC EXIT LOG
      console.log("[PAYMENT_ROUTES] ✅ Checkout Session Created:", result?.id || "No ID");

      // Audit the Attempt
      await emitAudit(req, {
        resource: 'payment_gateway',
        action: 'INITIATE_CHECKOUT',
        severity: 'INFO',
        summary: `Payment session started via ${req.body.gateway}`,
        metadata: { invoiceId: req.body.invoiceId, amount: req.body.amount },
      });

      if (!res.headersSent && result) res.status(201).json({ status: 'success', data: result });
    } catch (err) {
      console.error("[PAYMENT_ROUTES] 🚨 Checkout Fracture:", err.message);
      err.code = 'PAYMENT_INIT_FAILED';
      next(err);
    }
  }
);

/**
 * @route   POST /api/payments/webhook/:gateway
 * @desc    Handle Payment Provider Webhooks (Async)
 * @access  Public (Secured by Signature Verification)
 */
router.post(
  '/webhook/:gateway',
  async (req, res, next) => {
    console.log("[PAYMENT_ROUTES] 🛰️ Webhook Received from Gateway:", req.params.gateway);
    console.log("[PAYMENT_ROUTES] 🔍 Payload Integrity Check - Body Keys:", Object.keys(req.body));

    try {
      const result = await paymentController.handleWebhook(req, res);

      // 🛡️ FORENSIC EXIT LOG
      console.log("[PAYMENT_ROUTES] ✅ Webhook Processed Successfully for Gateway:", req.params.gateway);

      // Critical Audit: Money Confirmed
      await emitAudit(req, {
        resource: 'payment_gateway',
        action: 'WEBHOOK_RECEIVED',
        severity: 'INFO',
        summary: `Webhook received from ${req.params.gateway}`,
        actorEmail: 'system@wilsy.os',
        metadata: { gateway: req.params.gateway },
      });

      if (!res.headersSent && result) res.json({ status: 'success', received: true });
    } catch (err) {
      console.error("[PAYMENT_ROUTES] 🚨 Webhook Handshake Failed:", err.message);
      err.code = 'WEBHOOK_FAILED';
      next(err);
    }
  }
);

/**
 * @route   POST /api/payments/refund
 * @desc    Process Refund
 * @access  Admin, Finance (High Privilege)
 */
router.post(
  '/refund',
  protect,
  requireSameTenant,
  restrictTo('admin', 'finance', 'superadmin'),
  validate(refundSchema, 'body'),
  async (req, res, next) => {
    console.log("[PAYMENT_ROUTES] ⚠️ Refund Requested - Body:", req.body);
    console.log("[PAYMENT_ROUTES] 🔑 Authorized By:", req.user?.email);

    try {
      const result = await paymentController.processRefund(req, res);

      // 🛡️ FORENSIC EXIT LOG
      console.log("[PAYMENT_ROUTES] ✅ Refund Completed for Payment:", req.body.paymentId, "Amount:", req.body.amount);

      // Critical Audit: Money Outflow
      await emitAudit(req, {
        resource: 'payment_gateway',
        action: 'PROCESS_REFUND',
        severity: 'WARN',
        summary: `Refund processed for Payment ${req.body.paymentId}`,
        metadata: { reason: req.body.reason, amount: req.body.amount },
      });

      if (!res.headersSent && result) res.json({ status: 'success', data: result });
    } catch (err) {
      console.error("[PAYMENT_ROUTES] 🚨 Refund Operation Failed:", err.message);
      err.code = 'REFUND_FAILED';
      next(err);
    }
  }
);

/**
 * @route   GET /api/payments/history
 * @desc    Get Transaction History
 * @access  Authenticated Users
 */
router.get('/history', protect, requireSameTenant, async (req, res, next) => {
  console.log("[PAYMENT_ROUTES] 📊 Transaction History Requested for Tenant:", req.tenantId);

  try {
    const result = await paymentController.getTransactionHistory(req, res);

    // 🛡️ FORENSIC EXIT LOG
    console.log("[PAYMENT_ROUTES] ✅ Transaction History Returned. Count:", result?.length || 0);

    if (!res.headersSent && result) res.json({ status: 'success', data: result });
  } catch (err) {
    console.error("[PAYMENT_ROUTES] 🚨 History Retrieval Fracture:", err.message);
    err.code = 'TX_HISTORY_FAILED';
    next(err);
  }
});

export default router;

// 4. USAGE EXAMPLE
// -----------------------------------------------------------------------------
/*
const paymentRoutes = require('./server/routes/paymentRoutes');
app.use('/api/payments', paymentRoutes);
*/

// 5. ACCEPTANCE CRITERIA
// -----------------------------------------------------------------------------
/*
1. [x] Correctly imports 'validationMiddleware' (Joi).
2. [x] Validates gateway types (PAYFAST, STRIPE, etc.).
3. [x] Restricts refunds to 'finance'/'admin' roles.
4. [x] Exposes a Public Webhook endpoint (Signature verification handled in controller/middleware).
5. [x] Emits Audit Events for Checkout initiation and Refund processing.
*/
