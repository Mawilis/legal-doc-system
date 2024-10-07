// routes/chatRoutes.js
const express = require('express');
const chatController = require('../controllers/chatController');
const { protect, restrictToAdmin } = require('../middleware/authMiddleware');  // Import middleware
const router = express.Router();

// Protect all routes to ensure only authenticated users can access
router.use(protect);

// Route to get chat messages
router.get('/', chatController.getMessages);

// Route to send a message
router.post('/', chatController.sendMessage);

// Optional: Route to delete a message (Admin-only)
router.delete('/:messageId', restrictToAdmin, chatController.deleteMessage);

module.exports = router;
