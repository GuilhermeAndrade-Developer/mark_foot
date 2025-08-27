import api from './api'

export interface SocialStats {
  total_comments: number
  total_users: number
  total_follows: number
  active_comments_today: number
  pending_reports: number
  flagged_comments: number
  top_commenters: Array<{
    id: number
    username: string
    comment_count: number
  }>
  recent_activities: Array<{
    id: number
    user: {
      id: number
      username: string
    }
    activity_type: string
    description: string
    created_at: string
  }>
}

export interface Comment {
  id: number
  content: string
  user: {
    id: number
    username: string
    email: string
  }
  match: {
    id: number
    home_team: string
    away_team: string
    date: string
  }
  parent?: Comment
  is_approved: boolean
  is_flagged: boolean
  flag_reason?: string
  likes_count: number
  dislikes_count: number
  replies_count: number
  created_at: string
  updated_at: string
}

export interface UserProfile {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  is_active: boolean
  date_joined: string
  comments_count: number
  followers_count: number
  following_count: number
  recent_activity: Array<{
    id: number
    activity_type: string
    description: string
    created_at: string
  }>
}

export interface UserFollow {
  id: number
  follower: {
    id: number
    username: string
  }
  following: {
    id: number
    username: string
  }
  created_at: string
}

export interface CommentReport {
  id: number
  comment: Comment
  reporter: {
    id: number
    username: string
  }
  reason: string
  status: 'pending' | 'resolved' | 'dismissed'
  admin_notes?: string
  created_at: string
  resolved_at?: string
}

export class SocialApiService {
  // Dashboard Stats
  static async getStats(): Promise<SocialStats> {
    const response = await api.get('/social/dashboard/stats/')
    return response.data
  }

  // Comments Management
  static async getComments(params?: {
    page?: number
    search?: string
    status?: 'all' | 'approved' | 'pending' | 'flagged'
    match_id?: number
    user_id?: number
  }) {
    const response = await api.get('/social/comments/', { params })
    return response.data
  }

  static async getComment(id: number): Promise<Comment> {
    const response = await api.get(`/social/comments/${id}/`)
    return response.data
  }

  static async approveComment(id: number): Promise<Comment> {
    const response = await api.post(`/social/comments/${id}/approve/`)
    return response.data
  }

  static async flagComment(id: number, reason: string): Promise<Comment> {
    const response = await api.post(`/social/comments/${id}/flag/`, {
      reason
    })
    return response.data
  }

  static async unflagComment(id: number): Promise<Comment> {
    const response = await api.post(`/social/comments/${id}/unflag/`)
    return response.data
  }

  static async deleteComment(id: number): Promise<void> {
    await api.delete(`/social/comments/${id}/`)
  }

  static async bulkModerateComments(ids: number[], action: 'approve' | 'flag' | 'delete', reason?: string) {
    const response = await api.post('/social/comments/bulk_moderate/', {
      comment_ids: ids,
      action,
      reason
    })
    return response.data
  }

  // Users Management
  static async getUsers(params?: {
    page?: number
    search?: string
    is_active?: boolean
    has_comments?: boolean
    has_followers?: boolean
  }) {
    const response = await api.get('/social/users/', { params })
    return response.data
  }

  static async getUserProfile(id: number): Promise<UserProfile> {
    const response = await api.get(`/social/users/${id}/`)
    return response.data
  }

  static async updateUserStatus(id: number, is_active: boolean): Promise<UserProfile> {
    const response = await api.patch(`/social/users/${id}/`, {
      is_active
    })
    return response.data
  }

  static async getUserComments(userId: number, params?: {
    page?: number
    status?: string
  }) {
    const response = await api.get(`/social/users/${userId}/comments/`, { params })
    return response.data
  }

  static async getUserFollowers(userId: number, params?: { page?: number }) {
    const response = await api.get(`/social/users/${userId}/followers/`, { params })
    return response.data
  }

  static async getUserFollowing(userId: number, params?: { page?: number }) {
    const response = await api.get(`/social/users/${userId}/following/`, { params })
    return response.data
  }

  // Follow Management
  static async getFollows(params?: {
    page?: number
    search?: string
    user_id?: number
  }) {
    const response = await api.get('/social/follows/', { params })
    return response.data
  }

  static async removeFollow(id: number): Promise<void> {
    await api.delete(`/social/follows/${id}/`)
  }

  // Reports Management
  static async getReports(params?: {
    page?: number
    status?: 'pending' | 'resolved' | 'dismissed'
    reporter_id?: number
  }) {
    const response = await api.get('/social/reports/', { params })
    return response.data
  }

  static async getReport(id: number): Promise<CommentReport> {
    const response = await api.get(`/social/reports/${id}/`)
    return response.data
  }

  static async resolveReport(id: number, adminNotes?: string): Promise<CommentReport> {
    const response = await api.post(`/social/reports/${id}/resolve/`, {
      admin_notes: adminNotes
    })
    return response.data
  }

  static async dismissReport(id: number, adminNotes?: string): Promise<CommentReport> {
    const response = await api.post(`/social/reports/${id}/dismiss/`, {
      admin_notes: adminNotes
    })
    return response.data
  }

  // Activities
  static async getActivities(params?: {
    page?: number
    user_id?: number
    activity_type?: string
    date_from?: string
    date_to?: string
  }) {
    const response = await api.get('/social/activities/', { params })
    return response.data
  }

  // Export Functions
  static async exportComments(params?: {
    format?: 'csv' | 'json'
    status?: string
    date_from?: string
    date_to?: string
  }) {
    const response = await api.get('/social/export/comments/', {
      params,
      responseType: 'blob'
    })
    return response.data
  }

  static async exportUsers(params?: {
    format?: 'csv' | 'json'
    is_active?: boolean
    date_from?: string
    date_to?: string
  }) {
    const response = await api.get('/social/export/users/', {
      params,
      responseType: 'blob'
    })
    return response.data
  }

  static async exportActivities(params?: {
    format?: 'csv' | 'json'
    activity_type?: string
    date_from?: string
    date_to?: string
  }) {
    const response = await api.get('/social/export/activities/', {
      params,
      responseType: 'blob'
    })
    return response.data
  }
}

export default SocialApiService
