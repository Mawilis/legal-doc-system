// ~/legal-doc-system/client/src/context/ThemeContext.js

import React, { createContext, useState, useMemo, useContext } from 'react';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';

// 🎨 Define light and dark themes
const lightTheme = {
    mode: 'light',
    colors: {
        background: '#ffffff',
        text: '#333333',
        primary: '#007bff',
        sidebarBg: '#2c3e50',
        card: '#f8f9fa',
    },
};

const darkTheme = {
    mode: 'dark',
    colors: {
        background: '#121212',
        text: '#f0f0f0',
        primary: '#90caf9',
        sidebarBg: '#1f1f1f',
        card: '#1c1c1c',
        
    },
};

// 🌙 Create ThemeContext
const ThemeContext = createContext({
    isDarkMode: false,
    toggleDarkMode: () => { },
});

// 🔁 Provider that wraps your app
export const ThemeProvider = ({ children }) => {
    const [isDarkMode, setIsDarkMode] = useState(() => {
        const saved = localStorage.getItem('darkMode');
        return saved === 'true';
    });

    const toggleDarkMode = () => {
        setIsDarkMode((prev) => {
            localStorage.setItem('darkMode', !prev);
            return !prev;
        });
    };

    const theme = useMemo(() => (isDarkMode ? darkTheme : lightTheme), [isDarkMode]);

    return (
        <ThemeContext.Provider value={{ isDarkMode, toggleDarkMode }}>
            <StyledThemeProvider theme={theme}>{children}</StyledThemeProvider>
        </ThemeContext.Provider>
    );
};

// 🔓 Easy hook for consuming
export const useTheme = () => useContext(ThemeContext);
