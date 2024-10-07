// chatRoutes.js
const express = require('express');
const chatController = require('../controllers/chatController');
const authController = require('../controllers/authController');
const router = express.Router();

// Protect routes to ensure only authenticated users can send or receive messages
router.use(authController.protect);

// Route to get chat messages
router.get('/', chatController.getMessages);

// Route to send a message
router.post('/', chatController.sendMessage);

// Optional: Route to delete a message (Admin-only)
router.delete('/:messageId', authController.restrictToAdmin, chatController.deleteMessage);

module.exports = router;
