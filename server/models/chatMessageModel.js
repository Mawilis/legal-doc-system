// server/models/chatMessageModel.js

const mongoose = require('mongoose');

const chatMessageSchema = new mongoose.Schema(
    {
        // The user who sent the message. This is a mandatory link to the User model.
        sender: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'User',
            required: true,
        },
        // The actual content of the message.
        content: {
            type: String,
            trim: true,
            required: [true, 'Message content cannot be empty.'],
        },
        // A reference to the parent chat conversation this message belongs to.
        chat: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'Chat',
            required: true,
        },
        // An array to keep track of which users have seen the message.
        // This is useful for implementing "read receipts".
        readBy: [
            {
                type: mongoose.Schema.Types.ObjectId,
                ref: 'User',
            },
        ],
    },
    {
        // Automatically adds `createdAt` and `updatedAt` timestamps.
        // `createdAt` is essential for ordering messages chronologically.
        timestamps: true,
    }
);

const ChatMessage = mongoose.model('ChatMessage', chatMessageSchema);

module.exports = ChatMessage;
