// ~/server/controllers/adminController.js

const User = require('../models/userModel');
const Client = require('../models/clientModel');
const Document = require('../models/documentModel');
const Invoice = require('../models/invoiceModel');
const CustomError = require('../utils/customError');
const logger = require('../utils/logger');

/**
 * System statistics for admin dashboard
 */
exports.getSystemStats = async (req, res, next) => {
    try {
        const [
            totalUsers,
            totalClients,
            totalDocuments,
            documentsByStatus,
            unpaidInvoices
        ] = await Promise.all([
            User.countDocuments(),
            Client.countDocuments(),
            Document.countDocuments(),
            Document.aggregate([
                { $group: { _id: '$status', count: { $sum: 1 } } },
                { $sort: { _id: 1 } }
            ]),
            Invoice.aggregate([
                { $match: { status: { $in: ['Sent', 'Overdue'] } } },
                { $group: { _id: null, totalAmount: { $sum: '$total' } } }
            ])
        ]);

        const statusMap = {};
        documentsByStatus.forEach(({ _id, count }) => {
            statusMap[_id] = count;
        });

        res.status(200).json({
            success: true,
            data: {
                totalUsers,
                totalClients,
                totalDocuments,
                documentsByStatus: statusMap,
                unpaidInvoicesValue: unpaidInvoices[0]?.totalAmount || 0
            }
        });
    } catch (err) {
        logger.error(`[Admin Stats] Failed: ${err.message}`);
        next(new CustomError('System stats unavailable', 500));
    }
};
