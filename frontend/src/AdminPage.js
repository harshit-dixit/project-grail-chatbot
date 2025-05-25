import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Chip,
  CircularProgress,
  Stack,
  Button,
  Container,
  IconButton,
  useTheme,
} from '@mui/material';
import AutorenewIcon from '@mui/icons-material/Autorenew';
import RefreshIcon from '@mui/icons-material/Refresh';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import { Link as RouterLink } from 'react-router-dom';
import { useThemeMode } from './ThemeContext';

const AdminPage = ({ showSnackbar, refreshMainAppStatus }) => {
  const theme = useTheme();
  const { mode, toggleThemeMode } = useThemeMode();
  const adminPanelBorderRadius = 4; // Sharper, less rounded corners

  const [adminBackendStatus, setAdminBackendStatus] = useState('Checking backend status...');
  const [adminApiKeyLoaded, setAdminApiKeyLoaded] = useState(false);
  const [adminSopsProcessed, setAdminSopsProcessed] = useState(false);
  const [isLoadingAdminStatus, setIsLoadingAdminStatus] = useState(true);
  const [isProcessingAdminSops, setIsProcessingAdminSops] = useState(false);

  // const getStatusChipColor = (status) => {
  //   if (status.includes('Error') || status.includes('Failed') || status.includes('not loaded')) return 'error';
  //   if (status.includes('connected')) return 'success';
  //   return 'default';
  // };

  const getBooleanChipColor = (value) => (value ? 'success' : 'error');

  const fetchAdminStatus = useCallback(async () => {
    setIsLoadingAdminStatus(true);
    try {
      const response = await fetch('http://localhost:5001/api/status');
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      setAdminApiKeyLoaded(data.api_key_loaded);
      setAdminSopsProcessed(data.sops_processed);
      if (data.error_message) setAdminBackendStatus(`Backend Error: ${data.error_message}`);
      else if (!data.api_key_loaded) setAdminBackendStatus('API Key not loaded. Check gemini_api_key.env.');
      else setAdminBackendStatus('Backend connected.');
    } catch (error) {
      console.error("Failed to fetch admin backend status:", error);
      setAdminBackendStatus('Failed to connect to backend. Is it running?');
      if (showSnackbar) showSnackbar('Failed to fetch admin backend status.', 'error');
    }
    setIsLoadingAdminStatus(false);
  }, [showSnackbar]);

  useEffect(() => {
    fetchAdminStatus();
  }, [fetchAdminStatus]);

  const handleAdminProcessSops = async () => {
    setIsProcessingAdminSops(true);
    if (showSnackbar) showSnackbar('Processing SOP documents... This may take a moment.', 'info');
    try {
      const response = await fetch('http://localhost:5001/api/process_sops', { method: 'POST' });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || `HTTP error! status: ${response.status}`);
      
      setAdminSopsProcessed(true); 
      if (showSnackbar) showSnackbar(`SOPs processed successfully. ${data.message || ''}. Found ${data.documents_processed_count} docs, ${data.text_chunks_count} chunks.`, 'success');
      await fetchAdminStatus(); 
      if (refreshMainAppStatus) {
        await refreshMainAppStatus(); 
      }
    } catch (error) {
      console.error("Failed to process SOPs (Admin):", error);
      if (showSnackbar) showSnackbar(`Error processing SOPs: ${error.message}`, 'error');
      setAdminSopsProcessed(false); 
    }
    setIsProcessingAdminSops(false);
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 3, borderRadius: adminPanelBorderRadius }}>
        <Stack direction="row" alignItems="center" spacing={1} mb={3}>
            <IconButton component={RouterLink} to="/">
                <ArrowBackIcon />
            </IconButton>
            <Typography variant="h5" component="h1">
            Admin Panel - System Status
            </Typography>
            <Button
              variant="outlined"
              onClick={toggleThemeMode}
              startIcon={mode === 'light' ? <Brightness4Icon /> : <Brightness7Icon />}
              sx={{ textTransform: 'none' }}
            >
              {mode === 'light' ? 'Switch to Dark Mode' : 'Switch to Light Mode'}
            </Button>
        </Stack>

        {isLoadingAdminStatus ? (
          <Stack alignItems="center" spacing={1} sx={{my: 3}}>
            <CircularProgress size={30} />
            <Typography variant="body1">Loading Status...</Typography>
          </Stack>
        ) : (
          <Stack spacing={2} sx={{mb: 3}}>
            <Grid container justifyContent="space-between" alignItems="center">
              <Typography variant="body1" component="span" fontWeight="medium">Backend Status:</Typography>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body1" sx={{ color: theme.palette.text.secondary, fontWeight: 'medium' }}>
                  {adminBackendStatus.includes('Error') ? adminBackendStatus : 'Backend connected.'}
                </Typography>
                <Chip 
                  label={adminBackendStatus.includes('Error') ? 'Error' : 'Connected'}
                  color={adminBackendStatus.includes('Error') ? 'error' : 'success'} 
                  size="small" 
                />
              </Box>
            </Grid>
            <Grid container justifyContent="space-between" alignItems="center">
              <Typography variant="body1" component="span" fontWeight="medium">API Key Loaded:</Typography>
              <Chip label={adminApiKeyLoaded ? 'Loaded' : 'Not Loaded'} color={getBooleanChipColor(adminApiKeyLoaded)} size="small" />
            </Grid>
            <Grid container justifyContent="space-between" alignItems="center">
              <Typography variant="body1" component="span" fontWeight="medium">SOPs Data Processed:</Typography>
              <Chip label={adminSopsProcessed ? 'Processed' : 'Not Processed'} color={adminSopsProcessed ? 'success' : 'warning'} size="small" />
            </Grid>
          </Stack>
        )}

        <Stack direction="row" spacing={2} justifyContent="center">
          <Button 
            variant="contained" 
            color="primary"
            size="large" 
            startIcon={<AutorenewIcon />} 
            onClick={handleAdminProcessSops} 
            disabled={isProcessingAdminSops || !adminApiKeyLoaded || isLoadingAdminStatus}
            sx={{ flexGrow:1}}
          >
            {isProcessingAdminSops ? 'Processing...' : 'Process SOPs Data'}
          </Button>
          <Button 
            variant="outlined" 
            color="secondary"
            size="large" 
            startIcon={<RefreshIcon />} 
            onClick={fetchAdminStatus} 
            disabled={isLoadingAdminStatus || isProcessingAdminSops}
            sx={{ flexGrow:1}}
          >
            Refresh Status
          </Button>
        </Stack>
      </Paper>
    </Container>
  );
};

export default AdminPage;
