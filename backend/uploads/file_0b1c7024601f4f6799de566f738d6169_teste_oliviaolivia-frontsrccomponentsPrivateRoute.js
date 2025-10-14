import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '../context/AuthContext';

const PrivateRoute = ({ children }) => {
  const { isAuthenticated, loading, isLoggingOut } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !isAuthenticated && !isLoggingOut) {
      router.push('/');
    }
  }, [isAuthenticated, loading, isLoggingOut]);

  if (loading) return null;
  if (!isAuthenticated) return null;

  return children;
};

export default PrivateRoute;
