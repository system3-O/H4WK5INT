import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
} from '@mui/material';
import {
  Search,
  Assessment,
  Security,
  Public,
  Image,
  People,
  TrendingUp,
  PlayArrow,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    totalInvestigations: 12,
    activeInvestigations: 3,
    completedInvestigations: 9,
    totalResults: 1247,
  });

  const moduleStats = [
    { name: 'SOCMINT', results: 450, color: '#8884d8' },
    { name: 'HUMINT', results: 320, color: '#82ca9d' },
    { name: 'IMINT', results: 180, color: '#ffc658' },
    { name: 'TECHINT', results: 210, color: '#ff7300' },
    { name: 'GEOINT', results: 87, color: '#8dd1e1' },
  ];

  const recentActivity = [
    { id: 1, type: 'SOCMINT', target: 'john.doe@example.com', status: 'completed', time: '2 hours ago' },
    { id: 2, type: 'TECHINT', target: 'example.com', status: 'running', time: '4 hours ago' },
    { id: 3, type: 'HUMINT', target: 'Jane Smith', status: 'completed', time: '1 day ago' },
    { id: 4, type: 'IMINT', target: 'photo.jpg', status: 'completed', time: '2 days ago' },
  ];

  const osintModules = [
    { name: 'SOCMINT', icon: <People />, description: 'Social Media Intelligence', color: '#1976d2' },
    { name: 'HUMINT', icon: <Security />, description: 'Human Intelligence', color: '#388e3c' },
    { name: 'IMINT', icon: <Image />, description: 'Image Intelligence', color: '#f57c00' },
    { name: 'TECHINT', icon: <Public />, description: 'Technical Intelligence', color: '#7b1fa2' },
    { name: 'GEOINT', icon: <Public />, description: 'Geographic Intelligence', color: '#c2185b' },
    { name: 'WEBINT', icon: <Search />, description: 'Web Intelligence', color: '#0288d1' },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'running':
        return 'warning';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        OSINT Dashboard
      </Typography>
      <Typography variant="subtitle1" color="textSecondary" gutterBottom>
        Welcome to H4WK5INT - Your comprehensive OSINT platform
      </Typography>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Search sx={{ mr: 2, color: 'primary.main' }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Investigations
                  </Typography>
                  <Typography variant="h4">
                    {stats.totalInvestigations}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <PlayArrow sx={{ mr: 2, color: 'warning.main' }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Active Investigations
                  </Typography>
                  <Typography variant="h4">
                    {stats.activeInvestigations}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Assessment sx={{ mr: 2, color: 'success.main' }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Completed
                  </Typography>
                  <Typography variant="h4">
                    {stats.completedInvestigations}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <TrendingUp sx={{ mr: 2, color: 'info.main' }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Results
                  </Typography>
                  <Typography variant="h4">
                    {stats.totalResults}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* OSINT Modules */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                OSINT Modules
              </Typography>
              <Grid container spacing={2}>
                {osintModules.map((module) => (
                  <Grid item xs={12} sm={6} key={module.name}>
                    <Card variant="outlined" sx={{ cursor: 'pointer', '&:hover': { bgcolor: 'action.hover' } }}>
                      <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <Avatar sx={{ bgcolor: module.color, width: 32, height: 32, mr: 1 }}>
                            {module.icon}
                          </Avatar>
                          <Typography variant="subtitle2">
                            {module.name}
                          </Typography>
                        </Box>
                        <Typography variant="caption" color="textSecondary">
                          {module.description}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
              <Button
                variant="contained"
                fullWidth
                sx={{ mt: 2 }}
                onClick={() => navigate('/investigations/new')}
              >
                Start New Investigation
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Module Statistics Chart */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Results by Module
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={moduleStats}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="results" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Activity
              </Typography>
              <List>
                {recentActivity.map((activity) => (
                  <ListItem key={activity.id} divider>
                    <ListItemIcon>
                      <Avatar sx={{ width: 32, height: 32 }}>
                        {activity.type.charAt(0)}
                      </Avatar>
                    </ListItemIcon>
                    <ListItemText
                      primary={`${activity.type} investigation: ${activity.target}`}
                      secondary={activity.time}
                    />
                    <Chip
                      label={activity.status}
                      color={getStatusColor(activity.status)}
                      size="small"
                    />
                  </ListItem>
                ))}
              </List>
              <Button
                variant="outlined"
                fullWidth
                sx={{ mt: 2 }}
                onClick={() => navigate('/investigations')}
              >
                View All Investigations
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;