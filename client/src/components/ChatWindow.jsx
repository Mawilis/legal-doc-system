import React, { useState, useEffect, useCallback, useRef } from 'react';
import styled from 'styled-components';

const ChatWindow = ({ socket, user, roomId }) => { // Added roomId prop
    const [message, setMessage] = useState('');
    const [chatMessages, setChatMessages] = useState([]);
    const messagesEndRef = useRef(null); // Ref for scrolling to bottom

    // useCallback for sending messages
    const sendMessage = useCallback(() => {
        if (message.trim() !== '') { // Prevent sending empty messages
            socket.emit('sendMessage', { user, message, roomId }); // Include roomId
            setMessage('');
        }
    }, [message, socket, user, roomId]);

    useEffect(() => {
        if (socket) {
            socket.on('newMessage', (message) => { // Use 'newMessage' event
                setChatMessages(prevMessages => [...prevMessages, message]);
            });

            // Cleanup function to remove the event listener when the component unmounts
            return () => socket.off('newMessage');
        }
    }, [socket, roomId]); // Include roomId in the dependency array

    // useEffect for scrolling to the bottom when new messages arrive
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [chatMessages]);

    return (
        <ChatContainer>
            <MessagesList>
                {chatMessages.map((msg, index) => (
                    <MessageItem key={index} isCurrentUser={msg.user === user}>
                        <MessageText>
                            {msg.user === user ? '' : <strong>{msg.user}: </strong>} {/* Only show username if not current user */}
                            {msg.message}
                        </MessageText>
                    </MessageItem>
                ))}
                <div ref={messagesEndRef} /> {/* Empty div for scrolling */}
            </MessagesList>
            <InputArea>
                <MessageInput
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Type a message..."
                />
                <SendButton onClick={sendMessage} disabled={message.trim() === ''}>
                    Send
                </SendButton>
            </InputArea>
        </ChatContainer>
    );
};

// Styled Components
const ChatContainer = styled.div`
    display: flex;
    flex-direction: column;
    height: 100%; 
`;

const MessagesList = styled.ul`
    list-style: none;
    padding: 10px;
    overflow-y: auto; 
    flex-grow: 1; 
`;

const MessageItem = styled.li`
    margin-bottom: 10px;
    text-align: ${props => props.isCurrentUser ? 'right' : 'left'}; 
`;

const MessageText = styled.div`
    display: inline-block;
    padding: 8px 12px;
    border-radius: 5px;
    background-color: ${props => props.isCurrentUser ? '#007bff' : '#eee'}; 
    color: ${props => props.isCurrentUser ? '#fff' : '#333'}; 
    max-width: 70%; 
`;

const InputArea = styled.div`
    display: flex;
    padding: 10px;
    border-top: 1px solid #eee; 
`;

const MessageInput = styled.input`
    flex-grow: 1; 
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 5px;
    margin-right: 10px; 
`;

const SendButton = styled.button`
    background-color: #007bff;
    color: #fff;
    border: none;
    padding: 10px 15px; 
    cursor: pointer;
    border-radius: 5px;
    transition: background-color 0.2s ease;

    &:hover {
        background-color: #0062cc;
    }

    &:disabled { 
        background-color: #a0a0a0;
        cursor: not-allowed;
    }
`;

export default ChatWindow;