import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Add request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const apiService = {
  // Sensor data endpoints
  getSensorData: (params = {}) => {
    return api.get('/api/sensordata', { params });
  },

  getLatestSensorData: () => {
    return api.get('/api/sensordata/latest');
  },

  postSensorData: (data) => {
    return api.post('/api/sensordata', data);
  },

  // Alert endpoints
  getAlerts: (params = {}) => {
    return api.get('/api/alerts', { params });
  },

  resolveAlert: (alertId) => {
    return api.post(`/api/alerts/${alertId}/resolve`);
  },

  // System status
  getSystemStatus: () => {
    return api.get('/api/system/status');
  },

  // Analytics
  getAnalytics: (hours = 24) => {
    return api.get('/api/analytics/statistics', { params: { hours } });
  },

  // Health check
  healthCheck: () => {
    return api.get('/api/health');
  }
};

export default api;
