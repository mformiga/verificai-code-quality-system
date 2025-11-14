import React, { useState, useEffect } from 'react';
import { getAuthData, getAuthToken, isAuthenticated } from '@/utils/auth';

const AuthDebug: React.FC = () => {
  const [authData, setAuthData] = useState<any>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isAuth, setIsAuth] = useState<boolean>(false);
  const [localStorageData, setLocalStorageData] = useState<string>('');
  const [directToken, setDirectToken] = useState<string>('');

  const refreshData = () => {
    const data = getAuthData();
    const authToken = getAuthToken();
    const authStatus = isAuthenticated();
    const lsData = localStorage.getItem('auth-storage');
    const direct = localStorage.getItem('auth-token');

    setAuthData(data);
    setToken(authToken);
    setIsAuth(authStatus);
    setLocalStorageData(lsData || 'No data');
    setDirectToken(direct || 'No direct token');
  };

  useEffect(() => {
    refreshData();

    // Auto-refresh every 2 seconds
    const interval = setInterval(refreshData, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="fixed bottom-4 right-4 bg-white border border-gray-300 rounded-lg shadow-lg p-4 z-50 max-w-md">
      <div className="flex justify-between items-center mb-2">
        <h3 className="font-bold text-sm">Auth Debug</h3>
        <button
          onClick={refreshData}
          className="text-xs bg-blue-500 text-white px-2 py-1 rounded"
        >
          Refresh
        </button>
      </div>

      <div className="space-y-2 text-xs">
        <div>
          <strong>Is Authenticated:</strong> {isAuth ? '✅ Yes' : '❌ No'}
        </div>
        <div>
          <strong>Has Token:</strong> {token ? '✅ Yes' : '❌ No'}
        </div>
        <div>
          <strong>Token Length:</strong> {token ? token.length : 0}
        </div>
        <div>
          <strong>Token Source:</strong> {directToken !== 'No direct token' ? 'Direct Storage' : 'Zustand Storage'}
        </div>
        <div>
          <strong>User:</strong> {authData?.user?.username || 'No user'}
        </div>
        <div>
          <strong>Zustand Storage:</strong>
          <pre className="bg-gray-100 p-1 rounded text-xs overflow-x-auto">
            {localStorageData.substring(0, 100)}...
          </pre>
        </div>
        <div>
          <strong>Direct Token:</strong>
          <pre className="bg-gray-100 p-1 rounded text-xs overflow-x-auto">
            {directToken.substring(0, 50)}...
          </pre>
        </div>
      </div>
    </div>
  );
};

export default AuthDebug;