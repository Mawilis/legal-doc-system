// ~/legal-doc-system/client/src/App.js
import React, { useEffect } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import Header from './components/organisms/Header';
import Dashboard from './pages/Dashboard';
import Documents from './pages/Documents';
import Login from './features/auth/pages/Login';
import Profile from './pages/Profile';
import ErrorPage from './pages/ErrorPage';
import useWebSocket from './hooks/useWebSocket';
import styled from 'styled-components';
import { logout as logoutAction } from './reducers/authSlice';

function App() {
  const isAuthenticated = useSelector((state) => state.auth.isAuthenticated);
  const dispatch = useDispatch();
  const socket = useWebSocket();

  // Handle logout using Redux action
  const handleLogout = () => {
    dispatch(logoutAction());
  };

  // WebSocket lifecycle management
  useEffect(() => {
    if (socket) {
      console.log('Socket initialized in App component.');

      socket.on('connect', () => {
        console.log('Socket connected');
      });

      socket.on('disconnect', () => {
        console.log('Socket disconnected');
      });

      return () => {
        socket.off('connect');
        socket.off('disconnect');
      };
    }
  }, [socket]);

  return (
    <>
      <Header onLogout={handleLogout} />
      <LogoutButton onClick={handleLogout}>Logout</LogoutButton>
      <MainContainer>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <ProtectedRoute isAuthenticated={isAuthenticated}>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/documents"
            element={
              <ProtectedRoute isAuthenticated={isAuthenticated}>
                <Documents />
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute isAuthenticated={isAuthenticated}>
                <Profile />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<ErrorPage />} />
        </Routes>
      </MainContainer>
    </>
  );
}

// ProtectedRoute Component to secure specific routes
const ProtectedRoute = ({ isAuthenticated, children }) => {
  const location = useLocation();
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  return children;
};

// Logout Button Styled Component
const LogoutButton = styled.button`
  display: block;
  margin: 20px auto;
  padding: 10px 20px;
  background-color: ${({ theme }) => theme.colors.primary};
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;

  &:hover {
    background-color: ${({ theme }) => theme.colors.secondary};
  }
`;

// Main Container Styled Component
const MainContainer = styled.main`
  padding: ${({ theme }) => theme.spacing.lg};
`;

export default App;
