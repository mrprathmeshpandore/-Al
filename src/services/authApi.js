import { apiRequest } from './api';

export const authApi = {
  /**
   * Register a new user account
   */
  async register(email, fullName, password) {
    return apiRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        email,
        full_name: fullName,
        password,
      }),
    });
  },

  /**
   * Authenticate user credentials and return token
   */
  async login(email, password) {
    return apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({
        email,
        password,
      }),
    });
  },

  /**
   * Authenticate user with Google OAuth credential
   */
  async googleLogin(credential) {
    return apiRequest('/auth/google', {
      method: 'POST',
      body: JSON.stringify({
        credential,
      }),
    });
  },

  /**
   * Fetch current logged in user details using JWT
   */
  async getMe() {
    return apiRequest('/auth/me', {
      method: 'GET',
    });
  },

  /**
   * Store auth token in localStorage
   */
  setToken(token) {
    if (token) {
      localStorage.setItem('prashasak_auth_token', token);
    }
  },

  /**
   * Retrieve auth token from localStorage
   */
  getToken() {
    return localStorage.getItem('prashasak_auth_token');
  },

  /**
   * Remove stored token and user info
   */
  removeToken() {
    localStorage.removeItem('prashasak_auth_token');
    localStorage.removeItem('prashasak_user');
  },
};
