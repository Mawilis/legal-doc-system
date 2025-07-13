const express = require('express');
const {
    getAllUsers,
    getUserById,
    createUser,
    updateUser,
    deleteUser,
} = require('../controllers/userController');
const { protect, authorize } = require('../middleware/auth');  // ✅ Updated path

const router = express.Router();

// Apply authentication + admin authorization globally
router.use(protect);
router.use(authorize('admin'));

/**
 * @swagger
 * /api/users:
 *   get:
 *     summary: Get all users
 *     tags:
 *       - Users
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Users retrieved successfully.
 *       401:
 *         description: Unauthorized. Token is missing or invalid.
 *       403:
 *         description: Forbidden. Admin access required.
 *   post:
 *     summary: Create a new user
 *     tags:
 *       - Users
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
 *               - password
 *             properties:
 *               name:
 *                 type: string
 *                 example: John Doe
 *               email:
 *                 type: string
 *                 format: email
 *                 example: john.doe@example.com
 *               password:
 *                 type: string
 *                 format: password
 *                 example: P@ssw0rd123
 *     responses:
 *       201:
 *         description: User created successfully.
 *       400:
 *         description: Bad request. Invalid data.
 *       401:
 *         description: Unauthorized. Token is missing or invalid.
 *       403:
 *         description: Forbidden. Admin access required.
 */
router
    .route('/')
    .get(getAllUsers)
    .post(createUser);

/**
 * @swagger
 * /api/users/{id}:
 *   get:
 *     summary: Get a user by ID
 *     tags:
 *       - Users
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: User retrieved successfully.
 *       400:
 *         description: Bad request. Invalid ID.
 *       401:
 *         description: Unauthorized. Token is missing or invalid.
 *       403:
 *         description: Forbidden. Admin access required.
 *       404:
 *         description: User not found.
 *   put:
 *     summary: Update a user by ID
 *     tags:
 *       - Users
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               name:
 *                 type: string
 *                 example: Updated User
 *               email:
 *                 type: string
 *                 format: email
 *                 example: updated@example.com
 *     responses:
 *       200:
 *         description: User updated successfully.
 *       400:
 *         description: Bad request. Invalid data or ID.
 *       401:
 *         description: Unauthorized. Token is missing or invalid.
 *       403:
 *         description: Forbidden. Admin access required.
 *       404:
 *         description: User not found.
 *   delete:
 *     summary: Delete a user by ID
 *     tags:
 *       - Users
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: User deleted successfully.
 *       400:
 *         description: Bad request. Invalid ID.
 *       401:
 *         description: Unauthorized. Token is missing or invalid.
 *       403:
 *         description: Forbidden. Admin access required.
 *       404:
 *         description: User not found.
 */
router
    .route('/:id')
    .get(getUserById)
    .put(updateUser)
    .delete(deleteUser);

module.exports = router;
