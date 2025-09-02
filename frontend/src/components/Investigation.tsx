import React from 'react';
import { Box, Typography, Container } from '@mui/material';

interface InvestigationProps {
  onLogout: () => void;
  showNotification: (message: string, severity: 'success' | 'error' | 'warning' | 'info') => void;
}

const Investigation: React.FC<InvestigationProps> = ({ onLogout, showNotification }) => {
  return (
    <Container>
      <Box sx={{ mt: 4 }}>
        <Typography variant="h4" gutterBottom>
          Investigations
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Investigation management interface - Coming soon
        </Typography>
      </Box>
    </Container>
  );
};

export default Investigation;