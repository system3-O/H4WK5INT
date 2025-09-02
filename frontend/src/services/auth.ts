import ApiService from './api';

export interface User {
  id: string;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  last_login?: string;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  message: string;
  user: User;
  access_token: string;
  refresh_token: string;
}

class AuthService {
  private currentUser: User | null = null;

  constructor() {
    // Load user from localStorage on initialization
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        this.currentUser = JSON.parse(storedUser);
      } catch (error) {
        console.error('Error parsing stored user:', error);
        this.logout();
      }
    }
  }

  async login(username: string, password: string): Promise<AuthResponse> {
    try {
      const response = await ApiService.login(username, password);
      const authData: AuthResponse = response.data;

      // Store tokens and user data
      localStorage.setItem('access_token', authData.access_token);
      localStorage.setItem('refresh_token', authData.refresh_token);
      localStorage.setItem('user', JSON.stringify(authData.user));

      this.currentUser = authData.user;

      return authData;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Login failed');
    }
  }

  async register(userData: {
    username: string;
    email: string;
    password: string;
    first_name?: string;
    last_name?: string;
  }): Promise<AuthResponse> {
    try {
      const response = await ApiService.register(userData);
      const authData: AuthResponse = response.data;

      // Store tokens and user data
      localStorage.setItem('access_token', authData.access_token);
      localStorage.setItem('refresh_token', authData.refresh_token);
      localStorage.setItem('user', JSON.stringify(authData.user));

      this.currentUser = authData.user;

      return authData;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Registration failed');
    }
  }

  async logout(): Promise<void> {
    try {
      // Call logout endpoint if user is logged in
      if (this.isAuthenticated()) {
        await ApiService.logout();
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear local storage regardless of API call result
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      this.currentUser = null;
    }
  }

  async refreshProfile(): Promise<User> {
    try {
      const response = await ApiService.getProfile();
      const userData = response.data.user;

      localStorage.setItem('user', JSON.stringify(userData));
      this.currentUser = userData;

      return userData;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to refresh profile');
    }
  }

  async updateProfile(userData: any): Promise<User> {
    try {
      const response = await ApiService.updateProfile(userData);
      const updatedUser = response.data.user;

      localStorage.setItem('user', JSON.stringify(updatedUser));
      this.currentUser = updatedUser;

      return updatedUser;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to update profile');
    }
  }

  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    try {
      await ApiService.changePassword(currentPassword, newPassword);
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to change password');
    }
  }

  isAuthenticated(): boolean {
    const token = localStorage.getItem('access_token');
    const user = localStorage.getItem('user');
    return !!(token && user && this.currentUser);
  }

  getCurrentUser(): User | null {
    return this.currentUser;
  }

  getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }

  getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token');
  }

  isAdmin(): boolean {
    return this.currentUser?.role === 'admin';
  }

  hasRole(role: string): boolean {
    return this.currentUser?.role === role;
  }

  // Token validation
  isTokenExpired(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Date.now() / 1000;
      return payload.exp < currentTime;
    } catch (error) {
      return true;
    }
  }

  shouldRefreshToken(): boolean {
    const token = this.getAccessToken();
    if (!token) return false;

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Date.now() / 1000;
      const timeUntilExpiry = payload.exp - currentTime;
      
      // Refresh if token expires in less than 5 minutes
      return timeUntilExpiry < 300;
    } catch (error) {
      return true;
    }
  }

  // Event handling for logout across tabs
  handleStorageChange = (event: StorageEvent) => {
    if (event.key === 'access_token' && !event.newValue) {
      // Token was removed in another tab, logout this tab too
      this.currentUser = null;
      window.location.href = '/login';
    }
  };

  // Initialize storage event listener
  initStorageListener() {
    window.addEventListener('storage', this.handleStorageChange);
  }

  // Cleanup
  cleanup() {
    window.removeEventListener('storage', this.handleStorageChange);
  }
}

export default new AuthService();