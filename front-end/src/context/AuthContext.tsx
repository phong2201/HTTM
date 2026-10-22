import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { LoginResponse, UserData, RegisterData, apiService } from '../services/api';

interface AuthContextType {
  isAuthenticated: boolean;
  user: UserData | null;
  loading: boolean;
  error: string | null;
  login: (username: string, password: string) => Promise<UserData>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<UserData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setLoading(false);
      return;
    }

    apiService.getCurrentUser()
      .then((userData) => {
        localStorage.setItem('current_user', JSON.stringify(userData));
        setUser(userData);
        setIsAuthenticated(true);
      })
      .catch(() => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('token_type');
        localStorage.removeItem('current_user');
        setIsAuthenticated(false);
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const login = async (username: string, password: string): Promise<UserData> => {
    setLoading(true);
    setError(null);
    try {
      const response: LoginResponse = await apiService.login(username, password);
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('token_type', response.token_type);
      const userData = await apiService.getCurrentUser();
      localStorage.setItem('current_user', JSON.stringify(userData));
      setUser(userData);
      setIsAuthenticated(true);
      return userData;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Login failed';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const register = async (data: RegisterData) => {
    setLoading(true);
    setError(null);
    try {
      await apiService.register(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Registration failed';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('token_type');
    localStorage.removeItem('current_user');
    setIsAuthenticated(false);
    setUser(null);
  };

  const clearError = () => setError(null);

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, loading, error, login, register, logout, clearError }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
