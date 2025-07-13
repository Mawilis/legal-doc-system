const express = require('express');
const {
    createRole,
    getAllRoles,
    updateRole,
    deleteRole,
    assignRoleToUser,
} = require('../controllers/roleController');
const { protect, authorize } = require('../middleware/auth');  // ✅ Updated to modular path

const router = express.Router();

// All routes require admin privileges
router.use(protect);
router.use(authorize('admin'));

/**
 * @swagger
 * /api/roles:
 *   post:
 *     summary: Create a new role
 *     tags:
 *       - Roles
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
 *               - permissions
 *             properties:
 *               name:
 *                 type: string
 *                 example: EDITOR
 *               description:
 *                 type: string
 *                 example: Role with edit permissions
 *               permissions:
 *                 type: array
 *                 items:
 *                   type: string
 *                 example: [ "edit_documents", "view_documents" ]
 *     responses:
 *       201:
 *         description: Role created successfully.
 *       400:
 *         description: Bad request.
 * 
 *   get:
 *     summary: Get all roles
 *     tags:
 *       - Roles
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: List of roles retrieved successfully.
 */
router.route('/')
    .post(createRole)
    .get(getAllRoles);

/**
 * @swagger
 * /api/roles/{id}:
 *   put:
 *     summary: Update a role's description or permissions
 *     tags:
 *       - Roles
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
 *               description:
 *                 type: string
 *               permissions:
 *                 type: array
 *                 items:
 *                   type: string
 *     responses:
 *       200:
 *         description: Role updated successfully.
 *       400:
 *         description: Bad request.
 *       404:
 *         description: Role not found.
 * 
 *   delete:
 *     summary: Delete a role
 *     tags:
 *       - Roles
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
 *         description: Role deleted successfully.
 *       400:
 *         description: Cannot delete core role or assigned role.
 *       404:
 *         description: Role not found.
 */
router.route('/:id')
    .put(updateRole)
    .delete(deleteRole);

/**
 * @swagger
 * /api/roles/assign:
 *   post:
 *     summary: Assign a role to a user
 *     tags:
 *       - Roles
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - userId
 *               - roleName
 *             properties:
 *               userId:
 *                 type: string
 *                 example: 60d0fe4f5311236168a109ca
 *               roleName:
 *                 type: string
 *                 example: EDITOR
 *     responses:
 *       200:
 *         description: Role assigned successfully.
 *       400:
 *         description: Bad request.
 *       404:
 *         description: User or role not found.
 */
router.post('/assign', assignRoleToUser);

module.exports = router;
