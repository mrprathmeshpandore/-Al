import { apiRequest } from './api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export const resourcesApi = {
  /**
   * Upload a PDF file to create a resource and launch document processing
   */
  async uploadPdf(formData) {
    const token = localStorage.getItem('prashasak_auth_token');
    const response = await fetch(`${API_BASE_URL}/resources/upload`, {
      method: 'POST',
      headers: {
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      },
      body: formData,
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(data.detail || 'Failed to upload PDF');
    }
    return data;
  },

  /**
   * Get list of resources with optional filters
   */
  async getResources(params = {}) {
    const query = new URLSearchParams();
    if (params.category) query.append('category', params.category);
    if (params.subject) query.append('subject', params.subject);
    if (params.topic) query.append('topic', params.topic);
    if (params.resource_type) query.append('resource_type', params.resource_type);
    if (params.search) query.append('search', params.search);

    const queryString = query.toString() ? `?${query.toString()}` : '';
    return apiRequest(`/resources${queryString}`, { method: 'GET' });
  },

  /**
   * Get resource categories with dynamic counts
   */
  async getCategories() {
    return apiRequest('/resources/categories', { method: 'GET' });
  },

  /**
   * Get subjects with dynamic resource counts
   */
  async getSubjects() {
    return apiRequest('/resources/subjects', { method: 'GET' });
  },

  /**
   * Get single resource details
   */
  async getResourceDetail(id) {
    return apiRequest(`/resources/${id}`, { method: 'GET' });
  },

  /**
   * Get linked documents for resource
   */
  async getResourceDocuments(id) {
    return apiRequest(`/resources/${id}/documents`, { method: 'GET' });
  },

  /**
   * Add bookmark for a resource
   */
  async addBookmark(resourceId) {
    return apiRequest(`/resources/${resourceId}/bookmark`, { method: 'POST' });
  },

  /**
   * Remove bookmark for a resource
   */
  async removeBookmark(resourceId) {
    return apiRequest(`/resources/${resourceId}/bookmark`, { method: 'DELETE' });
  },

  /**
   * Get user bookmarked resources
   */
  async getBookmarkedResources() {
    return apiRequest('/resources/bookmarked', { method: 'GET' });
  },
};
