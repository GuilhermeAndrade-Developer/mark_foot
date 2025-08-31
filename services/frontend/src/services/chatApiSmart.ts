/**
 * Chat API service with automatic demo/real data detection
 */
import axios, { type AxiosInstance } from 'axios'

// Create custom axios instance specifically for chat API
const chatApi: AxiosInstance = axios.create({
  baseURL: 'http://localhost:8001/api/chat',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Add auth token interceptor
chatApi.interceptors.request.use((config: any) => {
  const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Demo data
const DEMO_STATS = {
  total_rooms: 5,
  active_rooms: 4,
  total_messages_today: 1247,
  total_active_users: 89,
  pending_reports: 3,
  flagged_messages: 8,
  banned_users: 5,
  top_rooms: [
    {
      id: '1',
      name: 'Chat Geral',
      room_type: 'general',
      messages_today: 456,
      active_users: 23
    },
    {
      id: '2',
      name: 'Real Madrid Fan Club',
      room_type: 'team',
      messages_today: 289,
      active_users: 18
    },
    {
      id: '3',
      name: 'Premier League Chat',
      room_type: 'general',
      messages_today: 156,
      active_users: 12
    }
  ],
  recent_activity: [
    {
      id: '1',
      action_type: 'message',
      moderator: 'Sistema',
      target_user: null,
      room_name: 'Chat Geral',
      reason: 'Nova mensagem flagada automaticamente',
      created_at: new Date(Date.now() - 2 * 60 * 1000).toISOString()
    },
    {
      id: '2',
      action_type: 'moderation',
      moderator: 'Admin',
      target_user: 'usuario123',
      room_name: 'Real Madrid Fan Club',
      reason: 'Usuário advertido por spam',
      created_at: new Date(Date.now() - 5 * 60 * 1000).toISOString()
    }
  ],
  moderation_stats: {
    actions_today: 12,
    warnings_today: 8,
    bans_today: 2,
    message_deletions_today: 15
  },
  hourly_activity: Array.from({ length: 24 }, (_, i) => ({
    hour: `${i.toString().padStart(2, '0')}:00`,
    messages: Math.floor(Math.random() * 100) + 10
  }))
}

const DEMO_ROOMS: ChatRoom[] = [
  {
    id: '1',
    name: 'Chat Geral',
    description: 'Discussões gerais sobre futebol',
    room_type: 'general' as const,
    status: 'active' as const,
    max_users: 1000,
    rate_limit_messages: 5,
    auto_moderation: true,
    allow_guests: true,
    profanity_filter: true,
    spam_detection: true,
    link_filter: false,
    emoji_only_mode: false,
    total_messages: 1247,
    peak_concurrent_users: 89,
    total_unique_users: 234,
    active_users_count: 23,
    recent_messages_count: 45,
    created_by_username: 'admin',
    moderation_stats: {
      flagged_messages: 3,
      banned_users: 1,
      reports_last_24h: 2,
      moderation_actions_last_24h: 5
    },
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: '2',
    name: 'Real Madrid Fan Club',
    description: 'Sala dos torcedores do Real Madrid',
    room_type: 'team' as const,
    status: 'active' as const,
    max_users: 500,
    rate_limit_messages: 5,
    auto_moderation: true,
    allow_guests: false,
    profanity_filter: true,
    spam_detection: true,
    link_filter: true,
    emoji_only_mode: false,
    total_messages: 892,
    peak_concurrent_users: 67,
    total_unique_users: 156,
    active_users_count: 18,
    recent_messages_count: 23,
    team_info: {
      id: 1,
      name: 'Real Madrid',
      short_name: 'RMA',
      crest: '/teams/real-madrid.png'
    },
    created_by_username: 'admin',
    moderation_stats: {
      flagged_messages: 1,
      banned_users: 0,
      reports_last_24h: 1,
      moderation_actions_last_24h: 2
    },
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
]

// System status cache
let systemStatus: 'unknown' | 'demo' | 'real' = 'unknown'
let lastStatusCheck = 0
const STATUS_CACHE_DURATION = 30000 // 30 seconds

export interface ChatRoom {
  id: string
  name: string
  description: string
  room_type: 'match' | 'team' | 'general' | 'admin'
  status: 'active' | 'inactive' | 'archived' | 'maintenance'
  max_users: number
  rate_limit_messages: number
  auto_moderation: boolean
  allow_guests: boolean
  profanity_filter: boolean
  spam_detection: boolean
  link_filter: boolean
  emoji_only_mode: boolean
  total_messages: number
  peak_concurrent_users: number
  total_unique_users: number
  active_users_count: number
  recent_messages_count: number
  match_info?: {
    id: number
    home_team: string
    away_team: string
    status: string
    utc_date: string
    home_score?: number
    away_score?: number
  }
  team_info?: {
    id: number
    name: string
    short_name: string
    crest?: string
  }
  created_by_username: string
  moderation_stats: {
    flagged_messages: number
    banned_users: number
    reports_last_24h: number
    moderation_actions_last_24h: number
  }
  created_at: string
  updated_at: string
}

export interface ChatStats {
  total_rooms: number
  active_rooms: number
  total_messages_today: number
  total_active_users: number
  pending_reports: number
  flagged_messages: number
  banned_users: number
  top_rooms: Array<{
    id: string
    name: string
    room_type: string
    messages_today: number
    active_users: number
  }>
  recent_activity: Array<{
    id: string
    action_type: string
    moderator: string
    target_user?: string
    room_name: string
    reason: string
    created_at: string
  }>
  moderation_stats: {
    actions_today: number
    warnings_today: number
    bans_today: number
    message_deletions_today: number
  }
  hourly_activity: Array<{
    hour: string
    messages: number
  }>
}

class ChatApiService {
  private baseUrl = ''

  /**
   * Check if real API is available and has data
   */
  private async checkSystemStatus(): Promise<'demo' | 'real'> {
    const now = Date.now()
    
    // Use cached status if still valid
    if (systemStatus !== 'unknown' && (now - lastStatusCheck) < STATUS_CACHE_DURATION) {
      return systemStatus
    }

    try {
      // Test if API is reachable and has authentication
      const response = await chatApi.get('/rooms/', { 
        timeout: 3000,
        params: { limit: 1 } 
      })
      
      if (response.status === 200) {
        const data = response.data
        // Check if we have real data (not empty)
        if (data.results && data.results.length > 0) {
          systemStatus = 'real'
          console.info('🔗 Chat API: Using REAL data from backend')
        } else {
          systemStatus = 'demo'
          console.info('📺 Chat API: Using DEMO data (no real data available)')
        }
      } else {
        systemStatus = 'demo'
        console.info('📺 Chat API: Using DEMO data (API not ready)')
      }
    } catch (error: any) {
      systemStatus = 'demo'
      if (error.response?.status === 401) {
        console.info('🔐 Chat API: Using DEMO data (authentication required)')
      } else {
        console.info('📺 Chat API: Using DEMO data (API not available)')
      }
    }
    
    lastStatusCheck = now
    return systemStatus
  }

  /**
   * Execute API call with fallback to demo data
   */
  private async executeWithFallback<T>(
    apiCall: () => Promise<T>,
    demoData: T,
    operation: string
  ): Promise<T> {
    const status = await this.checkSystemStatus()
    
    if (status === 'demo') {
      console.debug(`📺 ${operation}: Using demo data`)
      return demoData
    }

    try {
      const result = await apiCall()
      console.debug(`🔗 ${operation}: Using real data`)
      return result
    } catch (error: any) {
      console.warn(`⚠️ ${operation}: API failed, falling back to demo data`, error.message)
      // Update system status to demo on API failure
      systemStatus = 'demo'
      lastStatusCheck = Date.now()
      return demoData
    }
  }

  // Dashboard Statistics
  async getStats(): Promise<ChatStats> {
    return this.executeWithFallback(
      async () => {
        const response = await chatApi.get(`${this.baseUrl}/dashboard/stats/`)
        return response.data
      },
      DEMO_STATS,
      'Dashboard Stats'
    )
  }

  // Chat Rooms Management
  async getRooms(params?: {
    room_type?: string
    status?: string
    match?: number
    team?: number
    page?: number
  }): Promise<{ results: ChatRoom[]; count: number }> {
    return this.executeWithFallback(
      async () => {
        const response = await chatApi.get(`${this.baseUrl}/rooms/`, { params })
        return response.data
      },
      { results: DEMO_ROOMS, count: DEMO_ROOMS.length },
      'Get Rooms'
    )
  }

  async getRoom(roomId: string): Promise<ChatRoom> {
    return this.executeWithFallback(
      async () => {
        const response = await chatApi.get(`${this.baseUrl}/rooms/${roomId}/`)
        return response.data
      },
      DEMO_ROOMS.find(r => r.id === roomId) || DEMO_ROOMS[0],
      'Get Room'
    )
  }

  async createRoom(roomData: Partial<ChatRoom>): Promise<ChatRoom> {
    const status = await this.checkSystemStatus()
    
    if (status === 'demo') {
      // Simulate creation in demo mode
      const newRoom: ChatRoom = {
        id: Date.now().toString(),
        name: roomData.name || 'Nova Sala',
        description: roomData.description || '',
        room_type: roomData.room_type || 'general',
        status: 'active',
        max_users: roomData.max_users || 1000,
        rate_limit_messages: roomData.rate_limit_messages || 5,
        auto_moderation: roomData.auto_moderation ?? true,
        allow_guests: roomData.allow_guests ?? true,
        profanity_filter: roomData.profanity_filter ?? true,
        spam_detection: roomData.spam_detection ?? true,
        link_filter: roomData.link_filter ?? false,
        emoji_only_mode: roomData.emoji_only_mode ?? false,
        total_messages: 0,
        peak_concurrent_users: 0,
        total_unique_users: 0,
        active_users_count: 0,
        recent_messages_count: 0,
        created_by_username: 'admin',
        moderation_stats: {
          flagged_messages: 0,
          banned_users: 0,
          reports_last_24h: 0,
          moderation_actions_last_24h: 0
        },
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
      
      console.debug('📺 Create Room: Simulated in demo mode')
      return newRoom
    }

    try {
      const response = await chatApi.post(`${this.baseUrl}/rooms/`, roomData)
      console.debug('🔗 Create Room: Using real API')
      return response.data
    } catch (error: any) {
      console.warn('⚠️ Create Room: API failed, operation not possible in demo mode')
      throw new Error('Criação de salas não disponível no modo demonstração')
    }
  }

  async updateRoom(roomId: string, roomData: Partial<ChatRoom>): Promise<ChatRoom> {
    const status = await this.checkSystemStatus()
    
    if (status === 'demo') {
      console.debug('📺 Update Room: Simulated in demo mode')
      // Find and update demo room
      const room = DEMO_ROOMS.find(r => r.id === roomId)
      if (room) {
        Object.assign(room, roomData, { updated_at: new Date().toISOString() })
        return room
      }
      throw new Error('Sala não encontrada')
    }

    try {
      const response = await chatApi.patch(`${this.baseUrl}/rooms/${roomId}/`, roomData)
      console.debug('🔗 Update Room: Using real API')
      return response.data
    } catch (error: any) {
      console.warn('⚠️ Update Room: API failed')
      throw error
    }
  }

  async deleteRoom(roomId: string): Promise<void> {
    const status = await this.checkSystemStatus()
    
    if (status === 'demo') {
      console.debug('📺 Delete Room: Simulated in demo mode')
      const index = DEMO_ROOMS.findIndex(r => r.id === roomId)
      if (index > -1) {
        DEMO_ROOMS.splice(index, 1)
      }
      return
    }

    try {
      await chatApi.delete(`${this.baseUrl}/rooms/${roomId}/`)
      console.debug('🔗 Delete Room: Using real API')
    } catch (error: any) {
      console.warn('⚠️ Delete Room: API failed')
      throw error
    }
  }

  async activateRoom(roomId: string): Promise<void> {
    const status = await this.checkSystemStatus()
    
    if (status === 'demo') {
      console.debug('📺 Activate Room: Simulated in demo mode')
      const room = DEMO_ROOMS.find(r => r.id === roomId)
      if (room) {
        room.status = 'active'
      }
      return
    }

    try {
      await chatApi.post(`${this.baseUrl}/rooms/${roomId}/activate/`)
      console.debug('🔗 Activate Room: Using real API')
    } catch (error: any) {
      console.warn('⚠️ Activate Room: API failed')
      throw error
    }
  }

  async deactivateRoom(roomId: string): Promise<void> {
    const status = await this.checkSystemStatus()
    
    if (status === 'demo') {
      console.debug('📺 Deactivate Room: Simulated in demo mode')
      const room = DEMO_ROOMS.find(r => r.id === roomId)
      if (room) {
        room.status = 'inactive'
      }
      return
    }

    try {
      await chatApi.post(`${this.baseUrl}/rooms/${roomId}/deactivate/`)
      console.debug('🔗 Deactivate Room: Using real API')
    } catch (error: any) {
      console.warn('⚠️ Deactivate Room: API failed')
      throw error
    }
  }

  /**
   * Get current system status
   */
  async getSystemStatus(): Promise<{
    mode: 'demo' | 'real'
    api_available: boolean
    has_data: boolean
    last_check: Date
  }> {
    const mode = await this.checkSystemStatus()
    
    return {
      mode,
      api_available: mode === 'real',
      has_data: mode === 'real',
      last_check: new Date(lastStatusCheck)
    }
  }

  /**
   * Force refresh system status
   */
  async refreshSystemStatus(): Promise<'demo' | 'real'> {
    systemStatus = 'unknown'
    lastStatusCheck = 0
    return this.checkSystemStatus()
  }

  // Placeholder methods for other endpoints (can be expanded similarly)
  async getFlaggedMessages(params?: any): Promise<{ results: any[]; count: number }> {
    return this.executeWithFallback(
      async () => {
        const response = await chatApi.get(`${this.baseUrl}/messages/flagged/`, { params })
        return response.data
      },
      { results: [], count: 0 },
      'Get Flagged Messages'
    )
  }

  async getReports(params?: any): Promise<{ results: any[]; count: number }> {
    return this.executeWithFallback(
      async () => {
        const response = await chatApi.get(`${this.baseUrl}/reports/`, { params })
        return response.data
      },
      { results: [], count: 0 },
      'Get Reports'
    )
  }

  async getBannedUsers(params?: any): Promise<{ results: any[]; count: number }> {
    return this.executeWithFallback(
      async () => {
        const response = await chatApi.get(`${this.baseUrl}/banned-users/`, { params })
        return response.data
      },
      { results: [], count: 0 },
      'Get Banned Users'
    )
  }

  async getModerationActions(params?: any): Promise<{ results: any[]; count: number }> {
    return this.executeWithFallback(
      async () => {
        const response = await chatApi.get(`${this.baseUrl}/moderation/`, { params })
        return response.data
      },
      { results: [], count: 0 },
      'Get Moderation Actions'
    )
  }
}

export default new ChatApiService()
