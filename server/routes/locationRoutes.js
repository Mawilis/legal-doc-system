// ~/server/routes/locationRoutes.js

const express = require('express');
const { updateLocation, getAllLocations, getUserPath } = require('../controllers/locationController');
const { protect, authorize } = require('../middleware/authMiddleware');

const router = express.Router();

// This middleware ensures that any user accessing these routes must be authenticated.
router.use(protect);

// Route for sheriffs to update their own location
router.route('/').post(authorize('sheriff'), updateLocation);

// Route for admins to get the last known location of all users
router.route('/').get(authorize('admin'), getAllLocations);

/**
 * @swagger
 * /api/locations/history/{userId}:
 * get:
 * summary: Get a user's historical location path
 * description: Allows an authenticated admin to retrieve the full location history for a specific user, sorted by time.
 * tags: [Location]
 * security:
 * - bearerAuth: []
 * parameters:
 * - in: path
 * name: userId
 * required: true
 * schema:
 * type: string
 * description: The ID of the user whose path is to be retrieved.
 * responses:
 * 200:
 * description: An array of historical location points.
 * 403:
 * description: Forbidden, user is not an admin.
 * 404:
 * description: No location history found for the specified user.
 */
router.route('/history/:userId').get(authorize('admin'), getUserPath);

module.exports = router;
