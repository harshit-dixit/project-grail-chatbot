import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { grey } from '@mui/material/colors'; // Import MUI grey color palette
import { ThemeModeProvider, useThemeMode } from './ThemeContext';

// Import Google Fonts: Montserrat for headers, Roboto for body
const fontLink = document.createElement('link');
fontLink.href = 'https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;700&family=Roboto:wght@300;400;500;700&display=swap';
fontLink.rel = 'stylesheet';
document.head.appendChild(fontLink);

// MUI default shadows array (or a simplified version)
const defaultShadows = [
  'none',
  '0px 2px 1px -1px rgba(0,0,0,0.2),0px 1px 1px 0px rgba(0,0,0,0.14),0px 1px 3px 0px rgba(0,0,0,0.12)', // Elevation 1
  '0px 3px 1px -2px rgba(0,0,0,0.2),0px 2px 2px 0px rgba(0,0,0,0.14),0px 1px 5px 0px rgba(0,0,0,0.12)', // Elevation 2 (used by AppBar)
  '0px 3px 3px -2px rgba(0,0,0,0.2),0px 3px 4px 0px rgba(0,0,0,0.14),0px 1px 8px 0px rgba(0,0,0,0.12)', // Elevation 3
  '0px 2px 4px -1px rgba(0,0,0,0.2),0px 4px 5px 0px rgba(0,0,0,0.14),0px 1px 10px 0px rgba(0,0,0,0.12)', // Elevation 4
  // ... add more if needed, up to 24
];
for (let i = defaultShadows.length; i < 25; i++) {
  defaultShadows.push(defaultShadows[4]); // Fill remaining with a common shadow if not all are defined
}

// Standard MUI zIndex values
const zIndex = {
  mobileStepper: 1000,
  fab: 1050,
  speedDial: 1050,
  appBar: 1100,
  drawer: 1200,
  modal: 1300,
  snackbar: 1400,
  tooltip: 1500,
};

const spacing = (factor) => `${8 * factor}px`;

const breakpoints = {
  values: {
    xs: 0,
    sm: 600,
    md: 900,
    lg: 1200,
    xl: 1536,
  },
  // Helper functions can be added here if needed, e.g., up(), down(), between()
  // For simplicity, just defining values, MUI components will use these.
};

const transitions = {
  easing: {
    easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    easeOut: 'cubic-bezier(0.0, 0, 0.2, 1)',
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
    sharp: 'cubic-bezier(0.4, 0, 0.6, 1)',
  },
  duration: {
    shortest: 150,
    shorter: 200,
    short: 250,
    standard: 300,
    complex: 375,
    enteringScreen: 225,
    leavingScreen: 195,
  },
  create: function (props = 'all', options = {}) { // Use 'function' to access 'this' for its own properties
    const { duration = this.duration.standard, easing = this.easing.easeInOut, delay = 0 } = options;
    return `${props} ${typeof duration === 'string' ? duration : duration + 'ms'} ${easing} ${typeof delay === 'string' ? delay : delay + 'ms'}`;
  },
};

const mixins = {
  toolbar: {
    minHeight: 56,
    '@media (min-width:0px) and (orientation: landscape)': {
      minHeight: 48,
    },
  },
};

// Define your light and dark themes
const getDesignTokens = (mode) => ({
  palette: {
    mode,
    common: { 
      black: '#000000',
      white: '#ffffff',
    },
    grey: grey, // Use the imported grey scale from @mui/material/colors
    // Provide a default contrast text function
    getContrastText: (background) => {
      // Simple contrast calculation - can be enhanced
      const color = background.charAt(0) === '#' ? background : background.split('(')[0];
      const r = parseInt(color.substr(1, 2), 16);
      const g = parseInt(color.substr(3, 2), 16);
      const b = parseInt(color.substr(5, 2), 16);
      const brightness = (r * 299 + g * 587 + b * 114) / 1000;
      return brightness > 128 ? 'rgba(0, 0, 0, 0.87)' : '#ffffff';
    },
    primary: mode === 'light' 
      ? { main: '#2979FF', contrastText: '#FFFFFF' } 
      : { main: '#64B5F6', contrastText: '#000000' },
    secondary: mode === 'light' 
      ? { main: '#FF7043', contrastText: '#FFFFFF' } 
      : { main: '#FFAB91', contrastText: '#000000' }, 
    error: mode === 'light' 
      ? { main: '#D32F2F', contrastText: '#FFFFFF' } 
      : { main: '#F44336', contrastText: '#FFFFFF' },
    warning: mode === 'light' 
      ? { main: '#FFA000', contrastText: 'rgba(0,0,0,0.87)' } 
      : { main: '#FFC107', contrastText: 'rgba(0,0,0,0.87)' },
    info: mode === 'light' 
      ? { main: '#1976D2', contrastText: '#FFFFFF' } 
      : { main: '#2196F3', contrastText: '#FFFFFF' },
    success: mode === 'light' 
      ? { main: '#388E3C', contrastText: '#FFFFFF' } 
      : { main: '#4CAF50', contrastText: '#FFFFFF' },
    background: mode === 'light' 
      ? { default: '#F4F6F8', paper: '#FFFFFF' } 
      : { default: '#121212', paper: '#1E1E1E' },
    text: mode === 'light' 
      ? { primary: 'rgba(0,0,0,0.87)', secondary: 'rgba(0,0,0,0.6)', disabled: 'rgba(0,0,0,0.38)' } 
      : { primary: '#FFFFFF', secondary: 'rgba(255,255,255,0.7)', disabled: 'rgba(255,255,255,0.5)' },
    action: mode === 'light' 
      ? { 
          active: 'rgba(0, 0, 0, 0.54)',
          hover: 'rgba(0, 0, 0, 0.04)',
          hoverOpacity: 0.04,
          selected: 'rgba(0, 0, 0, 0.08)',
          selectedOpacity: 0.08,
          disabled: 'rgba(0, 0, 0, 0.26)',
          disabledBackground: 'rgba(0, 0, 0, 0.12)',
          disabledOpacity: 0.38,
          focus: 'rgba(0, 0, 0, 0.12)',
          focusOpacity: 0.12,
          activatedOpacity: 0.12,
        }
      : { 
          active: '#ffffff',
          hover: 'rgba(255, 255, 255, 0.08)',
          hoverOpacity: 0.08,
          selected: 'rgba(255, 255, 255, 0.16)',
          selectedOpacity: 0.16,
          disabled: 'rgba(255, 255, 255, 0.3)',
          disabledBackground: 'rgba(255, 255, 255, 0.12)',
          disabledOpacity: 0.38,
          focus: 'rgba(255, 255, 255, 0.12)',
          focusOpacity: 0.12,
          activatedOpacity: 0.24,
        },
    divider: mode === 'light' ? 'rgba(0, 0, 0, 0.12)' : 'rgba(255, 255, 255, 0.12)',
    // Removed the mode-specific 'grey' objects from here as it's now top-level and uses the imported 'grey'
  },
});

// Component to provide the correct theme based on context
const AppWithTheme = () => {
  const { mode } = useThemeMode();
  const theme = React.useMemo(() => {
    const designTokens = getDesignTokens(mode);
    
    // Create theme with all configurations
    return createTheme({
      // Typography settings
      typography: {
        fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
        h1: { fontFamily: '"Montserrat", sans-serif', fontWeight: 700 },
        h2: { fontFamily: '"Montserrat", sans-serif', fontWeight: 600 },
        h3: { fontFamily: '"Montserrat", sans-serif', fontWeight: 600 },
        h4: { fontFamily: '"Montserrat", sans-serif', fontWeight: 500 },
        h5: { fontFamily: '"Montserrat", sans-serif', fontWeight: 500 },
        h6: { fontFamily: '"Roboto", sans-serif', fontWeight: 500 },
        button: { textTransform: 'none' },
      },
      // Shape settings
      shape: {
        borderRadius: 4,
      },
      // Theme utilities
      shadows: defaultShadows,
      zIndex,
      spacing,
      breakpoints,
      transitions,
      mixins,
      // Apply design tokens
      ...designTokens, // This spreads the palette which includes the mode.
      // Component overrides
      components: {
        MuiCssBaseline: {
          styleOverrides: {
            body: {
              margin: 0,
              padding: 0,
              boxSizing: 'border-box',
              transition: 'background-color 0.3s ease, color 0.3s ease',
              backgroundColor: designTokens.palette.background?.default || '#ffffff',
              color: designTokens.palette.text?.primary || 'rgba(0, 0, 0, 0.87)',
            },
            '::-webkit-scrollbar': {
              width: '8px',
              height: '8px',
            },
            '::-webkit-scrollbar-track': {
              background: 'transparent',
            },
            '::-webkit-scrollbar-thumb': {
              background: '#888',
              borderRadius: '4px',
              '&:hover': {
                background: '#555',
              },
            },
          },
        },
        MuiButton: {
          styleOverrides: {
            root: {
              borderRadius: 4,
              transition: 'background-color 0.2s ease, box-shadow 0.2s ease',
            },
          },
        },
        MuiPaper: {
          styleOverrides: {
            root: {
              borderRadius: 4,
              backgroundImage: 'none',
            },
          },
        },
        MuiCard: {
          styleOverrides: {
            root: {
              borderRadius: 4,
            },
          },
        },
      },
    });
  }, [mode]);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  );
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <ThemeModeProvider> {/* Provider for mode toggle */}
      <BrowserRouter>
        <AppWithTheme /> {/* Consumes mode and provides theme */}
      </BrowserRouter>
    </ThemeModeProvider>
  </React.StrictMode>
);

reportWebVitals();
