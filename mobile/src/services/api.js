import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const BASE_URL = 'http://10.0.2.2:8000/api'; // Android emulator -> localhost

const api = axios.create({
  baseURL: BASE_URL,
  headers: {'Content-Type': 'application/json'},
});

api.interceptors.request.use(async config => {
  const token = await AsyncStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refresh = await AsyncStorage.getItem('refresh_token');
        const res = await axios.post(`${BASE_URL}/auth/token/refresh/`, {
          refresh,
        });
        await AsyncStorage.setItem('access_token', res.data.access);
        originalRequest.headers.Authorization = `Bearer ${res.data.access}`;
        return api(originalRequest);
      } catch (e) {
        await AsyncStorage.multiRemove(['access_token', 'refresh_token', 'user']);
        return Promise.reject(e);
      }
    }
    return Promise.reject(error);
  },
);

export const authAPI = {
  login: (username, password) =>
    api.post('/auth/login/', {username, password}),
  register: data => api.post('/auth/register/', data),
  profile: () => api.get('/auth/profile/'),
  updateProfile: data => api.put('/auth/profile/', data),
};

export const coursesAPI = {
  myCourses: () => api.get('/courses/my/'),
  list: () => api.get('/courses/'),
};

export const attendanceAPI = {
  myAttendance: params => api.get('/attendance/my/', {params}),
  summary: () => api.get('/attendance/summary/'),
  scan: data => api.post('/sessions/scan/', data),
};

export default api;
