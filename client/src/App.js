import AuditPage from './features/documents/pages/AuditPage';
import React, { Suspense, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { connectSocket, disconnectSocket } from './services/socket';
import { forceLogout } from './features/auth/reducers/authSlice';
import './App.css';

// Components
import ProtectedRoute from './components/ProtectedRoute';
import AppLayout from './components/layout/AppLayout';
import Login from './features/auth/pages/Login';
import Dashboard from './features/dashboard/pages/Dashboard';
import Documents from './features/documents/pages/Documents';
import NewCase from './pages/NewCase';
import DocumentDetails from './features/documents/pages/DocumentDetails';
import Profile from './features/profile/pages/Profile';
import AdminPanel from './features/admin/pages/AdminPanel';
import AdminDashboard from './components/AdminDashboard';
import SheriffDashboard from './features/admin/pages/SheriffDashboard';
import SheriffAnalytics from './features/sheriff/pages/SheriffAnalytics';
import Search from './features/search/pages/Search';
import SettingsHome from './features/settings/pages/SettingsHome';
import Chat from './features/chat/pages/Chat';

// --- SHERIFF MODULES ---
import SheriffInstructionForm from './features/documents/pages/SheriffInstructionForm';
import SheriffTracking from './features/documents/pages/SheriffTracking';

// Utilities
import ErrorBoundary from './components/ErrorBoundary';
import LoadingSpinner from './components/LoadingSpinner';
import Notifications from './components/Notifications';

function Loading() {
  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', flexDirection: 'column', gap: '15px', color: '#666' }}>
      <LoadingSpinner />
      <div style={{ fontWeight: 500 }}>Initializing Secure Environment...</div>
    </div>
  );
}

export default function App() {
  const dispatch = useDispatch();
  const { isAuthenticated, accessToken } = useSelector((state) => state.auth);

  useEffect(() => {
    if (isAuthenticated && accessToken) {
      connectSocket(accessToken);
    } else {
      disconnectSocket();
    }
    return () => disconnectSocket();
  }, [isAuthenticated, accessToken]);

  return (
    <ErrorBoundary>
      <Notifications />
      <Suspense fallback={<Loading />}>
        <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <Routes>
            <Route path="/login" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Login />} />
            
            <Route path="/" element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<Dashboard />} />
              
              {/* Documents */}
              <Route path="documents" element={<Documents />} />
              <Route path="documents/new" element={<NewCase />} />
              <Route path="documents/:id" element={<DocumentDetails />} />
              
              {/* --- SHERIFF ROUTES (Fixed 404s) --- */}
              {/* The sidebar points to /sheriff/new-instruction and /sheriff/tracking */}
              <Route path="sheriff/new-instruction" element={<SheriffInstructionForm />} />
              <Route path="sheriff/tracking" element={<SheriffTracking />} />
              <Route path="sheriff/dashboard" element={<SheriffDashboard />} />
              <Route path="sheriff/analytics" element={<SheriffAnalytics />} />
              <Route path="sheriff/audit" element={<AuditPage />} />

              {/* Admin & Utils */}
              <Route path="admin" element={<Navigate to="/admin/dashboard" replace />} />
              <Route path="admin/dashboard" element={<AdminDashboard />} />
              <Route path="admin/panel" element={<AdminPanel />} />
              <Route path="profile" element={<Profile />} />
              <Route path="settings" element={<SettingsHome />} />
              <Route path="chat" element={<Chat />} />
              <Route path="search" element={<Search />} />
              
              {/* Catch All */}
              <Route path="*" element={<div style={{ padding: '50px', textAlign: 'center' }}><h2>404 - Page Not Found</h2><p>The route you requested does not exist.</p></div>} />
            </Route>
          </Routes>
        </BrowserRouter>
      </Suspense>
    </ErrorBoundary>
  );
}
