import type { User, LoginCredentials, RegisterData, AuthResponse } from '@/types/auth';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/login/json`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: credentials.username,
          password: credentials.password,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Login failed:', response.status, errorText);
        throw new Error(`Login failed: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },

  async register(data: RegisterData): Promise<AuthResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Register failed:', response.status, errorText);
        throw new Error(`Register failed: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error('Register error:', error);
      throw error;
    }
  },

  async refreshToken(): Promise<{ access_token: string; token_type: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Refresh token failed:', response.status, errorText);
        throw new Error(`Refresh token failed: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error('Refresh token error:', error);
      throw error;
    }
  },

  async getCurrentUser(): Promise<User> {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        throw new Error('No auth token found');
      }

      const response = await fetch(`${API_BASE_URL}/me`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Get current user failed:', response.status, errorText);
        throw new Error(`Get current user failed: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error('Get current user error:', error);
      throw error;
    }
  },

  async logout(): Promise<void> {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        // If no token, just clear localStorage and return
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_data');
        return;
      }

      const response = await fetch(`${API_BASE_URL}/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      // Clear local storage regardless of response
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_data');

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Logout failed:', response.status, errorText);
        // Don't throw error for logout, just log it
        console.warn('Logout request failed but local storage was cleared');
      }
    } catch (error) {
      console.error('Logout error:', error);
      // Clear local storage even if request fails
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_data');
    }
  },
};