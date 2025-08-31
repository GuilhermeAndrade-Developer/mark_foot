import axios from 'axios'

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api/v1'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for auth
api.interceptors.request.use(
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
api.interceptors.response.use(
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
      // window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API Service Class
export class ApiService {
  // Dashboard
  static async getDashboardStats() {
    const response = await api.get('/dashboard/stats/')
    return response.data
  }

  static async getRecentMatches() {
    const response = await api.get('/dashboard/recent_matches/')
    return response.data
  }

  static async getTopScorers() {
    const response = await api.get('/dashboard/top_scorers/')
    return response.data
  }

  // Business Dashboard
  static async getBusinessMetrics() {
    try {
      const response = await api.get('/business/metrics/')
      return response.data
    } catch (error) {
      // Fallback to demo data if API not available
      return {
        activeUsers: { online: 234, today: 2847 },
        premiumUsers: { count: 1847, percentage: 14.5 },
        revenue: { monthly: 45000, growth: 22.1 },
        systemUptime: 99.8,
        services: [
          { name: 'API Backend', status: 'online', performance: 98, uptime: 99.8 },
          { name: 'Database MySQL', status: 'online', performance: 95, uptime: 99.9 },
          { name: 'Redis Cache', status: 'online', performance: 97, uptime: 99.7 },
          { name: 'Celery Workers', status: 'online', performance: 92, uptime: 99.5 },
          { name: 'IA Services', status: 'online', performance: 89, uptime: 98.2 }
        ]
      }
    }
  }

  static async getUserGrowthData() {
    try {
      const response = await api.get('/business/user-growth/')
      return response.data
    } catch (error) {
      // Fallback to demo data
      return {
        labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul'],
        totalUsers: [2400, 3200, 4100, 5800, 7200, 9500, 12500],
        premiumUsers: [120, 280, 450, 680, 920, 1350, 1800]
      }
    }
  }

  static async getRevenueData() {
    try {
      const response = await api.get('/business/revenue/')
      return response.data
    } catch (error) {
      // Fallback to demo data
      return {
        sources: ['Assinaturas Premium', 'Partnerships', 'API Marketplace', 'Publicidade'],
        values: [65, 20, 10, 5]
      }
    }
  }

  static async getSocialEngagementData() {
    try {
      const response = await api.get('/business/social-engagement/')
      return response.data
    } catch (error) {
      // Fallback to demo data
      return {
        platforms: ['Instagram', 'TikTok', 'Twitter', 'Facebook', 'YouTube'],
        engagement: [85, 92, 78, 65, 73]
      }
    }
  }

  static async getBusinessActivities() {
    try {
      const response = await api.get('/business/activities/')
      return response.data
    } catch (error) {
      // Fallback to demo data
      return [
        {
          id: 1,
          title: 'Novo usuário premium',
          description: 'Usuário #12847 assinou plano Premium',
          time: '5 min',
          icon: 'mdi-crown',
          color: 'warning'
        },
        {
          id: 2,
          title: 'Pico de acessos',
          description: 'Maior número de usuários simultâneos hoje',
          time: '12 min',
          icon: 'mdi-trending-up',
          color: 'success'
        },
        {
          id: 3,
          title: 'Backup realizado',
          description: 'Backup automático do banco de dados',
          time: '1 hora',
          icon: 'mdi-backup-restore',
          color: 'info'
        }
      ]
    }
  }

  // Teams
  static async getTeams(params?: any) {
    const response = await api.get('/teams/', { params })
    return response.data
  }

  static async getTeam(id: number) {
    const response = await api.get(`/teams/${id}/`)
    return response.data
  }

  static async getTeamPlayers(id: number) {
    const response = await api.get(`/teams/${id}/players/`)
    return response.data
  }

  // Players
  static async getPlayers(params?: any) {
    const response = await api.get('/players/', { params })
    return response.data
  }

  static async getPlayer(id: number) {
    const response = await api.get(`/players/${id}/`)
    return response.data
  }

  static async getPlayerStatistics(id: number) {
    const response = await api.get(`/players/${id}/statistics/`)
    return response.data
  }

  static async getPlayerTransfers(id: number) {
    const response = await api.get(`/players/${id}/transfers/`)
    return response.data
  }

  static async getTopScorersPlayers() {
    const response = await api.get('/players/top_scorers/')
    return response.data
  }

  // Matches
  static async getMatches(params?: any) {
    const response = await api.get('/matches/', { params })
    return response.data
  }

  static async getMatch(id: number) {
    const response = await api.get(`/matches/${id}/`)
    return response.data
  }

  static async getRecentMatchesData() {
    const response = await api.get('/matches/recent/')
    return response.data
  }

  static async getMatchesByDateRange(startDate: string, endDate: string) {
    const response = await api.get('/matches/by_date_range/', {
      params: { start_date: startDate, end_date: endDate }
    })
    return response.data
  }

  // Competitions
  static async getCompetitions(params?: any) {
    const response = await api.get('/competitions/', { params })
    return response.data
  }

  static async getCompetition(id: number) {
    const response = await api.get(`/competitions/${id}/`)
    return response.data
  }

  // Standings
  static async getStandings(params?: any) {
    const response = await api.get('/standings/', { params })
    return response.data
  }

  static async getCurrentStandings(competitionId: number) {
    const response = await api.get('/standings/current/', {
      params: { competition_id: competitionId }
    })
    return response.data
  }

  // Areas
  static async getAreas(params?: any) {
    const response = await api.get('/areas/', { params })
    return response.data
  }

  // Authentication methods
  static setAuthToken(token: string) {
    // Update the default authorization header
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
  }

  static removeAuthToken() {
    // Remove the authorization header
    delete api.defaults.headers.common['Authorization']
  }

  static async login(credentials: { username: string; password: string }) {
    const response = await api.post('/auth/login/', credentials)
    return response.data
  }

  static async refreshToken(refreshToken: string) {
    const response = await api.post('/auth/refresh/', { refresh: refreshToken })
    return response.data
  }

  static async getProfile() {
    const response = await api.get('/auth/profile/')
    return response.data
  }
}

export default api
