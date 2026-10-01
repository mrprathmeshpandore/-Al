import { apiRequest } from './api';

export const interviewApi = {
  /**
   * Start a new AI UPSC Interview Session.
   * @param {Object} [payload] - { interview_type, total_questions, include_daf_questions, include_current_affairs, include_rag_questions, difficulty, topic, category }
   */
  async startInterview(payload = {}) {
    return apiRequest('/interview/start', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  /**
   * Retrieve active or completed interview session state by ID.
   * @param {string} sessionId
   */
  async getInterviewSession(sessionId) {
    return apiRequest(`/interview/${sessionId}`, { method: 'GET' });
  },

  /**
   * Submit candidate answer for the current session question.
   * @param {string} sessionId
   * @param {Object} payload - { answer_text, answer_duration_seconds }
   */
  async submitInterviewAnswer(sessionId, payload) {
    return apiRequest(`/interview/${sessionId}/answer`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  /**
   * Request next served question in session sequence.
   * @param {string} sessionId
   */
  async getNextInterviewQuestion(sessionId) {
    return apiRequest(`/interview/${sessionId}/next-question`, {
      method: 'POST',
    });
  },

  /**
   * Mark interview session as COMPLETED.
   * @param {string} sessionId
   */
  async completeInterview(sessionId) {
    return apiRequest(`/interview/${sessionId}/complete`, {
      method: 'POST',
    });
  },

  /**
   * Retrieve authenticated user's interview history.
   * @param {Object} [params] - { status, interview_type, page, page_size }
   */
  async getInterviewHistory(params = {}) {
    const searchParams = new URLSearchParams();
    if (params.status) searchParams.append('status', params.status);
    if (params.interview_type) searchParams.append('interview_type', params.interview_type);
    if (params.page) searchParams.append('page', params.page);
    if (params.page_size) searchParams.append('page_size', params.page_size);

    const queryString = searchParams.toString();
    const endpoint = queryString ? `/interview/history?${queryString}` : '/interview/history';
    return apiRequest(endpoint, { method: 'GET' });
  },
  /**
   * Evaluate a submitted candidate answer using AI evaluation engine.
   * @param {string} answerId
   */
  async evaluateInterviewAnswer(answerId) {
    return apiRequest(`/interview/answers/${answerId}/evaluate`, {
      method: 'POST',
    });
  },

  /**
   * Retrieve existing AI evaluation for an answer.
   * @param {string} answerId
   */
  async getInterviewAnswerEvaluation(answerId) {
    return apiRequest(`/interview/answers/${answerId}/evaluation`, {
      method: 'GET',
    });
  },
};

export const startInterview = interviewApi.startInterview;
export const getInterviewSession = interviewApi.getInterviewSession;
export const submitInterviewAnswer = interviewApi.submitInterviewAnswer;
export const getNextInterviewQuestion = interviewApi.getNextInterviewQuestion;
export const completeInterview = interviewApi.completeInterview;
export const getInterviewHistory = interviewApi.getInterviewHistory;
export const evaluateInterviewAnswer = interviewApi.evaluateInterviewAnswer;
export const getInterviewAnswerEvaluation = interviewApi.getInterviewAnswerEvaluation;
