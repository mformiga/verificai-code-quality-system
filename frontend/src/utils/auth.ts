/**
 * Authentication utilities for handling JWT tokens
 */

export interface AuthData {
  user: any;
  token: string | null;
  isAuthenticated: boolean;
}

/**
 * Get authentication data from localStorage (Zustand persist storage)
 */
export function getAuthData(): AuthData | null {
  try {
    const authData = localStorage.getItem('auth-storage');
    if (!authData) {
      console.warn('No auth data found in localStorage');
      return null;
    }

    const parsed = JSON.parse(authData);
    if (!parsed.state) {
      console.warn('No state found in auth data');
      return null;
    }

    console.log('Auth data found:', {
      hasToken: !!parsed.state.token,
      isAuthenticated: parsed.state.isAuthenticated,
      user: parsed.state.user?.username || 'No user'
    });

    return parsed.state;
  } catch (error) {
    console.error('Error parsing auth data from localStorage:', error);
    return null;
  }
}

/**
 * Get JWT token from localStorage with multiple fallback strategies
 */
export function getAuthToken(): string | null {
  try {
    // Strategy 1: Try Zustand persist storage
    const authData = localStorage.getItem('auth-storage');
    if (authData) {
      const parsed = JSON.parse(authData);
      if (parsed.state && parsed.state.token) {
        console.log('Token found in Zustand storage');
        return parsed.state.token;
      }
    }

    // Strategy 2: Try direct token storage
    const directToken = localStorage.getItem('auth-token');
    if (directToken) {
      console.log('Token found in direct storage');
      return directToken;
    }

    console.warn('No token found in any storage');
    return null;
  } catch (error) {
    console.error('Error getting token:', error);
    return null;
  }
}

/**
 * Get authorization headers for API requests
 */
export function getAuthHeaders(): Record<string, string> {
  const token = getAuthToken();
  const headers: Record<string, string> = {};

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
    console.log('Auth headers generated with token length:', token.length);
  } else {
    console.warn('No token available for auth headers');
  }

  return headers;
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  const token = getAuthToken();
  const isAuthenticated = !!token;
  console.log('Authentication check:', { hasToken: isAuthenticated });
  return isAuthenticated;
}

/**
 * Store token directly in localStorage as backup
 */
export function storeToken(token: string): void {
  try {
    localStorage.setItem('auth-token', token);
    console.log('Token stored in direct storage');
  } catch (error) {
    console.error('Error storing token:', error);
  }
}

/**
 * Clear authentication data
 */
export function clearAuth(): void {
  localStorage.removeItem('auth-storage');
  localStorage.removeItem('auth-token');
  console.log('Auth data cleared from localStorage');
}