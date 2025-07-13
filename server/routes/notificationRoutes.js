const express = require('express');
const {
    getNotifications,
    markAsRead,
    markAllAsRead,
} = require('../controllers/notificationController');
const { protect } = require('../middleware/auth');  // ✅ Updated path to match modular auth

const router = express.Router();

router.use(protect);

/**
 * @swagger
 * /api/notifications:
 *   get:
 *     summary: Get all notifications for the authenticated user
 *     tags:
 *       - Notifications
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Notifications retrieved successfully.
 *       401:
 *         description: Unauthorized. Token missing or invalid.
 */
router.get('/', getNotifications);

/**
 * @swagger
 * /api/notifications/readall:
 *   put:
 *     summary: Mark all notifications as read
 *     tags:
 *       - Notifications
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: All notifications marked as read successfully.
 *       401:
 *         description: Unauthorized. Token missing or invalid.
 */
router.put('/readall', markAllAsRead);

/**
 * @swagger
 * /api/notifications/{id}/read:
 *   put:
 *     summary: Mark a specific notification as read
 *     tags:
 *       - Notifications
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *         description: The ID of the notification to mark as read.
 *     responses:
 *       200:
 *         description: Notification marked as read successfully.
 *       400:
 *         description: Invalid notification ID.
 *       401:
 *         description: Unauthorized. Token missing or invalid.
 *       404:
 *         description: Notification not found.
 */
router.put('/:id/read', markAsRead);

module.exports = router;
