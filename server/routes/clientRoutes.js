const express = require('express');
const {
    createClient,
    getAllClients,
    getClientById,
    updateClient,
    deleteClient,
} = require('../controllers/clientController');
const { protect, authorize } = require('../middleware/auth');  // ✅ Updated path

const router = express.Router();

// Apply security middleware to all routes in this file
router.use(protect);
router.use(authorize('admin'));

/**
 * @swagger
 * /api/clients:
 *   post:
 *     summary: Create a new client
 *     tags:
 *       - Clients
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
 *                 example: Acme Corporation
 *               email:
 *                 type: string
 *                 format: email
 *                 example: contact@acme.com
 *               phone:
 *                 type: string
 *                 example: "+1234567890"
 *     responses:
 *       201:
 *         description: Client created successfully.
 *       400:
 *         description: Bad request. Invalid or missing data.
 *       401:
 *         description: Unauthorized.
 *       403:
 *         description: Forbidden.
 *   get:
 *     summary: Get a list of all clients
 *     tags:
 *       - Clients
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Clients retrieved successfully.
 *       401:
 *         description: Unauthorized.
 *       403:
 *         description: Forbidden.
 */
router
    .route('/')
    .post(createClient)
    .get(getAllClients);

/**
 * @swagger
 * /api/clients/{id}:
 *   get:
 *     summary: Get client by ID
 *     tags:
 *       - Clients
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
 *         description: Client retrieved successfully.
 *       400:
 *         description: Bad request. Invalid ID.
 *       401:
 *         description: Unauthorized.
 *       403:
 *         description: Forbidden.
 *       404:
 *         description: Not found.
 *   put:
 *     summary: Update client by ID
 *     tags:
 *       - Clients
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
 *                 example: Acme Corporation Updated
 *               email:
 *                 type: string
 *                 format: email
 *                 example: new-contact@acme.com
 *               phone:
 *                 type: string
 *                 example: "+1987654321"
 *     responses:
 *       200:
 *         description: Client updated successfully.
 *       400:
 *         description: Bad request. Invalid data or ID.
 *       401:
 *         description: Unauthorized.
 *       403:
 *         description: Forbidden.
 *       404:
 *         description: Not found.
 *   delete:
 *     summary: Delete client by ID
 *     tags:
 *       - Clients
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
 *         description: Client deleted successfully.
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
    .get(getClientById)
    .put(updateClient)
    .delete(deleteClient);

module.exports = router;
