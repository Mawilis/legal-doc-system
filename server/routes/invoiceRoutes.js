const express = require('express');
const {
    getAllInvoices,
    getInvoiceById,
    updateInvoiceStatus,
    deleteInvoice,
} = require('../controllers/invoiceController');
const { protect, authorize } = require('../middleware/auth');  // ✅ Updated to modular auth import

const router = express.Router();

// Secure all routes: only authenticated admins can manage invoices.
router.use(protect);
router.use(authorize('admin'));

/**
 * @swagger
 * /api/invoices:
 *   get:
 *     summary: Retrieve a list of all invoices
 *     description: Returns all invoices managed in the system.
 *     tags:
 *       - Invoices
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: A list of invoices retrieved successfully.
 *       401:
 *         description: Unauthorized. Token is missing or invalid.
 *       403:
 *         description: Forbidden. Admin access required.
 */
router.route('/').get(getAllInvoices);

/**
 * @swagger
 * /api/invoices/{id}:
 *   get:
 *     summary: Get a single invoice by ID
 *     description: Retrieves details of a specific invoice.
 *     tags:
 *       - Invoices
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *         description: The invoice ID.
 *     responses:
 *       200:
 *         description: Invoice retrieved successfully.
 *       400:
 *         description: Bad request. Invalid ID.
 *       401:
 *         description: Unauthorized. Token is missing or invalid.
 *       403:
 *         description: Forbidden. Admin access required.
 *       404:
 *         description: Invoice not found.
 *
 *   delete:
 *     summary: Delete a draft invoice
 *     description: Deletes a draft invoice by its ID.
 *     tags:
 *       - Invoices
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *         description: The invoice ID.
 *     responses:
 *       200:
 *         description: Invoice deleted successfully.
 *       400:
 *         description: Cannot delete an invoice that is not in a Draft state or invalid ID.
 *       401:
 *         description: Unauthorized. Token is missing or invalid.
 *       403:
 *         description: Forbidden. Admin access required.
 *       404:
 *         description: Invoice not found.
 */
router
    .route('/:id')
    .get(getInvoiceById)
    .delete(deleteInvoice);

/**
 * @swagger
 * /api/invoices/{id}/status:
 *   put:
 *     summary: Update the status of an invoice
 *     description: Updates the status of a specific invoice.
 *     tags:
 *       - Invoices
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *         description: The invoice ID.
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - status
 *             properties:
 *               status:
 *                 type: string
 *                 enum: [Draft, Sent, Paid, Overdue, Cancelled]
 *                 example: Sent
 *     responses:
 *       200:
 *         description: Invoice status updated successfully.
 *       400:
 *         description: Bad request. Invalid status or ID.
 *       401:
 *         description: Unauthorized. Token is missing or invalid.
 *       403:
 *         description: Forbidden. Admin access required.
 *       404:
 *         description: Invoice not found.
 */
router.route('/:id/status').put(updateInvoiceStatus);

module.exports = router;
