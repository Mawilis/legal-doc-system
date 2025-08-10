// ~/server/controllers/auditController.js

const AuditLog = require('../models/auditLogModel');
const asyncHandler = require('../middleware/asyncHandler'); // Assuming an async handler utility
const { Parser } = require('json2csv'); // For converting data to CSV format

/**
 * @desc    Get all audit logs with filtering and pagination for UI display.
 * @route   GET /api/audit
 * @access  Private/Admin
 */
exports.getAuditLogs = asyncHandler(async (req, res, next) => {
    // --- Pagination Setup ---
    const page = parseInt(req.query.page, 10) || 1;
    const limit = parseInt(req.query.limit, 10) || 25;
    const startIndex = (page - 1) * limit;
    const total = await AuditLog.countDocuments();

    // --- Database Query ---
    const logs = await AuditLog.find(req.query) // Pass query params for filtering
        .populate('user', 'name email') // Populate user details for context
        .sort({ createdAt: -1 }) // Show the most recent logs first
        .skip(startIndex)
        .limit(limit);

    // --- Pagination Metadata ---
    const pagination = {};
    if ((startIndex + limit) < total) {
        pagination.next = { page: page + 1, limit };
    }
    if (startIndex > 0) {
        pagination.prev = { page: page - 1, limit };
    }

    res.status(200).json({
        success: true,
        count: logs.length,
        total,
        pagination,
        data: logs,
    });
});

/**
 * @desc    Export audit logs to a CSV file.
 * @route   GET /api/audit/export/csv
 * @access  Private/Admin
 */
exports.exportAuditLogsToCSV = asyncHandler(async (req, res, next) => {
    // Fetch all logs without pagination for a complete export
    const logs = await AuditLog.find().populate('user', 'name email').sort({ createdAt: -1 });

    // Define the fields for the CSV file
    const fields = [
        { label: 'Timestamp', value: 'createdAt' },
        { label: 'User Name', value: 'user.name' },
        { label: 'User Email', value: 'email' },
        { label: 'Method', value: 'method' },
        { label: 'Path', value: 'path' },
        { label: 'Status', value: 'status' },
        { label: 'IP Address', value: 'ip' },
        { label: 'Response Time (ms)', value: 'responseTime' },
    ];

    // Create a new CSV parser
    const json2csvParser = new Parser({ fields });
    const csv = json2csvParser.parse(logs);

    // Set headers to prompt a file download
    res.header('Content-Type', 'text/csv');
    res.attachment('audit-logs.csv');
    res.status(200).send(csv);
});
