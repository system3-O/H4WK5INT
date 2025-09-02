import React from 'react';
import { Box, Typography, Container } from '@mui/material';

interface OSINTModulesProps {
  onLogout: () => void;
  showNotification: (message: string, severity: 'success' | 'error' | 'warning' | 'info') => void;
}

const OSINTModules: React.FC<OSINTModulesProps> = ({ onLogout, showNotification }) => {
  return (
    <Container>
      <Box sx={{ mt: 4 }}>
        <Typography variant="h4" gutterBottom>
          OSINT Modules
        </Typography>
        <Typography variant="body1" color="text.secondary">
          OSINT module selection and execution interface - Coming soon
        </Typography>
      </Box>
    </Container>
  );
};

export default OSINTModules;