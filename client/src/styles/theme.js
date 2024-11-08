// /Users/wilsonkhanyezi/legal-doc-system/client/src/styles/theme.js

import { createTheme } from '@mui/material/styles';

const theme = createTheme({
    palette: {
        primary: {
            main: '#1976d2', // A blue color for primary actions
            light: '#63a4ff',
            dark: '#004ba0',
            contrastText: '#ffffff',
        },
        secondary: {
            main: '#f50057', // A pink color for secondary actions
            light: '#ff5983',
            dark: '#bb002f',
            contrastText: '#ffffff',
        },
        success: {
            main: '#4caf50',
            light: '#80e27e',
            dark: '#087f23',
            contrastText: '#ffffff',
        },
        error: {
            main: '#d32f2f',
            light: '#ff6659',
            dark: '#9a0007',
            contrastText: '#ffffff',
        },
        background: {
            default: '#f4f6f8', // Light grey background for application
            paper: '#ffffff',
        },
        text: {
            primary: '#333333', // Dark text for readability
            secondary: '#777777',
            disabled: '#bdbdbd',
        },
    },
    typography: {
        fontFamily: 'Roboto, Arial, sans-serif',
        h1: {
            fontSize: '2.5rem',
            fontWeight: 700,
            lineHeight: 1.2,
            color: '#333333',
        },
        h2: {
            fontSize: '2rem',
            fontWeight: 700,
            lineHeight: 1.3,
            color: '#333333',
        },
        h3: {
            fontSize: '1.75rem',
            fontWeight: 600,
            lineHeight: 1.4,
            color: '#333333',
        },
        body1: {
            fontSize: '1rem',
            lineHeight: 1.5,
            color: '#444444',
        },
        body2: {
            fontSize: '0.875rem',
            lineHeight: 1.6,
            color: '#666666',
        },
        button: {
            fontSize: '1rem',
            textTransform: 'none',
            fontWeight: 600,
        },
    },
    spacing: 8, // Default spacing of 8px, can be used as theme.spacing(2) for 16px, etc.
    shape: {
        borderRadius: 8, // Rounded corners for consistency across components
    },
    components: {
        MuiButton: {
            styleOverrides: {
                root: {
                    borderRadius: 8,
                    textTransform: 'none',
                    padding: '8px 16px',
                    transition: 'background-color 0.3s',
                },
                containedPrimary: {
                    '&:hover': {
                        backgroundColor: '#005bb5', // Darker shade for hover state
                    },
                },
                containedSecondary: {
                    '&:hover': {
                        backgroundColor: '#c51162',
                    },
                },
            },
        },
        MuiPaper: {
            styleOverrides: {
                root: {
                    padding: '16px',
                    borderRadius: '8px',
                },
            },
        },
        MuiTypography: {
            styleOverrides: {
                gutterBottom: {
                    marginBottom: '0.5em',
                },
            },
        },
    },
});

export default theme;
