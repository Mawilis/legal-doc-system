// server/controllers/chatController.js

const Chat = require('../models/chatModel');
const User = require('../models/userModel');
const ChatMessage = require('../models/chatMessageModel');
const CustomError = require('../utils/customError');
const logger = require('../utils/logger');

/**
 * @desc    Access a chat or create a new one if it doesn't exist
 * @route   POST /api/chat
 * @access  Private
 */
exports.accessChat = async (req, res, next) => {
    // The ID of the user we want to chat with
    const { userId } = req.body;

    if (!userId) {
        return next(new CustomError('UserId parameter not sent with request', 400));
    }

    // Find if a one-on-one chat already exists between the current user and the target user.
    let isChat = await Chat.findOne({
        isGroupChat: false,
        $and: [
            { users: { $elemMatch: { $eq: req.user._id } } },
            { users: { $elemMatch: { $eq: userId } } },
        ],
    })
        .populate('users', '-password') // Populate user details
        .populate('latestMessage');     // Populate the latest message preview

    // If a chat exists, populate the sender details of the latest message
    if (isChat) {
        isChat = await User.populate(isChat, {
            path: 'latestMessage.sender',
            select: 'name email',
        });
        res.status(200).json({ success: true, data: isChat });
    } else {
        // If no chat exists, create a new one.
        const chatData = {
            chatName: 'sender', // A default name, can be changed
            isGroupChat: false,
            users: [req.user._id, userId], // The two participants
        };

        try {
            const createdChat = await Chat.create(chatData);
            const fullChat = await Chat.findOne({ _id: createdChat._id }).populate(
                'users',
                '-password'
            );
            res.status(201).json({ success: true, data: fullChat });
        } catch (error) {
            next(error);
        }
    }
};

/**
 * @desc    Fetch all chats for the logged-in user
 * @route   GET /api/chat
 * @access  Private
 */
exports.fetchChats = async (req, res, next) => {
    try {
        let chats = await Chat.find({ users: { $elemMatch: { $eq: req.user._id } } })
            .populate('users', '-password')
            .populate('groupAdmin', '-password')
            .populate('latestMessage')
            .sort({ updatedAt: -1 }); // Sort by most recently updated

        // Populate the sender details for the latest message in each chat
        chats = await User.populate(chats, {
            path: 'latestMessage.sender',
            select: 'name email',
        });

        res.status(200).json({ success: true, data: chats });
    } catch (error) {
        next(error);
    }
};

/**
 * @desc    Send a new message
 * @route   POST /api/chat/message
 * @access  Private
 */
exports.sendMessage = async (req, res, next) => {
    const { content, chatId } = req.body;

    if (!content || !chatId) {
        return next(new CustomError('Invalid data passed into request', 400));
    }

    const newMessage = {
        sender: req.user._id,
        content: content,
        chat: chatId,
    };

    try {
        let message = await ChatMessage.create(newMessage);

        // Populate the sender and chat details for the new message
        message = await message.populate('sender', 'name');
        message = await message.populate('chat');
        message = await User.populate(message, {
            path: 'chat.users',
            select: 'name email',
        });

        // --- Critical Step ---
        // Update the 'latestMessage' field of the parent chat.
        await Chat.findByIdAndUpdate(req.body.chatId, {
            latestMessage: message,
        });

        res.status(201).json({ success: true, data: message });
    } catch (error) {
        next(error);
    }
};

/**
 * @desc    Fetch all messages for a specific chat
 * @route   GET /api/chat/:chatId
 * @access  Private
 */
exports.fetchMessages = async (req, res, next) => {
    try {
        const messages = await ChatMessage.find({ chat: req.params.chatId })
            .populate('sender', 'name email')
            .populate('chat');

        res.status(200).json({ success: true, data: messages });
    } catch (error) {
        next(error);
    }
};
