import apiClient from './apiClient';
import type { User, LoginCredentials, RegisterData, AuthResponse } from '@/types/auth';

export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await apiClient.post('/v1/login', new URLSearchParams({
      username: credentials.username,
      password: credentials.password,
    }), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await apiClient.post('/v1/register', data);
    return response.data;
  },

  async refreshToken(): Promise<{ access_token: string; token_type: string }> {
    const response = await apiClient.post('/v1/refresh');
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get('/v1/me');
    return response.data;
  },

  async logout(): Promise<void> {
    await apiClient.post('/v1/logout');
  },
};