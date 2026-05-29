import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

// 请求拦截器 - 自动添加 token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器
api.interceptors.response.use(
  response => response.data,
  error => {
    const msg = error.response?.data?.error || '请求失败'
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(new Error(msg))
  }
)

// ====== 用户认证 ======
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
  updateMe: (data) => api.put('/auth/me', data),
}

// ====== 电影 ======
export const moviesAPI = {
  list: (params) => api.get('/movies', { params }),
  get: (id) => api.get(`/movies/${id}`),
  genres: () => api.get('/movies/genres'),
  create: (data) => api.post('/movies', data),
  update: (id, data) => api.put(`/movies/${id}`, data),
  delete: (id) => api.delete(`/movies/${id}`),
}

// ====== 评分 ======
export const ratingsAPI = {
  create: (data) => api.post('/ratings', data),
  getByMovie: (movieId, params) => api.get(`/ratings/movie/${movieId}`, { params }),
  getByUser: (params) => api.get('/ratings/user', { params }),
  delete: (id) => api.delete(`/ratings/${id}`),
}

// ====== 推荐 ======
export const recommendationsAPI = {
  list: (params) => api.get('/recommendations', { params }),
  similar: (movieId) => api.get(`/recommendations/similar/${movieId}`),
  trigger: () => api.post('/recommendations/trigger'),
  dashboard: () => api.get('/recommendations/dashboard'),
}

export default api
