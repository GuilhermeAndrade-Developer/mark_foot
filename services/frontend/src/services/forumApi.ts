import axios from 'axios'

// Create axios instance for forum API
const forumApiClient = axios.create({
  baseURL: 'http://localhost:8001/api/forum',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for auth
forumApiClient.interceptors.request.use(
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

// Interfaces TypeScript
export interface ForumCategory {
  id: string
  name: string
  description: string
  slug: string
  category_type: 'team' | 'competition' | 'general' | 'news' | 'analysis'
  team_id?: number
  competition_id?: number
  is_active: boolean
  is_moderated: boolean
  created_at: string
  updated_at: string
  topic_count: number
  post_count: number
}

export interface ForumTopic {
  id: string
  title: string
  slug: string
  content: string
  author: {
    id: number
    username: string
    first_name: string
    last_name: string
  }
  category: ForumCategory
  category_id: string
  status: 'open' | 'closed' | 'pinned' | 'locked'
  created_at: string
  updated_at: string
  last_activity: string
  view_count: number
  post_count: number
  tags: string
}

export interface ForumPost {
  id: string
  topic: string
  content: string
  author: {
    id: number
    username: string
    first_name: string
    last_name: string
  }
  topic_title: string
  parent?: string
  created_at: string
  updated_at: string
  is_edited: boolean
  is_deleted: boolean
  is_reported: boolean
  position: number
  vote_score: number
  user_vote?: 'upvote' | 'downvote' | null
  replies_count: number
}

export interface ForumStats {
  total_categories: number
  total_topics: number
  total_posts: number
  total_users: number
  most_active_category: string
  most_active_user: string
  recent_activity: Array<{
    id: string
    author: string
    topic_title: string
    topic_slug: string
    created_at: string
  }>
}

export interface ForumUserProfile {
  user: {
    id: number
    username: string
    first_name: string
    last_name: string
    date_joined: string
  }
  total_posts: number
  total_topics: number
  reputation_score: number
  signature: string
  receive_notifications: boolean
  joined_at: string
  last_seen: string
}

// Service class para API do fórum
class ForumApiService {
  // ============ CATEGORIAS ============
  async getCategories(params?: {
    type?: string
    search?: string
    page?: number
  }): Promise<{ results: ForumCategory[], count: number }> {
    const response = await forumApiClient.get('/categories/', { params })
    return response.data
  }

  async getCategory(slug: string): Promise<ForumCategory> {
    const response = await forumApiClient.get(`/categories/${slug}/`)
    return response.data
  }

  async createCategory(data: Partial<ForumCategory>): Promise<ForumCategory> {
    const response = await forumApiClient.post('/categories/', data)
    return response.data
  }

  async updateCategory(slug: string, data: Partial<ForumCategory>): Promise<ForumCategory> {
    const response = await forumApiClient.put(`/categories/${slug}/`, data)
    return response.data
  }

  async deleteCategory(slug: string): Promise<void> {
    await forumApiClient.delete(`/categories/${slug}/`)
  }

  async getCategoryTopics(slug: string, params?: {
    search?: string
    sort?: 'latest' | 'popular' | 'posts' | 'last_activity'
    page?: number
  }): Promise<{ results: ForumTopic[], count: number }> {
    const response = await forumApiClient.get(`/categories/${slug}/topics/`, { params })
    return response.data
  }

  async getCategoryStats(): Promise<Array<{
    id: string
    name: string
    type: string
    topic_count: number
    post_count: number
  }>> {
    const response = await forumApiClient.get('/categories/stats/')
    return response.data
  }

  // ============ TÓPICOS ============
  async getTopics(params?: {
    category?: string
    author?: string
    status?: string
    search?: string
    page?: number
  }): Promise<{ results: ForumTopic[], count: number }> {
    const response = await forumApiClient.get('/topics/', { params })
    return response.data
  }

  async getTopic(slug: string): Promise<ForumTopic> {
    const response = await forumApiClient.get(`/topics/${slug}/`)
    return response.data
  }

  async createTopic(data: {
    category_id: string
    title: string
    content: string
    tags?: string
    slug?: string
  }): Promise<ForumTopic> {
    const response = await forumApiClient.post('/topics/', data)
    return response.data
  }

  async updateTopic(slug: string, data: Partial<ForumTopic>): Promise<ForumTopic> {
    const response = await forumApiClient.put(`/topics/${slug}/`, data)
    return response.data
  }

  async deleteTopic(slug: string): Promise<void> {
    await forumApiClient.delete(`/topics/${slug}/`)
  }

  async getTopicPosts(slug: string, params?: {
    parent_only?: boolean
    sort?: 'created_at' | 'votes'
    page?: number
  }): Promise<{ results: ForumPost[], count: number }> {
    const response = await forumApiClient.get(`/topics/${slug}/posts/`, { params })
    return response.data
  }

  async closeTopic(slug: string): Promise<{ message: string }> {
    const response = await forumApiClient.post(`/topics/${slug}/close/`)
    return response.data
  }

  async pinTopic(slug: string): Promise<{ message: string }> {
    const response = await forumApiClient.post(`/topics/${slug}/pin/`)
    return response.data
  }

  // ============ POSTS ============
  async getPosts(params?: {
    topic?: string
    author?: string
    search?: string
    page?: number
  }): Promise<{ results: ForumPost[], count: number }> {
    const response = await forumApiClient.get('/posts/', { params })
    return response.data
  }

  async getPost(id: string): Promise<ForumPost> {
    const response = await forumApiClient.get(`/posts/${id}/`)
    return response.data
  }

  async createPost(data: {
    topic: string
    content: string
    parent?: string
  }): Promise<ForumPost> {
    const response = await forumApiClient.post('/posts/', data)
    return response.data
  }

  async updatePost(id: string, data: { content: string }): Promise<ForumPost> {
    const response = await forumApiClient.put(`/posts/${id}/`, data)
    return response.data
  }

  async deletePost(id: string): Promise<void> {
    await forumApiClient.delete(`/posts/${id}/`)
  }

  async votePost(id: string, voteType: 'upvote' | 'downvote'): Promise<{
    vote_type: string | null
    score: number
    message: string
  }> {
    const response = await forumApiClient.post(`/posts/${id}/vote/`, {
      vote_type: voteType
    })
    return response.data
  }

  async getPostReplies(id: string): Promise<ForumPost[]> {
    const response = await forumApiClient.get(`/posts/${id}/replies/`)
    return response.data
  }

  async reportPost(id: string): Promise<{ message: string }> {
    const response = await forumApiClient.post(`/posts/${id}/report/`)
    return response.data
  }

  // ============ ESTATÍSTICAS ============
  async getForumStats(): Promise<ForumStats> {
    const response = await forumApiClient.get('/stats/')
    return response.data
  }

  // ============ BUSCA ============
  async searchForum(params: {
    query: string
    category?: string
    author?: string
    date_from?: string
    date_to?: string
    sort_by?: 'relevance' | 'date' | 'votes'
  }): Promise<{
    topics: ForumTopic[]
    posts: ForumPost[]
    total_topics: number
    total_posts: number
  }> {
    const response = await forumApiClient.get('/search/', { params })
    return response.data
  }

  // ============ PERFIS DE USUÁRIO ============
  async getUserProfile(username: string): Promise<ForumUserProfile> {
    const response = await forumApiClient.get(`/profiles/${username}/`)
    return response.data
  }

  async getUserActivity(username: string): Promise<{
    recent_posts: ForumPost[]
    recent_topics: ForumTopic[]
  }> {
    const response = await forumApiClient.get(`/profiles/${username}/activity/`)
    return response.data
  }

  // ============ MODERAÇÃO (Admin Dashboard) ============
  async getModerationQueue(): Promise<{
    reported_posts: ForumPost[]
    pending_topics: ForumTopic[]
    flagged_users: ForumUserProfile[]
  }> {
    try {
      // Buscar posts reportados
      const reportedPosts = await this.getPosts({ 
        search: 'is_reported:true' 
      })
      
      // Buscar tópicos pendentes (implementação futura)
      const pendingTopics = await this.getTopics({ 
        status: 'pending' 
      })
      
      return {
        reported_posts: reportedPosts.results || [],
        pending_topics: pendingTopics.results || [],
        flagged_users: [] // Implementação futura
      }
    } catch (error) {
      console.error('Erro ao buscar fila de moderação:', error)
      return {
        reported_posts: [],
        pending_topics: [],
        flagged_users: []
      }
    }
  }

  // ============ UTILITÁRIOS ============
  formatDate(dateString: string): string {
    const date = new Date(dateString)
    return date.toLocaleDateString('pt-BR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  truncateText(text: string, maxLength: number = 100): string {
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength) + '...'
  }

  getCategoryTypeLabel(type: string): string {
    const labels = {
      'team': 'Time',
      'competition': 'Competição',
      'general': 'Geral',
      'news': 'Notícias',
      'analysis': 'Análises'
    }
    return labels[type as keyof typeof labels] || type
  }

  getStatusLabel(status: string): string {
    const labels = {
      'open': 'Aberto',
      'closed': 'Fechado',
      'pinned': 'Fixo',
      'locked': 'Bloqueado'
    }
    return labels[status as keyof typeof labels] || status
  }

  getStatusColor(status: string): string {
    const colors = {
      'open': 'success',
      'closed': 'warning',
      'pinned': 'info',
      'locked': 'error'
    }
    return colors[status as keyof typeof colors] || 'default'
  }
}

// Instância única do serviço
export const forumApi = new ForumApiService()
export default forumApi
