import { apiRequest } from './api';

export const ragApi = {
  /**
   * Perform vector similarity search on uploaded UPSC knowledge base
   */
  async search(query, topK = null, filters = null) {
    return apiRequest('/rag/search', {
      method: 'POST',
      body: JSON.stringify({
        query,
        top_k: topK,
        filters,
      }),
    });
  },
};
