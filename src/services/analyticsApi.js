import { apiRequest } from './api';

export const analyticsApi = {
  /**
   * Retrieve combined analytics dashboard payload for Progress page.
   */
  async getAnalyticsDashboard() {
    return apiRequest('/analytics/dashboard', { method: 'GET' });
  },

  /**
   * Retrieve overview candidate statistics.
   */
  async getAnalyticsOverview() {
    return apiRequest('/analytics/overview', { method: 'GET' });
  },

  /**
   * Retrieve 6-dimensional skill breakdown.
   */
  async getSkillAnalytics() {
    return apiRequest('/analytics/skills', { method: 'GET' });
  },

  /**
   * Retrieve historical score trends.
   * @param {Object} [params] - { period: '30d' | '90d' | '1y' }
   */
  async getScoreTrends(params = {}) {
    const searchParams = new URLSearchParams();
    if (params.period) searchParams.append('period', params.period);
    const queryString = searchParams.toString();
    return apiRequest(`/analytics/trends${queryString ? `?${queryString}` : ''}`, { method: 'GET' });
  },

  /**
   * Retrieve topic and subject category performance.
   */
  async getTopicPerformance() {
    return apiRequest('/analytics/topics', { method: 'GET' });
  },

  /**
   * Retrieve adaptive follow-up and counter question statistics.
   */
  async getAdaptiveAnalytics() {
    return apiRequest('/analytics/adaptive', { method: 'GET' });
  },

  /**
   * Retrieve identified weak focus areas.
   */
  async getWeakAreas() {
    return apiRequest('/analytics/weak-areas', { method: 'GET' });
  },

  /**
   * Retrieve identified strong dimensions.
   */
  async getStrongAreas() {
    return apiRequest('/analytics/strong-areas', { method: 'GET' });
  },

  /**
   * Retrieve practice activity timeline points.
   * @param {Object} [params] - { days }
   */
  async getPracticeActivity(params = {}) {
    const searchParams = new URLSearchParams();
    if (params.days) searchParams.append('days', params.days);
    const queryString = searchParams.toString();
    return apiRequest(`/analytics/activity${queryString ? `?${queryString}` : ''}`, { method: 'GET' });
  },

  /**
   * Retrieve paginated session history analytics.
   * @param {Object} [params] - { status, interview_type, input_mode, page, page_size }
   */
  async getInterviewHistory(params = {}) {
    const searchParams = new URLSearchParams();
    if (params.status) searchParams.append('status', params.status);
    if (params.interview_type) searchParams.append('interview_type', params.interview_type);
    if (params.input_mode) searchParams.append('input_mode', params.input_mode);
    if (params.page) searchParams.append('page', params.page);
    if (params.page_size) searchParams.append('page_size', params.page_size);

    const queryString = searchParams.toString();
    return apiRequest(`/analytics/history${queryString ? `?${queryString}` : ''}`, { method: 'GET' });
  },
};
