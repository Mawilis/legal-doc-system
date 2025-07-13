// /src/theme.js
import { createTheme } from '@mui/material/styles';

/**
 * Creates and exports a Material UI theme.
 * Extend this theme to customize colors, typography, and component behavior.
 */
const theme = createTheme({
    palette: {
        primary: {
            main: '#1976d2', // A professional blue tone
        },
        secondary: {
            main: '#dc004e', // A contrasting pink tone
        },
    },
    typography: {
        fontFamily: 'Roboto, Arial, sans-serif',
    },
    // Optionally customize component defaults here
});

export default theme;
