import { apiRequest } from './api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export const aiApi = {
  /**
   * Send a user query to the RAG grounded answer generation service (Non-streaming).
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

  /**
   * Stream grounded answer tokens and metadata in real-time.
   * @param {string} query - User UPSC question.
   * @param {Function} onMetadata - Callback(meta) invoked when sources/grounded info arrives.
   * @param {Function} onChunk - Callback(textChunk) invoked for each streaming token.
   * @param {Object} [options] - Optional settings (top_k, filters).
   */
  async askAIStream(query, onMetadata, onChunk, options = {}) {
    const token = localStorage.getItem('prashasak_auth_token');
    const { top_k = null, filters = null } = options;

    const response = await fetch(`${API_BASE_URL}/ai/ask/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ query, top_k, filters }),
    });

    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      throw new Error(data.detail || `Request failed with status ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      let currentEvent = null;
      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed.startsWith('event: ')) {
          currentEvent = trimmed.substring(7).trim();
        } else if (trimmed.startsWith('data: ')) {
          const rawData = trimmed.substring(6).trim();
          if (!rawData) continue;
          try {
            const parsed = JSON.parse(rawData);
            if (currentEvent === 'metadata' && onMetadata) {
              onMetadata(parsed);
            } else if (currentEvent === 'token' && onChunk) {
              onChunk(parsed.text || '');
            }
          } catch (e) {
            if (currentEvent === 'token' && onChunk) {
              onChunk(rawData);
            }
          }
        }
      }
    }
  },
};

export const askAI = aiApi.askAI;
export const askAIStream = aiApi.askAIStream;
