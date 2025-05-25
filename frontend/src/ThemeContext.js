import React, { createContext, useState, useCallback, useContext } from 'react';

export const ThemeModeContext = createContext({
  mode: 'light',
  toggleThemeMode: () => {},
});

export const ThemeModeProvider = ({ children }) => {
  const [mode, setMode] = useState('light'); // Default to light mode

  const toggleThemeMode = useCallback(() => {
    setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
  }, []);

  return (
    <ThemeModeContext.Provider value={{ mode, toggleThemeMode }}>
      {children}
    </ThemeModeContext.Provider>
  );
};

export const useThemeMode = () => useContext(ThemeModeContext);
