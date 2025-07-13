// server/models/chatModel.js

const mongoose = require('mongoose');

const chatSchema = new mongoose.Schema(
    {
        // A name for the chat. This is optional and typically used for group chats.
        chatName: {
            type: String,
            trim: true,
        },
        // A boolean to distinguish between one-on-one chats and group chats.
        isGroupChat: {
            type: Boolean,
            default: false,
        },
        // An array of users who are part of this chat.
        // This is a critical field that links to the User model.
        users: [
            {
                type: mongoose.Schema.Types.ObjectId,
                ref: 'User',
            },
        ],
        // A reference to the latest message sent in this chat.
        // This is a performance optimization. It allows us to easily display
        // a preview of the last message in a list of chats without having to
        // query the entire message collection.
        latestMessage: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'ChatMessage', // References the ChatMessage model
        },
        // Only applicable for group chats, this field indicates who the admin of the group is.
        groupAdmin: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'User',
        },
    },
    {
        // Automatically adds `createdAt` and `updatedAt` fields.
        // `updatedAt` will be particularly useful for sorting chats by recent activity.
        timestamps: true,
    }
);

const Chat = mongoose.model('Chat', chatSchema);

module.exports = Chat;
