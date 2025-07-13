// /src/components/DebugCircularProgress.js
import React, { useEffect } from 'react';
import CircularProgress from '@mui/material/CircularProgress';
import { useTheme } from '@mui/material/styles'; // Use the useTheme hook to get the theme

const DebugCircularProgress = (props) => {
    const theme = useTheme();

    useEffect(() => {
        console.log("[DebugCircularProgress] Theme:", theme);
    }, [theme]);

    return <CircularProgress {...props} />;
};

export default DebugCircularProgress;
