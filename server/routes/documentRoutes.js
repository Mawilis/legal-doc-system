// documentRoutes.js
const express = require('express');
const documentController = require('../controllers/documentController');
const authController = require('../controllers/authController');
const router = express.Router();

// Protected routes for document management
router.use(authController.protect);

router.post('/', documentController.createDocument);
router.get('/:documentId', documentController.getDocumentById);
router.get('/', documentController.getAllDocuments);
router.put('/:documentId', documentController.updateDocument);
router.delete('/:documentId', documentController.deleteDocument);

module.exports = router;
