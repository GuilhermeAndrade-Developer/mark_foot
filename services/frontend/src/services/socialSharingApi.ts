import api from './api'

// Social Sharing Types
export interface SocialPlatform {
  id: number
  name: string
  display_name: string
  is_active: boolean
  character_limit: number
  supports_images: boolean
  supports_videos: boolean
  supports_hashtags: boolean
  created_at: string
  updated_at: string
}

export interface ShareTemplate {
  id: number
  name: string
  template_type: string
  platform: SocialPlatform
  title_template: string
  content_template: string
  hashtags: string
  available_variables: string[]
  is_active: boolean
  auto_share: boolean
  created_at: string
  updated_at: string
}

export interface SocialShare {
  id: number
  platform: SocialPlatform
  template?: ShareTemplate
  title: string
  content: string
  hashtags: string
  image_url?: string
  video_url?: string
  match?: number
  team?: number
  comment?: number
  user: {
    id: number
    username: string
  }
  scheduled_at?: string
  published_at?: string
  platform_post_id?: string
  platform_url?: string
  likes_count: number
  shares_count: number
  comments_count: number
  views_count: number
  status: 'pending' | 'scheduled' | 'published' | 'failed' | 'deleted'
  error_message?: string
  retry_count: number
  created_at: string
  updated_at: string
}

// Groups Types
export interface PrivateGroup {
  id: number
  name: string
  description: string
  group_type: 'family' | 'friends' | 'team_fans' | 'competition' | 'custom'
  privacy_level: 'private' | 'restricted' | 'public'
  max_members: number
  allow_member_invites: boolean
  require_admin_approval: boolean
  favorite_team?: string
  favorite_competition?: string
  cover_image?: string
  avatar_image?: string
  member_count: number
  post_count: number
  is_active: boolean
  is_featured: boolean
  user_membership?: {
    status: string
    role: string
    joined_at: string
  }
  can_join: boolean
  created_at: string
  updated_at: string
}

export interface GroupMembership {
  id: number
  group: PrivateGroup
  user: {
    id: number
    username: string
    first_name: string
    last_name: string
  }
  role: 'owner' | 'admin' | 'moderator' | 'member'
  status: 'active' | 'pending' | 'banned' | 'left'
  invited_by?: {
    id: number
    username: string
  }
  invitation_message?: string
  posts_count: number
  last_activity?: string
  joined_at: string
  left_at?: string
}

export interface GroupPost {
  id: number
  group: PrivateGroup
  author: {
    id: number
    username: string
    first_name: string
    last_name: string
  }
  post_type: 'text' | 'image' | 'video' | 'link' | 'poll' | 'event'
  title?: string
  content: string
  image_url?: string
  video_url?: string
  link_url?: string
  link_title?: string
  link_description?: string
  related_match?: number
  related_team?: number
  likes_count: number
  comments_count: number
  shares_count: number
  is_pinned: boolean
  is_announcement: boolean
  is_approved: boolean
  can_edit: boolean
  can_delete: boolean
  created_at: string
  updated_at: string
}

export interface GroupInvitation {
  id: number
  group: PrivateGroup
  inviter: {
    id: number
    username: string
  }
  invitee: {
    id: number
    username: string
  }
  message?: string
  status: 'pending' | 'accepted' | 'declined' | 'expired' | 'cancelled'
  expires_at: string
  responded_at?: string
  response_message?: string
  is_expired: boolean
  can_respond: boolean
  created_at: string
}

// Statistics Types
export interface SocialSharingStats {
  total_shares: number
  shares_by_platform: Record<string, number>
  shares_today: number
  shares_this_week: number
  shares_this_month: number
  top_shared_content: any[]
  most_active_users: any[]
  engagement_metrics: {
    total_likes: number
    total_shares: number
    total_comments: number
    total_views: number
  }
}

export interface GroupStats {
  total_groups: number
  total_members: number
  total_posts: number
  groups_by_type: Record<string, number>
  groups_by_privacy: Record<string, number>
  most_active_groups: any[]
  recent_activity: any[]
}

export class SocialSharingApiService {
  // Platforms
  static async getPlatforms(): Promise<SocialPlatform[]> {
    const response = await api.get('/social/platforms/')
    return response.data.results || response.data
  }

  static async getPlatform(id: number): Promise<SocialPlatform> {
    const response = await api.get(`/social/platforms/${id}/`)
    return response.data
  }

  static async createPlatform(data: Partial<SocialPlatform>): Promise<SocialPlatform> {
    const response = await api.post('/social/platforms/', data)
    return response.data
  }

  static async updatePlatform(id: number, data: Partial<SocialPlatform>): Promise<SocialPlatform> {
    const response = await api.patch(`/social/platforms/${id}/`, data)
    return response.data
  }

  static async deletePlatform(id: number): Promise<void> {
    await api.delete(`/social/platforms/${id}/`)
  }

  // Templates
  static async getTemplates(params?: {
    platform?: number
    type?: string
  }): Promise<ShareTemplate[]> {
    const response = await api.get('/social/templates/', { params })
    return response.data.results || response.data
  }

  static async getTemplate(id: number): Promise<ShareTemplate> {
    const response = await api.get(`/social/templates/${id}/`)
    return response.data
  }

  static async createTemplate(data: Partial<ShareTemplate>): Promise<ShareTemplate> {
    const response = await api.post('/social/templates/', data)
    return response.data
  }

  static async updateTemplate(id: number, data: Partial<ShareTemplate>): Promise<ShareTemplate> {
    const response = await api.patch(`/social/templates/${id}/`, data)
    return response.data
  }

  static async deleteTemplate(id: number): Promise<void> {
    await api.delete(`/social/templates/${id}/`)
  }

  // Shares
  static async getShares(params?: {
    platform?: number
    status?: string
    page?: number
  }): Promise<{ results: SocialShare[]; count: number }> {
    const response = await api.get('/social/shares/', { params })
    return response.data
  }

  static async getShare(id: number): Promise<SocialShare> {
    const response = await api.get(`/social/shares/${id}/`)
    return response.data
  }

  static async createShare(data: Partial<SocialShare>): Promise<SocialShare> {
    const response = await api.post('/social/shares/', data)
    return response.data
  }

  static async updateShare(id: number, data: Partial<SocialShare>): Promise<SocialShare> {
    const response = await api.patch(`/social/shares/${id}/`, data)
    return response.data
  }

  static async deleteShare(id: number): Promise<void> {
    await api.delete(`/social/shares/${id}/`)
  }

  // Statistics
  static async getSharingStats(): Promise<SocialSharingStats> {
    const response = await api.get('/social/shares/stats/')
    return response.data
  }
}

export class GroupsApiService {
  // Groups
  static async getGroups(params?: {
    type?: string
    page?: number
  }): Promise<{ results: PrivateGroup[]; count: number }> {
    const response = await api.get('/social/groups/', { params })
    return response.data
  }

  static async getGroup(id: number): Promise<PrivateGroup> {
    const response = await api.get(`/social/groups/${id}/`)
    return response.data
  }

  static async createGroup(data: Partial<PrivateGroup>): Promise<PrivateGroup> {
    const response = await api.post('/social/groups/', data)
    return response.data
  }

  static async updateGroup(id: number, data: Partial<PrivateGroup>): Promise<PrivateGroup> {
    const response = await api.patch(`/social/groups/${id}/`, data)
    return response.data
  }

  static async deleteGroup(id: number): Promise<void> {
    await api.delete(`/social/groups/${id}/`)
  }

  static async joinGroup(id: number): Promise<GroupMembership> {
    const response = await api.post(`/social/groups/${id}/join/`)
    return response.data
  }

  static async leaveGroup(id: number): Promise<{ message: string }> {
    const response = await api.post(`/social/groups/${id}/leave/`)
    return response.data
  }

  // Memberships
  static async getMemberships(params?: {
    group?: number
    user?: number
    page?: number
  }): Promise<{ results: GroupMembership[]; count: number }> {
    const response = await api.get('/social/memberships/', { params })
    return response.data
  }

  static async getMembership(id: number): Promise<GroupMembership> {
    const response = await api.get(`/social/memberships/${id}/`)
    return response.data
  }

  static async updateMembership(id: number, data: Partial<GroupMembership>): Promise<GroupMembership> {
    const response = await api.patch(`/social/memberships/${id}/`, data)
    return response.data
  }

  static async deleteMembership(id: number): Promise<void> {
    await api.delete(`/social/memberships/${id}/`)
  }

  // Posts
  static async getPosts(params?: {
    group?: number
    page?: number
  }): Promise<{ results: GroupPost[]; count: number }> {
    const response = await api.get('/social/posts/', { params })
    return response.data
  }

  static async getPost(id: number): Promise<GroupPost> {
    const response = await api.get(`/social/posts/${id}/`)
    return response.data
  }

  static async createPost(data: Partial<GroupPost>): Promise<GroupPost> {
    const response = await api.post('/social/posts/', data)
    return response.data
  }

  static async updatePost(id: number, data: Partial<GroupPost>): Promise<GroupPost> {
    const response = await api.patch(`/social/posts/${id}/`, data)
    return response.data
  }

  static async deletePost(id: number): Promise<void> {
    await api.delete(`/social/posts/${id}/`)
  }

  // Invitations
  static async getInvitations(): Promise<GroupInvitation[]> {
    const response = await api.get('/social/invitations/')
    return response.data.results || response.data
  }

  static async getPendingInvitations(): Promise<GroupInvitation[]> {
    const response = await api.get('/social/invitations/pending/')
    return response.data
  }

  static async createInvitation(data: {
    group: number
    invitee_username: string
    message?: string
    expires_at: string
  }): Promise<GroupInvitation> {
    const response = await api.post('/social/invitations/', data)
    return response.data
  }

  static async acceptInvitation(id: number): Promise<GroupMembership> {
    const response = await api.post(`/social/invitations/${id}/accept/`)
    return response.data
  }

  static async declineInvitation(id: number, message?: string): Promise<{ message: string }> {
    const response = await api.post(`/social/invitations/${id}/decline/`, { message })
    return response.data
  }

  // Statistics
  static async getGroupStats(): Promise<GroupStats> {
    const response = await api.get('/social/groups/stats/')
    return response.data
  }
}

export default {
  SocialSharingApiService,
  GroupsApiService
}
