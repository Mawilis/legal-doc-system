// server/controllers/analyticsController.js

const User = require('../models/userModel');
const Document = require('../models/documentModel');
const Client = require('../models/clientModel');
const Invoice = require('../models/invoiceModel');
const CustomError = require('../utils/customError');
const logger = require('../utils/logger');

/**
 * @desc    Get system-wide statistics for dashboards
 * @route   GET /api/analytics/system-stats
 * @access  Private/Admin
 */
exports.getSystemStats = async (req, res, next) => {
    try {
        // Use Promise.all to run all database queries concurrently for maximum efficiency.
        const [
            totalUsers,
            totalClients,
            totalDocuments,
            documentsByStatus,
            totalUnpaidInvoices
        ] = await Promise.all([
            User.countDocuments(),
            Client.countDocuments(),
            Document.countDocuments(),
            // Use an aggregation pipeline to count documents for each status
            Document.aggregate([
                { $group: { _id: '$status', count: { $sum: 1 } } },
                { $sort: { _id: 1 } } // Sort alphabetically by status name
            ]),
            // Use an aggregation pipeline to calculate the total value of unpaid invoices
            Invoice.aggregate([
                { $match: { status: { $in: ['Sent', 'Overdue'] } } },
                { $group: { _id: null, totalAmount: { $sum: '$total' } } }
            ])
        ]);

        // Format the results into a clean object for the frontend.
        const stats = {
            totalUsers,
            totalClients,
            totalDocuments,
            documentsByStatus: documentsByStatus.reduce((acc, item) => {
                acc[item._id] = item.count;
                return acc;
            }, {}),
            unpaidInvoicesValue: totalUnpaidInvoices.length > 0 ? totalUnpaidInvoices[0].totalAmount : 0,
        };

        res.status(200).json({
            success: true,
            data: stats,
        });

    } catch (error) {
        logger.error(`Error fetching system stats: ${error.message}`);
        next(error);
    }
};
