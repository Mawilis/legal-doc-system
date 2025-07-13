const express = require('express');
const {
    createDeputyProfile,
    getAllDeputies,
    getDeputyById,
    updateDeputyProfile,
    deleteDeputyProfile,
} = require('../controllers/deputyController');
const { protect, authorize } = require('../middleware/auth');  // ✅ Updated import

const router = express.Router();

// Apply security middleware to all routes
router.use(protect);
router.use(authorize('admin'));

/**
 * @swagger
 * /api/deputies:
 *   post:
 *     summary: Create a new deputy profile
 *     tags:
 *       - Deputies
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - name
 *               - email
 *             properties:
 *               name:
 *                 type: string
 *                 example: Jane Deputy
 *               email:
 *                 type: string
 *                 format: email
 *                 example: jane.deputy@example.com
 *               phone:
 *                 type: string
 *                 example: "+1234567890"
 *     responses:
 *       201:
 *         description: Deputy profile created successfully.
 *       400:
 *         description: Bad request. Invalid or missing data.
 *       401:
 *         description: Unauthorized.
 *       403:
 *         description: Forbidden.
 *   get:
 *     summary: Get all deputy profiles
 *     tags:
 *       - Deputies
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: List of deputies retrieved successfully.
 *       401:
 *         description: Unauthorized.
 *       403:
 *         description: Forbidden.
 */
router
    .route('/')
    .post(createDeputyProfile)
    .get(getAllDeputies);

/**
 * @swagger
 * /api/deputies/{id}:
 *   get:
 *     summary: Get a deputy profile by ID
 *     tags:
 *       - Deputies
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *         description: The deputy ID.
 *     responses:
 *       200:
 *         description: Deputy profile retrieved successfully.
 *       400:
 *         description: Bad request. Invalid ID.
 *       401:
 *         description: Unauthorized.
 *       403:
 *         description: Forbidden.
 *       404:
 *         description: Not found.
 *   put:
 *     summary: Update a deputy profile
 *     tags:
 *       - Deputies
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *         description: The deputy ID.
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               name:
 *                 type: string
 *                 example: Jane Deputy Updated
 *               email:
 *                 type: string
 *                 format: email
 *                 example: jane.updated@example.com
 *               phone:
 *                 type: string
 *                 example: "+1987654321"
 *     responses:
 *       200:
 *         description: Deputy profile updated successfully.
 *       400:
 *         description: Bad request. Invalid data or ID.
 *       401:
 *         description: Unauthorized.
 *       403:
 *         description: Forbidden.
 *       404:
 *         description: Not found.
 *   delete:
 *     summary: Delete a deputy profile
 *     tags:
 *       - Deputies
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *         description: The deputy ID.
 *     responses:
 *       200:
 *         description: Deputy profile deleted successfully.
 *       400:
 *         description: Bad request. Invalid ID.
 *       401:
 *         description: Unauthorized.
 *       403:
 *         description: Forbidden.
 *       404:
 *         description: Not found.
 */
router
    .route('/:id')
    .get(getDeputyById)
    .put(updateDeputyProfile)
    .delete(deleteDeputyProfile);

module.exports = router;
