import React, { useState, useEffect, useRef } from 'react';
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Grid,
  Chip,
  CircularProgress,
  Stack,
  useTheme,
  Snackbar,
  Alert,
  Fab,
  Grow, 
  IconButton,
  // Accordion, 
  // AccordionSummary, 
  // AccordionDetails
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import AutorenewIcon from '@mui/icons-material/Autorenew';
import DeleteSweepIcon from '@mui/icons-material/DeleteSweep'; 
// import ExpandMoreIcon from '@mui/icons-material/ExpandMore'; 
import FindInPageIcon from '@mui/icons-material/FindInPage';
import tataSteelLogo from './logo/tata-steel-logo_light.png'; 
import tataLogoRight from './logo/tata_logo_light.png';

const initialMessages = [
  { sender: 'bot', text: 'Hello! How can I help you today?', id: "initialWelcome" }
];

function App() {
  const theme = useTheme();
  const [backendStatus, setBackendStatus] = useState('Checking backend status...');
  const [apiKeyLoaded, setApiKeyLoaded] = useState(false);
  const [sopsProcessed, setSopsProcessed] = useState(false);
  const [isLoadingStatus, setIsLoadingStatus] = useState(true);

  const [userInput, setUserInput] = useState('');
  const [messages, setMessages] = useState([...initialMessages]); 
  const [isProcessingSops, setIsProcessingSops] = useState(false);
  const [isAsking, setIsAsking] = useState(false);

  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState('info');

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const fetchBackendStatus = async () => {
    setIsLoadingStatus(true);
    try {
      const response = await fetch('http://localhost:5001/api/status');
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      setApiKeyLoaded(data.api_key_loaded);
      setSopsProcessed(data.sops_processed);
      if (data.error_message) setBackendStatus(`Backend Error: ${data.error_message}`);
      else if (!data.api_key_loaded) setBackendStatus('API Key not loaded. Check gemini_api_key.env.');
      else setBackendStatus('Backend connected.');
    } catch (error) {
      console.error("Failed to fetch backend status:", error);
      setBackendStatus('Failed to connect to backend. Is it running?');
      showSnackbar('Failed to fetch backend status.', 'error');
    }
    setIsLoadingStatus(false);
  };

  useEffect(() => {
    fetchBackendStatus();
  }, []);

  const showSnackbar = (message, severity = 'info') => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setSnackbarOpen(true);
  };

  const handleCloseSnackbar = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }
    setSnackbarOpen(false);
  };

  const handleClearChat = () => {
    setMessages([...initialMessages]);
    showSnackbar('Chat cleared.', 'info');
  };

  const handleProcessSops = async () => {
    setIsProcessingSops(true);
    showSnackbar('Processing SOP documents... This may take a moment.', 'info');
    try {
      const response = await fetch('http://localhost:5001/api/process_sops', { method: 'POST' });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || `HTTP error! status: ${response.status}`);
      
      setSopsProcessed(true); 
      showSnackbar(`SOPs processed successfully. ${data.message || ''}. Found ${data.documents_processed_count} docs, ${data.text_chunks_count} chunks.`, 'success');
      fetchBackendStatus(); 
    } catch (error) {
      console.error("Failed to process SOPs:", error);
      showSnackbar(`Error processing SOPs: ${error.message}`, 'error');
      setSopsProcessed(false); 
    }
    setIsProcessingSops(false);
  };

  const handleAskQuestion = async () => {
    if (!userInput.trim()) return;

    const newMessages = [...messages, { sender: 'user', text: userInput.trim(), id: `user-${Date.now()}` }];
    setMessages(newMessages);
    const currentQuestion = userInput.trim();
    setUserInput('');
    setIsAsking(true);

    try {
      const response = await fetch('http://localhost:5001/api/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: currentQuestion }),
      });

      const data = await response.json();
      if (response.ok) {
        const botResponseId = `bot-${Date.now()}`;
        const botMessage = { text: data.answer, sender: "bot", id: botResponseId };
        setMessages(prevMessages => [...prevMessages, botMessage]);
        showSnackbar('Answer found.', 'success');
      } else {
        const errorData = await response.json().catch(() => ({ error: 'Failed to parse error response.' }));
        const botErrorId = `bot-error-${Date.now()}`;
        const botMessage = { text: errorData.error || `HTTP error! status: ${response.status}`, sender: "bot", id: botErrorId };
        setMessages(prevMessages => [...prevMessages, botMessage]);
        showSnackbar(errorData.error || `HTTP error! status: ${response.status}`, 'error');
      }
    } catch (error) {
      console.error('Network or other error asking question:', error);
      const errorId = `bot-network-error-${Date.now()}`;
      setMessages(prevMessages => [
        ...prevMessages,
        { sender: 'bot', text: 'Network error. Could not reach the chatbot service.', id: errorId }
      ]);
      showSnackbar('Network error. Please check backend connection.', 'error');
    } finally {
      setIsAsking(false);
      setUserInput(''); 
    }
  };

  const getStatusChipColor = (status) => {
    if (status.includes('Error') || status.includes('Failed') || status.includes('not loaded')) return 'error';
    if (status.includes('connected')) return 'success';
    return 'default';
  };
  const getBooleanChipColor = (value) => (value ? 'success' : 'error');

  return (
    <Container maxWidth="lg" sx={{
      display: 'flex', 
      flexDirection: 'column', 
      minHeight: '100vh', 
      py: 2,
      backgroundColor: theme.palette.background.default 
    }}>
      <Box 
        component="header" 
        sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between', 
          py: 2, 
          mb: 2,
          borderBottom: `1px solid ${theme.palette.divider}`
        }}
      >
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'flex-start', 
          width: '200px', 
          flexShrink: 0 
        }}>
          <img 
            src={tataSteelLogo} 
            alt="Tata Steel Logo" 
            style={{ maxHeight: '50px', width: 'auto', display: 'block' }} 
          />
        </Box>
        <Box sx={{ flexGrow: 1, textAlign: 'center', px: 2 }}>
          <Typography variant="h4" component="h1" fontWeight="bold" color="primary">
            Project GRAIL
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            AI assistant for Tata Steel Group Reporting
          </Typography>
        </Box>
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'flex-end', 
          width: '200px', 
          flexShrink: 0 
        }}>
          <img 
            src={tataLogoRight} 
            alt="Tata Logo" 
            style={{ maxHeight: '50px', width: 'auto', display: 'block' }} 
          />
        </Box>
      </Box>

      <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
        <Paper elevation={3} sx={{ p: 2, display: 'inline-block', minWidth: '300px', borderRadius: '12px' }}>
          {isLoadingStatus ? (
            <Stack alignItems="center" spacing={1}>
              <CircularProgress size={24} />
              <Typography variant="body2">Loading Status...</Typography>
            </Stack>
          ) : (
            <Stack spacing={1.5}>
              <Grid container justifyContent="space-between" alignItems="center">
                <Typography variant="body2" component="span" fontWeight="medium">Backend:</Typography>
                <Chip label={backendStatus} color={getStatusChipColor(backendStatus)} size="small" sx={{ flexGrow: 1, mx:1, justifyContent:'flex-start', '& .MuiChip-label': {overflow: 'visible'} }}/>
              </Grid>
              <Grid container justifyContent="space-between" alignItems="center">
                <Typography variant="body2" component="span" fontWeight="medium">API Key:</Typography>
                <Chip label={apiKeyLoaded ? 'Loaded' : 'Not Loaded'} color={getBooleanChipColor(apiKeyLoaded)} size="small" />
              </Grid>
              <Grid container justifyContent="space-between" alignItems="center">
                <Typography variant="body2" component="span" fontWeight="medium">SOPs:</Typography>
                <Chip label={sopsProcessed ? 'Processed' : 'Not Processed'} color={sopsProcessed ? 'success' : 'warning'} size="small" />
              </Grid>
              <Button 
                variant="outlined" 
                size="small" 
                startIcon={<AutorenewIcon />} 
                onClick={handleProcessSops} 
                disabled={isProcessingSops || !apiKeyLoaded}
                sx={{
                  mt: 1, 
                  width: '100%',
                  transition: 'transform 0.2s ease-in-out, filter 0.2s ease-in-out',
                  '&:hover': {
                    filter: 'brightness(1.15)',
                    transform: 'scale(1.03)'
                  }
                }} 
              >
                {isProcessingSops ? 'Processing...' : 'Process SOPs'}
              </Button>
              <Button 
                variant="outlined" 
                size="small" 
                color="warning" 
                startIcon={<DeleteSweepIcon />} 
                onClick={handleClearChat} 
                disabled={messages.length <= 1 && messages[0]?.text === initialMessages[0]?.text} 
                sx={{
                  mt: 1, 
                  width: '100%',
                  transition: 'transform 0.2s ease-in-out, filter 0.2s ease-in-out',
                  '&:hover': {
                    filter: 'brightness(1.15)',
                    transform: 'scale(1.03)'
                  }
                }}
              >
                Clear Chat
              </Button>
            </Stack>
          )}
        </Paper>
      </Box>

      <Paper elevation={6} sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', backgroundColor: theme.palette.background.paper, mt: 0, borderRadius: '12px' }}>
        <Box sx={{ flexGrow: 1, p: 2, overflowY: 'auto' }}>
          {messages.map((msg, index) => (
            <Grow in={true} key={msg.id}> 
              <Box key={index} sx={{ mb: 2, display: 'flex', justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start' }}>
                <Paper 
                  elevation={1} 
                  sx={{
                    padding: '10px 15px',
                    borderRadius: '20px',
                    borderTopLeftRadius: msg.sender === 'bot' ? '5px' : '20px', 
                    borderTopRightRadius: msg.sender === 'user' ? '5px' : '20px', 
                    bgcolor: msg.sender === 'user' ? '#27AE60' : (theme.palette.mode === 'dark' ? theme.palette.grey[700] : theme.palette.grey[200]),
                    color: msg.sender === 'user' ? 'white' : theme.palette.text.primary,
                    maxWidth: '70%',
                    wordWrap: 'break-word',
                  }}
                >
                  <Typography variant="body1">{msg.text}</Typography>
                </Paper>
              </Box>
            </Grow>
          ))}
          {isAsking && (
            <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 1 }}>
              <Paper 
                elevation={1} 
                sx={{
                  padding: '10px 15px',
                  borderRadius: '20px',
                  borderTopLeftRadius: '5px',
                  bgcolor: theme.palette.mode === 'dark' ? theme.palette.grey[700] : theme.palette.grey[200],
                  color: theme.palette.text.primary,
                  maxWidth: '70%',
                  fontStyle: 'italic'
                }}
              >
                <Typography variant="body1">Thinking...</Typography>
              </Paper>
            </Box>
          )}
          <div ref={messagesEndRef} />
        </Box>

        <Box sx={{ p: 2, borderTop: `1px solid ${theme.palette.divider}`, backgroundColor: theme.palette.background.default }}>
          <Stack direction="row" spacing={1}>
            <TextField 
              fullWidth 
              variant="outlined" 
              placeholder={!apiKeyLoaded ? "API Key not loaded" : !sopsProcessed ? "Data not processed" : "Ask anything..."} 
              size="small"
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              disabled={isAsking || !apiKeyLoaded || !sopsProcessed || isProcessingSops}
              onKeyPress={(e) => e.key === 'Enter' && !isAsking && handleAskQuestion()}
              sx={{ '& .MuiOutlinedInput-root': { borderRadius: '20px', backgroundColor: theme.palette.background.paper } }} 
            />
            <IconButton 
              type="submit" 
              color="primary" 
              disabled={isAsking || isProcessingSops || !sopsProcessed || userInput.trim() === ''}
              sx={{
                ml: 1,
                transition: 'transform 0.2s ease-in-out, filter 0.2s ease-in-out',
                '&:hover': {
                  filter: 'brightness(1.2)',
                  transform: 'scale(1.1)'
                }
              }}
            >
              <SendIcon />
            </IconButton>
          </Stack>
        </Box>
      </Paper>

      <Box component="footer" sx={{ textAlign: 'center', py: 2, mt: 'auto' }}>
        <Typography variant="caption" color="text.secondary">
          Designed by Tata Steel IT Services Group Reporting
        </Typography>
      </Box>

      <Snackbar open={snackbarOpen} autoHideDuration={6000} onClose={handleCloseSnackbar} anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}>
        <Alert onClose={handleCloseSnackbar} severity={snackbarSeverity} sx={{ width: '100%' }} variant="filled">
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </Container>
  );
}

export default App;
