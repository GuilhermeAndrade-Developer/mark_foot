import { defineStore } from 'pinia'
import { pollsApi } from '@/services/pollsApi'
import type { PollsStats, Poll, PollFormData, PollResults } from '@/types/polls'

export const usePollsStore = defineStore('polls', {
  state: () => ({
    // Estado das estatísticas
    stats: null as PollsStats | null,
    loadingStats: false,
    
    // Estado das enquetes
    polls: [] as Poll[],
    pollsCount: 0,
    currentPoll: null as Poll | null,
    loadingPolls: false,
    
    // Resultados
    pollResults: null as PollResults | null,
    loadingResults: false,
    
    // Paginação e filtros
    currentPage: 1,
    totalPages: 1,
    filters: {
      status: '',
      author: '',
      featured: undefined as boolean | undefined,
      search: ''
    },
    
    // Estado da UI
    showPollDialog: false,
    showResultsDialog: false,
    editingPoll: null as Poll | null,
    
    // Errors
    error: null as string | null
  }),

  getters: {
    activePolls: (state) => state.polls.filter(poll => poll.status === 'active'),
    closedPolls: (state) => state.polls.filter(poll => poll.status === 'closed'),
    featuredPolls: (state) => state.polls.filter(poll => poll.is_featured),
    draftPolls: (state) => state.polls.filter(poll => poll.status === 'draft'),
    
    getPollById: (state) => (id: number) => 
      state.polls.find(poll => poll.id === id),
    
    // Estatísticas computadas
    totalVotes: (state) => state.polls.reduce((total, poll) => total + poll.total_votes, 0),
    averageParticipation: (state) => {
      if (state.polls.length === 0) return 0
      const totalParticipation = state.polls.reduce((total, poll) => total + poll.participation_rate, 0)
      return Math.round(totalParticipation / state.polls.length)
    }
  },

  actions: {
    // Estatísticas
    async fetchStats() {
      this.loadingStats = true
      this.error = null
      try {
        this.stats = await pollsApi.getStats()
      } catch (error) {
        this.error = 'Erro ao carregar estatísticas'
        console.error(error)
      } finally {
        this.loadingStats = false
      }
    },

    // Enquetes
    async fetchPolls(page = 1) {
      this.loadingPolls = true
      this.error = null
      try {
        const response = await pollsApi.getPolls({
          page,
          ...this.filters
        })
        this.polls = response.results
        this.pollsCount = response.count
        this.currentPage = page
        this.totalPages = Math.ceil(response.count / 50) // 50 é o page size do backend
      } catch (error) {
        this.error = 'Erro ao carregar enquetes'
        console.error(error)
      } finally {
        this.loadingPolls = false
      }
    },

    async fetchPoll(id: number) {
      try {
        this.currentPoll = await pollsApi.getPoll(id)
        return this.currentPoll
      } catch (error) {
        this.error = 'Erro ao carregar enquete'
        throw error
      }
    },

    async createPoll(data: PollFormData) {
      try {
        const newPoll = await pollsApi.createPoll(data)
        this.polls.unshift(newPoll)
        return newPoll
      } catch (error) {
        this.error = 'Erro ao criar enquete'
        throw error
      }
    },

    async updatePoll(id: number, data: Partial<PollFormData>) {
      try {
        const updatedPoll = await pollsApi.updatePoll(id, data)
        const index = this.polls.findIndex(poll => poll.id === id)
        if (index !== -1) {
          this.polls[index] = updatedPoll
        }
        return updatedPoll
      } catch (error) {
        this.error = 'Erro ao atualizar enquete'
        throw error
      }
    },

    async deletePoll(id: number) {
      try {
        await pollsApi.deletePoll(id)
        this.polls = this.polls.filter(poll => poll.id !== id)
      } catch (error) {
        this.error = 'Erro ao deletar enquete'
        throw error
      }
    },

    async votePoll(id: number, optionId: number) {
      try {
        await pollsApi.votePoll(id, optionId)
        const poll = this.polls.find(p => p.id === id)
        if (poll) {
          poll.total_votes += 1
        }
      } catch (error) {
        this.error = 'Erro ao votar na enquete'
        throw error
      }
    },

    async fetchPollResults(id: number) {
      this.loadingResults = true
      try {
        this.pollResults = await pollsApi.getPollResults(id)
        return this.pollResults
      } catch (error) {
        this.error = 'Erro ao carregar resultados'
        throw error
      } finally {
        this.loadingResults = false
      }
    },

    // Filtros e busca
    setFilter(key: string, value: any) {
      (this.filters as any)[key] = value
    },

    clearFilters() {
      this.filters = {
        status: '',
        author: '',
        featured: undefined,
        search: ''
      }
    },

    // UI Actions
    openPollDialog(poll?: Poll) {
      this.editingPoll = poll || null
      this.showPollDialog = true
    },

    closePollDialog() {
      this.showPollDialog = false
      this.editingPoll = null
    },

    openResultsDialog(poll: Poll) {
      this.currentPoll = poll
      this.showResultsDialog = true
      this.fetchPollResults(poll.id)
    },

    closeResultsDialog() {
      this.showResultsDialog = false
      this.pollResults = null
    },

    // Inicialização
    async initialize() {
      await Promise.all([
        this.fetchStats(),
        this.fetchPolls()
      ])
    },

    clearError() {
      this.error = null
    }
  }
})
