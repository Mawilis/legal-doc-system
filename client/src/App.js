import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import styled, { ThemeProvider } from 'styled-components';
import GlobalStyle from './GlobalStyle';
import theme from './theme';
import PrivateRoute from './components/PrivateRoute';
import ErrorBoundary from './components/ErrorBoundary';
import { SnackbarProvider } from 'notistack';

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

const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  min-height: 100vh;
`;

const App = () => {
  return (
    <ThemeProvider theme={theme}>
      <GlobalStyle />
      <AppContainer>
        <SnackbarProvider maxSnack={3} anchorOrigin={{ vertical: 'top', horizontal: 'right' }}>
          <Router>
            <ErrorBoundary>
              <Suspense fallback={<div>Loading...</div>}>
                <Routes>
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
                <div>Hello, Legal Doc System!</div>
              </Suspense>
            </ErrorBoundary>
          </Router>
        </SnackbarProvider>
      </AppContainer>
    </ThemeProvider>
  );
};

export default App;
