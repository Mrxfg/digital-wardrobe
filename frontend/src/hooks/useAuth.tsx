import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react';
import { api, setAuthToken, getAuthToken, setOnUnauthorized } from '../services/api';

interface User {
  id: number;
  telegram_id: string;
  username: string | null;
  first_name: string | null;
  avatar_url: string | null;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isTelegram: boolean;
  error: string | null;
  login: (initData: string) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children, initData: telegramInitData, isTelegram }: { children: ReactNode; initData: string; isTelegram: boolean }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(getAuthToken());
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const logout = useCallback(() => {
    setAuthToken(null);
    setToken(null);
    setUser(null);
  }, []);

  // Register 401 handler
  useEffect(() => {
    setOnUnauthorized(logout);
  }, [logout]);

  // On mount: validate existing token or auto-login via Telegram
  useEffect(() => {
    const storedToken = getAuthToken();

    if (storedToken) {
      // Validate existing token
      api.get<User>('/auth/me')
        .then((userData) => {
          setUser(userData);
          setToken(storedToken);
        })
        .catch(() => {
          // Token invalid — clear it
          setAuthToken(null);
          setToken(null);
          // Auto-login via Telegram if available
          if (telegramInitData) {
            return performLogin(telegramInitData);
          }
        })
        .finally(() => setIsLoading(false));
    } else if (telegramInitData) {
      // No token but we have Telegram initData — auto-login
      performLogin(telegramInitData).finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const performLogin = async (initData: string) => {
    try {
      const result = await api.post<{ access_token: string; token_type: string }>('/auth/telegram-webapp', {
        init_data: initData,
      });
      setAuthToken(result.access_token);
      setToken(result.access_token);

      // Fetch user info
      const userData = await api.get<User>('/auth/me');
      setUser(userData);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Authentication failed');
      setAuthToken(null);
      setToken(null);
    }
  };

  const login = async (initData: string) => {
    setIsLoading(true);
    setError(null);
    await performLogin(initData);
    setIsLoading(false);
  };

  const clearError = () => setError(null);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user && !!token,
        isLoading,
        isTelegram,
        error,
        login,
        logout,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
