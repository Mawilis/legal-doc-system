// server/controllers/auditLogController.js

const AuditLog = require('../models/auditLogModel');
const CustomError = require('../utils/customError');
const logger = require('../utils/logger');

/**
 * @desc    Get all audit logs with filtering and pagination
 * @route   GET /api/audit
 * @access  Private/Admin
 */
exports.getAuditLogs = async (req, res, next) => {
    try {
        // --- Filtering ---
        // Build a query object based on query parameters from the request.
        const queryObj = { ...req.query };
        const excludedFields = ['page', 'sort', 'limit', 'fields'];
        excludedFields.forEach(el => delete queryObj[el]);

        // --- Pagination ---
        const page = parseInt(req.query.page, 10) || 1;
        const limit = parseInt(req.query.limit, 10) || 25; // Show 25 logs per page by default
        const skip = (page - 1) * limit;

        // --- Sorting ---
        const sortBy = req.query.sort ? req.query.sort.split(',').join(' ') : '-createdAt'; // Sort by newest first by default

        // Execute the query
        const logs = await AuditLog.find(queryObj)
            .populate('user', 'name email') // Populate user details
            .sort(sortBy)
            .skip(skip)
            .limit(limit);

        // Get total count for pagination metadata
        const totalLogs = await AuditLog.countDocuments(queryObj);

        res.status(200).json({
            success: true,
            count: logs.length,
            pagination: {
                currentPage: page,
                totalPages: Math.ceil(totalLogs / limit),
                totalLogs,
            },
            data: logs,
        });

    } catch (error) {
        logger.error(`Error fetching audit logs: ${error.message}`);
        next(error);
    }
};


// --- Helper Function to be used by other controllers ---
// This is not a route handler. It allows other parts of the app to easily create log entries.
exports.logAction = async (userId, action, details, status = 'SUCCESS', entity = null, ipAddress = null) => {
    try {
        await AuditLog.create({
            user: userId,
            action,
            details,
            status,
            entity,
            ipAddress,
        });
    } catch (error) {
        // We only log the error here and don't throw it, because a failure to log an action
        // should not crash the primary operation (e.g., a document update).
        logger.error(`Failed to create audit log: ${error.message}`);
    }
};
