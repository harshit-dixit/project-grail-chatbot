import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Chip,
  CircularProgress,
  Stack,
  Button,
} from '@mui/material';
import AutorenewIcon from '@mui/icons-material/Autorenew';
import DeleteSweepIcon from '@mui/icons-material/DeleteSweep';

function AdminPage({
  isLoadingStatus,
  backendStatus,
  apiKeyLoaded,
  sopsProcessed,
  isProcessingSops,
  handleProcessSops,
  handleClearChat,
  messages, // for disabled logic of clear chat
  initialMessages, // for disabled logic of clear chat
  getStatusChipColor,
  getBooleanChipColor,
}) {
  return (
    <>
      <h1>Admin Page</h1>
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
                disabled={messages.length <= 1 && messages[0]?.id === initialMessages[0]?.id}
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
    </>
  );
}

export default AdminPage;
