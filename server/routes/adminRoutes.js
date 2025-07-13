const express = require('express');
const { getSystemStats } = require('../controllers/adminController');
const { protect, authorize } = require('../middleware/auth');  // ✅ Updated to reflect new modular auth path

const router = express.Router();

// Apply security middleware to all admin routes
router.use(protect);
router.use(authorize('admin'));

/**
 * @swagger
 * /api/admin/stats:
 *   get:
 *     summary: Retrieve system-wide statistics for the admin dashboard.
 *     description: Provides aggregated statistics including user count, sessions, and document summary.
 *     tags:
 *       - Admin
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Successfully retrieved admin statistics.
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 totalUsers:
 *                   type: integer
 *                   example: 150
 *                 activeSessions:
 *                   type: integer
 *                   example: 45
 *                 documentSummary:
 *                   type: object
 *                   properties:
 *                     totalDocuments:
 *                       type: integer
 *                       example: 300
 *                     drafts:
 *                       type: integer
 *                       example: 50
 *                     published:
 *                       type: integer
 *                       example: 250
 *       401:
 *         description: Unauthorized. Token missing or invalid.
 *       403:
 *         description: Forbidden. Admin access required.
 */
router.get('/stats', getSystemStats);

module.exports = router;
