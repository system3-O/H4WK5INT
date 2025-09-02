import React from 'react';
import { Box, Typography, Container } from '@mui/material';

interface SettingsProps {
  onLogout: () => void;
  showNotification: (message: string, severity: 'success' | 'error' | 'warning' | 'info') => void;
}

const Settings: React.FC<SettingsProps> = ({ onLogout, showNotification }) => {
  return (
    <Container>
      <Box sx={{ mt: 4 }}>
        <Typography variant="h4" gutterBottom>
          Settings
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Application settings and configuration - Coming soon
        </Typography>
      </Box>
    </Container>
  );
};

export default Settings;