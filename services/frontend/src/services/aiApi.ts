import axios from 'axios'

// Use a URL direta da porta 8001 onde as APIs estão funcionando
const AI_BASE_URL = 'http://localhost:8001'

// Create axios instance specifically for AI endpoints
const aiApi = axios.create({
  baseURL: AI_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for auth
aiApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
aiApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired, clear all auth data
      localStorage.removeItem('auth_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user_data')
      sessionStorage.removeItem('auth_token')
      sessionStorage.removeItem('refresh_token')
      sessionStorage.removeItem('user_data')
    }
    return Promise.reject(error)
  }
)

// AI Service Class
export class AIService {
  // AI Stats
  static async getStats() {
    const response = await aiApi.get('/api/ai/stats/')
    return response.data
  }

  // AI Sentiment Analysis
  static async getSentimentData(params?: any) {
    const response = await aiApi.get('/api/ai/sentiment/', { params })
    return response.data
  }

  // AI Test Services
  static async runTest(action: string, params?: any) {
    const response = await aiApi.post('/api/ai/test/', { action, ...params })
    return response.data
  }

  // Test specific actions
  static async runBasicTest() {
    return this.runTest('test_basic')
  }

  static async runSentimentAnalysis() {
    return this.runTest('analyze_sentiment')
  }

  static async runDatabaseStats() {
    return this.runTest('database_stats')
  }

  static async runCompleteTest() {
    return this.runTest('test_all_services')
  }
}

export default aiApi
