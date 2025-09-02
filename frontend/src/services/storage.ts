class StorageService {
  // LocalStorage helpers
  setItem(key: string, value: any): void {
    try {
      const serializedValue = JSON.stringify(value);
      localStorage.setItem(key, serializedValue);
    } catch (error) {
      console.error('Error storing item in localStorage:', error);
    }
  }

  getItem<T>(key: string, defaultValue?: T): T | null {
    try {
      const serializedValue = localStorage.getItem(key);
      if (serializedValue === null) {
        return defaultValue || null;
      }
      return JSON.parse(serializedValue);
    } catch (error) {
      console.error('Error retrieving item from localStorage:', error);
      return defaultValue || null;
    }
  }

  removeItem(key: string): void {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error('Error removing item from localStorage:', error);
    }
  }

  clear(): void {
    try {
      localStorage.clear();
    } catch (error) {
      console.error('Error clearing localStorage:', error);
    }
  }

  // SessionStorage helpers
  setSessionItem(key: string, value: any): void {
    try {
      const serializedValue = JSON.stringify(value);
      sessionStorage.setItem(key, serializedValue);
    } catch (error) {
      console.error('Error storing item in sessionStorage:', error);
    }
  }

  getSessionItem<T>(key: string, defaultValue?: T): T | null {
    try {
      const serializedValue = sessionStorage.getItem(key);
      if (serializedValue === null) {
        return defaultValue || null;
      }
      return JSON.parse(serializedValue);
    } catch (error) {
      console.error('Error retrieving item from sessionStorage:', error);
      return defaultValue || null;
    }
  }

  removeSessionItem(key: string): void {
    try {
      sessionStorage.removeItem(key);
    } catch (error) {
      console.error('Error removing item from sessionStorage:', error);
    }
  }

  clearSession(): void {
    try {
      sessionStorage.clear();
    } catch (error) {
      console.error('Error clearing sessionStorage:', error);
    }
  }

  // App-specific helpers
  getThemeMode(): 'light' | 'dark' {
    return this.getItem('theme_mode', 'dark');
  }

  setThemeMode(mode: 'light' | 'dark'): void {
    this.setItem('theme_mode', mode);
  }

  getAppSettings(): any {
    return this.getItem('app_settings', {
      notifications: true,
      autoRefresh: true,
      refreshInterval: 30,
      defaultTorUsage: true,
    });
  }

  setAppSettings(settings: any): void {
    this.setItem('app_settings', settings);
  }

  // Investigation-specific helpers
  getRecentInvestigations(): string[] {
    return this.getItem('recent_investigations', []);
  }

  addRecentInvestigation(investigationId: string): void {
    const recent = this.getRecentInvestigations();
    const filtered = recent.filter(id => id !== investigationId);
    filtered.unshift(investigationId);
    
    // Keep only last 10 recent investigations
    const updated = filtered.slice(0, 10);
    this.setItem('recent_investigations', updated);
  }

  // Search history helpers
  getSearchHistory(module: string): string[] {
    return this.getItem(`search_history_${module}`, []);
  }

  addSearchHistory(module: string, query: string): void {
    const history = this.getSearchHistory(module);
    const filtered = history.filter(q => q !== query);
    filtered.unshift(query);
    
    // Keep only last 20 searches per module
    const updated = filtered.slice(0, 20);
    this.setItem(`search_history_${module}`, updated);
  }

  clearSearchHistory(module?: string): void {
    if (module) {
      this.removeItem(`search_history_${module}`);
    } else {
      // Clear all search history
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.startsWith('search_history_')) {
          this.removeItem(key);
        }
      });
    }
  }

  // Form data helpers (for unsaved forms)
  saveFormData(formId: string, data: any): void {
    this.setSessionItem(`form_data_${formId}`, {
      data,
      timestamp: Date.now(),
    });
  }

  getFormData(formId: string): any {
    const stored = this.getSessionItem(`form_data_${formId}`);
    
    if (!stored) return null;
    
    // Remove form data older than 1 hour
    const oneHour = 60 * 60 * 1000;
    if (Date.now() - stored.timestamp > oneHour) {
      this.removeSessionItem(`form_data_${formId}`);
      return null;
    }
    
    return stored.data;
  }

  clearFormData(formId: string): void {
    this.removeSessionItem(`form_data_${formId}`);
  }

  // Cache helpers for API responses
  setCacheItem(key: string, data: any, ttlMinutes: number = 5): void {
    const cacheData = {
      data,
      timestamp: Date.now(),
      ttl: ttlMinutes * 60 * 1000,
    };
    this.setSessionItem(`cache_${key}`, cacheData);
  }

  getCacheItem(key: string): any {
    const cached = this.getSessionItem(`cache_${key}`);
    
    if (!cached) return null;
    
    // Check if cache is expired
    if (Date.now() - cached.timestamp > cached.ttl) {
      this.removeSessionItem(`cache_${key}`);
      return null;
    }
    
    return cached.data;
  }

  clearCache(): void {
    const keys = Object.keys(sessionStorage);
    keys.forEach(key => {
      if (key.startsWith('cache_')) {
        this.removeSessionItem(key);
      }
    });
  }

  // Utility methods
  getStorageSize(): { localStorage: number; sessionStorage: number } {
    let localStorageSize = 0;
    let sessionStorageSize = 0;

    // Calculate localStorage size
    for (let key in localStorage) {
      if (localStorage.hasOwnProperty(key)) {
        localStorageSize += localStorage[key].length + key.length;
      }
    }

    // Calculate sessionStorage size
    for (let key in sessionStorage) {
      if (sessionStorage.hasOwnProperty(key)) {
        sessionStorageSize += sessionStorage[key].length + key.length;
      }
    }

    return {
      localStorage: localStorageSize,
      sessionStorage: sessionStorageSize,
    };
  }

  isStorageAvailable(): { localStorage: boolean; sessionStorage: boolean } {
    let localStorageAvailable = false;
    let sessionStorageAvailable = false;

    try {
      const testKey = '__storage_test__';
      localStorage.setItem(testKey, 'test');
      localStorage.removeItem(testKey);
      localStorageAvailable = true;
    } catch (e) {
      localStorageAvailable = false;
    }

    try {
      const testKey = '__storage_test__';
      sessionStorage.setItem(testKey, 'test');
      sessionStorage.removeItem(testKey);
      sessionStorageAvailable = true;
    } catch (e) {
      sessionStorageAvailable = false;
    }

    return {
      localStorage: localStorageAvailable,
      sessionStorage: sessionStorageAvailable,
    };
  }
}

export default new StorageService();