import type { PollsStats, Poll, PollsApiResponse, PollFormData, PollResults } from '@/types/polls'

const API_BASE_URL = 'http://localhost:8001/api'

class PollsApiService {
  private baseUrl = `${API_BASE_URL}/polls`

  // Estatísticas
  async getStats(): Promise<PollsStats> {
    try {
      const response = await fetch(`${this.baseUrl}/stats/`)
      if (!response.ok) throw new Error('Erro ao buscar estatísticas')
      return await response.json()
    } catch (error) {
      console.error('Erro ao buscar estatísticas das enquetes:', error)
      // Fallback para dados de demonstração
      return {
        total_polls: 89,
        active_polls: 15,
        closed_polls: 67,
        total_votes: 12543,
        total_comments: 1876,
        popular_polls: [
          {
            id: 1,
            title: 'Qual é o melhor jogador do mundo atual?',
            total_votes: 8745,
            views: 15230,
            author__username: 'poll_master'
          },
          {
            id: 2,
            title: 'Melhor formação tática para 2024?',
            total_votes: 6892,
            views: 12100,
            author__username: 'tactics_guru'
          }
        ],
        recent_polls: 8,
        recent_votes: 456,
        participation_rate: 67.8,
        average_votes_per_poll: 140.9
      }
    }
  }

  // Enquetes
  async getPolls(params?: {
    page?: number
    status?: string
    author?: string
    featured?: boolean
    search?: string
  }): Promise<PollsApiResponse<Poll>> {
    try {
      const queryParams = new URLSearchParams()
      if (params?.page) queryParams.append('page', params.page.toString())
      if (params?.status) queryParams.append('status', params.status)
      if (params?.author) queryParams.append('author', params.author)
      if (params?.featured !== undefined) queryParams.append('featured', params.featured.toString())
      if (params?.search) queryParams.append('search', params.search)
      
      const response = await fetch(`${this.baseUrl}/polls/?${queryParams}`)
      if (!response.ok) throw new Error('Erro ao buscar enquetes')
      return await response.json()
    } catch (error) {
      console.error('Erro ao buscar enquetes:', error)
      // Fallback para dados de demonstração
      return {
        count: 0,
        next: null,
        previous: null,
        results: []
      }
    }
  }

  async getPoll(id: number): Promise<Poll> {
    try {
      const response = await fetch(`${this.baseUrl}/polls/${id}/`)
      if (!response.ok) throw new Error('Erro ao buscar enquete')
      return await response.json()
    } catch (error) {
      console.error('Erro ao buscar enquete:', error)
      throw error
    }
  }

  async createPoll(data: PollFormData): Promise<Poll> {
    try {
      const response = await fetch(`${this.baseUrl}/polls/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      if (!response.ok) throw new Error('Erro ao criar enquete')
      return await response.json()
    } catch (error) {
      console.error('Erro ao criar enquete:', error)
      throw error
    }
  }

  async updatePoll(id: number, data: Partial<PollFormData>): Promise<Poll> {
    try {
      const response = await fetch(`${this.baseUrl}/polls/${id}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      if (!response.ok) throw new Error('Erro ao atualizar enquete')
      return await response.json()
    } catch (error) {
      console.error('Erro ao atualizar enquete:', error)
      throw error
    }
  }

  async deletePoll(id: number): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/polls/${id}/`, {
        method: 'DELETE'
      })
      if (!response.ok) throw new Error('Erro ao deletar enquete')
    } catch (error) {
      console.error('Erro ao deletar enquete:', error)
      throw error
    }
  }

  async votePoll(id: number, optionId: number): Promise<{ message: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/polls/${id}/vote/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ option_id: optionId })
      })
      if (!response.ok) throw new Error('Erro ao votar na enquete')
      return await response.json()
    } catch (error) {
      console.error('Erro ao votar na enquete:', error)
      throw error
    }
  }

  async getPollResults(id: number): Promise<PollResults> {
    try {
      const response = await fetch(`${this.baseUrl}/polls/${id}/results/`)
      if (!response.ok) throw new Error('Erro ao buscar resultados')
      return await response.json()
    } catch (error) {
      console.error('Erro ao buscar resultados da enquete:', error)
      throw error
    }
  }
}

export const pollsApi = new PollsApiService()
