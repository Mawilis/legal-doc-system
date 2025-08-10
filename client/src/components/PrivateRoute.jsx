// /client/src/components/PrivateRoute.jsx

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';
import PropTypes from 'prop-types';
import CircularProgress from '@mui/material/CircularProgress';
import Box from '@mui/material/Box';

const PrivateRoute = ({ children, roles = [] }) => {
    const { isAuthenticated, user, loading } = useSelector((state) => state.auth);
    const location = useLocation();

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
                <CircularProgress />
            </Box>
        );
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" replace state={{ from: location }} />;
    }

    if (roles.length && !roles.includes(user?.role)) {
        return (
            <Box sx={{ textAlign: 'center', mt: 8 }}>
                <h2>🚫 Access Denied</h2>
                <p>You do not have permission to view this page.</p>
            </Box>
        );
    }

    return children;
};

PrivateRoute.propTypes = {
    children: PropTypes.node.isRequired,
    roles: PropTypes.array,
};

export default PrivateRoute;
