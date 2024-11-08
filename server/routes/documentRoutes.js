const express = require('express');
const documentController = require('../controllers/documentController');
const { protect, authorize } = require('../middleware/authMiddleware');
const router = express.Router();

// Protect all routes to ensure only authenticated users can access them
router.use(protect);

// Define routes with appropriate authorization checks
router.post('/', authorize('Admin', 'Editor'), documentController.createDocument);
router.get('/:documentId', documentController.getDocumentById);  // Viewable by authenticated users
router.get('/', authorize('Admin', 'User'), documentController.getAllDocuments);
router.put('/:documentId', authorize('Admin', 'Editor'), documentController.updateDocument);
router.delete('/:documentId', authorize('Admin'), documentController.deleteDocument);
router.put('/:documentId/scanned', authorize('Admin', 'Editor'), documentController.markDocumentAsScanned);
router.put('/:documentId/status', authorize('Admin', 'Editor'), documentController.updateServiceStatus);

module.exports = router;
