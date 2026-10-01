const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

/**
 * Voice API Service client for Prashasak AI.
 */
export const voiceApi = {
  /**
   * Transcribe recorded audio blob into canonical text transcript.
   * @param {Blob} audioBlob - Recorded audio blob from MediaRecorder
   * @param {string} [language="en-IN"] - Optional target language code
   * @returns {Promise<{text: string, language: string, duration_seconds: number|null, confidence: number|null}>}
   */
  async transcribeAudio(audioBlob, language = 'en-IN') {
    const token = localStorage.getItem('prashasak_auth_token');
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.wav');
    if (language) {
      formData.append('language', language);
    }

    const headers = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/voice/transcribe`, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (response.status === 401 && token) {
      localStorage.removeItem('prashasak_auth_token');
      localStorage.removeItem('prashasak_user');
      window.dispatchEvent(new Event('auth_unauthorized'));
    }

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      const errorMessage = data.detail || `Transcription failed with status ${response.status}`;
      const error = new Error(errorMessage);
      error.status = response.status;
      error.data = data;
      throw error;
    }

    return data;
  },

  /**
   * Synthesize question text into speech audio.
   * @param {string} text - Text string to convert to speech
   * @param {string} [language="en-IN"] - Voice language
   * @param {string} [voice="default"] - Voice model/accent
   * @returns {Promise<string>} Blob Object URL for playing synthesized audio
   */
  async synthesizeSpeech(text, language = 'en-IN', voice = 'default') {
    const token = localStorage.getItem('prashasak_auth_token');
    const headers = {
      'Content-Type': 'application/json',
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/voice/synthesize`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ text, language, voice }),
    });

    if (response.status === 401 && token) {
      localStorage.removeItem('prashasak_auth_token');
      localStorage.removeItem('prashasak_user');
      window.dispatchEvent(new Event('auth_unauthorized'));
    }

    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      const errorMessage = data.detail || `TTS synthesis failed with status ${response.status}`;
      const error = new Error(errorMessage);
      error.status = response.status;
      throw error;
    }

    const audioBlob = await response.blob();
    return URL.createObjectURL(audioBlob);
  },
};
