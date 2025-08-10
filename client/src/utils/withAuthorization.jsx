// ~/client/src/utils/withAuthorization.jsx

import React from 'react';
import { useSelector } from 'react-redux';
import { Navigate, useLocation } from 'react-router-dom';
import LoadingSpinner from '../components/LoadingSpinner';

const withAuthorization = (WrappedComponent, allowedRoles = []) => {
    return (props) => {
        const { isAuthenticated, user, loading } = useSelector((state) => state.auth);
        const location = useLocation();

        if (loading) return <LoadingSpinner />;

        if (!isAuthenticated) {
            return <Navigate to="/login" replace state={{ from: location }} />;
        }

        if (allowedRoles.length && !allowedRoles.includes(user.role)) {
            return (
                <div style={{ padding: '2rem', color: 'crimson' }}>
                    ⛔ Access Denied — You don’t have the required permissions.
                </div>
            );
        }

        return <WrappedComponent {...props} />;
    };
};

export default withAuthorization;
