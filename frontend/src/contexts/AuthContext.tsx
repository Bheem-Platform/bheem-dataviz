import { createContext, useContext, useState, useEffect, useCallback, useRef, ReactNode } from 'react';
import { authApi, User } from '../services/auth';

// Storage keys
const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const REMEMBER_ME_KEY = 'remember_me';
const LAST_ACTIVITY_KEY = 'last_activity';

// 30 days in milliseconds
const THIRTY_DAYS_MS = 30 * 24 * 60 * 60 * 1000;

interface AuthContextType {
  user: User | null;
  loading: boolean;
  accessToken: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string, rememberMe?: boolean) => Promise<void>;
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

// Check if session should still be valid based on last activity and remember me setting
function isSessionValid(): boolean {
  const rememberMe = localStorage.getItem(REMEMBER_ME_KEY) === 'true';
  const lastActivity = localStorage.getItem(LAST_ACTIVITY_KEY);

  if (!rememberMe) {
    // If not "remember me", session is valid as long as we have tokens
    return !!localStorage.getItem(ACCESS_TOKEN_KEY);
  }

  if (!lastActivity) {
    return !!localStorage.getItem(ACCESS_TOKEN_KEY);
  }

  // Check if within 30 days of last activity
  const lastActivityTime = parseInt(lastActivity, 10);
  return Date.now() - lastActivityTime < THIRTY_DAYS_MS;
}

// Update last activity timestamp
function updateLastActivity() {
  localStorage.setItem(LAST_ACTIVITY_KEY, Date.now().toString());
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [accessToken, setAccessToken] = useState<string | null>(() => {
    // Check if session is still valid on init
    if (!isSessionValid()) {
      localStorage.removeItem(ACCESS_TOKEN_KEY);
      localStorage.removeItem(REFRESH_TOKEN_KEY);
      localStorage.removeItem(LAST_ACTIVITY_KEY);
      return null;
    }
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  });
  const refreshTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const isRefreshingRef = useRef(false);

  // Clear refresh timeout
  const clearRefreshTimeout = useCallback(() => {
    if (refreshTimeoutRef.current) {
      clearTimeout(refreshTimeoutRef.current);
      refreshTimeoutRef.current = null;
    }
  }, []);

  // Logout function - defined early so it can be used by other callbacks
  const logout = useCallback(() => {
    clearRefreshTimeout();
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(REMEMBER_ME_KEY);
    localStorage.removeItem(LAST_ACTIVITY_KEY);
    setAccessToken(null);
    setUser(null);
  }, [clearRefreshTimeout]);

  // Schedule token refresh - forward declaration to avoid circular dependency
  const scheduleTokenRefreshRef = useRef<((token: string) => void) | null>(null);

  // Refresh access token
  const refreshAccessToken = useCallback(async (): Promise<boolean> => {
    if (isRefreshingRef.current) {
      return false;
    }

    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    if (!refreshToken) {
      console.log('No refresh token available');
      return false;
    }

    // Check if session is still valid (within 30 days)
    if (!isSessionValid()) {
      console.log('Session expired (30 day limit)');
      logout();
      return false;
    }

    isRefreshingRef.current = true;

    try {
      const result = await authApi.refreshToken(refreshToken);

      // Store new tokens
      localStorage.setItem(ACCESS_TOKEN_KEY, result.access_token);
      localStorage.setItem(REFRESH_TOKEN_KEY, result.refresh_token);
      setAccessToken(result.access_token);

      // Update last activity
      updateLastActivity();

      // Schedule next refresh
      if (scheduleTokenRefreshRef.current) {
        scheduleTokenRefreshRef.current(result.access_token);
      }

      isRefreshingRef.current = false;
      return true;
    } catch (error) {
      console.error('Token refresh failed:', error);
      isRefreshingRef.current = false;
      // Only logout if it's a definitive auth error, not a network error
      if (error instanceof Error && !error.message.includes('network')) {
        logout();
      }
      return false;
    }
  }, [logout]);

  // Schedule token refresh
  const scheduleTokenRefresh = useCallback((token: string) => {
    clearRefreshTimeout();

    const expiration = getTokenExpiration(token);
    if (!expiration) {
      console.log('Could not determine token expiration');
      return;
    }

    const now = Date.now();
    const timeUntilExpiry = expiration - now;
    const refreshIn = timeUntilExpiry - REFRESH_THRESHOLD;

    console.log(`Token expires in ${Math.round(timeUntilExpiry / 1000 / 60)} minutes, scheduling refresh in ${Math.round(refreshIn / 1000 / 60)} minutes`);

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

  // Update the ref after scheduleTokenRefresh is defined
  scheduleTokenRefreshRef.current = scheduleTokenRefresh;

  // Handle visibility change - refresh token when user returns to tab
  const handleVisibilityChange = useCallback(() => {
    if (document.visibilityState === 'visible' && accessToken) {
      // User returned to the tab - check if we need to refresh
      const expiration = getTokenExpiration(accessToken);
      if (expiration) {
        const now = Date.now();
        const timeUntilExpiry = expiration - now;

        // If token is expired or about to expire, refresh immediately
        if (timeUntilExpiry <= REFRESH_THRESHOLD) {
          refreshAccessToken();
        } else {
          // Update last activity and reschedule refresh
          updateLastActivity();
          scheduleTokenRefresh(accessToken);
        }
      }
    }
  }, [accessToken, refreshAccessToken, scheduleTokenRefresh]);

  // Load user on mount or token change
  useEffect(() => {
    if (accessToken) {
      loadUser();
      scheduleTokenRefresh(accessToken);
      updateLastActivity();
    } else {
      setLoading(false);
    }

    // Listen for visibility changes to handle tab switching/browser minimize
    document.addEventListener('visibilitychange', handleVisibilityChange);

    // Listen for user activity to extend session
    const activityEvents = ['mousedown', 'keydown', 'touchstart', 'scroll'];
    const handleActivity = () => {
      if (accessToken) {
        updateLastActivity();
      }
    };

    activityEvents.forEach((event) => {
      window.addEventListener(event, handleActivity, { passive: true });
    });

    return () => {
      clearRefreshTimeout();
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      activityEvents.forEach((event) => {
        window.removeEventListener(event, handleActivity);
      });
    };
  }, [accessToken, scheduleTokenRefresh, clearRefreshTimeout, handleVisibilityChange]);

  const loadUser = async () => {
    try {
      const userData = await authApi.getCurrentUser(accessToken!);
      setUser(userData);
    } catch (error: any) {
      console.error('Failed to load user:', error);

      // Check if it's an auth error (401/403) vs network error
      const isAuthError = error?.message?.includes('401') ||
                          error?.message?.includes('403') ||
                          error?.message?.includes('Failed to get user');

      if (isAuthError) {
        // Try to refresh token before giving up
        console.log('Attempting token refresh...');
        const refreshed = await refreshAccessToken();
        if (refreshed) {
          // Retry loading user with new token
          try {
            const newToken = localStorage.getItem(ACCESS_TOKEN_KEY);
            if (newToken) {
              const userData = await authApi.getCurrentUser(newToken);
              setUser(userData);
              return;
            }
          } catch (retryError) {
            console.error('Failed to load user after refresh:', retryError);
          }
        }
        // Only logout if refresh also failed
        logout();
      }
      // For network errors, don't logout - just leave user as null temporarily
    } finally {
      setLoading(false);
    }
  };

  // Traditional login via BheemPassport
  const login = async (email: string, password: string, rememberMe: boolean = true) => {
    // Store remember me preference
    localStorage.setItem(REMEMBER_ME_KEY, rememberMe.toString());

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
    localStorage.setItem(ACCESS_TOKEN_KEY, token);
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
    setAccessToken(token);

    // Update last activity timestamp
    updateLastActivity();

    // Schedule token refresh
    scheduleTokenRefresh(token);

    // Sync user with your backend (creates local user if not exists)
    const syncResult = await authApi.syncUser(token);
    setUser(syncResult.user);
  };

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
