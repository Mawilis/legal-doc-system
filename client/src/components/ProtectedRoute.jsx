// ~/client/src/components/ProtectedRoute.jsx

import React, { useEffect, useMemo } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';
import styled from 'styled-components';
import PropTypes from 'prop-types';
import socket from '../services/socket'; // Import the shared socket instance from your Canvas
import LoadingSpinner from './LoadingSpinner';

/**
 * A robust, production-ready component to protect routes based on authentication,
 * user roles, and fine-grained permissions. It also includes real-time security auditing.
 *
 * @param {object} props
 * @param {React.ReactNode} props.children - The component to render if access is granted.
 * @param {string[]} [props.roles=[]] - An array of user roles that are allowed access.
 * @param {string} [props.permission] - A specific permission string required for access (e.g., "users:read").
 */
const ProtectedRoute = ({ children, roles = [], permission }) => {
    // --- Hooks ---
    const location = useLocation();
    const { isAuthenticated, user, loading } = useSelector((state) => state.auth);

    // --- Connect Socket on Authentication ---
    useEffect(() => {
        // Connect the shared socket instance when the user is authenticated.
        if (isAuthenticated) {
            socket.connect();
        }
        // The socketMiddleware in your store.js can handle disconnecting on logout.
    }, [isAuthenticated]);

    // --- Permission & Role Checks ---
    const hasRequiredRole = roles.length === 0 || (user && roles.includes(user.role));

    const hasRequiredPermission = useMemo(() => {
        if (!permission) return true; // No specific permission required
        if (!user?.permissions) return false; // User has no permissions object

        const [module, action] = permission.split(':');
        return user.permissions[module]?.includes(action) || false;
    }, [permission, user]);

    const isAuthorized = hasRequiredRole && hasRequiredPermission;

    // --- Real-time Audit Trail Effect ---
    useEffect(() => {
        // This effect triggers only when an access attempt is definitively unauthorized.
        if (!loading && isAuthenticated && !isAuthorized) {
            const log = {
                type: 'unauthorized_access_attempt',
                userId: user?.id || 'N/A',
                userRole: user?.role || 'N/A',
                requiredRoles: roles,
                requiredPermission: permission,
                attemptedRoute: location.pathname,
                timestamp: new Date().toISOString(),
            };
            socket.emit('audit:log', log);
        }
    }, [loading, isAuthenticated, isAuthorized, user, location, roles, permission]);

    // --- Render Logic ---
    if (loading) {
        return <LoadingSpinner />;
    }

    if (!isAuthenticated) {
        // Redirect unauthenticated users to the login page, saving their intended location.
        return <Navigate to="/login" replace state={{ from: location }} />;
    }

    if (!isAuthorized) {
        // Show a clear access denied message for authenticated but unauthorized users.
        return (
            <AccessDeniedContainer>
                <h2>🚫 Access Denied</h2>
                <p>You do not have the necessary permissions to view this page.</p>
                {roles.length > 0 && <p>Role Required: {roles.join(' or ')}</p>}
                {permission && <p>Permission Required: {permission}</p>}
                <p>Your Role: <strong>{user.role}</strong></p>
            </AccessDeniedContainer>
        );
    }

    // If all checks pass, render the child component.
    return children;
};

// --- PropTypes for Code Quality ---
ProtectedRoute.propTypes = {
    children: PropTypes.node.isRequired,
    roles: PropTypes.arrayOf(PropTypes.string),
    permission: PropTypes.string,
};

export default ProtectedRoute;

// --- Styled Components ---
const AccessDeniedContainer = styled.div`
  text-align: center;
  padding: 3rem;
  margin: 3rem auto;
  max-width: 600px;
  border-radius: 12px;
  background-color: #fff3f3;
  border: 1px solid #ffcccc;
  color: #d8000c;

  h2 {
    font-size: 2rem;
    margin-bottom: 0.75rem;
  }

  p {
    margin-bottom: 0.5rem;
    font-size: 1.1rem;
  }

  strong {
    color: #000;
  }
`;
