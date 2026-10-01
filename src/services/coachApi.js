import { apiRequest } from './api';

export const coachApi = {
  /**
   * Retrieve active tasks for today's preparation dashboard.
   */
  async getTodayPlan() {
    return apiRequest('/coach/today', { method: 'GET' });
  },

  /**
   * Retrieve candidate's preparation plans with optional filtering.
   * @param {Object} [params] - { type, status, date, skip, limit }
   */
  async getPlans(params = {}) {
    const searchParams = new URLSearchParams();
    if (params.type) searchParams.append('type', params.type);
    if (params.status) searchParams.append('status', params.status);
    if (params.date) searchParams.append('date', params.date);
    if (params.skip !== undefined) searchParams.append('skip', params.skip);
    if (params.limit !== undefined) searchParams.append('limit', params.limit);

    const queryString = searchParams.toString();
    return apiRequest(`/coach/plans${queryString ? `?${queryString}` : ''}`, { method: 'GET' });
  },

  /**
   * Retrieve a specific plan by ID.
   * @param {string} planId
   */
  async getPlan(planId) {
    return apiRequest(`/coach/plans/${planId}`, { method: 'GET' });
  },

  /**
   * Generate a daily preparation plan.
   * @param {boolean} [refresh=false]
   */
  async generateDailyPlan(refresh = false) {
    return apiRequest('/coach/daily-plan', {
      method: 'POST',
      body: JSON.stringify({ plan_type: 'DAILY', refresh }),
    });
  },

  /**
   * Generate a 7-day weekly preparation plan.
   * @param {boolean} [refresh=false]
   */
  async generateWeeklyPlan(refresh = false) {
    return apiRequest('/coach/weekly-plan', {
      method: 'POST',
      body: JSON.stringify({ plan_type: 'WEEKLY', refresh }),
    });
  },

  /**
   * Force regenerate preparation plan with latest analytics.
   * @param {string} [planType='DAILY']
   */
  async refreshCoach(planType = 'DAILY') {
    return apiRequest('/coach/refresh', {
      method: 'POST',
      body: JSON.stringify({ plan_type: planType, refresh: true }),
    });
  },

  /**
   * Mark task as in progress.
   * @param {string} taskId
   */
  async startTask(taskId) {
    return apiRequest(`/coach/tasks/${taskId}/start`, { method: 'POST' });
  },

  /**
   * Mark task as completed.
   * @param {string} taskId
   */
  async completeTask(taskId) {
    return apiRequest(`/coach/tasks/${taskId}/complete`, { method: 'POST' });
  },

  /**
   * Mark task as skipped.
   * @param {string} taskId
   */
  async skipTask(taskId) {
    return apiRequest(`/coach/tasks/${taskId}/skip`, { method: 'POST' });
  },
};
