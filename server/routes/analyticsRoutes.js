const express = require('express');
const { getSystemStats } = require('../controllers/analyticsController');
const { protect, authorize } = require('../middleware/auth');  // ✅ Updated import path

const router = express.Router();

// All analytics routes are sensitive and restricted to admin users
router.use(protect);
router.use(authorize('admin'));

/**
 * @swagger
 * /api/analytics/system-stats:
 *   get:
 *     summary: Retrieve detailed system-wide analytics for the admin dashboard.
 *     description: Provides comprehensive system analytics including user trends, document metrics, and session statistics for administrators.
 *     tags:
 *       - Analytics
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Successfully retrieved system analytics.
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 userTrends:
 *                   type: object
 *                   properties:
 *                     newUsersThisMonth:
 *                       type: integer
 *                       example: 25
 *                     totalUsers:
 *                       type: integer
 *                       example: 150
 *                 documentMetrics:
 *                   type: object
 *                   properties:
 *                     totalDocuments:
 *                       type: integer
 *                       example: 320
 *                     drafts:
 *                       type: integer
 *                       example: 50
 *                     published:
 *                       type: integer
 *                       example: 270
 *                 activeSessions:
 *                   type: integer
 *                   example: 47
 *       401:
 *         description: Authentication required. Token is missing or invalid.
 *       403:
 *         description: Access forbidden. User is not an administrator.
 */
router.get('/system-stats', getSystemStats);

module.exports = router;
