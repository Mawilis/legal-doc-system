/**
 * File: server/routes/documentRoutes.js
 * -----------------------------------------------------------------------------
 * COLLABORATION NOTES:
 * - Purpose: Express router for Document CRUD endpoints.
 * - Synchronization: Must match exports in documentController.js.
 * - Engineers: Always import controller functions explicitly; avoid undefined references.
 * -----------------------------------------------------------------------------
 */

'use strict';

const express = require('express');
const router = express.Router();
const documentController = require('../controllers/documentController');
const { protect } = require('../middleware/authMiddleware'); // if you want auth guard

// GET all documents
router.get('/', protect, documentController.getDocuments);

// GET single document
router.get('/:id', protect, documentController.getDocumentById);

// CREATE document
router.post('/', protect, documentController.createDocument);

// UPDATE document
router.put('/:id', protect, documentController.updateDocument);

// DELETE document
router.delete('/:id', protect, documentController.deleteDocument);

module.exports = router;
