// ~/legal-doc-system/client/src/features/chat/pages/Chat.jsx

import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { useDispatch, useSelector } from 'react-redux';
import { fetchChatMessages, sendMessage } from '../reducers/chatSlice';
import { FaPaperPlane } from 'react-icons/fa';

const ChatContainer = styled.div`
  padding: var(--spacing-lg);
  background-color: var(--background-color);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
`;

const ChatHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
`;

const ChatTitle = styled.h1`
  font-size: 2.5rem;
  color: var(--primary-color);

  @media (max-width: var(--breakpoint-tablet)) {
    font-size: 2rem;
  }

  @media (max-width: var(--breakpoint-mobile)) {
    font-size: 1.75rem;
  }
`;

const ChatMessages = styled.div`
  flex: 1;
  overflow-y: auto;
  margin-bottom: var(--spacing-md);
`;

const Message = styled.div`
  padding: var(--spacing-sm);
  margin-bottom: var(--spacing-xs);
  background-color: ${({ isOwn }) => (isOwn ? 'var(--accent-color)' : 'var(--light-color)')};
  border-radius: var(--border-radius);
  max-width: 70%;
  align-self: ${({ isOwn }) => (isOwn ? 'flex-end' : 'flex-start')};
`;

const MessageText = styled.p`
  font-size: 1rem;
  color: var(--text-color);
`;

const MessageInputContainer = styled.form`
  display: flex;
  align-items: center;
`;

const MessageInput = styled.input`
  flex: 1;
  padding: var(--spacing-sm);
  border: 1px solid var(--accent-color);
  border-radius: var(--border-radius);
  margin-right: var(--spacing-sm);
  transition: border-color var(--transition);

  &:focus {
    border-color: var(--primary-color);
    outline: none;
    box-shadow: 0 0 0 2px rgba(0, 112, 243, 0.2);
  }
`;

const SendButton = styled.button`
  background-color: var(--primary-color);
  color: #ffffff;
  border: none;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius);
  display: flex;
  align-items: center;
  transition: background-color var(--transition), transform 0.2s;

  &:hover {
    background-color: var(--secondary-color);
    transform: translateY(-2px);
    box-shadow: var(--shadow);
  }

  &:active {
    transform: translateY(0);
    box-shadow: none;
  }

  &:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }
`;

const Chat = () => {
  const dispatch = useDispatch();
  const { messages, loading, error } = useSelector((state) => state.chat);
  const [message, setMessage] = useState('');

  useEffect(() => {
    dispatch(fetchChatMessages());
  }, [dispatch]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim()) {
      dispatch(sendMessage({ content: message }));
      setMessage('');
    }
  };

  return (
    <ChatContainer>
      <ChatHeader>
        <ChatTitle>Chat</ChatTitle>
      </ChatHeader>
      <ChatMessages>
        {loading && <p>Loading messages...</p>}
        {error && <p style={{ color: 'var(--error-color)' }}>{error}</p>}
        {messages && messages.map((msg) => (
          <Message key={msg.id} isOwn={msg.isOwn}>
            <MessageText>{msg.content}</MessageText>
          </Message>
        ))}
      </ChatMessages>
      <MessageInputContainer onSubmit={handleSubmit}>
        <MessageInput
          type="text"
          placeholder="Type your message..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          required
        />
        <SendButton type="submit" disabled={!message.trim()}>
          <FaPaperPlane />
        </SendButton>
      </MessageInputContainer>
    </ChatContainer>
  );
};

export default Chat;
