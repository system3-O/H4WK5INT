import axios, { AxiosInstance, AxiosResponse } from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    });

    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor to handle auth errors
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Try to refresh token
          const refreshToken = localStorage.getItem('refresh_token');
          if (refreshToken) {
            try {
              const response = await this.api.post('/auth/refresh', {}, {
                headers: { Authorization: `Bearer ${refreshToken}` }
              });
              
              localStorage.setItem('access_token', response.data.access_token);
              
              // Retry original request
              error.config.headers.Authorization = `Bearer ${response.data.access_token}`;
              return this.api.request(error.config);
            } catch (refreshError) {
              // Refresh failed, logout user
              localStorage.removeItem('access_token');
              localStorage.removeItem('refresh_token');
              localStorage.removeItem('user');
              window.location.href = '/login';
            }
          } else {
            // No refresh token, logout user
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user');
            window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async login(username: string, password: string): Promise<AxiosResponse> {
    return this.api.post('/auth/login', { username, password });
  }

  async register(userData: {
    username: string;
    email: string;
    password: string;
    first_name?: string;
    last_name?: string;
  }): Promise<AxiosResponse> {
    return this.api.post('/auth/register', userData);
  }

  async logout(): Promise<AxiosResponse> {
    return this.api.post('/auth/logout');
  }

  async getProfile(): Promise<AxiosResponse> {
    return this.api.get('/profile');
  }

  async updateProfile(userData: any): Promise<AxiosResponse> {
    return this.api.put('/auth/update-profile', userData);
  }

  async changePassword(currentPassword: string, newPassword: string): Promise<AxiosResponse> {
    return this.api.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    });
  }

  // Investigation endpoints
  async getInvestigations(params?: any): Promise<AxiosResponse> {
    return this.api.get('/investigations', { params });
  }

  async getInvestigation(id: string): Promise<AxiosResponse> {
    return this.api.get(`/investigations/${id}`);
  }

  async createInvestigation(data: {
    name: string;
    description?: string;
    target?: string;
    priority?: string;
    tags?: string[];
  }): Promise<AxiosResponse> {
    return this.api.post('/investigations', data);
  }

  async updateInvestigation(id: string, data: any): Promise<AxiosResponse> {
    return this.api.put(`/investigations/${id}`, data);
  }

  async deleteInvestigation(id: string): Promise<AxiosResponse> {
    return this.api.delete(`/investigations/${id}`);
  }

  async getInvestigationSummary(id: string): Promise<AxiosResponse> {
    return this.api.get(`/investigations/${id}/summary`);
  }

  async getInvestigationResults(id: string, params?: any): Promise<AxiosResponse> {
    return this.api.get(`/investigations/${id}/results`, { params });
  }

  // OSINT endpoints
  async runPeopleIntel(data: {
    operation: string;
    query: string;
    investigation_id?: string;
    platforms?: string[];
    country_code?: string;
    use_tor?: boolean;
  }): Promise<AxiosResponse> {
    return this.api.post('/osint/peopint', data);
  }

  async runDomainIntel(data: {
    operation: string;
    domain: string;
    investigation_id?: string;
    wordlist?: string[];
    ports?: number[];
    port?: number;
    use_tor?: boolean;
  }): Promise<AxiosResponse> {
    return this.api.post('/osint/domain', data);
  }

  async getOsintResult(id: string): Promise<AxiosResponse> {
    return this.api.get(`/osint/results/${id}`);
  }

  async getOsintResults(params?: any): Promise<AxiosResponse> {
    return this.api.get('/osint/results', { params });
  }

  async getOsintModules(): Promise<AxiosResponse> {
    return this.api.get('/osint/modules');
  }

  async getOsintStatistics(): Promise<AxiosResponse> {
    return this.api.get('/osint/statistics');
  }

  async getTorStatus(): Promise<AxiosResponse> {
    return this.api.get('/osint/tor/status');
  }

  // Report endpoints
  async generateReport(data: {
    investigation_id: string;
    report_type: string;
    name?: string;
  }): Promise<AxiosResponse> {
    return this.api.post('/reports/generate', data);
  }

  async getReports(params?: any): Promise<AxiosResponse> {
    return this.api.get('/reports', { params });
  }

  async getReport(id: string): Promise<AxiosResponse> {
    return this.api.get(`/reports/${id}`);
  }

  async downloadReport(id: string): Promise<AxiosResponse> {
    return this.api.get(`/reports/${id}/download`, {
      responseType: 'blob'
    });
  }

  async deleteReport(id: string): Promise<AxiosResponse> {
    return this.api.delete(`/reports/${id}`);
  }

  // Health check
  async healthCheck(): Promise<AxiosResponse> {
    return this.api.get('/health');
  }

  async getApiInfo(): Promise<AxiosResponse> {
    return this.api.get('/info');
  }
}

export default new ApiService();