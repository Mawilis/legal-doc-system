// server/routes/searchRoutes.js

const express = require('express');
const { protect } = require('../middleware/auth'); // Adjust based on your modular auth
const { searchSystem } = require('../controllers/searchController');

const router = express.Router();

/**
 * @swagger
 * /api/search:
 *   get:
 *     summary: Perform a system-wide search
 *     description: Searches documents, clients, and users for matching records.
 *     tags:
 *       - Search
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: q
 *         required: true
 *         schema:
 *           type: string
 *         description: The search term.
 *     responses:
 *       200:
 *         description: Search results retrieved successfully.
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                 data:
 *                   type: object
 *                   properties:
 *                     documents:
 *                       type: array
 *                       items:
 *                         type: object
 *                     clients:
 *                       type: array
 *                       items:
 *                         type: object
 *                     users:
 *                       type: array
 *                       items:
 *                         type: object
 *       400:
 *         description: Bad request. Missing or invalid query.
 *       401:
 *         description: Unauthorized. Token missing or invalid.
 */
router.get('/', protect, searchSystem);
module.exports = router;
