// server/routes/fileUploadRoutes.js

const express = require('express');
const { protect } = require('../middleware/auth');  // ✅ Adjust to your actual auth path
const { uploadDocument } = require('../controllers/fileUploadController');

const router = express.Router();

/**
 * @swagger
 * /api/upload/document/{documentId}:
 *   post:
 *     summary: Upload a file for a specific document
 *     description: Uploads a file (PDF, DOC, DOCX, JPG, PNG) for a document by ID.
 *     tags:
 *       - FileUpload
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: documentId
 *         required: true
 *         schema:
 *           type: string
 *         description: Document ID
 *     requestBody:
 *       required: true
 *       content:
 *         multipart/form-data:
 *           schema:
 *             type: object
 *             required:
 *               - documentFile
 *             properties:
 *               documentFile:
 *                 type: string
 *                 format: binary
 *                 description: The file to upload (PDF, DOC, DOCX, JPG, PNG)
 *     responses:
 *       200:
 *         description: File uploaded successfully
 *       400:
 *         description: Bad request (missing file or invalid type)
 *       401:
 *         description: Unauthorized
 *       404:
 *         description: Document not found
 */
router.post('/document/:documentId', protect, uploadDocument);

module.exports = router;
