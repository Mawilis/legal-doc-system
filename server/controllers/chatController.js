// controllers/chatController.js

const ChatMessage = require('../models/chatMessageModel'); // Import the ChatMessage model
const CustomError = require('../utils/customError'); // Import custom error handling class
const { getIo } = require('../utils/socket'); // Import getIo function from socket utility
const User = require('../models/userModel'); // Import User model for user-based logic

/**
 * Get all messages for a specific chat room or user with pagination support.
 * Implement security checks to ensure users only access their own messages unless they're admins.
 */
const getMessages = async (req, res, next) => {
    try {
        const { chatRoomId, page = 1, limit = 20 } = req.query; // Pagination parameters
        const skip = (page - 1) * limit; // Calculate documents to skip

        // Set filter criteria based on chat room or user ID
        const filterCriteria = chatRoomId ? { chatRoom: chatRoomId } : { user: req.user.id };

        // Allow admins to access all messages
        if (req.user.role === 'admin') {
            delete filterCriteria.user;
        }

        // Fetch messages with pagination and populate user details
        const messages = await ChatMessage.find(filterCriteria)
            .skip(skip)
            .limit(parseInt(limit))
            .populate('user', 'name email')
            .sort({ createdAt: -1 }); // Newest messages first

        const totalMessages = await ChatMessage.countDocuments(filterCriteria);

        res.status(200).json({
            page: parseInt(page),
            limit: parseInt(limit),
            totalPages: Math.ceil(totalMessages / limit),
            totalMessages,
            messages,
        });
    } catch (err) {
        console.error('Error fetching messages:', err);
        next(new CustomError('Failed to fetch messages', 500));
    }
};

/**
 * Send a new chat message with real-time updates.
 * Ensure the message is saved and broadcasted to the connected clients in real-time.
 */
const sendMessage = async (req, res, next) => {
    try {
        const { chatRoomId, content } = req.body;

        if (!content || !chatRoomId) {
            return next(new CustomError('Content and chatRoomId are required', 400));
        }

        // Create and save the new message
        const newMessage = new ChatMessage({
            content,
            chatRoom: chatRoomId,
            user: req.user.id,
        });

        await newMessage.save();

        // Populate user details in the response
        const populatedMessage = await newMessage.populate('user', 'name email').execPopulate();

        // Emit the new message to the chat room
        const io = getIo();
        io.to(chatRoomId).emit('newMessage', populatedMessage);

        res.status(201).json(populatedMessage);
    } catch (err) {
        console.error('Error sending message:', err);
        next(new CustomError('Failed to send message', 500));
    }
};

/**
 * Delete a message by its ID.
 * Ensure only the message owner or an admin can delete the message.
 */
const deleteMessage = async (req, res, next) => {
    try {
        const messageId = req.params.messageId;

        // Fetch the message to verify ownership or admin rights
        const message = await ChatMessage.findById(messageId);

        if (!message) {
            return next(new CustomError('Message not found', 404));
        }

        // Ensure only the owner or an admin can delete the message
        if (message.user.toString() !== req.user.id && req.user.role !== 'admin') {
            return next(new CustomError('You do not have permission to delete this message', 403));
        }

        await message.remove();

        // Emit the message deletion event
        const io = getIo();
        io.to(message.chatRoom).emit('deleteMessage', messageId);

        res.status(204).send();
    } catch (err) {
        console.error('Error deleting message:', err);
        next(new CustomError('Failed to delete message', 500));
    }
};

module.exports = {
    getMessages,
    sendMessage,
    deleteMessage,
};
