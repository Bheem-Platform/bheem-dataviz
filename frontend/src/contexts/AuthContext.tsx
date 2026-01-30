import { createContext, useContext, useState, useEffect, useCallback, useRef, ReactNode } from 'react';
import { authApi, User } from '../services/auth';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  accessToken: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  socialLogin: (provider: string) => void;
  handleOAuthCallback: (token: string, refreshToken: string) => Promise<void>;
  logout: () => void;
  refreshAccessToken: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | null>(null);

interface AuthProviderProps {
  children: ReactNode;
}

// Parse JWT to get expiration time
function parseJwt(token: string): { exp?: number; [key: string]: any } | null {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (e) {
    console.error('Failed to parse JWT:', e);
    return null;
  }
}

// Get token expiration time in milliseconds
function getTokenExpiration(token: string): number | null {
  const payload = parseJwt(token);
  if (payload?.exp) {
    return payload.exp * 1000; // Convert to milliseconds
  }
  return null;
}

// Time before expiry to refresh (5 minutes in milliseconds)
const REFRESH_THRESHOLD = 5 * 60 * 1000;

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [accessToken, setAccessToken] = useState<string | null>(
    () => localStorage.getItem('access_token')
  );
  const refreshTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const isRefreshingRef = useRef(false);

  // Clear refresh timeout
  const clearRefreshTimeout = useCallback(() => {
    if (refreshTimeoutRef.current) {
      clearTimeout(refreshTimeoutRef.current);
      refreshTimeoutRef.current = null;
    }
  }, []);

  // Refresh access token
  const refreshAccessToken = useCallback(async (): Promise<boolean> => {
    if (isRefreshingRef.current) {
      return false;
    }

    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      return false;
    }

    isRefreshingRef.current = true;

    try {
      const result = await authApi.refreshToken(refreshToken);

      // Store new tokens
      localStorage.setItem('access_token', result.access_token);
      localStorage.setItem('refresh_token', result.refresh_token);
      setAccessToken(result.access_token);

      // Schedule next refresh
      scheduleTokenRefresh(result.access_token);

      isRefreshingRef.current = false;
      return true;
    } catch (error) {
      console.error('Token refresh failed:', error);
      isRefreshingRef.current = false;
      // Refresh failed - logout user
      logout();
      return false;
    }
  }, []);

  // Schedule token refresh
  const scheduleTokenRefresh = useCallback((token: string) => {
    clearRefreshTimeout();

    const expiration = getTokenExpiration(token);
    if (!expiration) {
      return;
    }

    const now = Date.now();
    const timeUntilExpiry = expiration - now;
    const refreshIn = timeUntilExpiry - REFRESH_THRESHOLD;

    if (refreshIn <= 0) {
      // Token is about to expire or already expired, refresh immediately
      refreshAccessToken();
    } else {
      // Schedule refresh
      refreshTimeoutRef.current = setTimeout(() => {
        refreshAccessToken();
      }, refreshIn);
    }
  }, [clearRefreshTimeout, refreshAccessToken]);

  // Load user on mount or token change
  useEffect(() => {
    if (accessToken) {
      loadUser();
      scheduleTokenRefresh(accessToken);
    } else {
      setLoading(false);
    }

    return () => {
      clearRefreshTimeout();
    };
  }, [accessToken, scheduleTokenRefresh, clearRefreshTimeout]);

  const loadUser = async () => {
    try {
      const userData = await authApi.getCurrentUser(accessToken!);
      setUser(userData);
    } catch (error) {
      console.error('Failed to load user:', error);
      // Try to refresh token before giving up
      const refreshed = await refreshAccessToken();
      if (!refreshed) {
        logout();
      }
    } finally {
      setLoading(false);
    }
  };

  // Traditional login via BheemPassport
  const login = async (email: string, password: string) => {
    const data = await authApi.login(email, password);
    await handleAuthSuccess(data.access_token, data.refresh_token);
  };

  // Social login redirect
  const socialLogin = (provider: string) => {
    window.location.href = authApi.getOAuthUrl(provider);
  };

  // Handle OAuth callback
  const handleOAuthCallback = async (token: string, refreshToken: string) => {
    await handleAuthSuccess(token, refreshToken);
  };

  // Common auth success handler
  const handleAuthSuccess = async (token: string, refreshToken: string) => {
    // Store tokens
    localStorage.setItem('access_token', token);
    localStorage.setItem('refresh_token', refreshToken);
    setAccessToken(token);

    // Schedule token refresh
    scheduleTokenRefresh(token);

    // Sync user with your backend (creates local user if not exists)
    const syncResult = await authApi.syncUser(token);
    setUser(syncResult.user);
  };

  const logout = useCallback(() => {
    clearRefreshTimeout();
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setAccessToken(null);
    setUser(null);
  }, [clearRefreshTimeout]);

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        accessToken,
        isAuthenticated: !!user,
        login,
        socialLogin,
        handleOAuthCallback,
        logout,
        refreshAccessToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
