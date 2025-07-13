const express = require('express');
const {
    addComment,
    getCommentsForDocument,
    updateComment,
    deleteComment,
} = require('../controllers/commentController');
const { protect } = require('../middleware/auth');  // ✅ Updated to modular auth import

const router = express.Router();

// Apply authentication globally
router.use(protect);

/**
 * @swagger
 * /api/comments:
 *   post:
 *     summary: Add a new comment to a document
 *     tags:
 *       - Comments
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - documentId
 *               - content
 *             properties:
 *               documentId:
 *                 type: string
 *                 example: 60c72b2f5f9b256d88f4e5b0
 *               content:
 *                 type: string
 *                 example: This is a helpful comment.
 *               parentCommentId:
 *                 type: string
 *                 example: 60c72b2f5f9b256d88f4e5c1
 *     responses:
 *       201:
 *         description: Comment added successfully.
 *       400:
 *         description: Validation error.
 *       404:
 *         description: Document or parent comment not found.
 */
router.route('/').post(addComment);

/**
 * @swagger
 * /api/comments/document/{documentId}:
 *   get:
 *     summary: Get all comments for a specific document
 *     tags:
 *       - Comments
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: documentId
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Comments retrieved successfully.
 *       404:
 *         description: Document not found.
 */
router.route('/document/:documentId').get(getCommentsForDocument);

/**
 * @swagger
 * /api/comments/{commentId}:
 *   put:
 *     summary: Update a comment
 *     tags:
 *       - Comments
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: commentId
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
 *               - content
 *             properties:
 *               content:
 *                 type: string
 *                 example: Updated comment content.
 *     responses:
 *       200:
 *         description: Comment updated successfully.
 *       403:
 *         description: Not authorized to update this comment.
 *       404:
 *         description: Comment not found.
 *   delete:
 *     summary: Delete a comment
 *     tags:
 *       - Comments
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: commentId
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Comment deleted successfully.
 *       403:
 *         description: Not authorized to delete this comment.
 *       404:
 *         description: Comment not found.
 */
router.route('/:commentId')
    .put(updateComment)
    .delete(deleteComment);

module.exports = router;
