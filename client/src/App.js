// /src/App.js
import React, { Suspense, lazy, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import CssBaseline from '@mui/material/CssBaseline';
import GlobalStyle from './GlobalStyle';
import PrivateRoute from './components/PrivateRoute';
import ErrorBoundary from './components/ErrorBoundary';
import axios from 'axios';
import PropTypes from 'prop-types';
import DebugCircularProgress from './components/DebugCircularProgress'; // Debug version of CircularProgress

// Define API Base URL
const API_URL = process.env.REACT_APP_API_BASE_URL || 'https://localhost:3001/api';

// Lazy load pages
const Dashboard = lazy(() => import('./features/dashboard/pages/Dashboard'));
const Documents = lazy(() => import('./features/documents/pages/Documents'));
const Profile = lazy(() => import('./features/profile/pages/Profile'));
const AdminPanel = lazy(() => import('./features/admin/pages/AdminPanel'));
const Chat = lazy(() => import('./features/chat/pages/Chat'));
const Instructions = lazy(() => import('./features/instructions/pages/Instructions'));
const DocumentDetails = lazy(() => import('./features/documents/pages/DocumentDetails'));
const DocumentForm = lazy(() => import('./features/documents/pages/DocumentForm'));
const UserManagement = lazy(() => import('./features/admin/pages/UserManagement'));
const ErrorPage = lazy(() => import('./features/shared/pages/ErrorPage'));
const Login = lazy(() => import('./features/auth/pages/Login'));

// Fallback Loading Component using DebugCircularProgress
const Loading = () => (
  <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
    <DebugCircularProgress color="primary" />
    <p style={{ marginTop: '16px', fontSize: '1.2rem' }}>Loading...</p>
  </div>
);

const App = () => {
  useEffect(() => {
    const source = axios.CancelToken.source();
    const testServerConnection = async () => {
      try {
        const response = await axios.get(`${API_URL}/test`, {
          withCredentials: true,
          cancelToken: source.token,
        });
        console.log('[App] Test response:', response.data);
      } catch (error) {
        if (axios.isCancel(error)) {
          console.log('[App] Server connection test cancelled:', error.message);
        } else {
          console.error('[App] Error testing server connection:', error.message);
        }
      }
    };
    testServerConnection();
    return () => source.cancel('Component unmounted, cancelling server test.');
  }, []);

  return (
    <>
      <CssBaseline />
      <GlobalStyle />
      <ErrorBoundary>
        <Suspense fallback={<Loading />}>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/login" element={<Login />} />
            <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
            <Route path="/documents" element={<PrivateRoute><Documents /></PrivateRoute>} />
            <Route path="/documents/new" element={<PrivateRoute><DocumentForm /></PrivateRoute>} />
            <Route path="/documents/:id" element={<PrivateRoute><DocumentDetails /></PrivateRoute>} />
            <Route path="/profile" element={<PrivateRoute><Profile /></PrivateRoute>} />
            <Route path="/admin" element={<PrivateRoute><AdminPanel /></PrivateRoute>} />
            <Route path="/admin/users" element={<PrivateRoute><UserManagement /></PrivateRoute>} />
            <Route path="/chat" element={<PrivateRoute><Chat /></PrivateRoute>} />
            <Route path="/instructions" element={<PrivateRoute><Instructions /></PrivateRoute>} />
            <Route path="/error" element={<ErrorPage />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Suspense>
      </ErrorBoundary>
    </>
  );
};

PrivateRoute.propTypes = {
  children: PropTypes.node.isRequired,
};

export default App;
