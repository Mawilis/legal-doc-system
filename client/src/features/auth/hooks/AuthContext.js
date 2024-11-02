// ~/legal-doc-system/client/src/features/auth/hooks/AuthContext.js
import React, { createContext, useContext, useState } from 'react';

// Create AuthContext
const AuthContext = createContext();

// Hook to use the Auth context
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

// AuthProvider component to wrap around the App
export const AuthProvider = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    const login = (userData) => {
        setIsAuthenticated(true);
        localStorage.setItem('token', userData.token);
    };

    const logout = () => {
        setIsAuthenticated(false);
        localStorage.removeItem('token');
    };

    return (
        <AuthContext.Provider value={{ isAuthenticated, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export default AuthContext;
