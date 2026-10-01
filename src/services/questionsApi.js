import { apiRequest } from './api';

export const questionsApi = {
  /**
   * Generate a grounded UPSC interview practice question.
   * @param {Object} payload - { topic, subject, category, difficulty, question_type, top_k }
   */
  async generateQuestion(payload) {
    return apiRequest('/questions/generate', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  /**
   * Generate a DAF-personalized UPSC interview practice question.
   * @param {Object} payload - { source, difficulty, question_type, top_k }
   */
  async generatePersonalizedQuestion(payload) {
    return apiRequest('/questions/generate-personalized', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  /**
   * List authenticated user's practice questions with pagination and filters.
   * @param {Object} [params] - { page, page_size, subject, topic, category, difficulty, question_type, is_personalized, personalization_source }
   */
  async getQuestions(params = {}) {
    const searchParams = new URLSearchParams();
    if (params.page) searchParams.append('page', params.page);
    if (params.page_size) searchParams.append('page_size', params.page_size);
    if (params.subject) searchParams.append('subject', params.subject);
    if (params.topic) searchParams.append('topic', params.topic);
    if (params.category) searchParams.append('category', params.category);
    if (params.difficulty) searchParams.append('difficulty', params.difficulty);
    if (params.question_type) searchParams.append('question_type', params.question_type);
    if (params.is_personalized !== undefined && params.is_personalized !== null) {
      searchParams.append('is_personalized', params.is_personalized);
    }
    if (params.personalization_source) {
      searchParams.append('personalization_source', params.personalization_source);
    }

    const queryString = searchParams.toString();
    const endpoint = queryString ? `/questions?${queryString}` : '/questions';
    return apiRequest(endpoint, { method: 'GET' });
  },

  /**
   * Retrieve a single practice question by ID.
   * @param {string} questionId
   */
  async getQuestion(questionId) {
    return apiRequest(`/questions/${questionId}`, { method: 'GET' });
  },

  /**
   * Delete a single practice question by ID.
   * @param {string} questionId
   */
  async deleteQuestion(questionId) {
    return apiRequest(`/questions/${questionId}`, { method: 'DELETE' });
  },
};

export const generateQuestion = questionsApi.generateQuestion;
export const generatePersonalizedQuestion = questionsApi.generatePersonalizedQuestion;
export const getQuestions = questionsApi.getQuestions;
export const getQuestion = questionsApi.getQuestion;
export const deleteQuestion = questionsApi.deleteQuestion;
