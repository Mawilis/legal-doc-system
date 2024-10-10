// routes/documentRoutes.js

const express = require('express');
const documentController = require('../controllers/documentController'); // Import documentController
const { protect } = require('../middleware/authMiddleware'); // Import protect middleware for authentication
const router = express.Router();

// Debug log to verify all functions are correctly imported from documentController
console.log('Document Controller Functions:', Object.keys(documentController)); // Debug log

// Protect all routes below this line to ensure only authenticated users can access them
router.use(protect);

// Define routes using correct function names from documentController
router.post('/', documentController.createDocument);
router.get('/:documentId', documentController.getDocumentById);
router.get('/', documentController.getAllDocuments);
router.put('/:documentId', documentController.updateDocument);
router.delete('/:documentId', documentController.deleteDocument);

module.exports = router;
