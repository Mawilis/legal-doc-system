// ~/legal-doc-system/client/src/App.js

import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import Documents from './pages/Documents';
import Login from './pages/Login';
import Profile from './pages/Profile';
import ErrorPage from './pages/ErrorPage';
import useWebSocket from './hooks/useWebSocket';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const socket = useWebSocket();

  // Define handleLogout to reset authentication status
  const handleLogout = () => {
    setIsAuthenticated(false);
    localStorage.removeItem('token'); // Clear user token or session data
  };

  useEffect(() => {
    if (socket) {
      console.log('Socket initialized in App component.');

      // Example: handle some global events with the socket if needed
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
    <Router>
      <div>
        <Header onLogout={handleLogout} />
        <button onClick={handleLogout}>Logout</button>
        <main>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={isAuthenticated ? <Dashboard /> : <Navigate to="/login" replace />} />
            <Route path="/documents" element={isAuthenticated ? <Documents /> : <Navigate to="/login" replace />} />
            <Route path="/profile" element={isAuthenticated ? <Profile /> : <Navigate to="/login" replace />} />
            <Route path="*" element={<ErrorPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
