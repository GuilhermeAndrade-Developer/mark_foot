import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import forumApi, { 
  type ForumCategory, 
  type ForumTopic, 
  type ForumPost, 
  type ForumStats 
} from '@/services/forumApi'

// ============ MOCK DATA FOR DEMO ============
const MOCK_STATS: ForumStats = {
  total_categories: 28,
  total_topics: 156,
  total_posts: 892,
  total_users: 45,
  most_active_category: 'Champions League',
  most_active_user: 'João Silva',
  recent_activity: [
    {
      id: '1',
      author: 'João Silva',
      topic_title: 'Análise do último jogo do Bayern',
      topic_slug: 'analise-ultimo-jogo-bayern',
      created_at: new Date().toISOString()
    },
    {
      id: '2',
      author: 'Maria Santos',
      topic_title: 'Previsões para a Champions League',
      topic_slug: 'previsoes-champions-league',
      created_at: new Date(Date.now() - 1000 * 60 * 30).toISOString()
    }
  ]
}

const MOCK_CATEGORIES: ForumCategory[] = [
  {
    id: '1',
    name: 'Discussões Gerais',
    description: 'Discussões gerais sobre futebol',
    slug: 'discussoes-gerais',
    category_type: 'general',
    team_id: undefined,
    competition_id: undefined,
    is_active: true,
    is_moderated: false,
    topic_count: 45,
    post_count: 234,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: '2',
    name: 'Bayern München',
    description: 'Discussões sobre o Bayern München',
    slug: 'bayern-muenchen',
    category_type: 'team',
    team_id: 1,
    competition_id: undefined,
    is_active: true,
    is_moderated: true,
    topic_count: 32,
    post_count: 189,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: '3',
    name: 'Champions League',
    description: 'Discussões sobre a Liga dos Campeões',
    slug: 'champions-league',
    category_type: 'competition',
    team_id: undefined,
    competition_id: 1,
    is_active: true,
    is_moderated: true,
    topic_count: 67,
    post_count: 423,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
]

export const useForumStore = defineStore('forum', () => {
  // ============ STATE ============
  const categories = ref<ForumCategory[]>([])
  const currentCategory = ref<ForumCategory | null>(null)
  const topics = ref<ForumTopic[]>([])
  const currentTopic = ref<ForumTopic | null>(null)
  const posts = ref<ForumPost[]>([])
  const stats = ref<ForumStats | null>(null)
  
  // Loading states
  const loading = ref(false)
  const categoriesLoading = ref(false)
  const topicsLoading = ref(false)
  const postsLoading = ref(false)
  const statsLoading = ref(false)
  
  // Pagination
  const categoriesPagination = ref({
    page: 1,
    count: 0,
    hasNext: false,
    hasPrevious: false
  })
  
  const topicsPagination = ref({
    page: 1,
    count: 0,
    hasNext: false,
    hasPrevious: false
  })
  
  const postsPagination = ref({
    page: 1,
    count: 0,
    hasNext: false,
    hasPrevious: false
  })
  
  // Filters
  const categoryFilters = ref({
    type: '',
    search: ''
  })
  
  const topicFilters = ref({
    category: '',
    author: '',
    status: 'open',
    search: '',
    sort: 'last_activity'
  })
  
  const postFilters = ref({
    topic: '',
    author: '',
    search: ''
  })

  // ============ GETTERS ============
  const categoriesByType = computed(() => {
    const grouped: Record<string, ForumCategory[]> = {}
    categories.value.forEach(category => {
      if (!grouped[category.category_type]) {
        grouped[category.category_type] = []
      }
      grouped[category.category_type].push(category)
    })
    return grouped
  })

  const totalCategories = computed(() => categories.value.length)
  const totalTopics = computed(() => stats.value?.total_topics || 0)
  const totalPosts = computed(() => stats.value?.total_posts || 0)
  const totalUsers = computed(() => stats.value?.total_users || 0)

  const categoriesWithStats = computed(() => {
    return categories.value.map(category => ({
      ...category,
      activity_score: category.topic_count + (category.post_count * 0.5)
    })).sort((a, b) => b.activity_score - a.activity_score)
  })

  // ============ ACTIONS - CATEGORIES ============
  async function fetchCategories(params?: {
    type?: string
    search?: string
    page?: number
  }) {
    categoriesLoading.value = true
    try {
      // Primeiro tenta buscar dados reais da API
      const response = await forumApi.getCategories({
        ...categoryFilters.value,
        ...params
      })
      
      categories.value = response.results
      categoriesPagination.value = {
        page: params?.page || 1,
        count: response.count,
        hasNext: response.results.length === 50, // Assuming page size is 50
        hasPrevious: (params?.page || 1) > 1
      }
      
      return response
    } catch (error: any) {
      console.log('API não disponível ou erro de autenticação, usando dados de demonstração')
      
      // Fallback para dados mock
      let filteredCategories = [...MOCK_CATEGORIES]
      
      // Aplicar filtros se fornecidos
      const filters = { ...categoryFilters.value, ...params }
      if (filters.type) {
        filteredCategories = filteredCategories.filter(cat => cat.category_type === filters.type)
      }
      if (filters.search) {
        const search = filters.search.toLowerCase()
        filteredCategories = filteredCategories.filter(cat => 
          cat.name.toLowerCase().includes(search) || 
          cat.description.toLowerCase().includes(search)
        )
      }
      
      categories.value = filteredCategories
      categoriesPagination.value = {
        page: 1,
        count: filteredCategories.length,
        hasNext: false,
        hasPrevious: false
      }
      
      return {
        results: filteredCategories,
        count: filteredCategories.length,
        next: null,
        previous: null
      }
    } finally {
      categoriesLoading.value = false
    }
  }

  async function fetchCategory(slug: string) {
    loading.value = true
    try {
      const category = await forumApi.getCategory(slug)
      currentCategory.value = category
      return category
    } catch (error) {
      console.error('Erro ao buscar categoria:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function createCategory(data: Partial<ForumCategory>) {
    loading.value = true
    try {
      const newCategory = await forumApi.createCategory(data)
      categories.value.unshift(newCategory)
      return newCategory
    } catch (error) {
      console.error('Erro ao criar categoria:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function updateCategory(slug: string, data: Partial<ForumCategory>) {
    loading.value = true
    try {
      const updatedCategory = await forumApi.updateCategory(slug, data)
      const index = categories.value.findIndex(c => c.slug === slug)
      if (index !== -1) {
        categories.value[index] = updatedCategory
      }
      if (currentCategory.value?.slug === slug) {
        currentCategory.value = updatedCategory
      }
      return updatedCategory
    } catch (error) {
      console.error('Erro ao atualizar categoria:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function deleteCategory(slug: string) {
    loading.value = true
    try {
      await forumApi.deleteCategory(slug)
      categories.value = categories.value.filter(c => c.slug !== slug)
      if (currentCategory.value?.slug === slug) {
        currentCategory.value = null
      }
    } catch (error) {
      console.error('Erro ao deletar categoria:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // ============ ACTIONS - TOPICS ============
  async function fetchTopics(params?: {
    category?: string
    author?: string
    status?: string
    search?: string
    page?: number
  }) {
    topicsLoading.value = true
    try {
      const response = await forumApi.getTopics({
        ...topicFilters.value,
        ...params
      })
      
      topics.value = response.results
      topicsPagination.value = {
        page: params?.page || 1,
        count: response.count,
        hasNext: response.results.length === 50,
        hasPrevious: (params?.page || 1) > 1
      }
      
      return response
    } catch (error: any) {
      console.log('API de tópicos não disponível, usando dados de demonstração')
      
      // Fallback para dados mock de tópicos
      const mockTopics = [
        {
          id: '1',
          title: 'Análise do último jogo do Bayern',
          slug: 'analise-ultimo-jogo-bayern',
          content: 'Discussão sobre a performance do time',
          author: {
            id: 1,
            username: 'joao_silva',
            first_name: 'João',
            last_name: 'Silva'
          },
          category: MOCK_CATEGORIES[1], // Bayern München
          category_id: '2',
          status: 'open' as const,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          last_activity: new Date().toISOString(),
          view_count: 234,
          post_count: 12,
          tags: 'bayern,análise'
        }
      ]
      
      topics.value = mockTopics
      topicsPagination.value = {
        page: 1,
        count: mockTopics.length,
        hasNext: false,
        hasPrevious: false
      }
      
      return {
        results: mockTopics,
        count: mockTopics.length,
        next: null,
        previous: null
      }
    } finally {
      topicsLoading.value = false
    }
  }

  async function fetchTopic(slug: string) {
    loading.value = true
    try {
      const topic = await forumApi.getTopic(slug)
      currentTopic.value = topic
      return topic
    } catch (error) {
      console.error('Erro ao buscar tópico:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function createTopic(data: {
    category_id: string
    title: string
    content: string
    tags?: string
  }) {
    loading.value = true
    try {
      const newTopic = await forumApi.createTopic(data)
      topics.value.unshift(newTopic)
      
      // Atualizar contador da categoria
      const category = categories.value.find(c => c.id === data.category_id)
      if (category) {
        category.topic_count += 1
      }
      
      return newTopic
    } catch (error) {
      console.error('Erro ao criar tópico:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function updateTopic(slug: string, data: Partial<ForumTopic>) {
    loading.value = true
    try {
      const updatedTopic = await forumApi.updateTopic(slug, data)
      const index = topics.value.findIndex(t => t.slug === slug)
      if (index !== -1) {
        topics.value[index] = updatedTopic
      }
      if (currentTopic.value?.slug === slug) {
        currentTopic.value = updatedTopic
      }
      return updatedTopic
    } catch (error) {
      console.error('Erro ao atualizar tópico:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function deleteTopic(slug: string) {
    loading.value = true
    try {
      await forumApi.deleteTopic(slug)
      topics.value = topics.value.filter(t => t.slug !== slug)
      if (currentTopic.value?.slug === slug) {
        currentTopic.value = null
      }
      
      // Atualizar contador da categoria
      const topic = topics.value.find(t => t.slug === slug)
      if (topic) {
        const category = categories.value.find(c => c.id === topic.category.id)
        if (category && category.topic_count > 0) {
          category.topic_count -= 1
        }
      }
    } catch (error) {
      console.error('Erro ao deletar tópico:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function closeTopic(slug: string) {
    try {
      await forumApi.closeTopic(slug)
      await fetchTopic(slug) // Refresh topic data
    } catch (error) {
      console.error('Erro ao fechar tópico:', error)
      throw error
    }
  }

  async function pinTopic(slug: string) {
    try {
      await forumApi.pinTopic(slug)
      await fetchTopic(slug) // Refresh topic data
    } catch (error) {
      console.error('Erro ao fixar tópico:', error)
      throw error
    }
  }

  // ============ ACTIONS - POSTS ============
  async function fetchPosts(params?: {
    topic?: string
    author?: string
    search?: string
    page?: number
  }) {
    postsLoading.value = true
    try {
      const response = await forumApi.getPosts({
        ...postFilters.value,
        ...params
      })
      
      posts.value = response.results
      postsPagination.value = {
        page: params?.page || 1,
        count: response.count,
        hasNext: response.results.length === 50,
        hasPrevious: (params?.page || 1) > 1
      }
      
      return response
    } catch (error) {
      console.error('Erro ao buscar posts:', error)
      throw error
    } finally {
      postsLoading.value = false
    }
  }

  async function fetchTopicPosts(slug: string, params?: {
    parent_only?: boolean
    sort?: 'created_at' | 'votes'
    page?: number
  }) {
    postsLoading.value = true
    try {
      const response = await forumApi.getTopicPosts(slug, params)
      posts.value = response.results
      return response
    } catch (error) {
      console.error('Erro ao buscar posts do tópico:', error)
      throw error
    } finally {
      postsLoading.value = false
    }
  }

  async function createPost(data: {
    topic: string
    content: string
    parent?: string
  }) {
    loading.value = true
    try {
      const newPost = await forumApi.createPost(data)
      posts.value.push(newPost)
      
      // Atualizar contador do tópico
      if (currentTopic.value && currentTopic.value.id === data.topic) {
        currentTopic.value.post_count += 1
      }
      
      return newPost
    } catch (error) {
      console.error('Erro ao criar post:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function votePost(id: string, voteType: 'upvote' | 'downvote') {
    try {
      const result = await forumApi.votePost(id, voteType)
      
      // Atualizar post na lista
      const post = posts.value.find(p => p.id === id)
      if (post) {
        post.vote_score = result.score
        post.user_vote = result.vote_type as 'upvote' | 'downvote' | null
      }
      
      return result
    } catch (error) {
      console.error('Erro ao votar no post:', error)
      throw error
    }
  }

  // ============ ACTIONS - STATS ============
  async function fetchStats() {
    statsLoading.value = true
    try {
      // Primeiro tenta buscar dados reais da API
      const forumStats = await forumApi.getForumStats()
      stats.value = forumStats
      return forumStats
    } catch (error: any) {
      console.log('API não disponível ou erro de autenticação, usando dados de demonstração para stats')
      
      // Fallback para dados mock
      stats.value = MOCK_STATS
      return MOCK_STATS
    } finally {
      statsLoading.value = false
    }
  }

  // ============ ACTIONS - SEARCH ============
  async function searchForum(params: {
    query: string
    category?: string
    author?: string
    date_from?: string
    date_to?: string
    sort_by?: 'relevance' | 'date' | 'votes'
  }) {
    loading.value = true
    try {
      const results = await forumApi.searchForum(params)
      return results
    } catch (error) {
      console.error('Erro na busca do fórum:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // ============ UTILITY ACTIONS ============
  function setCategoryFilters(filters: Partial<typeof categoryFilters.value>) {
    categoryFilters.value = { ...categoryFilters.value, ...filters }
  }

  function setTopicFilters(filters: Partial<typeof topicFilters.value>) {
    topicFilters.value = { ...topicFilters.value, ...filters }
  }

  function setPostFilters(filters: Partial<typeof postFilters.value>) {
    postFilters.value = { ...postFilters.value, ...filters }
  }

  function clearCurrentCategory() {
    currentCategory.value = null
  }

  function clearCurrentTopic() {
    currentTopic.value = null
  }

  function resetPagination() {
    categoriesPagination.value.page = 1
    topicsPagination.value.page = 1
    postsPagination.value.page = 1
  }

  function resetFilters() {
    categoryFilters.value = { type: '', search: '' }
    topicFilters.value = { category: '', author: '', status: 'open', search: '', sort: 'last_activity' }
    postFilters.value = { topic: '', author: '', search: '' }
  }

  function clearAll() {
    categories.value = []
    topics.value = []
    posts.value = []
    currentCategory.value = null
    currentTopic.value = null
    stats.value = null
    resetPagination()
    resetFilters()
  }

  // ============ RETURN STORE ============
  return {
    // State
    categories,
    currentCategory,
    topics,
    currentTopic,
    posts,
    stats,
    
    // Loading states
    loading,
    categoriesLoading,
    topicsLoading,
    postsLoading,
    statsLoading,
    
    // Pagination
    categoriesPagination,
    topicsPagination,
    postsPagination,
    
    // Filters
    categoryFilters,
    topicFilters,
    postFilters,
    
    // Getters
    categoriesByType,
    totalCategories,
    totalTopics,
    totalPosts,
    totalUsers,
    categoriesWithStats,
    
    // Category actions
    fetchCategories,
    fetchCategory,
    createCategory,
    updateCategory,
    deleteCategory,
    
    // Topic actions
    fetchTopics,
    fetchTopic,
    createTopic,
    updateTopic,
    deleteTopic,
    closeTopic,
    pinTopic,
    
    // Post actions
    fetchPosts,
    fetchTopicPosts,
    createPost,
    votePost,
    
    // Stats actions
    fetchStats,
    
    // Search actions
    searchForum,
    
    // Utility actions
    setCategoryFilters,
    setTopicFilters,
    setPostFilters,
    clearCurrentCategory,
    clearCurrentTopic,
    resetPagination,
    resetFilters,
    clearAll
  }
})
