import React, { useState, useEffect } from 'react';

const ChatWindow = ({ socket, user }) => {
    const [message, setMessage] = useState('');
    const [chatMessages, setChatMessages] = useState([]);

    useEffect(() => {
        if (socket) {
            socket.on('chatMessage', (message) => {
                setChatMessages((prevMessages) => [...prevMessages, message]);
            });
        }
    }, [socket]);

    const sendMessage = () => {
        socket.emit('sendMessage', { user, message });
        setMessage('');
    };

    return (
        <div className="chat-window">
            <div className="messages">
                {chatMessages.map((msg, index) => (
                    <div key={index}>
                        <strong>{msg.user}:</strong> {msg.message}
                    </div>
                ))}
            </div>
            <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Type a message..."
            />
            <button onClick={sendMessage}>Send</button>
        </div>
    );
};

export default ChatWindow;
