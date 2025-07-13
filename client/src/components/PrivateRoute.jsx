// /Users/wilsonkhanyezi/legal-doc-system/client/src/components/PrivateRoute.jsx

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';
import LoadingSpinner from './LoadingSpinner'; // Import your LoadingSpinner component

const PrivateRoute = ({ children, roles }) => { // Add roles prop
    const { isAuthenticated, user, loading } = useSelector((state) => state.auth);
    const location = useLocation();

    // Check if authentication status is still loading
    if (loading) {
        return <LoadingSpinner />; // Display a loading spinner
    }

    if (!isAuthenticated) {
        // Redirect to login page if not authenticated
        return <Navigate to="/login" replace state={{ from: location }} />;
    }

    // If roles prop is provided, check if the user has the required role
    if (roles && !roles.includes(user.role)) {
        return <div>You do not have permission to access this page.</div>;
    }

    return children; // Render the protected component
};

export default PrivateRoute;