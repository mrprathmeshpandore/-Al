const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

/**
 * Generic API request helper that injects Authorization headers and handles errors cleanly.
 */
export async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem('prashasak_auth_token');

  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const config = {
    ...options,
    headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

  // Handle 401 Unauthorized token expiry
  if (response.status === 401 && token && !endpoint.includes('/auth/login')) {
    localStorage.removeItem('prashasak_auth_token');
    localStorage.removeItem('prashasak_user');
    window.dispatchEvent(new Event('auth_unauthorized'));
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    let errorMessage = `Request failed with status ${response.status}`;
    if (typeof data.detail === 'string') {
      errorMessage = data.detail;
    } else if (Array.isArray(data.detail)) {
      errorMessage = data.detail.map(e => (typeof e === 'object' ? (e.msg || JSON.stringify(e)) : String(e))).join('; ');
    } else if (data.detail && typeof data.detail === 'object') {
      errorMessage = data.detail.msg || data.detail.message || JSON.stringify(data.detail);
    } else if (typeof data.message === 'string') {
      errorMessage = data.message;
    }

    const error = new Error(errorMessage);
    error.status = response.status;
    error.data = data;
    throw error;
  }

  return data;
}
