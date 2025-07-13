const express = require('express');
const {
    getUserApiKeys,
    createApiKey,
    revokeApiKey,
} = require('../controllers/apiKeyController');
const { protect } = require('../middleware/auth');  // ✅ Updated to point to your modular auth

const router = express.Router();

// Apply authentication globally
router.use(protect);

/**
 * @swagger
 * /api/apikeys:
 *   get:
 *     summary: Get all API keys for the logged-in user
 *     tags:
 *       - API Keys
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: API keys retrieved successfully.
 *       401:
 *         description: Unauthorized. Token missing or invalid.
 *   post:
 *     summary: Generate a new API key for the logged-in user
 *     tags:
 *       - API Keys
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
 *             properties:
 *               name:
 *                 type: string
 *                 example: My Integration Key
 *               permissions:
 *                 type: array
 *                 items:
 *                   type: string
 *                   enum: [read_only, read_write]
 *                 example: [read_only]
 *               expiresAt:
 *                 type: string
 *                 format: date-time
 *                 example: 2025-12-31T23:59:59Z
 *     responses:
 *       201:
 *         description: API key created successfully. The key will only be shown once.
 *       400:
 *         description: Validation error.
 *       401:
 *         description: Unauthorized.
 */
router.route('/')
    .get(getUserApiKeys)
    .post(createApiKey);

/**
 * @swagger
 * /api/apikeys/{id}:
 *   delete:
 *     summary: Revoke (delete) an API key
 *     tags:
 *       - API Keys
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
 *         description: API key revoked successfully.
 *       403:
 *         description: Not authorized to revoke this API key.
 *       404:
 *         description: API key not found.
 *       401:
 *         description: Unauthorized.
 */
router.route('/:id')
    .delete(revokeApiKey);

module.exports = router;
