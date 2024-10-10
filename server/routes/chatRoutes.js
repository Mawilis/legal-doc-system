// routes/chatRoutes.js

const express = require('express');
const chatController = require('../controllers/chatController'); // Assuming chatController.js is already created
const { protect } = require('../middleware/authMiddleware'); // Protect middleware for authentication
const router = express.Router();

// Protect all routes to ensure only authenticated users can access them
router.use(protect);

// Define chat routes
router.get('/messages', chatController.getMessages); // Get all chat messages
router.post('/messages', chatController.sendMessage); // Send a new message
router.delete('/messages/:messageId', chatController.deleteMessage); // Delete a message by ID

// Export the router
module.exports = router;
