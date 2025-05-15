import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Define a basic MUI theme
// For more sophisticated theming, see: https://mui.com/customization/theming/
const projectGrailTheme = createTheme({
  palette: {
    mode: 'dark', // Ensure dark mode
    primary: {
      main: '#64b5f6', // Brighter Material Design Blue (blue[300])
    },
    secondary: {
      main: '#f06292', // Brighter Material Design Pink (pink[300])
    },
    background: {
      default: '#121212', // Standard dark background
      paper: '#1E1E1E',   // Standard dark paper surface
    },
    text: {
      primary: '#FFFFFF', // White
      secondary: 'rgba(255, 255, 255, 0.7)', // Slightly transparent white for secondary text
    },
  },
  typography: {
    fontFamily: 'Roboto, sans-serif', 
    h1: {
      fontFamily: 'Montserrat, sans-serif',
      fontWeight: 700,
    },
    h2: {
      fontFamily: 'Montserrat, sans-serif',
      fontWeight: 700,
    },
    h3: {
      fontFamily: 'Montserrat, sans-serif',
      fontWeight: 700,
    },
    h4: {
      fontFamily: 'Montserrat, sans-serif',
      fontWeight: 700, 
    },
    h5: {
      fontFamily: 'Montserrat, sans-serif',
      fontWeight: 700,
    },
    h6: {
      fontFamily: 'Montserrat, sans-serif',
      fontWeight: 700,
    },
    subtitle1: {
      fontFamily: 'Roboto, sans-serif', 
    },
    body1: {
      fontFamily: 'Roboto, sans-serif',
    },
    body2: {
      fontFamily: 'Roboto, sans-serif',
    },
    button: {
      fontFamily: 'Montserrat, sans-serif', 
      fontWeight: 500, 
      textTransform: 'none', 
    },
    caption: {
      fontFamily: 'Roboto, sans-serif',
    },
    overline: {
      fontFamily: 'Montserrat, sans-serif',
    }
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8, 
          textTransform: 'none', 
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12, 
        }
      }
    }
    // Override other component styles here
  }
});

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <ThemeProvider theme={projectGrailTheme}> 
      <CssBaseline /> 
      <App />
    </ThemeProvider>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
