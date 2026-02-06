/**
 * File: server/routes/invoiceRoutes.js
 * PATH: server/routes/invoiceRoutes.js
 * STATUS: PRODUCTION-READY | BIBLICAL | FORENSIC SAFE
 * VERSION: 12.0.0 (Wilsy OS Fiscal Gateway)
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * - Sovereign ingress/egress for Tax Invoices and Fiscal Ledgers.
 * - Enforces South African VAT Act compliance and Law Society audit standards.
 * - Orchestrates the generation, delivery, and payment of Legal Assets.
 *
 * COLLABORATION (NON-NEGOTABLE):
 * - CHIEF ARCHITECT: Wilson Khanyezi
 * - TECH LEAD: @platform
 * - AUDIT: @sars-compliance-team
 * -----------------------------------------------------------------------------
 * EPITOME:
 * Biblical worth billions no child's place. Wilsy OS to the World.
 */

'use strict';

const express = require('express');
const router = express.Router();
const invoiceController = require('../controllers/invoiceController');

// MIDDLEWARE: The Wilsy Security Shield
const { protect } = require('../middleware/authMiddleware');
const { tenantGuard, restrictTo } = require('../middleware/security'); // Combined guards
const validate = require('../middleware/validationMiddleware');

/* ---------------------------------------------------------------------------
   UTILITY: Async Wrapper for Clean Ingress
   --------------------------------------------------------------------------- */
const asyncHandler = fn => (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);

/* ---------------------------------------------------------------------------
   SOVEREIGN ROUTES: TAX INVOICE OPERATIONS
   --------------------------------------------------------------------------- */

/**
 * @desc    Fetch Aggregated Ledger / List Invoices
 * @access  Private: Partners, Finance, Admin
 */
router.get(
    '/',
    protect,
    tenantGuard(),
    restrictTo('partner', 'finance', 'admin'),
    asyncHandler(invoiceController.getAllInvoices)
);

/**
 * @desc    Generate a Sovereign Tax Invoice
 * @access  Private: Partners, Finance, Admin
 */
router.post(
    '/',
    protect,
    tenantGuard(),
    restrictTo('partner', 'finance', 'admin'),
    asyncHandler(invoiceController.createInvoice)
);

/**
 * @route   GET /api/invoices/:id
 * @desc    Retrieve Single Invoice Metadata
 * @access  Private: Staff & The Owner (Client)
 */
router.get(
    '/:id',
    protect,
    tenantGuard(),
    restrictTo('partner', 'finance', 'admin', 'lawyer', 'client'),
    asyncHandler(invoiceController.getInvoice)
);

/**
 * @route   GET /api/invoices/:id/pdf
 * @desc    Generate/Stream SARS-Compliant Tax Invoice PDF
 * @access  Private: Staff & The Owner (Client)
 */
router.get(
    '/:id/pdf',
    protect,
    tenantGuard(),
    restrictTo('partner', 'finance', 'admin', 'lawyer', 'client'),
    asyncHandler(invoiceController.getInvoicePdf || ((req, res) => res.status(501).send('PDF Engine Pending')))
);

/**
 * @route   PATCH /api/invoices/:id/pay
 * @desc    Record Fiscal Allocation (Payment)
 * @access  Private: Finance, Admin, Partner
 */
router.patch(
    '/:id/pay',
    protect,
    tenantGuard(),
    restrictTo('finance', 'admin', 'partner'),
    asyncHandler(invoiceController.recordPayment)
);

/**
 * @route   POST /api/invoices/:id/send
 * @desc    Formal Dispatch to Client (Email/Vault)
 * @access  Private: Finance, Partner, Lawyer
 */
router.post(
    '/:id/send',
    protect,
    tenantGuard(),
    restrictTo('finance', 'partner', 'lawyer'),
    asyncHandler(invoiceController.emailInvoice || ((req, res) => res.status(501).send('Mailer Engine Pending')))
);

/**
 * @route   DELETE /api/invoices/:id
 * @desc    Void Invoice (Subject to Forensic Integrity Checks)
 * @access  Private: Partner, Admin Only
 */
router.delete(
    '/:id',
    protect,
    tenantGuard(),
    restrictTo('partner', 'admin'),
    asyncHandler(invoiceController.voidInvoice)
);

/* ---------------------------------------------------------------------------
   EXPORT GATEWAY
   --------------------------------------------------------------------------- */
module.exports = router;