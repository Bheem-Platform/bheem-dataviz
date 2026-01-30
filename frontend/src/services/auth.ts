const API_URL = import.meta.env.VITE_API_URL || '/api/v1';
const PASSPORT_URL = import.meta.env.VITE_BHEEMPASSPORT_URL || 'https://platform.bheem.co.uk/api/v1/auth';
const COMPANY_CODE = import.meta.env.VITE_COMPANY_CODE || 'BHM010';

export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  status: string;
  company_code: string;
  company_name: string | null;
  created_at: string;
}

export interface AuthResponse {
  user: User;
  access_token: string;
  token_type: string;
}

export interface AuthConfig {
  passport_url: string;
  company_code: string;
  oauth_providers: string[];
}

export interface RefreshTokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export const authApi = {
  // Get auth config from backend
  getConfig: async (): Promise<AuthConfig> => {
    const response = await fetch(`${API_URL}/auth/config`);
    if (!response.ok) {
      // Return default config if backend is not available
      return {
        passport_url: PASSPORT_URL,
        company_code: COMPANY_CODE,
        oauth_providers: ['google', 'github'],
      };
    }
    return response.json();
  },

  // Sync user after BheemPassport login
  syncUser: async (accessToken: string): Promise<AuthResponse> => {
    const response = await fetch(`${API_URL}/auth/sync`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ access_token: accessToken }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Sync failed');
    }

    return response.json();
  },

  // Get current user
  getCurrentUser: async (accessToken: string): Promise<User> => {
    const response = await fetch(`${API_URL}/auth/me`, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to get user');
    }

    return response.json();
  },

  // BheemPassport OAuth URL
  getOAuthUrl: (provider: string): string => {
    return `${PASSPORT_URL}/oauth/${provider}?company_code=${COMPANY_CODE}`;
  },

  // Login via Backend -> BheemPassport
  login: async (email: string, password: string): Promise<{ access_token: string; refresh_token: string }> => {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: email,
        password: password,
        company_code: COMPANY_CODE,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    return response.json();
  },

  // Registration via Backend -> BheemPassport
  register: async (email: string, password: string): Promise<{ id: string; username: string; role: string }> => {
    const response = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: email,
        password: password,
        company_code: COMPANY_CODE,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Registration failed');
    }

    return response.json();
  },

  // Refresh access token
  refreshToken: async (refreshToken: string): Promise<RefreshTokenResponse> => {
    const response = await fetch(`${API_URL}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        refresh_token: refreshToken,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Token refresh failed');
    }

    return response.json();
  },
};
