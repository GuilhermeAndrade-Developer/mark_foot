import type { ContentStats, ContentCategory, UserArticle, ContentApiResponse, ContentFormData } from '@/types/content'

const API_BASE_URL = 'http://localhost:8001/api'

class ContentApiService {
  private baseUrl = `${API_BASE_URL}/content`

  // Estatísticas
  async getStats(): Promise<ContentStats> {
    try {
      const response = await fetch(`${this.baseUrl}/stats/`)
      if (!response.ok) throw new Error('Erro ao buscar estatísticas')
      return await response.json()
    } catch (error) {
      console.error('Erro ao buscar estatísticas do conteúdo:', error)
      // Fallback para dados de demonstração
      return {
        total_articles: 156,
        published_articles: 142,
        pending_articles: 8,
        total_categories: 12,
        total_comments: 2847,
        total_votes: 15690,
        articles_by_category: [
          { category__name: 'Análises Táticas', count: 45 },
          { category__name: 'Mercado da Bola', count: 38 },
          { category__name: 'História do Futebol', count: 29 },
          { category__name: 'Estatísticas', count: 30 },
          { category__name: 'Opinião', count: 25 }
        ],
        popular_articles: [
          {
            id: 1,
            title: 'Análise Tática: Como o Barcelona Dominou o El Clásico',
            views: 15420,
            likes: 892,
            author__username: 'tactico_expert'
          }
        ],
        recent_activity: 23,
        engagement_rate: 78.5,
        average_read_time: 6.2
      }
    }
  }

  // Categorias
  async getCategories(params?: { is_active?: boolean }): Promise<ContentCategory[]> {
    try {
      const queryParams = new URLSearchParams()
      if (params?.is_active !== undefined) {
        queryParams.append('is_active', params.is_active.toString())
      }
      
      const response = await fetch(`${this.baseUrl}/categories/?${queryParams}`)
      if (!response.ok) throw new Error('Erro ao buscar categorias')
      return await response.json()
    } catch (error) {
      console.error('Erro ao buscar categorias:', error)
      // Fallback para dados de demonstração
      return [
        {
          id: 1,
          name: 'Análises Táticas',
          slug: 'analises-taticas',
          description: 'Análises detalhadas de jogos e formações',
          icon: 'mdi-strategy',
          is_active: true,
          articles_count: 45,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        }
      ]
    }
  }

  async createCategory(data: Partial<ContentCategory>): Promise<ContentCategory> {
    try {
      const response = await fetch(`${this.baseUrl}/categories/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      if (!response.ok) throw new Error('Erro ao criar categoria')
      return await response.json()
    } catch (error) {
      console.error('Erro ao criar categoria:', error)
      throw error
    }
  }

  async updateCategory(id: number, data: Partial<ContentCategory>): Promise<ContentCategory> {
    try {
      const response = await fetch(`${this.baseUrl}/categories/${id}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      if (!response.ok) throw new Error('Erro ao atualizar categoria')
      return await response.json()
    } catch (error) {
      console.error('Erro ao atualizar categoria:', error)
      throw error
    }
  }

  async deleteCategory(id: number): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/categories/${id}/`, {
        method: 'DELETE'
      })
      if (!response.ok) throw new Error('Erro ao deletar categoria')
    } catch (error) {
      console.error('Erro ao deletar categoria:', error)
      throw error
    }
  }

  // Artigos
  async getArticles(params?: {
    page?: number
    status?: string
    category?: string
    author?: string
    featured?: boolean
    search?: string
  }): Promise<ContentApiResponse<UserArticle>> {
    try {
      const queryParams = new URLSearchParams()
      if (params?.page) queryParams.append('page', params.page.toString())
      if (params?.status) queryParams.append('status', params.status)
      if (params?.category) queryParams.append('category', params.category)
      if (params?.author) queryParams.append('author', params.author)
      if (params?.featured !== undefined) queryParams.append('featured', params.featured.toString())
      if (params?.search) queryParams.append('search', params.search)
      
      const response = await fetch(`${this.baseUrl}/articles/?${queryParams}`)
      if (!response.ok) throw new Error('Erro ao buscar artigos')
      return await response.json()
    } catch (error) {
      console.error('Erro ao buscar artigos:', error)
      // Fallback para dados de demonstração
      return {
        count: 0,
        next: null,
        previous: null,
        results: []
      }
    }
  }

  async getArticle(id: number): Promise<UserArticle> {
    try {
      const response = await fetch(`${this.baseUrl}/articles/${id}/`)
      if (!response.ok) throw new Error('Erro ao buscar artigo')
      return await response.json()
    } catch (error) {
      console.error('Erro ao buscar artigo:', error)
      throw error
    }
  }

  async createArticle(data: ContentFormData): Promise<UserArticle> {
    try {
      const response = await fetch(`${this.baseUrl}/articles/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      if (!response.ok) throw new Error('Erro ao criar artigo')
      return await response.json()
    } catch (error) {
      console.error('Erro ao criar artigo:', error)
      throw error
    }
  }

  async updateArticle(id: number, data: Partial<ContentFormData>): Promise<UserArticle> {
    try {
      const response = await fetch(`${this.baseUrl}/articles/${id}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      if (!response.ok) throw new Error('Erro ao atualizar artigo')
      return await response.json()
    } catch (error) {
      console.error('Erro ao atualizar artigo:', error)
      throw error
    }
  }

  async deleteArticle(id: number): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/articles/${id}/`, {
        method: 'DELETE'
      })
      if (!response.ok) throw new Error('Erro ao deletar artigo')
    } catch (error) {
      console.error('Erro ao deletar artigo:', error)
      throw error
    }
  }

  async voteArticle(id: number, voteType: 'like' | 'dislike'): Promise<{ message: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/articles/${id}/vote/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ vote_type: voteType })
      })
      if (!response.ok) throw new Error('Erro ao votar no artigo')
      return await response.json()
    } catch (error) {
      console.error('Erro ao votar no artigo:', error)
      throw error
    }
  }
}

export const contentApi = new ContentApiService()
