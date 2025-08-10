// ~/legal-doc-system/client/src/components/ChatWindow.jsx

import React, { useState, useEffect, useCallback, useRef } from 'react';
import styled from 'styled-components';
import { useSelector } from 'react-redux';
import socket from '../services/socket'; // Shared socket singleton
import dayjs from 'dayjs';
import PropTypes from 'prop-types';
import Button from './atoms/Button'; // Import the masterpiece Button
import { FaPaperPlane } from 'react-icons/fa';

// --- Styled Components for a Professional Chat UI ---

const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  max-height: 70vh;
  width: 100%;
  background-color: ${({ theme }) => theme.colors.background || '#fff'};
  border: 1px solid ${({ theme }) => theme.colors.border || '#e0e0e0'};
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
`;

const ChatHeader = styled.header`
  padding: 1rem;
  background-color: ${({ theme }) => theme.colors.header || '#f8f9fa'};
  border-bottom: 1px solid ${({ theme }) => theme.colors.border || '#e0e0e0'};
  font-weight: 600;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const StatusIndicator = styled.span`
  font-size: 0.8rem;
  color: ${({ theme, $connected }) => ($connected ? theme.colors.success : theme.colors.danger) || ($connected ? '#28a745' : '#dc3545')};
  &::before {
    content: '●';
    margin-right: 0.5rem;
  }
`;

const MessagesList = styled.div`
  flex-grow: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
`;

const MessageItem = styled.div`
  display: flex;
  justify-content: ${({ $isCurrentUser }) => ($isCurrentUser ? 'flex-end' : 'flex-start')};
`;

const MessageBubble = styled.div`
  max-width: 70%;
  padding: 0.75rem 1rem;
  border-radius: 18px;
  color: ${({ $isCurrentUser, theme }) => ($isCurrentUser ? '#fff' : theme.colors.text || '#333')};
  background-color: ${({ $isCurrentUser, theme }) =>
        $isCurrentUser ? (theme.colors.primary || '#007bff') : (theme.colors.backgroundLight || '#e9ecef')};
`;

const MessageMeta = styled.div`
  font-size: 0.75rem;
  color: ${({ $isCurrentUser, theme }) =>
        $isCurrentUser ? 'rgba(255, 255, 255, 0.8)' : (theme.colors.textMuted || '#6c757d')};
  margin-bottom: 0.25rem;
  font-weight: 600;
`;

const InputArea = styled.div`
  display: flex;
  padding: 1rem;
  border-top: 1px solid ${({ theme }) => theme.colors.border || '#e0e0e0'};
  gap: 0.75rem;
`;

const MessageInput = styled.input`
  flex-grow: 1;
  padding: 0.75rem;
  border: 1px solid ${({ theme }) => theme.colors.border || '#ccc'};
  border-radius: 20px;
  font-size: 1rem;
  &:focus {
    outline: none;
    border-color: ${({ theme }) => theme.colors.primary || '#007bff'};
  }
  &:disabled {
    background-color: #f8f9fa;
  }
`;

const TypingIndicator = styled.div`
  padding: 0.5rem 1rem;
  font-style: italic;
  color: ${({ theme }) => theme.colors.textMuted || '#6c757d'};
  font-size: 0.85rem;
  height: 30px;
  transition: opacity 0.3s ease;
  opacity: ${({ $isVisible }) => ($isVisible ? 1 : 0)};
`;

/**
 * A real-time chat window component with typing indicators.
 * It connects to a shared socket, joins a specific room, and handles sending/receiving messages.
 *
 * @param {object} props
 * @param {string} props.roomId - The ID of the chat room to join.
 */
const ChatWindow = ({ roomId }) => {
    // --- State Management ---
    const [message, setMessage] = useState('');
    const [chatMessages, setChatMessages] = useState([]);
    const [isConnected, setConnected] = useState(socket.connected);
    const [typingUser, setTypingUser] = useState(null); // ✅ State for typing indicator
    const messagesEndRef = useRef(null);
    const typingTimeoutRef = useRef(null); // Ref to manage the typing timeout

    // --- Redux State ---
    const { user } = useSelector((state) => state.auth);

    // --- Real-time Logic ---
    useEffect(() => {
        if (!socket.connected) socket.connect();

        socket.emit('joinRoom', roomId);

        // --- Socket Event Listeners ---
        const handleConnect = () => setConnected(true);
        const handleDisconnect = () => setConnected(false);
        const handleNewMessage = (msg) => setChatMessages((prev) => [...prev, msg]);
        const handleTyping = (username) => setTypingUser(username); // ✅ Listen for typing
        const handleStopTyping = () => setTypingUser(null); // ✅ Listen for stop typing

        socket.on('connect', handleConnect);
        socket.on('disconnect', handleDisconnect);
        socket.on('newMessage', handleNewMessage);
        socket.on('typing', handleTyping);
        socket.on('stopTyping', handleStopTyping);

        // --- Cleanup on Unmount ---
        return () => {
            socket.emit('leaveRoom', roomId);
            socket.off('connect', handleConnect);
            socket.off('disconnect', handleDisconnect);
            socket.off('newMessage', handleNewMessage);
            socket.off('typing', handleTyping);
            socket.off('stopTyping', handleStopTyping);
        };
    }, [roomId]);

    // Auto-scroll to the latest message
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [chatMessages]);

    // --- Event Handlers ---
    const handleSendMessage = useCallback(() => {
        if (message.trim() && isConnected) {
            const messageData = {
                user: { id: user?.id, name: user?.name || 'Guest' },
                message,
                timestamp: new Date().toISOString(),
                roomId,
            };
            socket.emit('sendMessage', messageData);
            socket.emit('stopTyping', { roomId }); // ✅ Stop typing when message is sent
            setMessage('');
        }
    }, [message, roomId, user, isConnected]);

    // ✅ Effect for handling and debouncing typing indicators
    useEffect(() => {
        // Clear any existing timeout
        if (typingTimeoutRef.current) {
            clearTimeout(typingTimeoutRef.current);
        }

        // If there's a message, emit the 'typing' event
        if (message.trim() && isConnected) {
            socket.emit('typing', { roomId, user: user?.name });

            // Set a timeout to emit 'stopTyping' after a delay of inactivity
            typingTimeoutRef.current = setTimeout(() => {
                socket.emit('stopTyping', { roomId });
            }, 2000); // 2 seconds of inactivity
        } else {
            // If the input is cleared, immediately stop typing
            socket.emit('stopTyping', { roomId });
        }

        // Cleanup the timeout on unmount
        return () => clearTimeout(typingTimeoutRef.current);
    }, [message, roomId, user, isConnected]);


    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    return (
        <ChatContainer>
            <ChatHeader>
                Chat Room: {roomId}
                <StatusIndicator $connected={isConnected}>
                    {isConnected ? 'Connected' : 'Disconnected'}
                </StatusIndicator>
            </ChatHeader>

            <MessagesList>
                {chatMessages.map((msg, index) => {
                    const isCurrentUser = msg.user.id === user?.id;
                    return (
                        <MessageItem key={index} $isCurrentUser={isCurrentUser}>
                            <MessageBubble $isCurrentUser={isCurrentUser}>
                                <MessageMeta $isCurrentUser={isCurrentUser}>
                                    {isCurrentUser ? 'You' : msg.user.name} · {dayjs(msg.timestamp).format('HH:mm')}
                                </MessageMeta>
                                {msg.message}
                            </MessageBubble>
                        </MessageItem>
                    );
                })}
                <div ref={messagesEndRef} />
            </MessagesList>

            {/* ✅ Display the typing indicator */}
            <TypingIndicator $isVisible={!!typingUser && typingUser !== user?.name}>
                {typingUser && typingUser !== user?.name ? `${typingUser} is typing...` : ''}
            </TypingIndicator>

            <InputArea>
                <MessageInput
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyDown={handleKeyPress}
                    placeholder={isConnected ? "Type a message..." : "Connecting..."}
                    disabled={!isConnected}
                />
                <Button
                    onClick={handleSendMessage}
                    disabled={!message.trim() || !isConnected}
                    title="Send Message"
                >
                    <FaPaperPlane />
                </Button>
            </InputArea>
        </ChatContainer>
    );
};

// --- PropTypes for Code Quality ---
ChatWindow.propTypes = {
    roomId: PropTypes.string.isRequired,
};

export default ChatWindow;
