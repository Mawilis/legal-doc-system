const express = require('express');
const {
    getAllDocuments,
    getDocumentById,
    createDocument,
    updateDocument,
    deleteDocument,
    updateDocumentStatus,
} = require('../controllers/documentController');
const { protect, authorize } = require('../middleware/auth');  // ✅ Updated import

const router = express.Router();

// Apply authentication to all routes
router.use(protect);

/**
 * @swagger
 * /api/documents:
 *   get:
 *     summary: Get all documents
 *     tags:
 *       - Documents
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Documents retrieved successfully.
 *       401:
 *         description: Unauthorized.
 *   post:
 *     summary: Create a new document
 *     tags:
 *       - Documents
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - title
 *             properties:
 *               title:
 *                 type: string
 *                 example: New Contract Agreement
 *               content:
 *                 type: string
 *                 example: The contract states...
 *     responses:
 *       201:
 *         description: Document created successfully.
 *       400:
 *         description: Bad request.
 *       401:
 *         description: Unauthorized.
 */
router
    .route('/')
    .get(getAllDocuments)
    .post(createDocument);

/**
 * @swagger
 * /api/documents/{id}:
 *   get:
 *     summary: Get a document by ID
 *     tags:
 *       - Documents
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *         description: The document ID.
 *     responses:
 *       200:
 *         description: Document retrieved successfully.
 *       400:
 *         description: Bad request.
 *       401:
 *         description: Unauthorized.
 *       404:
 *         description: Not found.
 *   put:
 *     summary: Update a document
 *     tags:
 *       - Documents
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
 *               title:
 *                 type: string
 *                 example: Updated Contract Agreement
 *               content:
 *                 type: string
 *                 example: Updated content here...
 *     responses:
 *       200:
 *         description: Document updated successfully.
 *       400:
 *         description: Bad request.
 *       401:
 *         description: Unauthorized.
 *       404:
 *         description: Not found.
 *   delete:
 *     summary: Delete a document (admin only)
 *     tags:
 *       - Documents
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
 *         description: Document deleted successfully.
 *       400:
 *         description: Bad request.
 *       401:
 *         description: Unauthorized.
 *       403:
 *         description: Forbidden.
 *       404:
 *         description: Not found.
 */
router
    .route('/:id')
    .get(getDocumentById)
    .put(updateDocument)
    .delete(authorize('admin'), deleteDocument);

/**
 * @swagger
 * /api/documents/{id}/status:
 *   put:
 *     summary: Update document status
 *     tags:
 *       - Documents
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
 *             required:
 *               - status
 *             properties:
 *               status:
 *                 type: string
 *                 enum: [Draft, Published, Archived]
 *                 example: Published
 *     responses:
 *       200:
 *         description: Status updated successfully.
 *       400:
 *         description: Bad request.
 *       401:
 *         description: Unauthorized.
 *       404:
 *         description: Not found.
 */
router
    .route('/:id/status')
    .put(updateDocumentStatus);

module.exports = router;
