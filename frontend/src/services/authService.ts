import apiClient from './apiClient';
import type { User, LoginCredentials, RegisterData, AuthResponse } from '@/types/auth';

export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await apiClient.post('/login/json', {
      username: credentials.username,
      password: credentials.password,
    });
    return response.data;
  },

  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await apiClient.post('/register', data);
    return response.data;
  },

  async refreshToken(): Promise<{ access_token: string; token_type: string }> {
    const response = await apiClient.post('/refresh');
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get('/me');
    return response.data;
  },

  async logout(): Promise<void> {
    await apiClient.post('/logout');
  },
};