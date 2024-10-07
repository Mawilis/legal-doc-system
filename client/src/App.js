// App.js
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import PropTypes from 'prop-types';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import Documents from './pages/Documents';
import Instructions from './pages/Instructions';
import Profile from './pages/Profile';
import Login from './pages/Login';
import AdminPanel from './pages/AdminPanel';
import UserManagement from './pages/UserManagement';
import ErrorPage from './pages/ErrorPage';
import { getCurrentUserRole, isAuthenticated } from './services/authService';
import { useWebSocket } from './hooks/useWebSocket';  // Import the custom WebSocket hook
import './App.css';

function App() {
  const [authStatus, setAuthStatus] = useState(isAuthenticated());
  const [userRole, setUserRole] = useState(getCurrentUserRole());
  const navigate = useNavigate();

  // Use the custom WebSocket hook
  const socket = useWebSocket();

  useEffect(() => {
    console.log('App mounted');

    const handleAuthChange = () => {
      const isAuth = isAuthenticated();
      const role = getCurrentUserRole();
      console.log('Auth status:', isAuth, 'User role:', role);
      setAuthStatus(isAuth);
      setUserRole(role);
    };

    handleAuthChange();

    const tokenExpiredHandler = () => {
      toast.error('Session expired. Please login again.');
      handleAuthChange();
      navigate('/login');
    };

    if (socket) {
      socket.on('tokenExpired', tokenExpiredHandler);

      // WebSocket error handler
      socket.on('connect_error', (err) => {
        console.error('WebSocket connection error:', err);
        toast.error('Real-time connection failed. Please check your network.');
      });
    }

    return () => {
      if (socket) {
        socket.off('tokenExpired', tokenExpiredHandler);
        socket.off('connect_error');  // Clean up the listener
      }
    };
  }, [navigate, socket]); // Add socket to dependency array

  // Protected Route definition
  const ProtectedRoute = ({ role, children }) => {
    if (!authStatus) {
      console.log('User is not authenticated, redirecting to login');
      return <Navigate to="/login" replace />;
    }
    if (role && role !== userRole) {
      console.log('User role does not match, redirecting to home');
      return <Navigate to="/" replace />;
    }
    return children;
  };

  // Add PropTypes for the ProtectedRoute component
  ProtectedRoute.propTypes = {
    role: PropTypes.string,  // Role is an optional string
    children: PropTypes.node.isRequired,  // Children must be passed
  };

  return (
    <Router>
      <div>
        <Header isAuthenticated={authStatus} userRole={userRole} onLogout={() => setAuthStatus(false)} />
        <ToastContainer />
        <main>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/documents" element={<ProtectedRoute role="attorney"><Documents /></ProtectedRoute>} />
            <Route path="/instructions" element={<ProtectedRoute role="sheriff"><Instructions /></ProtectedRoute>} />
            <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
            <Route path="/admin" element={<ProtectedRoute role="admin"><AdminPanel /></ProtectedRoute>} />
            <Route path="/user-management" element={<ProtectedRoute role="admin"><UserManagement /></ProtectedRoute>} />
            <Route path="*" element={<ErrorPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
