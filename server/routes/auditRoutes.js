// ~/server/routes/auditRoutes.js

const express = require('express');
const { getAuditLogs, exportAuditLogsToCSV } = require('../controllers/auditController');
const { protect, authorize } = require('../middleware/authMiddleware'); // Assuming this path

const router = express.Router();

// Apply security middleware to all routes in this file.
// Only authenticated users with the 'admin' role can proceed.
router.use(protect);
router.use(authorize('admin'));

/**
 * @swagger
 * /api/audit:
 * get:
 * summary: Retrieve audit logs for UI display
 * description: Fetches a paginated list of audit logs. Can be filtered by user, status, or method.
 * tags:
 * - Audit
 * security:
 * - bearerAuth: []
 * parameters:
 * - in: query
 * name: page
 * schema:
 * type: integer
 * description: The page number for pagination.
 * - in: query
 * name: limit
 * schema:
 * type: integer
 * description: The number of logs to return per page.
 * - in: query
 * name: status
 * schema:
 * type: string
 * enum: [SUCCESS, FAILED]
 * description: Filter logs by status.
 * responses:
 * 200:
 * description: A paginated list of audit logs.
 * 401:
 * description: Unauthorized.
 * 403:
 * description: Forbidden.
 */
router.route('/').get(getAuditLogs);

/**
 * @swagger
 * /api/audit/export/csv:
 * get:
 * summary: Export all audit logs to a CSV file
 * description: Generates and downloads a CSV file containing all audit log entries.
 * tags:
 * - Audit
 * security:
 * - bearerAuth: []
 * responses:
 * 200:
 * description: CSV file generated successfully.
 * content:
 * text/csv:
 * schema:
 * type: string
 * format: binary
 * 401:
 * description: Unauthorized.
 * 403:
 * description: Forbidden.
 */
router.route('/export/csv').get(exportAuditLogsToCSV);

module.exports = router;
