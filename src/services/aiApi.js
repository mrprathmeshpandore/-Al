import { apiRequest } from './api';

export const aiApi = {
  /**
   * Send a user query to the RAG grounded answer generation service.
   * @param {string} query - The user's UPSC question string.
   * @param {Object} [options] - Optional settings (top_k, filters).
   * @returns {Promise<Object>} Response containing query, answer, grounded bool, and sources.
   */
  async askAI(query, options = {}) {
    const { top_k = null, filters = null } = options;
    return apiRequest('/ai/ask', {
      method: 'POST',
      body: JSON.stringify({
        query,
        top_k,
        filters,
      }),
    });
  },
};

export const askAI = aiApi.askAI;
