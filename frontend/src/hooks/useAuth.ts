import { useAuthStore } from '@/stores/authStore';

export const useAuth = () => {
  const auth = useAuthStore();

  return {
    user: auth.user,
    token: auth.token,
    isAuthenticated: auth.isAuthenticated,
    isLoading: auth.isLoading,
    login: auth.login,
    register: auth.register,
    logout: auth.logout,
    refreshToken: auth.refreshToken,
  };
};