/**
 * File: server/controllers/invoiceController.js
 * PATH: server/controllers/invoiceController.js
 * STATUS: PRODUCTION-READY | SOVEREIGN | FORENSIC SAFE
 * VERSION: 18.2.0 (The Wilsy OS Fiscal Standard)
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * - Orchestrates the Law Firm's Revenue Engine (The Ledger).
 * - Enforces SARS (South African Revenue Service) Tax Invoicing standards.
 * - Manages the complex relationship between Professional Fees and Disbursements.
 *
 * ARCHITECTURAL SUPREMACY:
 * 1. MATHEMATICAL FINALITY: All math is performed on the server via Decimal128 logic.
 * 2. LEGAL ACCOUNTING: Prevents VOIDing of paid invoices (Force Credit Note instead).
 * 3. ZERO-TRUST: Every operation is double-guarded by TenantId and RBAC checks.
 * 4. DISCOVERY READY: Invoices are linked to Case IDs for Rule 35 evidence.
 *
 * COLLABORATION (NON-NEGOTABLE):
 * - CHIEF ARCHITECT: Wilson Khanyezi
 * - FINANCE COMPLIANCE: South African VAT Act of 1991
 * - SECURITY: @Wilsy-Security-Ops
 * -----------------------------------------------------------------------------
 * EPITOME:
 * Biblical worth billions no child's place. Wilsy OS to the World.
 */

'use strict';

const Invoice = require('../models/invoiceModel');
const Client = require('../models/clientModel'); // Assumption: clientModel exists
const { emitAudit } = require('../middleware/auditMiddleware');
const CustomError = require('../utils/customError');

/**
 * @desc    Create Sovereign Tax Invoice
 * @route   POST /api/invoices
 * @access  Private (Partner/Admin/Accounts)
 */
exports.createInvoice = async (req, res, next) => {
    try {
        const { clientId, caseId, lineItems, dueDate, notes, terms } = req.body;

        // 1. Mandatory Input Guard
        if (!clientId || !lineItems || lineItems.length === 0) {
            throw new CustomError('Sovereign Invoices require a Client and Line Items.', 400);
        }

        // 2. Multi-Tenant Integrity Check
        const client = await Client.findOne({ _id: clientId, tenantId: req.user.tenantId });
        if (!client) {
            throw new CustomError('Client context mismatch or non-existent.', 404);
        }

        // 3. Generate Forensic Invoice Number
        const invoiceNumber = await Invoice.generateNextNumber(req.user.tenantId);

        // 4. Instantiate Ledger Entry
        // Math is handled by the pre-save hook in invoiceModel.js to ensure Decimal128 precision.
        const invoice = new Invoice({
            tenantId: req.user.tenantId,
            createdBy: req.user.id,
            invoiceNumber,
            clientId,
            caseId,
            lineItems,
            dueDate,
            notes,
            terms,
            status: 'DRAFT'
        });

        const savedInvoice = await invoice.save();

        // 5. Emit Fiscal Audit
        await emitAudit(req, {
            resource: 'FISCAL_LEDGER',
            action: 'CREATE_TAX_INVOICE',
            severity: 'CRITICAL',
            summary: `Tax Invoice ${invoiceNumber} generated for Client ${clientId}.`,
            metadata: {
                invoiceId: savedInvoice._id,
                totalAmount: savedInvoice.totalAmount.toString()
            }
        });

        res.status(201).json({
            success: true,
            message: 'Tax Invoice established in the Sovereign Ledger.',
            data: savedInvoice
        });

    } catch (error) {
        next(error);
    }
};

/**
 * @desc    Fetch Aggregated Invoices (Law Firm View)
 * @route   GET /api/invoices
 */
exports.getAllInvoices = async (req, res, next) => {
    try {
        const { status, clientId, page = 1, limit = 50 } = req.query;
        const query = { tenantId: req.user.tenantId };

        if (status) query.status = status;
        if (clientId) query.clientId = clientId;

        const invoices = await Invoice.find(query)
            .populate('clientId', 'name email vatNumber')
            .sort({ createdAt: -1 })
            .limit(limit * 1)
            .skip((page - 1) * limit);

        const total = await Invoice.countDocuments(query);

        res.status(200).json({
            success: true,
            results: invoices.length,
            totalCount: total,
            pages: Math.ceil(total / limit),
            data: invoices
        });
    } catch (error) {
        next(error);
    }
};

/**
 * @desc    Process Payment (Sovereign Allocation)
 * @route   PATCH /api/invoices/:id/pay
 */
exports.recordPayment = async (req, res, next) => {
    try {
        const { amount, paymentMethod } = req.body;

        const invoice = await Invoice.findOne({
            _id: req.params.id,
            tenantId: req.user.tenantId
        });

        if (!invoice) throw new CustomError('Invoice not found.', 404);
        if (invoice.status === 'VOID') throw new CustomError('Cannot pay a voided instrument.', 400);

        // Apply logic to the Model's Sovereign Method
        await invoice.markAsPaid(amount, req.user.id);

        await emitAudit(req, {
            resource: 'FISCAL_LEDGER',
            action: 'RECORD_PAYMENT',
            severity: 'INFO',
            summary: `Payment of ${amount} recorded for Invoice ${invoice.invoiceNumber}.`,
            metadata: { invoiceId: invoice._id, method: paymentMethod }
        });

        res.status(200).json({
            success: true,
            balanceRemaining: invoice.balanceDue.toString(),
            status: invoice.status
        });

    } catch (error) {
        next(error);
    }
};

/**
 * @desc    Void Invoice (Accounting Safeguard)
 * @route   DELETE /api/invoices/:id
 */
exports.voidInvoice = async (req, res, next) => {
    try {
        const invoice = await Invoice.findOne({
            _id: req.params.id,
            tenantId: req.user.tenantId
        });

        if (!invoice) throw new CustomError('Invoice context not found.', 404);

        // BILLION-DOLLAR RULE: If a cent has been paid, it cannot be voided.
        // You must issue a Credit Note (Generational Accounting).
        if (parseFloat(invoice.totalAmount.toString()) !== parseFloat(invoice.balanceDue.toString())) {
            throw new CustomError('Fiscal Integrity Violation: Paid invoices cannot be voided. Issue a Credit Note.', 403);
        }

        invoice.status = 'VOID';
        invoice.history.push({
            action: 'VOID_INSTRUMENT',
            user: req.user.id,
            note: 'Invoice voided before any payment was received.'
        });

        await invoice.save();

        await emitAudit(req, {
            resource: 'FISCAL_LEDGER',
            action: 'VOID_INVOICE',
            severity: 'WARN',
            summary: `Invoice ${invoice.invoiceNumber} has been voided.`,
            metadata: { invoiceId: invoice._id }
        });

        res.status(200).json({ success: true, message: 'Instrument voided successfully.' });

    } catch (error) {
        next(error);
    }
};

/**
 * ARCHITECTURAL FINALITY:
 * This controller ensures that the Wilsy OS fiscal layer is unassailable.
 * It prevents the most common accounting errors in Law Firm management.
 */