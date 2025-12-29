import React, { useEffect } from 'react';
import styled from 'styled-components';
import { useSelector, useDispatch } from 'react-redux';
// import { removeNotification } from '../features/ui/uiSlice'; // Uncomment when slice exists

// --- STABLE REFERENCE (The Fix) ---
// This prevents the infinite re-render loop by ensuring 'empty' is always the same object in memory.
const EMPTY_NOTIFICATIONS = [];

const NotificationContainer = styled.div`
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 10px;
`;

const NotificationCard = styled.div`
  background: #fff;
  border-left: 5px solid ${props => props.type === 'error' ? '#d32f2f' : props.type === 'success' ? '#2e7d32' : '#0288d1'};
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  padding: 16px 20px;
  border-radius: 4px;
  min-width: 300px;
  max-width: 450px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  animation: slideIn 0.3s ease-out;

  @keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }
`;

const Message = styled.p`
  margin: 0;
  font-family: 'Segoe UI', sans-serif;
  font-size: 0.95rem;
  color: #333;
  line-height: 1.4;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  color: #999;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0 0 0 10px;
  line-height: 1;
  &:hover { color: #333; }
`;

const Notifications = () => {
  const dispatch = useDispatch();

  // ✅ MEMOIZED SELECTOR FIX
  // If state.ui or state.ui.notifications doesn't exist, return the STABLE empty array.
  const notifications = useSelector((state) => state.ui?.notifications || EMPTY_NOTIFICATIONS);

  if (!notifications || notifications.length === 0) return null;

  return (
    <NotificationContainer>
      {notifications.map((note) => (
        <NotificationCard key={note.id} type={note.type || 'info'}>
          <Message>{note.message}</Message>
          <CloseButton onClick={() => console.log('Close', note.id)}>×</CloseButton>
        </NotificationCard>
      ))}
    </NotificationContainer>
  );
};

export default Notifications;
