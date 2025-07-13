const express = require('express');
const { getDashboardStats } = require('../controllers/dashboardController');
const { protect } = require('../middleware/auth');  // ✅ Updated to modular auth import

const router = express.Router();

// Apply authentication globally
router.use(protect);

/**
 * @swagger
 * /api/dashboard/stats:
 *   get:
 *     summary: Get dashboard statistics
 *     description: Retrieves key statistics and metrics for the authenticated user's dashboard.
 *     tags:
 *       - Dashboard
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Dashboard statistics retrieved successfully.
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 totalDocuments:
 *                   type: integer
 *                   example: 120
 *                 activeProjects:
 *                   type: integer
 *                   example: 5
 *                 recentActivity:
 *                   type: array
 *                   items:
 *                     type: string
 *                   example: ["Document A edited", "Document B created"]
 *       401:
 *         description: Unauthorized. Token is missing or invalid.
 */
router.route('/stats').get(getDashboardStats);

module.exports = router;
