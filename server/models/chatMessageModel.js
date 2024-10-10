// models/chatMessageModel.js

const mongoose = require('mongoose');
const Schema = mongoose.Schema;

// Define the ChatMessage schema
const chatMessageSchema = new Schema(
    {
        content: {
            type: String,
            required: [true, 'Message content is required'],
        },
        user: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'User', // Reference the User model
            required: [true, 'User is required'],
        },
        chatRoom: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'ChatRoom', // Reference a ChatRoom model if applicable
            required: [true, 'Chat room is required'],
        },
        createdAt: {
            type: Date,
            default: Date.now,
        },
    },
    {
        timestamps: true, // Automatically adds createdAt and updatedAt timestamps
    }
);

// Export the ChatMessage model
module.exports = mongoose.model('ChatMessage', chatMessageSchema);
