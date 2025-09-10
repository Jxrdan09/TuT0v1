import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Crear instancia de axios
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token a las peticiones
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar respuestas
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    if (error.response?.status === 402) {
      // Suscripción expirada
      try { alert('Tu suscripción ha expirado. Contacta al administrador o renueva.'); } catch (e) {}
      return Promise.reject(error);
    }
    return Promise.reject(error);
  }
);

// API de autenticación
export const authAPI = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  register: (userData) => api.post('/auth/register', userData),
  getCurrentUser: () => api.get('/auth/me'),
  createAdmin: (adminData) => api.post('/auth/create-admin', adminData),
};

// API de scripts
export const scriptsAPI = {
  getScripts: () => api.get('/scripts/'),
  getAllScripts: () => api.get('/scripts/all'),
  getScript: (id) => api.get(`/scripts/${id}`),
  createScript: (scriptData) => api.post('/scripts/', scriptData),
  updateScript: (id, scriptData) => api.put(`/scripts/${id}`, scriptData),
  deleteScript: (id) => api.delete(`/scripts/${id}`),
  executeScript: (id) => api.post(`/scripts/${id}/execute`),
  getScriptExecutions: (id) => api.get(`/scripts/${id}/executions`),
};

// API de administración
export const adminAPI = {
  getUsers: () => api.get('/admin/users'),
  toggleUserStatus: (id) => api.put(`/admin/users/${id}/toggle-status`),
  toggleUserAdmin: (id) => api.put(`/admin/users/${id}/toggle-admin`),
  
  getKeys: () => api.get('/admin/keys'),
  createKey: (keyData) => api.post('/admin/keys', keyData),
  toggleKeyStatus: (id) => api.put(`/admin/keys/${id}/toggle-status`),
  deleteKey: (id) => api.delete(`/admin/keys/${id}`),
  renewKey: (id) => api.post(`/admin/keys/${id}/renew`),
  extendUser: (userId, days = 30) => api.post(`/admin/users/${userId}/extend?days=${days}`),
  
  getGateways: () => api.get('/admin/gateways'),
  createGateway: (gatewayData) => api.post('/admin/gateways', gatewayData),
  updateGateway: (id, gatewayData) => api.put(`/admin/gateways/${id}`, gatewayData),
  deleteGateway: (id) => api.delete(`/admin/gateways/${id}`),
  
  getStats: () => api.get('/admin/stats'),
};

// API de Amazon Gateway
export const amazonAPI = {
  saveCookie: (cookieData) => api.post('/amazon/cookie', cookieData),
  getCookie: () => api.get('/amazon/cookie'),
  deleteCookie: () => api.delete('/amazon/cookie'),
  
  checkCard: (cardData) => api.post('/amazon/check-card', cardData),
  checkMultipleCards: (cards) => api.post('/amazon/check-cards', cards),
  
  getHistory: (limit = 50) => api.get(`/amazon/history?limit=${limit}`),
  getStats: () => api.get('/amazon/stats'),
};

// API de Gestión de Proxies
export const proxyAPI = {
  getProxies: () => api.get('/proxies/'),
  getStats: () => api.get('/proxies/stats'),
  testAll: () => api.post('/proxies/test-all'),
  toggleProxy: (proxyId) => api.put(`/proxies/${proxyId}/toggle`),
  deleteProxy: (proxyId) => api.delete(`/proxies/${proxyId}`),
  uploadFile: (formData) => api.post('/proxies/upload-file', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  loadFromFile: () => api.post('/proxies/load-from-file'),
  createTemplate: () => api.post('/proxies/create-template'),
  getUserStats: () => api.get('/proxies/user-stats'),
};

// API de Gates
export const gatesAPI = {
  // Obtener todos los gates
  getAllGates: async () => {
    const response = await api.get('/api/gates/');
    return response.data;
  },

  // Obtener un gate específico
  getGate: async (gateId) => {
    const response = await api.get(`/api/gates/${gateId}`);
    return response.data;
  },

  // Verificar datos con un gate
  checkGate: async (gateId, data) => {
    const response = await api.post(`/api/gates/${gateId}/check`, data);
    return response.data;
  },

  // Obtener estado de un gate
  getGateStatus: async (gateId) => {
    const response = await api.get(`/api/gates/${gateId}/status`);
    return response.data;
  },

  // Resetear estado de un gate
  resetGateStatus: async (gateId) => {
    const response = await api.post(`/api/gates/${gateId}/reset`);
    return response.data;
  },

  // Obtener estadísticas globales
  getGlobalStats: async () => {
    const response = await api.get('/api/gates/stats/global');
    return response.data;
  }
};

export default api;
