import {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback
} from 'react';
import { useRouter } from 'next/router';
import apiClient from '../services/apiClient';
import { decodeJwt, scheduleAutoLogout } from '../services/auth';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [authError, setAuthError] = useState(null);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) setUser(JSON.parse(savedUser));
    setLoading(false);
  }, []);

  const loginWithGovBr = async () => {
    try {
      window.location.href = `${process.env.NEXT_PUBLIC_BACKEND_URL}/auth/govbr/login`;
    } catch (error) {
      console.error('Falha ao iniciar login Gov.br:', error);
    }
  };

  const handleGovBrCallback = useCallback(
    async (code, state) => {
      try {
        const { data } = await apiClient.get('/auth/govbr/callback', {
          params: { code, state }
        });

        if (!data?.access_token)
          throw new Error(data?.message || 'Falha no login');

        sessionStorage.setItem('access_token', data.access_token);
        if (data.session_id)
          sessionStorage.setItem('session_id', data.session_id);
        if (data.expires_at)
          sessionStorage.setItem('expires_at', String(data.expires_at));

        const userUi = {
          sub: data.user.sub, // ID único Gov.br (CPF)
          name: data.user.name ?? null,
          email: data.user.email ?? null,
          email_verified: !!data.user.email_verified,
          picture: data.user.picture ?? null
        };
        localStorage.setItem('user', JSON.stringify(userUi));
        setUser(userUi);

        if (data.expires_at) {
          scheduleAutoLogout(
            Math.floor(data.expires_at / 1000),
            () => {
              sessionStorage.clear();
              localStorage.removeItem('user');
              setUser(null);
              router.replace('/');
            },
            120
          );
        }

        router.push('/arquivos');
      } catch (error) {
        console.error('Callback falhou:', error);
        const msg =
          (error &&
            error.response &&
            error.response.data &&
            error.response.data.message) ||
          error?.message ||
          'Falha no login';
        setAuthError(typeof msg === 'string' ? msg : JSON.stringify(msg));
        router.replace('/');
      }
    },
    [router]
  );

  const logout = async () => {
    try {
      setIsLoggingOut(true);
      const sessionId = sessionStorage.getItem('session_id') || '';

      try {
        await apiClient.get('/auth/govbr/logout', {
          params: { session_id: sessionId }
        });
      } catch (err) {
        console.warn(
          'Falha ao notificar logout no backend:',
          err?.message || err
        );
      }
      sessionStorage.clear();
      localStorage.clear();
      setUser(null);
      const defaultPostLogoutPath = '/auth/govbr/sair';
      const redirectUri =
        process.env.NEXT_PUBLIC_LOGOUT_REDIRECT_URI ||
        (typeof window !== 'undefined'
          ? `${window.location.origin}${defaultPostLogoutPath}`
          : defaultPostLogoutPath);

      const ssoLogout = `https://sso.staging.acesso.gov.br/logout?post_logout_redirect_uri=${encodeURIComponent(
        redirectUri
      )}`;

      if (typeof window !== 'undefined') {
        window.location.href = ssoLogout;
      } else {
        router.push('/');
      }
    } catch (e) {
      setIsLoggingOut(false);
      router.push('/');
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loginWithGovBr,
        handleGovBrCallback,
        logout,
        authError,
        clearAuthError: () => setAuthError(null),
        isAuthenticated: !!user,
        loading,
        isLoggingOut
      }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
