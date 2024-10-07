import React, { useState, useEffect } from 'react';
import { io } from 'socket.io-client';
import axios from 'axios';
import styled from 'styled-components';

// Styled Components for better UI
const ChatContainer = styled.div`
    padding: 20px;
    background-color: #f9f9f9;
    border-radius: 8px;
    max-width: 600px;
    margin: 20px auto;
`;

const MessagesContainer = styled.div`
    height: 400px;
    overflow-y: scroll;
    background-color: #fff;
    padding: 15px;
    border: 1px solid #ddd;
    border-radius: 8px;
    margin-bottom: 10px;
`;

const MessageItem = styled.div`
    margin-bottom: 10px;
    padding: 8px;
    background-color: ${(props) => (props.isUser ? '#d1e7dd' : '#f8d7da')};
    border-radius: 5px;
    align-self: ${(props) => (props.isUser ? 'flex-end' : 'flex-start')};
    max-width: 70%;
    word-wrap: break-word;
`;

const InputContainer = styled.form`
    display: flex;
    gap: 10px;
`;

const InputField = styled.input`
    flex: 1;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 5px;
`;

const SendButton = styled.button`
    padding: 10px 20px;
    background-color: #28a745;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;

    &:hover {
        background-color: #218838;
    }
`;

const ChatTitle = styled.h2`
    text-align: center;
    margin-bottom: 20px;
`;

const ErrorMsg = styled.p`
    color: red;
`;

const Chat = () => {
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [error, setError] = useState('');
    const socket = io('http://localhost:3001'); // Make sure this matches your backend

    // Fetch chat messages on component mount
    useEffect(() => {
        const fetchMessages = async () => {
            try {
                const response = await axios.get('/api/chat');
                setMessages(response.data);
            } catch (err) {
                console.error('Error fetching messages:', err);
                setError('Failed to load messages');
            }
        };

        fetchMessages();

        // Listen for new messages from Socket.io
        socket.on('chat-message', (message) => {
            setMessages((prevMessages) => [...prevMessages, message]);
        });

        // Handle socket connection errors
        socket.on('connect_error', (err) => {
            console.error('Socket connection error:', err);
            setError('Real-time connection error');
        });

        // Cleanup on unmount
        return () => {
            socket.disconnect();
        };
    }, [socket]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!inputMessage.trim()) {
            return;
        }

        const newMessage = { user: 'Admin', message: inputMessage };

        // Emit the new message to Socket.io
        socket.emit('chat-message', newMessage);

        // Save the new message to the server
        try {
            await axios.post('/api/chat', newMessage);
            setInputMessage(''); // Clear input field after sending
        } catch (error) {
            console.error('Error sending message:', error);
            setError('Failed to send message');
        }
    };

    return (
        <ChatContainer>
            <ChatTitle>Chat Room</ChatTitle>
            {error && <ErrorMsg>{error}</ErrorMsg>}

            <MessagesContainer>
                {messages.map((msg, index) => (
                    <MessageItem
                        key={index}
                        isUser={msg.user === 'Admin'} // Assuming the current user is 'Admin'
                    >
                        <strong>{msg.user}: </strong>
                        {msg.message}
                    </MessageItem>
                ))}
            </MessagesContainer>

            <InputContainer onSubmit={handleSubmit}>
                <InputField
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    placeholder="Type a message..."
                />
                <SendButton type="submit">Send</SendButton>
            </InputContainer>
        </ChatContainer>
    );
};

export default Chat;
