const express = require('express');
const { generateDocumentReportPDF } = require('../controllers/reportController');
const { protect, authorize } = require('../middleware/auth');  // ✅ Updated path

const router = express.Router();

// Apply security globally
router.use(protect);
router.use(authorize('admin'));

/**
 * @swagger
 * /api/reports/documents/pdf:
 *   get:
 *     summary: Generate a PDF report for documents
 *     description: Generates a PDF report of documents created within a specified date range.
 *     tags:
 *       - Reports
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: startDate
 *         required: true
 *         schema:
 *           type: string
 *           format: date
 *         description: Start date in YYYY-MM-DD format.
 *       - in: query
 *         name: endDate
 *         required: true
 *         schema:
 *           type: string
 *           format: date
 *         description: End date in YYYY-MM-DD format.
 *     responses:
 *       200:
 *         description: PDF report generated and downloaded successfully.
 *         content:
 *           application/pdf:
 *             schema:
 *               type: string
 *               format: binary
 *       400:
 *         description: Bad request. Missing or invalid dates.
 *       401:
 *         description: Unauthorized. Token missing or invalid.
 *       403:
 *         description: Forbidden. Admin access required.
 *       404:
 *         description: No documents found in the specified date range.
 */
router.get('/documents/pdf', generateDocumentReportPDF);

module.exports = router;
