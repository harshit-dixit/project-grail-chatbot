import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Container, Paper, TextField, Button, Typography, Box, AppBar, Toolbar, IconButton, 
  Grow, Avatar, useTheme, Snackbar, Alert as MuiAlert, Tooltip, CircularProgress
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import SettingsIcon from '@mui/icons-material/Settings';
import DeleteSweepIcon from '@mui/icons-material/DeleteSweep';
import { Routes, Route, Link as RouterLink, useLocation } from 'react-router-dom';
import AdminPage from './AdminPage';
import tataSteelBlueLogo from './logo/tata_steel_blue_svg.svg'; 
import tataBlueLogo from './logo/tata_svg.svg';

const Alert = React.forwardRef(function Alert(props, ref) {
  return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});

const initialMessages = [
  { sender: 'bot', text: 'Hello! How can I help you today?', id: "initialWelcome-1" }
];

const AppHeader = ({ theme }) => {
  if (typeof tataSteelBlueLogo === 'undefined') {
    console.warn('tataSteelBlueLogo is undefined at AppHeader render time.');
  } else {
    console.log('tataSteelBlueLogo in AppHeader:', tataSteelBlueLogo);
  }

  return (
    <AppBar position="static" sx={{ backgroundColor: theme.palette.background.paper, color: theme.palette.text.primary, boxShadow: theme.shadows[2] }}>
      <Container maxWidth="xl"> 
        <Toolbar disableGutters sx={{ minHeight: '64px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', px: { xs: 2, sm: 3 } }}>
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            minWidth: '120px',
            justifyContent: 'flex-start'
          }}> 
            {tataSteelBlueLogo ? (
              <img 
                src={tataSteelBlueLogo} 
                alt="Tata Steel Blue Logo" 
                style={{ 
                  height: '24.5px', /* 70% of 35px */
                  width: 'auto', 
                  display: 'block',
                  objectFit: 'contain',
                  alignSelf: 'center' /* Ensure vertical centering */
                }} 
              />
            ) : (
              <Typography variant="caption" color="error">Left Logo Missing</Typography>
            )}
          </Box>
          <Box sx={{ 
            flexGrow: 1, 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center', 
            textAlign: 'center', 
            px: 2 
          }}>
            <Typography variant="h5" component="h1" sx={{ 
              fontWeight: 'bold', 
              color: theme.palette.text.primary,
              whiteSpace: 'nowrap'
            }}>
              Project GRAIL Chatbot
            </Typography>
          </Box>
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'flex-end', 
            minWidth: '120px'
          }}> 
            {tataBlueLogo && (
              <img 
                src={tataBlueLogo} 
                alt="Tata Blue Logo" 
                style={{ 
                  height: '35px', 
                  width: 'auto', 
                  display: 'block',
                  objectFit: 'contain'
                }} 
              />
            )}
            <Tooltip title="Admin Settings">
              <IconButton component={RouterLink} to="/admin" sx={{ color: theme.palette.action.active }}>
                <SettingsIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

const ChatInterface = ({
  userInput, setUserInput, messages, isAsking, 
  handleAskQuestion, handleClearChat, messagesEndRef, 
  apiKeyLoaded, sopsProcessed
}) => {
  const theme = useTheme();
  const chatboxBorderRadius = 4; 

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      if (userInput.trim()) {
        handleAskQuestion();
      }
    }
  };

  let inputPlaceholder = "Ask anything...";
  if (!apiKeyLoaded) {
    inputPlaceholder = "API Key not loaded. Please check Admin Page.";
  } else if (!sopsProcessed) {
    inputPlaceholder = "SOPs data not processed. Please process on Admin Page.";
  }

  const buttonSx = {
    height: '56px', 
    minWidth: '56px',
    borderRadius: chatboxBorderRadius, 
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '0 16px', 
  };

  return (
    <Container maxWidth="lg" sx={{ height: 'calc(100vh - 64px - 16px)', display: 'flex', flexDirection: 'column', pt: 2, pb:0 }}> 
      <Paper elevation={3} sx={{
          flexGrow: 1, 
          display: 'flex', 
          flexDirection: 'column', 
          overflow: 'hidden', 
          backgroundColor: theme.palette.background.paper,
          borderRadius: chatboxBorderRadius, 
          minHeight: 0 
        }}>
        <Box sx={{ flexGrow: 1, p: 2, overflowY: 'auto' }}>
          {messages.map((msg) => (
            <Grow in={true} key={msg.id}>
              <Box sx={{
                mb: 1.5,
                display: 'flex',
                flexDirection: msg.sender === 'user' ? 'row-reverse' : 'row',
                alignItems: 'flex-start',
              }}>
                <Paper 
                  elevation={1} 
                  sx={{
                    p: 1.5,
                    borderRadius: chatboxBorderRadius, 
                    backgroundColor: msg.sender === 'user' 
                                     ? theme.palette.primary.main 
                                     : (theme.palette.mode === 'light' ? theme.palette.grey[200] : theme.palette.grey[700]), 
                    color: msg.sender === 'user' 
                           ? theme.palette.primary.contrastText 
                           : theme.palette.text.primary,
                    maxWidth: '75%',
                    wordWrap: 'break-word',
                  }}
                >
                  <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>{msg.text}</Typography>
                </Paper>
              </Box>
            </Grow>
          ))}
          <div ref={messagesEndRef} />
        </Box>

        <Box sx={{ p: 2, borderTop: `1px solid ${theme.palette.divider}` }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder={inputPlaceholder}
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              onKeyPress={handleKeyPress}
              multiline
              maxRows={4}
              disabled={isAsking || !apiKeyLoaded || !sopsProcessed}
              sx={{
                flexGrow: 1,
                '& .MuiOutlinedInput-root': {
                  borderRadius: chatboxBorderRadius, 
                  backgroundColor: theme.palette.background.default, 
                  '& input::placeholder': { 
                    color: theme.palette.text.secondary,
                    opacity: 1, 
                  },
                  '& textarea::placeholder': { 
                    color: theme.palette.text.secondary,
                    opacity: 1,
                  },
                }
              }}
            />
            <Button 
              variant="contained" 
              color="primary" 
              onClick={handleAskQuestion} 
              disabled={isAsking || !userInput.trim() || !apiKeyLoaded || !sopsProcessed}
              sx={{
                ...buttonSx,
                backgroundColor: theme.palette.primary.main,
                '&:hover': {
                  backgroundColor: theme.palette.primary.dark,
                }
              }}
            >
              {isAsking ? <CircularProgress size={24} sx={{ color: theme.palette.primary.contrastText }} /> : <SendIcon sx={{ color: theme.palette.primary.contrastText }}/>}
            </Button>
            <Tooltip title="Clear Chat">
              <IconButton 
                onClick={handleClearChat} 
                sx={{
                  ...buttonSx,
                  color: theme.palette.error.main,
                  border: `1px solid ${theme.palette.error.light}`,
                  '&:hover': {
                    backgroundColor: theme.palette.action.hover, 
                    borderColor: theme.palette.error.main,
                  }
                }}
              >
                <DeleteSweepIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
};

function App() {
  const theme = useTheme(); 
  const location = useLocation(); 

  const [userInput, setUserInput] = useState('');
  const [messages, setMessages] = useState([...initialMessages]); 
  const [isAsking, setIsAsking] = useState(false);
  const messagesEndRef = useRef(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState('info'); 
  const [apiKeyLoaded, setApiKeyLoaded] = useState(false);
  const [sopsProcessed, setSopsProcessed] = useState(false);

  const showSnackbar = (message, severity = 'info') => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setSnackbarOpen(true);
  };

  const handleCloseSnackbar = (event, reason) => {
    if (reason === 'clickaway') return;
    setSnackbarOpen(false);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const fetchAppStatus = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:5001/api/status');
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      setApiKeyLoaded(data.api_key_loaded);
      setSopsProcessed(data.sops_processed);
    } catch (error) {
      console.error("Failed to fetch app status:", error);
      setApiKeyLoaded(false);
      setSopsProcessed(false);
      if (location.pathname !== '/admin') {
         showSnackbar('Failed to fetch initial app status. Backend may be down.', 'error');
      }
    }
  }, [location.pathname]); 

  useEffect(() => {
    fetchAppStatus();
  }, [fetchAppStatus]);

  const handleAskQuestion = async () => {
    if (!userInput.trim()) return;
    const currentQuestion = userInput;
    const userMessage = { text: currentQuestion, sender: "user", id: `user-${Date.now()}` };

    setMessages(prev => [...prev, userMessage]);
    setUserInput('');
    setIsAsking(true);

    try {
      const response = await fetch('http://localhost:5001/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: currentQuestion }),
      });

      const responseText = await response.text();
      if (response.ok) {
        const data = JSON.parse(responseText);
        setMessages(prev => [...prev, { text: data.answer, sender: "bot", id: `bot-${Date.now()}` }]);
      } else {
        console.error('Error response status:', response.status, 'Raw text:', responseText);
        let displayMessage = `Error: ${response.status}`;
        try {
          const errorData = JSON.parse(responseText);
          displayMessage = errorData.error || errorData.message || displayMessage;
        } catch (parseError) { /* Use raw text or status if JSON parsing fails */ }
        setMessages(prev => [...prev, { text: displayMessage, sender: "bot", id: `bot-error-${Date.now()}` }]);
        showSnackbar(displayMessage, 'error');
      }
    } catch (error) {
      console.error('Network or other error asking question:', error);
      const errorMessage = 'Network error. Could not reach the chatbot service.';
      setMessages(prev => [...prev, { text: errorMessage, sender: "bot", id: `bot-network-error-${Date.now()}` }]);
      showSnackbar(errorMessage, 'error');
    }
    setIsAsking(false);
  };

  const handleClearChat = () => {
    setMessages([...initialMessages]); 
    showSnackbar('Chat cleared.', 'info');
  };

  if (location.pathname.startsWith("/admin")) {
    return <AdminPage />;
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh', backgroundColor: theme.palette.background.default }}>
      <AppHeader theme={theme} />
      <Routes>
        <Route 
          path="/"
          element={(
            <ChatInterface 
              userInput={userInput}
              setUserInput={setUserInput}
              messages={messages}
              isAsking={isAsking}
              handleAskQuestion={handleAskQuestion}
              handleClearChat={handleClearChat}
              messagesEndRef={messagesEndRef}
              apiKeyLoaded={apiKeyLoaded}
              sopsProcessed={sopsProcessed}
            />
          )}
        />
        <Route path="/admin" element={<AdminPage showSnackbar={showSnackbar} refreshMainAppStatus={fetchAppStatus} />} />
      </Routes>
      
      <Snackbar open={snackbarOpen} autoHideDuration={6000} onClose={handleCloseSnackbar} anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}>
        <Alert onClose={handleCloseSnackbar} severity={snackbarSeverity} sx={{ width: '100%' }}>
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default App;
