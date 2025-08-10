// ~/client/src/App.js

import React, { Suspense, lazy, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import GlobalStyle from './GlobalStyle';
import ProtectedRoute from './components/ProtectedRoute'; // Use the masterpiece security component
import ErrorBoundary from './components/ErrorBoundary';
import { loadUser } from './features/auth/reducers/authSlice';
import AppLayout from './components/layout/AppLayout';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import 'leaflet/dist/leaflet.css'; // Global Leaflet CSS for map components
import LoadingSpinner from './components/LoadingSpinner';

// --- Lazy-loaded Pages ---
// This pattern improves initial load time by only fetching the code for the page being viewed.
const Dashboard = lazy(() => import('./features/dashboard/pages/Dashboard'));
const Documents = lazy(() => import('./features/documents/pages/Documents'));
const Profile = lazy(() => import('./features/profile/pages/Profile'));
const AdminPanel = lazy(() => import('./features/admin/pages/AdminPanel'));
const UserManagement = lazy(() => import('./features/admin/pages/UserManagement'));
const SheriffDashboard = lazy(() => import('./features/admin/pages/SheriffDashboard'));
const SheriffAnalytics = lazy(() => import('./features/sheriff/pages/SheriffAnalytics'));
const GeofenceManager = lazy(() => import('./features/admin/pages/GeofenceManager'));
const Chat = lazy(() => import('./features/chat/pages/Chat'));
const Login = lazy(() => import('./features/auth/pages/Login'));
const ErrorPage = lazy(() => import('./features/shared/pages/ErrorPage'));

// --- Fallback Loading Screen ---
const Loading = () => (
  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
    <LoadingSpinner message="Loading..." />
  </div>
);

/**
 * The main application router.
 * This is where you define which routes are public and which are protected.
 */
const App = () => {
  const dispatch = useDispatch();

  useEffect(() => {
    // Attempt to load the user from the token on initial app load
    dispatch(loadUser());
  }, [dispatch]);

  return (
    <>
      <GlobalStyle />
      <ErrorBoundary>
        <Suspense fallback={<Loading />}>
          <BrowserRouter>
            <Routes>
              {/* --- Public Route --- */}
              <Route path="/login" element={<Login />} />

              {/* --- Protected Routes (Layout Wrapper) --- */}
              {/* This outer route ensures a user must be authenticated to see the main app layout. */}
              <Route path="/" element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
                {/* Nested routes will render inside AppLayout's <Outlet> */}
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard" element={<Dashboard />} />
                <Route path="documents" element={<Documents />} />
                <Route path="profile" element={<Profile />} />
                <Route path="chat" element={<Chat />} />

                {/* --- Admin-Only Routes --- */}
                <Route
                  path="admin"
                  element={<ProtectedRoute roles={['admin']}><AdminPanel /></ProtectedRoute>}
                />
                <Route
                  path="admin/users"
                  element={<ProtectedRoute roles={['admin']}><UserManagement /></ProtectedRoute>}
                />
                <Route
                  path="admin/sheriff-tracking"
                  element={<ProtectedRoute roles={['admin']}><SheriffDashboard /></ProtectedRoute>}
                />
                <Route
                  path="admin/analytics"
                  element={<ProtectedRoute roles={['admin']}><SheriffAnalytics /></ProtectedRoute>}
                />
                <Route
                  path="admin/geofences"
                  element={<ProtectedRoute roles={['admin']}><GeofenceManager /></ProtectedRoute>}
                />

                {/* --- Sheriff-Only Route --- */}
                <Route
                  path="sheriff/dashboard"
                  element={<ProtectedRoute roles={['sheriff']}><SheriffDashboard /></ProtectedRoute>}
                />

                {/* --- Error Page --- */}
                <Route path="*" element={<ErrorPage />} />
              </Route>
            </Routes>
          </BrowserRouter>
        </Suspense>
      </ErrorBoundary>

      {/* Global Toasts Container */}
      <ToastContainer
        position="top-right"
        autoClose={4000}
        hideProgressBar={false}
        newestOnTop
        closeOnClick
        pauseOnFocusLoss
        draggable
        pauseOnHover
      />
    </>
  );
};

export default App;
