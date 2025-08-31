<template>
  <v-container fluid>
    <!-- Header da página -->
    <v-row class="mb-4">
      <v-col>
        <div class="d-flex align-center justify-space-between">
          <div>
            <h1 class="text-h4 font-weight-bold">Gerenciar Artigos</h1>
            <p class="text-body-1 text-medium-emphasis mt-1">
              Gerencie todos os artigos criados pelos usuários
            </p>
          </div>
          <v-btn
            color="primary"
            prepend-icon="mdi-plus"
            @click="openCreateDialog"
          >
            Novo Artigo
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- Filtros -->
    <v-row class="mb-4">
      <v-col cols="12" md="3">
        <v-select
          v-model="statusFilter"
          :items="statusOptions"
          label="Status"
          clearable
          variant="outlined"
          density="compact"
          @update:model-value="applyFilters"
        />
      </v-col>
      
      <v-col cols="12" md="3">
        <v-select
          v-model="categoryFilter"
          :items="categoryOptions"
          label="Categoria"
          clearable
          variant="outlined"
          density="compact"
          @update:model-value="applyFilters"
        />
      </v-col>
      
      <v-col cols="12" md="3">
        <v-switch
          v-model="featuredFilter"
          label="Apenas Destacados"
          density="compact"
          @update:model-value="applyFilters"
        />
      </v-col>
      
      <v-col cols="12" md="3">
        <v-text-field
          v-model="searchQuery"
          label="Buscar artigos..."
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          density="compact"
          clearable
          @update:model-value="debounceSearch"
        />
      </v-col>
    </v-row>

    <!-- Data Table -->
    <v-card>
      <v-data-table-server
        v-model:items-per-page="itemsPerPage"
        v-model:page="currentPage"
        :headers="headers"
        :items="articles"
        :items-length="totalItems"
        :loading="loading"
        :search="searchQuery"
        class="elevation-0"
        @update:options="loadItems"
      >
        <!-- Título do artigo -->
        <template #item.title="{ item }">
          <div class="d-flex align-center">
            <v-avatar
              v-if="item.featured_image"
              size="40"
              class="mr-3"
            >
              <v-img :src="item.featured_image" />
            </v-avatar>
            <v-icon
              v-else
              class="mr-3"
              color="grey-lighten-1"
            >
              mdi-file-document
            </v-icon>
            <div>
              <div class="font-weight-medium">{{ item.title }}</div>
              <div class="text-caption text-grey">{{ item.excerpt }}</div>
            </div>
          </div>
        </template>

        <!-- Autor -->
        <template #item.author="{ item }">
          <div class="d-flex align-center">
            <v-avatar size="28" class="mr-2">
              <v-icon>mdi-account</v-icon>
            </v-avatar>
            <div>
              <div class="text-body-2">{{ item.author.full_name }}</div>
              <div class="text-caption text-grey">{{ item.author.username }}</div>
            </div>
          </div>
        </template>

        <!-- Categoria -->
        <template #item.category="{ item }">
          <v-chip
            :color="getCategoryColor(item.category.name)"
            variant="tonal"
            size="small"
          >
            <v-icon start :icon="item.category.icon" />
            {{ item.category.name }}
          </v-chip>
        </template>

        <!-- Status -->
        <template #item.status="{ item }">
          <v-chip
            :color="getStatusColor(item.status)"
            :icon="getStatusIcon(item.status)"
            variant="tonal"
            size="small"
          >
            {{ getStatusText(item.status) }}
          </v-chip>
        </template>

        <!-- Tags -->
        <template #item.tags="{ item }">
          <div class="d-flex flex-wrap ga-1">
            <v-chip
              v-for="tag in item.tags_list.slice(0, 2)"
              :key="tag"
              size="x-small"
              variant="outlined"
            >
              {{ tag }}
            </v-chip>
            <v-chip
              v-if="item.tags_list.length > 2"
              size="x-small"
              variant="text"
            >
              +{{ item.tags_list.length - 2 }}
            </v-chip>
          </div>
        </template>

        <!-- Métricas -->
        <template #item.metrics="{ item }">
          <div class="text-center">
            <div class="d-flex align-center justify-center mb-1">
              <v-icon size="16" class="mr-1">mdi-eye</v-icon>
              <span class="text-caption">{{ formatNumber(item.views) }}</span>
            </div>
            <div class="d-flex align-center justify-center">
              <v-icon size="16" class="mr-1" color="success">mdi-thumb-up</v-icon>
              <span class="text-caption">{{ formatNumber(item.likes) }}</span>
              <v-icon size="16" class="ml-2 mr-1" color="error">mdi-thumb-down</v-icon>
              <span class="text-caption">{{ formatNumber(item.dislikes) }}</span>
            </div>
          </div>
        </template>

        <!-- Data de criação -->
        <template #item.created_at="{ item }">
          <div class="text-center">
            <div class="text-body-2">{{ formatDate(item.created_at) }}</div>
            <div class="text-caption text-grey">{{ formatTime(item.created_at) }}</div>
          </div>
        </template>

        <!-- Ações -->
        <template #item.actions="{ item }">
          <div class="d-flex">
            <v-btn
              icon="mdi-eye"
              size="small"
              variant="text"
              @click="viewArticle(item)"
            />
            <v-btn
              icon="mdi-pencil"
              size="small"
              variant="text"
              @click="editArticle(item)"
            />
            <v-btn
              icon="mdi-delete"
              size="small"
              variant="text"
              color="error"
              @click="deleteArticle(item)"
            />
          </div>
        </template>

        <!-- No data -->
        <template #no-data>
          <div class="text-center py-8">
            <v-icon size="64" color="grey-lighten-1">mdi-file-document-outline</v-icon>
            <p class="mt-4 text-h6">Nenhum artigo encontrado</p>
            <p class="text-body-2 text-grey">
              {{ searchQuery ? 'Tente ajustar os filtros de busca' : 'Comece criando seu primeiro artigo' }}
            </p>
            <v-btn
              v-if="!searchQuery"
              color="primary"
              class="mt-4"
              @click="openCreateDialog"
            >
              Criar Artigo
            </v-btn>
          </div>
        </template>
      </v-data-table-server>
    </v-card>

    <!-- Dialog de Confirmação de Exclusão -->
    <v-dialog v-model="deleteDialog" max-width="500">
      <v-card>
        <v-card-title>
          <v-icon class="mr-2" color="error">mdi-delete</v-icon>
          Confirmar Exclusão
        </v-card-title>
        <v-card-text>
          Tem certeza que deseja excluir o artigo <strong>"{{ articleToDelete?.title }}"</strong>?
          Esta ação não pode ser desfeita.
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="deleteDialog = false">Cancelar</v-btn>
          <v-btn
            color="error"
            :loading="deleting"
            @click="confirmDelete"
          >
            Excluir
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useContentStore } from '@/stores/content'
import type { UserArticle } from '@/types/content'

const router = useRouter()
const contentStore = useContentStore()

// Estado local
const currentPage = ref(1)
const itemsPerPage = ref(10)
const loading = ref(false)
const deleting = ref(false)
const deleteDialog = ref(false)
const articleToDelete = ref<UserArticle | null>(null)

// Filtros
const statusFilter = ref('')
const categoryFilter = ref('')
const featuredFilter = ref(false)
const searchQuery = ref('')

// Computed
const articles = computed(() => contentStore.articles)
const totalItems = computed(() => contentStore.articlesCount)
const categories = computed(() => contentStore.categories)

// Headers da tabela
const headers = ref([
  { title: 'Artigo', key: 'title', sortable: false, width: '300px' },
  { title: 'Autor', key: 'author', sortable: false, width: '150px' },
  { title: 'Categoria', key: 'category', sortable: false, width: '120px' },
  { title: 'Status', key: 'status', sortable: false, width: '100px' },
  { title: 'Tags', key: 'tags', sortable: false, width: '150px' },
  { title: 'Métricas', key: 'metrics', sortable: false, width: '120px', align: 'center' as const },
  { title: 'Criado em', key: 'created_at', width: '120px', align: 'center' as const },
  { title: 'Ações', key: 'actions', sortable: false, width: '100px', align: 'center' as const }
])

// Options para filtros
const statusOptions = ref([
  { title: 'Rascunho', value: 'draft' },
  { title: 'Aguardando Moderação', value: 'pending' },
  { title: 'Publicado', value: 'published' },
  { title: 'Rejeitado', value: 'rejected' },
  { title: 'Arquivado', value: 'archived' }
])

const categoryOptions = computed(() => 
  categories.value.map(cat => ({
    title: cat.name,
    value: cat.slug
  }))
)

// Debounce para busca
let searchTimeout: NodeJS.Timeout
const debounceSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    applyFilters()
  }, 500)
}

// Methods
const loadItems = async ({ page, itemsPerPage: perPage }: any) => {
  loading.value = true
  try {
    currentPage.value = page
    itemsPerPage.value = perPage
    await contentStore.fetchArticles(page)
  } catch (error) {
    console.error('Erro ao carregar artigos:', error)
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  contentStore.setFilter('status', statusFilter.value)
  contentStore.setFilter('category', categoryFilter.value)
  contentStore.setFilter('featured', featuredFilter.value || undefined)
  contentStore.setFilter('search', searchQuery.value)
  loadItems({ page: 1, itemsPerPage: itemsPerPage.value })
}

const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('pt-BR')
}

const formatTime = (dateString: string): string => {
  return new Date(dateString).toLocaleTimeString('pt-BR', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

const getCategoryColor = (categoryName: string): string => {
  const colors: { [key: string]: string } = {
    'Análises Táticas': 'primary',
    'Mercado da Bola': 'success',
    'História do Futebol': 'warning',
    'Estatísticas': 'info',
    'Opinião': 'purple',
    'Entrevistas': 'teal'
  }
  return colors[categoryName] || 'grey'
}

const getStatusColor = (status: string): string => {
  const colors: { [key: string]: string } = {
    'draft': 'grey',
    'pending': 'warning',
    'published': 'success',
    'rejected': 'error',
    'archived': 'info'
  }
  return colors[status] || 'grey'
}

const getStatusIcon = (status: string): string => {
  const icons: { [key: string]: string } = {
    'draft': 'mdi-file-document-edit',
    'pending': 'mdi-clock-outline',
    'published': 'mdi-check-circle',
    'rejected': 'mdi-close-circle',
    'archived': 'mdi-archive'
  }
  return icons[status] || 'mdi-help-circle'
}

const getStatusText = (status: string): string => {
  const texts: { [key: string]: string } = {
    'draft': 'Rascunho',
    'pending': 'Aguardando',
    'published': 'Publicado',
    'rejected': 'Rejeitado',
    'archived': 'Arquivado'
  }
  return texts[status] || status
}

const openCreateDialog = () => {
  router.push('/content/articles/create')
}

const viewArticle = (article: UserArticle) => {
  router.push(`/content/articles/${article.id}`)
}

const editArticle = (article: UserArticle) => {
  router.push(`/content/articles/${article.id}/edit`)
}

const deleteArticle = (article: UserArticle) => {
  articleToDelete.value = article
  deleteDialog.value = true
}

const confirmDelete = async () => {
  if (!articleToDelete.value) return
  
  deleting.value = true
  try {
    await contentStore.deleteArticle(articleToDelete.value.id)
    deleteDialog.value = false
    articleToDelete.value = null
  } catch (error) {
    console.error('Erro ao deletar artigo:', error)
  } finally {
    deleting.value = false
  }
}

// Lifecycle
onMounted(async () => {
  await contentStore.fetchCategories()
  await loadItems({ page: 1, itemsPerPage: itemsPerPage.value })
})
</script>

<style scoped>
.v-data-table {
  background: transparent;
}
</style>
