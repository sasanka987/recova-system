import api from './api';

export const authService = {
  login: async (email, password) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response = await api.post('/auth/login', formData);
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
    }
    return response.data;
  },

  register: async (userData) => {
    return await api.post('/auth/register', userData);
  },

  getProfile: async () => {
    return await api.get('/auth/me');
  },

  logout: () => {
    localStorage.removeItem('token');
  }
};