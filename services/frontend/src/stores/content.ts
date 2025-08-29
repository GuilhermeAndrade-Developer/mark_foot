import { defineStore } from 'pinia'
import { contentApi } from '@/services/contentApi'
import type { ContentStats, ContentCategory, UserArticle, ContentFormData } from '@/types/content'

export const useContentStore = defineStore('content', {
  state: () => ({
    // Estado das estatísticas
    stats: null as ContentStats | null,
    loadingStats: false,
    
    // Estado das categorias
    categories: [] as ContentCategory[],
    loadingCategories: false,
    
    // Estado dos artigos
    articles: [] as UserArticle[],
    articlesCount: 0,
    currentArticle: null as UserArticle | null,
    loadingArticles: false,
    
    // Paginação e filtros
    currentPage: 1,
    totalPages: 1,
    filters: {
      status: '',
      category: '',
      author: '',
      featured: undefined as boolean | undefined,
      search: ''
    },
    
    // Estado da UI
    showArticleDialog: false,
    showCategoryDialog: false,
    editingArticle: null as UserArticle | null,
    editingCategory: null as ContentCategory | null,
    
    // Errors
    error: null as string | null
  }),

  getters: {
    publishedArticles: (state) => state.articles.filter(article => article.status === 'published'),
    pendingArticles: (state) => state.articles.filter(article => article.status === 'pending'),
    featuredArticles: (state) => state.articles.filter(article => article.is_featured),
    activeCategories: (state) => state.categories.filter(category => category.is_active),
    
    getArticlesByCategory: (state) => (categorySlug: string) => 
      state.articles.filter(article => article.category.slug === categorySlug),
    
    getArticleById: (state) => (id: number) => 
      state.articles.find(article => article.id === id),
    
    getCategoryById: (state) => (id: number) => 
      state.categories.find(category => category.id === id)
  },

  actions: {
    // Estatísticas
    async fetchStats() {
      this.loadingStats = true
      this.error = null
      try {
        this.stats = await contentApi.getStats()
      } catch (error) {
        this.error = 'Erro ao carregar estatísticas'
        console.error(error)
      } finally {
        this.loadingStats = false
      }
    },

    // Categorias
    async fetchCategories(isActive?: boolean) {
      this.loadingCategories = true
      this.error = null
      try {
        this.categories = await contentApi.getCategories({ is_active: isActive })
      } catch (error) {
        this.error = 'Erro ao carregar categorias'
        console.error(error)
      } finally {
        this.loadingCategories = false
      }
    },

    async createCategory(data: Partial<ContentCategory>) {
      try {
        const newCategory = await contentApi.createCategory(data)
        this.categories.push(newCategory)
        return newCategory
      } catch (error) {
        this.error = 'Erro ao criar categoria'
        throw error
      }
    },

    async updateCategory(id: number, data: Partial<ContentCategory>) {
      try {
        const updatedCategory = await contentApi.updateCategory(id, data)
        const index = this.categories.findIndex(cat => cat.id === id)
        if (index !== -1) {
          this.categories[index] = updatedCategory
        }
        return updatedCategory
      } catch (error) {
        this.error = 'Erro ao atualizar categoria'
        throw error
      }
    },

    async deleteCategory(id: number) {
      try {
        await contentApi.deleteCategory(id)
        this.categories = this.categories.filter(cat => cat.id !== id)
      } catch (error) {
        this.error = 'Erro ao deletar categoria'
        throw error
      }
    },

    // Artigos
    async fetchArticles(page = 1) {
      this.loadingArticles = true
      this.error = null
      try {
        const response = await contentApi.getArticles({
          page,
          ...this.filters
        })
        this.articles = response.results
        this.articlesCount = response.count
        this.currentPage = page
        this.totalPages = Math.ceil(response.count / 50) // 50 é o page size do backend
      } catch (error) {
        this.error = 'Erro ao carregar artigos'
        console.error(error)
      } finally {
        this.loadingArticles = false
      }
    },

    async fetchArticle(id: number) {
      try {
        this.currentArticle = await contentApi.getArticle(id)
        return this.currentArticle
      } catch (error) {
        this.error = 'Erro ao carregar artigo'
        throw error
      }
    },

    async createArticle(data: ContentFormData) {
      try {
        const newArticle = await contentApi.createArticle(data)
        this.articles.unshift(newArticle)
        return newArticle
      } catch (error) {
        this.error = 'Erro ao criar artigo'
        throw error
      }
    },

    async updateArticle(id: number, data: Partial<ContentFormData>) {
      try {
        const updatedArticle = await contentApi.updateArticle(id, data)
        const index = this.articles.findIndex(article => article.id === id)
        if (index !== -1) {
          this.articles[index] = updatedArticle
        }
        return updatedArticle
      } catch (error) {
        this.error = 'Erro ao atualizar artigo'
        throw error
      }
    },

    async deleteArticle(id: number) {
      try {
        await contentApi.deleteArticle(id)
        this.articles = this.articles.filter(article => article.id !== id)
      } catch (error) {
        this.error = 'Erro ao deletar artigo'
        throw error
      }
    },

    async voteArticle(id: number, voteType: 'like' | 'dislike') {
      try {
        await contentApi.voteArticle(id, voteType)
        const article = this.articles.find(a => a.id === id)
        if (article) {
          if (voteType === 'like') {
            article.likes += 1
          } else {
            article.dislikes += 1
          }
        }
      } catch (error) {
        this.error = 'Erro ao votar no artigo'
        throw error
      }
    },

    // Filtros e busca
    setFilter(key: string, value: any) {
      (this.filters as any)[key] = value
    },

    clearFilters() {
      this.filters = {
        status: '',
        category: '',
        author: '',
        featured: undefined,
        search: ''
      }
    },

    // UI Actions
    openArticleDialog(article?: UserArticle) {
      this.editingArticle = article || null
      this.showArticleDialog = true
    },

    closeArticleDialog() {
      this.showArticleDialog = false
      this.editingArticle = null
    },

    openCategoryDialog(category?: ContentCategory) {
      this.editingCategory = category || null
      this.showCategoryDialog = true
    },

    closeCategoryDialog() {
      this.showCategoryDialog = false
      this.editingCategory = null
    },

    // Inicialização
    async initialize() {
      await Promise.all([
        this.fetchStats(),
        this.fetchCategories(),
        this.fetchArticles()
      ])
    },

    clearError() {
      this.error = null
    }
  }
})
