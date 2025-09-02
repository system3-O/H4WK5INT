import React, { useState, useEffect } from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Button,
  Container,
  Grid,
  Card,
  CardContent,
  IconButton,
  Menu,
  MenuItem,
  Avatar,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Security,
  AccountCircle,
  Dashboard as DashboardIcon,
  Investigation,
  Assessment,
  Settings,
  ExitToApp,
  TrendingUp,
  Warning,
  CheckCircle,
  Schedule,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

// Services
import ApiService from '../services/api';
import AuthService from '../services/auth';

interface DashboardProps {
  onLogout: () => void;
  showNotification: (message: string, severity: 'success' | 'error' | 'warning' | 'info') => void;
}

interface DashboardStats {
  total_investigations: number;
  active_investigations: number;
  completed_investigations: number;
  archived_investigations: number;
  total_osint_operations: number;
  priority_breakdown: { [key: string]: number };
}

interface OSINTStats {
  total_operations: number;
  completed_operations: number;
  failed_operations: number;
  success_rate: number;
  module_usage: { [key: string]: number };
}

const Dashboard: React.FC<DashboardProps> = ({ onLogout, showNotification }) => {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [dashboardStats, setDashboardStats] = useState<DashboardStats | null>(null);
  const [osintStats, setOSINTStats] = useState<OSINTStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const user = AuthService.getCurrentUser();

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError('');

      const [investigationStatsResponse, osintStatsResponse] = await Promise.all([
        ApiService.getInvestigations(),
        ApiService.getOsintStatistics(),
      ]);

      // Calculate investigation statistics
      const investigations = investigationStatsResponse.data.investigations || [];
      const stats: DashboardStats = {
        total_investigations: investigations.length,
        active_investigations: investigations.filter((inv: any) => inv.status === 'active').length,
        completed_investigations: investigations.filter((inv: any) => inv.status === 'completed').length,
        archived_investigations: investigations.filter((inv: any) => inv.status === 'archived').length,
        total_osint_operations: 0,
        priority_breakdown: {},
      };

      // Calculate priority breakdown
      investigations.forEach((inv: any) => {
        const priority = inv.priority || 'medium';
        stats.priority_breakdown[priority] = (stats.priority_breakdown[priority] || 0) + 1;
      });

      setDashboardStats(stats);
      setOSINTStats(osintStatsResponse.data);

    } catch (error: any) {
      console.error('Dashboard data loading error:', error);
      setError('Failed to load dashboard data');
      showNotification('Failed to load dashboard data', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleNavigation = (path: string) => {
    navigate(path);
  };

  const handleLogout = () => {
    handleMenuClose();
    onLogout();
  };

  const getWelcomeMessage = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'primary';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
        bgcolor="background.default"
      >
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* App Bar */}
      <AppBar position="static" sx={{ bgcolor: 'background.paper', color: 'text.primary' }}>
        <Toolbar>
          <Security sx={{ mr: 2, color: 'primary.main' }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, color: 'primary.main' }}>
            H4WK5INT
          </Typography>
          
          <Button color="inherit" onClick={() => handleNavigation('/investigations')}>
            Investigations
          </Button>
          <Button color="inherit" onClick={() => handleNavigation('/osint')}>
            OSINT
          </Button>
          <Button color="inherit" onClick={() => handleNavigation('/reports')}>
            Reports
          </Button>
          
          <IconButton
            size="large"
            edge="end"
            aria-label="account menu"
            aria-controls="menu-appbar"
            aria-haspopup="true"
            onClick={handleMenuOpen}
            color="inherit"
          >
            <Avatar sx={{ bgcolor: 'primary.main' }}>
              {user?.username?.charAt(0).toUpperCase()}
            </Avatar>
          </IconButton>
          
          <Menu
            id="menu-appbar"
            anchorEl={anchorEl}
            anchorOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            keepMounted
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
          >
            <MenuItem onClick={() => { handleMenuClose(); handleNavigation('/settings'); }}>
              <Settings sx={{ mr: 1 }} />
              Settings
            </MenuItem>
            <MenuItem onClick={handleLogout}>
              <ExitToApp sx={{ mr: 1 }} />
              Logout
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Welcome Section */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" gutterBottom>
            {getWelcomeMessage()}, {user?.first_name || user?.username}
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Welcome to your OSINT command center
          </Typography>
        </Box>

        {/* Statistics Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {/* Investigations Overview */}
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Investigation sx={{ color: 'primary.main', mr: 1 }} />
                  <Typography variant="h6">Investigations</Typography>
                </Box>
                <Typography variant="h4" color="primary">
                  {dashboardStats?.total_investigations || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total investigations
                </Typography>
                <Box sx={{ mt: 1 }}>
                  <Chip 
                    label={`${dashboardStats?.active_investigations || 0} Active`}
                    size="small"
                    color="success"
                    sx={{ mr: 1 }}
                  />
                  <Chip 
                    label={`${dashboardStats?.completed_investigations || 0} Complete`}
                    size="small"
                    color="primary"
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* OSINT Operations */}
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Assessment sx={{ color: 'secondary.main', mr: 1 }} />
                  <Typography variant="h6">Operations</Typography>
                </Box>
                <Typography variant="h4" color="secondary">
                  {osintStats?.total_operations || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  OSINT operations
                </Typography>
                <Box sx={{ mt: 1 }}>
                  <Chip 
                    label={`${osintStats?.success_rate || 0}% Success`}
                    size="small"
                    color={osintStats && osintStats.success_rate > 80 ? 'success' : 'warning'}
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Success Rate */}
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <TrendingUp sx={{ color: 'success.main', mr: 1 }} />
                  <Typography variant="h6">Success Rate</Typography>
                </Box>
                <Typography variant="h4" color="success.main">
                  {osintStats?.success_rate?.toFixed(1) || '0.0'}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Operation success rate
                </Typography>
                <Box sx={{ mt: 1, display: 'flex', alignItems: 'center' }}>
                  <CheckCircle sx={{ fontSize: 16, color: 'success.main', mr: 0.5 }} />
                  <Typography variant="caption">
                    {osintStats?.completed_operations || 0} completed
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Status Overview */}
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Schedule sx={{ color: 'warning.main', mr: 1 }} />
                  <Typography variant="h6">Status</Typography>
                </Box>
                <Typography variant="h4" color="text.primary">
                  Active
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  System status
                </Typography>
                <Box sx={{ mt: 1 }}>
                  <Chip 
                    label="Tor Connected"
                    size="small"
                    color="success"
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Quick Actions */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Quick Actions
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Button
                      fullWidth
                      variant="outlined"
                      onClick={() => handleNavigation('/investigations')}
                      startIcon={<Investigation />}
                    >
                      New Investigation
                    </Button>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Button
                      fullWidth
                      variant="outlined"
                      onClick={() => handleNavigation('/osint')}
                      startIcon={<Assessment />}
                    >
                      Run OSINT
                    </Button>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Button
                      fullWidth
                      variant="outlined"
                      onClick={() => handleNavigation('/reports')}
                      startIcon={<Assessment />}
                    >
                      Generate Report
                    </Button>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Button
                      fullWidth
                      variant="outlined"
                      onClick={() => handleNavigation('/settings')}
                      startIcon={<Settings />}
                    >
                      Settings
                    </Button>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Module Usage
                </Typography>
                {osintStats?.module_usage && Object.keys(osintStats.module_usage).length > 0 ? (
                  <Box>
                    {Object.entries(osintStats.module_usage).map(([module, count]) => (
                      <Box key={module} sx={{ mb: 1 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                          <Typography variant="body2">{module.toUpperCase()}</Typography>
                          <Typography variant="body2">{count}</Typography>
                        </Box>
                      </Box>
                    ))}
                  </Box>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    No OSINT operations yet. Start an investigation to see module usage statistics.
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default Dashboard;