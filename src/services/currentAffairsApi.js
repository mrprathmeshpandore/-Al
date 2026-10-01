import { apiRequest } from './api';

export const currentAffairsApi = {
  /**
   * List current affairs with pagination and filters.
   * @param {Object} [params] - { category, topic, source, search, analysis_status, date_from, date_to, page, page_size }
   */
  async getCurrentAffairs(params = {}) {
    const searchParams = new URLSearchParams();
    if (params.category) searchParams.append('category', params.category);
    if (params.topic) searchParams.append('topic', params.topic);
    if (params.source) searchParams.append('source', params.source);
    if (params.search) searchParams.append('search', params.search);
    if (params.analysis_status) searchParams.append('analysis_status', params.analysis_status);
    if (params.date_from) searchParams.append('date_from', params.date_from);
    if (params.date_to) searchParams.append('date_to', params.date_to);
    if (params.page) searchParams.append('page', params.page);
    if (params.page_size) searchParams.append('page_size', params.page_size);

    const queryString = searchParams.toString();
    const endpoint = queryString ? `/current-affairs?${queryString}` : '/current-affairs';
    return apiRequest(endpoint, { method: 'GET' });
  },

  /**
   * Retrieve a single current affair item by ID or slug.
   * @param {string} id
   */
  async getCurrentAffair(id) {
    return apiRequest(`/current-affairs/${id}`, { method: 'GET' });
  },

  /**
   * Get supported current affairs categories.
   */
  async getCategories() {
    return apiRequest('/current-affairs/categories', { method: 'GET' });
  },

  /**
   * Get distinct current affairs topics.
   */
  async getTopics() {
    return apiRequest('/current-affairs/topics', { method: 'GET' });
  },

  /**
   * Trigger grounded Gemini analysis for a current affair item.
   * @param {string} id
   */
  async analyzeCurrentAffair(id) {
    return apiRequest(`/current-affairs/${id}/analyze`, { method: 'POST' });
  },
};

export const getCurrentAffairs = currentAffairsApi.getCurrentAffairs;
export const getCurrentAffair = currentAffairsApi.getCurrentAffair;
export const getCategories = currentAffairsApi.getCategories;
export const getTopics = currentAffairsApi.getTopics;
export const analyzeCurrentAffair = currentAffairsApi.analyzeCurrentAffair;
