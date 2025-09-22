import axios from 'axios';
import type { ApiError } from '@/types/api';

const apiClient = axios.create({
  baseURL: (import.meta as any).env.VITE_API_BASE_URL || '/api/v1',
  timeout: 60000, // Reduzido para 1 minuto (a detecção de marcador ajuda)
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available from Zustand store
    try {
      const authData = localStorage.getItem('auth-storage');
      if (authData) {
        const parsed = JSON.parse(authData);
        const token = parsed.state?.token;
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      }
    } catch (error) {
      // Ignore parsing errors
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Enhanced error logging
    console.error('🔍 API CLIENT INTERCEPTOR ERROR:', {
      message: error.message,
      code: error.code,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      config: error.config,
      stack: error.stack
    });

    if (error.response?.status === 401) {
      // Handle unauthorized - clear auth store
      localStorage.removeItem('auth-storage');
      window.location.href = '/login';
    }

    // Transform error to consistent format
    const apiError: ApiError = {
      message: error.response?.data?.message || error.message || 'Unknown error',
      code: error.response?.data?.code || error.code || 'UNKNOWN_ERROR',
      details: error.response?.data?.details || error.response?.data,
    };

    return Promise.reject(apiError);
  }
);

export default apiClient;