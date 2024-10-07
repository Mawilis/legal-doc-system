const Chat = require('../models/chatModel');

exports.sendMessage = async (req, res) => {
    try {
        const { message, user } = req.body;
        const chatMessage = new Chat({ user, message, createdAt: new Date() });
        await chatMessage.save();

        req.io.emit('chat-message', { user, message });  // Real-time updates
        res.status(200).json({ message: 'Message sent!' });
    } catch (err) {
        res.status(500).json({ message: 'Server error' });
    }
};

exports.getMessages = async (req, res) => {
    try {
        const messages = await Chat.find().sort({ createdAt: -1 }).limit(50);  // Get last 50 messages
        res.status(200).json(messages);
    } catch (err) {
        res.status(500).json({ message: 'Server error' });
    }
};
