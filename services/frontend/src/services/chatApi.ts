/**
 * Chat API service for administrative functions
 */
import api from './api'

// Create custom axios instance specifically for chat API
import axios from 'axios'

const chatApi = axios.create({
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

export interface ChatMessage {
  id: string
  content: string
  message_type: 'text' | 'emoji' | 'system' | 'admin'
  status: 'active' | 'hidden' | 'deleted' | 'flagged'
  is_flagged: boolean
  flag_count: number
  auto_flagged: boolean
  likes_count: number
  reports_count: number
  user_info?: {
    id: number
    username: string
    first_name: string
    last_name: string
  }
  username: string
  guest_name?: string
  room_name: string
  moderated_by_username?: string
  moderated_at?: string
  moderation_reason?: string
  can_moderate: boolean
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

export interface ChatReport {
  id: string
  reason: string
  description: string
  status: 'pending' | 'reviewed' | 'resolved' | 'dismissed'
  reporter_username: string
  message_content: string
  message_author: string
  room_name: string
  reviewed_by_username?: string
  reviewed_at?: string
  resolution_notes: string
  created_at: string
}

export interface ChatModeration {
  id: string
  action_type: 'warn' | 'timeout' | 'kick' | 'ban' | 'message_delete' | 'message_edit'
  reason: string
  duration_minutes?: number
  moderator_username: string
  target_username?: string
  room_name: string
  is_active: boolean
  is_expired: boolean
  created_at: string
  expires_at?: string
}

class ChatApiService {
  private baseUrl = ''

  // Dashboard Statistics
  async getStats(): Promise<ChatStats> {
    const response = await chatApi.get(`${this.baseUrl}/dashboard/stats/`)
    return response.data
  }

  // Chat Rooms Management
  async getRooms(params?: {
    room_type?: string
    status?: string
    match?: number
    team?: number
    page?: number
  }): Promise<{ results: ChatRoom[]; count: number }> {
    const response = await chatApi.get(`${this.baseUrl}/rooms/`, { params })
    return response.data
  }

  async getRoom(roomId: string): Promise<ChatRoom> {
    const response = await chatApi.get(`${this.baseUrl}/rooms/${roomId}/`)
    return response.data
  }

  async createRoom(roomData: Partial<ChatRoom>): Promise<ChatRoom> {
    const response = await chatApi.post(`${this.baseUrl}/rooms/`, roomData)
    return response.data
  }

  async updateRoom(roomId: string, roomData: Partial<ChatRoom>): Promise<ChatRoom> {
    const response = await chatApi.patch(`${this.baseUrl}/rooms/${roomId}/`, roomData)
    return response.data
  }

  async deleteRoom(roomId: string): Promise<void> {
    await chatApi.delete(`${this.baseUrl}/rooms/${roomId}/`)
  }

  async activateRoom(roomId: string): Promise<void> {
    await chatApi.post(`${this.baseUrl}/rooms/${roomId}/activate/`)
  }

  async deactivateRoom(roomId: string): Promise<void> {
    await chatApi.post(`${this.baseUrl}/rooms/${roomId}/deactivate/`)
  }

  async getRoomQuickStats(roomId: string): Promise<any> {
    const response = await chatApi.get(`${this.baseUrl}/rooms/${roomId}/quick_stats/`)
    return response.data
  }

  async getRoomRecentMessages(roomId: string, limit: number = 50): Promise<ChatMessage[]> {
    const response = await chatApi.get(`${this.baseUrl}/rooms/${roomId}/recent_messages/`, {
      params: { limit }
    })
    return response.data
  }

  async getRoomActiveUsers(roomId: string): Promise<any[]> {
    const response = await chatApi.get(`${this.baseUrl}/rooms/${roomId}/active_users/`)
    return response.data
  }

  async createMatchRoom(matchId: number): Promise<ChatRoom> {
    const response = await chatApi.post(`${this.baseUrl}/rooms/create_match_room/`, {
      match_id: matchId
    })
    return response.data
  }

  // Messages Management
  async getMessages(params?: {
    room?: string
    user?: number
    status?: string
    flagged?: boolean
    page?: number
  }): Promise<{ results: ChatMessage[]; count: number }> {
    const response = await chatApi.get(`${this.baseUrl}/messages/`, { params })
    return response.data
  }

  async getMessage(messageId: string): Promise<ChatMessage> {
    const response = await chatApi.get(`${this.baseUrl}/messages/${messageId}/`)
    return response.data
  }

  async getFlaggedMessages(params?: {
    severity?: string
    type?: string
    status?: string
    room?: string
    page?: number
  }): Promise<{ results: any[]; count: number }> {
    const response = await chatApi.get(`${this.baseUrl}/messages/flagged/`, { params })
    return response.data
  }

  async approveMessage(messageId: string): Promise<void> {
    await chatApi.post(`${this.baseUrl}/messages/${messageId}/approve/`)
  }

  async flagMessage(messageId: string, reason: string): Promise<void> {
    await chatApi.post(`${this.baseUrl}/messages/${messageId}/flag_message/`, { reason })
  }

  async unflagMessage(messageId: string): Promise<void> {
    await chatApi.post(`${this.baseUrl}/messages/${messageId}/unflag_message/`)
  }

  async hideMessage(messageId: string, reason: string): Promise<void> {
    await chatApi.post(`${this.baseUrl}/messages/${messageId}/hide_message/`, { reason })
  }

  async deleteMessage(messageId: string, reason: string): Promise<void> {
    await chatApi.post(`${this.baseUrl}/messages/${messageId}/delete_message/`, { reason })
  }

  // Reports Management
  async getReports(params?: {
    status?: string
    room?: string
    reason?: string
    page?: number
  }): Promise<{ results: ChatReport[]; count: number }> {
    const response = await chatApi.get(`${this.baseUrl}/reports/`, { params })
    return response.data
  }

  async getReport(reportId: string): Promise<ChatReport> {
    const response = await chatApi.get(`${this.baseUrl}/reports/${reportId}/`)
    return response.data
  }

  async updateReportStatus(reportId: string, status: string): Promise<void> {
    await chatApi.patch(`${this.baseUrl}/reports/${reportId}/`, { status })
  }

  async resolveReport(reportId: string, resolutionNotes: string): Promise<void> {
    await chatApi.post(`${this.baseUrl}/reports/${reportId}/resolve_report/`, {
      resolution_notes: resolutionNotes
    })
  }

  async dismissReport(reportId: string, resolutionNotes: string): Promise<void> {
    await chatApi.post(`${this.baseUrl}/reports/${reportId}/dismiss_report/`, {
      resolution_notes: resolutionNotes
    })
  }

  // Moderation Actions
  async getModerationActions(params?: {
    room?: string
    moderator?: number
    action_type?: string
    page?: number
  }): Promise<{ results: ChatModeration[]; count: number }> {
    const response = await chatApi.get(`${this.baseUrl}/moderation/`, { params })
    return response.data
  }

  async createModerationAction(actionData: {
    room: string
    target_user?: number
    target_message?: string
    action_type: string
    reason: string
    duration_minutes?: number
  }): Promise<ChatModeration> {
    const response = await chatApi.post(`${this.baseUrl}/moderation/`, actionData)
    return response.data
  }

  // Banned Users Management
  async getBannedUsers(params?: {
    room?: string
    ban_type?: string
    active_only?: boolean
    page?: number
  }): Promise<{ results: any[]; count: number }> {
    const response = await chatApi.get(`${this.baseUrl}/banned-users/`, { params })
    return response.data
  }

  async banUser(banData: {
    user: number
    room?: string
    ban_type: string
    reason: string
    expires_at?: string
  }): Promise<any> {
    const response = await chatApi.post(`${this.baseUrl}/banned-users/`, banData)
    return response.data
  }

  async unbanUser(banId: string): Promise<void> {
    await chatApi.post(`${this.baseUrl}/banned-users/${banId}/unban_user/`)
  }

  // User Moderation Actions
  async warnUser(userId: string, data: {
    reason: string
    room_id?: string
  }): Promise<void> {
    await chatApi.post(`${this.baseUrl}/users/${userId}/warn/`, data)
  }

  async muteUser(userId: string, data: {
    duration: number
    reason: string
    room_id?: string
  }): Promise<void> {
    await chatApi.post(`${this.baseUrl}/users/${userId}/mute/`, data)
  }

  // Moderation Statistics
  async getModerationStats(): Promise<any> {
    const response = await chatApi.get(`${this.baseUrl}/moderation/stats/`)
    return response.data
  }
}

export default new ChatApiService()
