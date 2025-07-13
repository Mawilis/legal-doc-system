// server/controllers/invoiceController.js

const Invoice = require('../models/invoiceModel');
const Document = require('../models/documentModel');
const Client = require('../models/clientModel');
const CustomError = require('../utils/customError');
const logger = require('../utils/logger');

// This is a helper function, not a route handler.
// It would be called internally when a document's status is set to 'Return Generated'.
exports.createInvoiceFromDocument = async (documentId) => {
    try {
        const doc = await Document.findById(documentId).populate('client');
        if (!doc || !doc.client) {
            throw new Error('Document or associated client not found.');
        }

        // 1. Generate a unique invoice number (this can be made more robust)
        const invoiceNumber = `INV-${Date.now()}`;

        // 2. Define line items based on document service (example logic)
        const lineItems = [
            { description: `Service of ${doc.documentType} - Case: ${doc.caseNumber}`, quantity: 1, unitPrice: 150.00 },
            { description: 'Travel Costs', quantity: 1, unitPrice: 50.00 },
        ];

        // 3. Calculate totals
        const subtotal = lineItems.reduce((acc, item) => acc + item.quantity * item.unitPrice, 0);
        const tax = subtotal * 0.15; // Assuming 15% tax
        const total = subtotal + tax;

        // 4. Set due date (e.g., 30 days from now)
        const dueDate = new Date();
        dueDate.setDate(dueDate.getDate() + 30);

        // 5. Create the invoice
        const invoice = await Invoice.create({
            invoiceNumber,
            issueDate: new Date(),
            dueDate,
            client: doc.client._id,
            document: doc._id,
            lineItems,
            subtotal,
            tax,
            total,
            status: 'Draft',
        });

        // 6. Update document status to 'Billed'
        doc.status = 'Billed';
        await doc.save();

        logger.info(`Invoice ${invoice.invoiceNumber} created for document ${doc.caseNumber}`);
        return invoice;

    } catch (error) {
        logger.error(`Failed to create invoice from document ${documentId}: ${error.message}`);
    }
};


// --- Route Handlers ---

/**
 * @desc    Get all invoices
 * @route   GET /api/invoices
 * @access  Private/Admin
 */
exports.getAllInvoices = async (req, res, next) => {
    try {
        const invoices = await Invoice.find()
            .populate('client', 'firmName accountNumber')
            .populate('document', 'caseNumber')
            .sort({ issueDate: -1 });

        res.status(200).json({
            success: true,
            count: invoices.length,
            data: invoices,
        });
    } catch (error) {
        next(error);
    }
};

/**
 * @desc    Get a single invoice by ID
 * @route   GET /api/invoices/:id
 * @access  Private/Admin
 */
exports.getInvoiceById = async (req, res, next) => {
    try {
        const invoice = await Invoice.findById(req.params.id)
            .populate('client')
            .populate('document', 'caseNumber title');

        if (!invoice) {
            return next(new CustomError(`Invoice not found with id of ${req.params.id}`, 404));
        }

        res.status(200).json({
            success: true,
            data: invoice,
        });
    } catch (error) {
        next(error);
    }
};

/**
 * @desc    Update an invoice status (e.g., mark as 'Paid' or 'Sent')
 * @route   PUT /api/invoices/:id/status
 * @access  Private/Admin
 */
exports.updateInvoiceStatus = async (req, res, next) => {
    try {
        const { status } = req.body;
        // Validate that the provided status is one of the allowed values from the schema enum
        const allowedStatuses = ['Draft', 'Sent', 'Paid', 'Overdue', 'Cancelled'];
        if (!status || !allowedStatuses.includes(status)) {
            return next(new CustomError(`Invalid status provided.`, 400));
        }

        const invoice = await Invoice.findByIdAndUpdate(
            req.params.id,
            { status },
            { new: true, runValidators: true }
        );

        if (!invoice) {
            return next(new CustomError(`Invoice not found with id of ${req.params.id}`, 404));
        }

        logger.info(`Invoice ${invoice.invoiceNumber} status updated to ${status}`);
        res.status(200).json({ success: true, data: invoice });

    } catch (error) {
        next(error);
    }
};

/**
 * @desc    Delete an invoice
 * @route   DELETE /api/invoices/:id
 * @access  Private/Admin
 */
exports.deleteInvoice = async (req, res, next) => {
    try {
        const invoice = await Invoice.findById(req.params.id);

        if (!invoice) {
            return next(new CustomError(`Invoice not found with id of ${req.params.id}`, 404));
        }

        // Data Integrity Check: For financial auditing, it's best practice to only allow
        // the deletion of invoices that are still in a 'Draft' state.
        if (invoice.status !== 'Draft') {
            return next(new CustomError(`Cannot delete an invoice that is not in a Draft state. Please cancel it instead.`, 400));
        }

        await invoice.remove();

        logger.info(`Draft invoice deleted: ${invoice.invoiceNumber}`);

        res.status(200).json({
            success: true,
            data: {},
        });

    } catch (error) {
        next(error);
    }
};
