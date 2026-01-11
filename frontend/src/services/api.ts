import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_V1 = `${API_URL}/api/v1`;

const api = axios.create({
  baseURL: API_V1,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth
export const authAPI = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  register: (email: string, password: string, full_name: string) =>
    api.post('/auth/register', { email, password, full_name }),
  getCurrentUser: () => api.get('/auth/me'),
};

// Dashboard
export const dashboardAPI = {
  getStats: () => api.get('/dashboard/stats'),
  getRecentAlerts: () => api.get('/dashboard/recent-alerts'),
  getScrapingStatus: () => api.get('/dashboard/scraping-status'),
};

// Products
export const productsAPI = {
  getAll: (params?: any) => api.get('/products/', { params }),
  getOne: (id: number) => api.get(`/products/${id}`),
  create: (data: any) => api.post('/products/', data),
  update: (id: number, data: any) => api.put(`/products/${id}`, data),
  delete: (id: number) => api.delete(`/products/${id}`),
  getPriceHistory: (id: number, params?: any) =>
    api.get(`/products/${id}/price-history`, { params }),
  bulkImport: (products: any[]) =>
    api.post('/products/bulk-import', { products }),
};

// Sources
export const sourcesAPI = {
  getAll: (params?: any) => api.get('/sources/', { params }),
  getOne: (id: number) => api.get(`/sources/${id}`),
  create: (data: any) => api.post('/sources/', data),
  update: (id: number, data: any) => api.put(`/sources/${id}`, data),
  delete: (id: number) => api.delete(`/sources/${id}`),
  getProductSources: (params?: any) =>
    api.get('/sources/product-sources/', { params }),
  createProductSource: (data: any) =>
    api.post('/sources/product-sources/', data),
  deleteProductSource: (id: number) =>
    api.delete(`/sources/product-sources/${id}`),
};

// Alerts
export const alertsAPI = {
  getAll: (params?: any) => api.get('/alerts/', { params }),
  getOne: (id: number) => api.get(`/alerts/${id}`),
  create: (data: any) => api.post('/alerts/', data),
  update: (id: number, data: any) => api.put(`/alerts/${id}`, data),
  delete: (id: number) => api.delete(`/alerts/${id}`),
};

// Reports
export const reportsAPI = {
  generate: (data: any) =>
    api.post('/reports/generate', data, { responseType: 'blob' }),
};

export default api;
