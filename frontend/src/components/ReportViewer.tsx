import React from 'react';
import { Box, Typography, Container } from '@mui/material';

interface ReportViewerProps {
  onLogout: () => void;
  showNotification: (message: string, severity: 'success' | 'error' | 'warning' | 'info') => void;
}

const ReportViewer: React.FC<ReportViewerProps> = ({ onLogout, showNotification }) => {
  return (
    <Container>
      <Box sx={{ mt: 4 }}>
        <Typography variant="h4" gutterBottom>
          Reports
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Report display and download interface - Coming soon
        </Typography>
      </Box>
    </Container>
  );
};

export default ReportViewer;