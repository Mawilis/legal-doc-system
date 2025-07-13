const express = require('express');
const {
    accessChat,
    fetchChats,
    sendMessage,
    fetchMessages,
} = require('../controllers/chatController');
const { protect } = require('../middleware/auth');  // ✅ Updated to your modular auth structure

const router = express.Router();

// Apply authentication globally
router.use(protect);

/**
 * @swagger
 * /api/chat:
 *   post:
 *     summary: Access or create a chat between users
 *     description: Creates a new chat or retrieves an existing one between users.
 *     tags:
 *       - Chat
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - userId
 *             properties:
 *               userId:
 *                 type: string
 *                 example: 60c72b2f5f9b256d88f4e5b0
 *     responses:
 *       200:
 *         description: Chat accessed or created successfully.
 *       400:
 *         description: Bad request. Missing userId.
 *       401:
 *         description: Unauthorized. Token is missing or invalid.
 * 
 *   get:
 *     summary: Fetch all chats for the authenticated user
 *     description: Retrieves a list of all chats that the authenticated user is part of.
 *     tags:
 *       - Chat
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: List of chats retrieved successfully.
 *       401:
 *         description: Unauthorized. Token is missing or invalid.
 */
router
    .route('/')
    .post(accessChat)
    .get(fetchChats);

/**
 * @swagger
 * /api/chat/message:
 *   post:
 *     summary: Send a message in a chat
 *     description: Sends a message to a specified chat.
 *     tags:
 *       - Chat
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - chatId
 *               - content
 *             properties:
 *               chatId:
 *                 type: string
 *                 example: 60d1b2f5f9b256d88f4e5c1
 *               content:
 *                 type: string
 *                 example: Hello, how are you?
 *     responses:
 *       200:
 *         description: Message sent successfully.
 *       400:
 *         description: Bad request. Missing chatId or content.
 *       401:
 *         description: Unauthorized. Token is missing or invalid.
 */
router.route('/message').post(sendMessage);

/**
 * @swagger
 * /api/chat/{chatId}:
 *   get:
 *     summary: Fetch messages from a chat
 *     description: Retrieves messages for a specific chat ID.
 *     tags:
 *       - Chat
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: chatId
 *         required: true
 *         schema:
 *           type: string
 *         description: The ID of the chat to fetch messages from.
 *     responses:
 *       200:
 *         description: Messages retrieved successfully.
 *       400:
 *         description: Bad request. Invalid chat ID.
 *       401:
 *         description: Unauthorized. Token is missing or invalid.
 *       404:
 *         description: Chat not found.
 */
router.route('/:chatId').get(fetchMessages);

module.exports = router;
