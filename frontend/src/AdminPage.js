import React, { useState, useEffect, useCallback, useRef } from 'react';
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
import FileUploadIcon from '@mui/icons-material/FileUpload';
import ListAltIcon from '@mui/icons-material/ListAlt';
import DescriptionIcon from '@mui/icons-material/Description'; // For SOP list items

const AdminPage = ({ showSnackbar, refreshMainAppStatus }) => {
  const theme = useTheme();
  const { mode, toggleThemeMode } = useThemeMode();
  const adminPanelBorderRadius = 4; // Sharper, less rounded corners

  const [adminBackendStatus, setAdminBackendStatus] = useState('Checking backend status...');
  const [adminApiKeyLoaded, setAdminApiKeyLoaded] = useState(false);
  const [adminSopsProcessed, setAdminSopsProcessed] = useState(false);
  const [isLoadingAdminStatus, setIsLoadingAdminStatus] = useState(true);
  const [isProcessingAdminSops, setIsProcessingAdminSops] = useState(false);

  // State for SOP file management
  const [sopFilesList, setSopFilesList] = useState([]);
  const [isLoadingSopFiles, setIsLoadingSopFiles] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploadingFile, setIsUploadingFile] = useState(false);
  const fileInputRef = useRef(null);

  const getBooleanChipColor = (value) => (value ? 'success' : 'error');

  // Define fetchAdminStatus and fetchSopFiles before useEffect that uses them
  const fetchAdminStatus = useCallback(async () => {
    setIsLoadingAdminStatus(true);
    try {
      const response = await fetch('http://127.0.0.1:5001/api/status');
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

  // Fetch SOP files list
  const fetchSopFiles = useCallback(async () => {
    setIsLoadingSopFiles(true);
    try {
      const response = await fetch('http://127.0.0.1:5001/api/list_sops');
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setSopFilesList(data.sops || []);
    } catch (error) {
      console.error("Failed to fetch SOP files list:", error);
      if (showSnackbar) showSnackbar(`Failed to fetch SOPs list: ${error.message}`, 'error');
      setSopFilesList([]); // Clear list on error
    }
    setIsLoadingSopFiles(false);
  }, [showSnackbar]);

  useEffect(() => {
    fetchAdminStatus();
    fetchSopFiles(); // Fetch SOP files on mount
  }, [fetchAdminStatus, fetchSopFiles]);

  const handleAdminProcessSops = async () => {
    setIsProcessingAdminSops(true);
    if (showSnackbar) showSnackbar('Processing SOP documents... This may take a moment.', 'info');
    try {
      const response = await fetch('http://127.0.0.1:5001/api/process_sops', { method: 'POST' });
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

  // Handle file selection
  const handleFileChange = (event) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedFile(event.target.files[0]);
    }
  };

  // Trigger hidden file input
  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  // Handle file upload
  const handleFileUpload = async () => {
    if (!selectedFile) {
      if (showSnackbar) showSnackbar('No file selected for upload.', 'warning');
      return;
    }
    setIsUploadingFile(true);
    if (showSnackbar) showSnackbar(`Uploading ${selectedFile.name}...`, 'info');
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('http://127.0.0.1:5001/api/upload_sop', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      if (!response.ok || !data.success) {
        throw new Error(data.message || `HTTP error! status: ${response.status}`);
      }
      if (showSnackbar) showSnackbar(data.message || 'File uploaded successfully!', 'success');
      setSelectedFile(null); // Clear selected file
      if(fileInputRef.current) fileInputRef.current.value = ""; // Reset file input
      await fetchSopFiles(); // Refresh SOP files list
      await fetchAdminStatus(); // Refresh backend status as sops_processed will be false
      if (refreshMainAppStatus) refreshMainAppStatus(); // Refresh main app status if needed
    } catch (error) {
      console.error("Failed to upload file:", error);
      if (showSnackbar) showSnackbar(`File upload failed: ${error.message}`, 'error');
    }
    setIsUploadingFile(false);
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        style={{ display: 'none' }}
        accept=".pdf,.txt,.md,.docx"
      />
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

      {/* SOP File Management Panel */}
      <Paper elevation={3} sx={{ p: 3, borderRadius: adminPanelBorderRadius, mt: 3 }}>
        <Stack direction="row" alignItems="center" spacing={1} mb={2}>
          <ListAltIcon />
          <Typography variant="h6" component="h2">
            Manage SOP Files
          </Typography>
        </Stack>

        {/* File Upload Section */}
        <Box sx={{ mb: 3, p: 2, border: `1px dashed ${theme.palette.divider}`, borderRadius: adminPanelBorderRadius }}>
          <Typography variant="subtitle1" gutterBottom fontWeight="medium">Upload New SOP Document</Typography>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems="center">
            <Button 
              variant="outlined" 
              onClick={triggerFileInput} 
              disabled={isUploadingFile}
              startIcon={<FileUploadIcon />}
            >
              Choose File
            </Button>
            {selectedFile && (
              <Typography variant="body2" sx={{ flexGrow: 1, textAlign: { xs: 'center', sm: 'left'} }}>
                Selected: {selectedFile.name}
              </Typography>
            )}
            {!selectedFile && (
                <Typography variant="body2" sx={{ flexGrow: 1, color: theme.palette.text.secondary, textAlign: { xs: 'center', sm: 'left'} }}>
                    No file chosen. (PDF, TXT, MD, DOCX)
                </Typography>
            )}
            <Button 
              variant="contained" 
              color="primary" 
              onClick={handleFileUpload} 
              disabled={!selectedFile || isUploadingFile}
              startIcon={isUploadingFile ? <CircularProgress size={20} color="inherit" /> : <FileUploadIcon />}
            >
              {isUploadingFile ? 'Uploading...' : 'Upload File'}
            </Button>
          </Stack>
        </Box>

        {/* Loaded SOPs Section */}
        <Box sx={{ p: 2, border: `1px dashed ${theme.palette.divider}`, borderRadius: adminPanelBorderRadius }}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="subtitle1" fontWeight="medium">Currently Loaded SOPs</Typography>
                <Button 
                    variant="outlined" 
                    size="small"
                    onClick={fetchSopFiles} 
                    disabled={isLoadingSopFiles}
                    startIcon={isLoadingSopFiles ? <CircularProgress size={16} /> : <RefreshIcon />}
                >
                    Refresh List
                </Button>
            </Stack>
          {isLoadingSopFiles ? (
            <Stack alignItems="center" spacing={1} sx={{my: 2}}><CircularProgress size={24} /><Typography>Loading files...</Typography></Stack>
          ) : sopFilesList.length > 0 ? (
            <Box sx={{ maxHeight: 200, overflow: 'auto', border: `1px solid ${theme.palette.divider}`, borderRadius: adminPanelBorderRadius -1, p:1}}>
                <Stack divider={<Box sx={{borderBottom: `1px solid ${theme.palette.divider}`, my: 0.5}} />} spacing={0.5}>
                {sopFilesList.map((fileName, index) => (
                    <Stack direction="row" alignItems="center" spacing={1} key={index} sx={{px:1, py:0.5}}>
                        <DescriptionIcon fontSize="small" color="action" />
                        <Typography variant="body2">{fileName}</Typography>
                    </Stack>
                ))}
                </Stack>
            </Box>
          ) : (
            <Typography variant="body2" sx={{ color: theme.palette.text.secondary, textAlign: 'center', my: 2 }}>No SOP files found in the directory.</Typography>
          )}
        </Box>
      </Paper>
    </Container>
  );
};

export default AdminPage;
