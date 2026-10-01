import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authApi } from '../services/authApi';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem('prashasak_user');
      return saved ? JSON.parse(saved) : null;
    } catch (e) {
      console.warn('Corrupt user data in localStorage, clearing:', e);
      localStorage.removeItem('prashasak_user');
      return null;
    }
  });
  const [token, setTokenState] = useState(() => authApi.getToken());
  const [loading, setLoading] = useState(true);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [authModalMode, setAuthModalMode] = useState('login'); // 'login' | 'register'

  // Initialize Auth State from Token
  useEffect(() => {
    let isMounted = true;
    async function initAuth() {
      const storedToken = authApi.getToken();
      if (storedToken) {
        try {
          const userData = await authApi.getMe();
          if (isMounted) {
            setUser(userData);
            localStorage.setItem('prashasak_user', JSON.stringify(userData));
          }
        } catch (error) {
          console.warn('Invalid or expired auth session:', error);
          authApi.removeToken();
          if (isMounted) {
            setUser(null);
            setTokenState(null);
          }
        }
      }
      if (isMounted) {
        setLoading(false);
      }
    }

    initAuth();

    // Listener for unauthorized 401 events
    const handleUnauthorized = () => {
      setUser(null);
      setTokenState(null);
      setIsAuthModalOpen(true);
    };

    window.addEventListener('auth_unauthorized', handleUnauthorized);
    return () => {
      isMounted = false;
      window.removeEventListener('auth_unauthorized', handleUnauthorized);
    };
  }, []);

  // Login Action
  const login = async (email, password) => {
    const response = await authApi.login(email, password);
    const { access_token, user: loggedUser } = response;
    authApi.setToken(access_token);
    setTokenState(access_token);
    setUser(loggedUser);
    localStorage.setItem('prashasak_user', JSON.stringify(loggedUser));
    setIsAuthModalOpen(false);
    return response;
  };

  // Register Action
  const register = async (email, fullName, password) => {
    const newUser = await authApi.register(email, fullName, password);
    // Automatically log in after registration
    return await login(email, password);
  };

  // Logout Action
  const logout = useCallback(() => {
    authApi.removeToken();
    setUser(null);
    setTokenState(null);
  }, []);

  // Auth Modal Triggers
  const openAuthModal = (mode = 'login') => {
    setAuthModalMode(mode);
    setIsAuthModalOpen(true);
  };

  const closeAuthModal = () => {
    setIsAuthModalOpen(false);
  };

  const value = {
    user,
    token,
    isAuthenticated: !!user && !!token,
    loading,
    login,
    register,
    logout,
    isAuthModalOpen,
    authModalMode,
    openAuthModal,
    closeAuthModal,
    setAuthModalMode,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
