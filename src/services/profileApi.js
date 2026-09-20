import { apiRequest } from './api';

export const profileApi = {
  /**
   * Fetch authenticated user's profile and dynamic backend completion percentage
   */
  async getProfile() {
    return apiRequest('/profile', {
      method: 'GET',
    });
  },

  /**
   * Update authenticated user's DAF profile data
   */
  async updateProfile(profilePayload) {
    return apiRequest('/profile', {
      method: 'PUT',
      body: JSON.stringify(profilePayload),
    });
  },
};
