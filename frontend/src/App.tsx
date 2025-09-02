import React, { useEffect, useState } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Box, CircularProgress, Alert, Snackbar } from '@mui/material';

// Components
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import Investigation from './components/Investigation';
import OSINTModules from './components/OSINTModules';
import ReportViewer from './components/ReportViewer';
import Settings from './components/Settings';

// Services
import AuthService from './services/auth';
import StorageService from './services/storage';

// Types
interface AppNotification {
  message: string;
  severity: 'success' | 'error' | 'warning' | 'info';
  open: boolean;
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [notification, setNotification] = useState<AppNotification>({
    message: '',
    severity: 'info',
    open: false,
  });

  const location = useLocation();

  useEffect(() => {
    // Initialize auth service
    AuthService.initStorageListener();
    
    // Check authentication status
    const checkAuth = async () => {
      try {
        if (AuthService.isAuthenticated()) {
          // Check if token needs refresh
          if (AuthService.shouldRefreshToken()) {
            await AuthService.refreshProfile();
          }
          setIsAuthenticated(true);
        } else {
          setIsAuthenticated(false);
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        setIsAuthenticated(false);
        // Clear any invalid tokens
        await AuthService.logout();
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();

    // Cleanup on unmount
    return () => {
      AuthService.cleanup();
    };
  }, []);

  // Handle login
  const handleLogin = async (username: string, password: string) => {
    try {
      await AuthService.login(username, password);
      setIsAuthenticated(true);
      showNotification('Login successful!', 'success');
    } catch (error: any) {
      showNotification(error.message || 'Login failed', 'error');
      throw error;
    }
  };

  // Handle register
  const handleRegister = async (userData: {
    username: string;
    email: string;
    password: string;
    first_name?: string;
    last_name?: string;
  }) => {
    try {
      await AuthService.register(userData);
      setIsAuthenticated(true);
      showNotification('Registration successful!', 'success');
    } catch (error: any) {
      showNotification(error.message || 'Registration failed', 'error');
      throw error;
    }
  };

  // Handle logout
  const handleLogout = async () => {
    try {
      await AuthService.logout();
      setIsAuthenticated(false);
      showNotification('Logged out successfully', 'info');
    } catch (error: any) {
      console.error('Logout error:', error);
      // Force logout even if API call fails
      setIsAuthenticated(false);
    }
  };

  // Show notification
  const showNotification = (message: string, severity: AppNotification['severity']) => {
    setNotification({
      message,
      severity,
      open: true,
    });
  };

  // Close notification
  const handleCloseNotification = () => {
    setNotification(prev => ({ ...prev, open: false }));
  };

  // Loading screen
  if (isLoading) {
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

  // Protected route wrapper
  const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    if (!isAuthenticated) {
      return <Navigate to="/login" state={{ from: location }} replace />;
    }
    return <>{children}</>;
  };

  // Public route wrapper (redirect if authenticated)
  const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    if (isAuthenticated) {
      return <Navigate to="/dashboard" replace />;
    }
    return <>{children}</>;
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <Routes>
        {/* Public routes */}
        <Route
          path="/login"
          element={
            <PublicRoute>
              <Login onLogin={handleLogin} />
            </PublicRoute>
          }
        />
        <Route
          path="/register"
          element={
            <PublicRoute>
              <Register onRegister={handleRegister} />
            </PublicRoute>
          }
        />

        {/* Protected routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard onLogout={handleLogout} showNotification={showNotification} />
            </ProtectedRoute>
          }
        />
        <Route
          path="/investigations"
          element={
            <ProtectedRoute>
              <Investigation onLogout={handleLogout} showNotification={showNotification} />
            </ProtectedRoute>
          }
        />
        <Route
          path="/investigations/:id"
          element={
            <ProtectedRoute>
              <Investigation onLogout={handleLogout} showNotification={showNotification} />
            </ProtectedRoute>
          }
        />
        <Route
          path="/osint"
          element={
            <ProtectedRoute>
              <OSINTModules onLogout={handleLogout} showNotification={showNotification} />
            </ProtectedRoute>
          }
        />
        <Route
          path="/reports"
          element={
            <ProtectedRoute>
              <ReportViewer onLogout={handleLogout} showNotification={showNotification} />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <Settings onLogout={handleLogout} showNotification={showNotification} />
            </ProtectedRoute>
          }
        />

        {/* Default route */}
        <Route
          path="/"
          element={
            isAuthenticated ? (
              <Navigate to="/dashboard" replace />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        {/* Catch all route */}
        <Route
          path="*"
          element={
            isAuthenticated ? (
              <Navigate to="/dashboard" replace />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
      </Routes>

      {/* Global notification snackbar */}
      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={handleCloseNotification}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <Alert
          onClose={handleCloseNotification}
          severity={notification.severity}
          sx={{ width: '100%' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default App;