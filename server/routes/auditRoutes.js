const express = require('express');
const {
    generateDocumentReportPDF,
    generateDocumentReportCSV
} = require('../controllers/reportController');
const { protect, authorize } = require('../middleware/auth');

const router = express.Router();

// Apply security middleware globally for this route
router.use(protect);
router.use(authorize('admin'));

/**
 * @swagger
 * /api/reports/documents/pdf:
 *   get:
 *     summary: Generate a PDF report of documents
 *     description: Creates and downloads a PDF listing documents within a date range.
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
 *         description: The start date (YYYY-MM-DD).
 *       - in: query
 *         name: endDate
 *         required: true
 *         schema:
 *           type: string
 *           format: date
 *         description: The end date (YYYY-MM-DD).
 *     responses:
 *       200:
 *         description: PDF file generated successfully.
 *         content:
 *           application/pdf:
 *             schema:
 *               type: string
 *               format: binary
 *       400:
 *         description: Bad request (e.g., missing dates).
 *       401:
 *         description: Unauthorized (token missing/invalid).
 *       403:
 *         description: Forbidden (admin access required).
 */
router.get('/documents/pdf', generateDocumentReportPDF);

/**
 * @swagger
 * /api/reports/documents/csv:
 *   get:
 *     summary: Generate a CSV report of documents
 *     description: Creates and downloads a CSV listing documents within a date range.
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
 *         description: The start date (YYYY-MM-DD).
 *       - in: query
 *         name: endDate
 *         required: true
 *         schema:
 *           type: string
 *           format: date
 *         description: The end date (YYYY-MM-DD).
 *     responses:
 *       200:
 *         description: CSV file generated successfully.
 *         content:
 *           text/csv:
 *             schema:
 *               type: string
 *       400:
 *         description: Bad request (e.g., missing dates).
 *       401:
 *         description: Unauthorized (token missing/invalid).
 *       403:
 *         description: Forbidden (admin access required).
 */
router.get('/documents/csv', generateDocumentReportCSV);

module.exports = router;
