// server/controllers/dashboardController.js

const Document = require('../models/documentModel');
const CustomError = require('../utils/customError');
const logger = require('../utils/logger');
const mongoose = require('mongoose');

/**
 * @desc    Get dashboard statistics
 * @route   GET /api/dashboard/stats
 * @access  Private
 */
exports.getDashboardStats = async (req, res, next) => {
    try {
        // --- 1. Basic Counts ---
        // Get total counts for key document statuses.
        const pendingCount = await Document.countDocuments({ status: { $in: ['Registered', 'Assigned', 'Out for Service'] } });
        const completedThisMonth = await Document.countDocuments({
            status: 'Served',
            updatedAt: { $gte: new Date(new Date().setDate(1)) } // From the first day of the current month
        });

        // --- 2. Aggregation Pipeline for Advanced Stats ---
        // The aggregation pipeline allows for complex data processing directly in the database.
        const statsByDeputy = await Document.aggregate([
            // Stage 1: Filter for documents that are currently assigned and in progress.
            {
                $match: {
                    status: { $in: ['Assigned', 'Out for Service', 'Attempted'] },
                    assignedTo: { $exists: true, $ne: null }
                }
            },
            // Stage 2: Group documents by the `assignedTo` user ID and count them.
            {
                $group: {
                    _id: '$assignedTo', // Group by the deputy's ID
                    activeCases: { $sum: 1 } // Count the number of documents in each group
                }
            },
            // Stage 3: Look up the user's details from the 'users' collection.
            {
                $lookup: {
                    from: 'users',         // The collection to join with
                    localField: '_id',     // The field from the input documents (the grouped _id)
                    foreignField: '_id',   // The field from the documents of the "from" collection
                    as: 'deputyDetails'    // The name of the new array field to add
                }
            },
            // Stage 4: Deconstruct the 'deputyDetails' array field from a one-element array to a single object.
            {
                $unwind: '$deputyDetails'
            },
            // Stage 5: Project the final shape of our data.
            {
                $project: {
                    _id: 0, // Exclude the default _id field
                    deputyId: '$_id',
                    deputyName: '$deputyDetails.name',
                    activeCases: 1 // Include the activeCases count
                }
            },
            // Stage 6: Sort by the number of active cases in descending order.
            {
                $sort: { activeCases: -1 }
            },
            // Stage 7: Limit the results to the top 5 deputies.
            {
                $limit: 5
            }
        ]);


        // --- 3. Assemble the Final Response ---
        const dashboardData = {
            pendingDocuments: pendingCount,
            completedThisMonth: completedThisMonth,
            workloadByDeputy: statsByDeputy
        };

        res.status(200).json({
            success: true,
            data: dashboardData,
        });

    } catch (error) {
        logger.error(`Error fetching dashboard stats: ${error.message}`);
        next(error);
    }
};
