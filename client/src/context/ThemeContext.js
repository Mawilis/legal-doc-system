import React, { createContext, useContext, useMemo, useState } from 'react';

const UiThemeContext = createContext(null);

export function ThemeProvider({ children }) {
  const [darkMode, setDarkMode] = useState(false);
  const value = useMemo(() => ({
    darkMode,
    toggleTheme: () => setDarkMode(d => !d),
  }), [darkMode]);

  return (
    <UiThemeContext.Provider value={value}>
      {children}
    </UiThemeContext.Provider>
  );
}

export function useTheme() {
  const ctx = useContext(UiThemeContext);
  return ctx ?? { darkMode: false, toggleTheme: () => {} };
}

export const useThemeContext = useTheme;
